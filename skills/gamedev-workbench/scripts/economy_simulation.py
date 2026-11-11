"""Deterministic integer-currency sensitivity scenarios; no player prediction."""

def integer(value,minimum,maximum):
    return type(value) is int and minimum<=value<=maximum

def simulate_economy(data):
    errors=[]; result={'kind':'economy-simulation','passed':False,'errors':errors,
                      'limits':['One cheapest-affordable purchase per step after income.','Integer growth uses ceiling after each purchase.','Scenarios are assumptions, not calibrated player behavior, fun or revenue forecasts.']}
    if not isinstance(data,dict): errors.append('Economy must be an object'); return result
    for key,default,minimum,maximum in [('steps',100,1,10000),('initial_currency',0,0,10**12),('base_income',1,0,10**9)]:
        if not integer(data.get(key,default),minimum,maximum): errors.append('Invalid '+key)
    upgrades=data.get('upgrades'); seen=set()
    if not isinstance(upgrades,list) or not 1<=len(upgrades)<=100: errors.append('upgrades must have 1..100 entries'); return result
    for item in upgrades:
        if not isinstance(item,dict) or not isinstance(item.get('id'),str) or not item['id'] or item['id'] in seen:
            errors.append('Upgrade ids must be nonempty and unique'); continue
        seen.add(item['id'])
        for key,default,minimum,maximum in [('cost',None,1,10**12),('income_bonus',0,0,10**9),('max_level',10,1,100),('price_growth_percent',0,0,500)]:
            if not integer(item.get(key,default),minimum,maximum): errors.append('Invalid '+item['id']+'.'+key)
    scales=data.get('income_scale_percent',[80,100,120])
    if not isinstance(scales,list) or not 1<=len(scales)<=10 or not all(integer(x,0,500) for x in scales): errors.append('Invalid income_scale_percent')
    if errors: return result
    scenarios=[]
    for scale in scales:
        wallet=data.get('initial_currency',0); initial=wallet; earned=0; spent=0; trace=[]; purchases=0; first=None
        levels={u['id']:0 for u in upgrades}; prices={u['id']:u['cost'] for u in upgrades}
        for step in range(1,data.get('steps',100)+1):
            income=(data.get('base_income',1)+sum(u.get('income_bonus',0)*levels[u['id']] for u in upgrades))*scale//100
            wallet+=income; earned+=income
            available=[u for u in upgrades if levels[u['id']]<u.get('max_level',10) and prices[u['id']]<=wallet]
            if not available: continue
            chosen=min(available,key=lambda u:(prices[u['id']],u['id'])); key=chosen['id']; cost=prices[key]
            wallet-=cost; spent+=cost; levels[key]+=1; purchases+=1
            if first is None: first=step
            if len(trace)<200: trace.append({'step':step,'upgrade':key,'cost':cost,'currency_after':wallet})
            prices[key]=(cost*(100+chosen.get('price_growth_percent',0))+99)//100
        scenarios.append({'income_scale_percent':scale,'final_currency':wallet,'total_earned':earned,'total_spent':spent,
                          'conservation_holds':initial+earned-spent==wallet,'levels':levels,'purchase_count':purchases,
                          'first_purchase_step':first,'purchases':trace,'trace_truncated':purchases>len(trace)})
    result.update(passed=all(s['conservation_holds'] for s in scenarios),scenarios=scenarios)
    return result
