"""Refine the neck silhouette and baked Gouraud lighting; retain all face PNGs."""
from pathlib import Path
import bpy
import numpy as np
import hashlib
import math
import json
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'expressoes_v1/Dery_10_Expressoes_PS1.blend'
source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
body = bpy.data.objects['Dery_Massacote_Rig_PS1_v2']; mesh = body.data
old_key_names = [key.name for key in mesh.shape_keys.key_blocks]
old_uv_names = [uv.name for uv in mesh.uv_layers]

def digest(values):
    return hashlib.sha256(np.asarray(values, dtype=np.float32).tobytes()).hexdigest()

def state():
    return {'basis': digest([v.co[:] for v in mesh.vertices]),
            'old_keys': {name: (mesh.shape_keys.key_blocks[name].value, digest([p.co[:] for p in mesh.shape_keys.key_blocks[name].data])) for name in old_key_names},
            'uvs': {name: digest([p.uv[:] for p in mesh.uv_layers[name].data]) for name in old_uv_names},
            'images': {im.name: digest(im.pixels[:]) for im in bpy.data.images if im.type == 'IMAGE'},
            'weights': digest([(v.index, g.group, g.weight) for v in mesh.vertices for g in v.groups]),
            'assignments': digest([p.material_index for p in mesh.polygons]),
            'original_lighting': digest([p.color[:] for p in mesh.color_attributes['PS1Lighting'].data])}

before = state()
key = body.shape_key_add(name='DERY | pescoço e ligação da mandíbula')
key.slider_min = 0; key.slider_max = 1
inverse = body.matrix_world.inverted()
width_profile = [(1.455, 1), (1.480, .96), (1.500, .86), (1.520, .86), (1.540, .93), (1.557, 1)]

def smooth(v):
    v = max(0, min(1, v)); return v * v * (3 - 2 * v)

def region(x, y, z):
    return (smooth((z - 1.455) / .025) * smooth((1.557 - z) / .017)
            * (1 - smooth((abs(x) - .080) / .035))
            * smooth((y + .075) / .025) * smooth((.130 - y) / .025))

changed = []; maximum_change = 0
for vertex, point in zip(mesh.vertices, key.data):
    co = body.matrix_world @ vertex.co; x, y, z = co
    w = region(x, y, z)
    if w == 0: continue
    target = co.copy()
    scale = float(np.interp(z, [v[0] for v in width_profile], [v[1] for v in width_profile]))
    target.x *= 1 + (scale - 1) * w
    target.y = .025 + (y - .025) * (1 - .045 * w)
    point.co = inverse @ target
    if (point.co - vertex.co).length > 1e-9:
        changed.append(vertex.index)
        maximum_change = max(maximum_change, (target - co).length)

assert changed and maximum_change < .015
# New per-corner attribute leaves the original lighting untouched. Vertices at
# the same rest coordinates receive identical correction, including UV seams.
mesh.color_attributes.new(name='DeryNeckLightingV9', type='FLOAT_COLOR', domain='CORNER')
old_light = mesh.color_attributes['PS1Lighting']
new_light = mesh.color_attributes['DeryNeckLightingV9']
changed_lighting = 0
for loop in mesh.loops:
    vi = loop.vertex_index
    co = body.matrix_world @ mesh.vertices[vi].co; x, y, z = co
    old = tuple(old_light.data[loop.index].color)
    w = (smooth((z - 1.486) / .021) * smooth((1.578 - z) / .020)
         * (1 - smooth((abs(x) - .076) / .030))
         * smooth((y + .085) / .030) * smooth((.135 - y) / .030))
    if w > 0:
        radial = Vector((x / .066, (y - .025) / .061, .14)).normalized()
        brightness = .84 + .15 * max(0, radial.dot(Vector((-.35, -.8, .35)).normalized()))
        front = 1 - smooth((y - .012) / .070)
        shadow = .19 * math.exp(-.5 * ((z - 1.547) / .016) ** 2) * front
        level = brightness * (1 - shadow)
        value = [old[i] * (1 - w) + level * w for i in range(3)]
        new_light.data[loop.index].color = (*value, old[3])
        changed_lighting += 1
    else:
        new_light.data[loop.index].color = old

