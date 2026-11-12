"""Check declared module directions in a saved Godot text-analysis snapshot."""
import hashlib
import json
import re
from analysis_reports import validate_snapshot

STRONG_KINDS = {'load', 'preload', 'extends', 'ext-resource', 'uid-resolution'}


def relative_path(value, directory=False):
    if not isinstance(value, str) or not 1 <= len(value) <= 4096:
        raise ValueError('Expected a bounded relative POSIX path')
    body = value[:-1] if directory and value.endswith('/') else value
    if any(c in value for c in ['\\', ':', '*', '?', '[', ']', '\x00']) or any(p in {'', '.', '..'} for p in body.split('/')):
        raise ValueError('Paths must be literal relative files or directories, without traversal or globs')
    return value


def validate_rules(rules):
    if not isinstance(rules, dict) or set(rules) != {'schema_version', 'modules'} or type(rules['schema_version']) is not int or rules['schema_version'] != 1:
        raise ValueError('Expected boundary rules schema_version=1 and modules')
    modules = rules['modules']
    if not isinstance(modules, list) or not 1 <= len(modules) <= 64: raise ValueError('Expected 1..64 modules')
    ids = set(); selectors = []
    for module in modules:
        if not isinstance(module, dict) or set(module) != {'id', 'paths', 'allow'}: raise ValueError('Module requires id, paths and allow only')
        name = module['id']
        if not isinstance(name, str) or not re.fullmatch(r'[a-z][a-z0-9_-]{0,31}', name) or name in ids: raise ValueError('Invalid or duplicate module ID')
        ids.add(name)
        paths, allowed = module['paths'], module['allow']
        if not isinstance(paths, list) or not 1 <= len(paths) <= 512: raise ValueError('Expected nonempty module paths')
        if not isinstance(allowed, list) or len(allowed) > 64 or not all(isinstance(v, str) for v in allowed) or len(set(allowed)) != len(allowed):
            raise ValueError('Invalid allowed module list')
        for selector in paths:
            relative_path(selector, directory=True)
            selectors.append((selector, name))
    if len(selectors) > 512: raise ValueError('Selector limit reached')
    for index, (left, _) in enumerate(selectors):
        for right, _ in selectors[index+1:]:
            if left == right or (left.endswith('/') and right.startswith(left)) or (right.endswith('/') and left.startswith(right)):
                raise ValueError('Overlapping module selectors are ambiguous or redundant')
    if any(not set(m['allow']) <= ids for m in modules): raise ValueError('Unknown allowed module ID')
    return selectors, {m['id']: set(m['allow']) | {m['id']} for m in modules}


def check_boundaries(snapshot, rules):
    validate_snapshot(snapshot)
    if type(snapshot['format_version']) is not int: raise ValueError('Invalid snapshot version')
    selectors, allowed = validate_rules(rules)
    for key, limit in [('files', 30000), ('references', 100000), ('warnings', 100000),
                       ('dynamic_references', 100000), ('uid_references', 100000), ('uid_conflicts', 100000)]:
        if not isinstance(snapshot.get(key, []), list) or len(snapshot.get(key, [])) > limit: raise ValueError('Invalid or excessive snapshot list: '+key)
    for path in snapshot['files']: relative_path(path)
    if len(set(snapshot['files'])) != len(snapshot['files']): raise ValueError('Duplicate snapshot file')
    unknowns = []; violations = []; owners = {}; observed = set(); checked = 0
    def owner(path):
        if path not in owners:
            owners[path] = next((name for selector, name in selectors if path == selector or selector.endswith('/') and path.startswith(selector)), None)
        if owners[path]: observed.add(owners[path])
        return owners[path]
    def clue(row):
        return {key: row[key] for key in ['source', 'target', 'line', 'status'] if key in row}
    if snapshot['scope'].get('analysis_revision') != 2:
        unknowns.append({'kind': 'snapshot-coverage', 'detail': 'Expected analysis_revision=2 coverage metadata'})
    for key in ['dynamic_references', 'uid_references', 'uid_conflicts']:
        if key not in snapshot: unknowns.append({'kind': 'snapshot-coverage', 'detail': 'Missing '+key})
    if snapshot['warnings']: unknowns.append({'kind': 'scan-warnings', 'count': len(snapshot['warnings'])})
    if not snapshot['files']: unknowns.append({'kind': 'no-observed-files'})
    scanned = set(snapshot['files'])
    for path in snapshot['files']:
        if not owner(path): unknowns.append({'kind': 'unowned-file', 'path': path})
        if not re.fullmatch(r'[a-f0-9]{64}', snapshot['source_fingerprints'].get(path, '')):
            unknowns.append({'kind': 'missing-source-fingerprint', 'path': path})
    for row in snapshot['references']:
        if not isinstance(row, dict): raise ValueError('Invalid reference row')
        source = relative_path(row.get('source')); target = row.get('target')
        if not isinstance(target, str) or not 1 <= len(target) <= 4096: raise ValueError('Invalid reference target')
        if source not in scanned:
            unknowns.append({'kind': 'unscanned-source', **clue(row)}); continue
        if row.get('status') != 'exists':
            unknowns.append({'kind': 'unresolved-reference', **clue(row)}); continue
        relative_path(target)
        if row.get('kind') not in STRONG_KINDS:
            unknowns.append({'kind': 'weak-reference', **clue(row)}); continue
        source_module, target_module = owner(source), owner(target)
        if not source_module or not target_module:
            unknowns.append({'kind': 'unowned-reference', **clue(row)}); continue
        checked += 1
        if target_module not in allowed[source_module]:
            violations.append({**clue(row), 'kind': row['kind'], 'source_module': source_module, 'target_module': target_module})
    for row in snapshot.get('dynamic_references', []):
        if not isinstance(row, dict): raise ValueError('Invalid dynamic reference')
        unknowns.append({'kind': 'dynamic-reference', **clue(row)})
    for row in snapshot.get('uid_references', []):
        if not isinstance(row, dict): raise ValueError('Invalid UID reference')
        if row.get('status') != 'source-resolved' or row.get('path_disagrees'):
            unknowns.append({'kind': 'uid-reference', **clue(row)})
    if snapshot.get('uid_conflicts'): unknowns.append({'kind': 'uid-conflicts', 'count': len(snapshot['uid_conflicts'])})
    for name in sorted(allowed.keys()-observed): unknowns.append({'kind': 'unobserved-module', 'module': name})
    def fingerprint(value):
        return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')).hexdigest()
    return {'schema_version': 1, 'kind': 'dependency-boundaries',
            'status': 'violations' if violations else 'partial' if unknowns else 'no-observed-violations',
            'passed': not violations and not unknowns, 'coverage': 'partial' if unknowns else 'observed-scope',
            'checked_reference_count': checked, 'violations': violations, 'unknowns': unknowns,
            'snapshot_utc': snapshot.get('snapshot_utc'), 'scan_scope': snapshot['scope'],
            'snapshot_sha256': fingerprint(snapshot), 'rules_sha256': fingerprint(rules),
            'limits': ['Evaluates explicit observed Godot resource references in this saved snapshot only.',
                       'Entry/autoload registrations are outside the explicit reference rows evaluated here.',
                       'No proof of runtime calls, signal/DI dependencies, unique state writers or architectural quality.',
                       'Snapshot may be stale; no current source or engine is read. Re-analyze the intended tree before use.',
                       'Analyzer exclusions and bounds still apply; unobserved runtime dependencies remain unknown.']}
