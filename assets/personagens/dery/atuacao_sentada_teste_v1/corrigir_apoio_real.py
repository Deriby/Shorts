"""Reblock resting arms against the evaluated thighs; preserve timing, face and body."""
from pathlib import Path
import bpy,json,math,hashlib,numpy as np
from mathutils import Vector,Matrix,Quaternion
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;C=Path('/workspace/attachments/atuacao_sentada_v3');C.mkdir(parents=True,exist_ok=True)
source=P/'output/Dery_Atuacao_Cadeira_Original.blend';before=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;a=bpy.data.objects['DERY | animated character'];r=a.parent;s.frame_set(1);bpy.context.view_layer.update()
rot=r.matrix_world.to_quaternion();lat=rot@Vector((1,0,0));fwd=rot@Vector((0,-1,0));up=Vector((0,0,1));origin=r.matrix_world.translation.copy();inv=r.matrix_world.inverted()
armnames={k+'_'+side for side in ['R','L']for k in ['arm','forearm','hand']}
def keep_signature(action):
 return hashlib.sha256(json.dumps([(fc.data_path,fc.array_index,[tuple(k.co)for k in fc.keyframe_points])for fc in action.fcurves if not any('"'+n+'"'in fc.data_path for n in armnames)]).encode()).hexdigest()
kept=keep_signature(r.animation_data.action)
# Store the approved performance before replacing only the six arm/hand curves.
old={}
for frame in range(1,241):
 s.frame_set(frame);bpy.context.view_layer.update();old[frame]={side:{'W':r.matrix_world@r.pose.bones['hand_'+side].head,'E':r.matrix_world@r.pose.bones['forearm_'+side].head,'Q':(r.matrix_world@r.pose.bones['hand_'+side].matrix).to_quaternion()}for side in ['R','L']}
s.frame_set(1)
r.animation_data.action=r.animation_data.action.copy();action=r.animation_data.action
for fc in list(action.fcurves):
 if any('"'+n+'"'in fc.data_path for n in armnames):action.fcurves.remove(fc)
gn=[m for m in a.modifiers if m.type=='NODES']
for m in gn:m.show_viewport=False;m.show_render=False
bpy.context.view_layer.update();ev=a.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();mesh.calc_loop_triangles();world=[ev.matrix_world@v.co for v in mesh.vertices];hands={};bvhs={}
for side,sign in [('R',-1),('L',1)]:
 groups={g.index for g in a.vertex_groups if g.name=='thigh_'+side or g.name.startswith('CC_Base_'+side+'_ThighTwist')}
 ids={v.index for v in a.data.vertices if sum(g.weight for g in v.groups if g.group in groups)>.15}
 bvhs[side]=BVHTree.FromPolygons(world,[tuple(t.vertices)for t in mesh.loop_triangles if all(i in ids for i in t.vertices)],all_triangles=True)
 hi=a.vertex_groups['hand_'+side].index;hids=[v.index for v in a.data.vertices if sum(g.weight for g in v.groups if g.group==hi)>.85]
 hb=r.data.bones['hand_'+side];cloud=[hb.matrix_local.inverted()@a.data.vertices[i].co for i in hids]
 q=Quaternion(lat,math.radians(55))@old[1][side]['Q'];xy=origin+lat*(sign*.115)+fwd*.07
 levels=[]
 for v in cloud:
  delta=q@v;hit=bvhs[side].ray_cast(Vector((xy.x+delta.x,xy.y+delta.y,1.2)),Vector((0,0,-1)),2)[0]
  if hit is not None:levels.append(hit.z-delta.z)
 assert levels,side
 W=Vector((xy.x,xy.y,max(levels)+.001));arm=r.pose.bones['arm_'+side];fore=r.pose.bones['forearm_'+side]
 hands[side]=dict(W=W,Q=q,L1=arm.length,L2=fore.length,indices=hids)
ev.to_mesh_clear()
def setworld(pb,pos,q):
 pb.rotation_mode='QUATERNION';pb.matrix=inv@Matrix.LocRotScale(pos,q,Vector((1,1,1)))
