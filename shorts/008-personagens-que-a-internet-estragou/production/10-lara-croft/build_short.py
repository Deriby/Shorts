"""Lara: phrase-led performance, PS1 precision and treasure ignored beside a PC in a ruin."""
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
 p.matrix=Matrix.LocRotScale(m.translation,delta@m.to_quaternion(),m.to_scale());bpy.context.view_layer.update();q=p.rotation_quaternion.copy();p.rotation_quaternion=(base2 if rig.name=='RUINS | Dery rig'else base)['head'];bpy.context.view_layer.update();return q
head_cam=toward(r,(2.1,-.85,1.65));head_final=toward(r,(1.25,-1.25,1.56));head_side=toward(r,(1.8,-.45,1.55));head_monitor=toward(r,(.11,-.80,1.30))
shoulders={side:r.matrix_world@r.pose.bones['arm_'+side].head for side in ['R','L']};front=Vector((math.sin(.6),-math.cos(.6),0));up=Vector((0,0,1))



Rkeys=[(0,(.17,.10,-.30,0)),(1.3,(.17,.10,-.30,0)),(1.65,(.22,.09,-.20,.4)),(2.55,(.22,.09,-.20,.4)),(3.3,(.17,.10,-.30,0)),(11.2,(.17,.10,-.30,0)),(11.6,(.16,.10,-.32,0)),(12.6,(.16,.10,-.32,0)),(13.25,(.17,.10,-.30,0)),(15.25,(.17,.10,-.30,0)),(15.55,(.25,.08,-.14,.75)),(16.15,(.25,.08,-.14,.75)),(16.8,(.17,.10,-.30,0))]
Lkeys=[(0,(.19,.10,-.29,0)),(1.8,(.19,.10,-.29,0)),(2.1,(.20,.11,-.25,.25)),(2.7,(.20,.11,-.25,.25)),(3.35,(.19,.10,-.29,0)),(11.2,(.19,.10,-.29,0)),(11.55,(.20,.11,-.25,.4)),(12.3,(.20,.11,-.25,.4)),(13.2,(.19,.10,-.29,0))]
orient={}
for side in ['R','L']:
 o=empty('ACTING | '+side+' palm');o.rotation_mode='QUATERNION';orient[side]=o;c=r.pose.bones['hand_'+side].constraints.new('COPY_ROTATION');c.target=o;c.owner_space='WORLD';c.target_space='WORLD'
objects=[]
def box(name,loc,size,mat,parent=None):
 o=H.box('RUINS | '+name,loc,size,mat,parent);objects.append(o);return o
def graphic(name,filename):
 mat=H.material('RUINS | '+name,lit=False);nt=mat.node_tree;tx=nt.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(ROOT/'assets/memes'/filename),check_existing=True);tx.interpolation='Closest';nt.links.new(tx.outputs['Color'],next(n for n in nt.nodes if n.type=='EMISSION').inputs['Color']);return mat
wood=H.material('RUINS | old timber',(.20,.12,.055),lit=False);metal=H.material('RUINS | aged bronze',(.28,.22,.075),lit=False);dark=H.material('RUINS | dark seat',(.045,.055,.040),lit=False);gold=H.material('RUINS | gold',(.82,.54,.08),lit=False);leaf=H.material('RUINS | moss',(.10,.20,.075),lit=False);fire=H.material('RUINS | amber flame',(.9,.35,.065),lit=False)
# Reuse the castle-derived museum shell and its packed 32px stone texture.
with bpy.data.libraries.load(str(REPO/'assets/cenarios/museu/Museu_Internet.blend'))as(src,dst):
 dst.objects=[n for n in src.objects if n.startswith(('MUSEUM | floor','MUSEUM | wall','MUSEUM | column','MUSEUM | capital'))]
