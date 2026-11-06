"""Verify face seams, original geometry, seated support and continuous camera movement."""
from pathlib import Path
from collections import defaultdict
import bpy,json,math
ROOT=Path(__file__).resolve().parent;REPO=next(p for p in ROOT.parents if(p/'AGENTS.md').exists())
s=bpy.context.scene;a=bpy.data.objects['DERY | animated character'];r=bpy.data.objects['Dery_Rig'];cam=s.camera
with bpy.data.libraries.load(str(REPO/'shorts/004-crash-apelido/production/output/Dery_Crash_Master_R5.blend'))as(src,dst):dst.objects=['DERY | animated character']
original=dst.objects[0];geometry=max((v.co-o.co).length for v,o in zip(a.data.vertices,original.data.vertices));assert geometry==0
samples=[205,248,284,366,440,553,608,677,733,759];checks=[];arms=[];hips=[];feet=[]
modifier=next(m for m in a.modifiers if m.type=='NODES')
def positions(on):
 modifier.show_viewport=on;bpy.context.view_layer.update();ev=a.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();out=[v.co.copy()for v in mesh.vertices];ev.to_mesh_clear();return out
for f in samples:
 s.frame_set(f);before=positions(False);after=positions(True);groups=defaultdict(list)
 for i,v in enumerate(a.data.vertices):
  if v.co.z>1.44 and v.co.y<-.015 and abs(v.co.x)<.14:groups[tuple(round(c,6)for c in before[i])].append(i)
 gap=max(((after[i]-after[ids[0]]).length for ids in groups.values()if len(ids)>1 for i in ids),default=0);assert gap<.00005
 disp=max((x-y).length for x,y in zip(before,after));assert disp>.0001
 checks.append(dict(frame=f,max_facial_split_m=gap,precision_displacement_m=disp));hips.append((r.matrix_world@r.pose.bones['pelvis'].head).copy());feet.append([(r.matrix_world@r.pose.bones['foot_'+side].head).copy()for side in ['R','L']])
 for side in ['R','L']:
  shoulder=r.matrix_world@r.pose.bones['arm_'+side].head;target=bpy.data.objects['R3 | '+side+' wrist'].location;distance=(target-shoulder).length;error=((r.matrix_world@r.pose.bones['hand_'+side].head)-target).length
  assert distance<.442 and error<.015,(f,side,distance,error);arms.append(dict(frame=f,side=side,reach_m=distance,target_error_m=error))
assert max((h-hips[0]).length for h in hips)<.00001
assert max((v[i]-feet[0][i]).length for v in feet for i in [0,1])<.00001
previous=None;deltas=[]
for f in range(205,768):
 s.frame_set(f);bpy.context.view_layer.update();value=(cam.matrix_world.translation.copy(),cam.matrix_world.to_quaternion(),cam.data.lens)
 if previous:
  step=(value[0]-previous[0]).length;rotation=value[1].rotation_difference(previous[1]).angle;lens=abs(value[2]-previous[2]);assert step<.045 and rotation<.06 and lens<.8,(f,step,rotation,lens);deltas.append((step,rotation,lens))
 previous=value
tex=next(n for n in bpy.data.objects['CRT moving picture'].data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE');assert tex.image_user.use_auto_refresh and tex.image_user.frame_duration==s.frame_end
assert s.render.resolution_x==640 and s.render.resolution_y==360
assert all(k.value==0 for k in a.data.shape_keys.key_blocks[1:])
assert all(key.interpolation=='CONSTANT'for fc in a.animation_data.action.fcurves if 'PS1_face_id'in fc.data_path for key in fc.keyframe_points)
report=dict(original_geometry_max_displacement_m=geometry,face_checks=checks,arm_checks=arms,seated_support_stable=True,camera_continuous=True,max_camera_step_m=max(d[0]for d in deltas),max_camera_rotation_rad=max(d[1]for d in deltas),max_lens_step_mm=max(d[2]for d in deltas),monitor_auto_refresh=True,monitor_frames=tex.image_user.frame_duration,format='16:9 only',picture_cuts=2)
(ROOT/'scene_validation.json').write_text(json.dumps(report,indent=2));print('INTRO_SCENE_VALIDATED',flush=True)