mat = mesh.materials[3]
nt = mat.node_tree; nodes, links = nt.nodes, nt.links
lighting = next(node for node in nodes if node.type == 'MIX_RGB' and node.blend_type == 'MULTIPLY')
original = lighting.inputs[2].links[0].from_socket
attr = nodes.new('ShaderNodeAttribute'); attr.attribute_name = 'DeryNeckLightingV9'
blend = nodes.new('ShaderNodeMixRGB'); blend.name = 'DERY | iluminação do pescoço v9'
links.new(original, blend.inputs[1]); links.new(attr.outputs['Color'], blend.inputs[2])
driver = blend.inputs[0].driver_add('default_value').driver
variable = driver.variables.new(); variable.name = 'neck'; variable.type = 'SINGLE_PROP'
variable.targets[0].id_type = 'KEY'; variable.targets[0].id = mesh.shape_keys
variable.targets[0].data_path = 'key_blocks[' + json.dumps(key.name, ensure_ascii=False) + '].value'
driver.expression = 'neck'
links.new(blend.outputs[0], lighting.inputs[2])

# The original lateral/neck fit used only a few image columns and less than
# one image row across the neck, producing large flat vertical color bands.
# A separate UV samples a larger unmarked cheek patch of the SAME neutral PNG.
active_uv = mesh.uv_layers.active.name
mesh.uv_layers.new(name='DeryNeckUVV9')
old_uv = mesh.uv_layers['DeryPS1UV']; neck_uv = mesh.uv_layers['DeryNeckUVV9']
neck_uv.data.foreach_set('uv', np.array([p.uv[:] for p in old_uv.data], dtype=np.float32).ravel())
for polygon in mesh.polygons:
    if polygon.material_index != 3: continue
    for li in polygon.loop_indices:
        co = body.matrix_world @ mesh.vertices[mesh.loops[li].vertex_index].co
        x, y, z = co
        w = (smooth((z - 1.490) / .012) * smooth((1.585 - z) / .020)
             * (1 - smooth((abs(x) - .080) / .030))
             * smooth((y + .085) / .030) * smooth((.135 - y) / .030))
        if w == 0: continue
        u, v = old_uv.data[li].uv
        patch_u = .025 + max(0, min(1, x / .16 + .5)) * .12
        patch_v = .36 + max(0, min(1, (z - 1.49) / .085)) * .28
        neck_uv.data[li].uv = (u + (patch_u - u) * w, v + (patch_v - v) * w)
mesh.uv_layers.active = mesh.uv_layers[active_uv]; mesh.uv_layers[active_uv].active_render = True
coords = next(node for node in nodes if node.type == 'UVMAP' and node.uv_map == 'DeryPS1UV').outputs['UV']
consumers = [link.to_socket for link in coords.links]
new_coords = nodes.new('ShaderNodeUVMap'); new_coords.uv_map = 'DeryNeckUVV9'
delta = nodes.new('ShaderNodeVectorMath'); delta.operation = 'SUBTRACT'
links.new(new_coords.outputs['UV'], delta.inputs[0]); links.new(coords, delta.inputs[1])
uv_control = nodes.new('ShaderNodeValue'); uv_control.name = 'DERY | força do encaixe do pescoço'
uv_driver = uv_control.outputs[0].driver_add('default_value').driver
uv_variable = uv_driver.variables.new(); uv_variable.name = 'neck'; uv_variable.type = 'SINGLE_PROP'
uv_variable.targets[0].id_type = 'KEY'; uv_variable.targets[0].id = mesh.shape_keys
uv_variable.targets[0].data_path = variable.targets[0].data_path; uv_driver.expression = 'neck'
scale_uv = nodes.new('ShaderNodeVectorMath'); scale_uv.operation = 'SCALE'
links.new(delta.outputs[0], scale_uv.inputs[0]); links.new(uv_control.outputs[0], scale_uv.inputs['Scale'])
mixed_uv = nodes.new('ShaderNodeVectorMath'); mixed_uv.operation = 'ADD'
links.new(coords, mixed_uv.inputs[0]); links.new(scale_uv.outputs[0], mixed_uv.inputs[1])
for socket in consumers: links.new(mixed_uv.outputs[0], socket)

