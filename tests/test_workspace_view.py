import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'skills/gamedev-workbench/scripts'))
from creative_workspace import create_workspace
from workspace_view import export_workspace, render_workspace


class WorkspaceViewTests(unittest.TestCase):
    def test_task_snapshot_does_not_execute_or_inject_untrusted_html(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve(); brief = json.loads((ROOT/'skills/gamedev-workbench/assets/design/brief.json').read_text(encoding='utf-8'))
            brief['title'] = '</script><script>bad()</script>'
            create_workspace(brief, root/'pack')
            result = export_workspace(root/'pack', root/'view.html')
            text = (root/'view.html').read_text(encoding='utf-8')
            self.assertNotIn(brief['title'], text); self.assertIn('sha256', text)
            self.assertEqual(result['state'], 'draft'); self.assertFalse(result['engine_started'])
            with self.assertRaises(FileExistsError): export_workspace(root/'pack', root/'view.html')
            with self.assertRaises(FileExistsError): export_workspace(root/'pack', root/'pack/brief.json')
            (root/'pack/design/experience.md').write_text('x'*64001, encoding='utf-8')
            with self.assertRaises(ValueError): render_workspace(root/'pack')