for o in dst.objects:s.collection.objects.link(o)
bpy.context.view_layer.update()
for o in dst.objects:
 mw=o.matrix_world.copy();o.parent=None;o.matrix_world=Matrix.Translation((20,0,0))@mw;o.animation_data_clear();o.hide_render=False;o.name=o.name.replace('MUSEUM |','RUINS | shell')
 if o.name=='RUINS | shell floor':o.scale.x*=2;o.scale.y*=2
 elif o.name=='RUINS | shell wall':o.scale.x*=2
 for m in list(o.modifiers):
  if m.type=='NODES':o.modifiers.remove(m)
 objects.append(o)
local=empty('RUINS | local origin',(20,.10,0));local.rotation_euler.z=.6
box('seat',(0,0,.49),(.56,.52,.12),dark,local);box('seat back',(0,.25,.99),(.59,.12,.98),wood,local)
for xx in [-.18,.18]:
 for yy in [-.15,.17]:box('seat leg',(xx,yy,.23),(.045,.045,.45),wood,local)
box('desk',(0,-.69,.685),(2.1,.58,.10),wood,local)
for xx in [-.84,.84]:box('desk leg',(xx,-.69,.32),(.08,.45,.64),wood,local)
box('keyboard',(-.18,-.78,.75),(.46,.16,.025),dark,local)
for i in range(6):box('keyboard key',(-.36+i*.07,-.79,.767),(.048,.08,.012),metal,local)
box('PC tower',(.65,-.54,.34),(.24,.39,.53),dark,local)
for z in [.46,.51]:box('PC drive',(.65,-.745,z),(.18,.012,.025),metal,local)
box('terminal foot',(.65,-.63,.77),(.31,.24,.06),metal,local);box('terminal stem',(.65,-.62,.85),(.07,.07,.15),dark,local)
box('CRT rear',(.65,-.48,1.12),(.80,.40,.50),dark,local);box('CRT bezel',(.65,-.63,1.12),(.93,.12,.55),metal,local)
o=H.quad('RUINS | terminal picture',[(.205,-.699,.87),(1.095,-.699,.87),(1.095,-.699,1.37),(.205,-.699,1.37)],graphic('PC fan mod preview','pc_mod.png'),parent=local);objects.append(o)
# An already-open static chest makes the neglected treasure legible without hand contact.
cx,cy=18.74,-.45
box('chest base',(cx,cy,.23),(.98,.67,.14),wood)
for yy in [-.34,.34]:box('chest wall',(cx,cy+yy,.44),(1.02,.065,.35),wood)
for xx in [-.48,.48]:box('chest side',(cx+xx,cy,.44),(.065,.67,.35),wood)
box('chest open lid',(cx,cy+.34,.87),(1.02,.075,.52),wood)
for xx in [-.31,.31]:
 box('chest band',(cx+xx,cy-.38,.44),(.07,.035,.36),metal)
 box('lid band',(cx+xx,cy+.29,.87),(.07,.035,.52),metal)
box('chest latch',(cx,cy-.39,.48),(.12,.04,.14),gold)
for i,(xx,yy,zz)in enumerate([(-.26,-.14,.56),(-.10,.02,.59),(.13,-.13,.57),(.28,.13,.61),(-.27,.15,.58),(.08,.16,.64),(.26,-.09,.66),(-.10,-.16,.67)]):
 coin=box('coin '+str(i),(cx+xx,cy+yy,zz),(.19,.17,.045),gold);coin.rotation_euler=(.12*(i%2),.1*(i%3),.4*i)
for x in [18.35,21.65]:
 box('torch bracket',(x,.93,1.64),(.12,.22,.13),metal);box('torch',(x,.80,1.92),(.07,.07,.47),wood)
 for z,sz in [(2.17,.15),(2.29,.09)]:box('flame',(x,.80,z),(sz,sz,.20),fire)
