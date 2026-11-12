"""Original editor-only case. Requires the engine's built-in Python plugin."""
import json
import os
from pathlib import Path
import unreal

report={'engine':'unreal','engine_version':unreal.SystemLibrary.get_engine_version(),'passed':False,'checks':[]}
actor=None
try:
    world=unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
    report['checks'].append({'name':'new disposable editor world','passed':world is not None})
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0))
    report['checks'].append({'name':'native actor created','passed':actor is not None})
    if actor is not None:
        actor.set_actor_location(unreal.Vector(100,0,0),False,False)
        report['checks'].append({'name':'native transform applied','passed':abs(actor.get_actor_location().x-100)<0.01})
        cleaned=actors.destroy_actor(actor); actor=None
        report['checks'].append({'name':'native actor destroyed','passed':bool(cleaned)})
    report['passed']=len(report['checks'])==4 and all(c['passed'] for c in report['checks'])
except Exception as error:
    report['error_type']=type(error).__name__
finally:
    if actor is not None: unreal.get_editor_subsystem(unreal.EditorActorSubsystem).destroy_actor(actor)
    path=Path(os.environ['GDW_EDITOR_REPORT']); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    unreal.log('WORKBENCH_EDITOR: '+('PASS' if report['passed'] else 'FAIL'))
    unreal.SystemLibrary.quit_editor()
