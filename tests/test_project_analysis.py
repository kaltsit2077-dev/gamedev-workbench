from pathlib import Path
import hashlib
import importlib.util
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/'skills/gamedev-workbench/scripts/project_analysis.py'
spec=importlib.util.spec_from_file_location('analysis',SCRIPT)
a=importlib.util.module_from_spec(spec); spec.loader.exec_module(a)

class ReadOnlyAnalysisTests(unittest.TestCase):
    def project(self,root):
        (root/'project.godot').write_text('[application]\nrun/main_scene="res://main.tscn"\nconfig/features=PackedStringArray("4.7")\n[autoload]\nGlobal="*res://a.gd"',encoding='utf-8')
        (root/'main.tscn').write_text('[ext_resource type="Script" path="res://a.gd" id="1"]',encoding='utf-8')
        (root/'a.gd').write_text('extends Node\nvar count = 0\nconst X = preload("res://b.gd")\n# preload("res://fake.gd")\nvar doc = """\npreload("res://fake2.gd")\n"""\nfunc tick():\n count += 1\n other.position = Vector2.ZERO\n var text = "count = 88"\n var path = load(dynamic_path)\n',encoding='utf-8')
        (root/'b.gd').write_text('extends "res://a.gd"',encoding='utf-8')
    def test_entry_edges_writes_cycles_and_read_only(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); self.project(root)
            before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.iterdir()}
            result=a.analyze_project(root)
            self.assertEqual(result['entry'],'res://main.tscn')
            self.assertEqual(result['autoloads'][0]['name'],'Global')
            targets=[e['target'] for e in result['references']]
            self.assertNotIn('fake.gd',targets); self.assertNotIn('fake2.gd',targets)
            self.assertTrue(result['cycles'])
            writes=result['state_write_clues']
            self.assertTrue(any(w['target']=='count' and w['operator']=='+=' for w in writes))
            self.assertFalse(any('88' in str(w) for w in writes))
            self.assertTrue(result['dynamic_references'])
            self.assertEqual(before,{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.iterdir()})
    def test_scope_limits_and_missing(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); self.project(root)
            for directory in ['tests','addons','.cache','ignored']:
                (root/directory).mkdir(); (root/directory/'skip.gd').write_text('var secret = 1')
            (root/'ignored/.gdignore').write_text('')
            (root/'.hidden.gd').write_text('var hidden = 1')
            result=a.analyze_project(root,max_files=1)
            self.assertEqual(len(result['files']),1)
            self.assertTrue(result['warnings'])
            result=a.analyze_project(root)
            self.assertFalse(any('skip.gd' in p for p in result['files']))
            self.assertNotIn('.hidden.gd',result['files'])
            self.assertIn('tests/skip.gd',a.analyze_project(root,include_tests=True)['files'])
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/'project.godot').write_text('[application]')
            (root/'a.gd').write_text('extends Node')
            (root/'nested').mkdir(); (root/'nested/b.gd').write_text('extends Node')
            # Hitting the cap at the root must not silently drop an entire subtree.
            self.assertTrue(a.analyze_project(root,max_files=1)['warnings'])
        with self.assertRaises(ValueError): a.analyze_project('nonexistent-project')
    def test_escaping_and_dynamic_paths(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); self.project(root)
            (root/'a.gd').write_text('const A = preload("res://../outside.gd")\nvar b=load("res://prefix/"+file)\nvar c=load("res://%s.tres" % id)',encoding='utf-8')
            result=a.analyze_project(root)
            self.assertEqual(result['references'][0]['status'],'outside-project')
            self.assertEqual(len(result['dynamic_references']),2)
    def test_symlinks_are_not_traversed(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as other:
            root=Path(d); self.project(root); external=Path(other)
            (external/'private.gd').write_text('var secret=1')
            try: (root/'link').symlink_to(external,target_is_directory=True)
            except OSError: self.skipTest('Symlink creation unavailable on this host')
            self.assertFalse(any('private' in p for p in a.analyze_project(root)['files']))

if __name__=='__main__': unittest.main()
