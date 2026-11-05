"""Save reusable stage geometry without actor, voice or movie dependencies."""
from pathlib import Path
import bpy
from mathutils import Matrix
ROOT=Path(__file__).resolve().parent;REPO=next(p for p in ROOT.parents if(p/'AGENTS.md').exists());s=bpy.context.scene;s.frame_set(378)
collection=bpy.data.collections.new('Massacote | sala de reunião');origin=bpy.data.objects.new('MEETING | reusable origin',None);collection.objects.link(origin)
objects=[o for o in s.objects if o.name.startswith('MEETING |')and o.type=='MESH'and'Dery'not in o.name];worlds={o:o.matrix_world.copy()for o in objects}
for o in objects:
 o.animation_data_clear();o.hide_render=False
 for m in list(o.modifiers):
  if m.type=='NODES':o.modifiers.remove(m)
 collection.objects.link(o);o.parent=origin;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_world=Matrix.Translation((-20,0,0))@worlds[o]
# A packed authored still replaces the episode-specific moving feed.
mat=bpy.data.materials.new('MEETING | reusable censored call');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');em=nt.nodes.new('ShaderNodeEmission');tx=nt.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(ROOT/'assets/memes/call_censored.png'),check_existing=True);tx.image.pack();tx.interpolation='Closest';nt.links.new(tx.outputs['Color'],em.inputs['Color']);nt.links.new(em.outputs[0],out.inputs[0]);bpy.data.objects['MEETING | projector image'].data.materials[0]=mat
path=REPO/'assets/cenarios/sala_reuniao/Sala_Reuniao.blend';path.parent.mkdir(parents=True,exist_ok=True);bpy.data.libraries.write(str(path),{collection},fake_user=True,compress=True);print('MEETING_ASSET_READY',flush=True)
