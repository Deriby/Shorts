"""Sonic: archive gestures, a single question-card burst and a quiet fan-horror arcade."""
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
 p.matrix=Matrix.LocRotScale(m.translation,delta@m.to_quaternion(),m.to_scale());bpy.context.view_layer.update();q=p.rotation_quaternion.copy();p.rotation_quaternion=base['head']if rig==r else Quaternion();bpy.context.view_layer.update();return q
head_cam=toward(r,(2.1,-.85,1.65));head_final=toward(r,(1.25,-1.25,1.56));head_side=toward(r,(1.8,-.45,1.55));head_monitor=toward(r,(.11,-.80,1.30))
shoulders={side:r.matrix_world@r.pose.bones['arm_'+side].head for side in ['R','L']};front=Vector((math.sin(.6),-math.cos(.6),0));up=Vector((0,0,1))



# Distinct phrase-led gestures: presentation, sigh, warning and reassurance.
R=[(0,(.17,.10,-.30,0)),(1.2,(.17,.10,-.30,0)),(1.55,(.24,.09,-.16,.65)),(2.2,(.24,.09,-.16,.65)),(3.0,(.17,.10,-.30,0)),(5.56,(.17,.10,-.30,0)),(5.9,(.22,.09,-.19,.55)),(6.45,(.22,.09,-.19,.55)),(7.2,(.17,.10,-.30,0)),(14.1,(.17,.10,-.30,0)),(14.5,(.20,.10,-.24,.35)),(15.15,(.20,.10,-.24,.35)),(16.3,(.17,.10,-.30,0)),(16.7,(.23,.09,-.18,.75)),(17.35,(.23,.09,-.18,.75)),(18.4,(.17,.10,-.30,0)),(21.6,(.17,.10,-.30,0)),(21.95,(.22,.08,-.20,.5)),(22.5,(.22,.08,-.20,.5)),(23.1,(.17,.10,-.30,0)),(23.7,(.17,.10,-.30,0)),(24.15,(.16,.10,-.32,0)),(25.2,(.16,.10,-.32,0))]
L=[(0,(.19,.10,-.29,0)),(6.15,(.19,.10,-.29,0)),(6.45,(.23,.10,-.17,.7)),(6.9,(.23,.10,-.17,.7)),(7.5,(.19,.10,-.29,0)),(14.1,(.19,.10,-.29,0)),(14.8,(.18,.11,-.27,.2)),(15.5,(.18,.11,-.27,.2)),(16.3,(.19,.10,-.29,0)),(21.6,(.19,.10,-.29,0)),(22.25,(.19,.12,-.25,.3)),(22.8,(.19,.12,-.25,.3)),(23.4,(.19,.10,-.29,0)),(25.2,(.19,.10,-.29,0))]
orient={}
for side in ['R','L']:
 o=empty('ACTING | '+side+' palm');o.rotation_mode='QUATERNION';orient[side]=o;c=r.pose.bones['hand_'+side].constraints.new('COPY_ROTATION');c.target=o;c.owner_space='WORLD';c.target_space='WORLD'
objects=[]
def box(name,loc,size,mat,parent=None):
 o=H.box('ARCADE | '+name,loc,size,mat,parent);objects.append(o);return o
dark=H.material('ARCADE | cabinet graphite',(.028,.035,.065),lit=False);metal=H.material('ARCADE | blue steel',(.08,.13,.20),lit=False);red=H.material('ARCADE | steady red',(.46,.035,.06),lit=False);blue=H.material('ARCADE | blue trim',(.07,.24,.32),lit=False);pale=H.material('ARCADE | buttons',(.44,.47,.43),lit=False)
# Only the existing garage walls and floor are reused; the car and boss UI stay behind.
with bpy.data.libraries.load(str(REPO/'assets/cenarios/garagem_driver/Garagem_Driver.blend'))as(src,dst):
 dst.objects=[n for n in src.objects if n.startswith(('GARAGE | floor','GARAGE | back wall','GARAGE | left wall'))]
