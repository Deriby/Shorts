"""Phrase-led acting, discrete faces, PS1 precision and a small castle vignette."""
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
# Gestures have different preparation, stroke, hold and release; hands do not loop.
R=[(0,(.17,.10,-.30,0)),(2.4,(.17,.10,-.30,0)),(2.72,(.16,.10,-.19,.15)),(3.18,(.28,.11,-.065,.8)),(3.55,(.28,.11,-.065,.8)),(4.18,(.21,.12,-.17,.35)),(4.8,(.17,.10,-.30,0)),(11.32,(.17,.10,-.30,0)),(11.75,(.27,.10,.025,.15)),(12.15,(.27,.10,.025,.15)),(12.55,(.21,.13,-.075,.3)),(13.22,(.17,.10,-.30,0)),(20.42,(.17,.10,-.30,0)),(20.82,(.23,.06,-.12,.85)),(21.3,(.27,.08,-.08,1.05)),(21.75,(.27,.08,-.08,1.05)),(22.4,(.20,.12,-.17,.5)),(23.55,(.17,.10,-.30,0)),(30.2,(.17,.10,-.30,0)),(30.55,(.14,.01,-.075,-.2)),(31.1,(.14,.01,-.075,-.2)),(31.72,(.17,.10,-.30,0)),(35.9,(.17,.10,-.30,0)),(36.3,(.28,.03,-.11,.85)),(37.05,(.28,.03,-.11,.85)),(37.65,(.19,.12,-.32,.05)),(38.18,(.17,.10,-.30,0))]
L=[(0,(.19,.10,-.29,0)),(2.95,(.19,.10,-.29,0)),(3.38,(.21,.14,-.16,.6)),(3.72,(.21,.14,-.16,.6)),(4.5,(.19,.10,-.29,0)),(11.35,(.19,.10,-.29,0)),(11.95,(.25,.12,.005,.15)),(12.4,(.25,.12,.005,.15)),(13.15,(.19,.10,-.29,0)),(21.3,(.19,.10,-.29,0)),(21.9,(.23,.13,-.11,.9)),(22.55,(.23,.13,-.11,.9)),(23.5,(.19,.10,-.29,0)),(36.3,(.19,.10,-.29,0)),(36.78,(.20,.14,-.19,.55)),(37.2,(.20,.14,-.19,.55)),(38.1,(.19,.10,-.29,0))]
orient={}
for side in ['R','L']:
 o=empty('ACTING | '+side+' palm');o.rotation_mode='QUATERNION';orient[side]=o;c=r.pose.bones['hand_'+side].constraints.new('COPY_ROTATION');c.name='ACTING | palm follow through';c.target=o;c.owner_space='WORLD';c.target_space='WORLD'
# One small low-poly castle entrance; no full Lady model or expensive simulation.
stone=H.material('CASTLE | grey stone',(.20,.19,.18),lit=False);dark=H.material('CASTLE | deep shadow',(.025,.018,.027),lit=False);door_mat=H.material('CASTLE | old wood',(.13,.075,.035),lit=False);gold=H.material('CASTLE | aged bronze',(.35,.19,.06),lit=False);orange=H.material('CASTLE | amber flame',(1,.29,.025),lit=False)
castle_objs=[]
def box(name,loc,size,mat):
 o=H.box('CASTLE | '+name,loc,size,mat);castle_objs.append(o);return o
box('floor',(20,-.4,-.07),(12 if WIDE else 7,8 if WIDE else 6,.12),stone);box('wall',(20,1,1.7),(10 if WIDE else 6,.14,3.5),stone);box('door',(20.25,.90,1.45),(1.65,.12,2.9),door_mat)
for x in [19.25,21.25]:
 box('column',(x,.64,1.5),(.24,.34,3),gold)
 for z in [.08,2.96]:box('capital',(x,.64,z),(.43,.46,.17),stone)
