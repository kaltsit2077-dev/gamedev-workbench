"""Finite authored dependency-rule regression; no engine or model comparison."""
import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT/'skills/gamedev-workbench'
sys.path.insert(0, str(SKILL/'scripts'))
from project_analysis import analyze_project
from dependency_boundaries import check_boundaries
from workspace_io import new_json


def evaluate():
    rules = json.loads((SKILL/'assets/dependency-rules.json').read_text(encoding='utf-8'))
    cases = [
        ('existing-sample', '', 'no-observed-violations', 0),
        ('reverse-state-dependency', '\nconst LEAK=preload("res://demo.gd")\n', 'violations', 1),
        ('runtime-load', '\nfunc probe(path):\n\treturn load(path)\n', 'partial', 0),
        ('literal-only', '\nvar example_path="res://demo.gd"\n', 'partial', 0),
        ('unknown-uid', '\nconst UNKNOWN=preload("uid://unknown")\n', 'partial', 0),
    ]
    records = []
    for name, addition, expected, count in cases:
        with tempfile.TemporaryDirectory(prefix='gdw-boundary-') as d:
            project = Path(d)/'project'
            shutil.copytree(SKILL/'assets/godot-demo', project, ignore=shutil.ignore_patterns('.godot', '*.log'))
            state = project/'state.gd'
            if addition: state.write_text(state.read_text(encoding='utf-8')+addition, encoding='utf-8', newline='\n')
            snapshot = analyze_project(project)
            before = {p.relative_to(project).as_posix(): p.read_bytes() for p in project.rglob('*') if p.is_file()}
            report = check_boundaries(snapshot, rules)
            unchanged = before == {p.relative_to(project).as_posix(): p.read_bytes() for p in project.rglob('*') if p.is_file()}
            records.append({'case': name, 'expected_status': expected, 'expected_violations': count,
                            'matched': report['status'] == expected and len(report['violations']) == count and unchanged,
                            'source_files_unchanged': unchanged, 'report': report})
    return {'kind': 'authored-tool-regression', 'passed': all(r['matched'] for r in records), 'records': records,
            'limits': ['Existing original Godot sample with authored mutations; regression, not held-out accuracy.',
                       'No engine, model comparison, productivity, fees or production-game claim.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', required=True)
    args = parser.parse_args(); result = evaluate(); new_json(args.output, result)
    print(json.dumps({'passed': result['passed'], 'matched': sum(r['matched'] for r in result['records']),
                      'case_count': len(result['records'])})); return 0 if result['passed'] else 1


if __name__ == '__main__': raise SystemExit(main())
