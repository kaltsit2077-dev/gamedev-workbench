import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'skills/gamedev-workbench/scripts'))
from creative_workspace import create_workspace, check_workspace


class CreativeWorkspaceTests(unittest.TestCase):
    def brief(self): return json.loads((ROOT/'skills/gamedev-workbench/assets/design/brief.json').read_text(encoding='utf-8'))
    def test_editable_linked_pack_is_not_claimed_as_implemented(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d).resolve()/'设计 包'; result = create_workspace(self.brief(), path)
            check = check_workspace(path)
            self.assertTrue(check['passed']); self.assertEqual(check['state'], 'draft')
            self.assertFalse(result['engine_started']); self.assertEqual(result['tasks'], 8)
            with self.assertRaises(ValueError): create_workspace(self.brief(), path)
            file = path/'workspace.json'; data = json.loads(file.read_text(encoding='utf-8'))
            ui = json.loads((path/'ui/spec.json').read_text(encoding='utf-8')); ui['requirements'] = ['req-002']
            next(t for t in data['tasks'] if t['id'] == 'ui')['requirements'] = ['req-002']
            (path/'ui/spec.json').write_text(json.dumps(ui), encoding='utf-8')
            file.write_text(json.dumps(data), encoding='utf-8')
            self.assertTrue(check_workspace(path)['passed'])
            data['tasks'][0]['depends_on'] = ['verification']; file.write_text(json.dumps(data), encoding='utf-8')
            self.assertFalse(check_workspace(path)['passed'])
    def test_missing_output_escape_and_changed_requirements_fail(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d).resolve()/'pack'; create_workspace(self.brief(), path)
            (path/'ui/spec.json').unlink(); self.assertFalse(check_workspace(path)['passed'])
            file = path/'workspace.json'; data = json.loads(file.read_text(encoding='utf-8'))
            data['tasks'][0]['outputs'] = ['../outside.md']; file.write_text(json.dumps(data), encoding='utf-8')
            with self.assertRaises(ValueError): check_workspace(path)
    def test_malformed_brief_creates_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d).resolve()/'bad'; brief = self.brief(); brief['features'] = 'not a list'
            with self.assertRaises(ValueError): create_workspace(brief, path)
            self.assertFalse(path.exists())
