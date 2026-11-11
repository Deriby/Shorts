"""Fit the lower jaw to the user's marked straight underside and neck corner."""
from pathlib import Path
import bpy
import numpy as np
import json
import hashlib
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'queixo_v10/Dery_Queixo_Ajustado_v10.blend'
source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
body = bpy.data.objects['Dery_Massacote_Rig_PS1_v2']; mesh = body.data
old_names = [key.name for key in mesh.shape_keys.key_blocks]
old_uv_names = [uv.name for uv in mesh.uv_layers]
base = np.asarray([v.co[:] for v in mesh.vertices], dtype=np.float64)
current = base.copy()
for old in mesh.shape_keys.key_blocks[1:]:
    current += (np.asarray([p.co[:] for p in old.data]) - base) * old.value
matrix = body.matrix_world.copy(); inverse_delta = matrix.inverted().to_3x3()
world = np.asarray([(matrix @ Vector(co))[:] for co in current])
triangles = np.asarray([p.vertices[:] for p in mesh.polygons], dtype=np.int32)
assert triangles.shape[1] == 3

def digest(values):
    return hashlib.sha256(np.asarray(values, dtype=np.float32).tobytes()).hexdigest()

def state():
    return {'basis': digest([v.co[:] for v in mesh.vertices]),
            'old_keys': {name: (mesh.shape_keys.key_blocks[name].value, digest([p.co[:] for p in mesh.shape_keys.key_blocks[name].data])) for name in old_names},
            'uvs': {name: digest([p.uv[:] for p in mesh.uv_layers[name].data]) for name in old_uv_names},
            'images': {im.name: digest(im.pixels[:]) for im in bpy.data.images if im.type == 'IMAGE'},
            'weights': digest([(v.index, g.group, g.weight) for v in mesh.vertices for g in v.groups]),
            'assignments': digest([p.material_index for p in mesh.polygons])}

before = state()
key = body.shape_key_add(name='DERY | mandíbula conforme marcação vermelha')
key.slider_min = 0; key.slider_max = 1

# Interpretation of the marked profile in the same orthographic inspection
# camera: nearly horizontal chin-to-throat underside, followed by a neck edge.
# These are manually fitted guide points, not a calibrated scan of the image.
guide_front = np.array((0, -.105, 1.554))
guide_throat = np.array((0, -.043, 1.557))
slope = (guide_throat[2] - guide_front[2]) / (guide_throat[1] - guide_front[1])
normals = np.cross(world[triangles[:, 1]] - world[triangles[:, 0]], world[triangles[:, 2]] - world[triangles[:, 0]])
areas = np.linalg.norm(normals, axis=1)
unit_z = normals[:, 2] / np.maximum(areas, 1e-15)
centers = world[triangles].mean(axis=1)
underside = ((np.abs(centers[:, 0]) < .090) & (centers[:, 1] > -.130) & (centers[:, 1] < -.030)
             & (centers[:, 2] > 1.535) & (centers[:, 2] < 1.579) & (unit_z < -.24))
selected = set(int(i) for i in triangles[underside].ravel())
selected = {i for i in selected if abs(world[i, 0]) < .095 and -.135 < world[i, 1] < -.026 and 1.530 < world[i, 2] < 1.584}
assert len(selected) > 20

# Use coincident-position groups so UV seams cannot separate under the fit.
groups = {}
for i, point in enumerate(world):
    groups.setdefault(tuple(np.round(point, 6)), []).append(i)
selected_groups = [indices for indices in groups.values() if any(i in selected for i in indices)]
target = world.copy()
for indices in selected_groups:
    center = world[indices].mean(axis=0)
    fitted_y = center[1] if center[1] <= -.060 else -.060 + (center[1] + .060) * .425
    target[indices, 1] += fitted_y - center[1]
    plane_z = guide_front[2] + slope * (fitted_y - guide_front[1])
    # Leave a tiny residual separation for near-vertical adjacent polygons;
    # the silhouette still follows the marked planar underside within 0.5mm.
    dz = (plane_z - center[2]) * .985
    target[indices, 2] += dz