# Keep the existing skin grain at low contrast. The old source patch has
# strong 5-bit color jumps; its average supplies the base skin tone instead
# of magnifying those jumps into bands around the entire neck.
mesh.attributes.new(name='DeryNeckSkinV9', type='FLOAT', domain='CORNER')
skin_field = mesh.attributes['DeryNeckSkinV9']
for loop in mesh.loops:
    x, y, z = body.matrix_world @ mesh.vertices[loop.vertex_index].co
    skin_field.data[loop.index].value = (smooth((z - 1.490) / .012) * smooth((1.585 - z) / .020)
        * (1 - smooth((abs(x) - .080) / .030)) * smooth((y + .085) / .030) * smooth((.135 - y) / .030))
face_image = bpy.data.images['Rosto_Neutro_128']
average = None
for u, v in [(.06, .41), (.11, .41), (.06, .53), (.11, .53)]:
    sample = nodes.new('ShaderNodeTexImage'); sample.image = face_image; sample.interpolation = 'Closest'
    sample.inputs['Vector'].default_value = (u, v, 0); sample['DerySkinOnly'] = True
    if average is None: average = sample.outputs['Color']
    else:
        add = nodes.new('ShaderNodeVectorMath'); add.operation = 'ADD'
        links.new(average, add.inputs[0]); links.new(sample.outputs['Color'], add.inputs[1]); average = add.outputs[0]
average_node = nodes.new('ShaderNodeVectorMath'); average_node.operation = 'SCALE'; average_node.inputs['Scale'].default_value = .25
links.new(average, average_node.inputs[0])
original_paint = lighting.inputs[1].links[0].from_socket
grain = nodes.new('ShaderNodeMixRGB'); grain.inputs[0].default_value = .18; grain.label = 'Grão de pele discreto | mesmo PNG'
links.new(average_node.outputs[0], grain.inputs[1]); links.new(original_paint, grain.inputs[2])
skin_mask = nodes.new('ShaderNodeAttribute'); skin_mask.attribute_name = 'DeryNeckSkinV9'
strength = nodes.new('ShaderNodeMath'); strength.operation = 'MULTIPLY'
links.new(skin_mask.outputs['Fac'], strength.inputs[0]); links.new(uv_control.outputs[0], strength.inputs[1])
# Reuse the original per-pixel skin classifier and an exact rest-height gate.
# Interpolated corner masks alone can otherwise spill skin across collar tris.
classifier = next(node for node in nodes if node.type == 'MATH' and node.operation == 'MAXIMUM')
skin_gate = nodes.new('ShaderNodeMath'); skin_gate.operation = 'MULTIPLY'
links.new(strength.outputs[0], skin_gate.inputs[0]); links.new(classifier.outputs[0], skin_gate.inputs[1])
rest_coords = nodes.new('ShaderNodeAttribute'); rest_coords.attribute_name = 'DeryRest'
rest_split = nodes.new('ShaderNodeSeparateXYZ'); links.new(rest_coords.outputs['Vector'], rest_split.inputs[0])
height_gate = nodes.new('ShaderNodeMapRange'); height_gate.clamp = True
height_gate.inputs['From Min'].default_value = 1.500; height_gate.inputs['From Max'].default_value = 1.512
links.new(rest_split.outputs['Z'], height_gate.inputs['Value'])
safe_strength = nodes.new('ShaderNodeMath'); safe_strength.operation = 'MULTIPLY'
links.new(skin_gate.outputs[0], safe_strength.inputs[0]); links.new(height_gate.outputs['Result'], safe_strength.inputs[1])
skin_mix = nodes.new('ShaderNodeMixRGB'); skin_mix.name = 'DERY | transição da pele do pescoço'
links.new(safe_strength.outputs[0], skin_mix.inputs[0]); links.new(original_paint, skin_mix.inputs[1]); links.new(grain.outputs[0], skin_mix.inputs[2])
links.new(skin_mix.outputs[0], lighting.inputs[1])
assert state() == before

