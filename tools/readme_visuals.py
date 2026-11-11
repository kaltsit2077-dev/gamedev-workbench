"""Derive README SVG figures from archived evidence, or check for drift."""
import argparse
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    return json.loads((ROOT/'docs'/name).read_text(encoding='utf-8'))


def text(x, y, value, size=22, fill='#e4ecee', weight=400):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}">{html.escape(str(value))}</text>'


def bar(x, y, width, color):
    return f'<rect x="{x}" y="{y}" width="{width:.2f}" height="18" rx="3" fill="{color}"/>'


def svg(title, description, height, parts):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="'+str(height)+'" viewBox="0 0 1080 '+str(height)+'" role="img" aria-labelledby="title desc">\n'
            '<title id="title">'+html.escape(title)+'</title><desc id="desc">'+html.escape(description)+'</desc>\n'
            '<rect width="1080" height="100%" rx="12" fill="#101c28"/>\n'
            '<g font-family="Segoe UI,Microsoft YaHei,sans-serif">\n'+'\n'.join(parts)+'\n</g></svg>\n')


def figures():
    analysis = load('analysis-labels-v05.json')
    baseline, current = analysis['baseline'], analysis['current']
    old, new = load('quality-v03/report.json'), load('quality-v05/report.json')
    parts = [text(36, 48, 'What changed in the tools', 30, weight=600),
             text(36, 81, 'Recorded snapshots · analyzer 0.4 → 0.5 · native fixtures 0.3 / 0.5', 18, '#a8b8c1'),
             text(36, 132, 'Explicit resource references', 24, weight=600)]
    for y, label, data, color in [(172, '0.4 baseline', baseline, '#ffd28b'), (223, '0.5 current', current, '#75d6cc')]:
        parts += [text(36, y, label, 20), bar(220, y-16, 390*data['matched_cases']/data['case_count'], color),
                  text(635, y, f"{data['matched_cases']} / {data['case_count']} cases", 23, color, 600),
                  text(830, y, f"FP {data['false_positive_references']}  /  FN {data['false_negative_references']}", 20)]
    parts += [text(36, 267, 'Hand-labeled regression corpus; not held-out or whole-project accuracy.', 18, '#a8b8c1'),
              '<path d="M36 292H1044" stroke="#3d5663"/>', text(36, 335, 'Native UI + effects coverage', 24, weight=600)]
    for y, label, data in [(377, 'Basic fixture (0.3)', old), (418, 'Menu fixture (0.5)', new)]:
        passed = sum(c['passed'] for c in data['checks'])
        views = len({(f['width'], f['height']) for f in data['frames']})
        parts += [text(36, y, label, 20), text(340, y, f"{passed} checks", 22, '#75d6cc'),
                  text(565, y, f"{len(data['frames'])} PNG captures", 22), text(850, y, f'{views} viewports', 22)]
    parts += [text(36, 465, 'Different original fixtures. Counts show coverage, not visual quality or speed.', 18, '#a8b8c1')]
    coverage = svg('Measured tool changes', 'Finite reference-regression results and native fixture coverage. Limits are stated beside each result.', 496, parts)
    trials = load('transactions-results.json')
    records = trials['records']; maximum = max(r['elapsed_seconds'] for r in records)
    parts = [text(36, 48, 'Did the skill make the task faster?', 30, weight=600),
             text(36, 82, 'Settings transaction repair · two paired pilots · skill treatment 0.4', 19, '#a8b8c1')]
    for index, r in enumerate(records):
        y = 133+index*52; color = '#75d6cc' if r['arm']=='a' else '#ffd28b'
        label = f"Run {r['repetition']} · {'without skill' if r['arm']=='a' else 'with skill'}"
        parts += [text(36, y, label, 20), bar(300, y-16, 430*r['elapsed_seconds']/maximum, color),
                  text(755, y, f"{r['elapsed_seconds']:.1f} s", 22, color, 600),
                  text(905, y, f"{sum(c['passed'] for c in r['checks'])}/{len(r['checks'])} pass", 20)]
    delta = trials['summary']['median_b_minus_a_seconds']
    parts += [text(36, 347, f'With-skill median paired difference: +{delta:.1f} s. No speed gain demonstrated.', 23, '#ffd28b', 600),
              text(36, 386, 'Both arms: 0 post-grading rework rounds. Tokens and actual fees unavailable.', 19, '#a8b8c1'),
              text(36, 421, 'Shared-host wall time; inherited model config, exact backend ID unavailable.', 18, '#a8b8c1'),
              text(36, 451, 'Small descriptive pilots; no causal claim. New 0.5 / 0.6 tools were not the treatment.', 18, '#a8b8c1')]
    return {'evidence-changes.svg': coverage,
            'paired-pilot.svg': svg('Paired pilot results', 'The with-skill arms were slower; no productivity or cost improvement was established.', 482, parts)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for name, content in figures().items():
        target = ROOT/'docs/media'/name
        if args.check:
            if not target.is_file() or target.read_bytes() != content.encode('utf-8'):
                raise SystemExit('Stale README figure: '+name+'; run python tools/readme_visuals.py')
        else:
            target.write_text(content, encoding='utf-8', newline='\n')
    print('README figures match recorded evidence.' if args.check else 'README figures generated from recorded evidence.')


if __name__ == '__main__': main()
