"""Phrase-specific performance, discrete faces, PS1 precision and a two-person interview with one supplied voice."""
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


Rkeys=[(0,(.17,.10,-.30,0)),(1.0,(.17,.10,-.30,0)),(1.28,(.23,.08,-.16,.7)),(1.95,(.23,.08,-.16,.7)),(2.4,(.17,.10,-.30,0)),(7.88,(.17,.10,-.30,0)),(8.2,(.17,.10,-.23,.3)),(9.3,(.17,.10,-.30,0)),(13.15,(.17,.10,-.30,0)),(13.55,(.16,.10,-.32,0)),(14,(.16,.10,-.32,0))]
Lkeys=[(0,(.19,.10,-.29,0)),(7.88,(.19,.10,-.29,0)),(8.15,(.25,.11,-.15,.8)),(8.7,(.25,.11,-.15,.8)),(9.4,(.19,.10,-.29,0)),(13.15,(.19,.10,-.29,0)),(13.6,(.18,.10,-.31,0)),(14,(.18,.10,-.31,0))]
orient={};wrists={side:bpy.data.objects['R3 | '+side+' wrist']for side in ['R','L']}
for side in ['R','L']:
 o=empty('ACTING | '+side+' palm');o.rotation_mode='QUATERNION';orient[side]=o;c=r.pose.bones['hand_'+side].constraints.new('COPY_ROTATION');c.target=o;c.owner_space='WORLD';c.target_space='WORLD'
objects=[]
def box(name,loc,size,mat,parent=None):
 o=H.box('INTERVIEW | '+name,loc,size,mat,parent);objects.append(o);return o
# Reuse the meeting-room shell, leaving its table, flags and microphone in the old asset.
with bpy.data.libraries.load(str(REPO/'assets/cenarios/sala_reuniao/Sala_Reuniao.blend'))as(src,dst):
 dst.objects=[n for n in src.objects if n.startswith(('MEETING | floor','MEETING | back wall','MEETING | skirting','MEETING | wall seam'))]
for o in dst.objects:s.collection.objects.link(o)
bpy.context.view_layer.update()
for o in dst.objects:
 mw=o.matrix_world.copy();o.parent=None;o.matrix_world=Matrix.Translation((20,0,0))@mw;o.animation_data_clear();o.hide_render=False;o.name=o.name.replace('MEETING |','INTERVIEW | shell')
 for m in list(o.modifiers):
  if m.type=='NODES':o.modifiers.remove(m)
 objects.append(o)