for i in range(6):box('moss',(17.3+i*.13,1.04,2.6-i*.14),(.19,.035,.24),leaf)
r2=r.copy();r2.data=r.data.copy();r2.name='RUINS | Dery rig';s.collection.objects.link(r2);r2.animation_data_clear();mw=r.matrix_world.copy();mw.translation.x+=20;r2.parent=None;r2.matrix_world=mw
for p in r2.pose.bones:
 p.rotation_quaternion=base[p.name]
 for c in list(p.constraints):p.constraints.remove(c)
for p in r2.pose.bones:
 kw={}if p.parent is None else dict(parent_matrix=seated_pose[p.parent.name],parent_matrix_local=p.parent.bone.matrix_local)
 p.matrix_basis=p.bone.convert_local_to_pose(seated_pose[p.name],p.bone.matrix_local,invert=True,**kw)
bpy.context.view_layer.update();basis2={p.name:p.matrix_basis.copy()for p in r2.pose.bones};base2={p.name:p.rotation_quaternion.copy()for p in r2.pose.bones}
a2=a.copy();a2.data=a.data.copy();a2.name='RUINS | Dery';s.collection.objects.link(a2);a2.animation_data_clear();a2.parent=r2;a2.matrix_parent_inverse=Matrix.Identity(4);a2.matrix_basis=Matrix.Identity(4)
for m in list(a2.modifiers):
 if m.type=='NODES':a2.modifiers.remove(m)
 elif m.type=='ARMATURE':m.object=r2
install_faces(a2);nt=a2.data.materials[1].node_tree;illum=neutral_light(nt)
for n in list(nt.nodes):
 if n.type=='VERTEX_COLOR'and n.layer_name=='PS1FaceLightFit':
  for link in list(n.outputs['Color'].links):nt.links.new(illum,link.to_socket)
a2.data.materials[1]['DeryNeutralLight']=True;precision(a2,True)


for o in objects:precision(o)
head_ruins=toward(r2,(22,-2.65,1.90));head_close=toward(r2,(21.4,-1.6,1.62));terminal_point=local.matrix_world@Vector((.65,-.65,1.12));head_terminal=toward(r2,terminal_point);head_chest=toward(r2,(cx,cy,.60))
bpy.context.view_layer.update();shoulders2={side:r2.matrix_world@r2.pose.bones['arm_'+side].head for side in ['R','L']};w2={};p2={}
for side in ['R','L']:
 w2[side]=empty('RUINS | '+side+' wrist');ik=r2.pose.bones['forearm_'+side].constraints.new('IK');ik.target=w2[side];ik.chain_count=2;ik.use_stretch=False
 p2[side]=empty('RUINS | '+side+' palm');p2[side].rotation_mode='QUATERNION';c=r2.pose.bones['hand_'+side].constraints.new('COPY_ROTATION');c.target=p2[side];c.owner_space='WORLD';c.target_space='WORLD'
