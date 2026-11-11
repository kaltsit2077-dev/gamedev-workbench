import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import contextlib
import io
from unittest.mock import patch

PROJECT=Path(__file__).resolve().parents[1]
SOURCE=PROJECT/'skills/gamedev-workbench'
spec=importlib.util.spec_from_file_location('workbench', SOURCE/'scripts/workbench.py')
w=importlib.util.module_from_spec(spec); spec.loader.exec_module(w)

class ToolboxTests(unittest.TestCase):
    def test_analysis_and_smoke_outputs_cannot_replace_game_files(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); config=root/'project.godot'; original='[application]\nconfig/name="Original"\n'
            config.write_text(original,encoding='utf-8')
            with contextlib.redirect_stderr(io.StringIO()),contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(w.main(['analyze-project',str(root),'--output',str(config)]),2)
                with patch.object(w,'verify_godot') as execute:
                    self.assertEqual(w.main(['verify-godot','--engine','unused','--output',str(config)]),2)
                    execute.assert_not_called()
            self.assertEqual(config.read_text(encoding='utf-8'),original)
    def test_bundle_references_and_catalog(self): self.assertEqual(w.validate(),[])
    def test_unicode_search_and_category(self):
        rows=w.search('粒子'); self.assertTrue(rows)
        self.assertTrue(all(r['tags']=='mcp' for r in w.search('', 'mcp')))
        self.assertEqual(w.search('nonexistent-unique-token'),[])
    def test_route_native_ui_and_architecture(self):
        self.assertIn('ui',w.route('原生菜单焦点'))
        self.assertIn('architecture',w.route('代码架构与依赖'))
        self.assertEqual(w.route('something unspecified'),['guide'])
    def test_english_substrings_do_not_route_ui(self):
        self.assertNotIn('ui', w.route('build a model'))
        self.assertNotIn('design', w.route('redesignation'))
        self.assertIn('ui', w.route('实现UI焦点'))
    def test_brief_selects_existing_workflows_and_sources(self):
        packet=w.brief('菜单焦点和粒子效果','godot')
        self.assertIn('ui',[m['id'] for m in packet['modes']])
        for m in packet['modes']:
            self.assertTrue((SOURCE/m['workflow']).is_file())
        self.assertTrue(packet['sources'])
        self.assertEqual(packet['execution_status'],'not-executed')
        with self.assertRaises(ValueError): w.brief('ui','godot','missing-project-dir')
    def test_brief_project_does_not_claim_patch_or_run(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); (p/'project.godot').write_text('config_version=5',encoding='utf-8')
            (p/'AGENTS.md').write_text('Project rules',encoding='utf-8')
            packet=w.brief('HUD','godot',d)
            self.assertIn('AGENTS.md',packet['project']['read_first'])
            self.assertEqual(packet['project']['engine_version'],'unknown; inspect project and actual executable')
    def test_godot_probe_rejects_wrong_engine_before_execution(self):
        with patch.object(w,'doctor',return_value={'engine_status':'version-mismatch-or-error'}):
            result=w.verify_godot('wrong-engine')
            self.assertEqual(result['headless_behavior'],'blocked')
    def test_godot_probe_rejects_script_errors_even_with_zero_exit(self):
        with patch.object(w,'doctor',return_value={'engine_status':'version-confirmed'}):
            with patch.object(w.subprocess,'run',return_value=subprocess.CompletedProcess([],0,b'SCRIPT ERROR: bad\nWORKBENCH_SMOKE: PASS',b'')):
                self.assertEqual(w.verify_godot('engine')['headless_behavior'],'failed')
    def test_official_probe_rejects_steam_and_other_patch(self):
        with patch.object(w.subprocess,'run',return_value=subprocess.CompletedProcess([],0,'4.7.2.stable.steam.hash','')):
            self.assertEqual(w.doctor(sys.executable,'4.7.2',True)['engine_status'],'version-mismatch-or-error')
    def test_mode_unknown_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'skill'; shutil.copytree(SOURCE,root)
            modes=w.modes(root); modes[0]['source_ids']=['UNKNOWN']
            (root/'catalog/modes.json').write_text(json.dumps(modes),encoding='utf-8')
            self.assertTrue(any('unknown mode source' in e for e in w.validate(root)))
    def test_missing_skill_entry_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'skill'; shutil.copytree(SOURCE,root)
            (root/'SKILL.md').unlink()
            self.assertTrue(any('missing package file: SKILL.md' in e for e in w.validate(root)))
    def test_missing_engine_never_passes(self):
        self.assertEqual(w.doctor('nonexistent-editor.exe')['engine_status'],'missing')
        self.assertEqual(w.doctor()['rendering'],'unverified')
    def test_wrong_patch_and_probe_timeout_do_not_pass(self):
        with patch.object(w.subprocess, 'run', return_value=subprocess.CompletedProcess([],0,'4.7.1.stable.official','')):
            self.assertEqual(w.doctor(sys.executable,'4.7.2')['engine_status'],'version-mismatch-or-error')
        with patch.object(w.subprocess, 'run', side_effect=subprocess.TimeoutExpired([],15)):
            self.assertEqual(w.doctor(sys.executable)['engine_status'],'probe-error')
    def test_catalog_corruption_detected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'skill'; shutil.copytree(SOURCE,root)
            records=w.catalog(root); records.append(records[0])
            (root/'catalog/resources.json').write_text(json.dumps(records),encoding='utf-8')
            self.assertTrue(any('duplicate ID' in e for e in w.validate(root)))
    def test_install_is_portable_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory(prefix='工作台 ') as d:
            plan=w.install(d); target=Path(plan['target'])
            self.assertEqual(w.validate(target),[])
            p=subprocess.run([sys.executable,str(target/'scripts/workbench.py'),'validate'],capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr)
            with self.assertRaises(ValueError): w.install(d)
    def test_install_prevents_copy_into_itself(self):
        with self.assertRaises(ValueError): w.install_plan(SOURCE/'nested')
    def test_cli_missing_id_and_version(self):
        script=str(SOURCE/'scripts/workbench.py')
        for args in [['inspect','BAD'],['doctor','--expect','4.7.2'],['doctor','--engine','nonexistent-editor.exe']]:
            p=subprocess.run([sys.executable,script,*args],capture_output=True)
            self.assertNotEqual(p.returncode,0)
    def test_shell_text_is_only_search_data(self):
        self.assertEqual(w.search('$(whoami); `test`'),[])

if __name__=='__main__': unittest.main()
