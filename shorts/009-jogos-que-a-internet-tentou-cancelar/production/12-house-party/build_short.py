"""House Party: approved seated acting and clean gameplay on the CRT."""
from pathlib import Path
import bpy,sys,json,math,hashlib,wave,numpy as np
from mathutils import Vector,Matrix,Quaternion
P=Path(__file__).resolve().parent;R=next(p for p in P.parents if(p/'AGENTS.md').exists());C=Path('/workspace/attachments/proximos_11_12/12-house-party');info=json.loads((P/'timeline.json').read_text());N=info['frames'];FPS=30;D=json.loads((P/'direcao.json').read_text())
sys.path.insert(0,str(R/'assets/personagens/dery'))
from psx_render import bake_faces
SOURCE=R/'assets/personagens/dery/atuacao_sentada_teste_v1/output/Dery_Atuacao_Apoio_Real.blend';source_sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();actor=bpy.data.objects['DERY | animated character'];r=actor.parent
mesh_sha=hashlib.sha256(np.array([v.co[:]for v in actor.data.vertices],np.float32).tobytes()).hexdigest();base={pb.name:pb.matrix_basis.copy()for pb in r.pose.bones};rest={side:dict(W=r.matrix_world@r.pose.bones['hand_'+side].head,Q=(r.matrix_world@r.pose.bones['hand_'+side].matrix).to_quaternion())for side in ['R','L']}
s.frame_set(91);bpy.context.view_layer.update();peak=dict(W=r.matrix_world@r.pose.bones['hand_R'].head,Q=(r.matrix_world@r.pose.bones['hand_R'].matrix).to_quaternion());s.frame_set(1);r.animation_data_clear();actor.animation_data_clear()
for pb in r.pose.bones:pb.matrix_basis=base[pb.name]
rot=r.matrix_world.to_quaternion();inv=r.matrix_world.inverted();lat=rot@Vector((1,0,0));fwd=rot@Vector((0,-1,0));up=Vector((0,0,1))
# Reuse the approved two-bone solution, with new intent/timing on this voice.
code=(P.parent/'revisao_r4/montar_sentado.py').read_text();functions=code[code.index(' def smooth'):code.index(' records={}')];exec('\n'.join(line[1:]for line in functions.splitlines()))
cam=bpy.data.objects[s['Production | camera']];host_mat=cam.matrix_world.copy();host_lens=cam.data.lens;monitor=bpy.data.objects['TESTE | jogo no CRT'];monitor_mat=monitor.matrix_world.copy();monitor_lens=monitor.data.lens
cam.animation_data_clear();cam.data.animation_data_clear();records={};renderframes=[];aliases={};max_reach=0
for sh in info['shots']:
 if sh['kind']not in ['monitor','host','close']:continue
 if sh['kind']=='monitor':aliases[str(sh['start'])]=list(range(sh['start']+1,sh['end']+1))
 for frame in ([sh['start'],sh['end']] if sh['kind']=='monitor' else range(sh['start'],sh['end']+1)):
  s.frame_set(frame)
  for pb in r.pose.bones:pb.matrix_basis=base[pb.name]
  u=(frame-sh['start'])/max(1,sh['end']-sh['start']);weight=0;tilt=0;nod=0;mood=sh['mood']
  # Intent-specific preparation, hold and return. Left hand retains real support.
  gesture=D['gestures'].get(mood,{});weight=gesture.get('strength',0)*envelope(u,*gesture.get('timing',[.05,.30,.55,.94]));tilt=gesture.get('tilt',0)*envelope(u,.12,.38,.64,.96);nod=gesture.get('nod',0)*envelope(u,.16,.44,.66,.98)
  for name,factor in [('neck',.22),('head',.78)]:
   pb=r.pose.bones[name];pb.rotation_mode='QUATERNION';pb.rotation_quaternion=base[name].to_quaternion()@Quaternion((0,1,0),tilt*factor)@Quaternion((1,0,0),nod*factor)
  bpy.context.view_layer.update()
  for side in ['R','L']:
   W=rest[side]['W'].copy();Q=rest[side]['Q'].copy();v=weight if side=='R'else 0
   if v:
    W=W.lerp(peak['W'],v)+lat*(.022*math.sin(math.pi*v));Q=Q.slerp(peak['Q'],v)
   arm(side,W,Q,v);max_reach=max(max_reach,(W-r.matrix_world@r.pose.bones['arm_'+side].head).length)
  for name in ['neck','head',*['%s_%s'%(k,side)for side in ['R','L']for k in ['arm','forearm','hand']]]:
   pb=r.pose.bones[name];records.setdefault(name,[]).append((frame,pb.rotation_quaternion.copy(),pb.location.copy()))
  cam.matrix_world=monitor_mat if sh['kind']=='monitor'else host_mat
  if sh['kind']=='close':
   cam.location+=cam.matrix_world.to_quaternion()@Vector((0,0,-1))*.24
  cam.rotation_mode='QUATERNION'
  for prop in ['location','rotation_quaternion']:cam.keyframe_insert(prop,frame=frame)
  cam.data.lens=monitor_lens if sh['kind']=='monitor'else host_lens;cam.data.keyframe_insert('lens',frame=frame)
  if sh['kind']!='monitor'or frame==sh['start']:renderframes.append(frame)
