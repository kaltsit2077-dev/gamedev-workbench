"""Offline GameDev Workbench. Python 3.11+, standard library only."""
import argparse
import json
import re
import shutil
import subprocess
import sys
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(__file__).resolve().parent))

def modes(root=ROOT):
    return json.loads((root/'catalog/modes.json').read_text(encoding='utf-8'))

def catalog(root=ROOT):
    records = json.loads((root / 'catalog/resources.json').read_text(encoding='utf-8'))
    if not isinstance(records, list):
        raise ValueError('catalog must be an array')
    return records

def search(query='', category=None, root=ROOT):
    terms = query.casefold().split()
    return [r for r in catalog(root) if (not category or r['tags'] == category)
            and all(term in json.dumps(r, ensure_ascii=False).casefold() for term in terms)]

def route(task):
    task = task.casefold()
    def matches(word):
        if word.isascii():
            return re.search(r'(?<![a-z0-9_])'+re.escape(word)+r's?(?![a-z0-9_])',task) is not None
        return word in task
    scores = [(m['id'],sum(matches(word) for word in m['keywords'])) for m in modes()]
    return [mode for mode, score in sorted(scores, key=lambda pair: -pair[1]) if score] or ['guide']

def brief(task, engine='godot', project=None):
    if engine not in {'godot','unity','unreal','web','blender'}:
        raise ValueError('Unsupported engine mapping: '+engine)
    selected=route(task)
    selected_modes=[next(m for m in modes() if m['id']==key) for key in selected]
    ids={rid for m in selected_modes for rid in m['source_ids']}
    result={'task':task,'engine':engine,'modes':selected_modes,
            'adapter':f'references/adapters/{engine}.md',
            'sources':[r for r in catalog() if r['id'] in ids],
            'read_first':['project rules and current decisions before external templates'],
            'execution_status':'not-executed',
            'instruction':'Paths are relative to the installed skill. Read selected workflows; produce their templates and actual verification evidence. Keyword routing requires agent judgment.'}
    if project:
        path=Path(project).expanduser().resolve()
        if not path.is_dir(): raise ValueError('Project directory does not exist')
        result['project']={'name':path.name,'read_first':[p for p in ['AGENTS.md','CODE_MAP.md','CONTEXT.md'] if (path/p).is_file()],
                           'detected_markers':[p for p in ['project.godot','ProjectSettings/ProjectVersion.txt','package.json'] if (path/p).is_file()]+[p.name for p in path.glob('*.uproject')],
                           'engine_version':'unknown; inspect project and actual executable'}
    return result

def doctor(engine=None, expected=None, official=False):
    report = {'python': sys.version.split()[0], 'catalog_available': (ROOT/'catalog/resources.json').is_file(),
              'engine_status': 'not-requested', 'rendering': 'unverified', 'behavior': 'unverified'}
    if engine:
        path = Path(engine).expanduser().resolve()
        if not path.is_file():
            report.update(engine_status='missing', engine_path=str(path))
            return report
        try:
            p = subprocess.run([str(path), '--version'], capture_output=True, text=True, timeout=15)
            version = (p.stdout or p.stderr).strip()
            matched = (not expected or re.match(r'^'+re.escape(expected)+r'(?:\.|\s|$)', version) is not None) and (not official or '.stable.official.' in version)
            report.update(engine_path=str(path), engine_version=version,
                          engine_status='version-confirmed' if p.returncode == 0 and matched else 'version-mismatch-or-error')
        except (OSError, subprocess.TimeoutExpired) as exc:
            report.update(engine_status='probe-error', error=str(exc))
    return report

