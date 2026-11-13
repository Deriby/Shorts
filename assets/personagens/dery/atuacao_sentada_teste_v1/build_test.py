"""Eight-second seated acting study: measured support, one authored gesture, no cycles."""
from pathlib import Path
import bpy,bmesh,sys,json,math,hashlib,wave
import numpy as np
from mathutils import Vector,Matrix,Quaternion
P=Path(__file__).resolve().parent;R=next(p for p in P.parents if(p/'AGENTS.md').exists());C=Path('/workspace/attachments/atuacao_sentada');C.mkdir(parents=True,exist_ok=True)
SOURCE=R/'shorts/009-jogos-que-a-internet-tentou-cancelar/production/04-saints-row-iv/output/Dery_Saints_Row_IV.blend';source_sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
sys.path[:0]=[str(R/'assets/personagens/dery'),str(R/'shorts/003-teste-quarto-gamer/production')]
from psx_render import bake_faces,affine_material
import helpers as H
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene;H.C.s=s;s.frame_set(1);bpy.context.view_layer.update()
a=bpy.data.objects['DERY | animated character'];rig=a.parent;cam=bpy.data.objects[s['Production | camera']];chair=bpy.data.objects['Cadeira do Dery'];FPS=30;N=240
mesh_sha=hashlib.sha256(np.array([v.co[:]for v in a.data.vertices],np.float32).tobytes()).hexdigest()
base={p.name:p.matrix_basis.copy()for p in rig.pose.bones};baseq={p.name:p.rotation_quaternion.copy()for p in rig.pose.bones}
# Remove the old actions and all wrist/arm constraints; the seated lower body stays frozen.
for obj in list(s.objects):
 if obj.animation_data:obj.animation_data_clear()
for p in rig.pose.bones:
 if p.name.startswith(('arm_','forearm_','hand_')):
  for co in list(p.constraints):p.constraints.remove(co)
for image in bpy.data.images:
 if image.source=='MOVIE':
  placeholder=bpy.data.images.get('Test | static black')or bpy.data.images.new('Test | static black',width=1,height=1)
  placeholder.generated_color=(.02,.02,.02,1)
  for mat in bpy.data.materials:
   if mat.use_nodes:
    for node in mat.node_tree.nodes:
     if node.type=='TEX_IMAGE'and node.image==image:node.image=placeholder
# The standing actors and distant sets do not enter this experiment.
remove=set()
for obj in list(s.objects):
 center=obj.matrix_world.translation if obj.type!='MESH'else sum((obj.matrix_world@Vector(v)for v in obj.bound_box),Vector())/8
 if abs(center.x)>10:remove.add(obj);remove.update(obj.children_recursive)
for obj in remove:
 if obj.name in bpy.data.objects:bpy.data.objects.remove(obj,do_unlink=True)
cam.animation_data_clear();cam.data.animation_data_clear();cam.location=(-.35,-2.22,1.52);target=Vector((rig.location.x,rig.location.y,1.12));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=50;cam.data.sensor_fit='VERTICAL';cam.data.sensor_height=24;s.camera=cam
s.frame_start=1;s.frame_end=N;s.render.fps=FPS;s.render.resolution_x=768;s.render.resolution_y=432;s.render.resolution_percentage=100;s.render.engine='CYCLES';s.cycles.samples=1;s.cycles.use_denoising=False;s.render.use_persistent_data=True;s.render.threads_mode='FIXED';s.render.threads=2;s.render.dither_intensity=0
# Calibrate an actual hand frame from the undeformed weighted skin, not the arbitrary bone tail.
rot=rig.matrix_world.to_quaternion();lat=rot@Vector((1,0,0));fwd=rot@Vector((0,-1,0));up=Vector((0,0,1));inv_rig=rig.matrix_world.inverted();hands={}
bpy.context.view_layer.update()
for side,sign in [('R',-1),('L',1)]:
 arm=rig.pose.bones['arm_'+side];fore=rig.pose.bones['forearm_'+side];hand=rig.pose.bones['hand_'+side];index=a.vertex_groups['hand_'+side].index
 cloud=np.array([tuple(hand.bone.matrix_local.inverted()@v.co)for v in a.data.vertices if sum(g.weight for g in v.groups if g.group==index)>.65]);mean=Vector(cloud.mean(0));eig,V=np.linalg.eigh(np.cov(cloud.T));normal=Vector(V[:,0]);finger=(mean-normal*mean.dot(normal)).normalized();thumb=Vector(V[:,2]);thumb-=finger*thumb.dot(finger)
 if thumb.z<0:thumb.negate()
 thumb.normalize();normal=thumb.cross(finger).normalized();local_basis=Matrix((thumb,finger,normal)).transposed()
 S=rig.matrix_world@arm.head;L1=arm.length;L2=fore.length;E=S-up*L1;W=E+fwd*math.sqrt(L2*L2-.015*.015)-up*.015;direction=(W-E).normalized();world_thumb=lat*(-sign);world_thumb-=direction*world_thumb.dot(direction);world_thumb.normalize();world_basis=Matrix((world_thumb,direction,world_thumb.cross(direction))).transposed();qhand=(world_basis@local_basis.transposed()).to_quaternion()
 hands[side]=dict(S=S,E=E,W=W,L1=L1,L2=L2,qhand=qhand,rest_dir=direction,cloud=cloud,thumb=thumb,local_finger=finger)
