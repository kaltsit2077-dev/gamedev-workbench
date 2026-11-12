"""Engine capability declarations and common envelopes over original cases."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from project_runner import native_verdict
from workspace_io import new_json, read_json


def capabilities():
    return {'schema_version': 1, 'kind': 'adapter-capabilities', 'adapters': [
        {'engine': 'godot', 'implemented': ['source-analysis', 'native-ui-effects-case', 'declared-project-tests'], 'requires': 'official matching Godot executable', 'evidence': 'local run required; archived Windows 4.7.2 cases exist'},
        {'engine': 'unity', 'implemented': ['editor-smoke-case', 'declared-project-tests'], 'requires': 'licensed local Unity Editor', 'evidence': 'real editor run pending'},
        {'engine': 'unreal', 'implemented': ['editor-python-smoke-case', 'declared-project-tests'], 'requires': 'local Unreal Editor with Python enabled in fixture', 'evidence': 'real editor run pending'},
        {'engine': 'web', 'implemented': ['javascript-state-lifecycle-case', 'declared-project-tests'], 'requires': 'Node.js for original case; browser validation separate', 'evidence': 'runtime check is not browser/UI/rendering evidence'},
        {'engine': 'blender', 'implemented': ['background-object-smoke-case', 'declared-project-tests'], 'requires': 'local Blender executable', 'evidence': 'real Blender run pending'}],
        'limits': ['Capabilities describe implemented entry points, not all-engine feature parity or a successful local run.',
                   'No editor MCP is connected by this registry; engine-native behavior remains adapter-specific.']}


def run_adapter_case(kind, editor, expected, scratch, output):
    if kind not in {a['engine'] for a in capabilities()['adapters']}: raise ValueError('Unknown adapter')
    if not isinstance(expected, str) or not expected: raise ValueError('Explicit expected version required')
    destination = Path(output).absolute()
    if destination.exists() or destination.is_symlink() or any(p.is_symlink() for p in destination.parents):
        raise ValueError('Adapter output must be new without symlink parents')
    result = {'schema_version': 1, 'kind': 'execution-report', 'engine': kind, 'status': 'blocked', 'passed': False,
              'dimensions': {'rendering': 'not-run', 'physical_input': 'not-run', 'performance': 'not-measured'}, 'native': None}
    root = Path(__file__).resolve().parents[1]
    if not editor or not Path(editor).expanduser().is_file():
        result['reason'] = 'Editor/runtime executable not supplied or not found'
    elif kind in {'unity', 'unreal'}:
        from editor_cases import verify_editor_case
        native = verify_editor_case(kind, editor, expected, scratch, destination/'native')
        result.update(status=native['status'], passed=native['passed'], native=native)
    elif kind == 'godot':
        from workbench import doctor
        from quality_checks import check_sample
        probe = doctor(editor, expected, official=True)
        if probe['engine_status'] != 'version-confirmed': result['reason'] = 'Expected official Godot version not confirmed'
        else:
            native = check_sample(editor, destination/'native', scratch, False, case='menu')
            native.update(engine='godot', engine_version=probe['engine_version'])
            passed = native.get('passed') is True and isinstance(native.get('checks'), list) and bool(native['checks']) and all(c.get('passed') is True for c in native['checks'])
            result.update(status='passed' if passed else 'failed', passed=passed, native=native)
    else:
        Path(scratch).mkdir(parents=True, exist_ok=True)
        destination.mkdir(parents=True)
        with tempfile.TemporaryDirectory(prefix='gdw-adapter-', dir=scratch) as d:
            project = Path(d)/'case'; shutil.copytree(root/('assets/'+kind+'-smoke'), project)
            command = ([str(Path(editor).resolve()), str(project/'smoke.mjs')] if kind == 'web' else
                       [str(Path(editor).resolve()), '--background', '--factory-startup', '--python', str(project/'smoke.py')])
            native_path = destination/'native.json'
            try:
                with (destination/'process.log').open('xb') as log:
                    process = subprocess.run(command, cwd=project, env=dict(os.environ, GDW_TEST_REPORT=str(native_path)),
                                             stdout=log, stderr=subprocess.STDOUT, timeout=120, shell=False)
                native = read_json(native_path)
                required = ['state event and unsubscribe', 'bounded reset'] if kind == 'web' else ['object transform', 'object and mesh cleanup']
                passed = process.returncode == 0 and native_verdict(native, kind, expected, required)
                result.update(status='passed' if passed else 'failed', passed=passed, native=native, exit_code=process.returncode)
            except (OSError, ValueError, subprocess.TimeoutExpired) as error:
                result.update(status='failed', reason=type(error).__name__)
    destination.mkdir(parents=True, exist_ok=True)
    new_json(destination/'run.json', result)
    return result