def verify_godot(engine, expected='4.7.2', scratch=None):
    report={'engine':doctor(engine,expected,official=True),'headless_behavior':'blocked',
            'rendering':'unverified','native_input':'unverified','performance':'unverified'}
    if report['engine']['engine_status']!='version-confirmed': return report
    # Always run our own sample in a disposable copy, never the caller's game.
    if scratch:
        Path(scratch).expanduser().resolve().mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='gdw-godot-',dir=scratch) as directory:
        folder=Path(directory).resolve()
        sample=folder/'sample'
        shutil.copytree(ROOT/'assets/godot-demo',sample,ignore=shutil.ignore_patterns('.godot','*.tmp'))
        data=folder/'data'; data.mkdir()
        (data/'Godot/app_userdata/Workbench isolated demo/logs').mkdir(parents=True)
        env=dict(os.environ,APPDATA=str(data),LOCALAPPDATA=str(data),XDG_DATA_HOME=str(data),XDG_CONFIG_HOME=str(data))
        try:
            process=subprocess.run([str(Path(engine).expanduser().resolve()),'--headless','--path',str(sample),'--log-file',str(folder/'godot.log'),'--script','res://smoke.gd'],
                                   stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60,env=env)
            output=process.stdout.decode('utf-8',errors='replace')
            report.update(exit_code=process.returncode,log=output)
            diagnostics=[line for line in output.splitlines() if line.startswith(('ERROR:','SCRIPT ERROR:')) or 'leaked at exit' in line or 'was leaked' in line]
            blocking=[line for line in diagnostics if line.strip()!='ERROR: Failed to read the root certificate store.']
            report['diagnostics']=diagnostics
            report['headless_behavior']='passed' if process.returncode==0 and 'WORKBENCH_SMOKE: PASS' in output and not blocking else 'failed'
        except (OSError,subprocess.TimeoutExpired) as exc:
            report.update(headless_behavior='failed',error=str(exc))
    return report

def validate(root=ROOT):
    errors = []
    try:
        for name in ['SKILL.md','LICENSE','catalog/modes.json','assets/godot-demo/smoke.gd','assets/godot-demo/quality.gd','assets/godot-demo/validation_probe.gd','scripts/project_analysis.py','scripts/quality_checks.py','scripts/analysis_reports.py']:
            if not (root/name).is_file(): errors.append('missing package file: '+name)
        for name in ['gd_references.py','manual_input.py','editor_cases.py','narrative_checks.py','economy_simulation.py','asset_preflight.py','evaluation_ledger.py','evidence_gallery.py','workspace_io.py','creative_workspace.py','engine_adapters.py','project_runner.py','workspace_view.py']:
            if not (root/'scripts'/name).is_file(): errors.append('missing package script: '+name)
        for name in ['godot-menu/quality.gd','godot-menu/manual.gd','design/narrative.json','design/economy.json','unity-smoke/Assets/Editor/WorkbenchSmoke.cs','unreal-smoke/WorkbenchSmoke.uproject']:
            if not (root/'assets'/name).is_file(): errors.append('missing package case: '+name)
        records = catalog(root)
        schema = json.loads((root/'catalog/schema.json').read_text(encoding='utf-8'))['items']
        seen = set()
        for r in records:
            if not isinstance(r, dict):
                errors.append('record is not an object'); continue
            rid = r.get('id', '?')
            if rid in seen: errors.append(f'duplicate ID: {rid}')
            seen.add(rid)
            if not re.fullmatch(r'[STAEK]\d{2}', str(rid)): errors.append(f'invalid ID: {rid}')
            for key in schema['required']:
                if not isinstance(r.get(key), str) or not r.get(key): errors.append(f'{rid}: missing/non-string {key}')
            if set(r)-set(schema['properties']): errors.append(f'{rid}: unknown fields')
            if not str(r.get('url','')).startswith('https://'): errors.append(f'{rid}: invalid HTTPS source')
            if r.get('local_verification') not in {'not-run','isolated','project'}: errors.append(f'{rid}: invalid verification state')
        mode_ids=set()
        for mode in modes(root):
            if mode['id'] in mode_ids: errors.append('duplicate mode: '+mode['id'])
            mode_ids.add(mode['id'])
            for key in ['workflow','template']:
                target=(root/mode[key]).resolve()
                if not target.is_relative_to(root.resolve()) or not target.is_file(): errors.append('invalid mode path: '+mode[key])
            if not set(mode['source_ids']).issubset(seen): errors.append('unknown mode source: '+mode['id'])
        for f in root.rglob('*.md'):
            text = f.read_text(encoding='utf-8')
            for target in re.findall(r'\]\(([^)]+)\)', text):
                if '://' in target or target.startswith('#'): continue
                target = target.split('#')[0]
                resolved = (f.parent/target).resolve()
                if not resolved.is_relative_to(root.resolve()): errors.append(f'outside skill: {f.name}: {target}')
                elif not resolved.exists(): errors.append(f'broken link: {f.name}: {target}')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(str(exc))
    return errors

