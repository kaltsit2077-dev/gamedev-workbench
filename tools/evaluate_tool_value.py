"""Frozen parse-only versus task-specific defect detection; not an AI productivity trial."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'skills/gamedev-workbench/scripts'))
from project_analysis import analyze_project
from quality_checks import check_sample
from workspace_io import new_json


def frozen_protocol(root=ROOT):
    data = json.loads((root/'evals/tool-value/protocol.json').read_text(encoding='utf-8'))
    for name, expected in data['source_sha256'].items():
        raw = (root/name).read_bytes().replace(b'\r\n', b'\n')
        if hashlib.sha256(raw).hexdigest() != expected: raise ValueError('Frozen experiment source changed: '+name)
    return data


def evaluate(engine, scratch, output):
    protocol = frozen_protocol()
    from workbench import doctor
    if doctor(engine, '4.7.2', official=True)['engine_status'] != 'version-confirmed':
        raise ValueError('Official Godot 4.7.2 is required')
    destination = Path(output).resolve()
    if destination.exists(): raise ValueError('Experiment output must be new')
    destination.mkdir(parents=True); scratch = Path(scratch).resolve(); scratch.mkdir(parents=True, exist_ok=True)
    records = []
    for task in protocol['tasks']:
        for defective in [False, True]:
            name = task['id']+('-defect' if defective else '-intact')
            with tempfile.TemporaryDirectory(prefix='gdw-value-', dir=scratch) as d:
                work = Path(d); custom_skill = work/'skill'; project = custom_skill/'assets/godot-menu'
                if task['id'] == 'architecture':
                    project.mkdir(parents=True)
                    (project/'project.godot').write_text('config_version=5\n[application]\n', encoding='utf-8')
                    target = 'missing.tres' if defective else 'data.tres'
                    (project/'case.gd').write_text('extends Node\nfunc choose_resource():\n\treturn load("res://'+target+'")\n', encoding='utf-8')
                    (project/'data.tres').write_text('[gd_resource type="Resource" format=3]\n', encoding='utf-8')
                    script = 'res://case.gd'
                else:
                    shutil.copytree(ROOT/'skills/gamedev-workbench/assets/godot-menu', project)
                    script = 'res://quality.gd'
                    if defective:
                        file = project/task['file']; text = file.read_text(encoding='utf-8')
                        if text.count(task['before']) != 1: raise ValueError('Defect injection anchor changed')
                        file.write_text(text.replace(task['before'], task['after']), encoding='utf-8', newline='\n')
                data_dir = work/'data'; data_dir.mkdir()
                env = dict(os.environ, APPDATA=str(data_dir), LOCALAPPDATA=str(data_dir), XDG_DATA_HOME=str(data_dir), XDG_CONFIG_HOME=str(data_dir))
                started = perf_counter()
                process = subprocess.run([str(Path(engine).resolve()), '--headless', '--path', str(project), '--log-file', str(work/'parse.log'),
                                          '--check-only', '--script', script], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30, env=env)
                text = process.stdout.decode('utf-8', errors='replace')
                diagnostics = [line for line in text.splitlines() if line.startswith(('ERROR:', 'SCRIPT ERROR:')) and line.strip() != 'ERROR: Failed to read the root certificate store.']
                parse_passed = process.returncode == 0 and not diagnostics
                parse_seconds = perf_counter()-started
                started = perf_counter()
                if task['id'] == 'architecture':
                    report = analyze_project(project)
                    failures = [r['target'] for r in report['references'] if r['status'] == 'missing' and r['kind'] == 'load']
                    tool_passed = not failures
                else:
                    report = check_sample(engine, destination/name, scratch, False, custom_skill, case='menu')
                    tool_passed = report['passed']; failures = [c['name'] for c in report.get('checks', []) if not c['passed']]
                    if not failures and not tool_passed: failures = ['native execution/report failure']
                records.append({'task': task['id'], 'variant': 'seeded-defect' if defective else 'intact',
                                'expected_defect': defective, 'parse_only_passed': parse_passed, 'tool_passed': tool_passed,
                                'parse_only_seconds': parse_seconds, 'tool_seconds': perf_counter()-started,
                                'tool_diagnostics': failures, 'parse_exit_code': process.returncode})
    def metrics(key):
        return {'true_positive': sum(r['expected_defect'] and not r[key] for r in records),
                'false_positive': sum(not r['expected_defect'] and not r[key] for r in records),
                'false_negative': sum(r['expected_defect'] and r[key] for r in records)}
    result = {'kind': 'tool-defect-detection-experiment', 'protocol_version': protocol['version'], 'records': records,
              'parse_only': metrics('parse_only_passed'), 'task_tools': metrics('tool_passed'),
              'all_intact_accepted': all(r['tool_passed'] for r in records if not r['expected_defect']),
              'all_seeded_defects_detected': all(not r['tool_passed'] for r in records if r['expected_defect']),
              'new_model_trials': {'status': 'not-run', 'records': [], 'actual_cost_usd': None, 'tokens': None,
                                   'human_blind_review': 'pending'},
              'limits': protocol['limits']}
    new_json(destination/'results.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', required=True); parser.add_argument('--scratch', required=True); parser.add_argument('--output', required=True)
    args = parser.parse_args(); result = evaluate(args.engine, args.scratch, args.output)
    print(json.dumps({k: result[k] for k in ['parse_only', 'task_tools', 'all_intact_accepted', 'all_seeded_defects_detected', 'new_model_trials']}, indent=2))
    return 0 if result['all_intact_accepted'] and result['all_seeded_defects_detected'] else 1


if __name__ == '__main__': raise SystemExit(main())
