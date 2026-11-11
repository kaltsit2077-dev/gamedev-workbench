"""Descriptive paired results with explicit missing/estimated/provider-reported costs."""
import math
from statistics import median

def number(value):
    try: return type(value) in {int,float} and math.isfinite(value) and value>=0
    except OverflowError: return False

def summarize_evaluations(data):
    if not isinstance(data,dict) or not isinstance(data.get('records'),list) or not 1<=len(data['records'])<=10000:
        raise ValueError('Expected 1..10000 evaluation records')
    groups={}; ids=set(); measured=[]; records=data['records']
    for row in records:
        if not isinstance(row,dict): raise ValueError('Invalid evaluation row')
        for key in ['run_id','task','model_configuration']:
            if not isinstance(row.get(key),str) or not row[key]: raise ValueError('Missing '+key)
        if row['run_id'] in ids: raise ValueError('Duplicate run_id')
        ids.add(row['run_id'])
        if not isinstance(row.get('arm'),str) or row['arm'] not in {'a','b'} or type(row.get('repetition')) is not int or row['repetition']<1: raise ValueError('Invalid arm/repetition')
        if type(row.get('passed')) is not bool or not number(row.get('elapsed_seconds')): raise ValueError('Invalid outcome/timer')
        rework=row.get('rework_rounds')
        if rework is not None and (type(rework) is not int or rework<0): raise ValueError('Invalid rework count')
        usage=row.get('usage',{'source':'unavailable'})
        if not isinstance(usage,dict) or not isinstance(usage.get('source'),str) or usage['source'] not in {'unavailable','estimate','provider_record'}: raise ValueError('Invalid usage source')
        for key in ['input_tokens','output_tokens']:
            value=usage.get(key)
            if value is not None and (type(value) is not int or value<0): raise ValueError('Invalid '+key)
        cost=usage.get('cost_usd')
        if cost is not None and not number(cost): raise ValueError('Invalid cost_usd')
        if usage['source']=='unavailable' and any(usage.get(k) is not None for k in ['input_tokens','output_tokens','cost_usd']):
            raise ValueError('Unavailable usage cannot contain fabricated measurements')
        if usage['source']=='provider_record' and not isinstance(usage.get('reference'),str): raise ValueError('Provider record needs a traceable reference')
        if usage['source']=='provider_record' and not usage['reference'].strip(): raise ValueError('Provider record reference is empty')
        measured.append(cost if usage['source']=='provider_record' else None)
        group=groups.setdefault((row['task'],row['repetition']),{})
        if row['arm'] in group: raise ValueError('Duplicate arm in one pair')
        group[row['arm']]=row
    pairs=[]; incomplete=[]
    for (task,repetition),arms in sorted(groups.items()):
        if set(arms)!={'a','b'}: incomplete.append({'task':task,'repetition':repetition,'reason':'missing arm'}); continue
        a,b=arms['a'],arms['b']
        if a['model_configuration']!=b['model_configuration'] or a['model_configuration'].startswith('unverified'):
            incomplete.append({'task':task,'repetition':repetition,'reason':'different or unverified declared model configurations'}); continue
        pairs.append({'task':task,'repetition':repetition,'a_passed':a['passed'],'b_passed':b['passed'],
                      'b_minus_a_seconds':b['elapsed_seconds']-a['elapsed_seconds'],
                      'b_minus_a_rework_rounds':b['rework_rounds']-a['rework_rounds'] if a.get('rework_rounds') is not None and b.get('rework_rounds') is not None else None})
    median_delta=median(p['b_minus_a_seconds'] for p in pairs) if pairs else None
    if median_delta is not None and not math.isfinite(median_delta): raise ValueError('Timer aggregate outside finite range')
    total=sum(measured) if all(c is not None for c in measured) else None
    if total is not None and not number(total): raise ValueError('Cost aggregate outside finite range')
    return {'kind':'evaluation-summary','paired_runs':len(pairs),'pairs':pairs,'unpaired_or_mismatched':incomplete,
            'median_b_minus_a_seconds':median_delta,
            'b_only_passed':sum(p['b_passed'] and not p['a_passed'] for p in pairs),
            'a_only_passed':sum(p['a_passed'] and not p['b_passed'] for p in pairs),
            'reported_measured_cost_usd_total':total,
            'cost_records_missing_or_not_measured':sum(c is None for c in measured),
            'limits':['Caller supplies model/isolation/timing records; this tool cannot verify backend identity or an invoice.',
                      'Estimated costs never enter measured-cost totals; missing fees remain null.',
                      'Descriptive pairs are not causal, statistically significant productivity evidence.',
                      'Behavioral acceptance and post-grading rework do not replace independent architecture/design review.']}
