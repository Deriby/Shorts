"""Phrase-specific performance, discrete faces, PS1 precision and a fictional inspection room."""
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
 p.matrix=Matrix.LocRotScale(m.translation,delta@m.to_quaternion(),m.to_scale());bpy.context.view_layer.update();q=p.rotation_quaternion.copy();p.rotation_quaternion=base['head'];bpy.context.view_layer.update();return q
head_cam=toward(r,(2.1,-.85,1.65));head_final=toward(r,(1.25,-1.25,1.56));head_side=toward(r,(1.8,-.45,1.55));head_monitor=toward(r,(.11,-.80,1.30))
shoulders={side:r.matrix_world@r.pose.bones['arm_'+side].head for side in ['R','L']};front=Vector((math.sin(.6),-math.cos(.6),0));up=Vector((0,0,1))


# Preparation, stroke, hold and rest are distinct for every phrase and arm.
R=[(0,(.17,.10,-.30,0)),(1.60,(.17,.10,-.30,0)),(1.95,(.24,.08,-.16,.65)),(2.35,(.24,.08,-.16,.65)),(2.9,(.17,.10,-.30,0)),(4,(.17,.10,-.30,0)),(4.25,(.22,.09,-.19,.6)),(4.65,(.22,.09,-.19,.6)),(5,(.17,.10,-.30,0)),(13.68,(.17,.10,-.30,0)),(14.2,(.16,.10,-.32,0)),(18,(.16,.10,-.32,0)),(18.3,(.21,.07,-.18,.55)),(18.65,(.21,.07,-.18,.55)),(19.2,(.17,.10,-.30,0)),(20.9,(.17,.10,-.30,0)),(21.2,(.24,.08,-.16,.6)),(21.5,(.20,.09,-.23,.25)),(21.9,(.17,.10,-.30,0)),(26.5,(.17,.10,-.30,0)),(26.85,(.28,.10,-.085,.85)),(27.18,(.28,.10,-.085,.85)),(27.65,(.17,.10,-.30,0)),(30.3,(.17,.10,-.30,0)),(30.65,(.19,.10,-.22,.45)),(31.05,(.19,.10,-.22,.45)),(31.6,(.17,.10,-.30,0))]
L=[(0,(.19,.10,-.29,0)),(7.3,(.19,.10,-.29,0)),(7.65,(.24,.12,-.16,.75)),(8.3,(.24,.12,-.16,.75)),(9,(.19,.10,-.29,0)),(11.55,(.19,.10,-.29,0)),(11.95,(.25,.10,-.13,.8)),(12.5,(.25,.10,-.13,.8)),(13.2,(.19,.10,-.29,0)),(13.68,(.19,.10,-.29,0)),(14.2,(.18,.10,-.32,0)),(40,(.18,.10,-.32,0))]
orient={}
for side in ['R','L']:
 o=empty('ACTING | '+side+' palm');o.rotation_mode='QUATERNION';orient[side]=o;c=r.pose.bones['hand_'+side].constraints.new('COPY_ROTATION');c.name='ACTING | palm follow through';c.target=o;c.owner_space='WORLD';c.target_space='WORLD'
# Reusable inspection bay: baked-style emission colors keep the low-poly capture look.
wall=H.material('INSPECTION | slate walls',(.18,.19,.16),lit=False);floor=H.material('INSPECTION | carpet',(.075,.105,.11),lit=False);wood=H.material('INSPECTION | wood',(.28,.20,.095),lit=False);metal=H.material('INSPECTION | metal',(.10,.125,.13),lit=False);dark=H.material('INSPECTION | dark upholstery',(.025,.037,.045),lit=False);light=H.material('INSPECTION | trim',(.48,.53,.49),lit=False);green=H.material('INSPECTION | green',(.055,.34,.20),lit=False);red=H.material('INSPECTION | red',(.52,.09,.08),lit=False)
inspection_objs=[]
def box(name,loc,size,mat,parent=None):
 o=H.box('INSPECTION | '+name,loc,size,mat,parent);inspection_objs.append(o);return o
