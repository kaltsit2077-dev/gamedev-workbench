from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'skills/gamedev-workbench/scripts'))
from project_analysis import analyze_project
from dependency_boundaries import check_boundaries
from analysis_reports import render_analysis,compare_analysis


class NamedInheritanceTests(unittest.TestCase):
    def project(self, root):
        (root/'project.godot').write_text('[application]\nconfig/name="Case"\n', encoding='utf-8')
        (root/'base.gd').write_text('class_name CaseBase\nextends RefCounted\n', encoding='utf-8')

    def test_named_and_inline_bases_become_real_source_edges(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self.project(root)
            (root/'child.gd').write_text('extends CaseBase # comment\n', encoding='utf-8')
            (root/'inline.gd').write_text('class_name CaseInline extends CaseBase\n', encoding='utf-8')
            (root/'path.gd').write_text('class_name CasePath extends "res://base.gd"\n', encoding='utf-8')
            report = analyze_project(root)
            named = [r for r in report['references'] if r['kind'] == 'extends-class']
            self.assertEqual({(r['source'], r['target']) for r in named}, {('child.gd', 'base.gd'), ('inline.gd', 'base.gd')})
            self.assertTrue(any(r['source'] == 'path.gd' and r['kind'] == 'extends' for r in report['references']))
            rules = {'schema_version': 1, 'modules': [
                {'id': 'base', 'paths': ['base.gd'], 'allow': []},
                {'id': 'consumer', 'paths': ['child.gd', 'inline.gd', 'path.gd'], 'allow': []}]}
            self.assertEqual(len(check_boundaries(report, rules)['violations']), 3)

    def test_comments_strings_inner_classes_and_unindexed_bases_are_not_guessed(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self.project(root)
            (root/'noise.gd').write_text('extends Node\n# extends CaseBase\nvar text="""\nclass_name FalseGlobal\nextends CaseBase\n"""\nclass Inner:\n\textends CaseBase\n', encoding='utf-8')
            (root/'external.gd').write_text('extends NotScanned\n', encoding='utf-8')
            report = analyze_project(root)
            self.assertFalse(any(r['kind'] == 'extends-class' for r in report['references']))
            self.assertNotIn('FalseGlobal', [r['name'] for r in report['class_definitions']])
            self.assertTrue(any(r['name'] == 'NotScanned' and r['status'] == 'unindexed' for r in report['class_references']))

    def test_duplicate_global_name_remains_uncertain(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self.project(root)
            (root/'child.gd').write_text('extends CaseBase\n', encoding='utf-8')
            before = analyze_project(root)
            (root/'other.gd').write_text('class_name CaseBase\nextends RefCounted\n', encoding='utf-8')
            report = analyze_project(root)
            self.assertFalse(any(r['kind'] == 'extends-class' for r in report['references']))
            self.assertTrue(any(r['status'] == 'ambiguous' for r in report['class_references']))
            rules = {'schema_version': 1, 'modules': [{'id': 'all', 'paths': ['base.gd', 'other.gd', 'child.gd'], 'allow': []}]}
            result = check_boundaries(report, rules)
            self.assertEqual(result['status'], 'partial')
            self.assertTrue(any(r['kind'] == 'class-reference' for r in result['unknowns']))
            self.assertTrue(any(r['status'] == 'ambiguous' for r in compare_analysis(before,report)['class_clues_added']))
            invalid = dict(report); invalid['class_references'] = [None]
            with self.assertRaises(ValueError): render_analysis(invalid)

    def test_local_alias_is_not_resolved_as_a_global_class(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self.project(root)
            (root/'alias.gd').write_text('extends CaseBase\nconst CaseBase=preload("res://base.gd")\n', encoding='utf-8')
            report = analyze_project(root)
            self.assertFalse(any(r['kind'] == 'extends-class' for r in report['references']))
            self.assertTrue(any(r['status'] == 'shadowed' for r in report['class_references']))