action=bpy.data.actions.new('House Party | authored seated acting');r.animation_data_create().action=action
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
for owner in [cam,cam.data]:
 for fc in owner.animation_data.action.fcurves:
  for k in fc.keyframe_points:k.interpolation='CONSTANT'
families=json.loads((R/'assets/personagens/dery/expressions_ps1/v3/fala_familias.json').read_text())
with wave.open(str(P/'assets/voz/voz_timeline.wav'))as w:rate=w.getframerate();voice=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(float)/32768
code=(P.parent/'01-gta-san-andreas/revise_animation.py').read_text();exec(code[code.index('def mouth_at(t):'):code.index('face_metrics={}')]);keys=[]
for frame in range(1,N+1):
 t=(frame-1)/30;shot=next(sh for sh in info['shots']if sh['start']<=frame<=sh['end']);mood=D['families'].get(shot['mood'],'neutra');value=families[mood][mouth_at(math.floor(t*15)/15)]
 for begin,end,index in D['faces']:
  if begin<=t<end:value=index
 for blink in D['blinks']:
  if blink<=t<blink+.1:value=10
 keys.append((frame,value));actor['PS1_face_id']=value;actor.keyframe_insert('["PS1_face_id"]',frame=frame)
bake_faces(actor,keys)
for fc in actor.animation_data.action.fcurves:
 for k in fc.keyframe_points:k.interpolation='CONSTANT'
screen=bpy.data.objects['Tela do PC | substituir por vídeo'];tex=next(n for n in screen.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE');tex.image=bpy.data.images.load(str(P/info['monitor_file']),check_existing=True);tex.interpolation='Linear';tex.image_user.frame_start=1;tex.image_user.frame_offset=0;tex.image_user.frame_duration=N;tex.image_user.use_auto_refresh=True
s.frame_start=1;s.frame_end=N;s.render.fps=30;s.render.resolution_x=768;s.render.resolution_y=432
if s.sequence_editor:s.sequence_editor_clear()
s.sequence_editor_create().sequences.new_sound('Voz original integral',str(P/'assets/voz/voz_timeline.wav'),channel=1,frame_start=1);s.render.use_sequencer=False;s.render.use_compositing=False
for image in bpy.data.images:
 if image.source in ['FILE','MOVIE']and image.filepath and not image.packed_file:image.filepath=bpy.path.abspath(image.filepath)
exec(compile((P/'criar_ceninhas.py').read_text(),str(P/'criar_ceninhas.py'),'exec'))
s.frame_set(1);bpy.context.view_layer.update();assert mesh_sha==hashlib.sha256(np.array([v.co[:]for v in actor.data.vertices],np.float32).tobytes()).hexdigest();assert not any('lojista'in o.name for o in s.objects)
bpy.ops.file.pack_all();bpy.ops.file.make_paths_relative();s['Production | chapter']='House Party';s['Production | chapter order']=12;s['Production | revision']=5;s['Production | standing Dery']=False
bpy.ops.wm.save_as_mainfile(filepath=str(P/'output'/info['model']),compress=True);assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_sha
report=dict(source=str(SOURCE.relative_to(R)),source_sha256=source_sha,source_unchanged=True,avatar_mesh_unchanged=True,standing_dery=False,original_chair=True,new_props=True,gag_count=sum(sh['kind']=='gag'for sh in info['shots']),gag_frames={sh['mood']:[sh['start'],sh['end']]for sh in info['shots']if sh['kind']=='gag'},face_ids=len(set(v for _,v in keys)),face_changes=sum(a[1]!=b[1]for a,b in zip(keys,keys[1:])),max_wrist_reach=max_reach,frames_to_render=renderframes,monitor_background_aliases=aliases,monitor_video_composed_per_frame=True)
(P/'construcao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('DOAX3_SCENE_READY',len(renderframes),report['face_ids'],flush=True)
