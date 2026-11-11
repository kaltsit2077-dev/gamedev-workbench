import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('tool_value', ROOT/'tools/evaluate_tool_value.py')
v = importlib.util.module_from_spec(spec); spec.loader.exec_module(v)


class ValueProtocolTests(unittest.TestCase):
    def test_protocol_is_frozen_and_does_not_claim_model_comparison(self):
        data = v.frozen_protocol()
        self.assertEqual([r['id'] for r in data['tasks']], ['architecture', 'menu', 'effects'])
        self.assertTrue(any('neither arm is a model' in limit for limit in data['limits']))
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for path in [*data['source_sha256'], 'evals/tool-value/protocol.json']:
                target = root/path; target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(ROOT/path, target)
            target = root/'skills/gamedev-workbench/assets/godot-menu/menu.gd'
            target.write_text('# changed', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'source changed'): v.frozen_protocol(root)
