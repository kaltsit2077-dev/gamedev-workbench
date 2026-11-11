"""Prepare equal agent tasks, then grade their actual artifacts with a shared Godot check.
This tool does not call models and cannot retrieve token/billing telemetry.
"""
import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/'evals/paired'

def fresh_output(path):
    path=Path(path).resolve()
    if path.exists() and any(path.iterdir()): raise ValueError('Output must be new or empty')
    path.mkdir(parents=True,exist_ok=True)
    return path

def prepare(output):
    output=fresh_output(output)
    expected=json.loads((FIXTURE/'input-manifest.json').read_text())
    # Normalize platform line endings; both prepared arms still receive byte-identical copies.
    actual={p.name:hashlib.sha256(p.read_text(encoding='utf-8').encode('utf-8')).hexdigest() for p in (FIXTURE/'input').iterdir() if p.is_file()}
    if actual!=expected: raise ValueError('Original task hash mismatch')
    for arm in ['arm-a','arm-b']: shutil.copytree(FIXTURE/'input',output/arm)
    (output/'input-manifest.json').write_text(json.dumps(expected,indent=2),encoding='utf-8')
    return {'directory':str(output),'task_inputs_identical':True,'next':'Run two fresh contexts, same model/tools. A: no custom skills; B: read gamedev-workbench. Do not expose sibling outputs or grader. Record timers; then grade.'}

def experiment_context(metadata=None):
    data=json.loads(Path(metadata).read_text(encoding='utf-8')) if metadata else None
    if data is not None and not isinstance(data,dict): raise ValueError('Experiment metadata must be a JSON object')
    return {'model_configuration':data.get('model_configuration','unverified; caller must record model conditions') if data else 'unverified; caller must record model conditions',
            'experiment_metadata':data,'metadata_provenance':'caller-supplied; not verified by the grader' if data else 'not supplied'}

def grade(engine,artifacts,output,scratch=None,metadata=None):
    context=experiment_context(metadata)
    w=runpy.run_path(str(ROOT/'skills/gamedev-workbench/scripts/workbench.py'))
    probe=w['doctor'](engine,'4.7.2',official=True)
    if probe['engine_status']!='version-confirmed': raise ValueError('Matching Godot 4.7.2 official is required')
    output=fresh_output(output); artifacts=Path(artifacts).resolve()
    if scratch: Path(scratch).resolve().mkdir(parents=True,exist_ok=True)
    records=[]
    for arm in ['arm-a','arm-b']:
        source=artifacts/arm
        protected=all((source/name).read_text(encoding='utf-8')==(FIXTURE/'input'/name).read_text(encoding='utf-8') for name in ['AGENTS.md','REQUIREMENTS.md'])
        changes=[]
        for name in ['state.gd','feedback.gd','ui.gd']:
            original=(FIXTURE/'input'/name).read_text(encoding='utf-8').splitlines()
            modified=(source/name).read_text(encoding='utf-8').splitlines()
            diff=list(difflib.ndiff(original,modified))
            changes.append({'file':name,'added_lines':sum(x.startswith('+ ') for x in diff),'removed_lines':sum(x.startswith('- ') for x in diff)})
        timer=source/'.run/timing-end.json'
        timing=json.loads(timer.read_text()) if timer.is_file() else {}
        with tempfile.TemporaryDirectory(prefix='gdw-grade-',dir=scratch) as directory:
            work=Path(directory).resolve(); sample=work/'project'; data=work/'data'; data.mkdir()
            shutil.copytree(source,sample,ignore=shutil.ignore_patterns('.git','.godot','.run','grader.gd','paired_grader.gd'))
            shutil.copy2(FIXTURE/'grader.gd',sample/'paired_grader.gd')
            env=dict(os.environ,APPDATA=str(data),LOCALAPPDATA=str(data),XDG_DATA_HOME=str(data),XDG_CONFIG_HOME=str(data))
            command=[str(Path(engine).resolve()),'--headless','--path',str(sample),'--log-file',str(work/'engine.log'),'--script','res://paired_grader.gd','--',str(work/'grade.json')]
            try:
                process=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60,env=env)
                log=process.stdout.decode('utf-8',errors='replace')
                result=json.loads((work/'grade.json').read_text()) if (work/'grade.json').is_file() else {'passed':False,'checks':[]}
                errors=[line for line in log.splitlines() if line.startswith(('ERROR:','SCRIPT ERROR:')) and 'Failed to read the root certificate store.' not in line]
                result['passed']=bool(result['passed'] and process.returncode==0 and 'PAIRED_GRADER: PASS' in log and not errors)
                result['exit_code']=process.returncode
            except (OSError,subprocess.TimeoutExpired,ValueError) as exc:
                result={'passed':False,'checks':[],'error':str(exc)}
        result.update(arm=arm,elapsed_seconds=timing.get('elapsed_seconds'),elapsed_source='arm-recorded first-to-last work timer',tokens=None,cost_usd=None,
                      production_changes=changes,protected_requirements_unchanged=protected,documents_present={n:(source/n).is_file() for n in ['AUDIT.md','RESULT.md']})
        result['passed']=result['passed'] and protected
        records.append(result)
    summary={'task':'one executable charge-feedback repair pilot',**context,
             'engine_version':probe['engine_version'],'records':records,
             'limits':['One pair is not a statistical productivity study.','Model configuration and isolation require external protocol records; the grader cannot verify them.','Wall timers are arm-recorded and include tools/environment; they are not model-only latency.','Token usage and actual fees are not exposed.','Behavioral grading does not replace independent human blind quality review.']}
    (output/'results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    return summary

def main():
    parser=argparse.ArgumentParser(description=__doc__); sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('prepare'); p.add_argument('--output',required=True)
    p=sub.add_parser('grade'); p.add_argument('--engine',required=True); p.add_argument('--artifacts',required=True); p.add_argument('--output',required=True); p.add_argument('--scratch'); p.add_argument('--metadata')
    args=parser.parse_args()
    result=prepare(args.output) if args.command=='prepare' else grade(args.engine,args.artifacts,args.output,args.scratch,args.metadata)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 1 if args.command=='grade' and not all(r['passed'] for r in result['records']) else 0

if __name__=='__main__': sys.exit(main())