for o in dst.objects:s.collection.objects.link(o)
bpy.context.view_layer.update()
for o in dst.objects:
 mw=o.matrix_world.copy();o.parent=None;o.matrix_world=Matrix.Translation((20,0,0))@mw;o.animation_data_clear();o.hide_render=False;o.name=o.name.replace('GARAGE |','ARCADE | shell')
 for m in list(o.modifiers):
  if m.type=='NODES':o.modifiers.remove(m)
 if 'back wall'in o.name:o.location.y=1.8
 objects.append(o)
box('platform',(20.55,.15,-.045),(3.9,2.8,.09),dark)
for x in [18.63,22.47]:box('platform trim',(x,.15,.004),(.035,2.7,.012),blue)
for x in [18.6,22.5]:
 box('wall strip',(x,1.68,1.5),(.09,.06,2.5),blue);box('wall strip base',(x,1.68,.2),(.28,.10,.10),metal)
cx=21.12
box('cabinet body',(cx,.40,.47),(.96,.72,.94),dark);box('kick panel',(cx,.027,.38),(.78,.025,.61),metal)
for xx in [cx-.48,cx+.48]:
 box('side fin',(xx,.40,1.27),(.07,.74,.75),dark);box('red edge',(xx,-.008,1.36),(.035,.035,.75),red)
box('control deck',(cx,-.04,.96),(1.02,.42,.10),metal)
box('joystick',(cx-.25,-.14,1.08),(.035,.035,.17),pale);box('joystick cap',(cx-.25,-.14,1.18),(.09,.09,.09),red)
for i in range(3):box('button '+str(i),(cx+.05+i*.12,-.17,1.03),(.075,.075,.025),red if i==0 else blue)
box('screen bezel',(cx,.18,1.40),(.94,.24,.66),dark)
box('marquee',(cx,.27,1.89),(1.03,.68,.23),metal);box('marquee red',(cx,-.079,1.89),(.88,.025,.11),red)
panel=H.material('ARCADE | authored horror menu',lit=False);pn=panel.node_tree;images=[]
for filename in ['terror_menu.png','terror_exit.png','terror_closed.png']:
 n=pn.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(ROOT/'assets/memes'/filename));n.interpolation='Closest';images.append(n)
selection=pn.nodes.new('ShaderNodeMixRGB');selection.name='ARCADE | exit selected';pn.links.new(images[0].outputs['Color'],selection.inputs[1]);pn.links.new(images[1].outputs['Color'],selection.inputs[2])
closed=pn.nodes.new('ShaderNodeMixRGB');closed.name='ARCADE | closed';pn.links.new(selection.outputs[0],closed.inputs[1]);pn.links.new(images[2].outputs['Color'],closed.inputs[2]);pn.links.new(closed.outputs[0],next(n for n in pn.nodes if n.type=='EMISSION').inputs['Color'])
o=H.quad('ARCADE | screen picture',[(cx-.42,.048,1.13),(cx+.42,.048,1.13),(cx+.42,.048,1.67),(cx-.42,.048,1.67)],panel);objects.append(o)
# Standing clone uses the previously validated castle pose without modifying the mesh.
r2=r.copy();r2.data=r.data.copy();r2.name='ARCADE | Dery rig';s.collection.objects.link(r2);r2.animation_data_clear();r2.parent=None;r2.rotation_mode='XYZ';r2.location=(20,-.25,0);r2.rotation_euler=(0,0,.2)
for p in r2.pose.bones:
 p.matrix_basis=Matrix.Identity(4)
 for c in list(p.constraints):p.constraints.remove(c)
a2=a.copy();a2.data=a.data.copy();a2.name='ARCADE | Dery';s.collection.objects.link(a2);a2.animation_data_clear();a2.parent=r2;a2.matrix_parent_inverse=Matrix.Identity(4);a2.matrix_basis=Matrix.Identity(4)
for m in list(a2.modifiers):
 if m.type=='NODES':a2.modifiers.remove(m)
 elif m.type=='ARMATURE':m.object=r2
