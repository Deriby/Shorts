"""Phrase-specific performance, discrete faces, PS1 precision and a cockpit whose panels slide away."""
from pathlib import Path
import sys,json,math,wave,array,bpy
from mathutils import Vector,Quaternion,Matrix
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parent;REPO=next(p for p in ROOT.parents if(p/'AGENTS.md').exists());WIDE='--wide'in sys.argv
sys.path[:0]=[str(REPO/'shorts/003-teste-quarto-gamer/production'),str(REPO/'assets/personagens/dery'),str(REPO/'assets/personagens/dery/expressions_ps1/v2'),str(REPO/'assets/personagens/dery/roupas/camiseta_preta')]
import helpers as H
from ps1_precision import add_safe_precision
from setup_faces31 import install as install_faces
from aplicar import aplicar
from limpar import light as neutral_light
bpy.ops.wm.open_mainfile(filepath=str(REPO/'shorts/004-crash-apelido/production/output/Dery_Crash_Master_R5.blend'))
s=bpy.context.scene;H.C.s=s;r=bpy.data.objects['Dery_Rig'];a=bpy.data.objects['DERY | animated character'];cam=s.camera
for im in bpy.data.images:
 if im.source=='FILE'and im.filepath:im.filepath=bpy.path.abspath(im.filepath)
s.frame_set(1);base={p.name:p.rotation_quaternion.copy()for p in r.pose.bones};rest={p.name:p.matrix_local.to_quaternion()for p in r.data.bones}
bpy.context.view_layer.update();evaluated_rig=r.evaluated_get(bpy.context.evaluated_depsgraph_get());seated_pose={p.name:p.matrix.copy()for p in evaluated_rig.pose.bones}
r.animation_data_clear();a.animation_data_clear();cam.animation_data_clear();cam.data.animation_data_clear()
if a.data.shape_keys:
 a.data.shape_keys.animation_data_clear()
 for k in a.data.shape_keys.key_blocks[1:]:k.value=0
for side in ['R','L']:
 bpy.data.objects['R3 | '+side+' wrist'].animation_data_clear();ik=r.pose.bones['forearm_'+side].constraints['R3 | conversational gesture'];ik.influence=1;ik.use_stretch=False
for m in list(a.modifiers):
 if m.type=='NODES':a.modifiers.remove(m)
aplicar(a);info=json.loads((ROOT/'timeline.json').read_text());N=info['frames'];aspect=16/9 if WIDE else 9/16
s.render.resolution_x=640 if WIDE else 360;s.render.resolution_y=360 if WIDE else 640;s.render.resolution_percentage=100;s.render.fps=24;s.frame_start=1;s.frame_end=N
s.render.engine='CYCLES';s.cycles.samples=1;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2;s.render.use_persistent_data=True;s.render.use_compositing=False;s.render.use_sequencer=False;s.render.dither_intensity=0;s.sequence_editor_clear();cam.data.sensor_fit='VERTICAL'
def precision(obj,avatar=False):
 add_safe_precision(obj,cam,width=405 if WIDE else 128,height=228,aspect=aspect)
 if not avatar:
  for x in obj.data.attributes['PS1SnapWeight'].data:x.value=1
precision(a,True)
for p in a.data.polygons:
 if p.material_index!=1:p.use_smooth=False
# Quantize original body/nose texture addressing, leaving the reviewed face atlas intact.
for mat in a.data.materials:
 if not mat or not mat.use_nodes:continue
 for n in mat.node_tree.nodes:
  if n.type=='TEX_IMAGE':n.interpolation='Closest'
  if n.type=='VECT_MATH'and n.operation=='SNAP':n.inputs[1].default_value=(1/128,1/128,1)
  elif n.type=='VECT_MATH'and n.operation=='ADD'and abs(n.inputs[1].default_value[0]-.5/512)<1e-7:n.inputs[1].default_value=(.5/128,.5/128,0)
