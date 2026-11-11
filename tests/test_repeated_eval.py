import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('repeated',ROOT/'tools/repeated_eval.py')
r=importlib.util.module_from_spec(spec); spec.loader.exec_module(r)

class RepeatedEvaluationTests(unittest.TestCase):
    def test_equal_frozen_inputs_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'trials'; r.prepare(out,2)
            expected={p.name:p.read_bytes() for p in (out/'rep-01/arm-a').iterdir()}
            for arm in ['rep-01/arm-b','rep-02/arm-a','rep-02/arm-b']:
                self.assertEqual(expected,{p.name:p.read_bytes() for p in (out/arm).iterdir()})
            with self.assertRaises(ValueError): r.prepare(out,2)
    def test_missing_context_remains_unverified(self):
        ledger_spec=importlib.util.spec_from_file_location('isolated_ledger',ROOT/'skills/gamedev-workbench/scripts/evaluation_ledger.py')
        ledger=importlib.util.module_from_spec(ledger_spec); ledger_spec.loader.exec_module(ledger)
        data={'records':[{'run_id':arm,'task':'x','repetition':1,'arm':arm,'model_configuration':'unverified; unknown',
                         'passed':True,'elapsed_seconds':1,'rework_rounds':None} for arm in ['a','b']]}
        report=ledger.summarize_evaluations(data)
        self.assertEqual(report['paired_runs'],0)
        self.assertIsNone(report['reported_measured_cost_usd_total'])

if __name__=='__main__': unittest.main()
