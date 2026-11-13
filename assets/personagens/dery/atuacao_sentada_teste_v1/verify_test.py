"""Check actual skinned support contact, settled wrists, bone stability and PNG swaps."""
from pathlib import Path
import bpy,json,hashlib,numpy as np
from mathutils import Vector
P=Path(__file__).resolve().parent;C=Path('/workspace/attachments/atuacao_sentada');report=json.loads((P/'atuacao.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(P/'output/Dery_Atuacao_Sentada_Teste.blend'));s=bpy.context.scene;a=bpy.data.objects['DERY | animated character'];r=a.parent
left=[];right=[];legs=[];faces=[];contact={side:[]for side in['R','L']};hand_indices={side:[v.index for v in a.data.vertices if sum(g.weight for g in v.groups if g.group==a.vertex_groups['hand_'+side].index)>.85]for side in['R','L']}
for f in[1,20,46,91,116,139,145,180,211,240]:
 s.frame_set(f);bpy.context.view_layer.update();left.append(list(r.matrix_world@r.pose.bones['hand_L'].head));right.append(list(r.matrix_world@r.pose.bones['hand_R'].head));legs.append([tuple(r.pose.bones[n].matrix.translation)for n in ['pelvis','thigh_L','thigh_R','foot_L','foot_R']if n in r.pose.bones])
 actual=a.data.materials[1].node_tree.nodes['PS1 | face ID'].outputs[0].default_value;assert abs(actual-int(a['PS1_face_id']))<1e-5;faces.append(int(actual))
 if True:
  ev=a.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
  try:
   for side in['R','L']:
    if side=='R'and f not in[1,20,145,211,240]:continue
    pad=bpy.data.objects['Test | fitted armrest '+side];inv=pad.matrix_world.inverted();points=[inv@(ev.matrix_world@mesh.vertices[i].co)for i in hand_indices[side]];points=[p for p in points if abs(p.x)<.0525 and abs(p.y)<.1775];assert points,(f,side)
    gap=min(p.z for p in points)-.018;contact[side].append(dict(frame=f,lowest_gap_m=gap))
  finally:ev.to_mesh_clear()
assert np.max(np.linalg.norm(np.array(left)-np.array(left[0]),axis=1))<.001
# Both wrists return to exactly the same neutral contact instead of running a cycle.
assert np.linalg.norm(np.array(right[-1])-np.array(right[0]))<.001
assert np.max(np.abs(np.array(legs)-np.array(legs[0])))<1e-5
assert all(not fc.modifiers for fc in r.animation_data.action.fcurves)
contact_gaps=[x['lowest_gap_m']for values in contact.values()for x in values]
assert min(contact_gaps)>-.004 and max(contact_gaps)<.004,contact_gaps
record=dict(face_material_matches_selector=True,face_ids_sampled=faces,left_wrist_drift_m=float(np.max(np.linalg.norm(np.array(left)-np.array(left[0]),axis=1))),right_returns_to_rest_m=float(np.linalg.norm(np.array(right[-1])-np.array(right[0]))),legs_frozen=True,no_curve_cycles_or_noise=True,actual_skin_contact=contact,source_unchanged=hashlib.sha256((Path('/workspace/Shorts')/report['source']).read_bytes()).hexdigest()==report['source_sha256'])
(P/'validacao_pose.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print('TEST_POSE_CHECKED',json.dumps(record),flush=True)
