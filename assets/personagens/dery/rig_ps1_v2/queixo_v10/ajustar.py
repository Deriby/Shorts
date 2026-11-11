"""Round the protruding chin base while retaining the neck and expression setup."""
from pathlib import Path
import bpy
import numpy as np
import hashlib
import math
import json
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'pescoco_v9/Dery_Pescoco_Ajustado_v9.blend'
source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
body = bpy.data.objects['Dery_Massacote_Rig_PS1_v2']; mesh = body.data
old_keys = list(mesh.shape_keys.key_blocks)
old_names = [key.name for key in old_keys]
base = np.asarray([v.co[:] for v in mesh.vertices], dtype=np.float64)
current = base.copy()
for old in old_keys[1:]:
    current += (np.asarray([p.co[:] for p in old.data]) - base) * old.value
jaw = np.asarray([p.co[:] for p in mesh.shape_keys.key_blocks['DERY | contorno de mandíbula e queixo'].data])
matrix = body.matrix_world.copy(); inv_delta = matrix.inverted().to_3x3()

def digest(values):
    return hashlib.sha256(np.asarray(values, dtype=np.float32).tobytes()).hexdigest()

def state():
    return {'basis': digest([v.co[:] for v in mesh.vertices]),
            'old_keys': {name: (mesh.shape_keys.key_blocks[name].value, digest([p.co[:] for p in mesh.shape_keys.key_blocks[name].data])) for name in old_names},
            'uvs': {uv.name: digest([p.uv[:] for p in uv.data]) for uv in mesh.uv_layers},
            'images': {im.name: digest(im.pixels[:]) for im in bpy.data.images if im.type == 'IMAGE'},
            'weights': digest([(v.index, g.group, g.weight) for v in mesh.vertices for g in v.groups]),
            'assignments': digest([p.material_index for p in mesh.polygons])}

before = state()
key = body.shape_key_add(name='DERY | base do queixo arredondada')
key.slider_min = 0; key.slider_max = 1
def smooth(value):
    value = max(0, min(1, value)); return value * value * (3 - 2 * value)

world = np.asarray([(matrix @ Vector(co))[:] for co in current])
targets = world.copy()
for index, co_array in enumerate(world):
    co = Vector(co_array); x, y, z = co
    scope = (smooth((z - 1.533) / .014) * smooth((1.597 - z) / .016)
             * (1 - smooth((abs(x) - .052) / .032)) * smooth((-.030 - y) / .025))
    if scope == 0: continue
    target = co.copy()
    jaw_delta = matrix.to_3x3() @ Vector(jaw[index] - base[index])
    # Undo the earlier downward extension at the chin, preserving jaw width.
    target.z -= jaw_delta.z * scope
    target.y += .006 * math.exp(-.5 * ((z - 1.561) / .016) ** 2) * scope
    widen = .040 * math.exp(-.5 * ((z - 1.568) / .017) ** 2)
    target.x *= 1 + widen * scope
    targets[index] = target[:]

# Relax the irregular lower edge on a welded adjacency graph. Coincident UV
# seam vertices share a displacement, so smoothing cannot open new cracks.
groups = {}; members = []; vertex_group = []
for index, co in enumerate(world):
    token = tuple(np.round(co, 6))
    if token not in groups:
        groups[token] = len(members); members.append([])
    group = groups[token]; members[group].append(index); vertex_group.append(group)
neighbors = [set() for group in members]
for edge in mesh.edges:
    a, b = (vertex_group[v] for v in edge.vertices)
    if a != b: neighbors[a].add(b); neighbors[b].add(a)
centers = np.asarray([targets[group].mean(axis=0) for group in members])
weights = []
for x, y, z in [world[group].mean(axis=0) for group in members]:
    weights.append(smooth((z - 1.533) / .013) * smooth((1.593 - z) / .015)
                   * (1 - smooth((abs(x) - .048) / .035)) * smooth((-.035 - y) / .025))
selected = [index for index, weight in enumerate(weights) if weight > 0 and neighbors[index]]
adjacency = {index: np.asarray(sorted(neighbors[index])) for index in selected}
starts = centers.copy()
for iteration in range(6):
    for amount in (.45, -.25):
        previous = centers.copy()
        for index in selected:
            other = adjacency[index]
            average = previous[other].mean(axis=0)
            centers[index] += amount * weights[index] * (average - previous[index])
