"""Reversible jaw/chin silhouette adjustment, retaining the current texture fit."""
from pathlib import Path
import bpy
import numpy as np
import json
import hashlib
import math
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'texturas/camiseta_m_v6/Dery_Camiseta_M_v6.blend'
source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
body = bpy.data.objects['Dery_Massacote_Rig_PS1_v2']
mesh = body.data

def digest(values, dtype=np.float32):
    return hashlib.sha256(np.array(values, dtype=dtype).tobytes()).hexdigest()

def preserved_state():
    return {
        'basis_vertices': digest([v.co[:] for v in mesh.vertices]),
        'uvs': {uv.name: digest([v.uv[:] for v in uv.data]) for uv in mesh.uv_layers},
        'images': {i.name: digest(i.pixels[:]) for i in bpy.data.images if i.type == 'IMAGE'},
        'materials': [m.name for m in mesh.materials],
        'indices': digest([p.material_index for p in mesh.polygons], np.int32),
        'weights': digest([(v.index, g.group, g.weight) for v in mesh.vertices for g in v.groups]),
        'bone_count': len(next(o for o in bpy.data.objects if o.type == 'ARMATURE').data.bones),
    }

before = preserved_state()
body.shape_key_add(name='Basis') if mesh.shape_keys is None else None
key = body.shape_key_add(name='DERY | contorno de mandíbula e queixo')
key.slider_min = 0; key.slider_max = 1
head_index = body.vertex_groups['CC_Base_Head'].index
inverse = body.matrix_world.inverted()
profile = [(1.535, 1), (1.554, .90), (1.575, .84), (1.596, .87),
           (1.620, .92), (1.640, .97), (1.665, .995), (1.698, 1)]

def smooth(v):
    v = min(1, max(0, v))
    return v * v * (3 - 2 * v)

def width(z):
    return float(np.interp(z, [p[0] for p in profile], [p[1] for p in profile]))

changed = []
maximum_change = 0
for vertex, point in zip(mesh.vertices, key.data):
    co = body.matrix_world @ vertex.co
    x, y, z = co
    head_weight = sum(g.weight for g in vertex.groups if g.group == head_index)
    if not (1.535 < z < 1.698 and abs(x) < .12 and head_weight > .15):
        continue
    # Protect the ears, upper face, cap and back of the head.
    if abs(x) > .086 and z > 1.606:
        continue
    influence = smooth((z - 1.535) / .025) * smooth((1.698 - z) / .022) * smooth((.072 - y) / .045)
    if influence == 0:
        continue
    target = co.copy()
    target.x *= 1 + (width(z) - 1) * influence
    lower_face = math.exp(-((z - 1.564) / .024) ** 2)
    target.z += (-.005 * math.exp(-(x / .038) ** 2) + .002 * min(1, abs(x) / .08)) * lower_face * influence
    point.co = inverse @ target
    changed.append(vertex.index)
    maximum_change = max(maximum_change, (target - co).length)

assert changed and maximum_change < .02
assert preserved_state() == before
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT'; scene.eevee.taa_render_samples = 1
scene.render.resolution_x = 640; scene.render.resolution_y = 640; scene.render.resolution_percentage = 100
camera = scene.camera; camera.data.ortho_scale = .44
focus = Vector((0, -.045, 1.647))
views = [('Frente', (0, -3, 1.647)), ('Tres_Quartos', (1.55, -3, 1.68))]
for stage, value in [('Antes', 0), ('Depois', 1)]:
    key.value = value
    for view, position in views:
        camera.location = position
        camera.rotation_euler = (focus - camera.location).to_track_quat('-Z', 'Y').to_euler()
        scene.render.filepath = str(ROOT / (stage + '_' + view + '.png'))
        bpy.ops.render.render(write_still=True)

key.value = 1
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'Dery_Contorno_Rosto_v7.blend'))
assert preserved_state() == before
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == source_hash
record = {'source': '../texturas/camiseta_m_v6/' + SOURCE.name, 'source_sha256': source_hash,
          'source_unchanged': True, 'visual_reference': 'Previously supplied selfies in the conversation; visual interpretation, no calibrated scan or automatic landmarks.',
          'scope': 'Lower-face silhouette: taper jaw below cheekbones and soften the flat chin base, without redrawing the texture.',
          'method': 'Reversible shape key; value 0 restores the prior silhouette.', 'shape_key': key.name,
          'changed_vertices': len(changed), 'maximum_vertex_displacement_m': maximum_change,
          'basis_vertices_uvs_images_materials_weights_preserved': True, 'rig_bones': before['bone_count'],
          'nose_eye_brow_mouth_texture_design_preserved': True, 'new_expressions': 0, 'approved_by_user': False,
          'width_profile_z_scale': profile}
(ROOT / 'ajuste.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
print(record)
