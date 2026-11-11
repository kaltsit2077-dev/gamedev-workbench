"""Score a pinned, previously external source set without changing labels."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'skills/gamedev-workbench/scripts'))
from project_analysis import analyze_project


def evaluate(root=None):
    root = Path(root or ROOT/'evals/analysis-external').resolve()
    manifest = json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    def checked(path, expected):
        target = root/path
        if target.is_symlink() or not target.resolve().is_relative_to(root):
            raise ValueError('Frozen path escapes fixture')
        data = target.read_bytes()
        # Text hashes tolerate checkout newline conversion, not content edits.
        data = data.replace(b'\r\n', b'\n')
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError('Frozen fixture hash mismatch: '+path)
        return data
    labels = json.loads(checked('labels.json', manifest['labels_sha256']))
    for item in manifest['files']: checked(item['path'], item['sha256'])
    records = []; tp = fp = fn = 0
    for path, expected in labels['expected'].items():
        with tempfile.TemporaryDirectory(prefix='gdw-external-') as d:
            project = Path(d)
            (project/'project.godot').write_text('[application]\n', encoding='utf-8')
            target = project/path; target.parent.mkdir(parents=True)
            target.write_bytes((root/'sources'/path).read_bytes())
            result = analyze_project(project)
            predicted = {(r['kind'], r['target']) for r in result['references']
                         if r['source'] == path and r['kind'] in {'load', 'preload', 'extends', 'ext-resource'}}
            expected = {tuple(x) for x in expected}
            tp += len(predicted & expected); fp += len(predicted-expected); fn += len(expected-predicted)
            records.append({'path': path, 'expected': sorted(expected), 'predicted': sorted(predicted),
                            'matched': predicted == expected, 'false_positive': sorted(predicted-expected),
                            'false_negative': sorted(expected-predicted), 'unknown_uid_clues': len(result['uid_references']),
                            'dynamic_clues': len(result['dynamic_references'])})
    return {'kind': 'external-analysis-evaluation', 'upstream': manifest['upstream'], 'commit': manifest['commit'],
            'labels_sha256': manifest['labels_sha256'], 'files': records, 'matched_files': sum(r['matched'] for r in records),
            'file_count': len(records), 'true_positive_references': tp, 'false_positive_references': fp,
            'false_negative_references': fn, 'precision': tp/(tp+fp) if tp+fp else None,
            'recall': tp/(tp+fn) if tp+fn else None, 'unmodeled_runtime_inputs': labels['unmodeled_runtime_inputs'],
            'human_review': 'pending; assistant labels are not independent human review',
            'limits': ['Small selected official-demo source subset, not whole projects or a representative population.',
                       'External authorship; labels frozen before first run, but authored by the same assistant.',
                       'Scores explicit edge identity only; referenced resources were not all downloaded or executed.',
                       'Format-specific runtime loaders, signal wiring and state ownership remain outside this score.',
                       'Once used to guide changes, treat this corpus as regression, not fresh held-out evidence.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    args = parser.parse_args(); result = evaluate()
    with Path(args.output).open('x', encoding='utf-8', newline='\n') as file:
        json.dump(result, file, ensure_ascii=False, indent=2); file.write('\n')
    print(json.dumps({k: result[k] for k in ['matched_files', 'file_count', 'true_positive_references', 'false_positive_references', 'false_negative_references', 'human_review']}))
    return 0 if result['matched_files'] == result['file_count'] else 1


if __name__ == '__main__': raise SystemExit(main())
