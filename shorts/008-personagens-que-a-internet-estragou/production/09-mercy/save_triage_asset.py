"""Extract the triage furniture, retaining local groups and neutral displays."""
from pathlib import Path
import bpy
from mathutils import Matrix

ROOT = Path(__file__).resolve().parent
REPO = next(p for p in ROOT.parents if (p / 'AGENTS.md').exists())
scene = bpy.context.scene
scene.frame_set(420)
bpy.context.view_layer.update()
objects = [o for o in scene.objects
           if o.name.startswith('TRIAGE |') and 'Dery' not in o.name
           and o.type in {'MESH', 'EMPTY'}
           and not o.name.endswith((' wrist', ' palm'))]
selected = set(objects)
worlds = {o: o.matrix_world.copy() for o in objects}
parents = {o: o.parent for o in objects}
collection = bpy.data.collections.new('Massacote | baia de triagem')
origin = bpy.data.objects.new('TRIAGE | reusable origin', None)
collection.objects.link(origin)
neutral = bpy.data.materials.new('TRIAGE | replaceable display')
neutral.use_nodes = True
nodes = neutral.node_tree.nodes
nodes.clear()
emission = nodes.new('ShaderNodeEmission')
emission.inputs['Color'].default_value = (.12, .29, .30, 1)
output = nodes.new('ShaderNodeOutputMaterial')
neutral.node_tree.links.new(emission.outputs[0], output.inputs[0])
for obj in objects:
    obj.animation_data_clear()
    obj.hide_render = False
    if obj.type == 'MESH':
        for modifier in list(obj.modifiers):
            if modifier.type == 'NODES':
                obj.modifiers.remove(modifier)
        if obj.name in {'TRIAGE | Mercy picture', 'TRIAGE | terminal picture'}:
            obj.data.materials.clear()
            obj.data.materials.append(neutral)
    collection.objects.link(obj)
for obj in objects:
    parent = parents[obj]
    obj.matrix_parent_inverse = Matrix.Identity(4)
    if parent in selected:
        obj.parent = parent
        obj.matrix_basis = worlds[parent].inverted() @ worlds[obj]
    else:
        obj.parent = origin
        obj.matrix_basis = Matrix.Translation((-20, 0, 0)) @ worlds[obj]
assert objects and all(o.type != 'ARMATURE' for o in collection.objects)
path = REPO / 'assets/cenarios/baia_triagem/Baia_Triagem.blend'
path.parent.mkdir(parents=True, exist_ok=True)
bpy.data.libraries.write(str(path), {collection}, fake_user=True, compress=True)
print('TRIAGE_ASSET_READY', flush=True)
