import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('engineering_eval', ROOT/'tools/engineering_eval.py')
e = importlib.util.module_from_spec(spec); spec.loader.exec_module(e)


class EngineeringEvalTests(unittest.TestCase):
    def test_archived_outputs_and_treatment_match_recorded_hashes(self):
        report = json.loads((ROOT/'docs/engineering-v08.json').read_text(encoding='utf-8'))
        for section in ['skill_files_sha256', 'artifact_sha256']:
            for name, expected in report[section].items():
                self.assertEqual(e.digest(e.FIXTURE/name), expected, name)
        for record in report['records']:
            result = json.loads((e.FIXTURE/'outputs'/record['arm']/'result.json').read_text(encoding='utf-8'))
            self.assertEqual(record['passed'], result['passed'])
            self.assertEqual(record['checks_passed'], sum(c['passed'] for c in result['checks']))
            self.assertEqual(record['checks_total'], len(result['checks']))
            self.assertIsNone(record['usage']['cost_usd'])
    def test_independent_cases_start_with_identical_real_conflicts(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d)/'prepared'
            self.assertTrue(e.prepare(output)['prepared'])
            a, b = output/'arm-a', output/'arm-b'
            self.assertEqual(e.git(a, 'rev-parse', 'HEAD').stdout, e.git(b, 'rev-parse', 'HEAD').stdout)
            self.assertEqual(e.git(a, 'ls-files', '-u').stdout, e.git(b, 'ls-files', '-u').stdout)
            self.assertTrue(e.git(a, 'ls-files', '-u').stdout)
            for name in e.git(a, 'ls-files', '-z').stdout.split(b'\0'):
                if name:
                    path = name.decode()
                    self.assertEqual((a/path).read_bytes(), (b/path).read_bytes())
            with self.assertRaises(ValueError): e.prepare(output)

    def test_changed_grader_and_driver_cannot_silently_regrade(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            fixture = root/'evals/engineering'
            shutil.copytree(e.FIXTURE, fixture)
            (root/'tools').mkdir()
            shutil.copyfile(ROOT/'tools/engineering_eval.py', root/'tools/engineering_eval.py')
            with patch.object(e, 'ROOT', root), patch.object(e, 'FIXTURE', fixture):
                e.frozen()
                grader = fixture/'grader.gd'; original = grader.read_bytes()
                grader.write_bytes(original+b'\n# changed\n')
                with self.assertRaises(ValueError): e.frozen()
                grader.write_bytes(original)
                driver = root/'tools/engineering_eval.py'
                driver.write_bytes(driver.read_bytes()+b'\n# changed\n')
                with self.assertRaises(ValueError): e.frozen()