precision(bpy.data.objects['ROOM | baked lighting geometry'])
# Keep the monitor bright and continuously refreshed.
screen=bpy.data.objects['CRT moving picture'];nt=screen.data.materials[0].node_tree;tex=next(n for n in nt.nodes if n.type=='TEX_IMAGE');tex.image=bpy.data.images.load(str(ROOT/'assets/gameplay/monitor_montado.mp4'));tex.interpolation='Closest';tex.image_user.frame_start=1;tex.image_user.frame_offset=0;tex.image_user.frame_duration=N;tex.image_user.use_auto_refresh=True
next(n for n in nt.nodes if n.type=='EMISSION').inputs['Strength'].default_value=1.15
wide_monitor_lens=39
if WIDE:
 cam.location=(1.15,.28,1.55);cam.rotation_euler=(Vector((.1095,-.7959,1.262))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=39;bpy.context.view_layer.update()
 points=[world_to_camera_view(s,cam,screen.matrix_world@v.co)for v in screen.data.vertices]
 width=max(p.x for p in points)-min(p.x for p in points);height=max(p.y for p in points)-min(p.y for p in points)
 wide_monitor_lens=39*min(.88/width,.80/height)

with wave.open(str(ROOT/'assets/voz/narracao_completa.wav'))as w:sr=w.getframerate();voice=array.array('h',w.readframes(w.getnframes()))
def empty(name,loc=(0,0,0),parent=None):
 o=bpy.data.objects.new(name,None);s.collection.objects.link(o);o.parent=parent;o.location=loc;return o
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
def curve(keys,t):
 if t<=keys[0][0]:return keys[0][1]
 for (t0,v0),(t1,v1)in zip(keys,keys[1:]):
  if t<=t1:
   u=smooth((t-t0)/(t1-t0))
   if isinstance(v0,(float,int)):return v0+(v1-v0)*u
   return tuple(x+(y-x)*u for x,y in zip(v0,v1))
 return keys[-1][1]
def talk(t):
 t=math.floor(t*8)/8;v=voice[int(t*sr):int((t+.065)*sr)];return sum((x/32768)**2 for x in v)/max(1,len(v))>.0007
def toward(rig,point):
 p=rig.pose.bones['head'];bpy.context.view_layer.update();m=p.matrix.copy();wq=rig.matrix_world.to_quaternion();fwd=(wq@m.to_quaternion()@rest['head'].inverted())@Vector((0,-1,0));v=Vector(point)-(rig.matrix_world@m.translation);ang=math.atan2(v.y,v.x)-math.atan2(fwd.y,fwd.x);delta=wq.inverted()@Quaternion((0,0,1),ang)@wq
 p.matrix=Matrix.LocRotScale(m.translation,delta@m.to_quaternion(),m.to_scale());bpy.context.view_layer.update();q=p.rotation_quaternion.copy();p.rotation_quaternion=(base2 if rig.name=='COCKPIT | Dery rig'else base)['head'];bpy.context.view_layer.update();return q
head_cam=toward(r,(2.1,-.85,1.65));head_final=toward(r,(1.25,-1.25,1.56));head_side=toward(r,(1.8,-.45,1.55));head_monitor=toward(r,(.11,-.80,1.30))
shoulders={side:r.matrix_world@r.pose.bones['arm_'+side].head for side in ['R','L']};front=Vector((math.sin(.6),-math.cos(.6),0));up=Vector((0,0,1))


Rkeys=[(0,(.17,.10,-.30,0)),(3.8,(.17,.10,-.30,0)),(4.1,(.24,.08,-.15,.75)),(4.8,(.24,.08,-.15,.75)),(5.4,(.17,.10,-.30,0)),(14,(.17,.10,-.30,0)),(14.35,(.23,.11,-.17,.85)),(15.35,(.23,.11,-.17,.85)),(16.2,(.17,.10,-.30,0)),(23.9,(.17,.10,-.30,0)),(24.3,(.16,.08,-.24,.3)),(25.25,(.16,.08,-.24,.3)),(26.35,(.17,.10,-.30,0))]
Lkeys=[(0,(.19,.10,-.29,0)),(15.0,(.19,.10,-.29,0)),(15.3,(.20,.12,-.24,.3)),(15.75,(.20,.12,-.24,.3)),(16.2,(.19,.10,-.29,0)),(24.2,(.19,.10,-.29,0)),(24.6,(.17,.10,-.25,.25)),(25.5,(.17,.10,-.25,.25)),(26.36,(.19,.10,-.29,0))]
orient={}
for side in ['R','L']:
 o=empty('ACTING | '+side+' palm');o.rotation_mode='QUATERNION';orient[side]=o;c=r.pose.bones['hand_'+side].constraints.new('COPY_ROTATION');c.target=o;c.owner_space='WORLD';c.target_space='WORLD'
objects=[]
def box(name,loc,size,mat,parent=None):
 o=H.box('COCKPIT | '+name,loc,size,mat,parent);objects.append(o);return o
def graphic(name,filename):
 m=H.material('COCKPIT | '+name,lit=False);nt=m.node_tree;tx=nt.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(ROOT/'assets/memes'/filename),check_existing=True);tx.interpolation='Closest';nt.links.new(tx.outputs['Color'],next(n for n in nt.nodes if n.type=='EMISSION').inputs['Color']);return m
