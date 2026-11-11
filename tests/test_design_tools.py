import copy
import importlib.util
import json
from pathlib import Path
import shutil
import struct
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
def module(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'skills/gamedev-workbench/scripts'/f'{name}.py')
    value=importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value
n=module('narrative_checks'); e=module('economy_simulation'); a=module('asset_preflight')

class DesignToolTests(unittest.TestCase):
    def story(self):
        return {'start':'start','flags':{'key':False},'nodes':[
            {'id':'start','choices':[{'to':'cache','require':{'key':False}},{'to':'end','require':{'key':True}}]},
            {'id':'cache','choices':[{'to':'start','set':{'key':True}}]}, {'id':'end','ending':True}]}
    def test_narrative_revisits_same_node_with_new_flags(self):
        story=self.story(); original=copy.deepcopy(story); report=n.check_narrative(story)
        self.assertTrue(report['passed']); self.assertEqual(report['states_explored'],4)
        self.assertEqual(story,original)
    def test_narrative_softlock_and_cycle_without_exit(self):
        story=self.story(); story['nodes'][1]['choices']=[]
        report=n.check_narrative(story); self.assertFalse(report['passed']); self.assertEqual(report['softlocks'][0]['node'],'cache')
        story={'start':'a','nodes':[{'id':'a','choices':[{'to':'loop'},{'to':'end'}]},
                {'id':'loop','choices':[{'to':'loop'}]},{'id':'end','ending':True}]}
        report=n.check_narrative(story); self.assertEqual(report['non_terminating_states'],1); self.assertFalse(report['passed'])
    def test_narrative_unknown_flags_targets_and_partial_budget(self):
        story=self.story(); story['nodes'][0]['choices'][0]['require']={'absent':True}
        self.assertFalse(n.check_narrative(story)['passed'])
        self.assertFalse(n.check_narrative({'start':{},'nodes':[{'id':'a'}]})['passed'])
        self.assertFalse(n.check_narrative({'start':'a','nodes':[{'id':'a','choices':[{'to':[]}]}]})['passed'])
        report=n.check_narrative(self.story(),max_states=2)
        self.assertFalse(report['complete']); self.assertIsNone(report['non_terminating_states'])
    def test_economy_conserves_currency_and_is_repeatable(self):
        data={'steps':4,'base_income':2,'income_scale_percent':[100],
              'upgrades':[{'id':'drill','cost':3,'income_bonus':1,'max_level':2,'price_growth_percent':50}]}
        report=e.simulate_economy(data); result=report['scenarios'][0]
        self.assertTrue(report['passed']); self.assertEqual(result['final_currency'],2)
        self.assertEqual(result['total_spent'],8); self.assertEqual(result['first_purchase_step'],2)
        self.assertEqual(e.simulate_economy(data),report)
    def test_economy_rejects_invalid_domains(self):
        for data in [{'steps':True,'upgrades':[{'id':'a','cost':1}]},
                     {'upgrades':[{'id':'a','cost':0}]},
                     {'income_scale_percent':[float('nan')],'upgrades':[{'id':'a','cost':1}]}]:
            self.assertFalse(e.simulate_economy(data)['passed'])
    def test_asset_header_dependency_and_no_writes(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); shutil.copy2(ROOT/'docs/media/godot-demo.png',root/'ui.png')
            (root/'scene.gltf').write_text(json.dumps({'asset':{'version':'2.0'},'images':[{'uri':'ui.png'}]}))
            before={p.name:p.read_bytes() for p in root.iterdir()}
            report=a.audit_assets(root,{'assets':[{'path':'scene.gltf','license':'Apache-2.0'},{'path':'ui.png','license':'Apache-2.0','expected_size':[960,540]}]})
            self.assertTrue(report['passed']); self.assertEqual(report['assets'][0]['dependencies'],['ui.png'])
            self.assertEqual(before,{p.name:p.read_bytes() for p in root.iterdir()})
            payload=json.dumps({'asset':{'version':'2.0'},'images':[{'uri':'ui.png'}]}).encode()
            payload+=b' '*((-len(payload))%4)
            binary=struct.pack('<4sII',b'glTF',2,20+len(payload))+struct.pack('<II',len(payload),0x4e4f534a)+payload
            (root/'scene.glb').write_bytes(binary)
            manifest={'assets':[{'path':'scene.glb','license':'Apache-2.0'}]}
            self.assertTrue(a.audit_assets(root,manifest)['passed'])
            (root/'scene.glb').write_bytes(binary[:-1])
            self.assertFalse(a.audit_assets(root,manifest)['passed'])
    def test_asset_missing_escaping_and_unknown_metadata(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/'scene.gltf').write_text(json.dumps({'images':[{'uri':'../escape.png'}]}))
            self.assertFalse(a.audit_assets(root,{'assets':[{'path':'scene.gltf','license':'unknown'}]})['passed'])
            (root/'scene.gltf').write_text(json.dumps({'images':[{'uri':'missing.png'}]}))
            self.assertFalse(a.audit_assets(root,{'assets':[{'path':'scene.gltf','license':'Apache-2.0'}]})['passed'])
            self.assertFalse(a.audit_assets(root,{'assets':[{'path':[]}]})['passed'])

if __name__=='__main__': unittest.main()
