"""Reproduce the historical v0.7 experiment using its original frozen sources."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT/'evals/tool-value/frozen-v07'


def frozen_protocol(root=SNAPSHOT):
    root = Path(root)
    path = root/'evals/tool-value/protocol.json'
    if root == SNAPSHOT and path.read_bytes() != (ROOT/'evals/tool-value/protocol.json').read_bytes():
        raise ValueError('Frozen protocol copies disagree')
    data = json.loads(path.read_text(encoding='utf-8'))
    for name, expected in data['source_sha256'].items():
        raw = (root/name).read_bytes().replace(b'\r\n', b'\n')
        if hashlib.sha256(raw).hexdigest() != expected: raise ValueError('Frozen experiment source changed: '+name)
    return data


def evaluate(engine, scratch, output):
    frozen_protocol()
    # A subprocess keeps historical imports separate from the installed/current tools.
    subprocess.run([sys.executable, str(SNAPSHOT/'tools/evaluate_tool_value.py'), '--engine', str(engine),
                    '--scratch', str(scratch), '--output', str(output)], check=True)
    return json.loads((Path(output)/'results.json').read_text(encoding='utf-8'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', required=True); parser.add_argument('--scratch', required=True); parser.add_argument('--output', required=True)
    args = parser.parse_args(); result = evaluate(args.engine, args.scratch, args.output)
    return 0 if result['all_intact_accepted'] and result['all_seeded_defects_detected'] else 1


if __name__ == '__main__': raise SystemExit(main())