TR=[(0,(.17,.10,-.30,0)),(24.9,(.17,.10,-.30,0)),(25.2,(.22,.08,-.21,.4)),(25.85,(.22,.08,-.21,.4)),(26.5,(.17,.10,-.30,0)),(29.5,(.17,.10,-.30,0)),(29.85,(.25,.10,-.14,.85)),(30.6,(.25,.10,-.14,.85)),(31.25,(.17,.10,-.30,0)),(32.2,(.17,.10,-.30,0)),(32.65,(.24,.11,-.17,.8)),(33.5,(.24,.11,-.17,.8)),(34.4,(.17,.10,-.30,0)),(37.4,(.17,.10,-.30,0))]
TL=[(0,(.19,.10,-.29,0)),(25.1,(.19,.10,-.29,0)),(25.4,(.18,.10,-.26,.2)),(26,(.18,.10,-.26,.2)),(26.6,(.19,.10,-.29,0)),(32.5,(.19,.10,-.29,0)),(32.9,(.23,.10,-.18,.75)),(33.8,(.23,.10,-.18,.75)),(34.75,(.19,.10,-.29,0)),(35.1,(.19,.10,-.29,0)),(35.4,(.21,.10,-.24,.3)),(35.9,(.21,.10,-.24,.3)),(36.5,(.19,.10,-.29,0))]
for marker in list(s.timeline_markers):s.timeline_markers.remove(marker)
for sh in info['shots']:s.timeline_markers.new(f"{sh['id']:02d} | {sh['kind']} | {sh['mood']}",frame=sh['start'])
faces={'room':[],'ruins':[]}
for f in range(1,N+1):
 t=(f-1)/24;sh=next(x for x in info['shots']if x['start']<=f<=x['end']);mood=sh['mood'];u=(f-sh['start'])/max(1,sh['end']-sh['start']);speaking=talk(t)
 for name,q in base.items():r.pose.bones[name].rotation_quaternion=q
 gaze=curve([(0,.75),(1.3,.75),(1.65,0),(3.35,0),(11.2,.15),(11.55,0),(13.25,0),(15.25,.45),(15.65,0),(16.8,0)],t);tilt=curve([(0,0),(1.65,-.02),(2.8,-.02),(3.35,0),(11.55,.05),(12.5,.05),(13.25,0),(15.6,-.035),(16.2,-.035),(16.8,0)],t)
 r.pose.bones['head'].rotation_quaternion=head_cam.slerp(head_monitor,gaze)@(rest['head'].inverted()@Quaternion((0,1,0),tilt)@rest['head'])
 lean=curve([(0,0),(1.65,-.02),(2.8,-.02),(3.35,0),(11.5,.055),(12.6,.055),(13.25,0),(15.6,-.03),(16.25,-.03),(16.8,0)],t)
 r.pose.bones['upper_chest'].rotation_quaternion@=rest['upper_chest'].inverted()@Quaternion((1,0,0),lean)@rest['upper_chest']
 for side,sign,keys in [('R',-1,Rkeys),('L',1,Lkeys)]:
  fw,ou,z,roll=curve(keys,t);out=Vector((math.cos(.6)*sign,math.sin(.6)*sign,0));w=bpy.data.objects['R3 | '+side+' wrist'];w.location=shoulders[side]+front*fw+out*ou+up*z;H.record(w,'location',f)
  direction=(front*.75+up*(-.75+2.4*smooth((z+.29)/.33))).normalized();orient[side].rotation_quaternion=direction.to_track_quat('Y','Z')@Quaternion((0,1,0),sign*roll);H.record(orient[side],'rotation_quaternion',f)
 for p in r.pose.bones:H.record(p,'rotation_quaternion',f)
 face=(12 if speaking else 20)if t<11.2 else(16 if speaking else 4)if t<15.25 else(12 if speaking else 22)
 if any(b<=t<b+.083 for b in [2.8,12.7,16.4]):face=10
 a['PS1_face_id']=face;a.keyframe_insert(data_path='["PS1_face_id"]',frame=f)
 if not faces['room']or faces['room'][-1]['id']!=face:faces['room'].append(dict(frame=f,id=face))
 for name,basis in basis2.items():r2.pose.bones[name].matrix_basis=basis
 glance=curve([(0,0),(24.9,.7),(25.5,.7),(26.2,.3),(29.5,.2),(30.2,0),(30.9,0),(31.2,.75),(32.2,.75),(32.6,.2),(33.2,.2),(33.6,0),(37.4,0)],t)
 hq=head_close if mood in ['annoyed','final']else head_ruins
 r2.pose.bones['head'].rotation_quaternion=hq.slerp(head_chest if 30.9<=t<32.65 else head_terminal,glance)
 lean2=curve([(0,0),(24.9,-.02),(25.5,-.02),(26.3,0),(29.5,0),(29.85,.045),(30.6,.045),(31.1,0),(32.2,0),(32.65,.025),(33.5,.025),(34.2,0),(35.3,.015),(37.4,.015)],t)
 r2.pose.bones['upper_chest'].rotation_quaternion@=rest['upper_chest'].inverted()@Quaternion((1,0,0),lean2)@rest['upper_chest']
 for side,sign,keys in [('R',-1,TR),('L',1,TL)]:
  fw,ou,z,roll=curve(keys,t);out=Vector((math.cos(.6)*sign,math.sin(.6)*sign,0));w2[side].location=shoulders2[side]+front*fw+out*ou+up*z;H.record(w2[side],'location',f)
  direction=(front*.75+up*(-.75+2.4*smooth((z+.29)/.33))).normalized();p2[side].rotation_quaternion=direction.to_track_quat('Y','Z')@Quaternion((0,1,0),sign*roll);H.record(p2[side],'rotation_quaternion',f)
 for p in r2.pose.bones:H.record(p,'rotation_quaternion',f)
 face2=(16 if speaking else 4)if t<29.5 else(24 if speaking else 7)
 if any(b<=t<b+.083 for b in [25.9,30.7,33.6,36.1]):face2=10
 a2['PS1_face_id']=face2;a2.keyframe_insert(data_path='["PS1_face_id"]',frame=f)
 if not faces['ruins']or faces['ruins'][-1]['id']!=face2:faces['ruins'].append(dict(frame=f,id=face2))
 if sh['kind']=='ruins':
  if mood=='treasure':cam.location=(cx+.25,-2.25,1.65);target=Vector((cx,cy,.62));lens=42 if WIDE else 33
  elif mood in ['annoyed','final']:cam.location=(21.4,-1.6,1.62);target=Vector((20,.1,1.32));lens=56
  else:cam.location=(22,-3.05,1.98);target=Vector((19.85,-.15,.98));lens=34 if WIDE else 25
 elif sh['kind']=='monitor':cam.location=(1.15,.28,1.55);target=Vector((.1095,-.7959,1.262));lens=wide_monitor_lens if WIDE else 39
 else:cam.location=(2.1-.025*u,-.85+.015*u,1.65);target=Vector((0,.10,1.18));lens=42
 cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;H.record(cam,'location',f);H.record(cam,'rotation_euler',f);H.record(cam.data,'lens',f)