box('floor',(20,0,-.04),(9,8,.08),floor);box('back wall',(20,1.65,1.6),(9,.12,3.3),wall);box('skirting',(20,1.55,.16),(9,.07,.11),metal)
for x in [17.5,18.5,19.5,20.5,21.5,22.5]:box('wall seam',(x,1.57,1.65),(.023,.02,2.9),metal)
# The seated clone retains the original hip and leg pose, and original body mesh.
r2=r.copy();r2.data=r.data.copy();r2.name='INSPECTION | Dery rig';s.collection.objects.link(r2);r2.animation_data_clear();mw=r.matrix_world.copy();mw.translation.x+=20;r2.parent=None;r2.matrix_world=mw
for p in r2.pose.bones:
 p.rotation_quaternion=base[p.name]
 for c in list(p.constraints):p.constraints.remove(c)
a2=a.copy();a2.data=a.data.copy();a2.name='INSPECTION | Dery';s.collection.objects.link(a2);a2.animation_data_clear();a2.parent=r2;a2.matrix_parent_inverse=Matrix.Identity(4);a2.matrix_basis=Matrix.Identity(4)
for m in list(a2.modifiers):
 if m.type=='NODES':a2.modifiers.remove(m)
 elif m.type=='ARMATURE':m.object=r2
install_faces(a2);nt=a2.data.materials[1].node_tree;illum=neutral_light(nt)
for n in list(nt.nodes):
 if n.type=='VERTEX_COLOR'and n.layer_name=='PS1FaceLightFit':
  for link in list(n.outputs['Color'].links):nt.links.new(illum,link.to_socket)
a2.data.materials[1]['DeryNeutralLight']=True;precision(a2,True)
chair=empty('INSPECTION | chair support',(20,.10,0));chair.rotation_euler.z=.6
box('chair seat',(0,0,.49),(.47,.44,.12),dark,chair);box('chair back',(0,.24,.94),(.48,.11,.76),dark,chair)
for x in [-.18,.18]:
 for y in [-.15,.17]:box('chair leg',(x,y,.23),(.04,.04,.45),metal,chair)
# Table sits in front of the lap rather than cutting through the body.
box('table',(20,-.82,.665),(3.8,.64,.10),wood)
for x in [18.7,21.3]:box('table leg',(x,-.82,.31),(.09,.40,.62),metal)
# Projector image faces the camera; the same shot-aligned feed drives both screens.
box('projector bezel',(21.22,1.48,1.55),(2.10,.09,1.25),dark)
quad=H.quad('INSPECTION | projector image',[(20.22,1.42,.99),(22.22,1.42,.99),(22.22,1.42,2.115),(20.22,1.42,2.115)],screen.data.materials[0]);inspection_objs.append(quad)


# A front panel and sign turn the existing table bay into a comic inspection desk.
box('counter front',(20,-1.13,.35),(3.8,.08,.54),wood)
def graphic(name,path):
 mat=H.material('INSPECTION | '+name,lit=False);nt=mat.node_tree;tx=nt.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(ROOT/'assets/memes'/path),check_existing=True);tx.interpolation='Closest';em=next(n for n in nt.nodes if n.type=='EMISSION');nt.links.new(tx.outputs['Color'],em.inputs['Color']);return mat
sign=graphic('desk sign','inspection_sign.png'if WIDE else'inspection_sign_vertical.png');o=H.quad('INSPECTION | sign',([(18.95,-1.177,.19),(21.05,-1.177,.19),(21.05,-1.177,.52),(18.95,-1.177,.52)]if WIDE else[(20.2,-1.177,.12),(21.4,-1.177,.12),(21.4,-1.177,.60),(20.2,-1.177,.60)]),sign);inspection_objs.append(o)
card=graphic('inspection card','inspection_checked.png');o=H.quad('INSPECTION | paper checklist',[(20.38,-.94,.721),(20.84,-.94,.721),(20.84,-.68,.721),(20.38,-.68,.721)],card);inspection_objs.append(o)
# A stationary pedestal camera avoids hand/object contact and complex simulation.
pedestal=(18.93,-.27)
for i in range(3):
 angle=i*math.tau/3;p=(pedestal[0]+math.cos(angle)*.32,pedestal[1]+math.sin(angle)*.32,.04);o=H.beam('INSPECTION | tripod leg',(pedestal[0],pedestal[1],.43),p,.035,metal);inspection_objs.append(o)
