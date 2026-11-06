"""Horizontal intro: a single room action with a pullback, case archive and motivated handoff."""
from pathlib import Path
import sys,json,math,wave,array,bpy
from mathutils import Vector,Quaternion,Matrix
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parent;REPO=next(p for p in ROOT.parents if(p/'AGENTS.md').exists());WIDE=True
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
 wide_monitor_lens=39*min(.98/width,.94/height)

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



# Each gesture belongs to a complete idea, with rests between intentions.
R=[(0,(.17,.10,-.30,0)),(8.5,(.17,.10,-.30,0)),(9.3,(.23,.10,-.18,.65)),(10.3,(.23,.10,-.18,.65)),(11.2,(.17,.10,-.30,0)),(11.8,(.17,.10,-.30,0)),(12.2,(.24,.09,-.15,.75)),(13.1,(.24,.09,-.15,.75)),(13.9,(.17,.10,-.30,0)),(17.0,(.17,.10,-.30,0)),(17.5,(.25,.10,-.13,.8)),(19.4,(.25,.10,-.13,.8)),(20.5,(.17,.10,-.30,0)),(24.5,(.17,.10,-.30,0)),(24.9,(.18,.12,-.26,.5)),(25.8,(.18,.12,-.26,.5)),(26.9,(.17,.10,-.30,0)),(32.9,(.17,.10,-.30,0))]
L=[(0,(.19,.10,-.29,0)),(13.3,(.19,.10,-.29,0)),(13.9,(.23,.10,-.17,.7)),(15.1,(.23,.10,-.17,.7)),(16.2,(.19,.10,-.29,0)),(21.5,(.19,.10,-.29,0)),(22.0,(.24,.10,-.16,.7)),(22.9,(.24,.10,-.16,.7)),(23.9,(.19,.10,-.29,0)),(27.4,(.19,.10,-.29,0)),(27.8,(.24,.09,-.14,.8)),(28.7,(.24,.09,-.14,.8)),(29.7,(.19,.10,-.29,0)),(32.9,(.19,.10,-.29,0))]
orient={}
for side in ['R','L']:
 o=empty('INTRO | '+side+' palm');o.rotation_mode='QUATERNION';orient[side]=o;c=r.pose.bones['hand_'+side].constraints.new('COPY_ROTATION');c.target=o;c.owner_space='WORLD';c.target_space='WORLD'
for marker in list(s.timeline_markers):s.timeline_markers.remove(marker)
for sh in info['shots']:s.timeline_markers.new(sh['description'],frame=sh['start'])
faces=[]
def camera_pose(t):
 # The physical camera only leaves the screen to reveal who is presenting.
 pull=smooth((t-9.0)/2.6)
 start=Vector((1.15,.28,1.55));host=Vector((2.05,-.80,1.64));screen_target=Vector((.1095,-.7959,1.262));host_target=Vector((0,.10,1.25))
 loc=start.lerp(host,pull);target=screen_target.lerp(host_target,pull);lens=wide_monitor_lens+(42-wide_monitor_lens)*pull
 drift=smooth((t-12.0)/10.0);loc+=Vector((-.10,-.10,.01))*drift;lens+=2*drift
 push=smooth((t-28.1)/3.4)
 if t>=28.1:loc=loc.lerp(start,push);target=target.lerp(screen_target,push);lens=lens+(wide_monitor_lens-lens)*push
 return loc,target,lens
