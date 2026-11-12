"""Read local Git evidence without fetching or changing index/branches/files."""
import os
from pathlib import Path
import re
import subprocess
import tempfile

TEXT_TYPES = {'.gd', '.gdshader', '.tscn', '.tres', '.cs', '.cpp', '.h', '.hpp', '.py', '.json', '.yaml', '.yml',
              '.ts', '.tsx', '.js', '.mjs', '.shader', '.md', '.ini', '.cfg', '.txt', '.unity', '.prefab', '.meta'}


def git(root, args, optional=False):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', GIT_TERMINAL_PROMPT='0')
    overrides = []
    if args[0] in {'status', 'diff'}:
        keys = git(root, ['config', '--null', '--name-only', '--get-regexp', r'^filter\..*\.(clean|smudge|process|required)$'], optional=True)
        names = [decode(key) for key in (keys or b'').split(b'\0') if key]
        if len(names) > 100: raise ValueError('Configured filter limit reached')
        for name in names:
            overrides += ['-c', name+('=false' if name.endswith('.required') else '=')]
    with tempfile.TemporaryFile() as stream:
        process = subprocess.run(['git', '--no-pager', '--literal-pathspecs', '-c', 'core.fsmonitor=false', *overrides, '-C', str(root), *args],
                                 stdout=stream, stderr=subprocess.STDOUT, timeout=20, env=env, shell=False)
        stream.seek(0); raw = stream.read(5_000_001)
    if len(raw) > 5_000_000: raise ValueError('Git output limit reached')
    if process.returncode:
        if optional: return None
        raise ValueError('Local Git command failed: '+args[0])
    return raw


def decode(raw): return raw.decode('utf-8', errors='replace')


