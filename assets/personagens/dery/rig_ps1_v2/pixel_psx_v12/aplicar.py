"""Sharper 64-texel facial sampling, retaining approved v11 geometry and all art."""
from pathlib import Path
import bpy
import numpy as np
import hashlib
import json
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'contorno_marcado_v11/Dery_Contorno_Marcado_v11.blend'
source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
body = bpy.data.objects['Dery_Massacote_Rig_PS1_v2']; mesh = body.data
original_key_names = [key.name for key in mesh.shape_keys.key_blocks]

def digest(values):
    return hashlib.sha256(np.asarray(values, dtype=np.float32).tobytes()).hexdigest()

def state():
    return {'basis': digest([v.co[:] for v in mesh.vertices]),
            'keys': {name: (mesh.shape_keys.key_blocks[name].value, digest([p.co[:] for p in mesh.shape_keys.key_blocks[name].data])) for name in original_key_names},
            'uvs': {uv.name: digest([p.uv[:] for p in uv.data]) for uv in mesh.uv_layers},
            'images': {im.name: digest(im.pixels[:]) for im in bpy.data.images if im.type == 'IMAGE'},
            'weights': digest([(v.index, g.group, g.weight) for v in mesh.vertices for g in v.groups]),
            'assignments': digest([p.material_index for p in mesh.polygons])}

before = state()
# Fit the complete frontal jaw/neck contour marked in the later user image.
# Width changes only: retain the previously marked side profile (Y/Z).
base = np.asarray([v.co[:] for v in mesh.vertices], dtype=np.float64)
current = base.copy()
for old in mesh.shape_keys.key_blocks[1:]:
    current += (np.asarray([p.co[:] for p in old.data]) - base) * old.value
matrix = body.matrix_world.copy(); inverse_delta = matrix.inverted().to_3x3()
neck = body.shape_key_add(name='DERY | rosto e pescoço conforme guia frontal')
neck.slider_min = 0; neck.slider_max = 1
def smooth(value):
    value = max(0, min(1, value)); return value * value * (3 - 2 * value)
head_group = body.vertex_groups['CC_Base_Head'].index
head_weights = [sum(g.weight for g in v.groups if g.group == head_group) for v in mesh.vertices]
world = np.asarray([(matrix @ Vector(co))[:] for co in current])
welded = {}
for index, co in enumerate(world): welded.setdefault(tuple(np.round(co, 6)), []).append(index)
face_profile = [(1.548, .62), (1.558, .62), (1.575, .80), (1.590, .88), (1.610, .94), (1.640, .99), (1.665, 1)]
neck_profile = [(1.483, 1), (1.515, 1), (1.527, .97), (1.540, .78), (1.558, .76), (1.585, .82), (1.610, 1)]
neck_displacements = []
for indices in welded.values():
    x, y, z = world[indices].mean(axis=0)
    head = smooth((float(np.mean([head_weights[i] for i in indices])) - .75) / .23)
    scope = (smooth((z - 1.483) / .015) * smooth((1.665 - z) / .020)
             * smooth((y + .150) / .025) * smooth((.115 - y) / .035)
             * (1 - smooth((abs(x) - .100) / .030)))
    face_scale = float(np.interp(z, [p[0] for p in face_profile], [p[1] for p in face_profile]))
    neck_scale = float(np.interp(z, [p[0] for p in neck_profile], [p[1] for p in neck_profile]))
    scale = face_scale * head + neck_scale * (1 - head)
    dx = x * (scale - 1) * scope
    for index in indices:
        neck.data[index].co = Vector(base[index]) + inverse_delta @ Vector((dx, 0, 0))
    if abs(dx) > 1e-8: neck_displacements.extend([abs(dx)] * len(indices))
