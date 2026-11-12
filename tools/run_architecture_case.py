"""Run the original architecture repair case in isolated, engine-writable copies."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT/'skills/gamedev-workbench'
sys.path.insert(0, str(SKILL/'scripts'))
from project_analysis import analyze_project
from dependency_boundaries import check_boundaries
from workspace_io import new_json


def run_case(engine, scratch, output, baseline_skill=None):
    engine = Path(engine).resolve(strict=True)
    version = subprocess.run([str(engine), '--version'], capture_output=True, text=True, timeout=15)
    if version.returncode or not version.stdout.strip().startswith('4.7.2.stable.official.'):
        raise ValueError('This recorded case requires official Godot 4.7.2')
    scratch, output = Path(scratch).resolve(), Path(output).resolve()
    for path in [scratch, output]:
        if path.exists() or path.is_relative_to(SKILL) or SKILL.is_relative_to(path):
            raise ValueError('Use new output/scratch directories outside the skill source')
    if scratch.is_relative_to(output) or output.is_relative_to(scratch): raise ValueError('Outputs and projects must be separate')
    baseline = Path(baseline_skill).resolve(strict=True) if baseline_skill else None
    if baseline and (baseline/'VERSION').read_text(encoding='utf-8').strip() != '0.9.0-preview':
        raise ValueError('Optional comparison requires the explicitly selected original 0.9 skill')
    scratch.mkdir(parents=True); output.mkdir(parents=True)
    # Keep a containing Godot project from importing these disposable subprojects.
    (scratch/'.gdignore').write_bytes(b'')
    source = SKILL/'assets/architecture-case'
    rules = json.loads((source/'rules.json').read_text(encoding='utf-8'))
    reports = []
    for name in ['before', 'after']:
        project = scratch/name; shutil.copytree(source/name, project)
        original = {p.relative_to(project): p.read_bytes() for p in project.rglob('*') if p.is_file()}
        boundary = check_boundaries(analyze_project(project), rules)
        baseline_result = None
        if baseline and name == 'before':
            old_analysis, old_boundary = output/'baseline-analysis.json', output/'baseline-boundaries.json'
            cli = baseline/'scripts/workbench.py'
            for args in [['analyze-project', str(project), '--output', str(old_analysis)],
                         ['check-boundaries', str(old_analysis), '--rules', str(source/'rules.json'), '--output', str(old_boundary)]]:
                subprocess.run([sys.executable, str(cli), *args], check=True, capture_output=True, timeout=30)
            old = json.loads(old_boundary.read_text(encoding='utf-8'))
            baseline_result = {'version': '0.9.0-preview', 'status': old['status'], 'violation_count': len(old['violations']),
                               'analyzer_sha256': hashlib.sha256((baseline/'scripts/project_analysis.py').read_bytes()).hexdigest()}
        case_output = output/name; case_output.mkdir()
        env = dict(os.environ, APPDATA=str(case_output), LOCALAPPDATA=str(case_output), XDG_DATA_HOME=str(case_output), XDG_CONFIG_HOME=str(case_output))
        imported = subprocess.run([str(engine), '--headless', '--editor', '--path', str(project), '--import', '--quit', '--log-file', str(case_output/'import.log')],
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60, env=env)
        native = case_output/'native.json'
        executed = subprocess.run([str(engine), '--headless', '--path', str(project), '--script', 'res://smoke.gd', '--log-file', str(case_output/'runtime.log'), '--', str(native)],
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30, env=env)
        lines = (imported.stdout+executed.stdout).decode('utf-8', errors='replace').splitlines()
        diagnostics = [line for line in lines if line.lstrip().startswith(('ERROR:', 'SCRIPT ERROR:'))]
        environment = [line for line in diagnostics if line.strip() == 'ERROR: Failed to read the root certificate store.']
        blocking = [line for line in diagnostics if line not in environment]
        evidence = json.loads(native.read_text(encoding='utf-8')) if native.exists() else {}
        checks = evidence.get('checks', [])
        expected_passed = name == 'after'
        expected_checks = [True, True, True, expected_passed]
        unchanged = all((project/path).read_bytes() == data for path, data in original.items())
        matched = (unchanged and imported.returncode == 0 and not blocking and
                   executed.returncode == (0 if expected_passed else 1) and
                   evidence.get('passed') is expected_passed and len(checks) == 4 and
                   [r.get('passed') for r in checks] == expected_checks and
                   boundary['status'] == ('no-observed-violations' if expected_passed else 'violations') and
                   len(boundary['violations']) == (0 if expected_passed else 1))
        if baseline_result: matched = matched and baseline_result['status'] == 'no-observed-violations'
        reports.append({'case': name, 'matched_expected_result': matched, 'original_source_bytes_unchanged': unchanged,
                        'source_sha256': {path.as_posix(): hashlib.sha256(data.replace(b'\r\n', b'\n')).hexdigest() for path,data in original.items()},
                        'compile_exit_code': imported.returncode, 'runtime_exit_code': executed.returncode,
                        'blocking_diagnostic_count': len(blocking), 'environment_diagnostic_count': len(environment),
                        'boundary_report': boundary, 'native': evidence, 'baseline': baseline_result})
    result = {'kind': 'original-architecture-repair-case', 'engine_version': version.stdout.strip(),
              'passed': all(r['matched_expected_result'] for r in reports), 'records': reports,
              'limits': ['Original demonstration with a deliberately introduced dependency; not a production-game bug.',
                         'Same native acceptance before/after; no rendering, physical input, performance or model productivity test.',
                         'Working copies may acquire engine caches/UIDs; distributed originals are not modified.',
                         'Optional baseline executes the explicitly selected local 0.9 Python tool; no download or installation.']}
    new_json(output/'report.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', required=True); parser.add_argument('--scratch', required=True)
    parser.add_argument('--output-dir', required=True); parser.add_argument('--baseline-skill')
    args = parser.parse_args()
    result = run_case(args.engine, args.scratch, args.output_dir, args.baseline_skill)
    print(json.dumps({'passed': result['passed'], 'cases': [(r['case'], r['matched_expected_result']) for r in result['records']]}))
    return 0 if result['passed'] else 1


if __name__ == '__main__': raise SystemExit(main())
