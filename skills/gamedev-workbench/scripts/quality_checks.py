"""Run only the bundled original sample, with explicit output and isolated state."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

def check_sample(engine, output_dir, scratch=None, graphical=False, skill_root=None,case='basic'):
    root=Path(skill_root) if skill_root else Path(__file__).resolve().parents[1]
    output=Path(output_dir).expanduser().resolve()
    if output.exists() and any(output.iterdir()): raise ValueError('Output directory must be empty or new')
    if scratch: Path(scratch).expanduser().resolve().mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='gdw-quality-',dir=scratch) as temporary:
        work=Path(temporary).resolve(); sample=work/'sample'; evidence=work/'evidence'; evidence.mkdir()
        if case not in {'basic','menu'}: raise ValueError('Unknown original sample case')
        shutil.copytree(root/('assets/godot-menu' if case=='menu' else 'assets/godot-demo'),sample,ignore=shutil.ignore_patterns('.godot'))
        name='Workbench menu and layered impact' if case=='menu' else 'Workbench isolated demo'
        data=work/'data'; (data/'Godot/app_userdata'/name/'logs').mkdir(parents=True)
        env=dict(os.environ,APPDATA=str(data),LOCALAPPDATA=str(data),XDG_DATA_HOME=str(data),XDG_CONFIG_HOME=str(data))
        command=[str(Path(engine).expanduser().resolve()),'--path',str(sample),'--log-file',str(work/'engine.log')]
        command += ['--rendering-method','gl_compatibility'] if graphical else ['--headless']
        command += ['--script','res://quality.gd','--',str(evidence/'report.json')]
        if graphical: command.append('capture')
        try:
            process=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=90,env=env)
            log=process.stdout.decode('utf-8',errors='replace')
        except (OSError,subprocess.TimeoutExpired) as exc:
            return {'passed':False,'error':str(exc),'rendering':'unverified'}
        diagnostics=[line for line in log.splitlines() if line.startswith(('ERROR:','SCRIPT ERROR:')) or 'leaked at exit' in line or 'was leaked' in line]
        blocking=[line for line in diagnostics if line.strip()!='ERROR: Failed to read the root certificate store.']
        report=json.loads((evidence/'report.json').read_text(encoding='utf-8')) if (evidence/'report.json').is_file() else {'passed':False,'error':'engine report missing'}
        report.update(exit_code=process.returncode,diagnostics=diagnostics)
        report['passed']=bool(report['passed'] and process.returncode==0 and not blocking and 'WORKBENCH_QUALITY: PASS' in log)
        output.mkdir(parents=True,exist_ok=True)
        # Only known evidence files from our own sample, not arbitrary project files.
        for path in evidence.iterdir():
            if path.suffix in {'.png','.json'} and path.is_file(): shutil.copy2(path,output/path.name)
        (output/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        (output/'engine.log').write_text(log,encoding='utf-8')
        return report