H.commit_curves()
for obj in [a,a2]:
 for fc in obj.animation_data.action.fcurves:
  for k in fc.keyframe_points:k.interpolation='CONSTANT'
(ROOT/'face_cues.json').write_text(json.dumps(faces,indent=2));(ROOT/'acting_cues.json').write_text(json.dumps(dict(method='Phrase-led introduction, sarcasm, curious presentation, treasure glance, one incredulous palm and annoyed ending. Complete evaluated seated pose preserved; no repeating conversation loop.',room_right=Rkeys,room_left=Lkeys,ruins_right=TR,ruins_left=TL,reference='Private gesture reference from episode 007; not republished.'),indent=2))
s['DeryPS1Look']=f'{405 if WIDE else 128}x228 seam-safe geometry precision; Closest textures; 5-bit RGB and ordered dither at export';s['DeryFormats']='9:16 and 16:9 with separate cameras and graphic layouts'
s.sequence_editor_create().sequences.new_sound('VOZ | supplied recording',str(ROOT/'assets/voz/narracao_mix.wav'),channel=1,frame_start=1)
s.frame_set(45);bpy.data.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();(ROOT/'output').mkdir(exist_ok=True);dest=ROOT/'output'/('Dery_Lara_Master_16x9.blend'if WIDE else'Dery_Lara.blend');bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
for t in [2.1,12.0,16.0,25.6,30.1,31.5,33.1,35.3]:
 f=round(t*24)+1;ruins=next(x for x in info['shots']if x['start']<=f<=x['end'])['kind']=='ruins'
 for o in s.objects:
  if o.type=='MESH':o.hide_render=(not ruins)if o.name.startswith('RUINS |')else ruins
 s.frame_set(f);s.render.filepath=str(ROOT/f"output/preview_{'wide_'if WIDE else ''}{f:04d}.png");bpy.ops.render.render(write_still=True)
print('LARA_SCENE_READY',flush=True)
