"""Horizontal closing: one warm room take, a brief farewell gesture and the approved M."""
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



R=[(0,(.17,.10,-.30,0)),(.45,(.17,.10,-.30,0)),(.85,(.22,.10,-.20,.55)),(1.75,(.22,.10,-.20,.55)),(2.5,(.17,.10,-.30,0)),(2.8,(.17,.10,-.30,0)),(3.2,(.23,.11,-.17,.7)),(4.8,(.23,.11,-.17,.7)),(5.8,(.17,.10,-.30,0)),(9.7,(.17,.10,-.30,0)),(10.1,(.24,.10,-.14,.85)),(10.9,(.24,.10,-.14,.85)),(11.8,(.17,.10,-.30,0)),(14.8,(.17,.10,-.30,0)),(15.2,(.17,.12,-.18,.55)),(15.8,(.16,.21,.10,.8)),(16.4,(.16,.21,.10,1.15)),(17.0,(.16,.21,.10,.75)),(17.6,(.16,.21,.10,1.1)),(18.25,(.16,.21,.08,1.0)),(19.25,(.20,.11,-.18,.5)),(19.9,(.17,.10,-.30,0)),(21.3,(.17,.10,-.30,0))]
L=[(0,(.19,.10,-.29,0)),(6.2,(.19,.10,-.29,0)),(6.6,(.24,.09,-.15,.8)),(8.5,(.24,.09,-.15,.8)),(9.3,(.19,.10,-.29,0)),(11.7,(.19,.10,-.29,0)),(12.15,(.24,.10,-.16,.7)),(13.3,(.24,.10,-.16,.7)),(14.3,(.19,.10,-.29,0)),(15.0,(.19,.10,-.29,0)),(15.4,(.19,.13,-.22,.45)),(16.3,(.19,.13,-.22,.45)),(17.3,(.19,.10,-.29,0)),(21.3,(.19,.10,-.29,0))]
orient={}
for side in ['R','L']:
 o=empty('OUTRO | '+side+' palm');o.rotation_mode='QUATERNION';orient[side]=o;c=r.pose.bones['hand_'+side].constraints.new('COPY_ROTATION');c.target=o;c.owner_space='WORLD';c.target_space='WORLD'
for marker in list(s.timeline_markers):s.timeline_markers.remove(marker)
for sh in info['shots']:s.timeline_markers.new(sh['description'],frame=sh['start'])
faces=[]
for f in range(1,N+1):
 t=(f-1)/24;speaking=talk(t)
 for name,q in base.items():r.pose.bones[name].rotation_quaternion=q
 gaze=curve([(0,0),(2.4,0),(3.0,.25),(4.4,.25),(5.8,0),(6.2,0),(7.4,.2),(8.5,.2),(9.3,0),(10,.4),(10.8,.4),(11.8,0),(14.5,0),(21.3,0)],t)
 r.pose.bones['head'].rotation_quaternion=head_cam.slerp(head_monitor,gaze)
 tilt=curve([(0,0),(.85,-.02),(1.75,-.02),(2.5,0),(3.2,.035),(4.8,.035),(5.8,0),(6.6,-.02),(8.5,-.02),(9.3,0),(10.1,.015),(10.9,.015),(11.8,0),(15.2,-.04),(16.8,-.04),(17.6,-.015),(18.3,-.015),(19.5,0)],t)
 r.pose.bones['head'].rotation_quaternion@=rest['head'].inverted()@Quaternion((0,1,0),tilt)@rest['head']
 lean=curve([(0,0),(.85,-.02),(1.75,-.02),(2.5,0),(3.2,.025),(4.8,.025),(5.8,0),(6.6,-.025),(8.5,-.025),(9.3,0),(10.1,-.02),(10.9,-.02),(11.8,0),(12.15,-.015),(13.3,-.015),(14.3,0),(15.2,-.03),(17.3,-.03),(18.3,-.015),(19.5,0)],t)
 r.pose.bones['upper_chest'].rotation_quaternion@=rest['upper_chest'].inverted()@Quaternion((1,0,0),lean)@rest['upper_chest']
 for side,sign,keys in [('R',-1,R),('L',1,L)]:
  fw,ou,z,roll=curve(keys,t);out=Vector((math.cos(.6)*sign,math.sin(.6)*sign,0));w=bpy.data.objects['R3 | '+side+' wrist'];w.location=shoulders[side]+front*fw+out*ou+up*z;H.record(w,'location',f)
  direction=(front*.75+up*(-.75+2.4*smooth((z+.29)/.33))).normalized();orient[side].rotation_quaternion=direction.to_track_quat('Y','Z')@Quaternion((0,1,0),sign*roll);H.record(orient[side],'rotation_quaternion',f)
 for p in r.pose.bones:H.record(p,'rotation_quaternion',f)
 face=(12 if speaking else 2)if t<2.4 else(16 if speaking else 4)if t<6.2 else(12 if speaking else 2)if t<15.0 else(3 if speaking else 2)
 if any(b<=t<b+.083 for b in [1.9,5.8,8.6,11.8,14.6,19.15]):face=10
 if 17.65<=t<17.9:face=17
 a['PS1_face_id']=face;a.keyframe_insert(data_path='["PS1_face_id"]',frame=f)
 if not faces or faces[-1]['id']!=face:faces.append(dict(frame=f,id=face))
 u=smooth(t/14.8);loc=Vector((2.05,-.80,1.64))+Vector((-.13,-.09,.015))*u;target=Vector((0,.10,1.24+.07*u));cam.location=loc;cam.rotation_euler=(target-loc).to_track_quat('-Z','Y').to_euler();cam.data.lens=42+6*u
 H.record(cam,'location',f);H.record(cam,'rotation_euler',f);H.record(cam.data,'lens',f)
H.commit_curves()
for fc in a.animation_data.action.fcurves:
 for key in fc.keyframe_points:key.interpolation='CONSTANT'
(ROOT/'face_cues.json').write_text(json.dumps(faces,indent=2));(ROOT/'acting_cues.json').write_text(json.dumps(dict(method='One sustained room take: friendly conclusion, one comic lesson, audience suggestions, support prompts and a short farewell wave. The wink accompanies the recorded goodbye; no hand-to-mouth contact or invented finger rig.',right=R,left=L,camera='Gentle continuous push until 14.8 seconds, then held for farewell.',wave=[15.2,19.9],wink=[17.65,17.9],reference='Private gesture reference from episode 007; not republished.'),indent=2))
s['DeryPS1Look']='405x228 seam-safe precision; Closest 128px texture addressing; 5-bit RGB ordered dither at export';s['DeryFormats']='16:9 only';s['OutroPictureCuts']=1
s.sequence_editor_create().sequences.new_sound('VOZ | supplied revised closing',str(ROOT/'assets/voz/narracao_mix.wav'),channel=1,frame_start=1)
s.frame_set(60);bpy.data.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();(ROOT/'output').mkdir(exist_ok=True)
dest=ROOT/'output/Dery_Encerramento_Personagens_16x9.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
for t in [1.2,4.2,7.8,10.6,13.0,15.8,16.7,17.75,18.7,19.7]:
 s.frame_set(round(t*24)+1);s.render.filepath=str(ROOT/f'output/preview_{round(t*24)+1:04d}.png');bpy.ops.render.render(write_still=True)
print('OUTRO_SCENE_READY',flush=True)