metal=H.material('INTERVIEW | metal',(.10,.14,.16),lit=False);dark=H.material('INTERVIEW | chair cloth',(.025,.043,.055),lit=False);gold=H.material('INTERVIEW | gold',(.68,.46,.08),lit=False)
# A fixed normal reference stays on the rear wall; no hand-to-hand prop transfer.
box('portrait frame',(20,1.47,1.72),(1.65,.09,.97),metal)
mat=H.material('INTERVIEW | normal Tracer reference',lit=False);nt=mat.node_tree;tx=nt.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(ROOT/'assets/memes/tracer_retrato.png'));tx.interpolation='Closest';nt.links.new(tx.outputs['Color'],next(n for n in nt.nodes if n.type=='EMISSION').inputs['Color'])
o=H.quad('INTERVIEW | reference picture',[(19.2,1.415,1.27),(20.8,1.415,1.27),(20.8,1.415,2.17),(19.2,1.415,2.17)],mat);objects.append(o)
box('wall accent',(20,1.55,.18),(4.4,.025,.035),gold)
def seated_clone(label,x,yaw):
 rig=r.copy();rig.data=r.data.copy();rig.name='INTERVIEW | '+label+' rig';s.collection.objects.link(rig);rig.animation_data_clear();mw=Matrix.Rotation(yaw-.6,4,'Z')@r.matrix_world;mw.translation.x=x;mw.translation.y=.10;rig.parent=None;rig.matrix_world=mw
 for p in rig.pose.bones:
  p.rotation_quaternion=base[p.name]
  for c in list(p.constraints):p.constraints.remove(c)
 avatar=a.copy();avatar.data=a.data.copy();avatar.name='INTERVIEW | '+label;s.collection.objects.link(avatar);avatar.animation_data_clear();avatar.parent=rig;avatar.matrix_parent_inverse=Matrix.Identity(4);avatar.matrix_basis=Matrix.Identity(4)
 for m in list(avatar.modifiers):
  if m.type=='NODES':avatar.modifiers.remove(m)
  elif m.type=='ARMATURE':m.object=rig
 install_faces(avatar);nt=avatar.data.materials[1].node_tree;illum=neutral_light(nt)
 for n in list(nt.nodes):
  if n.type=='VERTEX_COLOR'and n.layer_name=='PS1FaceLightFit':
   for link in list(n.outputs['Color'].links):nt.links.new(illum,link.to_socket)
 avatar.data.materials[1]['DeryNeutralLight']=True;precision(avatar,True)
 chair=empty('INTERVIEW | '+label+' chair',(x,.10,0));chair.rotation_euler.z=yaw
 box(label+' seat',(0,0,.49),(.47,.44,.12),dark,chair);box(label+' back',(0,.24,.94),(.48,.11,.76),dark,chair)
 for xx in [-.18,.18]:
  for yy in [-.15,.17]:box(label+' chair leg',(xx,yy,.23),(.04,.04,.45),metal,chair)
 bpy.context.view_layer.update();sh={side:rig.matrix_world@rig.pose.bones['arm_'+side].head for side in ['R','L']};w={};palm={}
 for side in ['R','L']:
  w[side]=empty('INTERVIEW | '+label+' '+side+' wrist');ik=rig.pose.bones['forearm_'+side].constraints.new('IK');ik.target=w[side];ik.chain_count=2;ik.use_stretch=False
  palm[side]=empty('INTERVIEW | '+label+' '+side+' palm');palm[side].rotation_mode='QUATERNION';c=rig.pose.bones['hand_'+side].constraints.new('COPY_ROTATION');c.target=palm[side];c.owner_space='WORLD';c.target_space='WORLD'
 return dict(rig=rig,avatar=avatar,shoulders=sh,wrists=w,palms=palm,yaw=yaw,label=label)
host=seated_clone('Host',19.4,.95);guest=seated_clone('Guest',20.6,-.95)
for o in objects:precision(o)
host['to_other']=toward(host['rig'],(20.6,.10,1.48));host['to_cam']=toward(host['rig'],(20.65,-1.8,1.65));guest['to_other']=toward(guest['rig'],(19.4,.10,1.48));guest['to_cam']=toward(guest['rig'],(19.35,-1.8,1.65))
HR=[(0,(.17,.10,-.30,0)),(13.9,(.17,.10,-.30,0)),(14.15,(.23,.09,-.17,.7)),(14.7,(.23,.09,-.17,.7)),(15.2,(.17,.10,-.30,0)),(17.8,(.17,.10,-.30,0)),(18.1,(.25,.07,-.13,.85)),(18.85,(.25,.07,-.13,.85)),(19.65,(.17,.10,-.30,0)),(20.5,(.17,.10,-.30,0)),(20.85,(.22,.08,-.17,.65)),(21.35,(.22,.08,-.17,.65)),(22.1,(.17,.10,-.30,0))]
HL=[(0,(.19,.10,-.29,0)),(20.85,(.19,.10,-.29,0)),(21.1,(.19,.11,-.23,.25)),(21.6,(.19,.10,-.29,0))]
GR=[(0,(.16,.09,-.32,0)),(16.5,(.16,.09,-.32,0)),(16.8,(.20,.08,-.23,.45)),(17.25,(.20,.08,-.23,.45)),(17.8,(.16,.09,-.32,0)),(19.9,(.16,.09,-.32,0)),(20.1,(.17,.09,-.28,.2)),(20.5,(.16,.09,-.32,0)),(21.7,(.16,.09,-.32,0)),(22.1,(.15,.09,-.34,0)),(25.1,(.15,.09,-.34,0))]
GL=[(0,(.18,.09,-.31,0)),(25.1,(.18,.09,-.31,0))]
def perform(rig,sh,w,palms,yaw,kr,kl,hq,lean,f,t):
 for name,q in base.items():rig.pose.bones[name].rotation_quaternion=q
 rig.pose.bones['head'].rotation_quaternion=hq
 rig.pose.bones['upper_chest'].rotation_quaternion@=rest['upper_chest'].inverted()@Quaternion((1,0,0),lean)@rest['upper_chest']
 fwvec=Vector((math.sin(yaw),-math.cos(yaw),0))
 for side,sign,keys in [('R',-1,kr),('L',1,kl)]:
  fw,ou,z,roll=curve(keys,t);out=Vector((math.cos(yaw)*sign,math.sin(yaw)*sign,0));w[side].location=sh[side]+fwvec*fw+out*ou+up*z;H.record(w[side],'location',f)
  direction=(fwvec*.75+up*(-.75+2.4*smooth((z+.29)/.33))).normalized();palms[side].rotation_quaternion=direction.to_track_quat('Y','Z')@Quaternion((0,1,0),sign*roll);H.record(palms[side],'rotation_quaternion',f)
 for p in rig.pose.bones:H.record(p,'rotation_quaternion',f)
