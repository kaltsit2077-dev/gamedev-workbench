"""Evaluate explicit call/extends reference labels in original finite fixtures."""
import argparse
import importlib.util
import json
from pathlib import Path
import tempfile

ROOT=Path(__file__).resolve().parents[1]

def evaluate(script):
    spec=importlib.util.spec_from_file_location('labeled_analysis',script)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    cases=json.loads((ROOT/'evals/analysis/labeled-cases.json').read_text(encoding='utf-8'))
    records=[]; tp=fp=fn=0
    for case in cases:
        with tempfile.TemporaryDirectory(prefix='gdw-analysis-label-') as d:
            root=Path(d)
            files={'project.godot':'[application]','case.gd':case['code'],'base.gd':'extends Node',
                   **{name:'[gd_resource format=3]' for name in ['a.tres','b.tres','a_b.tres','a#v.tres']},**case['extra_files']}
            for name,text in files.items(): (root/name).write_text(text,encoding='utf-8')
            result=module.analyze_project(root)
            predicted={(r['kind'],r['target']) for r in result['references'] if r['source']=='case.gd' and r['kind'] in {'load','preload','extends'}}
            expected={tuple(x) for x in case['expected']}
            tp+=len(predicted&expected); fp+=len(predicted-expected); fn+=len(expected-predicted)
            records.append({'id':case['id'],'expected':sorted(expected),'predicted':sorted(predicted),'matched':predicted==expected})
    return {'cases':records,'matched_cases':sum(r['matched'] for r in records),'case_count':len(records),
            'true_positive_references':tp,'false_positive_references':fp,'false_negative_references':fn,
            'precision':tp/(tp+fp) if tp+fp else None,'recall':tp/(tp+fn) if tp+fn else None}

def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--baseline-script'); parser.add_argument('--output',required=True)
    args=parser.parse_args()
    result={'current':evaluate(ROOT/'skills/gamedev-workbench/scripts/project_analysis.py'),
            'limits':['Hand-labeled regression corpus developed with this implementation; not an independent held-out benchmark.',
                      'Metrics concern explicit resource-call/extends edges in these fixtures, not whole-project semantic accuracy.']}
    if args.baseline_script: result['baseline']=evaluate(args.baseline_script)
    with Path(args.output).open('x',encoding='utf-8') as file: json.dump(result,file,indent=2)
    print(json.dumps({k:{f:v for f,v in value.items() if f!='cases'} for k,value in result.items() if isinstance(value,dict)},indent=2))
    return 0 if result['current']['matched_cases']==result['current']['case_count'] else 1

if __name__=='__main__': raise SystemExit(main())