scene = bpy.context.scene; camera = scene.camera
scene.render.engine = 'BLENDER_EEVEE_NEXT'; scene.eevee.taa_render_samples = 1
scene.render.resolution_x = 640; scene.render.resolution_y = 640; scene.render.resolution_percentage = 100
camera.data.ortho_scale = .49
focus = Vector((0, .005, 1.615))
views = [('Frente', (0, -3, 1.615)), ('Tres_Quartos', (1.55, -3, 1.65)), ('Perfil', (3, -.005, 1.615))]
for stage, value in [('Antes', 0), ('Depois', 1)]:
    key.value = value; body.update_tag(); bpy.context.view_layer.update()
    assert abs(blend.inputs[0].default_value - value) < .001
    for view, position in views:
        camera.location = position
        camera.rotation_euler = (focus - camera.location).to_track_quat('-Z', 'Y').to_euler()
        scene.render.filepath = str(ROOT / (stage + '_' + view + '.png'))
        bpy.ops.render.render(write_still=True)

# Reuse all eleven IDs and verify drivers still select the same atlas cells.
for index in range(11):
    body['PS1_face_id'] = index; body.update_tag(); bpy.context.view_layer.update()
    for slot in (1, 2):
        assert abs(mesh.materials[slot].node_tree.nodes['DERY | PS1_face_id'].outputs[0].default_value - index) < .001
body['PS1_face_id'] = 2; body.update_tag(); bpy.context.view_layer.update()
camera.location = views[1][1]
camera.rotation_euler = (focus - camera.location).to_track_quat('-Z', 'Y').to_euler()
scene.render.filepath = str(ROOT / 'Depois_Risada.png'); bpy.ops.render.render(write_still=True)
body['PS1_face_id'] = 0; body.update_tag(); bpy.context.view_layer.update()
key.value = 1
assert state() == before

# Check one turning pose without changing the retained rig/action.
armature = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
bone = armature.pose.bones['CC_Base_Head']; original_basis = bone.matrix_basis.copy()
from mathutils import Matrix
bone.matrix_basis = original_basis @ Matrix.Rotation(math.radians(25), 4, 'Y')
bpy.context.view_layer.update()
evaluated = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
temporary_mesh = evaluated.to_mesh()
assert np.isfinite(np.asarray([v.co[:] for v in temporary_mesh.vertices])).all()
evaluated.to_mesh_clear()
bone.matrix_basis = original_basis; bpy.context.view_layer.update()

camera.location = views[0][1]
camera.rotation_euler = (focus - camera.location).to_track_quat('-Z', 'Y').to_euler()
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_location = focus
            area.spaces.active.region_3d.view_rotation = camera.rotation_euler.to_quaternion()
bpy.ops.file.pack_all(); bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'Dery_Pescoco_Ajustado_v9.blend'))
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == source_hash
record = {'source': '../expressoes_v1/' + SOURCE.name, 'source_sha256': source_hash, 'source_unchanged': True,
          'method': 'Reversible neck contour shape key with linked baked Gouraud neck lighting.', 'shape_key': key.name,
          'changed_vertices': len(changed), 'maximum_vertex_displacement_m': maximum_change,
          'width_profile_z_scale': width_profile, 'modified_neck_lighting_corners': changed_lighting,
          'neck_uv': 'DeryNeckUVV9', 'neck_texture': 'Clear skin patch in the same original neutral face PNG; no new image art.',
          'neck_skin_grain_contrast': .18, 'skin_tone_average': 'Four unmarked cheek texels from the same neutral face PNG.',
          'neck_shader_skin_classifier_and_collar_height_gate': True,
          'basis_existing_shape_keys_uvs_images_weights_assignments_original_lighting_unchanged': True,
          'face_contour_and_expression_art_unchanged': True, 'expression_selector_checked_ids': list(range(11)),
          'turning_pose_degrees': 25, 'turning_pose_finite': True, 'rig_bones': len(armature.data.bones),
          'neck_height_changed': False, 'new_expressions': 0, 'approved_by_user': False}
(ROOT / 'ajuste.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
print(record)