install_faces(a2);nt=a2.data.materials[1].node_tree;illum=neutral_light(nt)
for n in list(nt.nodes):
 if n.type=='VERTEX_COLOR'and n.layer_name=='PS1FaceLightFit':
  for link in list(n.outputs['Color'].links):nt.links.new(illum,link.to_socket)
a2.data.materials[1]['DeryNeutralLight']=True;precision(a2,True)
for obj in objects:precision(obj)
head_arcade=toward(r2,(21.2,-3.4,1.96));head_close=toward(r2,(21.1,-2.2,1.82));head_screen=toward(r2,(cx,.05,1.4))
bpy.context.view_layer.update();shoulders2={side:r2.matrix_world@r2.pose.bones['arm_'+side].head for side in ['R','L']};w2={};p2={};front2=Vector((math.sin(.2),-math.cos(.2),0))
for side in ['R','L']:
 w2[side]=empty('ARCADE | '+side+' wrist');ik=r2.pose.bones['forearm_'+side].constraints.new('IK');ik.target=w2[side];ik.chain_count=2;ik.use_stretch=False
 p2[side]=empty('ARCADE | '+side+' palm');p2[side].rotation_mode='QUATERNION';c=r2.pose.bones['hand_'+side].constraints.new('COPY_ROTATION');c.target=p2[side];c.owner_space='WORLD';c.target_space='WORLD'