for group, indices in enumerate(members):
    targets[indices] += centers[group] - starts[group]

# Round the bottom/front corner against a soft ellipsoidal envelope. Blend
# toward it rather than collapsing layers onto a single surface. The front
# of the mouth and the neck shaft are outside this correction field.
chin_center = np.array((0, -.079, 1.582))
chin_radii = np.array((.070, .032, .026))
for index, (x, y, z) in enumerate(world):
    w = (smooth((z - 1.535) / .015) * smooth((1.591 - z) / .014)
         * (1 - smooth((abs(x) - .045) / .030)) * smooth((-.055 - y) / .023))
    if w == 0: continue
    radial = targets[index] - chin_center
    length = np.linalg.norm(radial / chin_radii)
    if length > 1:
        rounded = chin_center + radial / length
        targets[index] += (rounded - targets[index]) * (.85 * w)

changed = []; maximum_change = 0
for index, point in enumerate(key.data):
    delta = Vector(targets[index] - world[index])
    point.co = Vector(base[index]) + inv_delta @ delta
    if delta.length > 1e-8:
        changed.append(index); maximum_change = max(maximum_change, delta.length)

assert changed and maximum_change < .025
assert state() == before
scene = bpy.context.scene; camera = scene.camera
scene.render.engine = 'BLENDER_EEVEE_NEXT'; scene.eevee.taa_render_samples = 1
scene.render.resolution_x = 640; scene.render.resolution_y = 640; scene.render.resolution_percentage = 100
views = [('Detalhe', .205, (0, -.035, 1.582), (1.55, -3, 1.62)),
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
focus = Vector((0, -.045, 1.647))
camera.rotation_euler = (focus - camera.location).to_track_quat('-Z', 'Y').to_euler()
scene.render.filepath = str(ROOT / 'Depois_Rosto.png'); bpy.ops.render.render(write_still=True)
for expression in range(11):
    body['PS1_face_id'] = expression; body.update_tag(); bpy.context.view_layer.update()
    for slot in (1, 2):
        assert abs(mesh.materials[slot].node_tree.nodes['DERY | PS1_face_id'].outputs[0].default_value - expression) < .001
body['PS1_face_id'] = 2; body.update_tag(); bpy.context.view_layer.update()
scene.render.filepath = str(ROOT / 'Depois_Risada.png'); bpy.ops.render.render(write_still=True)
body['PS1_face_id'] = 0; body.update_tag(); bpy.context.view_layer.update()
assert state() == before
evaluated = body.evaluated_get(bpy.context.evaluated_depsgraph_get()); temporary = evaluated.to_mesh()
assert np.isfinite(np.asarray([v.co[:] for v in temporary.vertices])).all()
evaluated.to_mesh_clear()
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_location = focus
            area.spaces.active.region_3d.view_rotation = camera.rotation_euler.to_quaternion()
bpy.ops.file.pack_all(); bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'Dery_Queixo_Ajustado_v10.blend'))
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == source_hash
record = {'source': '../pescoco_v9/' + SOURCE.name, 'source_sha256': source_hash, 'source_unchanged': True,
          'scope': 'Round and retract the chin base, cancel the earlier downward chin extension, and soften the jaw-to-neck silhouette.',
          'shape_key': key.name, 'changed_vertices': len(changed), 'maximum_vertex_displacement_m': maximum_change,
          'chin_tip_retraction_m': .006, 'welded_edge_relaxation_passes': 6,
          'rounded_envelope_center_m': chin_center.tolist(), 'rounded_envelope_radii_m': chin_radii.tolist(),
          'original_basis_shape_keys_uvs_images_weights_assignments_unchanged': True,
          'material_changes': False, 'new_texture_art': False, 'new_expressions': 0,
          'expression_selector_checked_ids': list(range(11)), 'rig_bones': len(next(o for o in bpy.data.objects if o.type == 'ARMATURE').data.bones),
          'evaluated_geometry_finite': True, 'approved_by_user': False}
(ROOT / 'ajuste.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
print(record)