def install_plan(destination):
    target = Path(destination).expanduser().resolve()/'gamedev-workbench'
    if target.exists(): raise ValueError(f'Refusing to overwrite existing skill: {target}')
    if target.is_relative_to(ROOT): raise ValueError('Destination must be outside the source skill')
    return {'source': str(ROOT), 'target': str(target), 'action': 'copy self-contained skill; no third-party installers',
            'files': sum(p.is_file() for p in ROOT.rglob('*') if '__pycache__' not in p.parts)}

def install(destination):
    plan = install_plan(destination)
    errors = validate()
    if errors: raise ValueError('Source validation failed: '+'; '.join(errors))
    shutil.copytree(ROOT, plan['target'], ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    return plan

def emit(value): print(json.dumps(value, ensure_ascii=False, indent=2))

def read_document(path):
    path=Path(path)
    if path.stat().st_size>10_000_000: raise ValueError('Input JSON exceeds 10 MB')
    return json.loads(path.read_text(encoding='utf-8'))

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('search'); p.add_argument('query', nargs='?', default=''); p.add_argument('--category')
    p = sub.add_parser('inspect'); p.add_argument('id')
    p = sub.add_parser('route'); p.add_argument('task')
    p = sub.add_parser('brief'); p.add_argument('task'); p.add_argument('--engine',default='godot',choices=['godot','unity','unreal','web','blender']); p.add_argument('--project')
    p = sub.add_parser('doctor'); p.add_argument('--engine'); p.add_argument('--expect'); p.add_argument('--official',action='store_true')
    p = sub.add_parser('verify-godot'); p.add_argument('--engine',required=True); p.add_argument('--expect',default='4.7.2'); p.add_argument('--output'); p.add_argument('--scratch',help='optional writable directory for disposable run')
    p = sub.add_parser('analyze-project'); p.add_argument('project'); p.add_argument('--include-tests',action='store_true'); p.add_argument('--include-addons',action='store_true'); p.add_argument('--max-files',type=int,default=3000); p.add_argument('--output')
    p = sub.add_parser('check-ui-effects'); p.add_argument('--engine',required=True); p.add_argument('--expect',default='4.7.2'); p.add_argument('--scratch'); p.add_argument('--output-dir',required=True); p.add_argument('--graphical',action='store_true'); p.add_argument('--case',choices=['basic','menu'],default='basic')
    p = sub.add_parser('report-analysis'); p.add_argument('input'); p.add_argument('--output',required=True); p.add_argument('--max-rows',type=int,default=40)
    p = sub.add_parser('compare-analysis'); p.add_argument('before'); p.add_argument('after'); p.add_argument('--output',required=True)
    p = sub.add_parser('gallery'); p.add_argument('evidence_dir'); p.add_argument('--output',required=True)
    p = sub.add_parser('create-workspace'); p.add_argument('brief'); p.add_argument('--output',required=True)
    p = sub.add_parser('check-workspace'); p.add_argument('workspace'); p.add_argument('--output')
    p = sub.add_parser('workspace-page'); p.add_argument('workspace'); p.add_argument('--output',required=True)
    sub.add_parser('capabilities')
    p = sub.add_parser('run-adapter-case'); p.add_argument('kind',choices=['godot','unity','unreal','web','blender']); p.add_argument('--editor'); p.add_argument('--expect',required=True); p.add_argument('--scratch',required=True); p.add_argument('--output-dir',required=True)
    p = sub.add_parser('project-tests'); p.add_argument('project'); p.add_argument('--config',required=True); p.add_argument('--engine'); p.add_argument('--output-dir'); p.add_argument('--execute',action='store_true')
    p = sub.add_parser('freeze-project-tests'); p.add_argument('project'); p.add_argument('--config',required=True); p.add_argument('--output',required=True)
    p = sub.add_parser('manual-input'); p.add_argument('--engine',required=True); p.add_argument('--scratch',required=True); p.add_argument('--output-dir',required=True); p.add_argument('--mode',choices=['operator','os-automation'],default='operator')
    for command in ['check-narrative','simulate-economy','summarize-evals']:
        p=sub.add_parser(command); p.add_argument('input'); p.add_argument('--output')
    p=sub.add_parser('audit-assets'); p.add_argument('project'); p.add_argument('--manifest',required=True); p.add_argument('--output')
    p=sub.add_parser('verify-editor-case'); p.add_argument('editor_kind',choices=['unity','unreal']); p.add_argument('--editor'); p.add_argument('--expect'); p.add_argument('--scratch',default=tempfile.gettempdir()); p.add_argument('--output-dir',required=True)
    sub.add_parser('validate')
    for name in ['install-plan','install']:
        p = sub.add_parser(name); p.add_argument('--dest', required=True, help='parent skills directory')
    args = parser.parse_args(argv)
    try:
        if args.command == 'search': emit(search(args.query,args.category))
        elif args.command == 'inspect':
            rows = [r for r in catalog() if r['id'] == args.id.upper()]
            if not rows: raise ValueError('Unknown source ID: '+args.id)
            emit(rows[0])
        elif args.command == 'route': emit({'suggested_modes': route(args.task), 'method':'keyword suggestion; agent judgment required'})
        elif args.command == 'brief': emit(brief(args.task,args.engine,args.project))
        elif args.command == 'analyze-project':
            from project_analysis import analyze_project
            result=analyze_project(args.project,args.include_tests,args.include_addons,args.max_files)
            if args.output:
                from analysis_reports import write_new
                write_new(args.output,json.dumps(result,ensure_ascii=False,indent=2)+'\n')
                emit({'output':args.output,'files':len(result['files']),'references':len(result['references']),'write_clues':len(result['state_write_clues']),'warnings':result['warnings']})
            else: emit(result)
        elif args.command in {'report-analysis','compare-analysis'}:
            from analysis_reports import read_analysis,render_analysis,compare_analysis,write_new
            if args.command=='report-analysis':
                text=render_analysis(read_analysis(args.input),args.max_rows)
            else:
                text=json.dumps(compare_analysis(read_analysis(args.before),read_analysis(args.after)),ensure_ascii=False,indent=2)+'\n'
            write_new(args.output,text)
            emit({'output':args.output,'source_reports':'unchanged'})
        elif args.command=='create-workspace':
            from creative_workspace import create_workspace
            emit(create_workspace(read_document(args.brief),args.output))
        elif args.command=='workspace-page':
            from workspace_view import export_workspace
            emit(export_workspace(args.workspace,args.output))
        elif args.command=='check-workspace':
            from creative_workspace import check_workspace
            result=check_workspace(args.workspace)
            if args.output:
                from workspace_io import new_json
                new_json(args.output,result)
            emit(result); return 0 if result['passed'] else 2
        elif args.command=='capabilities':
            from engine_adapters import capabilities
            emit(capabilities())
        elif args.command=='run-adapter-case':
            from engine_adapters import run_adapter_case
            result=run_adapter_case(args.kind,args.editor,args.expect,args.scratch,args.output_dir)
            emit(result); return 0 if result['passed'] else 2
        elif args.command=='freeze-project-tests':
            from project_runner import freeze_project
            emit(freeze_project(args.project,args.config,args.output))
        elif args.command=='project-tests':
            from project_runner import plan_project,run_project
            if args.execute:
                if not args.output_dir: raise ValueError('--execute requires --output-dir')
                result=run_project(args.project,args.config,args.output_dir,args.engine)
                emit(result); return 0 if result['passed'] else 2
            emit(plan_project(args.project,args.config,args.engine,args.output_dir))
        elif args.command=='gallery':
            from evidence_gallery import export_gallery
            emit(export_gallery(args.evidence_dir,args.output))
        elif args.command=='verify-editor-case':
            from editor_cases import verify_editor_case
            result=verify_editor_case(args.editor_kind,args.editor,args.expect,args.scratch,args.output_dir)
            emit(result); return 0 if result['passed'] else 2
        elif args.command in {'check-narrative','simulate-economy','audit-assets','summarize-evals'}:
            if args.command=='check-narrative':
                from narrative_checks import check_narrative
                result=check_narrative(read_document(args.input))
            elif args.command=='simulate-economy':
                from economy_simulation import simulate_economy
                result=simulate_economy(read_document(args.input))
            elif args.command=='summarize-evals':
                from evaluation_ledger import summarize_evaluations
                result=summarize_evaluations(read_document(args.input))
            else:
                from asset_preflight import audit_assets
                result=audit_assets(args.project,read_document(args.manifest))
            if args.output:
                from analysis_reports import write_new
                write_new(args.output,json.dumps(result,ensure_ascii=False,indent=2)+'\n')
            emit(result); return 0 if result.get('passed',True) else 2
        elif args.command == 'manual-input':
            probe=doctor(args.engine,'4.7.2',official=True)
            if probe['engine_status']!='version-confirmed': emit({'status':'blocked','engine':probe}); return 2
            from manual_input import launch_manual
            emit(launch_manual(args.engine,args.scratch,args.output_dir,mode=args.mode))
        elif args.command == 'check-ui-effects':
            probe=doctor(args.engine,args.expect,official=True)
            if probe['engine_status']!='version-confirmed': emit({'passed':False,'engine':probe}); return 2
            from quality_checks import check_sample
            result=check_sample(args.engine,args.output_dir,args.scratch,args.graphical,case=args.case)
            result['engine_version']=probe['engine_version']
            if Path(args.output_dir,'report.json').is_file():
                Path(args.output_dir,'report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
            emit(result); return 0 if result['passed'] else 2
        elif args.command == 'verify-godot':
            if args.output and Path(args.output).exists(): raise ValueError('Output must not overwrite an existing file')
            result=verify_godot(args.engine,args.expect,args.scratch)
            if args.output:
                from analysis_reports import write_new
                write_new(args.output,json.dumps(result,ensure_ascii=False,indent=2)+'\n')
            emit(result); return 0 if result['headless_behavior']=='passed' else 2
        elif args.command == 'doctor':
            if (args.expect or args.official) and not args.engine: raise ValueError('--expect/--official requires --engine')
            result = doctor(args.engine,args.expect,args.official); emit(result)
            return 0 if result['engine_status'] in {'not-requested','version-confirmed'} else 2
        elif args.command == 'validate':
            errors=validate(); emit({'valid':not errors,'errors':errors}); return 1 if errors else 0
        elif args.command == 'install-plan': emit(install_plan(args.dest))
        elif args.command == 'install': emit(install(args.dest))
    except (OSError, ValueError, KeyError) as exc:
        print(str(exc),file=sys.stderr); return 2
    return 0

if __name__ == '__main__': sys.exit(main())