MR=[(0,(.14,.08,-.34,0)),(25.2,(.14,.08,-.34,0)),(25.55,(.20,.10,-.23,.45)),(26.15,(.20,.10,-.23,.45)),(26.8,(.14,.08,-.34,0)),(28.7,(.14,.08,-.34,0)),(29.05,(.16,.11,-.29,.2)),(29.65,(.16,.11,-.29,.2)),(30.2,(.14,.08,-.34,0)),(32.5,(.14,.08,-.34,0)),(32.85,(.24,.10,-.14,.8)),(33.3,(.24,.10,-.14,.8)),(34.1,(.14,.08,-.34,0)),(35,(.14,.08,-.34,0))]
ML=[(0,(.14,.08,-.34,0)),(25.9,(.14,.08,-.34,0)),(26.2,(.18,.09,-.26,.25)),(26.6,(.18,.09,-.26,.25)),(27.2,(.14,.08,-.34,0)),(28.7,(.14,.08,-.34,0)),(29.15,(.16,.10,-.29,.2)),(29.8,(.16,.10,-.29,.2)),(30.4,(.14,.08,-.34,0)),(33.0,(.14,.08,-.34,0)),(33.35,(.19,.09,-.25,.3)),(33.7,(.19,.09,-.25,.3)),(34.5,(.14,.08,-.34,0))]
for m in list(s.timeline_markers):s.timeline_markers.remove(m)
for sh in info['shots']:s.timeline_markers.new(f"{sh['id']:02d} | {sh['kind']} | {sh['mood']}",frame=sh['start'])
faces={'room':[],'arcade':[]}
for f in range(1,N+1):
 t=(f-1)/24;sh=next(x for x in info['shots']if x['start']<=f<=x['end']);mood=sh['mood'];u=(f-sh['start'])/max(1,sh['end']-sh['start']);speaking=talk(t)
 for name,q in base.items():r.pose.bones[name].rotation_quaternion=q
 gaze=curve([(0,.65),(1.2,.65),(1.55,0),(3,0),(5.56,.4),(5.9,0),(6.7,.1),(7.2,0),(14.1,.5),(14.6,0),(16.3,0),(16.7,.4),(17.4,.4),(18.4,0),(21.6,.4),(22.1,.4),(22.7,0),(23.7,0),(25.2,0)],t)
 r.pose.bones['head'].rotation_quaternion=(head_side if mood in ['confused','disbelief','brain']else head_cam).slerp(head_monitor,gaze)
 tilt=curve([(0,0),(1.55,-.02),(2.3,-.02),(3,0),(5.9,.02),(6.7,.02),(7.2,0),(14.5,.04),(15.4,.04),(16.3,0),(16.7,-.05),(17.6,-.05),(18.4,0),(21.95,.025),(22.6,.025),(23.7,0),(24.0,-.035),(25.2,-.035)],t)
 r.pose.bones['head'].rotation_quaternion@=rest['head'].inverted()@Quaternion((0,1,0),tilt)@rest['head']
 lean=curve([(0,0),(1.55,-.025),(2.3,-.025),(3,0),(5.9,-.015),(6.6,-.015),(7.2,0),(14.5,.045),(15.5,.045),(16.3,0),(16.7,-.02),(17.6,-.02),(18.4,0),(21.95,-.025),(22.6,-.025),(23.7,0),(24.0,.035),(25.2,.035)],t)
 r.pose.bones['upper_chest'].rotation_quaternion@=rest['upper_chest'].inverted()@Quaternion((1,0,0),lean)@rest['upper_chest']
 for side,sign,keys in [('R',-1,R),('L',1,L)]:
  fw,ou,z,roll=curve(keys,t);out=Vector((math.cos(.6)*sign,math.sin(.6)*sign,0));w=bpy.data.objects['R3 | '+side+' wrist'];w.location=shoulders[side]+front*fw+out*ou+up*z;H.record(w,'location',f)
  direction=(front*.75+up*(-.75+2.4*smooth((z+.29)/.33))).normalized();orient[side].rotation_quaternion=direction.to_track_quat('Y','Z')@Quaternion((0,1,0),sign*roll);H.record(orient[side],'rotation_quaternion',f)
 for p in r.pose.bones:H.record(p,'rotation_quaternion',f)
 face=(12 if speaking else 2)if t<5.56 else(16 if speaking else 4)if t<14.1 else(16 if speaking else 18)if t<16.3 else(24 if speaking else 22)if t<23.7 else 5
 if any(b<=t<b+.083 for b in [2.4,6.5,15.5,17.7,22.8]):face=10
 a['PS1_face_id']=face;a.keyframe_insert(data_path='["PS1_face_id"]',frame=f)
 if not faces['room']or faces['room'][-1]['id']!=face:faces['room'].append(dict(frame=f,id=face))
 for p in r2.pose.bones:p.rotation_quaternion=Quaternion()
 hq=head_close if mood in ['recoil','final']else head_arcade
 glance=curve([(0,0),(25.2,.2),(25.6,.65),(26.4,.65),(27.2,.25),(28.7,.5),(29.2,.5),(29.8,0),(32.5,.6),(33.15,.6),(33.5,.15),(34.1,0),(35,0)],t)
 r2.pose.bones['head'].rotation_quaternion=hq.slerp(head_screen,glance)
 nod=curve([(0,0),(25.2,0),(25.55,-.02),(26.1,-.02),(26.8,0),(28.7,0),(29.05,.085),(29.7,.085),(30.2,.04),(32.5,.04),(32.85,-.02),(33.25,-.02),(34.1,.015),(35,.015)],t)
 r2.pose.bones['upper_chest'].rotation_quaternion=rest['upper_chest'].inverted()@Quaternion((1,0,0),nod)@rest['upper_chest']
 for side,sign,keys in [('R',-1,MR),('L',1,ML)]:
  fw,ou,z,roll=curve(keys,t);out=Vector((math.cos(.2)*sign,math.sin(.2)*sign,0));w2[side].location=shoulders2[side]+front2*fw+out*ou+up*z;H.record(w2[side],'location',f)
  direction=(front2*.75+up*(-.8+2.3*smooth((z+.34)/.36))).normalized();p2[side].rotation_quaternion=direction.to_track_quat('Y','Z')@Quaternion((0,1,0),sign*roll);H.record(p2[side],'rotation_quaternion',f)
 for p in r2.pose.bones:H.record(p,'rotation_quaternion',f)
 face2=(24 if speaking else 5)if t<28.7 else(24 if speaking else 22)if t<32.5 else(16 if speaking else 9)
 if any(b<=t<b+.083 for b in [26.5,29.7,33.8]):face2=10
 a2['PS1_face_id']=face2;a2.keyframe_insert(data_path='["PS1_face_id"]',frame=f)
 if not faces['arcade']or faces['arcade'][-1]['id']!=face2:faces['arcade'].append(dict(frame=f,id=face2))
 selection.inputs[0].default_value=1 if t>=32.5 else 0;closed.inputs[0].default_value=1 if t>=34.1 else 0
 H.record(selection.inputs[0],'default_value',f);H.record(closed.inputs[0],'default_value',f)
 if sh['kind']=='arcade':
  if mood=='exit':cam.location=(cx,-1.6,1.43);target=Vector((cx,.05,1.40));lens=52 if WIDE else 32
  elif mood in ['recoil','final']:cam.location=(21.1,-2.2,1.82);target=Vector((20,-.25,1.56));lens=48
  else:cam.location=(21.2,-3.4,1.96);target=Vector((20.55,.08,1.12));lens=37 if WIDE else 28
 elif sh['kind']=='monitor':cam.location=(1.15,.28,1.55);target=Vector((.1095,-.7959,1.262));lens=wide_monitor_lens if WIDE else 39
 elif mood in ['confused','disbelief','brain']:cam.location=(1.8,-.45,1.55);target=Vector((0,.10,1.39));lens=60
 else:cam.location=(2.1-.025*u,-.85+.015*u,1.65);target=Vector((0,.10,1.18));lens=42
 cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;H.record(cam,'location',f);H.record(cam,'rotation_euler',f);H.record(cam.data,'lens',f)
