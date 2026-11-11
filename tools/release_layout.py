"""Explicit public source areas shared by packaging, audit and initial Git staging."""
from pathlib import Path

ROOT_FILES={'.gitignore','.gitattributes','README.md','README.en.md','LICENSE','NOTICE',
            'CHANGELOG.md','CONTRIBUTING.md','THIRD_PARTY_NOTICES.md','DESIGN.md','PLAN.md','RESEARCH.md'}
SOURCE_DIRS={'skills','tools','tests','docs','examples','evals','.github'}
IGNORED_PARTS={'.git','.godot','__pycache__','dist','.cache','.venv','node_modules','private',
               'Library','Temp','Logs','UserSettings','Intermediate','Saved','DerivedDataCache','Binaries'}

def release_files(root):
    root=Path(root).resolve(); files=[]
    for path in sorted(root.rglob('*')):
        relative=path.relative_to(root)
        if relative.parts[0] not in SOURCE_DIRS and relative.as_posix() not in ROOT_FILES: continue
        if any(part in IGNORED_PARTS for part in relative.parts): continue
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError('Release cannot include a symlink or escaping path: '+relative.as_posix())
        if not path.is_file(): continue
        if path.name.startswith('.env') or path.name=='local-profile.json' or path.suffix in {'.pyc','.pem','.key','.p12'}: continue
        if '.run' in relative.parts and path.name not in {'timing-start.json','timing-end.json'}: continue
        if path.suffix=='.log' and relative.as_posix() not in {'docs/quality-v03/engine.log','docs/quality-v05/engine.log'}: continue
        files.append(path)
    return files

def skill_files(source):
    source=Path(source).resolve(); project=source.parent.parent
    return [path for path in release_files(project) if path.is_relative_to(source)]
