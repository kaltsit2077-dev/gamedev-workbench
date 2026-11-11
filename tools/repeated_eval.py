"""Grade frozen original transaction tasks; does not call models or billing APIs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]; FIXTURE=ROOT/'evals/transactions'

def frozen_inputs():
    expected=json.loads((FIXTURE/'input-manifest.json').read_text(encoding='utf-8'))
    actual={p.name:hashlib.sha256(p.read_text(encoding='utf-8').encode()).hexdigest() for p in (FIXTURE/'input').iterdir() if p.is_file()}
    protocol=json.loads((FIXTURE/'protocol.json').read_text(encoding='utf-8'))
    if actual!=expected or hashlib.sha256((FIXTURE/'grader.py').read_text(encoding='utf-8').encode()).hexdigest()!=protocol['grader_sha256']:
        raise ValueError('Frozen task/grader hash mismatch')
    return expected,protocol

def prepare(output,repetitions=2):
    frozen_inputs(); output=Path(output)
    if not 1<=repetitions<=20: raise ValueError('repetitions must be 1..20')
    if output.exists(): raise ValueError('Preparation output must not exist')
    for index in range(1,repetitions+1):
        for arm in ['a','b']: shutil.copytree(FIXTURE/'input',output/f'rep-{index:02d}'/f'arm-{arm}',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    return {'prepared':True,'repetitions':repetitions,'next':'Dispatch independent contexts with identical model/tools; A no custom skill, B selected version. Record actual timers and any provider usage export. Never expose the common grader.'}

def grade(artifacts,output,metadata=None):
    expected,protocol=frozen_inputs(); artifacts=Path(artifacts); output=Path(output)
    if output.exists(): raise ValueError('Grading output must not exist')
    context=json.loads(Path(metadata).read_text(encoding='utf-8')) if metadata else {}
    if not isinstance(context,dict): raise ValueError('Run metadata must be an object')
    records=[]
    folders=sorted(artifacts.glob('rep-*/arm-*'))
    if not folders or len(folders)>40: raise ValueError('Expected 1..20 pairs')
    for source in folders:
        protected=all(hashlib.sha256((source/n).read_text(encoding='utf-8').encode()).hexdigest()==expected[n] for n in ['AGENTS.md','REQUIREMENTS.md'])
        timer=json.loads((source/'.run/timing-end.json').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory(prefix='gdw-transaction-grade-') as d:
            work=Path(d); shutil.copy2(source/'settings.py',work/'settings.py')
            try:
                process=subprocess.run([sys.executable,str(FIXTURE/'grader.py'),str(work)],capture_output=True,text=True,
                                       timeout=30,env=dict(os.environ,PYTHONUTF8='1'))
                lines=[line for line in process.stdout.splitlines() if line.startswith('EVAL_RESULT:')]
                verdict=json.loads(lines[-1].split(':',1)[1]) if len(lines)==1 else {'passed':False,'checks':[]}
                passed=protected and process.returncode==0 and verdict.get('passed') is True
            except (OSError,ValueError,subprocess.TimeoutExpired): verdict={'passed':False,'checks':[]}; passed=False
        name=source.parent.name+'/'+source.name
        records.append({'run_id':name,'task':'settings-transaction-v1','repetition':int(source.parent.name.removeprefix('rep-')),
                        'arm':source.name.removeprefix('arm-'),'model_configuration':context.get('model_configuration','unverified; run metadata not supplied'),
                        'skill_version':context.get('skill_version') if source.name=='arm-b' else None,
                        'passed':passed,'checks':verdict['checks'],'protected_requirements_unchanged':protected,
                        'elapsed_seconds':timer['elapsed_seconds'],'rework_rounds':context.get('rework_rounds_by_run',{}).get(name),
                        'rework_scope':'caller-recorded rounds after common grading; unknown if not supplied',
                        'usage':context.get('usage_by_run',{}).get(name,{'source':'unavailable','input_tokens':None,'output_tokens':None,'cost_usd':None})})
    result={'protocol_snapshot':protocol,'run_metadata':context,'records':records}
    sys.path.insert(0,str(ROOT/'skills/gamedev-workbench/scripts'))
    from evaluation_ledger import summarize_evaluations
    result['summary']=summarize_evaluations(result)
    output.mkdir(parents=True); (output/'results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__); sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('prepare'); p.add_argument('--output',required=True); p.add_argument('--repetitions',type=int,default=2)
    p=sub.add_parser('grade'); p.add_argument('--artifacts',required=True); p.add_argument('--output',required=True); p.add_argument('--metadata')
    args=parser.parse_args(); result=prepare(args.output,args.repetitions) if args.command=='prepare' else grade(args.artifacts,args.output,args.metadata)
    print(json.dumps(result,indent=2)); return 1 if args.command=='grade' and not all(r['passed'] for r in result['records']) else 0

if __name__=='__main__': raise SystemExit(main())