box('lintel',(20.25,.64,3.15),(2.4,.40,.24),stone)
for x in [19.75,20.05,20.35,20.65]:box('plank joint',(x,.815,1.45),(.018,.022,2.75),dark)
for z in [.45,1.48,2.48]:box('iron door strap',(20.25,.805,z),(1.58,.025,.085),gold)
handle=H.torus('CASTLE | ring handle',(20.83,.75,1.38),.08,.017,gold,rot=(math.pi/2,0,0),segments=8);castle_objs.append(handle)
for x in [18.7,21.9]:
 box('sconce',(x,.61,1.8),(.13,.19,.4),dark)
 flame=H.mesh('CASTLE | flame',[(x-.08,.48,1.96),(x+.08,.48,1.96),(x+.05,.48,2.16),(x-.015,.48,2.31),(x-.055,.48,2.12)],[(0,1,2,3,4)],orange);castle_objs.append(flame)
# Pixel-size stone tiles and subdued values make the stage read as PS1 geometry.
im=bpy.data.images.new('CASTLE | 64px stone',64,64);pixels=[]
for y in range(64):
 for x in range(64):
  edge=y%16 in [0,1]or(x+(8 if(y//16)%2 else 0))%16 in [0,1];v=.095 if edge else .19+((x*7+y*3)%5)*.006;pixels.extend((v,v*.96,v*.91,1))
im.pixels=pixels;im.pack();nt=stone.node_tree;tx=nt.nodes.new('ShaderNodeTexImage');tx.image=im;tx.interpolation='Closest';co=nt.nodes.new('ShaderNodeTexCoord');nt.links.new(co.outputs['Generated'],tx.inputs['Vector']);tx.projection='BOX';em=next(n for n in nt.nodes if n.type=='EMISSION');nt.links.new(tx.outputs[0],em.inputs['Color'])
# Flat moving silhouette on the rear wall implies a tall woman off camera.
xy=[(-.28,0),(.28,0),(.21,.43),(.18,1.55),(.40,1.80),(.37,2.18),(.20,2.28),(.14,2.47),(.17,2.58),(.53,2.64),(.48,2.74),(.22,2.76),(.13,2.94),(-.13,2.94),(-.22,2.76),(-.53,2.74),(-.55,2.64),(-.17,2.58),(-.14,2.47),(-.20,2.28),(-.37,2.18),(-.40,1.80),(-.18,1.55),(-.21,.43)]
shadow=H.mesh('CASTLE | hat silhouette',[(x,.775,z)for x,z in xy],[tuple(range(len(xy)))],dark);shadow.location.x=20.75
r2=r.copy();r2.data=r.data.copy();r2.name='CASTLE | Dery rig';s.collection.objects.link(r2);r2.animation_data_clear();r2.parent=None;r2.location=(19.75,-.25,0);r2.rotation_euler=(0,0,.2)
for p in r2.pose.bones:
 p.matrix_basis=Matrix.Identity(4)
 for c in list(p.constraints):p.constraints.remove(c)
a2=a.copy();a2.data=a.data.copy();a2.name='CASTLE | Dery';s.collection.objects.link(a2);a2.animation_data_clear();a2.parent=r2;a2.matrix_parent_inverse=Matrix.Identity(4);a2.location=(0,0,0);a2.rotation_euler=(0,0,0)
for m in list(a2.modifiers):
 if m.type=='NODES':a2.modifiers.remove(m)
 elif m.type=='ARMATURE':m.object=r2
install_faces(a2);nt=a2.data.materials[1].node_tree;illum=neutral_light(nt)
for n in list(nt.nodes):
 if n.type=='VERTEX_COLOR'and n.layer_name=='PS1FaceLightFit':
  for link in list(n.outputs['Color'].links):nt.links.new(illum,link.to_socket)
a2.data.materials[1]['DeryNeutralLight']=True;precision(a2,True)
head_castle=toward(r2,(21.2,-4.3,2.15));bpy.context.view_layer.update();shoulders2={side:r2.matrix_world@r2.pose.bones['arm_'+side].head for side in ['R','L']};w2={};p2={};front2=Vector((math.sin(.2),-math.cos(.2),0))
for side in ['R','L']:
 w2[side]=empty('CASTLE | '+side+' wrist');ik=r2.pose.bones['forearm_'+side].constraints.new('IK');ik.target=w2[side];ik.chain_count=2;ik.use_stretch=False
 p2[side]=empty('CASTLE | '+side+' palm');p2[side].rotation_mode='QUATERNION';c=r2.pose.bones['hand_'+side].constraints.new('COPY_ROTATION');c.target=p2[side];c.owner_space='WORLD';c.target_space='WORLD'
for obj in castle_objs:precision(obj)
precision(shadow)
for m in list(s.timeline_markers):s.timeline_markers.remove(m)
for sh in info['shots']:s.timeline_markers.new(f"{sh['id']:02d} | {sh['kind']} | {sh['mood']}",frame=sh['start'])
face_events=[]
for f in range(1,N+1):
 t=(f-1)/24;sh=next(x for x in info['shots']if x['start']<=f<=x['end']);mood=sh['mood'];u=(f-sh['start'])/max(1,sh['end']-sh['start']);speaking=talk(t)
 for name,q in base.items():r.pose.bones[name].rotation_quaternion=q
 gaze=curve([(0,.6),(2.4,.6),(2.95,0),(4.8,0),(5.4,.8),(6.8,.1),(11.35,.1),(11.8,0),(20.4,.8),(21.15,0),(23.6,0),(30.2,0),(31.0,.45),(31.6,0),(36.6,.55),(37.2,0),(39,0)],t)
 hq=head_side if mood=='embarrassed'or(WIDE and mood=='final')else head_final if mood=='final'else head_cam;r.pose.bones['head'].rotation_quaternion=hq.slerp(head_monitor,gaze)
 tilt=curve([(0,0),(2.8,-.045),(3.5,.025),(4.8,0),(11.7,-.03),(12.5,.04),(13.2,0),(20.5,.08),(22.2,.08),(23.6,0),(30.2,-.075),(31.4,-.075),(31.8,0),(37,.035),(38.5,0)],t)
 r.pose.bones['head'].rotation_quaternion@=rest['head'].inverted()@Quaternion((0,1,0),tilt)@rest['head']
 lean=curve([(0,0),(2.5,.03),(3.2,-.055),(4.4,-.02),(11.4,.025),(12,.045),(13.1,-.01),(20.4,0),(21,-.05),(22.6,-.025),(23.5,0),(30.2,.04),(31,.06),(31.8,0),(36.6,-.04),(37.5,.02),(38.4,.01)],t)
 r.pose.bones['upper_chest'].rotation_quaternion@=rest['upper_chest'].inverted()@Quaternion((1,0,0),lean)@rest['upper_chest']
 for side,sign,keys in [('R',-1,R),('L',1,L)]:
  fw,ou,z,roll=curve(keys,t);outward=Vector((math.cos(.6)*sign,math.sin(.6)*sign,0));w=bpy.data.objects['R3 | '+side+' wrist'];w.location=shoulders[side]+front*fw+outward*ou+up*z;H.record(w,'location',f)
  direction=(front*.75+up*(-.75+2.4*smooth((z+.29)/.33))).normalized();orient[side].rotation_quaternion=direction.to_track_quat('Y','Z')@Quaternion((0,1,0),sign*roll);H.record(orient[side],'rotation_quaternion',f)
 for p in r.pose.bones:H.record(p,'rotation_quaternion',f)
 face=(5 if t<3.25 else 11 if speaking else 4)if mood=='opposite'else(12 if speaking else 20)if mood in ['name','height','career']else(24 if speaking else 5)if mood=='claws'else(16 if speaking else 22)if mood=='strange'else(11 if speaking else 9)if mood=='embarrassed'else(16 if speaking else 6)
 if any(b<=t<b+.083 for b in [3.92,6.10,12.88,21.8,30.8,37.9]):face=10
 a['PS1_face_id']=face;a.keyframe_insert(data_path='["PS1_face_id"]',frame=f)
 if not face_events or face_events[-1]['id']!=face:face_events.append(dict(frame=f,id=face))
 # Castle gestures: one height indication, then a different defensive recoil.
 for p in r2.pose.bones:p.rotation_quaternion=Quaternion()
 r2.pose.bones['head'].rotation_quaternion=head_castle@rest['head'].inverted()@Quaternion((1,0,0),-.24 if mood=='height'else .10)@rest['head']
 shock=smooth((t-26.15)/.33);r2.pose.bones['upper_chest'].rotation_quaternion=rest['upper_chest'].inverted()@Quaternion((1,0,0),.10*shock if mood=='escape'else-.025)@rest['upper_chest']
 for side,sign in [('R',-1),('L',1)]:
  out=Vector((math.cos(.2)*sign,math.sin(.2)*sign,0));lift=curve([(0,0),(16.44,0),(16.85,.27),(17.5,.30),(18.2,.30),(18.8,0),(25.82,0),(26.22,.18),(27,.18),(28.4,.03)],t)if side=='R'else curve([(0,0),(17.1,0),(17.55,.025),(18.15,.025),(18.8,0),(25.82,0),(26.5,.04),(27.3,.04),(28.6,0)],t)
  w2[side].location=shoulders2[side]+front2*(.14+.04*shock)+out*.08+up*(-.34+lift*2);H.record(w2[side],'location',f)
  direction=(front2*.30+up*(-1+lift*7)).normalized();p2[side].rotation_quaternion=direction.to_track_quat('Y','Z')@Quaternion((0,1,0),sign*.2);H.record(p2[side],'rotation_quaternion',f)
 for p in r2.pose.bones:H.record(p,'rotation_quaternion',f)
 a2['PS1_face_id']=26 if mood=='height'else 5 if t<26.7 else 25;a2.keyframe_insert(data_path='["PS1_face_id"]',frame=f);a2.hide_render=sh['kind']!='castle';a2.keyframe_insert(data_path='hide_render',frame=f)
 shadow.location.x=curve([(0,21),(16.44,21),(18.8,20.35),(25.82,20.95),(28.66,20.35)],t);H.record(shadow,'location',f)
 if sh['kind']=='castle':cam.location=(21.2,-4.3+.05*u,2.15);target=Vector((20.12,.35,1.47));lens=33
 elif sh['kind']=='monitor':cam.location=(1.15,.28,1.55);target=Vector((.1095,-.7959,1.262));lens=wide_monitor_lens if WIDE else 39
 elif mood=='embarrassed':cam.location=(1.8,-.45,1.55);target=Vector((0,.10,1.41));lens=68
 elif mood=='final':cam.location=(1.8,-.45,1.57)if WIDE else(1.25,-1.25,1.56);target=Vector((0,.10,1.40));lens=57
 else:cam.location=(2.1-.025*u,-.85+.015*u,1.65);target=Vector((0,.10,1.18));lens=42
 cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;H.record(cam,'location',f);H.record(cam,'rotation_euler',f);H.record(cam.data,'lens',f)
H.commit_curves()
for obj in [a,a2]:
 for fc in obj.animation_data.action.fcurves:
  for k in fc.keyframe_points:k.interpolation='CONSTANT'
(ROOT/'face_cues.json').write_text(json.dumps(face_events,indent=2));(ROOT/'acting_cues.json').write_text(json.dumps(dict(method='Distinct phrase gestures with preparation, stroke, holds and asymmetric follow-through; no periodic arm loop.',right=R,left=L,reference='User talking reference from episode 007; personal video kept private.'),indent=2))
s['DeryPS1Look']=f'{405 if WIDE else 128}x228 seam-safe vertex precision; 128px body texture addressing; 5-bit RGB + ordered dithering at export';s['DeryFormats']='First 9:16; run build_short.py --wide for future 16:9 with the same acting.'
s.sequence_editor_create().sequences.new_sound('VOZ | supplied recording',str(ROOT/'assets/voz/narracao_mix.wav'),channel=1,frame_start=1)
s.frame_set(80);bpy.data.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();(ROOT/'output').mkdir(exist_ok=True);dest=ROOT/'output'/('Dery_Lady_Master_16x9.blend'if WIDE else'Dery_Lady_Dimitrescu.blend');bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
for t in [3.3,5.8,12.1,17.5,21.5,26.8,30.8,37.6]:
 s.frame_set(round(t*24)+1);s.render.filepath=str(ROOT/f"output/preview_{'wide_'if WIDE else ''}{round(t*24)+1:04d}.png");bpy.ops.render.render(write_still=True)
print('LADY_SCENE_READY',flush=True)