# Replace the low, wide armrest components only in this copy of the chair.
chair.data=chair.data.copy();bm=bmesh.new();bm.from_mesh(chair.data);seat=rig.location.copy();kill=[]
for face in bm.faces:
 points=[chair.matrix_world@v.co for v in face.verts];center=sum(points,Vector())/len(points);delta=center-Vector((seat.x,seat.y,.61745))
 if abs(delta.dot(lat))>.24 and -.20<delta.dot(fwd)<.37 and max(p.z for p in points)<.80 and max(p.z for p in points)>.64:kill.append(face)
bmesh.ops.delete(bm,geom=kill,context='FACES');bm.to_mesh(chair.data);bm.free();chair.data.update()
padmat=H.material('Test | chair upholstery',(.105,.048,.030),lit=False);stemmat=H.material('Test | armrest support',(.06,.055,.047),lit=False);pads={};props=[]
for side,d in hands.items():
 transformed=np.array([tuple(d['W']+d['qhand']@Vector(v))for v in d['cloud']]);z=float(np.quantile(transformed[:,2],.04))-.001+({'R':-.0081,'L':-.0017}[side]);center=d['W']-fwd*.035;center.z=z-.018
 pad=H.box('Test | fitted armrest '+side,center,(.105,.355,.036),padmat);pad.rotation_euler.z=math.atan2(-fwd.x,fwd.y);pads[side]=dict(center=list(center),top=z);props.append(pad)
 for offset in[-.105,.085]:
  xy=center+fwd*offset;bottom=Vector((xy.x,xy.y,.62));top=Vector((xy.x,xy.y,z-.035));obj=H.beam('Test | armrest post '+side,bottom,top,.024,stemmat);props.append(obj)
# Reuse the scene's PSX graph for the small furniture adjustments.
for obj in props:
 if not obj.data.uv_layers:H.uv_faces(obj)
 attr=obj.data.attributes.new(name='PS1SnapWeight',type='FLOAT',domain='POINT')
 for v in attr.data:v.value=1
 m=obj.modifiers.new('PSX | geometry precision','NODES');m.node_group=bpy.data.node_groups['PSX | snapped vertices + affine UVs']
 for mat in obj.data.materials:affine_material(mat,'UVMap',1)

def hermite(keys,t):
 if t<=keys[0][0]:return np.array(keys[0][1],float)
 if t>=keys[-1][0]:return np.array(keys[-1][1],float)
 k=next(i for i in range(len(keys)-1)if t<keys[i+1][0]);ta,a,va=keys[k];tb,b,vb=keys[k+1];u=(t-ta)/(tb-ta);a,b,va,vb=map(lambda x:np.array(x,float),(a,b,va,vb));dt=tb-ta
 return(2*u**3-3*u*u+1)*a+(u**3-2*u*u+u)*dt*va+(-2*u**3+3*u*u)*b+(u**3-u*u)*dt*vb
Z=(0,0,0,0)
gesture=[(0,Z,Z),(.95,Z,Z),(1.18,(0,0,-.004,0),Z),(1.60,(.010,.003,.035,25),(.020,.006,.120,50)),(2.30,(.035,.012,.130,85),(.020,.005,.090,55)),(2.95,(.047,.018,.170,105),Z),(3.35,(.043,.018,.166,104),Z),(3.85,(.022,.010,.095,60),(-.050,-.015,-.220,-110)),(4.30,(.005,.003,.020,12),(-.015,-.010,-.070,-50)),(4.62,Z,Z),(8,Z,Z)]
# Authored body/gaze events; there is no periodic sway, breathing loop or mirrored arm cycle.
body=[(0,(0,0), (0,0)),(1.25,(0,0),(0,0)),(2.55,(.017,.003),(0,0)),(3.45,(.015,.003),(0,0)),(4.62,(0,0),(0,0)),(8,(0,0),(0,0))]
gaze=[(0,(0,0,0),(0,0,0)),(1.4,(0,0,0),(0,0,0)),(2.8,(-.008,0,-.008),(0,0,0)),(4.4,(0,0,0),(0,0,0)),(5.15,(.006,0,.006),(0,0,0)),(5.85,(.005,.095,.030),(0,0,0)),(6.65,(.005,.095,.030),(0,0,0)),(7.3,(0,0,.014),(0,0,0)),(8,(0,0,.014),(0,0,0))]
records={};world_wrist={side:[]for side in hands};metrics={'max_reach':0,'max_wrist_error':0}
def record_bone(name,frame):
 p=rig.pose.bones[name];records.setdefault(name,[]).append((frame,list(p.rotation_quaternion),list(p.location)))
