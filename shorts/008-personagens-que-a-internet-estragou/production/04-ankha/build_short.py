"""Phrase-specific performance, discrete faces, PS1 precision and a small museum of the character and music."""
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
R=[(0,(.17,.10,-.30,0)),(2.1,(.17,.10,-.30,0)),(2.45,(.24,.08,-.15,.7)),(2.95,(.24,.08,-.15,.7)),(3.65,(.17,.10,-.30,0)),(5.1,(.17,.10,-.30,0)),(5.55,(.16,.10,-.32,0)),(6.5,(.16,.10,-.32,0)),(7.5,(.17,.10,-.30,0)),(35.8,(.17,.10,-.30,0)),(36.15,(.27,.08,-.045,.15)),(36.8,(.27,.08,-.045,.15)),(37.45,(.27,.08,-.045,.15)),(38.5,(.19,.11,-.21,.4)),(39.2,(.17,.10,-.30,0))]
L=[(0,(.19,.10,-.29,0)),(5.4,(.19,.10,-.29,0)),(5.8,(.18,.10,-.32,0)),(6.8,(.18,.10,-.32,0)),(7.7,(.19,.10,-.29,0)),(36.4,(.19,.10,-.29,0)),(36.8,(.19,.12,-.24,.25)),(37.7,(.19,.12,-.24,.25)),(39,(.19,.10,-.29,0))]
orient={}
for side in ['R','L']:
 o=empty('ACTING | '+side+' palm');o.rotation_mode='QUATERNION';orient[side]=o;c=r.pose.bones['hand_'+side].constraints.new('COPY_ROTATION');c.target=o;c.owner_space='WORLD';c.target_space='WORLD'
# Reuse the castle's compact wall/column/floor layout as a warm low-poly museum.
stone=H.material('MUSEUM | sandstone',(.45,.34,.19),lit=False);dark=H.material('MUSEUM | shadow',(.09,.075,.045),lit=False);gold=H.material('MUSEUM | gold',(.60,.40,.095),lit=False);wood=H.material('MUSEUM | pedestal',(.20,.13,.065),lit=False);black=H.material('MUSEUM | cassette plastic',(.035,.045,.045),lit=False)
objects=[]
def box(name,loc,size,mat,parent=None):
 o=H.box('MUSEUM | '+name,loc,size,mat,parent);objects.append(o);return o
def graphic(name,filename):
 mat=H.material('MUSEUM | '+name,lit=False);nt=mat.node_tree;tx=nt.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(ROOT/'assets/memes'/filename),check_existing=True);tx.interpolation='Closest';em=next(n for n in nt.nodes if n.type=='EMISSION');nt.links.new(tx.outputs['Color'],em.inputs['Color']);return mat
box('floor',(20,0,-.055),(9,7,.11),stone);box('wall',(20,1.15,1.65),(8,.14,3.4),stone);box('wall band',(20,1.055,2.65),(8,.045,.15),gold)
for x in [18.35,21.65]:
 box('column',(x,.82,1.4),(.25,.32,2.8),gold)
 for z in [.10,2.73]:box('capital',(x,.82,z),(.42,.44,.16),stone)
