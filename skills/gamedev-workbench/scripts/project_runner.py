"""Explicit project test plans, no implicit shell; native evidence gates success."""
import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys
from time import perf_counter
from workspace_io import local_path, new_json, read_json


def file_hash(path):
    if not path.is_file() or path.stat().st_size > 5_000_000:
        raise ValueError('Selected source must be a file below 5 MB')
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def native_verdict(native, engine, expected, required):
    if not isinstance(native, dict): return False
    checks = native.get('checks'); version = native.get('engine_version')
    valid = (isinstance(checks, list) and 0 < len(checks) <= 5000
             and all(isinstance(c, dict) and isinstance(c.get('name'), str) and c['name'] and type(c.get('passed')) is bool for c in checks))
    if not valid or not isinstance(version, str): return False
    names = [c['name'] for c in checks]
    return (native.get('engine') == engine and native.get('passed') is True and all(c['passed'] for c in checks)
            and len(names) == len(set(names)) and set(required) <= set(names)
            and bool(re.match('^'+re.escape(expected)+r'(?:[.\-\s]|$)', version)))


def plan_project(project, config, engine=None, output=None):
    root = Path(project).expanduser().resolve(strict=True)
    if not root.is_dir(): raise ValueError('Project directory required')
    data = config if isinstance(config, dict) else read_json(config)
    if not isinstance(data, dict) or set(data) != {'schema_version', 'engine', 'expected_version', 'sources', 'tests'} or type(data['schema_version']) is not int or data['schema_version'] != 1:
        raise ValueError('Unknown project-test plan fields/version')
    if not isinstance(data['engine'], str) or data['engine'] not in {'godot', 'unity', 'unreal', 'web', 'blender', 'custom'}:
        raise ValueError('Unknown test-plan engine')
    if not isinstance(data['expected_version'], str) or not re.fullmatch(r'[0-9A-Za-z.\-]{1,60}', data['expected_version']):
        raise ValueError('Explicit expected version prefix required')
    sources = data['sources']
    if not isinstance(sources, dict) or not 1 <= len(sources) <= 200: raise ValueError('1..200 frozen selected sources required')
    fingerprints = {}
    for name, expected in sources.items():
        if not isinstance(expected, str) or not re.fullmatch(r'[a-f0-9]{64}', expected): raise ValueError('Invalid source hash')
        actual = file_hash(local_path(root, name))
        if actual != expected: raise ValueError('Selected source changed: '+name)
        fingerprints[name] = actual
    tests = data['tests']
    if not isinstance(tests, list) or not 1 <= len(tests) <= 20: raise ValueError('1..20 explicit tests required')
    output_path = Path(output).absolute() if output else None
    if output_path and (output_path.resolve().is_relative_to(root) or output_path.exists() or output_path.is_symlink()):
        raise ValueError('Execution output must be new and outside the project')
    if output_path and any(p.is_symlink() for p in output_path.parents): raise ValueError('Output parent cannot be symlinked')
    replacements = {'project': str(root), 'engine': str(Path(engine).expanduser().resolve()) if engine else '{engine}',
                    'python': sys.executable, 'output': str(output_path) if output_path else '{output}'}
    result = []; ids = set()
    for item in tests:
        if not isinstance(item, dict) or set(item) != {'id', 'argv', 'cwd', 'timeout_seconds', 'effects', 'required_checks'}:
            raise ValueError('Invalid test fields')
        name = item['id']
        if not isinstance(name, str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', name) or name in ids:
            raise ValueError('Test ids must be unique lowercase names')
        ids.add(name)
        argv = item['argv']; required = item['required_checks']
        if not isinstance(argv, list) or not 1 <= len(argv) <= 100 or not all(isinstance(a, str) and 0 < len(a) <= 8192 and '\x00' not in a for a in argv):
            raise ValueError('argv must be a bounded nonempty string list')
        if type(item['timeout_seconds']) is not int or not 1 <= item['timeout_seconds'] <= 300:
            raise ValueError('Timeout must be 1..300 seconds')
        if not isinstance(item['effects'], str) or not 1 <= len(item['effects']) <= 4000:
            raise ValueError('Describe test side effects explicitly')
        if not isinstance(required, list) or not 1 <= len(required) <= 500 or not all(isinstance(x, str) and 0 < len(x) <= 1000 for x in required):
            raise ValueError('Declare nonempty required check names')
        expanded = []
        for arg in argv:
            if any(key not in replacements for key in re.findall(r'\{([a-z_]+)\}', arg)):
                raise ValueError('Unknown argv placeholder')
            for key, value in replacements.items(): arg = arg.replace('{'+key+'}', value)
            expanded.append(arg)
        cwd = local_path(root, item['cwd'])
        if not cwd.is_dir(): raise ValueError('Test cwd is not a project directory')
        result.append({**item, 'argv': expanded, 'cwd': str(cwd)})
    return {'schema_version': 1, 'kind': 'project-test-plan', 'engine': data['engine'], 'expected_version': data['expected_version'],
            'project': str(root), 'sources': fingerprints, 'tests': result, 'execution': 'preview',
            'limits': ['Explicit user-selected code runs with normal process permissions, not an isolation boundary.',
                       'Only selected source hashes are tracked; unlisted saves/caches/files are outside that snapshot.',
                       'Native reports are project-authored assertions, not independent proof of visual or gameplay quality.']}


def freeze_project(project, config, output):
    root = Path(project).expanduser().resolve(strict=True)
    data = read_json(config)
    if not isinstance(data, dict) or not isinstance(data.get('sources'), dict) or not 1 <= len(data['sources']) <= 200:
        raise ValueError('Declare the selected source paths before freezing')
    data['sources'] = {name: file_hash(local_path(root, name)) for name in data['sources']}
    plan_project(root, data)
    new_json(output, data)
    return {'output': str(output), 'sources': data['sources'], 'execution': 'not-run',
            'next': 'Preview project-tests with this frozen config; changed selected files will require a new snapshot.'}


def run_project(project, config, output, engine=None):
    plan = plan_project(project, config, engine, output)
    root = Path(plan['project']); destination = Path(output).absolute(); destination.mkdir(parents=True)
    records = []
    for item in plan['tests']:
        folder = destination/item['id']; folder.mkdir()
        report = folder/'native.json'; log = folder/'process.log'; native = None; started = perf_counter()
        row = {'id': item['id'], 'status': 'failed', 'passed': False, 'effects': item['effects'], 'exit_code': None}
        if any('{engine}' in arg for arg in item['argv']) or (engine and not Path(engine).expanduser().is_file()):
            row.update(status='blocked', reason='Engine executable not supplied')
        else:
            try:
                with log.open('xb') as stream:
                    process = subprocess.run(item['argv'], cwd=item['cwd'], env=dict(os.environ, GDW_TEST_REPORT=str(report)),
                                             stdout=stream, stderr=subprocess.STDOUT, timeout=item['timeout_seconds'], shell=False)
                row['exit_code'] = process.returncode
                native = read_json(report)
                passed = process.returncode == 0 and native_verdict(native, plan['engine'], plan['expected_version'], item['required_checks'])
                row.update(status='passed' if passed else 'failed', passed=passed)
                if not passed: row['reason'] = 'Exit code, version, required checks or native verdict failed'
            except subprocess.TimeoutExpired: row['reason'] = 'timeout'
            except (OSError, ValueError, TypeError) as error: row['reason'] = type(error).__name__
        row.update(elapsed_seconds=perf_counter()-started, native=native)
        records.append(row)
    changes = []
    for name, before in plan['sources'].items():
        try: after = file_hash(local_path(root, name))
        except (OSError, ValueError): after = None
        if before != after: changes.append(name)
    status = 'failed' if changes or any(r['status'] == 'failed' for r in records) else ('blocked' if any(r['status'] == 'blocked' for r in records) else 'passed')
    result = {'schema_version': 1, 'kind': 'execution-report', 'engine': plan['engine'], 'status': status, 'passed': status == 'passed',
              'source_fingerprints': plan['sources'], 'selected_sources_changed': changes, 'tests': records,
              'dimensions': {'rendering': 'not-inferred', 'physical_input': 'not-inferred', 'performance': 'not-measured'},
              'limits': plan['limits']}
    new_json(destination/'run.json', result)
    return result
