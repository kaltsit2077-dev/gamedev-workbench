import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import contextlib
import io

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('paired',ROOT/'tools/paired_eval.py')
p=importlib.util.module_from_spec(spec); spec.loader.exec_module(p)

class PairedPreparationTests(unittest.TestCase):
    def test_equal_inputs_and_refuse_overwrite(self):
        self.assertIsNone(p.experiment_context()['experiment_metadata'])
        self.assertIn('unverified',p.experiment_context()['model_configuration'])
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'prepared'
            result=p.prepare(out)
            self.assertTrue(result['task_inputs_identical'])
            a={f.name:f.read_bytes() for f in (out/'arm-a').iterdir()}
            b={f.name:f.read_bytes() for f in (out/'arm-b').iterdir()}
            self.assertEqual(a,b)
            with self.assertRaises(ValueError): p.prepare(out)
    def test_failed_grading_has_failure_exit(self):
        with patch.object(p.sys,'argv',['paired_eval.py','grade','--engine','fake','--artifacts','fake','--output','fake']):
            with patch.object(p,'grade',return_value={'records':[{'passed':False}]}):
                with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(p.main(),1)

if __name__=='__main__': unittest.main()
