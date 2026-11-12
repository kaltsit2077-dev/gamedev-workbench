"""Original Blender background case; requires real bpy inside Blender."""
import json
import os
import bpy

bpy.ops.mesh.primitive_cube_add(size=1, location=(1, 2, 3))
cube = bpy.context.object
mesh = cube.data
position_ok = tuple(cube.location) == (1.0, 2.0, 3.0)
name, mesh_name = cube.name, mesh.name
bpy.data.objects.remove(cube, do_unlink=True)
bpy.data.meshes.remove(mesh)
checks = [{'name': 'object transform', 'passed': position_ok},
          {'name': 'object and mesh cleanup', 'passed': name not in bpy.data.objects and mesh_name not in bpy.data.meshes}]
result = {'engine': 'blender', 'engine_version': bpy.app.version_string,
          'passed': all(c['passed'] for c in checks), 'checks': checks}
with open(os.environ['GDW_TEST_REPORT'], 'x', encoding='utf-8') as file: json.dump(result, file, indent=2)
if not result['passed']: raise RuntimeError('Original Blender fixture failed')