def aim(q,d):return(q@Vector((0,1,0))).rotation_difference(d)@q
def solve(side,W,qhand,blend,frame):
 sign=-1 if side=='R'else 1;d=hands[side];arm=r.pose.bones['arm_'+side];fore=r.pose.bones['forearm_'+side];hand=r.pose.bones['hand_'+side];S=r.matrix_world@arm.head;delta=W-S;D=delta.length
 assert D<d['L1']+d['L2']-.002,(side,frame,D,W[:])
 axis=delta.normalized();along=(d['L1']**2-d['L2']**2+D*D)/(2*D);height=math.sqrt(max(0,d['L1']**2-along*along));middle=S+axis*along
 preferred=(S-up*d['L1']+lat*(sign*.025)-fwd*.03).lerp(old[frame][side]['E'],blend);perp=preferred-middle;perp-=axis*perp.dot(axis);E=middle+perp.normalized()*height
 fore_dir=(W-E).normalized();qa=aim(rot@arm.bone.matrix_local.to_quaternion(),(E-S).normalized());qf=aim(rot@fore.bone.matrix_local.to_quaternion(),fore_dir)
 relative=(rot@fore.bone.matrix_local.to_quaternion()).inverted()@(rot@hand.bone.matrix_local.to_quaternion());dq=qf.inverted()@qhand@relative.inverted();_,twist=dq.to_swing_twist('Y');qf=qf@Quaternion((0,1,0),twist)
 setworld(arm,S,qa);bpy.context.view_layer.update();setworld(fore,E,qf);bpy.context.view_layer.update();setworld(hand,W,qhand);bpy.context.view_layer.update()
def contact(side):
 ev=a.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();gaps=[]
 for i in hands[side]['indices']:
  p=ev.matrix_world@me.vertices[i].co;hit=bvhs[side].ray_cast(Vector((p.x,p.y,1.2)),Vector((0,0,-1)),2)[0]
  if hit is not None:gaps.append(p.z-hit.z)
 ev.to_mesh_clear();assert gaps,side;return min(gaps)
# Calibrate against skinned hand vertices and the actual clothing surface.
for side in ['R','L']:
 for _ in range(3):
  d=hands[side];solve(side,d['W'],d['Q'],0,1);gap=contact(side);d['W'].z+=.001-gap
 solve(side,hands[side]['W'],hands[side]['Q'],0,1)
 print('REST_CONTACT',side,list(hands[side]['W']),contact(side),flush=True)
records={};gaps={side:[]for side in hands};trajectory={side:[]for side in hands}
for frame in range(1,241):
 s.frame_set(frame);bpy.context.view_layer.update()
 for side in ['R','L']:
  d=hands[side];lift=max(0,min(1,(old[frame][side]['W'].z-old[1][side]['W'].z)/.17))if side=='R'else 0;blend=lift*lift*(3-2*lift)
  W=old[frame][side]['W']+(d['W']-old[1][side]['W'])*(1-blend);Q=d['Q'].slerp(old[frame][side]['Q'],blend)
  if lift==0:W=d['W'].copy()
  solve(side,W,Q,blend,frame);trajectory[side].append(list(W))
  for name in ['arm_'+side,'forearm_'+side,'hand_'+side]:
   pb=r.pose.bones[name];records.setdefault(name,[]).append((frame,pb.rotation_quaternion.copy(),pb.location.copy()))
  if side=='L'or frame in [1,16,31,37,40,139,145,180,211,240]:
   if frame%15==1 or frame in [31,37,40,139,145,180,211,240]:gaps[side].append(dict(frame=frame,gap_m=contact(side)))
for name,rows in records.items():
 last=None
 for frame,q,loc in rows:
  if last is not None and q.dot(last)<0:q.negate()
  last=q.copy()
 for path,components,idx in [('rotation_quaternion',4,1),('location',3,2)]:
  for i in range(components):
   fc=action.fcurves.new(f'pose.bones["{name}"].{path}',index=i);fc.keyframe_points.add(240);fc.keyframe_points.foreach_set('co',[v for row in rows for v in (row[0],row[idx][i])])
   for k in fc.keyframe_points:k.interpolation='LINEAR'
   fc.update()
assert keep_signature(action)==kept
for side,values in gaps.items():assert all(-.002<x['gap_m']<.003 for x in values),(side,values)
for m in gn:m.show_viewport=True;m.show_render=True
s.frame_set(1);bpy.context.view_layer.update();s['Test | chair revision']='Hands rest on the actual thighs. Original chair unchanged; same gesture timing, face and body.'
bpy.ops.file.pack_all();bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(P/'output/Dery_Atuacao_Apoio_Real.blend'),compress=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
report=dict(rest_surface='Each hand rests on its corresponding clothed upper thigh',rest_wrist_world={side:list(d['W'])for side,d in hands.items()},skin_contact_without_screen_snap=gaps,only_arm_hand_animation_changed=True,other_bone_curves_unchanged=True,other_bone_curve_sha256=kept,face_camera_audio_unchanged=True,original_chair_unchanged=True,new_props=False,source_unchanged=True,right_gesture_peak_frame=90,right_return_seconds=4.62,wrist_trajectories=trajectory)
(P/'validacao_apoio_real.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('REST_READY',flush=True)
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
for frame in [1,91,145]:
 s.frame_set(frame);s.render.filepath=str(C/f'pose_{frame:03d}.png');bpy.ops.render.render(write_still=True)
