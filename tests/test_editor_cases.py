import importlib.util
from pathlib import Path
import tempfile
import json
import subprocess
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('editor_cases',ROOT/'skills/gamedev-workbench/scripts/editor_cases.py')
e=importlib.util.module_from_spec(spec); spec.loader.exec_module(e)

class EditorCaseTests(unittest.TestCase):
    def test_missing_editor_blocks_before_any_process_or_output(self):
        with tempfile.TemporaryDirectory() as d,patch.object(e.subprocess,'run') as process:
            output=Path(d)/'evidence'
            for kind in ['unity','unreal']:
                result=e.verify_editor_case(kind,None,None,d,output)
                self.assertEqual(result['status'],'blocked'); self.assertFalse(result['passed'])
            process.assert_not_called(); self.assertFalse(output.exists())
    def test_command_preserves_spaces_as_separate_arguments(self):
        project=Path('original project with spaces')
        unity=e.command_for('unity','editor exe',project,'log file')
        self.assertEqual(unity[unity.index('-projectPath')+1],str(project))
        unreal=e.command_for('unreal','editor exe',project,'log file')
        self.assertIn(str(project/'WorkbenchSmoke.uproject'),unreal)
        self.assertFalse(any('shell' in str(x) for x in unity+unreal))
    def test_zero_exit_marker_without_native_report_cannot_pass(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); editor=root/'fake-editor'; editor.write_text('unused test placeholder')
            with patch.object(e.subprocess,'run',return_value=subprocess.CompletedProcess([],0,b'WORKBENCH_EDITOR: PASS',b'')):
                report=e.verify_editor_case('unity',editor,'6000.3',root,root/'evidence')
            self.assertFalse(report['passed'])
    def test_report_version_and_exit_are_independent_gates(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); editor=root/'fake-editor'; editor.write_text('unused test placeholder')
            def mocked(command,env,**kwargs):
                Path(env['GDW_EDITOR_REPORT']).write_text(json.dumps({'engine':'unity','engine_version':'6000.3.0f1','passed':True,'checks':[{'passed':True}]}))
                return subprocess.CompletedProcess([],1,b'WORKBENCH_EDITOR: PASS',b'')
            with patch.object(e.subprocess,'run',side_effect=mocked):
                report=e.verify_editor_case('unity',editor,'6000.3',root,root/'failed-exit')
            self.assertFalse(report['passed']); self.assertTrue(report['version_confirmed'])
            with patch.object(e.subprocess,'run',side_effect=mocked):
                report=e.verify_editor_case('unity',editor,'6000.4',root,root/'wrong-version')
            self.assertFalse(report['version_confirmed'])

if __name__=='__main__': unittest.main()
