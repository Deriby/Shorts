"""Save the interview set with neutral reference surface and no actors or media."""
from pathlib import Path
import bpy
from mathutils import Matrix
ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'AGENTS.md').exists())
s=bpy.context.scene;s.frame_set(346);bpy.context.view_layer.update()
collection=bpy.data.collections.new('Massacote | set de entrevista')
origin=bpy.data.objects.new('INTERVIEW | reusable origin',None);collection.objects.link(origin)
objects=[o for o in s.objects if o.type=='MESH' and o.name.startswith('INTERVIEW |')
         and o.name not in ['INTERVIEW | Host','INTERVIEW | Guest']]
worlds={o:o.matrix_world.copy()for o in objects}
mat=bpy.data.materials.new('INTERVIEW | neutral reference surface');mat.use_nodes=True
nt=mat.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(.15,.25,.31,1)
out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],out.inputs[0])
for o in objects:
    o.animation_data_clear();o.hide_render=False
    for m in list(o.modifiers):
        if m.type=='NODES':o.modifiers.remove(m)
    if o.name=='INTERVIEW | reference picture':o.data.materials[0]=mat
    collection.objects.link(o);o.parent=origin;o.matrix_parent_inverse=Matrix.Identity(4)
    o.matrix_world=Matrix.Translation((-20,0,0))@worlds[o]
path=REPO/'assets/cenarios/set_entrevista/Set_Entrevista.blend'
path.parent.mkdir(parents=True,exist_ok=True)
bpy.data.libraries.write(str(path),{collection},fake_user=True,compress=True)
print('INTERVIEW_ASSET_READY',flush=True)