o=H.cylinder('INSPECTION | tripod column',(pedestal[0],pedestal[1],.76),.026,.76,metal,vertices=8);inspection_objs.append(o)
filmhead=empty('INSPECTION | filming camera head',(pedestal[0],pedestal[1],1.20));camera_yaw=math.atan2(1.42-pedestal[1],21.22-pedestal[0])+math.pi/2;filmhead.rotation_euler.z=camera_yaw
box('camera body',(0,0,0),(.32,.25,.22),dark,filmhead);box('camera viewfinder',(.10,.17,.055),(.11,.12,.09),metal,filmhead)
o=H.cylinder('INSPECTION | camera lens',(0,-.18,0),.105,.16,metal,parent=filmhead,vertices=8,rot=(math.pi/2,0,0));inspection_objs.append(o)
o=H.cylinder('INSPECTION | camera glass',(0,-.267,0),.078,.013,green,parent=filmhead,vertices=8,rot=(math.pi/2,0,0));inspection_objs.append(o)
for obj in inspection_objs:precision(obj)
bpy.context.view_layer.update();head_inspect=toward(r2,(22,-3,1.8));head_tv=toward(r2,(21.3,1.35,1.55))
# The side screen is behind him; keep his turn modest instead of twisting 180 degrees.
head_tv=head_inspect.slerp(head_tv,.38)
shoulders2={side:r2.matrix_world@r2.pose.bones['arm_'+side].head for side in ['R','L']};w2={};p2={};front2=front.copy()
for side in ['R','L']:
 w2[side]=empty('INSPECTION | '+side+' wrist');ik=r2.pose.bones['forearm_'+side].constraints.new('IK');ik.target=w2[side];ik.chain_count=2;ik.use_stretch=False
 p2[side]=empty('INSPECTION | '+side+' palm');p2[side].rotation_mode='QUATERNION';c=r2.pose.bones['hand_'+side].constraints.new('COPY_ROTATION');c.target=p2[side];c.owner_space='WORLD';c.target_space='WORLD'