# Shared stone tile pattern, not a large new texture.
im=bpy.data.images.new('MUSEUM | 32px stone',32,32);pixels=[]
for y in range(32):
 for x in range(32):
  edge=y%8==0 or(x+(4 if(y//8)%2 else 0))%8==0;v=.29 if edge else .44+((x*5+y*3)%4)*.009;pixels.extend((v,v*.78,v*.45,1))
im.pixels=pixels;im.pack();nt=stone.node_tree;tx=nt.nodes.new('ShaderNodeTexImage');tx.image=im;tx.interpolation='Closest';co=nt.nodes.new('ShaderNodeTexCoord');nt.links.new(co.outputs['Generated'],tx.inputs['Vector']);tx.projection='BOX';nt.links.new(tx.outputs['Color'],next(n for n in nt.nodes if n.type=='EMISSION').inputs['Color'])
left_x,right_x=(18.95,21.05)if WIDE else(19.25,20.75)
for x in [left_x,right_x]:
 box('pedestal',(x,.25,.46),(.73,.62,.92),wood);box('pedestal lip',(x,.25,.94),(.80,.68,.10),gold)
artroot=empty('MUSEUM | character exhibit');taperoot=empty('MUSEUM | music exhibit')
poster=graphic('Ankha framed image','exhibit_ankha.png');pw=.76 if WIDE else .65;ph=pw*512/384
box('portrait frame',(left_x,.36,1.0+ph/2),(pw+.07,.12,ph+.07),gold,artroot)
o=H.quad('MUSEUM | character picture',[(left_x-pw/2,.289,1.0),(left_x+pw/2,.289,1.0),(left_x+pw/2,.289,1.0+ph),(left_x-pw/2,.289,1.0+ph)],poster,parent=artroot);objects.append(o)
cw=.9 if WIDE else .72;ch=cw*400/640
box('cassette',(right_x,.17,1.39),(cw,.16,ch),black,taperoot)
label=graphic('cassette label','cassette_label.png');o=H.quad('MUSEUM | music label',[(right_x-cw/2,.083,1.39-ch/2),(right_x+cw/2,.083,1.39-ch/2),(right_x+cw/2,.083,1.39+ch/2),(right_x-cw/2,.083,1.39+ch/2)],label,parent=taperoot);objects.append(o)
# Standing clone uses the previously validated castle pose without modifying the mesh.
r2=r.copy();r2.data=r.data.copy();r2.name='MUSEUM | Dery rig';s.collection.objects.link(r2);r2.animation_data_clear();r2.parent=None;r2.rotation_mode='XYZ';r2.location=(20,-.25,0);r2.rotation_euler=(0,0,.2)
for p in r2.pose.bones:
 p.matrix_basis=Matrix.Identity(4)
 for c in list(p.constraints):p.constraints.remove(c)
a2=a.copy();a2.data=a.data.copy();a2.name='MUSEUM | Dery';s.collection.objects.link(a2);a2.animation_data_clear();a2.parent=r2;a2.matrix_parent_inverse=Matrix.Identity(4);a2.matrix_basis=Matrix.Identity(4)
for m in list(a2.modifiers):
 if m.type=='NODES':a2.modifiers.remove(m)
 elif m.type=='ARMATURE':m.object=r2
install_faces(a2);nt=a2.data.materials[1].node_tree;illum=neutral_light(nt)
for n in list(nt.nodes):
 if n.type=='VERTEX_COLOR'and n.layer_name=='PS1FaceLightFit':
  for link in list(n.outputs['Color'].links):nt.links.new(illum,link.to_socket)
a2.data.materials[1]['DeryNeutralLight']=True;precision(a2,True)
for obj in objects:precision(obj)
head_museum=toward(r2,(21.2,-4.3,2.15));head_close=toward(r2,(21.1,-2.2,1.82));head_art=toward(r2,(left_x,-.15,1.70));head_tape=toward(r2,(right_x,-.15,1.50))
bpy.context.view_layer.update();shoulders2={side:r2.matrix_world@r2.pose.bones['arm_'+side].head for side in ['R','L']};w2={};p2={};front2=Vector((math.sin(.2),-math.cos(.2),0))
for side in ['R','L']:
 w2[side]=empty('MUSEUM | '+side+' wrist');ik=r2.pose.bones['forearm_'+side].constraints.new('IK');ik.target=w2[side];ik.chain_count=2;ik.use_stretch=False
 p2[side]=empty('MUSEUM | '+side+' palm');p2[side].rotation_mode='QUATERNION';c=r2.pose.bones['hand_'+side].constraints.new('COPY_ROTATION');c.target=p2[side];c.owner_space='WORLD';c.target_space='WORLD'
MR=[(0,(.14,.08,-.34,0)),(12.3,(.14,.08,-.34,0)),(12.7,(.23,.10,-.14,.75)),(13.4,(.23,.10,-.14,.75)),(14.3,(.14,.08,-.34,0)),(17.4,(.14,.08,-.34,0)),(17.85,(.24,.11,-.13,.8)),(18.5,(.24,.11,-.13,.8)),(19.4,(.14,.08,-.34,0)),(23,(.14,.08,-.34,0)),(23.4,(.25,.10,-.11,.9)),(24.0,(.25,.10,-.11,.9)),(24.6,(.14,.08,-.34,0)),(26.9,(.14,.08,-.34,0)),(27.3,(.22,.10,-.15,.8)),(28.1,(.22,.10,-.15,.8)),(29.4,(.14,.08,-.34,0)),(39.2,(.14,.08,-.34,0)),(39.7,(.23,.10,-.14,.75)),(40.45,(.23,.10,-.14,.75)),(41.2,(.14,.08,-.34,0)),(41.8,(.14,.08,-.34,0)),(42.15,(.25,.10,-.12,.85)),(42.85,(.25,.10,-.12,.85)),(43.55,(.14,.08,-.34,0))]
ML=[(0,(.14,.08,-.34,0)),(19.55,(.14,.08,-.34,0)),(19.95,(.24,.09,-.15,.8)),(20.7,(.24,.09,-.15,.8)),(21.7,(.14,.08,-.34,0)),(23.25,(.14,.08,-.34,0)),(23.8,(.22,.11,-.16,.7)),(24.2,(.22,.11,-.16,.7)),(24.95,(.14,.08,-.34,0)),(27.5,(.14,.08,-.34,0)),(27.9,(.17,.10,-.24,.4)),(28.3,(.17,.10,-.24,.4)),(29.4,(.14,.08,-.34,0)),(44.1,(.14,.08,-.34,0))]
for m in list(s.timeline_markers):s.timeline_markers.remove(m)
for sh in info['shots']:s.timeline_markers.new(f"{sh['id']:02d} | {sh['kind']} | {sh['mood']}",frame=sh['start'])
faces={'room':[],'museum':[]}
for f in range(1,N+1):
 t=(f-1)/24;sh=next(x for x in info['shots']if x['start']<=f<=x['end']);mood=sh['mood'];u=(f-sh['start'])/max(1,sh['end']-sh['start']);speaking=talk(t)
 for name,q in base.items():r.pose.bones[name].rotation_quaternion=q
 gaze=curve([(0,.7),(2.1,.7),(2.55,0),(3.8,0),(5.1,.4),(5.6,0),(7.6,.1),(35.9,.4),(36.3,0),(37.8,0),(38.8,.3),(39.2,0)],t)
 r.pose.bones['head'].rotation_quaternion=(head_side if mood=='sigh'else head_cam).slerp(head_monitor,gaze)
 tilt=curve([(0,0),(2.5,-.025),(3.1,-.025),(3.8,0),(5.45,.06),(6.7,.06),(7.7,0),(36,.015),(36.5,-.035),(37.5,-.035),(38.8,0)],t)
 r.pose.bones['head'].rotation_quaternion@=rest['head'].inverted()@Quaternion((0,1,0),tilt)@rest['head']
 lean=curve([(0,0),(2.45,-.025),(3.1,-.025),(3.8,0),(5.55,.065),(6.8,.065),(7.7,0),(35.9,0),(36.35,-.035),(37.55,-.035),(39,0)],t)
 r.pose.bones['upper_chest'].rotation_quaternion@=rest['upper_chest'].inverted()@Quaternion((1,0,0),lean)@rest['upper_chest']
 for side,sign,keys in [('R',-1,R),('L',1,L)]:
  fw,ou,z,roll=curve(keys,t);out=Vector((math.cos(.6)*sign,math.sin(.6)*sign,0));w=bpy.data.objects['R3 | '+side+' wrist'];w.location=shoulders[side]+front*fw+out*ou+up*z;H.record(w,'location',f)
  direction=(front*.75+up*(-.75+2.4*smooth((z+.29)/.33))).normalized();orient[side].rotation_quaternion=direction.to_track_quat('Y','Z')@Quaternion((0,1,0),sign*roll);H.record(orient[side],'rotation_quaternion',f)
 for p in r.pose.bones:H.record(p,'rotation_quaternion',f)
 face=(12 if speaking else 20)if t<3.8 else(16 if speaking else 18)if t<35.9 else(24 if speaking else 23)
 if any(b<=t<b+.083 for b in [3.1,6.7,36.95,38.65]):face=10
 a['PS1_face_id']=face;a.keyframe_insert(data_path='["PS1_face_id"]',frame=f)
 if not faces['room']or faces['room'][-1]['id']!=face:faces['room'].append(dict(frame=f,id=face))
 for p in r2.pose.bones:p.rotation_quaternion=Quaternion()
 hq=head_close if mood in ['laugh','relax','forgive']else head_museum
 glance=curve([(0,0),(12.3,0),(12.9,.7),(13.5,.7),(14.3,0),(17.4,.4),(18.3,.4),(19.3,0),(19.96,.6),(21.5,.6),(23,0),(23.5,.2),(24.3,.2),(25,0),(26.9,.15),(27.6,0),(39.2,0),(40.4,0),(44.1,0)],t)
 exhibit=head_tape if 19.5<t<22 else head_art;r2.pose.bones['head'].rotation_quaternion=hq.slerp(exhibit,glance)
 nod=curve([(0,0),(12.6,-.025),(13.2,-.025),(14.3,0),(23,.025),(23.4,-.025),(24,.025),(24.6,0),(26.9,.035),(27.4,-.03),(28,.025),(28.7,0),(39.5,-.025),(40.5,-.025),(41.4,0),(42.2,.035),(43.3,.01)],t)
 r2.pose.bones['upper_chest'].rotation_quaternion=rest['upper_chest'].inverted()@Quaternion((1,0,0),nod)@rest['upper_chest']
 for side,sign,keys in [('R',-1,MR),('L',1,ML)]:
  fw,ou,z,roll=curve(keys,t);out=Vector((math.cos(.2)*sign,math.sin(.2)*sign,0));w2[side].location=shoulders2[side]+front2*fw+out*ou+up*z;H.record(w2[side],'location',f)
  direction=(front2*.75+up*(-.8+2.3*smooth((z+.34)/.36))).normalized();p2[side].rotation_quaternion=direction.to_track_quat('Y','Z')@Quaternion((0,1,0),sign*roll);H.record(p2[side],'rotation_quaternion',f)
 for p in r2.pose.bones:H.record(p,'rotation_quaternion',f)
 face2=(12 if speaking else 20)if t<23 else(3 if speaking else 2)if t<29.62 else(12 if speaking else 2)if t<41.8 else(3 if speaking else 2)
 if any(b<=t<b+.083 for b in [13.6,18.8,24.55,28.7,40.9]):face2=10
 a2['PS1_face_id']=face2;a2.keyframe_insert(data_path='["PS1_face_id"]',frame=f)
 if not faces['museum']or faces['museum'][-1]['id']!=face2:faces['museum'].append(dict(frame=f,id=face2))
 artroot.location.z=curve([(0,0),(23.1,0),(23.3,.07),(23.6,0),(44.1,0)],t);taperoot.location.z=curve([(0,0),(23.35,0),(23.55,.07),(23.85,0),(44.1,0)],t);H.record(artroot,'location',f);H.record(taperoot,'location',f)
 if sh['kind']=='museum':
  if mood=='cassette':cam.location=(right_x+.12,-1.65,1.60);target=Vector((right_x,.17,1.39));lens=48 if WIDE else 25
  elif mood in ['laugh','relax','forgive']:cam.location=(21.1,-2.2,1.82);target=Vector((20,-.25,1.56));lens=48
  else:cam.location=(21.2,-4.3+.025*u,2.15)if WIDE else(20.65,-4.7+.025*u,2.05);target=Vector((20,.15,1.27));lens=33 if WIDE else 27
 elif sh['kind']=='monitor':cam.location=(1.15,.28,1.55);target=Vector((.1095,-.7959,1.262));lens=wide_monitor_lens if WIDE else 39
 elif mood=='sigh':cam.location=(1.8,-.45,1.55);target=Vector((0,.10,1.39));lens=60
 else:cam.location=(2.1-.025*u,-.85+.015*u,1.65);target=Vector((0,.10,1.18));lens=42
 cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;H.record(cam,'location',f);H.record(cam,'rotation_euler',f);H.record(cam.data,'lens',f)
H.commit_curves()
for obj in [a,a2]:
 for fc in obj.animation_data.action.fcurves:
  for k in fc.keyframe_points:k.interpolation='CONSTANT'
(ROOT/'face_cues.json').write_text(json.dumps(faces,indent=2));(ROOT/'acting_cues.json').write_text(json.dumps(dict(method='Asymmetric phrase gestures with preparation, holds and rests; single warning and forgiving presentation; no conversation loop.',right=R,left=L,museum_right=MR,museum_left=ML,reference='Private gesture reference retained from episode 007; not republished.'),indent=2))
s['DeryPS1Look']=f'{405 if WIDE else 128}x228 seam-safe geometry precision; 128px body texture addressing; 5-bit RGB and fixed ordered dither at export';s['DeryFormats']='9:16 and 16:9, independent cameras and graphic layouts.'
s.sequence_editor_create().sequences.new_sound('VOZ | supplied recording',str(ROOT/'assets/voz/narracao_mix.wav'),channel=1,frame_start=1)
s.frame_set(80);bpy.data.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();(ROOT/'output').mkdir(exist_ok=True);dest=ROOT/'output'/('Dery_Ankha_Master_16x9.blend'if WIDE else'Dery_Ankha.blend');bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
for t in [6.0,13.2,20.6,24.0,28.0,37.5,42.5]:
 f=round(t*24)+1;sh=next(x for x in info['shots']if x['start']<=f<=x['end']);museum=sh['kind']=='museum'
 for o in s.objects:
  if o.type=='MESH':o.hide_render=(not museum)if o.name.startswith('MUSEUM |')else museum
 s.frame_set(f);s.render.filepath=str(ROOT/f"output/preview_{'wide_'if WIDE else ''}{f:04d}.png");bpy.ops.render.render(write_still=True)
print('ANKHA_SCENE_READY',flush=True)
