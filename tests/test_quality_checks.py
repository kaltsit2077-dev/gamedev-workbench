import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import json

ROOT=Path(__file__).resolve().parents[1]/'skills/gamedev-workbench'
spec=importlib.util.spec_from_file_location('quality',ROOT/'scripts/quality_checks.py')
q=importlib.util.module_from_spec(spec); spec.loader.exec_module(q)

class QualityRunnerTests(unittest.TestCase):
    def test_existing_output_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)/'out'; output.mkdir(); marker=output/'keep'; marker.write_text('original')
            with self.assertRaises(ValueError): q.check_sample('unused',output,skill_root=ROOT)
            self.assertEqual(marker.read_text(),'original')
    def test_missing_engine_report_cannot_pass(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.object(q.subprocess,'run',return_value=subprocess.CompletedProcess([],0,b'WORKBENCH_QUALITY: PASS',b'')):
                result=q.check_sample('fake',Path(d)/'out',skill_root=ROOT)
            self.assertFalse(result['passed'])
    def test_timeout_and_script_error_are_failed(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.object(q.subprocess,'run',side_effect=subprocess.TimeoutExpired([],90)):
                self.assertFalse(q.check_sample('fake',Path(d)/'timeout',skill_root=ROOT)['passed'])
            def fake(command,**kwargs):
                report=Path(command[command.index('--')+1])
                report.write_text(json.dumps({'passed':True,'checks':[]}))
                return subprocess.CompletedProcess([],0,b'SCRIPT ERROR: broken\nWORKBENCH_QUALITY: PASS',b'')
            with patch.object(q.subprocess,'run',side_effect=fake):
                self.assertFalse(q.check_sample('fake',Path(d)/'broken',skill_root=ROOT)['passed'])
            def leaked(command,**kwargs):
                report=Path(command[command.index('--')+1])
                report.write_text(json.dumps({'passed':True,'checks':[]}))
                return subprocess.CompletedProcess([],0,b'WARNING: ObjectDB instances were leaked at exit\nWORKBENCH_QUALITY: PASS',b'')
            with patch.object(q.subprocess,'run',side_effect=leaked):
                self.assertFalse(q.check_sample('fake',Path(d)/'leaked',skill_root=ROOT)['passed'])
    def test_success_evidence_is_preserved_and_source_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            before=(ROOT/'assets/godot-demo/demo.gd').read_bytes()
            def fake(command,**kwargs):
                report=Path(command[command.index('--')+1])
                report.write_text(json.dumps({'passed':True,'checks':[{'passed':True}]}))
                return subprocess.CompletedProcess([],0,b'WORKBENCH_QUALITY: PASS',b'')
            out=Path(d)/'out'
            with patch.object(q.subprocess,'run',side_effect=fake): result=q.check_sample('fake',out,skill_root=ROOT)
            self.assertTrue(result['passed']); self.assertTrue((out/'engine.log').exists())
            self.assertEqual((ROOT/'assets/godot-demo/demo.gd').read_bytes(),before)

if __name__=='__main__': unittest.main()
