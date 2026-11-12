import importlib.util
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'skills/gamedev-workbench/scripts'))
from project_analysis import analyze_project
from dependency_boundaries import check_boundaries
spec = importlib.util.spec_from_file_location('architecture_case', ROOT/'tools/run_architecture_case.py')
runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)


class ArchitectureCaseTests(unittest.TestCase):
    def test_recorded_native_evidence_matches_distributed_sources(self):
        record = json.loads((ROOT/'docs/architecture-case-v010.json').read_text(encoding='utf-8'))
        for case in record['records']:
            source = ROOT/'skills/gamedev-workbench/assets/architecture-case'/case['case']
            for name, expected in case['source_sha256'].items():
                self.assertEqual(hashlib.sha256((source/name).read_bytes().replace(b'\r\n', b'\n')).hexdigest(), expected)
            self.assertEqual(case['blocking_diagnostic_count'], 0)
            self.assertTrue(case['matched_expected_result'])

    def test_same_acceptance_detects_named_boundary_before_and_not_after(self):
        base = ROOT/'skills/gamedev-workbench/assets/architecture-case'
        rules = json.loads((base/'rules.json').read_text(encoding='utf-8'))
        before = check_boundaries(analyze_project(base/'before'), rules)
        after = check_boundaries(analyze_project(base/'after'), rules)
        self.assertEqual(len(before['violations']), 1)
        self.assertEqual(before['violations'][0]['kind'], 'extends-class')
        self.assertTrue(after['passed'])
        self.assertEqual((base/'before/smoke.gd').read_bytes(), (base/'after/smoke.gd').read_bytes())
        self.assertEqual((base/'before/presentation/widget_state.gd').read_bytes(), (base/'after/presentation/widget_state.gd').read_bytes())
        # Repair removes only the inappropriate parent; gameplay remains the same.
        self.assertEqual((base/'before/domain/run_state.gd').read_text().replace('extends CaseWidgetState', 'extends RefCounted'),
                         (base/'after/domain/run_state.gd').read_text())

    def test_wrong_engine_is_rejected_before_creating_working_copies(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); engine = root/'editor'; engine.write_text('placeholder')
            with patch.object(runner.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, '4.7.1.stable.official.hash', '')):
                with self.assertRaises(ValueError): runner.run_case(engine, root/'scratch', root/'output')
            self.assertFalse((root/'scratch').exists()); self.assertFalse((root/'output').exists())