def set_world(p,position,q):
 p.rotation_mode='QUATERNION';p.matrix=inv_rig@Matrix.LocRotScale(position,q,Vector((1,1,1)))
def aim(rest_q,direction):return(rest_q@Vector((0,1,0))).rotation_difference(direction)@rest_q
for frame in range(1,N+1):
 t=(frame-1)/FPS;pitch,roll=hermite(body,t);hp,hy,hr=hermite(gaze,t)
 for name,factor in [('spine',.25),('chest',.40),('upper_chest',.35)]:
  p=rig.pose.bones[name];q=p.bone.matrix_local.to_quaternion();p.rotation_quaternion=baseq[name]@(q.inverted()@Quaternion((1,0,0),float(pitch)*factor)@Quaternion((0,1,0),float(roll)*factor)@q);record_bone(name,frame)
 for name,factor in [('neck',.22),('head',.78)]:
  p=rig.pose.bones[name];q=p.bone.matrix_local.to_quaternion();p.rotation_quaternion=baseq[name]@(q.inverted()@Quaternion((1,0,0),float(hp)*factor)@Quaternion((0,0,1),float(hy)*factor)@Quaternion((0,1,0),float(hr)*factor)@q);record_bone(name,frame)
 bpy.context.view_layer.update()
 for side,sign in [('R',-1),('L',1)]:
  d=hands[side];arm=rig.pose.bones['arm_'+side];fore=rig.pose.bones['forearm_'+side];hand=rig.pose.bones['hand_'+side];S=rig.matrix_world@arm.head
  fw,out,z,turn=hermite(gesture,t)if side=='R'else Z;W=d['W']+fwd*float(fw)+lat*float(out)+up*float(z);delta=W-S;D=delta.length;assert D<d['L1']+d['L2']-.01
  axis=delta.normalized();a_dist=(d['L1']**2-d['L2']**2+D*D)/(2*D);h=math.sqrt(max(0,d['L1']**2-a_dist*a_dist));middle=S+axis*a_dist;preferred=S-up*d['L1'];perp=preferred-middle;perp-=axis*perp.dot(axis);E=middle+perp.normalized()*h
  fore_dir=(W-E).normalized();swing=d['rest_dir'].rotation_difference(fore_dir);qhand=Quaternion(fore_dir,math.radians(float(turn)))@swing@d['qhand']
  qa=aim(rot@arm.bone.matrix_local.to_quaternion(),(E-S).normalized());qf=aim(rot@fore.bone.matrix_local.to_quaternion(),fore_dir)
  relative=(rot@fore.bone.matrix_local.to_quaternion()).inverted()@(rot@hand.bone.matrix_local.to_quaternion());dq=qf.inverted()@qhand@relative.inverted();_,twist=dq.to_swing_twist('Y');qf=qf@Quaternion((0,1,0),twist)
  set_world(arm,S,qa);bpy.context.view_layer.update();set_world(fore,E,qf);bpy.context.view_layer.update();set_world(hand,W,qhand);bpy.context.view_layer.update()
  error=(rig.matrix_world@hand.head-W).length;metrics['max_wrist_error']=max(metrics['max_wrist_error'],error);metrics['max_reach']=max(metrics['max_reach'],D);world_wrist[side].append(list(W))
  for name in['arm_'+side,'forearm_'+side,'hand_'+side]:record_bone(name,frame)
# Bake native bone curves. Quaternion signs are continuous; no runtime script is required.
action=bpy.data.actions.new('TEST | authored seated gesture');rig.animation_data_create().action=action
for name,items in records.items():
 last=None
 for row in items:
  q=Quaternion(row[1])
  if last and q.dot(last)<0:q.negate();row[1][:]=list(q)
  last=q
 for path,offset,components in [('rotation_quaternion',1,4),('location',2,3)]:
  for i in range(components):
   fc=action.fcurves.new(f'pose.bones["{name}"].{path}',index=i);fc.keyframe_points.add(N);fc.keyframe_points.foreach_set('co',[v for f,q,loc in items for v in(f,(q if offset==1 else loc)[i])])
   for key in fc.keyframe_points:key.interpolation='LINEAR'
   fc.update()
