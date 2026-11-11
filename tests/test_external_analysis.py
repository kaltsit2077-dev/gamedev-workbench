import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('external_eval', ROOT/'tools/evaluate_external_analysis.py')
e = importlib.util.module_from_spec(spec); spec.loader.exec_module(e)


class ExternalAnalysisTests(unittest.TestCase):
    def test_frozen_sources_and_labels_cannot_silently_drift(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)/'fixture'; shutil.copytree(ROOT/'evals/analysis-external', root)
            source = root/'sources/2d/platformer/player/gun.gd'
            source.write_text(source.read_text(encoding='utf-8')+'\n# changed\n', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'hash mismatch'): e.evaluate(root)
    def test_external_result_keeps_runtime_and_human_review_limits(self):
        result = e.evaluate()
        self.assertEqual(result['file_count'], 8)
        self.assertEqual(len(result['unmodeled_runtime_inputs']), 2)
        self.assertIn('pending', result['human_review'])
        self.assertEqual(result['true_positive_references']+result['false_negative_references'], 7)
