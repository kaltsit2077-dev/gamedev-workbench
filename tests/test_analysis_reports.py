import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('analysis_reports',ROOT/'skills/gamedev-workbench/scripts/analysis_reports.py')
r=importlib.util.module_from_spec(spec); spec.loader.exec_module(r)

def snapshot():
    return {'format_version':1,'engine':'godot','entry':'res://main.tscn','autoloads':[],
            'scope':{'max_files':3000},'warnings':[],'files':['a.gd'],
            'source_fingerprints':{'a.gd':'old'},'references':[], 'state_write_clues':[],
            'dynamic_references':[],'cycles':[],'limits':['No AST resolution']}

class AnalysisReportTests(unittest.TestCase):
    def test_comparison_tracks_structural_changes_without_line_noise(self):
        before=snapshot()
        before['references']=[{'source':'a.gd','target':'b.gd','kind':'load','status':'exists','line':3}]
        before['state_write_clues']=[{'file':'a.gd','method':'tick','target':'self.hp','operator':'-=','line':5}]
        after=copy.deepcopy(before); after['source_fingerprints']['a.gd']='new'
        after['source_fingerprints']['b.gd']='new'; after['files'].append('b.gd')
        after['references'][0]['line']=30; after['state_write_clues'][0]['line']=50
        after['references'].append({'source':'b.gd','target':'lost.tres','kind':'load','status':'missing'})
        after['cycles']=[['a.gd','b.gd','a.gd']]
        after['uid_references']=[{'source':'a.gd','uid':'uid://unknown','status':'unknown','candidates':[]}]
        result=r.compare_analysis(before,after)
        self.assertEqual(result['files_modified'],['a.gd'])
        self.assertEqual(result['files_added'],['b.gd'])
        self.assertEqual(len(result['references_added']),1)
        self.assertEqual(result['write_clues_added'],[])
        self.assertEqual(len(result['new_unresolved_references']),1)
        self.assertEqual(len(result['cycles_added']),1)
        self.assertEqual(len(result['uid_clues_added']),1)
        self.assertTrue(result['scope_comparable'])
        self.assertEqual(r.compare_analysis(before,before)['files_modified'],[])
    def test_scope_warnings_and_rotated_cycles(self):
        before=snapshot(); before['cycles']=[['a','b','a']]
        after=copy.deepcopy(before); after['cycles']=[['b','a','b']]
        after['scope']['max_files']=1
        self.assertFalse(r.compare_analysis(before,after)['scope_comparable'])
        self.assertEqual(r.compare_analysis(before,after)['cycles_added'],[])
        after=copy.deepcopy(before); after['warnings']=['partial']
        self.assertFalse(r.compare_analysis(before,after)['scope_comparable'])
    def test_rendering_bounds_and_escapes_untrusted_names(self):
        data=snapshot(); hostile='<script>x</script> | [link](https://bad)\n# injected'
        data['entry']=hostile
        data['references']=[{'source':hostile,'target':'b.gd','kind':'load','status':'missing'}]*4
        text=r.render_analysis(data,max_rows=1)
        self.assertNotIn('<script>',text); self.assertNotIn('\n# injected',text)
        self.assertNotIn('[link](https://bad)',text)
        self.assertIn('省略 3',text)
        with self.assertRaises(ValueError): r.render_analysis(data,max_rows=0)
    def test_invalid_reports_and_existing_outputs_are_refused(self):
        with self.assertRaises(ValueError): r.compare_analysis({},snapshot())
        with tempfile.TemporaryDirectory() as d:
            file=Path(d)/'report.json'; original=json.dumps(snapshot())
            file.write_text(original,encoding='utf-8')
            r.render_analysis(r.read_analysis(file))
            with self.assertRaises(FileExistsError): r.write_new(file,'replacement')
            self.assertEqual(file.read_text(encoding='utf-8'),original)

if __name__=='__main__': unittest.main()