# Manually timed mouth poses for the spoken hook; PNG swaps remain discrete.
families=json.loads((R/'assets/personagens/dery/expressions_ps1/v3/fala_familias.json').read_text())
visemes=[(0,'fechada_mbp'),(.06,'larga_e'),(.24,'estreita_i'),(.40,'redonda_o'),(.65,'labio_fv'),(.80,'redonda_o'),(.96,'fechada_mbp'),(1.12,'aberta_a'),(1.32,'redonda_o'),(1.47,'entreaberta_dtn'),(1.58,'aberta_a'),(1.75,'pequena_u'),(1.92,'aberta_a'),(2.10,'estreita_i'),(2.24,'aberta_a'),(2.38,'redonda_o'),(2.52,'aberta_a'),(2.72,'larga_e'),(2.86,'pequena_u'),(3.02,'aberta_a'),(3.20,'fechada_mbp'),(3.35,'aberta_a'),(3.60,'estreita_i'),(3.76,'aberta_a'),(4.00,'pequena_u'),(4.18,'lingua_l'),(4.36,'aberta_a'),(4.55,'redonda_o'),(4.70,'larga_e'),(4.90,'redonda_o'),(5.10,'redonda_o'),(5.30,'aberta_a'),(5.50,'redonda_o'),(5.70,'fechada_mbp'),(5.92,'aberta_a'),(6.14,'larga_e'),(6.40,'fechada_mbp')]
with wave.open(str(P/'assets/voz_teste.wav'))as w:sr=w.getframerate();voice=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(float)/32768
keys=[]
for frame in range(1,N+1):
 t=(frame-1)/FPS;shape=max((p for p in visemes if p[0]<=t),key=lambda x:x[0])[1];mood='neutra'if t<5.1 else'sarcastica';value=families[mood][shape]
 sample=voice[round(t*sr):round((t+.035)*sr)]
 if len(sample)and np.sqrt(np.mean(sample*sample))<.012:value=families[mood]['fechada_mbp']
 if .92<=t<1.02:value=10
 if 6.42<=t<6.92:value=88
 elif 6.92<=t<7.35:value=81
 elif t>=7.35:value=84
 keys.append((frame,value));a['PS1_face_id']=value;a.keyframe_insert('["PS1_face_id"]',frame=frame)
bake_faces(a,keys)
for fc in a.animation_data.action.fcurves:
 for key in fc.keyframe_points:key.interpolation='CONSTANT'
# One short voice excerpt and a genuine reaction pause; the original narration stays intact.
if s.sequence_editor:s.sequence_editor_clear()
seq=s.sequence_editor_create();seq.sequences.new_sound('Voz | gancho original',str(P/'assets/voz_teste.wav'),channel=1,frame_start=1)
s.render.use_sequencer=False;s.render.use_compositing=False
s.frame_set(1);bpy.context.view_layer.update();assert hashlib.sha256(np.array([v.co[:]for v in a.data.vertices],np.float32).tobytes()).hexdigest()==mesh_sha
for image in bpy.data.images:
 if image.source=='FILE'and image.filepath and not image.packed_file:image.filepath=bpy.path.abspath(image.filepath)
bpy.ops.file.pack_all();bpy.ops.file.make_paths_relative();s['Test | scope']='8 seconds, seated, one authored right-hand gesture; no cyclic body motion.'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'output/Dery_Atuacao_Sentada_Teste.blend'),compress=True);assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_sha
report=dict(source=str(SOURCE.relative_to(R)),source_sha256=source_sha,source_unchanged=True,avatar_mesh_unchanged=True,duration=8,fps=FPS,frames=N,periodic_body_motion=False,standing_scenes=False,camera_static=True,chair_original_armrest_faces_removed=len(kill),new_supports=pads,metrics=metrics,rest_hand_world={side:list(d['W'])for side,d in hands.items()},wrist_trajectories=world_wrist,face_unique_ids=len({i for _,i in keys}),reference='Stored observations in Driver gesture_reference.json; original private video unavailable in current environment, no new video analysis or mocap.')
(P/'atuacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('SEATED_TEST_READY',json.dumps({k:v for k,v in report.items()if k!='wrist_trajectories'}),flush=True)
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
for frame in[1,91,145,211]:
 s.frame_set(frame);s.render.filepath=str(C/f'pose_{frame:03d}.png');bpy.ops.render.render(write_still=True)
