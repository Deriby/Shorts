"""Reusable entrance geometry, without actor, camera, voice or source references."""
from pathlib import Path
import bpy
from mathutils import Matrix
ROOT=Path(__file__).resolve().parent;REPO=next(p for p in ROOT.parents if(p/'AGENTS.md').exists());s=bpy.context.scene;s.frame_set(421)
collection=bpy.data.collections.new('Massacote | entrada de castelo');origin=bpy.data.objects.new('CASTLE | reusable origin',None);collection.objects.link(origin)
objects=[o for o in s.objects if o.name.startswith('CASTLE |')and o.type=='MESH'and 'Dery'not in o.name]
for o in objects:
 o.animation_data_clear();o.hide_render=False
 for m in list(o.modifiers):
  if m.type=='NODES':o.modifiers.remove(m)
 collection.objects.link(o);o.parent=origin;o.matrix_parent_inverse=Matrix.Identity(4);o.location.x-=20
path=REPO/'assets/cenarios/entrada_castelo/Entrada_Castelo.blend';path.parent.mkdir(parents=True,exist_ok=True);bpy.data.libraries.write(str(path),{collection},fake_user=True,compress=True)
print('CASTLE_ASSET_READY',flush=True)
