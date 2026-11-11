"""Place the approved Massacote M on the existing v5 shirt material only."""
from pathlib import Path
import bpy
import hashlib
import json
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'refino_v3_v5/Dery_v3_Refino_v5.blend'
LOGO = ROOT.parents[4] / 'marca/massacote-games/logo.png'
source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
body = bpy.data.objects['Dery_Massacote_Rig_PS1_v2']
mesh = body.data

def state():
    return {
        'positions': hashlib.sha256(np.array([v.co[:] for v in mesh.vertices], dtype=np.float32).tobytes()).hexdigest(),
        'existing_uvs': {uv.name: hashlib.sha256(np.array([v.uv[:] for v in uv.data], dtype=np.float32).tobytes()).hexdigest() for uv in mesh.uv_layers if uv.name != 'DeryLogoChest'},
        'material_indices': [p.material_index for p in mesh.polygons],
        'bones': len(next(o for o in bpy.data.objects if o.type == 'ARMATURE').data.bones),
    }

before = state()
original_images = {im.name: hashlib.sha256(np.array(im.pixels[:], dtype=np.float32).tobytes()).hexdigest() for im in bpy.data.images if im.type == 'IMAGE'}
active_uv = mesh.uv_layers.active.name
mesh.uv_layers.new(name='DeryLogoChest')
mesh.attributes.new(name='DeryLogoFront', type='FLOAT', domain='CORNER')
# Adding mesh attributes can invalidate RNA references to earlier layers.
uv = mesh.uv_layers['DeryLogoChest']
front = mesh.attributes['DeryLogoFront']
for loop in mesh.loops:
    co = body.matrix_world @ mesh.vertices[loop.vertex_index].co
    uv.data[loop.index].uv = (co.x / .22 + .5, (co.z - 1.31) / .22 + .5)
    front.data[loop.index].value = float(co.y < -.02)
mesh.uv_layers.active = mesh.uv_layers[active_uv]
mesh.uv_layers[active_uv].active_render = True

material = mesh.materials[0]
nt = material.node_tree
nodes, links = nt.nodes, nt.links
lighting = next(n for n in nodes if n.type == 'MIX_RGB' and n.blend_type == 'MULTIPLY')
base = lighting.inputs[1].links[0].from_socket
coords = nodes.new('ShaderNodeUVMap')
coords.uv_map = 'DeryLogoChest'
coords.label = 'M central no peito | acompanha a malha'
scale = nodes.new('ShaderNodeVectorMath'); scale.operation = 'SCALE'; scale.inputs['Scale'].default_value = 64
links.new(coords.outputs['UV'], scale.inputs[0])
floor = nodes.new('ShaderNodeVectorMath'); floor.operation = 'FLOOR'; links.new(scale.outputs[0], floor.inputs[0])
center = nodes.new('ShaderNodeVectorMath'); center.operation = 'ADD'; center.inputs[1].default_value = (.5, .5, 0); links.new(floor.outputs[0], center.inputs[0])
down = nodes.new('ShaderNodeVectorMath'); down.operation = 'SCALE'; down.inputs['Scale'].default_value = 1/64; links.new(center.outputs[0], down.inputs[0])
logo = nodes.new('ShaderNodeTexImage')
logo.name = 'MASSACOTE | M amarelo aprovado'
logo.label = 'Logo original | amostragem PS1 64 x 64'
logo.image = bpy.data.images.load(str(LOGO), check_existing=True)
logo.interpolation = 'Closest'; logo.extension = 'CLIP'
links.new(down.outputs[0], logo.inputs['Vector'])
mask = nodes.new('ShaderNodeAttribute'); mask.attribute_name = 'DeryLogoFront'
alpha = nodes.new('ShaderNodeMath'); alpha.operation = 'MULTIPLY'
links.new(logo.outputs['Alpha'], alpha.inputs[0]); links.new(mask.outputs['Fac'], alpha.inputs[1])
mix = nodes.new('ShaderNodeMixRGB'); mix.name = 'MASSACOTE | estampa sobre tecido existente'
links.new(alpha.outputs[0], mix.inputs[0]); links.new(base, mix.inputs[1]); links.new(logo.outputs['Color'], mix.inputs[2])
links.new(mix.outputs[0], lighting.inputs[1])

after = state()
assert after == before, {k: (before[k], after[k]) for k in before if before[k] != after[k]}
assert all(hashlib.sha256(np.array(bpy.data.images[name].pixels[:], dtype=np.float32).tobytes()).hexdigest() == value for name, value in original_images.items())
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT'; scene.eevee.taa_render_samples = 1
scene.render.resolution_percentage = 100
camera = scene.camera
for name, w, h, scale, focus, position in [
    ('Corpo', 900, 1100, 2.06, (0, 0, .91), (0, -5, .98)),
    ('Camiseta', 800, 800, .72, (0, -.045, 1.40), (0, -3, 1.40)),
]:
    scene.render.resolution_x = w; scene.render.resolution_y = h
    camera.data.ortho_scale = scale; camera.location = position
    camera.rotation_euler = (Vector(focus) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = str(ROOT / ('Previa_' + name + '.png'))
    bpy.ops.render.render(write_still=True)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'Dery_Camiseta_M_v6.blend'))
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == source_hash
record = {'source': str(SOURCE.relative_to(ROOT.parent)), 'source_sha256': source_hash, 'source_unchanged': True, 'existing_texture_pixels_unchanged': True, 'geometry_existing_uvs_material_assignments_unchanged': True, 'rig_bones': before['bones'], 'logo': 'assets/marca/massacote-games/logo.png', 'placement': 'center of front chest only', 'sampling_grid': [64, 64], 'logo_uv_square_m': .22, 'logo_uv_center_z_m': 1.31, 'new_expressions': 0, 'approved_by_user': False}
(ROOT / 'aplicacao.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
print(record)