for marker in list(s.timeline_markers):s.timeline_markers.remove(marker)
for sh in info['shots']:s.timeline_markers.new(f"{sh['id']:02d} | {sh['kind']} | {sh['mood']}",frame=sh['start'])
faces={'room':[],'host':[],'guest':[]}
def face_key(obj,role,face,f):
 obj['PS1_face_id']=face;obj.keyframe_insert(data_path='["PS1_face_id"]',frame=f)
 if not faces[role]or faces[role][-1]['id']!=face:faces[role].append(dict(frame=f,id=face))
for f in range(1,N+1):
 t=(f-1)/24;sh=next(x for x in info['shots']if x['start']<=f<=x['end']);u=(f-sh['start'])/max(1,sh['end']-sh['start']);mood=sh['mood'];speaking=talk(t)
 gaze=curve([(0,.8),(1,.8),(1.3,0),(2.4,0),(7.88,.2),(8.2,0),(9.4,0),(13.15,.25),(13.5,0),(14,0)],t)
 tilt=curve([(0,0),(1.25,-.025),(1.9,-.025),(2.4,0),(8.15,-.035),(8.7,-.035),(9.4,0),(13.15,.04),(13.65,.04),(14,0)],t)
 hq=head_cam.slerp(head_monitor,gaze)@(rest['head'].inverted()@Quaternion((0,1,0),tilt)@rest['head'])
 lean=curve([(0,0),(1.3,-.025),(1.9,-.025),(2.4,0),(8.15,-.02),(8.8,-.02),(9.4,0),(13.15,0),(13.6,.065),(14,.065)],t)
 perform(r,shoulders,wrists,orient,.6,Rkeys,Lkeys,hq,lean,f,t)
 face=(12 if speaking else 20)if t<13.15 else(16 if speaking else 18)
 if any(b<=t<b+.083 for b in [1.95,8.8,13.65]):face=10
 face_key(a,'room',face,f)
 hhead=host['to_other'].slerp(host['to_cam'],curve([(0,.1),(13.9,.1),(14.5,0),(17.8,0),(19.6,0),(20.5,.05),(21.6,.05),(25.1,0)],t))
 perform(host['rig'],host['shoulders'],host['wrists'],host['palms'],.95,HR,HL,hhead,curve([(0,0),(18.1,-.025),(18.8,-.025),(19.9,0),(20.7,-.015),(21.5,-.015),(22.3,0)],t),f,t)
 hf=(12 if speaking else 20)if t<17.8 else(3 if speaking else 2)if t<20.5 else(24 if speaking else 23)
 if any(b<=t<b+.083 for b in [14.8,19.4,21.3]):hf=10
 face_key(host['avatar'],'host',hf,f)
 ghead=guest['to_other'].slerp(guest['to_cam'],curve([(0,0),(13.9,0),(16.5,.1),(17.8,0),(21.7,0),(22.2,.4),(22.9,.4),(25.1,.4)],t))
 nod=curve([(0,0),(14.1,0),(14.35,.04),(14.6,-.025),(14.95,0),(16.5,0),(16.8,.055),(17.1,-.025),(17.45,0),(19.9,0),(20.15,.035),(20.4,0),(21.7,0),(22.3,.065),(25.1,.065)],t)
 ghead@=rest['head'].inverted()@Quaternion((1,0,0),nod)@rest['head']
 perform(guest['rig'],guest['shoulders'],guest['wrists'],guest['palms'],-.95,GR,GL,ghead,curve([(0,0),(16.8,-.02),(17.4,-.02),(18.1,0),(21.7,0),(22.2,.04),(25.1,.04)],t),f,t)
 gf=13 if t<21.7 else 15 if t<22.25 else 6
 if any(b<=t<b+.083 for b in [14.75,17.4,20.3]):gf=10
 face_key(guest['avatar'],'guest',gf,f)
 if sh['kind']=='interview':
  if mood=='wide':cam.location=(20,-3.5,1.65);target=Vector((20,.1,1.0 if WIDE else 1.2));lens=40 if WIDE else 30
  elif mood in ['host','followup']:cam.location=(20.65,-1.8,1.65);target=Vector((19.4,.10,1.35));lens=54
  else:cam.location=(19.35,-1.8,1.65);target=Vector((20.6,.10,1.35));lens=54
 elif sh['kind']=='monitor':cam.location=(1.15,.28,1.55);target=Vector((.1095,-.7959,1.262));lens=wide_monitor_lens if WIDE else 39
 elif mood=='sigh':cam.location=(1.8,-.45,1.55);target=Vector((0,.10,1.39));lens=60
 else:cam.location=(2.1-.025*u,-.85+.015*u,1.65);target=Vector((0,.10,1.18));lens=42
 cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;H.record(cam,'location',f);H.record(cam,'rotation_euler',f);H.record(cam.data,'lens',f)