# Blend only the directly adjacent row toward the same correction, keeping
# mouth, upper cheek, neck shaft and collar fixed.
offset = target - world
adjacent = [set() for i in mesh.vertices]
for edge in mesh.edges:
    a, b = edge.vertices; adjacent[a].add(b); adjacent[b].add(a)
fixed = {i for group in selected_groups for i in group}
for indices in groups.values():
    if any(i in fixed for i in indices): continue
    x, y, z = world[indices].mean(axis=0)
    if not (abs(x) < .095 and -.135 < y < -.026 and 1.538 < z < 1.589): continue
    touches = set().union(*(adjacent[i] & fixed for i in indices))
    if not touches: continue
    blend_delta = np.mean([offset[i] for i in touches], axis=0) * .28
    target[indices] += blend_delta

displacement = np.linalg.norm(target - world, axis=1)
changed = np.flatnonzero(displacement > 1e-8)
assert 0 < displacement.max() < .04
for i, point in enumerate(key.data):
    point.co = Vector(base[i]) + inverse_delta @ Vector(target[i] - world[i])

after_normals = np.cross(target[triangles[:, 1]] - target[triangles[:, 0]], target[triangles[:, 2]] - target[triangles[:, 0]])
after_areas = np.linalg.norm(after_normals, axis=1)
new_degenerate = int(np.sum((areas > 1e-10) & (after_areas < 1e-12)))
assert new_degenerate == 0
assert state() == before

# Refit the lower-face UV after changing vertex heights, so the original
# mouth/goatee landmarks stay at their current heights rather than streaking.
active_uv = mesh.uv_layers.active.name
mesh.uv_layers.new(name='DeryJawUVV11')
uv_source = mesh.uv_layers['DeryFaceFitV8']; uv_fit = mesh.uv_layers['DeryJawUVV11']
uv_fit.data.foreach_set('uv', np.asarray([p.uv[:] for p in uv_source.data], dtype=np.float32).ravel())
for polygon in mesh.polygons:
    if polygon.material_index not in (1, 2): continue
    for li in polygon.loop_indices:
        vi = mesh.loops[li].vertex_index
        u, v = uv_source.data[li].uv
        uv_fit.data[li].uv = (u, v + (target[vi, 2] - world[vi, 2]) / .190)
mesh.uv_layers.active = mesh.uv_layers[active_uv]; mesh.uv_layers[active_uv].active_render = True
for slot in (1, 2):
    nt = mesh.materials[slot].node_tree; nodes, links = nt.nodes, nt.links
    original_uv = next(node for node in nodes if node.type == 'UVMAP' and node.uv_map == 'DeryFaceFitV8').outputs['UV']
    consumers = [link.to_socket for link in original_uv.links]
    corrected_uv = nodes.new('ShaderNodeUVMap'); corrected_uv.uv_map = 'DeryJawUVV11'
    difference = nodes.new('ShaderNodeVectorMath'); difference.operation = 'SUBTRACT'
    links.new(corrected_uv.outputs['UV'], difference.inputs[0]); links.new(original_uv, difference.inputs[1])
    control = nodes.new('ShaderNodeValue'); control.name = 'DERY | encaixe da mandíbula marcada'
    driver = control.outputs[0].driver_add('default_value').driver
    variable = driver.variables.new(); variable.name = 'fit'; variable.type = 'SINGLE_PROP'
    variable.targets[0].id_type = 'KEY'; variable.targets[0].id = mesh.shape_keys
    variable.targets[0].data_path = 'key_blocks[' + json.dumps(key.name, ensure_ascii=False) + '].value'
    driver.expression = 'fit'
    scale_uv = nodes.new('ShaderNodeVectorMath'); scale_uv.operation = 'SCALE'
    links.new(difference.outputs[0], scale_uv.inputs[0]); links.new(control.outputs[0], scale_uv.inputs['Scale'])
    add_uv = nodes.new('ShaderNodeVectorMath'); add_uv.operation = 'ADD'
    links.new(original_uv, add_uv.inputs[0]); links.new(scale_uv.outputs[0], add_uv.inputs[1])
    for socket in consumers: links.new(add_uv.outputs[0], socket)
