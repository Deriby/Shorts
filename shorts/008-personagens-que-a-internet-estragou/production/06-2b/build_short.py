"""Phrase-specific performance, discrete faces, PS1 precision and an industrial training terminal."""
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




# Different intentions for each phrase: present, reflect, smirk, resign and object.
R=[(0,(.17,.10,-.30,0)),(1.4,(.17,.10,-.30,0)),(1.7,(.24,.08,-.15,.7)),(2.4,(.24,.08,-.15,.7)),(3.05,(.17,.10,-.30,0)),(6.02,(.17,.10,-.30,0)),(6.4,(.16,.10,-.32,0)),(7.7,(.16,.10,-.32,0)),(8.5,(.17,.10,-.30,0)),(18.92,(.17,.10,-.30,0)),(19.3,(.23,.11,-.17,.85)),(20.3,(.23,.11,-.17,.85)),(21.3,(.17,.10,-.30,0)),(25.24,(.17,.10,-.30,0)),(25.6,(.21,.07,-.10,.2)),(26.05,(.21,.07,-.10,.2)),(26.9,(.17,.10,-.30,0))]
L=[(0,(.19,.10,-.29,0)),(11.02,(.19,.10,-.29,0)),(11.4,(.25,.11,-.15,.9)),(12.25,(.25,.11,-.15,.9)),(13.2,(.19,.10,-.29,0)),(19.7,(.19,.10,-.29,0)),(20.1,(.19,.12,-.25,.25)),(21.3,(.19,.10,-.29,0)),(25.8,(.19,.10,-.29,0)),(26.15,(.18,.12,-.24,.3)),(26.7,(.19,.10,-.29,0))]
orient={}
for side in ['R','L']:
 o=empty('ACTING | '+side+' palm');o.rotation_mode='QUATERNION';orient[side]=o;c=r.pose.bones['hand_'+side].constraints.new('COPY_ROTATION');c.target=o;c.owner_space='WORLD';c.target_space='WORLD'
objects=[]
def box(name,loc,size,mat,parent=None):
 o=H.box('TRAIN | '+name,loc,size,mat,parent);objects.append(o);return o
# Append only the industrial garage shell. The car, driver and boss UI stay in the old asset.
with bpy.data.libraries.load(str(REPO/'assets/cenarios/garagem_driver/Garagem_Driver.blend'))as(src,dst):
 dst.objects=[n for n in src.objects if n.startswith('GARAGE |')and n!='GARAGE | reusable origin']
for o in dst.objects:
 if o.type!='MESH':continue
 s.collection.objects.link(o)
bpy.context.view_layer.update()
for o in dst.objects:
 if o.type!='MESH':continue
 mw=o.matrix_world.copy()
 if abs(mw.translation.x)<.6 and mw.translation.y<-1.0:
  bpy.data.objects.remove(o,do_unlink=True);continue
 o.parent=None;o.matrix_world=Matrix.Translation((20,0,0))@mw;o.animation_data_clear();o.hide_render=False;o.name=o.name.replace('GARAGE |','TRAIN | garage')
 for m in list(o.modifiers):
  if m.type=='NODES':o.modifiers.remove(m)
 if 'back wall'in o.name:o.location.y=1.8
 if 'floor'in o.name:o.location.z=-.18
 objects.append(o)
