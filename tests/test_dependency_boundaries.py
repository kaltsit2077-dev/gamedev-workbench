import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'skills/gamedev-workbench/scripts'))
from project_analysis import analyze_project
from dependency_boundaries import check_boundaries
from workbench import main


class DependencyBoundaryTests(unittest.TestCase):
    def test_limits_and_packaged_example_are_executable(self):
        skill = ROOT/'skills/gamedev-workbench'
        rules = json.loads((skill/'assets/dependency-rules.json').read_text(encoding='utf-8'))
        snapshot = analyze_project(skill/'assets/godot-demo')
        self.assertTrue(check_boundaries(snapshot, rules)['passed'])
        missing_hash = copy.deepcopy(snapshot); missing_hash['source_fingerprints'].pop('demo.gd')
        self.assertFalse(check_boundaries(missing_hash, rules)['passed'])
        unscanned = copy.deepcopy(snapshot); unscanned['files'].remove('demo.gd')
        self.assertTrue(any(r['kind'] == 'unscanned-source' for r in check_boundaries(unscanned, rules)['unknowns']))
        oversized = copy.deepcopy(snapshot); oversized['files'] = ['x.gd']*30001
        with self.assertRaises(ValueError): check_boundaries(oversized, rules)
        invalid = {'schema_version': 1, 'modules': [{'id': 'x'+str(i), 'paths': [str(i)+'/'], 'allow': []} for i in range(65)]}
        with self.assertRaises(ValueError): check_boundaries(snapshot, invalid)

    def fixture(self, root):
        (root/'project.godot').write_text('[application]\nconfig/name="Original"\n', encoding='utf-8')
        for folder in ['ui', 'state']: (root/folder).mkdir()
        (root/'ui/menu.gd').write_text('extends Node\nconst S=preload("res://state/model.gd")\n', encoding='utf-8')
        (root/'state/model.gd').write_text('extends RefCounted\nvar count=0\n', encoding='utf-8')
        return {'schema_version': 1, 'modules': [
            {'id': 'ui', 'paths': ['ui/'], 'allow': ['state']},
            {'id': 'state', 'paths': ['state/'], 'allow': []}]}

    def test_real_reference_direction_and_read_only(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); rules = self.fixture(root)
            before = {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            snapshot = analyze_project(root); report = check_boundaries(snapshot, rules)
            self.assertEqual(report['status'], 'no-observed-violations')
            self.assertEqual(report['checked_reference_count'], 1)
            self.assertEqual(before, {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*') if p.is_file()})
            (root/'state/model.gd').write_text('extends RefCounted\nconst UI=preload("res://ui/menu.gd")\n', encoding='utf-8')
            snapshot = analyze_project(root); original = copy.deepcopy(snapshot)
            report = check_boundaries(snapshot, rules)
            self.assertEqual(report['status'], 'violations')
            self.assertEqual(report['violations'][0]['source'], 'state/model.gd')
            self.assertEqual(report['violations'][0]['target_module'], 'ui')
            self.assertEqual(snapshot, original)

    def test_self_edges_and_exact_file_selectors(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); rules = self.fixture(root)
            rules['modules'][0]['paths'] = ['ui/menu.gd']
            (root/'state/model.gd').write_text('extends RefCounted\nconst X=preload("res://state/model.gd")\n', encoding='utf-8')
            self.assertEqual(check_boundaries(analyze_project(root), rules)['status'], 'no-observed-violations')
            (root/'ui/menu.gd.backup.gd').write_text('extends Node\n', encoding='utf-8')
            report = check_boundaries(analyze_project(root), rules)
            self.assertEqual(report['status'], 'partial')
            self.assertTrue(any(r.get('path') == 'ui/menu.gd.backup.gd' for r in report['unknowns']))

    def test_weak_literals_dynamic_uid_and_scan_limits_remain_unknown(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); rules = self.fixture(root)
            (root/'state/model.gd').write_text('extends RefCounted\nvar note="res://ui/menu.gd"\nvar x=load(runtime_path)\nconst U=preload("uid://unknown")\n', encoding='utf-8')
            report = check_boundaries(analyze_project(root), rules)
            self.assertEqual(report['status'], 'partial'); self.assertEqual(report['violations'], [])
            kinds = {r['kind'] for r in report['unknowns']}
            self.assertTrue({'weak-reference', 'dynamic-reference', 'uid-reference'} <= kinds)
            report = check_boundaries(analyze_project(root, max_files=1), rules)
            self.assertEqual(report['coverage'], 'partial')

    def test_violation_survives_other_uncertainty(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); rules = self.fixture(root)
            (root/'state/model.gd').write_text('extends RefCounted\nconst UI=preload("res://ui/menu.gd")\nvar x=load(runtime_path)\n', encoding='utf-8')
            report = check_boundaries(analyze_project(root), rules)
            self.assertEqual(report['status'], 'violations'); self.assertEqual(report['coverage'], 'partial')
            (root/'ui/menu.gd').write_text('extends Node\nconst M=preload("res://state/missing.gd")\n', encoding='utf-8')
            self.assertTrue(any(r['kind'] == 'unresolved-reference' for r in check_boundaries(analyze_project(root), rules)['unknowns']))

    def test_invalid_or_ambiguous_rules_and_snapshot_paths_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); rules = self.fixture(root); snapshot = analyze_project(root)
            for path in ['../outside', '/absolute', 'C:/outside', 'ui\\menu.gd', 'ui//', './ui/', 'ui/*']:
                invalid = copy.deepcopy(rules); invalid['modules'][0]['paths'] = [path]
                with self.subTest(path=path), self.assertRaises(ValueError): check_boundaries(snapshot, invalid)
            for mutation in ['overlap', 'unknown-id', 'bool-version', 'unknown-field']:
                invalid = copy.deepcopy(rules)
                if mutation == 'overlap': invalid['modules'][1]['paths'] = ['ui/menu.gd']
                elif mutation == 'unknown-id': invalid['modules'][0]['allow'] = ['missing']
                elif mutation == 'bool-version': invalid['schema_version'] = True
                else: invalid['ignored'] = True
                with self.subTest(mutation=mutation), self.assertRaises(ValueError): check_boundaries(snapshot, invalid)
            malformed = copy.deepcopy(snapshot); malformed['files'].append('../escape.gd')
            with self.assertRaises(ValueError): check_boundaries(malformed, rules)

    def test_cli_refuses_to_replace_either_input(self):
        import contextlib, io
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); rules = self.fixture(root)
            inputs = [root/'snapshot.json', root/'rules.json']
            inputs[0].write_text(json.dumps(analyze_project(root)), encoding='utf-8')
            inputs[1].write_text(json.dumps(rules), encoding='utf-8')
            before = [hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs]
            for output in inputs:
                with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(main(['check-boundaries', str(inputs[0]), '--rules', str(inputs[1]), '--output', str(output)]), 2)
            self.assertEqual(before, [hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs])