# Small garage shell, without the car or the obstructing central foreground pillar.
with bpy.data.libraries.load(str(REPO/'assets/cenarios/garagem_driver/Garagem_Driver.blend'))as(src,dst):
 dst.objects=[n for n in src.objects if n.startswith('GARAGE |')and n!='GARAGE | reusable origin']
for o in dst.objects:
 if o.type=='MESH':s.collection.objects.link(o)
bpy.context.view_layer.update()
for o in dst.objects:
 if o.type!='MESH':continue
 mw=o.matrix_world.copy()
 if abs(mw.translation.x)<.6 and mw.translation.y<-1:
  bpy.data.objects.remove(o,do_unlink=True);continue
 o.parent=None;o.matrix_world=Matrix.Translation((20,0,0))@mw;o.animation_data_clear();o.hide_render=False;o.name=o.name.replace('GARAGE |','COCKPIT | garage')
 for m in list(o.modifiers):
  if m.type=='NODES':o.modifiers.remove(m)
 if 'floor'in o.name:o.location.z=-.06
 if 'back wall'in o.name:o.location.y=1.8
 objects.append(o)
metal=H.material('COCKPIT | shell graphite',(.065,.10,.13),lit=False);edge=H.material('COCKPIT | pink trim',(.53,.13,.33),lit=False);cyan=H.material('COCKPIT | cyan trim',(.13,.46,.55),lit=False);dark=H.material('COCKPIT | seat fabric',(.022,.037,.048),lit=False)
local=empty('COCKPIT | local origin',(20,.10,0));local.rotation_euler.z=.6
box('seat',(0,0,.49),(.56,.52,.12),dark,local);box('seat back',(0,.25,1.0),(.64,.13,1.0),dark,local)
box('headrest',(0,.27,1.48),(.38,.15,.30),dark,local)
for x in [-.29,.29]:
 box('seat side trim',(x,.175,1.0),(.035,.025,.92),cyan,local)
 box('armrest',(x,-.01,.78),(.09,.43,.08),metal,local)
for x in [-.18,.18]:
 for y in [-.15,.17]:box('seat leg',(x,y,.23),(.04,.04,.45),metal,local)
roots={};lateral=.80 if WIDE else .62;pw=.50 if WIDE else .36
for label,sign,filename in [('Left',-1,'painel_left.png'),('Right',1,'painel_right.png')]:
 root=empty('COCKPIT | '+label+' panel root',parent=local);roots[label]=root;x=sign*lateral
 box(label+' screen case',(x,-.48,1.05),(pw+.06,.14,.42),metal,root)
 box(label+' screen edge',(x,-.558,1.05),(pw+.03,.018,.39),edge if sign<0 else cyan,root)
 mat=graphic(label+' instrument',filename);o=H.quad('COCKPIT | '+label+' picture',[(x-pw/2,-.572,.89),(x+pw/2,-.572,.89),(x+pw/2,-.572,1.21),(x-pw/2,-.572,1.21)],mat,parent=root);objects.append(o)
 fx=sign*(1.03 if WIDE else .86);half=abs(fx)/2
 box(label+' upright',(fx,-.79,1.17),(.10,.13,1.62),metal,root)
 box(label+' upright trim',(fx-sign*.055,-.863,1.17),(.025,.012,1.42),edge if sign<0 else cyan,root)
 box(label+' top frame',(sign*half,-.79,1.94),(abs(fx),.13,.12),metal,root)
 box(label+' lower frame',(sign*half,-.79,.61),(abs(fx),.13,.09),metal,root)
