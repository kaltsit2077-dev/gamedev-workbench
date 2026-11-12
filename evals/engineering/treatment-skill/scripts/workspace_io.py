"""Bounded local workspace I/O shared by explicit project tools."""
import json
from pathlib import Path, PurePosixPath


def read_json(path, limit=2_000_000):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > limit:
        raise ValueError('Expected a bounded regular JSON file')
    return json.loads(path.read_text(encoding='utf-8'))


def local_path(root, name):
    root = Path(root).resolve()
    if not isinstance(name, str) or not name or '\\' in name or ':' in name:
        raise ValueError('Expected a relative local path')
    parts = PurePosixPath(name)
    if parts.is_absolute() or '..' in parts.parts:
        raise ValueError('Path cannot leave the selected root')
    path = root
    for part in parts.parts:
        path = path/part
        if path.is_symlink(): raise ValueError('Symlinks are not accepted')
    if not path.resolve().is_relative_to(root): raise ValueError('Path escapes selected root')
    return path


def new_json(path, data):
    with Path(path).open('x', encoding='utf-8', newline='\n') as file:
        json.dump(data, file, ensure_ascii=False, indent=2); file.write('\n')