def review_git(project, base=None, max_paths=2000, max_bytes=1_000_000):
    if type(max_paths) is not int or not 1 <= max_paths <= 10000 or type(max_bytes) is not int or not 1 <= max_bytes <= 5_000_000:
        raise ValueError('Invalid Git scan limits')
    root = Path(project).expanduser().resolve(strict=True)
    top = git(root, ['rev-parse', '--show-toplevel'])
    if Path(decode(top).strip()).resolve() != root: raise ValueError('Select the repository root, not a subdirectory')
    report = {'schema_version': 1, 'kind': 'git-review', 'execution': 'local read-only; no fetch or mutation',
              'head': None, 'base': None, 'branch': None, 'upstream': None, 'local_divergence': None,
              'operations': [], 'changes': [], 'unmerged_paths': [], 'findings': [], 'warnings': [],
              'scan_complete': True, 'limits': ['Remote references may be stale; no network freshness check.',
                                              'Checks changed paths and selected metadata, not semantic merge correctness or all project references.',
                                              'Configured filters, external diff, text conversion and fsmonitor are disabled; filtered files may be reported differently.',
                                              'Path names are decoded as UTF-8; invalid bytes are replaced.']}
    def oid(ref):
        if not isinstance(ref, str) or not 1 <= len(ref) <= 512 or '\x00' in ref: raise ValueError('Invalid local reference')
        value = git(root, ['rev-parse', '--verify', '--end-of-options', ref+'^{commit}'], optional=True)
        text = decode(value).strip() if value else ''
        return text if re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', text) else None
    report['head'] = oid('HEAD')
    if not report['head']: report['warnings'].append('HEAD does not resolve to a readable commit; unborn or unreadable history')
    branch = git(root, ['symbolic-ref', '--quiet', '--short', 'HEAD'], optional=True)
    report['branch'] = decode(branch).strip() if branch else None
    upstream = git(root, ['rev-parse', '--symbolic-full-name', '@{upstream}'], optional=True)
    if upstream:
        report['upstream'] = decode(upstream).strip()
        upstream_oid = oid('@{upstream}')
        if upstream_oid and report['head']:
            counts = git(root, ['rev-list', '--left-right', '--count', report['head']+'...'+upstream_oid], optional=True)
            if counts and re.fullmatch(rb'\d+\s+\d+\s*', counts):
                ahead, behind = map(int, counts.split()); report['local_divergence'] = {'ahead': ahead, 'behind': behind}
            else: report['warnings'].append('Upstream graph could not be read')
    if base is not None:
        report['base'] = oid(base)
        if not report['base']: report['warnings'].append('Requested local base cannot be resolved')
    for name in ['MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD', 'rebase-merge', 'rebase-apply']:
        value = git(root, ['rev-parse', '--git-path', name])
        path = Path(decode(value).strip())
        if not path.is_absolute(): path = root/path
        if path.exists(): report['operations'].append(name)
    raw = git(root, ['status', '--porcelain=v1', '-z', '--untracked-files=all'])
    fields = raw.split(b'\0'); changes = {}; index = 0
    while index < len(fields) and fields[index]:
        field = fields[index]; index += 1
        if len(field) < 4: raise ValueError('Malformed porcelain status')
        status, path = decode(field[:2]), decode(field[3:]); item = {'path': path, 'status': status, 'origin': 'working-tree/index'}
        if 'R' in status or 'C' in status:
            if index >= len(fields) or not fields[index]: raise ValueError('Missing rename source')
            item['old_path'] = decode(fields[index]); index += 1
        changes[path] = item
    if report['base']:
        fields = git(root, ['diff', '--no-ext-diff', '--no-textconv', '--no-renames', '--name-status', '-z', report['base'], '--']).split(b'\0')
        for index in range(0, len(fields)-1, 2):
            status, path = decode(fields[index]), decode(fields[index+1])
            if path and path not in changes: changes[path] = {'path': path, 'status': status, 'origin': 'base-to-worktree'}
    entries = git(root, ['ls-files', '--unmerged', '-z']).split(b'\0')
    report['unmerged_paths'] = sorted({decode(row.split(b'\t', 1)[1]) for row in entries if b'\t' in row})
    tracked = {decode(p) for p in git(root, ['ls-files', '--cached', '-z']).split(b'\0') if p}
    if len(tracked) > 100000: raise ValueError('Tracked path limit reached')
    def finding(kind, path, detail): report['findings'].append({'kind': kind, 'path': path, 'detail': detail})
    for name in report['unmerged_paths'][:max_paths]: finding('unmerged-index', name, 'Index still contains unresolved stages')
    folded = {}
    for path in tracked: folded.setdefault(path.casefold(), []).append(path)
    for paths in folded.values():
        if len(paths) > 1: finding('case-collision', sorted(paths)[0], 'Tracked names differ only by case; review target filesystem behavior')
    if len(changes) > max_paths:
        report['scan_complete'] = False; report['warnings'].append('Changed path limit reached')
    for path, item in sorted(changes.items())[:max_paths]:
        report['changes'].append(item)
        candidate = root/path
        if not candidate.resolve().is_relative_to(root) or candidate.is_symlink():
            report['warnings'].append('Escaping or symlink changed path skipped'); report['scan_complete'] = False; continue
        old = item.get('old_path')
        if old and old != path and old.casefold() == path.casefold(): finding('case-only-rename', path, 'Verify case-sensitive references and target platforms')
        if old:
            for suffix in ['.uid', '.meta']:
                if old+suffix in tracked and path+suffix not in tracked:
                    finding('metadata-rename', path, 'Old metadata remains tracked without the renamed counterpart: '+suffix)
        if 'D' in item['status'] and not candidate.exists():
            for suffix in ['.uid', '.meta']:
                if path+suffix in tracked: finding('orphaned-metadata', path+suffix, 'Source was deleted; verify metadata and references in the integrated tree')
        if not candidate.is_file(): continue
        if candidate.stat().st_size > max_bytes:
            report['warnings'].append('Changed file content skipped by size limit: '+path); report['scan_complete'] = False; continue
        if candidate.suffix.lower() not in TEXT_TYPES: continue
        try: text = candidate.read_bytes()
        except OSError:
            report['warnings'].append('Changed file could not be read: '+path); report['scan_complete'] = False; continue
        if b'\0' in text: continue
        if all(re.search(pattern, text, re.MULTILINE) for pattern in [rb'^<{7}(?: |\r?$)', rb'^={7}\r?$', rb'^>{7}(?: |\r?$)']):
            finding('possible-conflict-markers', path, 'A complete marker pattern is present; distinguish unresolved merge text from intentional examples')
    if oid('HEAD') != report['head']: report['warnings'].append('HEAD changed during inspection; repeat before integration')
    if report['warnings']: report['scan_complete'] = False
    report['assessment'] = ('blocked-by-unmerged-index' if report['unmerged_paths'] else
                            'requires-review' if report['findings'] else 'partial' if not report['scan_complete'] else 'no-listed-issues')
    return report