MR=[(0,(.17,.10,-.30,0)),(33.0,(.17,.10,-.30,0)),(33.4,(.21,.08,-.19,.4)),(34.2,(.21,.08,-.19,.4)),(34.9,(.17,.10,-.30,0)),(35.45,(.17,.10,-.30,0)),(35.8,(.26,.08,-.13,.9)),(36.15,(.26,.08,-.13,.9)),(36.7,(.17,.10,-.30,0)),(40,(.17,.10,-.30,0))]
ML=[(0,(.19,.10,-.29,0)),(37.8,(.19,.10,-.29,0)),(38.12,(.22,.12,-.20,.65)),(38.5,(.22,.12,-.20,.65)),(39.05,(.18,.10,-.31,0)),(40,(.18,.10,-.31,0))]
for m in list(s.timeline_markers):s.timeline_markers.remove(m)
for sh in info['shots']:s.timeline_markers.new(f"{sh['id']:02d} | {sh['kind']} | {sh['mood']}",frame=sh['start'])
face_events={'room':[],'inspection':[]}
for f in range(1,N+1):
 t=(f-1)/24;sh=next(x for x in info['shots']if x['start']<=f<=x['end']);mood=sh['mood'];u=(f-sh['start'])/max(1,sh['end']-sh['start']);speaking=talk(t)
 for name,q in base.items():r.pose.bones[name].rotation_quaternion=q
 gaze=curve([(0,.8),(1.55,.8),(1.9,0),(2.75,0),(4,.3),(4.4,0),(5.95,.6),(7.24,0),(11.64,0),(12.3,0),(13.68,0),(14.3,.55),(15,.25),(18,.45),(18.5,0),(19.36,0),(21,.5),(21.6,.25),(23.46,.7),(26.68,0),(27.65,.3),(30.3,.4),(30.8,0),(31.6,0)],t)
 hq=head_side if mood in ['sigh','sarcasm','chuckle']else head_cam;r.pose.bones['head'].rotation_quaternion=hq.slerp(head_monitor,gaze)
 tilt=curve([(0,0),(1.9,.045),(2.4,.045),(3,0),(11.64,0),(12.1,-.05),(12.8,-.05),(13.5,0),(14,.065),(15.3,.065),(18,.02),(18.5,-.03),(19.2,0),(26.68,0),(27.0,-.025),(27.55,.025),(28,0),(30.3,0),(30.7,.055),(31.2,.055),(31.6,0)],t)
 r.pose.bones['head'].rotation_quaternion@=rest['head'].inverted()@Quaternion((0,1,0),tilt)@rest['head']
 lean=curve([(0,0),(1.9,-.025),(2.4,-.025),(3.1,0),(11.64,0),(12.1,-.035),(13.1,-.035),(13.68,0),(14.15,.065),(15.3,.065),(18,.035),(18.7,.035),(19.36,0),(26.6,0),(26.9,-.03),(27.2,.025),(27.45,-.02),(27.7,0),(30.3,.025),(30.7,-.015),(31.25,.025),(31.6,0)],t)
 sway=curve([(0,0),(26.7,0),(26.9,.025),(27.1,-.025),(27.3,.025),(27.55,-.02),(27.8,0)],t)
 r.pose.bones['upper_chest'].rotation_quaternion@=rest['upper_chest'].inverted()@Quaternion((1,0,0),lean)@Quaternion((0,1,0),sway)@rest['upper_chest']
 for side,sign,keys in [('R',-1,R),('L',1,L)]:
  fw,ou,z,roll=curve(keys,t);outward=Vector((math.cos(.6)*sign,math.sin(.6)*sign,0));w=bpy.data.objects['R3 | '+side+' wrist'];w.location=shoulders[side]+front*fw+outward*ou+up*z;H.record(w,'location',f)
  direction=(front*.75+up*(-.75+2.4*smooth((z+.29)/.33))).normalized();orient[side].rotation_quaternion=direction.to_track_quat('Y','Z')@Quaternion((0,1,0),sign*roll);H.record(orient[side],'rotation_quaternion',f)
 for p in r.pose.bones:H.record(p,'rotation_quaternion',f)
 face=(12 if speaking else 20)if t<11.64 else(11 if speaking else 13)if t<13.68 else(16 if speaking else 4)if t<19.36 else(12 if speaking else 18)if t<23.46 else(12 if speaking else 20)if t<26.68 else(1 if speaking else 27)if t<30.3 else(3 if speaking else 2)
 if any(b<=t<b+.083 for b in [4.45,6.9,12.75,18.85,24.1,27.45,31.1]):face=10
 a['PS1_face_id']=face;a.keyframe_insert(data_path='["PS1_face_id"]',frame=f)
 if not face_events['room']or face_events['room'][-1]['id']!=face:face_events['room'].append(dict(frame=f,id=face))
 # The inspector starts overly serious, checks the sheet, then looks defeated.
 for name,q in base.items():r2.pose.bones[name].rotation_quaternion=q
 gaze2=curve([(0,0),(32.8,.6),(33.5,.6),(34.3,0),(35.42,0),(36.1,.15),(36.7,.4),(37.8,.4),(38.1,.3),(38.55,0),(40,0)],t)
 r2.pose.bones['head'].rotation_quaternion=head_inspect.slerp(head_tv,gaze2)
 nod=curve([(0,0),(35.42,0),(36,-.03),(36.5,0),(37,.07),(37.9,.07),(38.35,0),(39,.045),(40,.045)],t)
 r2.pose.bones['head'].rotation_quaternion@=rest['head'].inverted()@Quaternion((1,0,0),nod)@rest['head']
 lean2=curve([(0,0),(32.8,-.025),(34,-.025),(34.8,0),(35.8,-.025),(36.5,0),(38.1,0),(38.8,.045),(40,.045)],t)
 r2.pose.bones['upper_chest'].rotation_quaternion@=rest['upper_chest'].inverted()@Quaternion((1,0,0),lean2)@rest['upper_chest']
 for side,sign,keys in [('R',-1,MR),('L',1,ML)]:
  fw,ou,z,roll=curve(keys,t);out=Vector((math.cos(.6)*sign,math.sin(.6)*sign,0));w2[side].location=shoulders2[side]+front2*fw+out*ou+up*z;H.record(w2[side],'location',f)
  direction=(front2*.75+up*(-.75+2.4*smooth((z+.29)/.33))).normalized();p2[side].rotation_quaternion=direction.to_track_quat('Y','Z')@Quaternion((0,1,0),sign*roll);H.record(p2[side],'rotation_quaternion',f)
 for p in r2.pose.bones:H.record(p,'rotation_quaternion',f)
 face2=23 if t<35.42 else(24 if speaking else 7)if t<38.45 else 6
 a2['PS1_face_id']=face2;a2.keyframe_insert(data_path='["PS1_face_id"]',frame=f)
 if not face_events['inspection']or face_events['inspection'][-1]['id']!=face2:face_events['inspection'].append(dict(frame=f,id=face2))
 filmhead.rotation_euler=(curve([(0,0),(31.6,0),(32.65,.16),(40,.16)],t),0,camera_yaw);H.record(filmhead,'rotation_euler',f)
 if sh['kind']=='inspection':
  if mood=='camera':cam.location=(20.15,.8,1.5);target=Vector((18.96,-.25,1.15));lens=52
  elif mood=='final':cam.location=(21.35,-1.9,1.56);target=Vector((20,.10,1.38));lens=56
  else:cam.location=(22.0-.04*u,-3+.03*u,1.80);target=Vector((20.50,.1,1.02))if WIDE else Vector((20.05,-.05,.85));lens=34 if WIDE else 36
 elif sh['kind']=='monitor':cam.location=(1.15,.28,1.55);target=Vector((.1095,-.7959,1.262));lens=wide_monitor_lens if WIDE else 39
 elif mood in ['sigh','sarcasm','chuckle']:cam.location=(1.8,-.45,1.55);target=Vector((0,.10,1.39));lens=60
 else:cam.location=(2.1-.025*u,-.85+.015*u,1.65);target=Vector((0,.10,1.18));lens=42
 cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;H.record(cam,'location',f);H.record(cam,'rotation_euler',f);H.record(cam.data,'lens',f)
