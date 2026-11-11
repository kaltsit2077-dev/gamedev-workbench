"""Frozen common behavioral grader. Execute against a disposable artifact copy."""
import importlib.util
import json
from pathlib import Path
import sys

def load(folder):
    spec=importlib.util.spec_from_file_location('settings_under_test',Path(folder)/'settings.py')
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module.Settings

def grade(folder):
    Settings=load(folder); checks=[]
    def check(name,body):
        try: body(); checks.append({'name':name,'passed':True})
        except Exception as error: checks.append({'name':name,'passed':False,'error_type':type(error).__name__})
    def expect(value):
        if not value: raise AssertionError()
    def initial_copy():
        s=Settings(lambda c:True,lambda c:None); view=s.values
        expect(view=={'volume':0.5,'bindings':{'jump':'Space','fire':'J'}})
        view['bindings']['jump']='X'; expect(s.values['bindings']['jump']=='Space')
    def invalid():
        for changes in [None,[],{}, {'other':1},{'volume':True},{'volume':-1},{'volume':1.1},
                        {'volume':float('nan')},{'volume':float('inf')},{'bindings':{}},
                        {'bindings':{'unknown':'X'}},{'bindings':{'jump':'  '}},{'bindings':{'jump':1}},
                        {'bindings':{'jump':'J'}}]:
            calls=[]; s=Settings(lambda c:calls.append(c) or True,lambda c:calls.append(c))
            original=s.values.copy(); expect(s.apply(changes) is False); expect(not calls); expect(s.values==original)
    def persistence_failure():
        for result in [False,None,1,'yes']:
            calls=[]; s=Settings(lambda c:result,lambda c:calls.append(c))
            expect(s.apply({'volume':0.8}) is False); expect(s.values['volume']==0.5); expect(not calls)
        failing=[True]
        def fail(c):
            if failing[0]: raise OSError('synthetic failure')
            return True
        s=Settings(fail,lambda c:None); expect(s.apply({'volume':0.8}) is False); expect(s.values['volume']==0.5)
        failing[0]=False; expect(s.apply({'volume':0.8}) is True)
    def order():
        events=[]; holder=[]
        def writer(candidate):
            expect(holder[0].values['volume']==0.5); events.append('write'); return True
        def listener(candidate):
            expect(holder[0].values['volume']==0.8); events.append('notify')
        s=Settings(writer,listener); holder.append(s)
        expect(s.apply({'volume':0.8}) is True); expect(events==['write','notify'])
    def patches():
        calls=[]; s=Settings(lambda c:calls.append(c) or True,lambda c:None)
        patch={'bindings':{'jump':'K'}}
        expect(s.apply(patch) is True); patch['bindings']['jump']='X'
        expect(s.values['bindings']=={'jump':'K','fire':'J'})
        expect(calls[0]['bindings']=={'jump':'K','fire':'J'})
    def callback_copies():
        def writer(c): c['bindings']['jump']='POISON'; return True
        def listener(c): c['bindings']['fire']='POISON'
        s=Settings(writer,listener); expect(s.apply({'volume':0.8}) is True)
        expect(s.values['bindings']=={'jump':'Space','fire':'J'})
    def no_op():
        calls=[]; s=Settings(lambda c:calls.append(c) or True,lambda c:calls.append(c))
        expect(s.apply({'volume':0.5}) is True); expect(s.apply({'bindings':{'jump':'Space'}}) is True); expect(not calls)
    def reentrant():
        nested=[]; holder=[]
        def writer(c): nested.append(holder[0].apply({'volume':0.2})); return True
        def listener(c): nested.append(holder[0].apply({'volume':0.1}))
        s=Settings(writer,listener); holder.append(s)
        expect(s.apply({'volume':0.8}) is True); expect(nested==[False,False]); expect(s.values['volume']==0.8)
        expect(s.apply({'volume':0.7}) is True); expect(s.values['volume']==0.7)
    def listener_failure():
        def listener(c): raise ValueError('synthetic notification failure')
        s=Settings(lambda c:True,listener)
        expect(s.apply({'volume':0.8}) is True); expect(s.values['volume']==0.8)
        expect(s.apply({'volume':0.9}) is True); expect(s.values['volume']==0.9)
    def atomic_invalid():
        calls=[]; s=Settings(lambda c:calls.append(c) or True,lambda c:calls.append(c))
        expect(s.apply({'volume':0.8,'bindings':{'jump':'J'}}) is False)
        expect(s.values['volume']==0.5); expect(not calls)
    for name,body in [('initial and deep-copy read',initial_copy),('invalid inputs have no effects',invalid),
                      ('strict persistence result and recovery',persistence_failure),('persist before commit before notify',order),
                      ('binding patch and caller ownership',patches),('callback snapshots isolated',callback_copies),
                      ('no-op is silent',no_op),('reentrant writes rejected',reentrant),
                      ('notification exception keeps commit',listener_failure),('mixed invalid patch atomicity',atomic_invalid)]: check(name,body)
    return {'passed':all(c['passed'] for c in checks),'checks':checks}

if __name__=='__main__':
    result=grade(sys.argv[1]); print('EVAL_RESULT:'+json.dumps(result)); raise SystemExit(0 if result['passed'] else 1)