for f in range(1,N+1):
 t=(f-1)/24;speaking=talk(t)
 for name,q in base.items():r.pose.bones[name].rotation_quaternion=q
 gaze=curve([(0,1),(8.5,1),(9.5,1),(11.5,0),(12.0,.2),(13.2,.2),(15.5,.2),(16.7,0),(20.7,0),(21.5,.6),(23.5,.6),(24.5,0),(26.8,0),(27.5,.15),(28.2,1),(32.9,1)],t)
 r.pose.bones['head'].rotation_quaternion=head_cam.slerp(head_monitor,gaze)
 tilt=curve([(0,0),(9.3,.025),(10.3,.025),(11.5,0),(13.9,-.02),(15.1,-.02),(16.2,0),(17.5,-.025),(19.4,-.025),(20.5,0),(22,.035),(23,.035),(24.5,0),(24.9,.05),(25.8,.05),(27.4,0),(28.0,-.02),(29,-.02),(31,0)],t)
 r.pose.bones['head'].rotation_quaternion@=rest['head'].inverted()@Quaternion((0,1,0),tilt)@rest['head']
 lean=curve([(0,0),(9.3,.025),(10.3,.025),(11.5,0),(12.2,-.02),(13.1,-.02),(13.9,0),(17.5,-.03),(19.4,-.03),(20.5,0),(22,.035),(23,.035),(24.5,0),(24.9,.045),(25.8,.045),(26.9,0),(27.8,-.02),(28.7,-.02),(30,0)],t)
 r.pose.bones['upper_chest'].rotation_quaternion@=rest['upper_chest'].inverted()@Quaternion((1,0,0),lean)@rest['upper_chest']
 for side,sign,keys in [('R',-1,R),('L',1,L)]:
  fw,ou,z,roll=curve(keys,t);out=Vector((math.cos(.6)*sign,math.sin(.6)*sign,0));w=bpy.data.objects['R3 | '+side+' wrist'];w.location=shoulders[side]+front*fw+out*ou+up*z;H.record(w,'location',f)
  direction=(front*.75+up*(-.75+2.4*smooth((z+.29)/.33))).normalized();orient[side].rotation_quaternion=direction.to_track_quat('Y','Z')@Quaternion((0,1,0),sign*roll);H.record(orient[side],'rotation_quaternion',f)
 for p in r.pose.bones:H.record(p,'rotation_quaternion',f)
 face=(24 if speaking else 23)if t<8.5 else(16 if speaking else 18)if t<11.5 else(12 if speaking else 2)if t<21.2 else(16 if speaking else 4)if t<27.5 else(11 if speaking else 4)
 if any(b<=t<b+.083 for b in [10.7,13.7,17.1,20.2,24.4,27.3,30.5]):face=10
 a['PS1_face_id']=face;a.keyframe_insert(data_path='["PS1_face_id"]',frame=f)
 if not faces or faces[-1]['id']!=face:faces.append(dict(frame=f,id=face))
 loc,target,lens=camera_pose(t);cam.location=loc;cam.rotation_euler=(target-loc).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
 H.record(cam,'location',f);H.record(cam,'rotation_euler',f);H.record(cam.data,'lens',f)
H.commit_curves()
for fc in a.animation_data.action.fcurves:
 for key in fc.keyframe_points:key.interpolation='CONSTANT'
(ROOT/'face_cues.json').write_text(json.dumps(faces,indent=2));(ROOT/'acting_cues.json').write_text(json.dumps(dict(method='Continuous room situation: reveal presenter from the interrupted call, present case archive, discard an unwanted folder, select Lady. Phrase gestures with preparation, holds and returns; no periodic conversation loop.',right=R,left=L,camera=dict(pullback=[9,11.6],quiet_drift=[12,22],push_in=[28.1,31.5]),reference='Private gesture reference from episode 007; not republished.'),indent=2))
s['DeryPS1Look']='405x228 seam-safe precision; Closest 128px texture addressing; 5-bit RGB ordered dither at export';s['DeryFormats']='16:9 only';s['IntroPictureCuts']=2
s.sequence_editor_create().sequences.new_sound('VOZ | supplied intro',str(ROOT/'assets/voz/narracao_mix.wav'),channel=1,frame_start=1)
s.frame_set(300);bpy.data.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();(ROOT/'output').mkdir(exist_ok=True)
dest=ROOT/'output/Dery_Intro_Personagens_16x9.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
for t in [8.5,10.3,11.8,15.2,18.3,23,25.3,28.2,30.5,31.6]:
 f=round(t*24)+1;s.frame_set(f);s.render.filepath=str(ROOT/f'output/preview_{f:04d}.png');bpy.ops.render.render(write_still=True)
print('INTRO_SCENE_READY',flush=True)
