"""Explicit editor cases in isolated project copies; absent editors are blocked."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

def command_for(kind,editor,project,log):
    if kind=='unity':
        return [str(editor),'-batchmode','-nographics','-quit','-projectPath',str(project),'-executeMethod','WorkbenchSmoke.Run','-logFile',str(log)]
    if kind=='unreal':
        return [str(editor),str(project/'WorkbenchSmoke.uproject'),'-unattended','-NullRHI','-nosplash','-stdout',
                '-ExecutePythonScript='+str(project/'Content/Python/workbench_smoke.py'),'-abslog='+str(log)]
    raise ValueError('Editor kind must be unity or unreal')

def verify_editor_case(kind,editor,expected,scratch,output_dir,skill_root=None):
    if kind not in {'unity','unreal'}: raise ValueError('Unknown editor case')
    result={'engine':kind,'status':'blocked','passed':False,'rendering':'not-run','physical_input':'not-run',
            'limits':['Original editor-only fixture; not a gameplay/UI/rendering integration test.',
                      'The licensed editor uses its normal user environment; only project files are copied.']}
    if not editor or not Path(editor).expanduser().is_file():
        result['reason']='Editor executable not supplied or not found; no editor process started'
        return result
    if not expected or not re.fullmatch(r'[0-9A-Za-z.\-]+',expected): raise ValueError('An explicit expected editor version prefix is required')
    output=Path(output_dir).resolve()
    if output.exists() and any(output.iterdir()): raise ValueError('Output must be new or empty')
    scratch=Path(scratch).resolve(); scratch.mkdir(parents=True,exist_ok=True)
    root=Path(skill_root) if skill_root else Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix='gdw-editor-',dir=scratch) as temp:
        project=Path(temp)/'project'; shutil.copytree(root/('assets/'+kind+'-smoke'),project)
        output.mkdir(parents=True,exist_ok=True); report_path=output/'report.json'; log=output/'native.log'
        command=command_for(kind,Path(editor).resolve(),project,log)
        env=dict(os.environ,GDW_EDITOR_REPORT=str(report_path))
        try:
            process=subprocess.run(command,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=300)
            stdout=process.stdout.decode('utf-8',errors='replace')
            native=log.read_text(encoding='utf-8',errors='replace') if log.exists() else ''
            evidence=json.loads(report_path.read_text(encoding='utf-8')) if report_path.exists() else {}
            checks=evidence.get('checks',[]); version=evidence.get('engine_version','')
            confirmed=bool(re.match('^'+re.escape(expected)+r'(?:[.\-\s]|$)',version))
            passed=(process.returncode==0 and evidence.get('engine')==kind and evidence.get('passed') is True and confirmed
                    and isinstance(checks,list) and bool(checks) and all(isinstance(c,dict) and c.get('passed') is True for c in checks)
                    and 'WORKBENCH_EDITOR: PASS' in stdout+native)
            result.update(status='passed' if passed else 'failed',passed=passed,engine_version=version,
                          version_confirmed=confirmed,checks=checks,exit_code=process.returncode)
            (output/'engine.log').write_text(stdout,encoding='utf-8')
        except (OSError,ValueError,subprocess.TimeoutExpired) as error:
            result.update(status='failed',reason=type(error).__name__)
        (output/'report.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result