assert neck_displacements and max(neck_displacements) < .055
neck.value = 1; body.update_tag(); bpy.context.view_layer.update()
assert state() == before
scene = bpy.context.scene; camera = scene.camera
scene.render.engine = 'BLENDER_EEVEE_NEXT'; scene.eevee.taa_render_samples = 1
scene.render.resolution_x = 640; scene.render.resolution_y = 640; scene.render.resolution_percentage = 100
focus = Vector((0, -.045, 1.647))
camera.data.ortho_scale = .44; camera.location = (0, -3, 1.647)
camera.rotation_euler = (focus - camera.location).to_track_quat('-Z', 'Y').to_euler()

def expression(index):
    body['PS1_face_id'] = index; body.update_tag(); bpy.context.view_layer.update()
    for slot in (1, 2):
        assert abs(mesh.materials[slot].node_tree.nodes['DERY | PS1_face_id'].outputs[0].default_value - index) < .001

def render(stage, index, name):
    expression(index)
    scene.render.filepath = str(ROOT / f'{stage}_{index:02d}_{name}.png')
    bpy.ops.render.render(write_still=True)

cases = [(0, 'Neutro'), (2, 'Risada'), (3, 'Surpresa')]
for index, name in cases: render('Antes', index, name)

group = bpy.data.node_groups.new('DERY | grade de texels faciais PSX', 'ShaderNodeTree')
group.interface.new_socket(name='UV', in_out='INPUT', socket_type='NodeSocketVector')
group.interface.new_socket(name='Resolution', in_out='INPUT', socket_type='NodeSocketFloat')
group.interface.new_socket(name='UV', in_out='OUTPUT', socket_type='NodeSocketVector')
nodes, links = group.nodes, group.links
inputs = nodes.new('NodeGroupInput'); outputs = nodes.new('NodeGroupOutput')
def math(op, a, b=0):
    node = nodes.new('ShaderNodeMath'); node.operation = op
    for socket, value in zip(node.inputs, (a, b)):
        if isinstance(value, (int, float)): socket.default_value = value
        else: links.new(value, socket)
    return node.outputs[0]
resolution = math('FLOOR', math('MINIMUM', math('MAXIMUM', inputs.outputs['Resolution'], 32), 128))
half = math('DIVIDE', .5, resolution)
last = math('SUBTRACT', 1, half)
split = nodes.new('ShaderNodeSeparateXYZ'); links.new(inputs.outputs['UV'], split.inputs[0])
combine = nodes.new('ShaderNodeCombineXYZ')
for axis in ('X', 'Y'):
    coordinate = math('DIVIDE', math('ADD', math('FLOOR', math('MULTIPLY', split.outputs[axis], resolution)), .5), resolution)
    coordinate = math('MINIMUM', math('MAXIMUM', coordinate, half), last)
    links.new(coordinate, combine.inputs[axis])
links.new(combine.outputs[0], outputs.inputs['UV'])

body['PSX_face_resolution'] = 64
body.id_properties_ui('PSX_face_resolution').update(min=32, max=128, description='64 padrão PSX; 32 pixels maiores; 128 mais detalhe. Só rosto e expressões.')
counts = {}; removed_sharpening = {}
for slot in (1, 2):
    mat = mesh.materials[slot]; nt = mat.node_tree
    ns, ls = nt.nodes, nt.links
    control = ns.new('ShaderNodeValue'); control.name = 'DERY | resolução facial PSX'
    driver = control.outputs[0].driver_add('default_value').driver
    variable = driver.variables.new(); variable.name = 'resolution'; variable.type = 'SINGLE_PROP'
    variable.targets[0].id = body; variable.targets[0].data_path = '["PSX_face_resolution"]'
    driver.expression = 'resolution'
    sockets = []
    for node in list(ns):
        if node.type == 'TEX_IMAGE' and node.image and node.image.name == 'Rosto_Neutro_128':
            node.interpolation = 'Closest'; sockets.append(node.inputs['Vector'])
        elif node.type == 'GROUP' and node.node_tree and node.node_tree.name.startswith('DERY | expressão PNG 4x3'):
            sockets.append(node.inputs['UV'])
    assert len(sockets) == 10, (mat.name, len(sockets))
    for socket in sockets:
        source_coords = socket.links[0].from_socket
        sampler = ns.new('ShaderNodeGroup'); sampler.node_tree = group
        sampler.label = 'Texel facial nítido | grade 64'
        ls.new(source_coords, sampler.inputs['UV']); ls.new(control.outputs[0], sampler.inputs['Resolution'])
        ls.new(sampler.outputs['UV'], socket)
    sharpen = ns.get('Refino | Rosto_Neutro_128')
    if sharpen:
        removed_sharpening[mat.name] = sharpen.outputs[0].default_value
        sharpen.outputs[0].default_value = 0
    counts[mat.name] = len(sockets)