metal=H.material('TRAIN | graphite',(.08,.115,.13),lit=False);light=H.material('TRAIN | pale metal',(.29,.34,.34),lit=False);gold=H.material('TRAIN | hazard gold',(.70,.48,.06),lit=False);black=H.material('TRAIN | display frame',(.025,.045,.05),lit=False)
box('platform',(20.4,.1,-.06),(3,1.9,.12),metal)
for x in [19.05,21.75]:box('platform rim',(x,.1,.003),(.06,1.8,.012),gold)
px=21.12 if WIDE else 20.82;pw=1.25 if WIDE else .9;ph=pw*360/640
box('terminal foot',(px,.36,.08),(.57,.55,.16),metal);box('terminal support',(px,.38,.58),(.18,.18,1.05),light);box('terminal frame',(px,.28,1.42),(pw+.10,.17,ph+.10),black)
panelmat=H.material('TRAIN | normal interface selection',lit=False);nt=panelmat.node_tree
tex1=nt.nodes.new('ShaderNodeTexImage');tex1.image=bpy.data.images.load(str(ROOT/'assets/memes/treino_maquinas.png'));tex1.interpolation='Closest'
tex2=nt.nodes.new('ShaderNodeTexImage');tex2.image=bpy.data.images.load(str(ROOT/'assets/memes/treino_internet.png'));tex2.interpolation='Closest'
selection=nt.nodes.new('ShaderNodeMixRGB');selection.name='TRAIN | test selection';nt.links.new(tex1.outputs['Color'],selection.inputs[1]);nt.links.new(tex2.outputs['Color'],selection.inputs[2]);nt.links.new(selection.outputs[0],next(n for n in nt.nodes if n.type=='EMISSION').inputs['Color'])
o=H.quad('TRAIN | terminal image',[(px-pw/2,.187,1.42-ph/2),(px+pw/2,.187,1.42-ph/2),(px+pw/2,.187,1.42+ph/2),(px-pw/2,.187,1.42+ph/2)],panelmat);objects.append(o)
# Standing clone uses the previously validated castle pose without modifying the mesh.
r2=r.copy();r2.data=r.data.copy();r2.name='TRAIN | Dery rig';s.collection.objects.link(r2);r2.animation_data_clear();r2.parent=None;r2.rotation_mode='XYZ';r2.location=(20,-.25,0);r2.rotation_euler=(0,0,.2)
for p in r2.pose.bones:
 p.matrix_basis=Matrix.Identity(4)
 for c in list(p.constraints):p.constraints.remove(c)
a2=a.copy();a2.data=a.data.copy();a2.name='TRAIN | Dery';s.collection.objects.link(a2);a2.animation_data_clear();a2.parent=r2;a2.matrix_parent_inverse=Matrix.Identity(4);a2.matrix_basis=Matrix.Identity(4)
for m in list(a2.modifiers):
 if m.type=='NODES':a2.modifiers.remove(m)
 elif m.type=='ARMATURE':m.object=r2
install_faces(a2);nt=a2.data.materials[1].node_tree;illum=neutral_light(nt)
for n in list(nt.nodes):
 if n.type=='VERTEX_COLOR'and n.layer_name=='PS1FaceLightFit':
  for link in list(n.outputs['Color'].links):nt.links.new(illum,link.to_socket)
a2.data.materials[1]['DeryNeutralLight']=True;precision(a2,True)
for obj in objects:precision(obj)

head_training=toward(r2,(21.2,-3.7,2.0));head_close=toward(r2,(21.0,-2.0,1.78));head_terminal=toward(r2,(px,.05,1.42))
bpy.context.view_layer.update();shoulders2={side:r2.matrix_world@r2.pose.bones['arm_'+side].head for side in ['R','L']};w2={};p2={};front2=Vector((math.sin(.2),-math.cos(.2),0))
for side in ['R','L']:
 w2[side]=empty('TRAIN | '+side+' wrist');ik=r2.pose.bones['forearm_'+side].constraints.new('IK');ik.target=w2[side];ik.chain_count=2;ik.use_stretch=False
 p2[side]=empty('TRAIN | '+side+' palm');p2[side].rotation_mode='QUATERNION';c=r2.pose.bones['hand_'+side].constraints.new('COPY_ROTATION');c.target=p2[side];c.owner_space='WORLD';c.target_space='WORLD'
