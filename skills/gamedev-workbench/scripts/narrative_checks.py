"""Finite boolean-state dialogue checks. Does not execute story expressions."""
from collections import deque

def check_narrative(data,max_states=50000):
    errors=[]
    result={'kind':'narrative-check','passed':False,'complete':False,'errors':errors,'states_explored':0,
            'limits':['Only declared boolean flags and choice require/set maps are modeled.','Reachability and termination are structural checks, not narrative quality or player behavior.']}
    if not isinstance(data,dict): errors.append('Story must be an object'); return result
    flags=data.get('flags',{}); nodes=data.get('nodes')
    if not isinstance(flags,dict) or len(flags)>12 or not all(isinstance(k,str) and type(v) is bool for k,v in flags.items()):
        errors.append('flags must contain at most 12 boolean declarations'); return result
    if not isinstance(nodes,list) or not 1<=len(nodes)<=256 or not 1<=max_states<=50000:
        errors.append('nodes/state budget outside supported range'); return result
    by_id={}
    for node in nodes:
        if not isinstance(node,dict) or not isinstance(node.get('id'),str) or not node['id']:
            errors.append('Every node needs a nonempty id'); continue
        if node['id'] in by_id: errors.append('Duplicate node: '+node['id'])
        by_id[node['id']]=node
        if type(node.get('ending',False)) is not bool: errors.append('ending must be boolean: '+node['id'])
        choices=node.get('choices',[])
        if not isinstance(choices,list) or len(choices)>32:
            errors.append('Invalid choices: '+node['id']); continue
        if node.get('ending') and choices: errors.append('Ending has outgoing choices: '+node['id'])
        for choice in choices:
            if not isinstance(choice,dict) or not isinstance(choice.get('to'),str):
                errors.append('Invalid choice target: '+node['id']); continue
            for key in ['require','set']:
                mapping=choice.get(key,{})
                if not isinstance(mapping,dict) or not all(k in flags and type(v) is bool for k,v in mapping.items()):
                    errors.append('Invalid '+key+' flag map: '+node['id'])
    if not isinstance(data.get('start'),str) or data['start'] not in by_id: errors.append('Unknown start node')
    for node in by_id.values():
        if not isinstance(node.get('choices',[]),list): continue
        for choice in node.get('choices',[]):
            if isinstance(choice,dict) and isinstance(choice.get('to'),str) and choice['to'] not in by_id: errors.append('Dangling target from '+node['id'])
    if errors: return result
    names=sorted(flags); initial=(data['start'],tuple(flags[n] for n in names))
    queue=deque([initial]); visited={initial}; reverse={}; endings=set(); softlocks=[]; previous={initial:None}
    complete=True
    while queue and complete:
        state=queue.popleft(); node=by_id[state[0]]; values=dict(zip(names,state[1])); successors=[]
        if node.get('ending',False): endings.add(state)
        for index,choice in enumerate(node.get('choices',[])):
            if not all(values[k]==v for k,v in choice.get('require',{}).items()): continue
            updated={**values,**choice.get('set',{})}; target=(choice['to'],tuple(updated[n] for n in names))
            successors.append(target); reverse.setdefault(target,set()).add(state)
            if target not in visited:
                if len(visited)>=max_states: complete=False; break
                visited.add(target); previous[target]=(state,index); queue.append(target)
        if not successors and not node.get('ending',False): softlocks.append(state)
    terminating=set(endings); queue=deque(endings)
    while queue:
        for parent in reverse.get(queue.popleft(),()):
            if parent not in terminating: terminating.add(parent); queue.append(parent)
    def describe(state): return {'node':state[0],'flags':dict(zip(names,state[1]))}
    witnesses=[]
    for state in softlocks[:20]:
        path=[]; cursor=state
        while cursor is not None:
            path.append(cursor[0]); prior=previous[cursor]; cursor=prior[0] if prior else None
        witnesses.append({**describe(state),'node_path':list(reversed(path))[:200],'path_truncated':len(path)>200})
    result.update(complete=complete,states_explored=len(visited),reachable_endings=sorted({s[0] for s in endings}),
                  unreachable_nodes=sorted(by_id.keys()-{s[0] for s in visited}) if complete else None,
                  softlocks=witnesses,non_terminating_states=len(visited-terminating) if complete else None,
                  passed=complete and not softlocks and bool(endings) and visited<=terminating)
    if not complete: errors.append('State budget reached; reachability/termination results are incomplete')
    return result
