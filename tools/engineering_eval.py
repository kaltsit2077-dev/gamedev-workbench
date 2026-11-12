"""Prepare/grade frozen original Godot integration tasks; never dispatch models."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT/'evals/engineering'


def digest(path): return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def frozen():
    protocol = json.loads((FIXTURE/'protocol.json').read_text(encoding='utf-8'))
    for name, expected in protocol['sha256'].items():
        if digest(FIXTURE/name) != expected: raise ValueError('Frozen input/grader changed: '+name)
    if digest(ROOT/'tools/engineering_eval.py') != protocol['driver_sha256']: raise ValueError('Frozen grading driver changed')
    return protocol


def git(root, *args, check=True):
    empty_hooks = root.parent/'empty-hooks'; empty_hooks.mkdir(exist_ok=True)
    env = dict(os.environ, GIT_TERMINAL_PROMPT='0', GIT_CONFIG_NOSYSTEM='1',
               GIT_AUTHOR_DATE='2026-11-12T00:00:00+00:00', GIT_COMMITTER_DATE='2026-11-12T00:00:00+00:00')
    return subprocess.run(['git', '-c', 'core.autocrlf=false', '-c', 'commit.gpgsign=false', '-c', 'core.hooksPath='+str(empty_hooks),
                           '-C', str(root), *args], check=check, capture_output=True, env=env)


def prepare(output):
    frozen(); output = Path(output).resolve()
    if output.exists(): raise ValueError('Preparation output must be new')
    output.mkdir(parents=True)
    seed = output/'seed'; shutil.copytree(FIXTURE/'input/base', seed)
    git(seed, 'init', '-b', 'integration', '--template=')
    git(seed, 'config', 'user.name', 'Fixture'); git(seed, 'config', 'user.email', 'fixture@example.invalid')
    git(seed, 'add', '.'); git(seed, 'commit', '-m', 'base settings')
    base = git(seed, 'rev-parse', 'HEAD').stdout.decode().strip()
    shutil.copyfile(FIXTURE/'input/branch-reduced/settings_state.gd', seed/'settings_state.gd')
    git(seed, 'commit', '-am', 'add reduced motion'); reduced = git(seed, 'rev-parse', 'HEAD').stdout.decode().strip()
    git(seed, 'switch', '-c', 'volume', base)
    shutil.copyfile(FIXTURE/'input/branch-volume/settings_state.gd', seed/'settings_state.gd')
    git(seed, 'commit', '-am', 'add master volume')
    git(seed, 'switch', 'integration')
    merged = git(seed, 'merge', '--no-edit', 'volume', check=False)
    if merged.returncode == 0 or not git(seed, 'ls-files', '-u').stdout: raise ValueError('Expected genuine integration conflict')
    for arm in ['a', 'b']: shutil.copytree(seed, output/('arm-'+arm))
    return {'prepared': True, 'base': base, 'head': reduced,
            'limits': ['Original bounded Godot fixture, not a medium-size production game.',
                       'Dispatcher must use independent equal model/tool contexts; skill treatment is the only intended difference.']}


def grade(case, engine, output):
    protocol = frozen(); case = Path(case).resolve(); output = Path(output).resolve()
    if output.exists(): raise ValueError('Grading output must be new')
    output.mkdir(parents=True)
    protected = all(digest(case/name) == protocol['sha256']['input/base/'+name] for name in ['AGENTS.md', 'REQUIREMENTS.md', 'project.godot', 'hud.gd', 'smoke.gd', '.gitignore'])
    unmerged = bool(git(case, 'ls-files', '-u').stdout)
    state_staged = not bool(git(case, 'diff', '--name-only', '--', 'settings_state.gd').stdout)
    native = output/'native.json'; log = output/'engine.log'
    env = dict(os.environ, APPDATA=str(output), LOCALAPPDATA=str(output), XDG_DATA_HOME=str(output), XDG_CONFIG_HOME=str(output))
    try:
        probe = subprocess.run([str(Path(engine).resolve()), '--version'], capture_output=True, text=True, timeout=15)
        binary_version = probe.stdout.strip()
        process = subprocess.run([str(Path(engine).resolve()), '--headless', '--path', str(case), '--log-file', str(log),
                                  '--script', str(FIXTURE/'grader.gd'), '--', str(native)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=45, env=env)
        text = process.stdout.decode('utf-8', errors='replace')
        evidence = json.loads(native.read_text(encoding='utf-8')) if native.is_file() else {}
        diagnostics = [row for row in text.splitlines() if row.startswith(('ERROR:', 'SCRIPT ERROR:')) and row.strip() != 'ERROR: Failed to read the root certificate store.']
        checks = evidence.get('checks', [])
        passed = (protected and not unmerged and state_staged and process.returncode == 0 and evidence.get('passed') is True
                  and len(checks) == 13 and all(c.get('passed') is True for c in checks) and not diagnostics
                  and probe.returncode == 0 and binary_version.startswith('4.7.2.stable.official.')
                  and str(evidence.get('engine_version', '')).startswith(('4.7.2-stable', '4.7.2.stable')))
        result = {'passed': passed, 'protected_files_unchanged': protected, 'unmerged_index': unmerged, 'state_resolution_staged': state_staged,
                  'exit_code': process.returncode, 'checks': checks, 'engine_version': evidence.get('engine_version'),
                  'binary_version': binary_version, 'diagnostic_count': len(diagnostics), 'usage': {'source': 'unavailable', 'input_tokens': None, 'output_tokens': None, 'cost_usd': None}}
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        result = {'passed': False, 'reason': type(error).__name__, 'checks': []}
    (output/'result.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__); sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('prepare'); p.add_argument('--output', required=True)
    p = sub.add_parser('grade'); p.add_argument('--case', required=True); p.add_argument('--engine', required=True); p.add_argument('--output', required=True)
    args = parser.parse_args()
    result = prepare(args.output) if args.command == 'prepare' else grade(args.case, args.engine, args.output)
    print(json.dumps(result, indent=2)); return 0 if result.get('passed', result.get('prepared')) else 1


if __name__ == '__main__': raise SystemExit(main())
