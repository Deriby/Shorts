"""Seat reactions over the original voice; use the approved contact pose."""
from pathlib import Path
import bpy,sys,json,math,hashlib,numpy as np
from mathutils import Vector,Matrix,Quaternion
P=Path(__file__).resolve().parent;ROOT=P.parent;REPO=next(p for p in P.parents if(p/'AGENTS.md').exists());sys.path.insert(0,str(REPO/'assets/personagens/dery'))
from psx_render import bake_faces
APPROVED=REPO/'assets/personagens/dery/atuacao_sentada_teste_v1/output/Dery_Atuacao_Apoio_Real.blend'
for project in sorted(ROOT.glob('0[1-4]-*')):
 out=project/'output/R4_Sem_Dery_Em_Pe';info=json.loads((out/'timeline.json').read_text());slug=info['slug'];N=info['frames'];C=Path('/workspace/attachments/revisao_r4')/project.name;C.mkdir(parents=True,exist_ok=True)
 original=next((project/'output').glob('Dery_*.blend'));source_sha=hashlib.sha256(original.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(original));actor=bpy.data.objects['DERY | animated character'];fc=actor.animation_data.action.fcurves.find('["PS1_face_id"]');assert fc
 facekeys=[(f,int(round(fc.evaluate(f))))for f in range(1,N+1)]
 bpy.ops.wm.open_mainfile(filepath=str(APPROVED));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();actor=bpy.data.objects['DERY | animated character'];r=actor.parent
 base={pb.name:pb.matrix_basis.copy()for pb in r.pose.bones};rest={side:dict(W=r.matrix_world@r.pose.bones['hand_'+side].head,Q=(r.matrix_world@r.pose.bones['hand_'+side].matrix).to_quaternion())for side in ['R','L']}
 s.frame_set(91);bpy.context.view_layer.update();peak=dict(W=r.matrix_world@r.pose.bones['hand_R'].head,Q=(r.matrix_world@r.pose.bones['hand_R'].matrix).to_quaternion());s.frame_set(1)
 r.animation_data_clear();actor.animation_data_clear()
 for pb in r.pose.bones:pb.matrix_basis=base[pb.name]
 rot=r.matrix_world.to_quaternion();inv=r.matrix_world.inverted();lat=rot@Vector((1,0,0));fwd=rot@Vector((0,-1,0));up=Vector((0,0,1))
 def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
 def envelope(u,a,b,c,d):
  return smooth((u-a)/(b-a))if u<b else 1 if u<c else 1-smooth((u-c)/(d-c))
 def setworld(pb,pos,q):pb.rotation_mode='QUATERNION';pb.matrix=inv@Matrix.LocRotScale(pos,q,Vector((1,1,1)))
 def aim(q,d):return(q@Vector((0,1,0))).rotation_difference(d)@q
 def arm(side,W,Q,weight):
  sign=-1 if side=='R'else 1;a=r.pose.bones['arm_'+side];f=r.pose.bones['forearm_'+side];h=r.pose.bones['hand_'+side];S=r.matrix_world@a.head;delta=W-S;D=delta.length;assert D<a.length+f.length-.002
  axis=delta.normalized();along=(a.length*a.length-f.length*f.length+D*D)/(2*D);height=math.sqrt(max(0,a.length*a.length-along*along));middle=S+axis*along;preferred=S-up*a.length+lat*(sign*.025)*(1-weight)-fwd*.03*(1-weight);perp=preferred-middle;perp-=axis*perp.dot(axis);E=middle+perp.normalized()*height;direction=(W-E).normalized()
  qa=aim(rot@a.bone.matrix_local.to_quaternion(),(E-S).normalized());qf=aim(rot@f.bone.matrix_local.to_quaternion(),direction);relative=(rot@f.bone.matrix_local.to_quaternion()).inverted()@(rot@h.bone.matrix_local.to_quaternion());dq=qf.inverted()@Q@relative.inverted();_,twist=dq.to_swing_twist('Y');qf=qf@Quaternion((0,1,0),twist)
  setworld(a,S,qa);bpy.context.view_layer.update();setworld(f,E,qf);bpy.context.view_layer.update();setworld(h,W,Q);bpy.context.view_layer.update()
 records={};renderframes=[]
 for sh in info['shots']:
  if sh['kind']!='seated':continue
  for frame in range(sh['start'],sh['end']+1):
   s.frame_set(frame)
   for pb in r.pose.bones:pb.matrix_basis=base[pb.name]
   u=(frame-sh['start'])/max(1,sh['end']-sh['start']);label=sh['label'];weight=0
   if label=='desbloqueio':weight=.65*envelope(u,.08,.40,.53,.89)
   elif label=='juiz_gamer':weight=.75*envelope(u,.04,.34,.54,.88)
   # Other reactions deliberately rest the arms; look and PNGs carry the beat.
   tilt=.035*math.sin(math.pi*u) if label in ['classificacao','consequencia'] else -.022*math.sin(math.pi*u)
   for name,factor in [('neck',.22),('head',.78)]:
    pb=r.pose.bones[name];pb.rotation_mode='QUATERNION';pb.rotation_quaternion=base[name].to_quaternion()@Quaternion((0,1,0),tilt*factor)
   bpy.context.view_layer.update()
   for side in ['R','L']:
    W=rest[side]['W'].copy();Q=rest[side]['Q'].copy();v=weight if side=='R'else 0
    if v:W=W.lerp(peak['W'],v);Q=Q.slerp(peak['Q'],v)
    arm(side,W,Q,v)
   for name in ['neck','head',*['%s_%s'%(k,side)for side in ['R','L']for k in ['arm','forearm','hand']]]:
    pb=r.pose.bones[name];records.setdefault(name,[]).append((frame,pb.rotation_quaternion.copy(),pb.location.copy()))
   renderframes.append(frame)
 action=bpy.data.actions.new(slug+' | seated revisions');r.animation_data_create().action=action
 for name,rows in records.items():
  prev=None
  for frame,q,loc in rows:
   if prev is not None and q.dot(prev)<0:q.negate()
   prev=q.copy()
  for path,components,col in [('rotation_quaternion',4,1),('location',3,2)]:
   for i in range(components):
    fc=action.fcurves.new(f'pose.bones["{name}"].{path}',index=i);fc.keyframe_points.add(len(rows));fc.keyframe_points.foreach_set('co',[v for row in rows for v in (row[0],row[col][i])])
    for k in fc.keyframe_points:k.interpolation='LINEAR'
    fc.update()
 for frame,value in facekeys:actor['PS1_face_id']=value;actor.keyframe_insert('["PS1_face_id"]',frame=frame)
 bake_faces(actor,facekeys)
 for fc in actor.animation_data.action.fcurves:
  for k in fc.keyframe_points:k.interpolation='CONSTANT'
 s.frame_start=1;s.frame_end=N;s.render.fps=30
 if s.sequence_editor:s.sequence_editor_clear()
 s.sequence_editor_create().sequences.new_sound('Voz original integral',str(project/'assets/voz/voz_timeline.wav'),channel=1,frame_start=1);s.render.use_sequencer=False
 for image in bpy.data.images:
  if image.source=='FILE'and image.filepath and not image.packed_file:image.filepath=bpy.path.abspath(image.filepath)
 bpy.ops.file.pack_all();bpy.ops.file.make_paths_relative();s.frame_set(renderframes[0]);dest=out/(slug+'_R4_Dery_Sentado.blend');bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
 assert not any('lojista'in o.name for o in s.objects);assert hashlib.sha256(original.read_bytes()).hexdigest()==source_sha
 data=dict(source=str(original.relative_to(REPO)),source_sha256=source_sha,source_unchanged=True,approved_pose=str(APPROVED.relative_to(REPO)),frames=renderframes,standing_actor_count=0,original_chair=True,new_props=False,original_face_ids=True,left_hand_on_thigh=True)
 (out/'animacao_revisada.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print('SEATED_CHAPTER_READY',project.name,len(renderframes),flush=True)