# Fixed normal pilot portrait keeps the cockpit reveal consistent.
box('rear frame',(1.0,.70,1.48),(1.48,.10,.93),metal,local)
o=H.quad('COCKPIT | rear picture',[(.29,.641,1.06),(1.71,.641,1.06),(1.71,.641,1.90),(.29,.641,1.90)],graphic('pilot reference','piloto_poster.png'),parent=local);objects.append(o)
r2=r.copy();r2.data=r.data.copy();r2.name='COCKPIT | Dery rig';s.collection.objects.link(r2);r2.animation_data_clear();mw=r.matrix_world.copy();mw.translation.x+=20;r2.parent=None;r2.matrix_world=mw
for p in r2.pose.bones:
 p.rotation_quaternion=base[p.name]
 for c in list(p.constraints):p.constraints.remove(c)
for p in r2.pose.bones:
 kw={}if p.parent is None else dict(parent_matrix=seated_pose[p.parent.name],parent_matrix_local=p.parent.bone.matrix_local)
 p.matrix_basis=p.bone.convert_local_to_pose(seated_pose[p.name],p.bone.matrix_local,invert=True,**kw)
bpy.context.view_layer.update();basis2={p.name:p.matrix_basis.copy()for p in r2.pose.bones};base2={p.name:p.rotation_quaternion.copy()for p in r2.pose.bones}
a2=a.copy();a2.data=a.data.copy();a2.name='COCKPIT | Dery';s.collection.objects.link(a2);a2.animation_data_clear();a2.parent=r2;a2.matrix_parent_inverse=Matrix.Identity(4);a2.matrix_basis=Matrix.Identity(4)
for m in list(a2.modifiers):
 if m.type=='NODES':a2.modifiers.remove(m)
 elif m.type=='ARMATURE':m.object=r2
install_faces(a2);nt=a2.data.materials[1].node_tree;illum=neutral_light(nt)
for n in list(nt.nodes):
 if n.type=='VERTEX_COLOR'and n.layer_name=='PS1FaceLightFit':
  for link in list(n.outputs['Color'].links):nt.links.new(illum,link.to_socket)
a2.data.materials[1]['DeryNeutralLight']=True;precision(a2,True)

for o in objects:precision(o)
head_cockpit=toward(r2,(21.7,-2.5,1.75));head_close=toward(r2,(21.4,-2.1,1.65))
left_point=local.matrix_world@Vector((-.9,-.45,1.10));right_point=local.matrix_world@Vector((.9,-.45,1.10));poster_point=local.matrix_world@Vector((1.0,.70,1.48))
head_left=toward(r2,left_point);head_right=toward(r2,right_point);head_poster=head_close.slerp(toward(r2,poster_point),.35)
bpy.context.view_layer.update();shoulders2={side:r2.matrix_world@r2.pose.bones['arm_'+side].head for side in ['R','L']};w2={};p2={}
for side in ['R','L']:
 w2[side]=empty('COCKPIT | '+side+' wrist');ik=r2.pose.bones['forearm_'+side].constraints.new('IK');ik.target=w2[side];ik.chain_count=2;ik.use_stretch=False
 p2[side]=empty('COCKPIT | '+side+' palm');p2[side].rotation_mode='QUATERNION';c=r2.pose.bones['hand_'+side].constraints.new('COPY_ROTATION');c.target=p2[side];c.owner_space='WORLD';c.target_space='WORLD'