assert state() == before
for index in range(11): expression(index)
neck.value = 0; body.update_tag(); bpy.context.view_layer.update()
render('Antes', 4, 'Pescoco')
neck.value = 1; body.update_tag(); bpy.context.view_layer.update()
for index, name in cases + [(4, 'Raiva')]: render('Depois', index, name)
expression(0)
camera.location = (1.55, -3, 1.68)
camera.rotation_euler = (focus - camera.location).to_track_quat('-Z', 'Y').to_euler()
scene.render.filepath = str(ROOT / 'Previa_Tres_Quartos.png'); bpy.ops.render.render(write_still=True)
camera.data.ortho_scale = .42; camera.location = (3, -.005, 1.628)
profile_focus = Vector((0, 0, 1.628)); camera.rotation_euler = (profile_focus - camera.location).to_track_quat('-Z', 'Y').to_euler()
scene.render.filepath = str(ROOT / 'Previa_Perfil.png'); bpy.ops.render.render(write_still=True)
camera.data.ortho_scale = .44; camera.location = (1.55, -3, 1.68)
camera.rotation_euler = (focus - camera.location).to_track_quat('-Z', 'Y').to_euler()
assert state() == before
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_location = focus
            area.spaces.active.region_3d.view_rotation = camera.rotation_euler.to_quaternion()
bpy.ops.file.pack_all(); bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'Dery_Rosto_PSX_64_v12.blend'))
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == source_hash
record = {'source': '../contorno_marcado_v11/' + SOURCE.name, 'source_sha256': source_hash, 'source_unchanged': True,
          'approved_profile_source_version': 'v11',
          'original_basis_shape_keys_uvs_image_pixels_weights_material_assignments_unchanged': True,
          'frontal_contour_shape_key': neck.name,
          'frontal_reference': 'Later user frontal red outline: tapered jaw/chin and neck widening toward shoulders. Manually interpreted width profiles, not calibrated pixel tracing.',
          'face_width_profile_z_scale': face_profile, 'neck_width_profile_z_scale': neck_profile,
          'frontal_maximum_vertex_displacement_m': max(neck_displacements),
          'profile_yz_preserved': True, 'frontal_contour_approved_by_user': False,
          'method': '64x64 effective local UV sampling before facial PNG/atlas lookup; Closest; no screen postprocessing.',
          'effective_face_resolution': [64, 64], 'original_png_resolution': [128, 128],
          'new_image_art_generated': False, 'images_resized_or_repainted': False,
          'facial_coordinate_inputs_quantized': counts, 'previous_sharpening_strengths': removed_sharpening,
          'facial_sharpening_disabled': True, 'atlas_cell_boundaries_preserved': True,
          'resolution_property': 'PSX_face_resolution', 'resolution_range': [32, 128],
          'expression_selector_checked_ids': list(range(11)), 'new_expressions': 0,
          'rig_bones': len(next(o for o in bpy.data.objects if o.type == 'ARMATURE').data.bones),
          'pixel_finish_approved_by_user': False}
(ROOT / 'validacao.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
print(record)
