"""Refit the existing neutral-face texture to the v7 jaw using a dedicated UV."""
from pathlib import Path
import bpy
import numpy as np
import hashlib
import math
import json
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parents[1] / 'formato_rosto_v7/Dery_Contorno_Rosto_v7.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
body = bpy.data.objects['Dery_Massacote_Rig_PS1_v2']
mesh = body.data
original_uv_names = [uv.name for uv in mesh.uv_layers]

def digest(values, dtype=np.float32):
    return hashlib.sha256(np.asarray(values, dtype=dtype).tobytes()).hexdigest()

def state():
    return {
        'basis': digest([v.co[:] for v in mesh.vertices]),
        'shape_keys': {k.name: {'value': k.value, 'coordinates': digest([p.co[:] for p in k.data])} for k in mesh.shape_keys.key_blocks},
        'uvs': {name: digest([v.uv[:] for v in mesh.uv_layers[name].data]) for name in original_uv_names},
        'images': {im.name: digest(im.pixels[:]) for im in bpy.data.images if im.type == 'IMAGE'},
        'materials': [mat.name for mat in mesh.materials],
        'material_indices': digest([p.material_index for p in mesh.polygons], np.int32),
        'weights': digest([(v.index, g.group, g.weight) for v in mesh.vertices for g in v.groups]),
    }

before = state()
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT'; scene.eevee.taa_render_samples = 1
scene.render.resolution_x = 640; scene.render.resolution_y = 640; scene.render.resolution_percentage = 100
camera = scene.camera; camera.data.ortho_scale = .44
focus = Vector((0, -.045, 1.647))
views = [('Frente', (0, -3, 1.647)), ('Tres_Quartos', (1.55, -3, 1.68))]

def render(stage):
    for view, position in views:
        camera.location = position
        camera.rotation_euler = (focus - camera.location).to_track_quat('-Z', 'Y').to_euler()
        scene.render.filepath = str(ROOT / (stage + '_' + view + '.png'))
        bpy.ops.render.render(write_still=True)

render('Antes')
active_uv = mesh.uv_layers.active.name
mesh.uv_layers.new(name='DeryFaceFitV8')
src = mesh.uv_layers['DeryPS1UV']
dst = mesh.uv_layers['DeryFaceFitV8']
# Copy all values first; only frontal face polygons receive the fit correction.
dst.data.foreach_set('uv', np.array([item.uv[:] for item in src.data], dtype=np.float32).ravel())

def gaussian(value, center, sigma):
    return math.exp(-.5 * ((value - center) / sigma) ** 2)

modified = 0
for polygon in mesh.polygons:
    if polygon.material_index not in (1, 2):
        continue
    for li in polygon.loop_indices:
        vertex = mesh.vertices[mesh.loops[li].vertex_index]
        x, y, z = body.matrix_world @ vertex.co
        if not (abs(x) < .088 and y < -.035 and 1.559 < z < 1.726):
            continue
        u, v = src.data[li].uv
        # Keep eyes at their existing horizontal spacing; fit lower features
        # to the tapered jaw and leave side/ear skin samples untouched.
        edge = min(1, max(0, (.088 - abs(x)) / .018))
        edge = edge * edge * (3 - 2 * edge)
        width = 1 - .020 * gaussian(v, .835, .055) - .045 * gaussian(v, .310, .070) - .095 * gaussian(v, .135, .065)
        vertical = -.009 * gaussian(v, .835, .045) - .003 * gaussian(v, .725, .045) + .011 * gaussian(v, .310, .065) - .032 * gaussian(v, .125, .055)
        dst.data[li].uv = (u + ((u - .5) / width - (u - .5)) * edge, v + vertical * edge)
        modified += 1

changed_nodes = []
for index in (1, 2):
    mat = mesh.materials[index]
    for node in mat.node_tree.nodes:
        if node.type == 'UVMAP' and node.uv_map == 'DeryPS1UV':
            node.uv_map = 'DeryFaceFitV8'
            changed_nodes.append((mat.name, node.name))
assert len(changed_nodes) == 2
# All five v5 samples of the face family share the modified UV origin. Native
# atlas masks, their original UVs and skin alpha branches remain unchanged.
mesh.uv_layers.active = mesh.uv_layers[active_uv]
mesh.uv_layers[active_uv].active_render = True
assert before == state()
render('Depois')
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'Dery_Encaixe_Rosto_v8.blend'))
assert before == state()
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == source_hash
record = {
    'source': '../../formato_rosto_v7/' + SOURCE.name, 'source_sha256': source_hash, 'source_unchanged': True,
    'method': 'Dedicated UV fit of the existing 128px neutral-face painting; no image repaint or pixel edit.',
    'fit_uv': 'DeryFaceFitV8', 'previous_uv': 'DeryPS1UV', 'modified_face_corners': modified,
    'changed_uv_nodes': changed_nodes, 'eyebrow_lift_uv': .009, 'mouth_drop_uv': .011,
    'mouth_width_reduction': .045, 'chin_width_reduction': .095, 'chin_clearance_uv': .032,
    'original_images_basis_shape_keys_uvs_material_assignments_weights_unchanged': True,
    'rig_bones': len(next(o for o in bpy.data.objects if o.type == 'ARMATURE').data.bones),
    'new_texture_art_generated': False, 'new_expressions': 0, 'approved_by_user': False,
    'reference': 'Visual fit guided by the previously supplied photos; no calibrated landmarks or exact-likeness claim.',
}
(ROOT / 'encaixe.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
print(record)