MR=[(0,(.14,.08,-.34,0)),(31.28,(.14,.08,-.34,0)),(31.7,(.24,.10,-.14,.8)),(32.7,(.24,.10,-.14,.8)),(33.35,(.16,.09,-.27,.3)),(34.3,(.16,.09,-.27,.3)),(34.65,(.23,.10,-.14,.75)),(35.2,(.23,.10,-.14,.75)),(35.65,(.23,.10,-.14,.75)),(36.4,(.14,.08,-.34,0)),(39.4,(.14,.08,-.34,0))]
ML=[(0,(.14,.08,-.34,0)),(32.5,(.14,.08,-.34,0)),(32.9,(.17,.11,-.24,.4)),(33.5,(.17,.11,-.24,.4)),(34.4,(.14,.08,-.34,0)),(39.4,(.14,.08,-.34,0))]
for m in list(s.timeline_markers):s.timeline_markers.remove(m)
for sh in info['shots']:s.timeline_markers.new(f"{sh['id']:02d} | {sh['kind']} | {sh['mood']}",frame=sh['start'])
faces={'room':[],'training':[]}
for f in range(1,N+1):
 t=(f-1)/24;sh=next(x for x in info['shots']if x['start']<=f<=x['end']);mood=sh['mood'];u=(f-sh['start'])/max(1,sh['end']-sh['start']);speaking=talk(t)
 for name,q in base.items():r.pose.bones[name].rotation_quaternion=q
 gaze=curve([(0,.8),(1.35,.8),(1.85,0),(3.1,0),(6.02,.2),(6.5,0),(8.4,0),(11.02,.2),(11.5,0),(13.2,0),(18.92,.4),(19.4,0),(21.52,0),(25.24,.1),(25.6,0),(27.2,0)],t)
 r.pose.bones['head'].rotation_quaternion=head_cam.slerp(head_monitor,gaze)
 tilt=curve([(0,0),(1.7,-.025),(2.4,-.025),(3.1,0),(6.3,.035),(7.5,.035),(8.4,0),(11.2,-.045),(12.4,-.045),(13.2,0),(19.15,.04),(20.3,.04),(21.52,0),(25.24,.02),(25.65,-.04),(26.5,-.04),(27.2,0)],t)
 pitch=curve([(0,0),(6.02,0),(6.5,.07),(7.3,.07),(8.4,0),(39.4,0)],t)
 r.pose.bones['head'].rotation_quaternion@=rest['head'].inverted()@Quaternion((0,1,0),tilt)@Quaternion((1,0,0),pitch)@rest['head']
 lean=curve([(0,0),(1.8,-.025),(2.5,-.025),(3.1,0),(6.02,0),(6.5,.055),(7.6,.055),(8.4,0),(11.3,-.025),(12.6,-.025),(13.2,0),(19.2,.05),(20.3,.05),(21.52,0),(25.24,0),(25.6,-.035),(26.3,-.035),(27.2,0)],t)
 r.pose.bones['upper_chest'].rotation_quaternion@=rest['upper_chest'].inverted()@Quaternion((1,0,0),lean)@rest['upper_chest']
 for side,sign,keys in [('R',-1,R),('L',1,L)]:
  fw,ou,z,roll=curve(keys,t);out=Vector((math.cos(.6)*sign,math.sin(.6)*sign,0));w=bpy.data.objects['R3 | '+side+' wrist'];w.location=shoulders[side]+front*fw+out*ou+up*z;H.record(w,'location',f)
  direction=(front*.75+up*(-.75+2.4*smooth((z+.29)/.33))).normalized();orient[side].rotation_quaternion=direction.to_track_quat('Y','Z')@Quaternion((0,1,0),sign*roll);H.record(orient[side],'rotation_quaternion',f)
 for p in r.pose.bones:H.record(p,'rotation_quaternion',f)
 face=(12 if speaking else 20)if t<6.02 else(24 if speaking else 20)if t<11.02 else(16 if speaking else 4)if t<18.92 else(16 if speaking else 18)if t<25.24 else(24 if speaking else 7)
 if any(b<=t<b+.083 for b in [2.7,7.15,12.7,20.55,26.7]):face=10
 a['PS1_face_id']=face;a.keyframe_insert(data_path='["PS1_face_id"]',frame=f)
 if not faces['room']or faces['room'][-1]['id']!=face:faces['room'].append(dict(frame=f,id=face))
 for p in r2.pose.bones:p.rotation_quaternion=Quaternion()
 glance=curve([(0,0),(31.28,0),(31.8,.65),(32.6,.65),(33.3,0),(34.7,0),(35.25,.75),(35.9,.75),(36.25,0),(39.4,0)],t)
 r2.pose.bones['head'].rotation_quaternion=(head_close if mood=='final'else head_training).slerp(head_terminal,glance)
 slump=curve([(0,0),(31.28,0),(31.8,-.025),(34.8,-.025),(35.25,-.025),(35.7,.035),(36.4,.055),(39.4,.055)],t)
 r2.pose.bones['upper_chest'].rotation_quaternion=rest['upper_chest'].inverted()@Quaternion((1,0,0),slump)@rest['upper_chest']
 for side,sign,keys in [('R',-1,MR),('L',1,ML)]:
  fw,ou,z,roll=curve(keys,t);out=Vector((math.cos(.2)*sign,math.sin(.2)*sign,0));w2[side].location=shoulders2[side]+front2*fw+out*ou+up*z;H.record(w2[side],'location',f)
  direction=(front2*.75+up*(-.8+2.3*smooth((z+.34)/.36))).normalized();p2[side].rotation_quaternion=direction.to_track_quat('Y','Z')@Quaternion((0,1,0),sign*roll);H.record(p2[side],'rotation_quaternion',f)
 for p in r2.pose.bones:H.record(p,'rotation_quaternion',f)
 face2=(3 if speaking else 2)if t<35.25 else 5 if t<36.25 else 6
 if any(b<=t<b+.083 for b in [32.9,34.5]):face2=10
 a2['PS1_face_id']=face2;a2.keyframe_insert(data_path='["PS1_face_id"]',frame=f)
 if not faces['training']or faces['training'][-1]['id']!=face2:faces['training'].append(dict(frame=f,id=face2))
 selection.inputs[0].default_value=0 if t<35.25 else 1;H.record(selection.inputs[0],'default_value',f)
 if sh['kind']=='training':
  if mood=='final':cam.location=(21.0,-2.0,1.78);target=Vector((20,-.25,1.52));lens=48
  else:cam.location=(21.2,-3.7+.025*u,2.0);target=Vector((20.40,.05,1.10));lens=33 if WIDE else 28
 elif sh['kind']=='monitor':cam.location=(1.15,.28,1.55);target=Vector((.1095,-.7959,1.262));lens=wide_monitor_lens if WIDE else 39
 elif mood in ['reflect','annoyed']:cam.location=(1.8,-.45,1.55);target=Vector((0,.10,1.39));lens=60
 else:cam.location=(2.1-.025*u,-.85+.015*u,1.65);target=Vector((0,.10,1.18));lens=42
 cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;H.record(cam,'location',f);H.record(cam,'rotation_euler',f);H.record(cam.data,'lens',f)
