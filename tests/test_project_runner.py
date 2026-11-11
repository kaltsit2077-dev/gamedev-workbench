import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'skills/gamedev-workbench/scripts'))
from project_runner import file_hash, native_verdict, plan_project, run_project, freeze_project
from engine_adapters import run_adapter_case, capabilities


class ProjectRunnerTests(unittest.TestCase):
    def fixture(self, path, native, code=''):
        project = path/'project with spaces'; project.mkdir()
        script = project/'probe.py'
        script.write_text('import json,os,time\n'+code+'\nwith open(os.environ["GDW_TEST_REPORT"],"w") as f: json.dump('+repr(native)+',f)\n', encoding='utf-8')
        plan = {'schema_version': 1, 'engine': 'custom', 'expected_version': '1.2', 'sources': {'probe.py': file_hash(script)},
                'tests': [{'id': 'probe', 'argv': ['{python}', '{project}/probe.py'], 'cwd': '.', 'timeout_seconds': 5,
                           'effects': 'writes only explicit native report', 'required_checks': ['behavior']}]}
        config = path/'plan.json'; config.write_text(json.dumps(plan), encoding='utf-8')
        return project, config, plan
    def native(self): return {'engine': 'custom', 'engine_version': '1.2.0', 'passed': True, 'checks': [{'name': 'behavior', 'passed': True}]}
    def test_preview_is_read_only_execution_retains_native_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve(); project, config, data = self.fixture(root, self.native())
            before = {p.name: p.read_bytes() for p in project.iterdir()}
            preview = plan_project(project, config)
            self.assertEqual(preview['execution'], 'preview'); self.assertEqual(len(preview['tests'][0]['argv']), 2)
            result = run_project(project, config, root/'evidence')
            self.assertTrue(result['passed']); self.assertEqual(result['selected_sources_changed'], [])
            self.assertEqual(before, {p.name: p.read_bytes() for p in project.iterdir()})
            with self.assertRaises(ValueError): run_project(project, config, root/'evidence')
            (project/'probe.py').write_text('# changed', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'source changed'): plan_project(project, config)
    def test_zero_exit_and_empty_or_contradictory_evidence_do_not_pass(self):
        for native in [{}, {**self.native(), 'checks': []}, {**self.native(), 'checks': [{'name': 'behavior', 'passed': False}]}]:
            with self.subTest(native=native), tempfile.TemporaryDirectory() as d:
                root = Path(d).resolve(); project, config, data = self.fixture(root, native)
                result = run_project(project, config, root/'out')
                self.assertEqual(result['tests'][0]['exit_code'], 0); self.assertFalse(result['passed'])
    def test_timeout_and_path_escape(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve(); project, config, data = self.fixture(root, self.native(), 'time.sleep(4)')
            data['tests'][0]['timeout_seconds'] = 1; config.write_text(json.dumps(data), encoding='utf-8')
            result = run_project(project, config, root/'out')
            self.assertEqual(result['tests'][0]['reason'], 'timeout')
            data['tests'][0]['cwd'] = '..'; config.write_text(json.dumps(data), encoding='utf-8')
            with self.assertRaises(ValueError): plan_project(project, config)
    def test_missing_adapters_preserve_blocked_common_contract(self):
        with tempfile.TemporaryDirectory() as d:
            for kind in ['unity', 'unreal', 'blender']:
                result = run_adapter_case(kind, None, '1', d, Path(d).resolve()/kind)
                self.assertEqual(result['status'], 'blocked'); self.assertFalse(result['passed'])
                self.assertEqual(result['dimensions']['rendering'], 'not-run')
        self.assertEqual(len(capabilities()['adapters']), 5)
    def test_missing_required_or_wrong_version_checks_fail(self):
        self.assertFalse(native_verdict(self.native(), 'custom', '1.20', ['behavior']))
        self.assertFalse(native_verdict(self.native(), 'custom', '1.2', ['other']))
    def test_freeze_takes_explicit_snapshot_without_running(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve(); project, config, data = self.fixture(root, self.native())
            data['sources']['probe.py'] = None; config.write_text(json.dumps(data), encoding='utf-8')
            result = freeze_project(project, config, root/'frozen.json')
            self.assertEqual(result['execution'], 'not-run')
            self.assertEqual(plan_project(project, root/'frozen.json')['sources'], result['sources'])
            self.assertFalse((root/'native.json').exists())
