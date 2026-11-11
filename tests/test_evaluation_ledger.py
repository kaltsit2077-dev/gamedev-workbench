import copy
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('ledger',ROOT/'skills/gamedev-workbench/scripts/evaluation_ledger.py')
l=importlib.util.module_from_spec(spec); spec.loader.exec_module(l)

class LedgerTests(unittest.TestCase):
    def rows(self):
        return {'records':[{'run_id':arm,'task':'original','repetition':1,'arm':arm,'model_configuration':'same declared model',
                 'passed':True,'elapsed_seconds':seconds,'rework_rounds':0,'usage':{'source':'unavailable'}} for arm,seconds in [('a',10),('b',12)]]}
    def test_missing_cost_stays_unknown_and_estimate_is_excluded(self):
        data=self.rows(); report=l.summarize_evaluations(data)
        self.assertEqual(report['paired_runs'],1); self.assertEqual(report['median_b_minus_a_seconds'],2)
        self.assertIsNone(report['reported_measured_cost_usd_total'])
        data['records'][0]['usage']={'source':'estimate','cost_usd':3}
        self.assertIsNone(l.summarize_evaluations(data)['reported_measured_cost_usd_total'])
    def test_traceable_reported_cost_and_mismatched_models(self):
        data=self.rows()
        for row in data['records']: row['usage']={'source':'provider_record','cost_usd':0.1,'reference':'original provider export id'}
        self.assertAlmostEqual(l.summarize_evaluations(data)['reported_measured_cost_usd_total'],0.2)
        data['records'][1]['model_configuration']='different model'
        self.assertEqual(l.summarize_evaluations(data)['paired_runs'],0)
    def test_invalid_fees_and_duplicate_pairs_are_rejected(self):
        for usage in [{'source':'unavailable','cost_usd':0},{'source':'provider_record','cost_usd':1},
                      {'source':'estimate','cost_usd':float('nan')},{'source':[]},
                      {'source':'provider_record','reference':'x','cost_usd':10**1000},
                      {'source':'provider_record','reference':'x','input_tokens':True}]:
            data=self.rows(); data['records'][0]['usage']=usage
            with self.assertRaises(ValueError): l.summarize_evaluations(data)
        data=self.rows(); data['records'].append(copy.deepcopy(data['records'][0]))
        with self.assertRaises(ValueError): l.summarize_evaluations(data)

if __name__=='__main__': unittest.main()