H.commit_curves()
for obj in [a,a2]:
 for fc in obj.animation_data.action.fcurves:
  for k in fc.keyframe_points:k.interpolation='CONSTANT'
for fc in pn.animation_data.action.fcurves:
 for key in fc.keyframe_points:key.interpolation='CONSTANT'
(ROOT/'face_cues.json').write_text(json.dumps(faces,indent=2));(ROOT/'acting_cues.json').write_text(json.dumps(dict(method='Phrase-led introduction, asymmetric enumeration, interrupted search gesture, one shock hold, restrained recoil and exit palm. No repeated conversation loop or prop contact.',right=R,left=L,arcade_right=MR,arcade_left=ML,menu_switches=dict(exit=32.5,closed=34.1),brain_graphic=[23.7,25.2],reference='Private gesture reference from episode 007; not republished.'),indent=2))
s['DeryPS1Look']=f'{405 if WIDE else 128}x228 seam-safe geometry precision; 128px body texture addressing; 5-bit RGB and fixed ordered dither at export';s['DeryFormats']='9:16 and 16:9, independent cameras and graphic layouts.'
s.sequence_editor_create().sequences.new_sound('VOZ | supplied recording',str(ROOT/'assets/voz/narracao_mix.wav'),channel=1,frame_start=1)
s.frame_set(80);bpy.data.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();(ROOT/'output').mkdir(exist_ok=True);dest=ROOT/'output'/('Dery_Sonic_Master_16x9.blend'if WIDE else'Dery_Sonic.blend');bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
for t in [1.7,6.2,15.1,17.4,22.4,24.3,25.8,29.3,32.8,34.4]:
 f=round(t*24)+1;sh=next(x for x in info['shots']if x['start']<=f<=x['end']);arcade=sh['kind']=='arcade'
 for o in s.objects:
  if o.type=='MESH':o.hide_render=(not arcade)if o.name.startswith('ARCADE |')else arcade
 s.frame_set(f);s.render.filepath=str(ROOT/f"output/preview_{'wide_'if WIDE else ''}{f:04d}.png");bpy.ops.render.render(write_still=True)
print('SONIC_SCENE_READY',flush=True)