CR=[(0,(.17,.10,-.30,0)),(26.36,(.17,.10,-.30,0)),(26.7,(.23,.12,-.15,.8)),(27.35,(.23,.12,-.15,.8)),(28.25,(.17,.10,-.30,0)),(31.8,(.17,.10,-.30,0)),(32.2,(.22,.10,-.16,.7)),(33.2,(.22,.10,-.16,.7)),(34,(.17,.10,-.30,0)),(35.8,(.17,.10,-.30,0)),(36.2,(.22,.08,-.18,.7)),(36.9,(.22,.08,-.18,.7)),(37.8,(.17,.10,-.30,0)),(39.5,(.17,.10,-.30,0)),(39.85,(.20,.09,-.21,.45)),(40.55,(.20,.09,-.21,.45)),(41.5,(.17,.10,-.30,0))]
CL=[(0,(.19,.10,-.29,0)),(29.9,(.19,.10,-.29,0)),(30.25,(.25,.11,-.14,.85)),(30.95,(.25,.11,-.14,.85)),(31.8,(.19,.10,-.29,0)),(34.3,(.19,.10,-.29,0)),(34.6,(.20,.12,-.23,.4)),(35.0,(.20,.12,-.23,.4)),(35.8,(.19,.10,-.29,0)),(41.9,(.19,.10,-.29,0))]
for marker in list(s.timeline_markers):s.timeline_markers.remove(marker)
for sh in info['shots']:s.timeline_markers.new(f"{sh['id']:02d} | {sh['kind']} | {sh['mood']}",frame=sh['start'])
faces={'room':[],'cockpit':[]}
for f in range(1,N+1):
 t=(f-1)/24;sh=next(x for x in info['shots']if x['start']<=f<=x['end']);mood=sh['mood'];u=(f-sh['start'])/max(1,sh['end']-sh['start']);speaking=talk(t)
 if 23.9<=t<26.36:
  tt=math.floor(t*8)/8;v=voice[int(tt*sr):int((tt+.065)*sr)];speaking=sum((x/32768)**2 for x in v)/max(1,len(v))>.00012
 for name,q in base.items():r.pose.bones[name].rotation_quaternion=q
 gaze=curve([(0,.8),(3.8,.8),(4.1,0),(5.4,0),(14,.3),(14.4,0),(16.2,0),(23.9,0),(24.4,.25),(25.1,.25),(26.36,0)],t)
 hq=(head_side if mood=='whisper'else head_cam).slerp(head_monitor,gaze)
 tilt=curve([(0,0),(4.1,-.025),(4.8,-.025),(5.4,0),(14.3,.04),(15.4,.04),(16.2,0),(23.9,.015),(24.4,.055),(25.4,.055),(26.36,0)],t)
 r.pose.bones['head'].rotation_quaternion=hq@(rest['head'].inverted()@Quaternion((0,1,0),tilt)@rest['head'])
 lean=curve([(0,0),(4.1,-.025),(4.8,-.025),(5.4,0),(14,0),(14.4,.06),(15.4,.06),(16.2,0),(23.9,0),(24.3,-.05),(25.5,-.05),(26.36,0)],t)
 r.pose.bones['upper_chest'].rotation_quaternion@=rest['upper_chest'].inverted()@Quaternion((1,0,0),lean)@rest['upper_chest']
 for side,sign,keys in [('R',-1,Rkeys),('L',1,Lkeys)]:
  fw,ou,z,roll=curve(keys,t);out=Vector((math.cos(.6)*sign,math.sin(.6)*sign,0));w=bpy.data.objects['R3 | '+side+' wrist'];w.location=shoulders[side]+front*fw+out*ou+up*z;H.record(w,'location',f)
  direction=(front*.75+up*(-.75+2.4*smooth((z+.29)/.33))).normalized();orient[side].rotation_quaternion=direction.to_track_quat('Y','Z')@Quaternion((0,1,0),sign*roll);H.record(orient[side],'rotation_quaternion',f)
 for p in r.pose.bones:H.record(p,'rotation_quaternion',f)
 face=(12 if speaking else 20)if t<14 else(16 if speaking else 18)
 if any(b<=t<b+.083 for b in [4.9,15.7,25.1]):face=10
 a['PS1_face_id']=face;a.keyframe_insert(data_path='["PS1_face_id"]',frame=f)
 if not faces['room']or faces['room'][-1]['id']!=face:faces['room'].append(dict(frame=f,id=face))
 for name,basis in basis2.items():r2.pose.bones[name].matrix_basis=basis
 hq2=head_close if mood in ['knowing','final']else head_cockpit
 glance=curve([(0,0),(26.36,0),(26.9,.45),(27.4,.45),(28.3,0),(29.9,0),(30.4,.45),(31.1,.45),(31.8,0),(33.7,0),(34.45,.35),(34.8,.35),(35.3,0),(35.8,.2),(36.3,0),(39.5,.15),(40.0,0),(41.9,0)],t)
 targethead=head_poster if t>=35 else head_right if 29.9<=t<31.8 else head_left
 r2.pose.bones['head'].rotation_quaternion=hq2.slerp(targethead,glance)
 nod=curve([(0,0),(26.7,-.025),(27.4,-.025),(28.3,0),(30.2,-.025),(31.1,-.025),(31.8,0),(34.3,.02),(34.7,.05),(35.0,.02),(35.8,0),(36.3,-.025),(37.1,-.025),(38.1,0),(39.8,.025),(40.2,-.015),(40.8,0)],t)
 r2.pose.bones['upper_chest'].rotation_quaternion@=rest['upper_chest'].inverted()@Quaternion((1,0,0),nod)@rest['upper_chest']
 for side,sign,keys in [('R',-1,CR),('L',1,CL)]:
  fw,ou,z,roll=curve(keys,t);out=Vector((math.cos(.6)*sign,math.sin(.6)*sign,0));w2[side].location=shoulders2[side]+front*fw+out*ou+up*z;H.record(w2[side],'location',f)
  direction=(front*.75+up*(-.75+2.4*smooth((z+.29)/.33))).normalized();p2[side].rotation_quaternion=direction.to_track_quat('Y','Z')@Quaternion((0,1,0),sign*roll);H.record(p2[side],'rotation_quaternion',f)
 for p in r2.pose.bones:H.record(p,'rotation_quaternion',f)
 face2=(12 if speaking else 13)if t<31.8 else(3 if speaking else 2)if t<35.8 else(16 if speaking else 4)
 if any(b<=t<b+.083 for b in [27.6,30.9,37.6,40.6]):face2=10
 a2['PS1_face_id']=face2;a2.keyframe_insert(data_path='["PS1_face_id"]',frame=f)
 if not faces['cockpit']or faces['cockpit'][-1]['id']!=face2:faces['cockpit'].append(dict(frame=f,id=face2))
 amount=curve([(0,0),(34.3,0),(34.95,1.65),(41.9,1.65)],t)
 for label,sign in [('Left',-1),('Right',1)]:roots[label].location.x=sign*amount;H.record(roots[label],'location',f)
 if sh['kind']=='cockpit':
  if mood in ['knowing','final']:cam.location=(21.4,-2.1,1.65);target=Vector((20,.1,1.32));lens=54
  elif mood=='opening':cam.location=(22.3,-2.0,1.80);target=local.matrix_world@Vector((.25,0,1.15));lens=35 if WIDE else 25
  else:cam.location=(21.58,-2.21,1.65);target=Vector((20,.1,1.14));lens=35 if WIDE else 24
 elif sh['kind']=='monitor':cam.location=(1.15,.28,1.55);target=Vector((.1095,-.7959,1.262));lens=wide_monitor_lens if WIDE else 39
 elif mood=='whisper':cam.location=(1.75,-.50,1.54);target=Vector((0,.10,1.40));lens=64
 else:cam.location=(2.1-.025*u,-.85+.015*u,1.65);target=Vector((0,.10,1.18));lens=42
 cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;H.record(cam,'location',f);H.record(cam,'rotation_euler',f);H.record(cam.data,'lens',f)
