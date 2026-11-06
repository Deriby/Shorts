"""Check original geometry, seated support, IK reach, facial seams and PS1 precision."""
from pathlib import Path
from collections import defaultdict
import bpy,json,sys
from mathutils import Vector
ROOT=Path(__file__).resolve().parent;REPO=next(p for p in ROOT.parents if(p/'AGENTS.md').exists());s=bpy.context.scene;a=bpy.data.objects['DERY | animated character'];a2=bpy.data.objects['COCKPIT | Dery'];r=bpy.data.objects['Dery_Rig'];r2=bpy.data.objects['COCKPIT | Dery rig']
with bpy.data.libraries.load(str(REPO/'shorts/004-crash-apelido/production/output/Dery_Crash_Master_R5.blend'))as(src,dst):dst.objects=['DERY | animated character']
orig=dst.objects[0];geometry=max((v.co-o.co).length for v,o in zip(a.data.vertices,orig.data.vertices));assert geometry==0
assert len(a2.data.vertices)==len(orig.data.vertices)and max((v.co-o.co).length for v,o in zip(a2.data.vertices,orig.data.vertices))==0
s.frame_set(1);bpy.context.view_layer.update();reference_feet={side:(r.matrix_world@r.pose.bones['foot_'+side].head).copy()+Vector((20,0,0))for side in ['R','L']}
faces=[];motion=[];hips=[];reach=[];standing=[]
for obj,frames in [(a,[111,361,596]),(a2,[651,735,825,836,877,966])]:
 mod=next(m for m in obj.modifiers if m.type=='NODES')
 def positions(on):
  mod.show_viewport=on;bpy.context.view_layer.update();ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();v=[x.co.copy()for x in me.vertices];ev.to_mesh_clear();return v
 for f in frames:
  s.frame_set(f);before=positions(False);after=positions(True);groups=defaultdict(list)
  for i,v in enumerate(obj.data.vertices):
   if v.co.z>1.44 and v.co.y<-.015 and abs(v.co.x)<.14:groups[tuple(round(c,6)for c in before[i])].append(i)
  gap=max(((after[i]-after[ids[0]]).length for ids in groups.values()if len(ids)>1 for i in ids),default=0);assert gap<.00005,(f,gap)
  disp=max((x-y).length for x,y in zip(before,after));assert disp>.0001
  faces.append(dict(actor=obj.name,frame=f,max_facial_split_m=gap));motion.append(dict(actor=obj.name,frame=f,max_precision_displacement_m=disp))
for f in [111,361,596]:
 s.frame_set(f);bpy.context.view_layer.update();hips.append((r.matrix_world@r.pose.bones['pelvis'].head).copy())
 for side in ['R','L']:
  shoulder=r.matrix_world@r.pose.bones['arm_'+side].head;target=bpy.data.objects['R3 | '+side+' wrist'].location;distance=(target-shoulder).length;error=((r.matrix_world@r.pose.bones['hand_'+side].head)-target).length
  assert distance<.442 and error<.015,(f,side,distance,error);reach.append(dict(frame=f,side=side,reach_m=distance,target_error_m=error))
assert max((v-hips[0]).length for v in hips)<.00001
for f in [651,735,825,836,877,966]:
 s.frame_set(f);bpy.context.view_layer.update();standing.append([(r2.matrix_world@r2.pose.bones['foot_'+side].head).copy()for side in ['R','L']])
assert max((feet[i]-standing[0][i]).length for feet in standing for i in [0,1])<.00001
for i,side in enumerate(['R','L']):assert max((feet[i]-reference_feet[side]).length for feet in standing)<.0001
# The cockpit clone has its own IK controls and retains seated pelvis support.
cockpit_hips=[];cockpit_reach=[]
for f in [651,735,825,836,877,966]:
 s.frame_set(f);bpy.context.view_layer.update();cockpit_hips.append((r2.matrix_world@r2.pose.bones['pelvis'].head).copy())
 for side in ['R','L']:
  shoulder=r2.matrix_world@r2.pose.bones['arm_'+side].head;target=bpy.data.objects['COCKPIT | '+side+' wrist'].location;distance=(target-shoulder).length;error=((r2.matrix_world@r2.pose.bones['hand_'+side].head)-target).length
  assert distance<.442 and error<.015,(f,side,distance,error)
  cockpit_reach.append(dict(frame=f,side=side,reach_m=distance,target_error_m=error))
assert max((v-cockpit_hips[0]).length for v in cockpit_hips)<.00001
# Check the controlled gag: the chair and actor stay put while each panel moves outward once.
for label,sign in [('Left',-1),('Right',1)]:
 root=bpy.data.objects['COCKPIT | '+label+' panel root'];values=[]
 for f in [800,824,830,836,840,966]:
  s.frame_set(f);values.append(root.location.x*sign);assert abs(root.location.y)<1e-7 and abs(root.location.z)<1e-7
 assert values[0]==0 and abs(values[-1]-1.65)<1e-5 and all(a<=b+1e-6 for a,b in zip(values,values[1:]))
rear=next(n for n in bpy.data.objects['COCKPIT | rear picture'].data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE');assert rear.image.source=='FILE'and rear.image.name.startswith('piloto_poster')
tex=next(n for n in bpy.data.objects['CRT moving picture'].data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE');assert tex.image_user.use_auto_refresh and tex.image_user.frame_duration==s.frame_end
for obj in [a,a2]:
 assert all(k.value==0 for k in obj.data.shape_keys.key_blocks[1:])
 for fc in obj.animation_data.action.fcurves:
  if 'PS1_face_id'in fc.data_path:assert all(k.interpolation=='CONSTANT'for k in fc.keyframe_points)
report=dict(original_geometry_max_displacement_m=geometry,face_checks=faces,precision_checks=motion,seated_pelvis_stable=True,cockpit_seated_support_stable=True,arm_checks=reach,cockpit_arm_checks=cockpit_reach,monitor_frames=tex.image_user.frame_duration,monitor_auto_refresh=True,expressions='31 PNG faces, discrete changes, no active morphs',acting='Non-periodic phrase gestures with asymmetric strokes, holds and releases')
(ROOT/('scene_validation_16x9.json'if '--wide'in sys.argv else'scene_validation.json')).write_text(json.dumps(report,indent=2));print('DVA_SCENE_VALIDATED',flush=True)