H.commit_curves()
for obj in [a,a2]:
 for fc in obj.animation_data.action.fcurves:
  for k in fc.keyframe_points:k.interpolation='CONSTANT'
for fc in panelmat.node_tree.animation_data.action.fcurves:
 for k in fc.keyframe_points:k.interpolation='CONSTANT'
(ROOT/'face_cues.json').write_text(json.dumps(faces,indent=2));(ROOT/'acting_cues.json').write_text(json.dumps(dict(method='Asymmetric phrase gestures, reflective head drop, resigned palm, single objection and interrupted confident presentation. No periodic loop.',right=R,left=L,training_right=MR,training_left=ML,reference='Private gesture reference retained from episode 007; not republished.'),indent=2))
s['DeryPS1Look']=f'{405 if WIDE else 128}x228 seam-safe geometry precision; Closest textures; 5-bit RGB and ordered dither at export';s['DeryFormats']='9:16 and 16:9 with separate camera and graphic layouts'
s.sequence_editor_create().sequences.new_sound('VOZ | supplied recording',str(ROOT/'assets/voz/narracao_mix.wav'),channel=1,frame_start=1)
s.frame_set(80);bpy.data.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();(ROOT/'output').mkdir(exist_ok=True);dest=ROOT/'output'/('Dery_2B_Master_16x9.blend'if WIDE else'Dery_2B.blend');bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
for t in [7.0,12.0,20.0,26.0,32.7,36.1,38.2]:
 f=round(t*24)+1;training=next(x for x in info['shots']if x['start']<=f<=x['end'])['kind']=='training'
 for o in s.objects:
  if o.type=='MESH':o.hide_render=(not training)if o.name.startswith('TRAIN |')else training
 s.frame_set(f);s.render.filepath=str(ROOT/f"output/preview_{'wide_'if WIDE else ''}{f:04d}.png");bpy.ops.render.render(write_still=True)
print('TWOB_SCENE_READY',flush=True)