H.commit_curves()
for obj in [a,a2]:
 for fc in obj.animation_data.action.fcurves:
  for k in fc.keyframe_points:k.interpolation='CONSTANT'
(ROOT/'face_cues.json').write_text(json.dumps(faces,indent=2));(ROOT/'acting_cues.json').write_text(json.dumps(dict(method='Distinct phrase gestures, low-amplitude whispered aside, alternating cockpit presentation, a single outward panel slide and knowing ending. Original seated support remains fixed.',room_right=Rkeys,room_left=Lkeys,cockpit_right=CR,cockpit_left=CL,panel_slide_seconds=[34.3,34.95],reference='Private gesture reference retained from episode 007; not republished.'),indent=2))
s['DeryPS1Look']=f'{405 if WIDE else 128}x228 seam-safe geometry precision; Closest textures; 5-bit RGB and ordered dither at export';s['DeryFormats']='9:16 and 16:9 with independent cameras and graphic layouts'
s.sequence_editor_create().sequences.new_sound('VOZ | supplied recording',str(ROOT/'assets/voz/narracao_mix.wav'),channel=1,frame_start=1)
s.frame_set(90);bpy.data.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();(ROOT/'output').mkdir(exist_ok=True);dest=ROOT/'output'/('Dery_DVa_Master_16x9.blend'if WIDE else'Dery_DVa.blend');bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
for t in [4.6,15.0,24.8,27.1,30.6,34.32,34.8,36.5,40.2]:
 f=round(t*24)+1;cockpit=next(x for x in info['shots']if x['start']<=f<=x['end'])['kind']=='cockpit'
 for o in s.objects:
  if o.type=='MESH':o.hide_render=(not cockpit)if o.name.startswith('COCKPIT |')else cockpit
 s.frame_set(f);s.render.filepath=str(ROOT/f"output/preview_{'wide_'if WIDE else ''}{f:04d}.png");bpy.ops.render.render(write_still=True)
print('DVA_SCENE_READY',flush=True)
