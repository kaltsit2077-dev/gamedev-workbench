"""Open an explicit interactive original fixture; no synthetic OS input is sent."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

def launch_manual(engine,scratch,output_dir,skill_root=None,mode='operator'):
    if mode not in {'operator','os-automation'}: raise ValueError('Unknown input-session mode')
    root=Path(skill_root) if skill_root else Path(__file__).resolve().parents[1]
    output=Path(output_dir).expanduser().resolve()
    if output.exists() and any(output.iterdir()): raise ValueError('Manual output must be new or empty')
    scratch=Path(scratch).expanduser().resolve(); scratch.mkdir(parents=True,exist_ok=True)
    work=Path(tempfile.mkdtemp(prefix='gdw-manual-',dir=scratch))
    sample=work/'sample'; shutil.copytree(root/'assets/godot-menu',sample,ignore=shutil.ignore_patterns('.godot'))
    data=work/'data'; (data/'Godot/app_userdata/Workbench menu and layered impact/logs').mkdir(parents=True)
    output.mkdir(parents=True,exist_ok=True)
    env=dict(os.environ,APPDATA=str(data),LOCALAPPDATA=str(data),XDG_DATA_HOME=str(data),XDG_CONFIG_HOME=str(data))
    command=[str(Path(engine).resolve()),'--path',str(sample),'--rendering-method','gl_compatibility',
             '--log-file',str(output/'native.log'),'--script','res://manual.gd','--',str(output/'report.json'),mode]
    with (output/'engine.log').open('wb') as log:
        process=subprocess.Popen(command,env=env,stdout=log,stderr=subprocess.STDOUT,
                                 creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    return {'status':'input-session-opened','mode':mode,'pid':process.pid,'report':str(output/'report.json'),
            'retained_scratch':str(work),'timeout_seconds':1800,'synthetic_os_input_sent':False,
            'instruction':'Use Tab and Enter to open Options; move text slider; Escape back; click Replay twice; Finish input check. Confirm actual devices separately.'}