H.commit_curves()
for obj in [a,host['avatar'],guest['avatar']]:
 for fc in obj.animation_data.action.fcurves:
  for k in fc.keyframe_points:k.interpolation='CONSTANT'
(ROOT/'face_cues.json').write_text(json.dumps(faces,indent=2));(ROOT/'acting_cues.json').write_text(json.dumps(dict(method='Phrase-led asymmetric gestures, seated interview with matching eyelines, silent guest nods and closed-mouth deadpan. No added response or periodic arm loop.',room_right=Rkeys,room_left=Lkeys,host_right=HR,host_left=HL,guest_right=GR,guest_left=GL,reference='Private gesture reference from episode 007; not republished.'),indent=2))
s['DeryPS1Look']=f'{405 if WIDE else 128}x228 seam-safe geometry precision; Closest textures; 5-bit RGB and ordered dither at export';s['DeryFormats']='9:16 and 16:9, separate camera and card layouts';s['GuestSilent']=True
s.sequence_editor_create().sequences.new_sound('VOZ | supplied recording',str(ROOT/'assets/voz/narracao_mix.wav'),channel=1,frame_start=1)
s.frame_set(45);bpy.data.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();(ROOT/'output').mkdir(exist_ok=True);dest=ROOT/'output'/('Dery_Tracer_Master_16x9.blend'if WIDE else'Dery_Tracer.blend');bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
def visibility(sh):
 interview=sh['kind']=='interview';m=sh['mood']
 for o in s.objects:
  if o.type!='MESH':continue
  o.hide_render=(not interview)if o.name.startswith('INTERVIEW |')else interview
  if interview and o.name=='INTERVIEW | Host'and m in ['guest','proud','final']:o.hide_render=True
  if interview and o.name=='INTERVIEW | Guest'and m in ['host','followup']:o.hide_render=True
for t in [1.6,8.5,13.5,14.4,17.1,18.7,20.2,21.1,22.5,24.6]:
 f=round(t*24)+1;sh=next(x for x in info['shots']if x['start']<=f<=x['end']);visibility(sh);s.frame_set(f);s.render.filepath=str(ROOT/f"output/preview_{'wide_'if WIDE else ''}{f:04d}.png");bpy.ops.render.render(write_still=True)
print('TRACER_SCENE_READY',flush=True)
