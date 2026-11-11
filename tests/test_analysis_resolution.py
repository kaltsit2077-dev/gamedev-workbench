import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('project_analysis_new',ROOT/'skills/gamedev-workbench/scripts/project_analysis.py')
a=importlib.util.module_from_spec(spec); spec.loader.exec_module(a)

class SourceResolutionTests(unittest.TestCase):
    def project(self,root):
        (root/'project.godot').write_text('[application]\nrun/main_scene="uid://main"',encoding='utf-8')
        (root/'main.tscn').write_text('[gd_scene format=3 uid="uid://main"]\n[ext_resource type="Script" uid="uid://script" path="res://retired.gd" id="1"]',encoding='utf-8')
        (root/'actual.gd').write_text('extends Node',encoding='utf-8')
        (root/'actual.gd.uid').write_text('uid://script',encoding='utf-8')
    def test_uid_sidecars_headers_imports_and_fallback_disagreement(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); self.project(root)
            (root/'icon.svg').write_text('<svg/>'); (root/'icon.svg.import').write_text('[remap]\nuid="uid://icon"\n')
            (root/'load.gd').write_text('const I = preload("uid://icon")\nconst S = preload("uid://script")')
            report=a.analyze_project(root)
            self.assertEqual(report['entry_resolution'],'res://main.tscn')
            self.assertTrue(any(r['target']=='icon.svg' for r in report['references']))
            fallback=next(r for r in report['references'] if r['target']=='retired.gd')
            self.assertEqual(fallback['status'],'missing-path-with-uid-candidate')
            self.assertTrue(any(r.get('path_disagrees') for r in report['uid_references']))
    def test_ambiguous_and_unknown_uids_not_guessed(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); self.project(root)
            (root/'other.gd').write_text('extends Node'); (root/'other.gd.uid').write_text('uid://script')
            (root/'load.gd').write_text('const S=preload("uid://script")\nconst X=load("uid://unknown")')
            report=a.analyze_project(root)
            self.assertEqual(len(report['uid_conflicts']),1)
            self.assertTrue(any(r['status']=='unknown' for r in report['uid_references']))
            self.assertFalse(any(r['source']=='load.gd' for r in report['references']))
    def test_finite_paths_shadowing_and_local_write_false_positive(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); self.project(root)
            (root/'load.gd').write_text('const BASE="res://"\nconst NAME="actual"\nconst HASH="res://has#tag.tres" # comment\nvar count=0\nfunc safe():\n var a=load(BASE + NAME + ".gd")\n var b=load("res://%s.gd" % NAME)\n var c=load(HASH)\nfunc unsafe(BASE: String):\n var count=3\n count += 1\n var d=load(BASE + NAME)\n self.count += 1\n',encoding='utf-8')
            report=a.analyze_project(root)
            actual=[r for r in report['references'] if r['source']=='load.gd' and r['kind']=='load']
            self.assertEqual([r['target'] for r in actual],['actual.gd','actual.gd','has#tag.tres'])
            self.assertEqual(len([r for r in report['dynamic_references'] if r['source']=='load.gd' and r['kind']=='load']),1)
            self.assertFalse(any(r['target']=='count' for r in report['state_write_clues']))
            self.assertTrue(any(r['target']=='self.count' for r in report['state_write_clues']))
    def test_multiline_parameter_and_custom_loader_do_not_become_resource_edges(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); self.project(root)
            (root/'load.gd').write_text('const PATH="res://actual.gd"\nfunc go(\n PATH: String\n):\n var x=load(PATH)\n var y=custom.load("res://custom-format.dat")\n',encoding='utf-8')
            report=a.analyze_project(root)
            self.assertFalse(any(r['source']=='load.gd' and r['kind']=='load' for r in report['references']))
            self.assertTrue(any(r['source']=='load.gd' for r in report['dynamic_references']))

if __name__=='__main__': unittest.main()
