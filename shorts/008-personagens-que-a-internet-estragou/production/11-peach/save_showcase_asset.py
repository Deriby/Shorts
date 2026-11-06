"""Extract the crown display, pedestals and frame with a neutral picture surface."""
from pathlib import Path
import bpy
from mathutils import Matrix

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if(p/'AGENTS.md').exists())
scene=bpy.context.scene;scene.frame_set(438);bpy.context.view_layer.update()
objects=[o for o in scene.objects if o.name.startswith('SHOWCASE |') and 'Dery'not in o.name
         and o.type in {'MESH','EMPTY'} and not o.name.endswith((' wrist',' palm'))]
selected=set(objects);worlds={o:o.matrix_world.copy()for o in objects};parents={o:o.parent for o in objects}
collection=bpy.data.collections.new('Massacote | vitrine de coroas')
origin=bpy.data.objects.new('SHOWCASE | reusable origin',None);collection.objects.link(origin)
mat=bpy.data.materials.new('SHOWCASE | replaceable display');mat.use_nodes=True
nt=mat.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(.12,.04,.12,1)
out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],out.inputs[0])
for o in objects:
 o.animation_data_clear();o.hide_render=False
 if o.type=='MESH':
  for m in list(o.modifiers):
   if m.type=='NODES':o.modifiers.remove(m)
  if o.name=='SHOWCASE | display picture':o.data.materials.clear();o.data.materials.append(mat)
 collection.objects.link(o)
for o in objects:
 parent=parents[o];o.matrix_parent_inverse=Matrix.Identity(4)
 if parent in selected:o.parent=parent;o.matrix_basis=worlds[parent].inverted()@worlds[o]
 else:o.parent=origin;o.matrix_basis=Matrix.Translation((-20,0,0))@worlds[o]
path=REPO/'assets/cenarios/vitrine_coroas/Vitrine_Coroas.blend';path.parent.mkdir(parents=True,exist_ok=True)
bpy.data.libraries.write(str(path),{collection},fake_user=True,compress=True)
print('SHOWCASE_ASSET_READY',flush=True)