assert state() == before

scene = bpy.context.scene; camera = scene.camera
scene.render.engine = 'BLENDER_EEVEE_NEXT'; scene.eevee.taa_render_samples = 1
scene.render.resolution_x = 640; scene.render.resolution_y = 640; scene.render.resolution_percentage = 100
views = [('Tres_Quartos', .205, (0, -.035, 1.582), (1.55, -3, 1.62)),
         ('Perfil', .42, (0, 0, 1.628), (3, -.005, 1.628))]
for stage, value in [('Antes', 0), ('Depois', 1)]:
    key.value = value; body.update_tag(); bpy.context.view_layer.update()
    for name, scale, focus, position in views:
        camera.data.ortho_scale = scale; camera.location = position
        camera.rotation_euler = (Vector(focus) - camera.location).to_track_quat('-Z', 'Y').to_euler()
        scene.render.filepath = str(ROOT / (stage + '_' + name + '.png'))
        bpy.ops.render.render(write_still=True)

key.value = 1
camera.data.ortho_scale = .44; camera.location = (1.55, -3, 1.68)
focus = Vector((0, -.045, 1.647)); camera.rotation_euler = (focus - camera.location).to_track_quat('-Z', 'Y').to_euler()
scene.render.filepath = str(ROOT / 'Depois_Rosto.png'); bpy.ops.render.render(write_still=True)
for expression in range(11):
    body['PS1_face_id'] = expression; body.update_tag(); bpy.context.view_layer.update()
    for slot in (1, 2):
        assert abs(mesh.materials[slot].node_tree.nodes['DERY | PS1_face_id'].outputs[0].default_value - expression) < .001
body['PS1_face_id'] = 2; body.update_tag(); bpy.context.view_layer.update()
scene.render.filepath = str(ROOT / 'Depois_Risada.png'); bpy.ops.render.render(write_still=True)
body['PS1_face_id'] = 0; body.update_tag(); bpy.context.view_layer.update()
assert state() == before
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_location = focus
            area.spaces.active.region_3d.view_rotation = camera.rotation_euler.to_quaternion()
bpy.ops.file.pack_all(); bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'Dery_Contorno_Marcado_v11.blend'))
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == source_hash
residual = [abs(target[i, 2] - (guide_front[2] + slope * (target[i, 1] - guide_front[1]))) for group in selected_groups for i in group]
record = {'source': '../queixo_v10/' + SOURCE.name, 'source_sha256': source_hash, 'source_unchanged': True,
          'reference': 'User red-marked 3/4 and profile screenshot; manually interpreted guide points in the same cameras.',
          'scope': 'Straighter lower-jaw base and defined throat corner according to the red outline, retaining the existing face textures.',
          'shape_key': key.name, 'changed_vertices': int(len(changed)), 'underside_triangles': int(underside.sum()),
          'maximum_vertex_displacement_m': float(displacement.max()), 'guide_front_m': guide_front.tolist(), 'guide_throat_m': guide_throat.tolist(),
          'maximum_fitted_plane_residual_m': float(max(residual)), 'new_degenerate_triangles': new_degenerate,
          'original_basis_shape_keys_uvs_images_weights_assignments_preserved': True,
          'material_changes': 'UV routing only; original image pixels and material assignments preserved.',
          'lower_face_fit_uv': 'DeryJawUVV11', 'throat_depth_compression': .425,
          'new_texture_art': False, 'new_expressions': 0, 'expression_selector_checked_ids': list(range(11)),
          'rig_bones': len(next(o for o in bpy.data.objects if o.type == 'ARMATURE').data.bones), 'approved_by_user': False}
(ROOT / 'ajuste.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
print(record)
