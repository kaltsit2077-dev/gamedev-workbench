"""Small deterministic routing regression, not an LLM productivity benchmark."""
import json
from pathlib import Path
import runpy

ROOT=Path(__file__).resolve().parents[1]
w=runpy.run_path(str(ROOT/'skills/gamedev-workbench/scripts/workbench.py'))

def baseline(task):
    task=task.casefold()
    scores=[(m['id'],sum(k in task for k in m['keywords'])) for m in w['modes']()]
    return [name for name,score in sorted(scores,key=lambda r:-r[1]) if score] or ['guide']

def evaluate():
    records=[]
    cases=json.loads((ROOT/'evals/routing_cases.json').read_text(encoding='utf-8'))
    for case in cases:
        old=baseline(case['task']); new=w['route'](case['task'])
        def passes(value): return set(case['include']).issubset(value) and not set(case['exclude']).intersection(value)
        records.append(dict(task=case['task'],before=old,after=new,before_pass=passes(old),after_pass=passes(new)))
    return {'scope':'deterministic keyword routing regression; no agent comparison',
            'cases':len(records),'before_pass':sum(r['before_pass'] for r in records),
            'after_pass':sum(r['after_pass'] for r in records),'results':records}

if __name__=='__main__':
    print(json.dumps(evaluate(),ensure_ascii=False,indent=2))
