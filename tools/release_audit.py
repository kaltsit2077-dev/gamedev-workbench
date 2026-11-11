"""Audit selected public release files; a bounded heuristic, not a secrecy guarantee."""
import argparse
import json
from pathlib import Path
import re
from release_layout import release_files

PATTERNS={
    'personal absolute path':re.compile(r'(?i)(?:[A-Z]:[\\/]Users[\\/]|/(?:Users|home)/[A-Za-z0-9_.-]+/)'),
    'GitHub credential':re.compile(r'(?:gh[pousr]_|github_pat_)[A-Za-z0-9_]{30,}'),
    'private key':re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
}

def audit(root):
    root=Path(root).resolve(); findings=[]
    for path in release_files(root):
        if path.suffix=='.png': continue
        if path.stat().st_size>20_000_000:
            findings.append(path.relative_to(root).as_posix()+': exceeds text audit limit'); continue
        try: content=path.read_text(encoding='utf-8')
        except UnicodeError:
            findings.append(path.relative_to(root).as_posix()+': unrecognized binary'); continue
        for label,pattern in PATTERNS.items():
            if pattern.search(content): findings.append(path.relative_to(root).as_posix()+': '+label)
    return findings

def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--root',default=str(Path(__file__).resolve().parents[1]))
    args=parser.parse_args(); findings=audit(args.root)
    print(json.dumps({'passed':not findings,'findings':findings,'scope':'selected public release files; heuristic checks only'},indent=2))
    return 1 if findings else 0

if __name__=='__main__': raise SystemExit(main())