H.commit_curves()
for obj in [a,a2]:
 for fc in obj.animation_data.action.fcurves:
  for k in fc.keyframe_points:k.interpolation='CONSTANT'
(ROOT/'face_cues.json').write_text(json.dumps(face_events,indent=2));(ROOT/'acting_cues.json').write_text(json.dumps(dict(method='Phrase-specific preparation, holds, releases and rests. Single brief shoulder rhythm, not a periodic conversation loop.',right=R,left=L,inspection_right=MR,inspection_left=ML,reference='Gesture guidance retained from private episode 007 reference; no personal video published.'),indent=2))
s['DeryPS1Look']=f'{405 if WIDE else 128}x228 seam-safe vertex precision; 128px texture addressing; 5-bit RGB and ordered dithering at export';s['DeryFormats']='9:16 and 16:9 with independent cameras and media layouts.'
s.sequence_editor_create().sequences.new_sound('VOZ | supplied recording',str(ROOT/'assets/voz/narracao_mix.wav'),channel=1,frame_start=1)
s.frame_set(80);bpy.data.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();(ROOT/'output').mkdir(exist_ok=True);dest=ROOT/'output'/('Dery_ChunLi_Master_16x9.blend'if WIDE else'Dery_ChunLi.blend');bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
for t in [12.2,14.5,27.2,32.1,34.0,35.9,38.8]:
 f=round(t*24)+1;sh=next(x for x in info['shots']if x['start']<=f<=x['end']);inspection=sh['kind']=='inspection'
 for o in s.objects:
  if o.type=='MESH':o.hide_render=(not inspection)if o.name.startswith('INSPECTION |')else inspection
 s.frame_set(f);s.render.filepath=str(ROOT/f"output/preview_{'wide_'if WIDE else ''}{f:04d}.png");bpy.ops.render.render(write_still=True)
print('CHUNLI_SCENE_READY',flush=True)
