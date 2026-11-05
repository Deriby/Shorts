"""Save the reusable writing desk geometry without actor, voice, camera or episode movie."""
from pathlib import Path
import bpy
from mathutils import Matrix
ROOT=Path(__file__).resolve().parent;REPO=next(p for p in ROOT.parents if(p/'AGENTS.md').exists());s=bpy.context.scene;s.frame_set(721);bpy.context.view_layer.update()
collection=bpy.data.collections.new('Massacote | mesa de redação');origin=bpy.data.objects.new('DESK | reusable origin',None);collection.objects.link(origin)
objects=[o for o in s.objects if o.name.startswith('DESK |')and o.type=='MESH'and'Dery'not in o.name];worlds={o:o.matrix_world.copy()for o in objects}
mat=bpy.data.materials.new('DESK | replaceable display surface');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(.72,.64,.42,1);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],out.inputs[0])
for o in objects:
 o.animation_data_clear();o.hide_render=False
 for m in list(o.modifiers):
  if m.type=='NODES':o.modifiers.remove(m)
 if o.name=='DESK | display':o.data.materials[0]=mat
 collection.objects.link(o);o.parent=origin;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_world=Matrix.Translation((-20,0,0))@worlds[o]
path=REPO/'assets/cenarios/mesa_redacao/Mesa_Redacao.blend';path.parent.mkdir(parents=True,exist_ok=True);bpy.data.libraries.write(str(path),{collection},fake_user=True,compress=True);print('DESK_ASSET_READY',flush=True)
