"""Six-second test: the unchanged original Dery seated in the new library room."""
from pathlib import Path
import bpy,sys,math,json,hashlib,wave
import numpy as np
from mathutils import Vector,Matrix,Quaternion
from mathutils.bvhtree import BVHTree

P=Path(__file__).resolve().parent;ROOM=P.parent;REPO=ROOM.parents[2]
WORK=Path('/workspace/attachments/quarto_gamer_cena');WORK.mkdir(exist_ok=True)
FPS=16;N=96
AVATAR=REPO/'assets/personagens/dery/roupas/camiseta_preta/Dery_Camiseta_Preta.blend'
ROOMFILE=ROOM/'Quarto_Gamer_Banco_PS1.blend'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source_hashes={str(p.relative_to(REPO)):sha(p)for p in (AVATAR,ROOMFILE)}

# Preserve the evaluated seated pose, including constraints on the old legs.
bpy.ops.wm.open_mainfile(filepath=str(REPO/'shorts/004-crash-apelido/production/output/Dery_Crash_Master_R5.blend'))
bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
evaluated=bpy.data.objects['Dery_Rig'].evaluated_get(bpy.context.evaluated_depsgraph_get())
seated={p.name:p.matrix.copy()for p in evaluated.pose.bones}
bpy.ops.wm.open_mainfile(filepath=str(ROOMFILE));scene=bpy.context.scene
with bpy.data.libraries.load(str(AVATAR),link=False)as(src,dst):dst.objects=['Dery_Rig','DERY | animated character']
collection=bpy.data.collections.new('TESTE | Dery original');scene.collection.children.link(collection)
for o in dst.objects:collection.objects.link(o)
rig=next(o for o in dst.objects if o.type=='ARMATURE');actor=next(o for o in dst.objects if o.type=='MESH')
mesh_digest=hashlib.sha256(np.asarray([v.co[:]for v in actor.data.vertices],dtype=np.float32).tobytes()).hexdigest()
rig.animation_data_clear();actor.animation_data_clear()
for pb in rig.pose.bones:
    for constraint in list(pb.constraints):pb.constraints.remove(constraint)
    kw={}if pb.parent is None else {'parent_matrix':seated[pb.parent.name],'parent_matrix_local':pb.parent.bone.matrix_local}
    pb.matrix_basis=pb.bone.convert_local_to_pose(seated[pb.name],pb.bone.matrix_local,invert=True,**kw)
    pb.rotation_mode='QUATERNION'
for modifier in list(actor.modifiers):
    if modifier.type=='NODES':actor.modifiers.remove(modifier)
    elif modifier.type=='ARMATURE':modifier.object=rig
actor.parent=rig;actor.matrix_parent_inverse=Matrix.Identity(4);actor.matrix_basis=Matrix.Identity(4)
if actor.data.shape_keys:actor.data.shape_keys.animation_data_clear()

# Locate the broad horizontal seat, rather than guessing the chair's height.
chair=bpy.data.objects['Cadeira do Dery'];bins={}
for face in chair.data.polygons:
    if abs(face.normal.z)>.90 and .30<face.center.z<.72:
        bins.setdefault(round(face.center.z/.018),[]).append(face)
planes=sorted(bins.values(),key=lambda fs:sum(f.area for f in fs),reverse=True)
largest=sum(f.area for f in planes[0]);candidates=[fs for fs in planes if sum(f.area for f in fs)>largest*.80]
seatfaces=max(candidates,key=lambda fs:sum(f.center.z*f.area for f in fs)/sum(f.area for f in fs))
seat=sum((f.center*f.area for f in seatfaces),Vector())/sum(f.area for f in seatfaces)
yaw=-.50
high=[v.co for v in chair.data.vertices if v.co.z>.85]
back=sum(high,Vector())/len(high)-seat
angle=math.atan2(math.cos(yaw),-math.sin(yaw))-math.atan2(back.y,back.x)
chair.data.transform(Matrix.Translation(seat)@Matrix.Rotation(angle,4,'Z')@Matrix.Translation(-seat))

rig.parent=None;rig.matrix_world=Matrix.Rotation(yaw,4,'Z');bpy.context.view_layer.update()
groups={g.index:g.name for g in actor.vertex_groups}
posed=actor.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
hip=[]
for v,original in zip(posed.vertices,actor.data.vertices):
    weights=sum(g.weight for g in original.groups if groups[g.group]in ('pelvis','thigh_L','thigh_R'))
    if weights>.40 and abs(v.co.x)<.19 and v.co.y>-.10 and .5<v.co.z<1.0:hip.append(v.co.z)
assert hip
hip_bottom=float(np.quantile(hip,.06));rig.location=(seat.x,seat.y,seat.z-hip_bottom+.003)
actor.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear();bpy.context.view_layer.update()
base={p.name:p.rotation_quaternion.copy()for p in rig.pose.bones}
bases={p.name:p.matrix_basis.copy()for p in rig.pose.bones}
rest={p.name:p.bone.matrix_local.to_quaternion()for p in rig.pose.bones}

def empty(name):
    obj=bpy.data.objects.new(name,None);collection.objects.link(obj);return obj
def camera(name,loc,target,lens):
    data=bpy.data.cameras.new(name);obj=bpy.data.objects.new(name,data);collection.objects.link(obj);obj.location=loc;obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler();data.lens=lens;data.sensor_fit='VERTICAL';data.sensor_height=24;return obj
host=camera('TESTE | apresentador',(-.35,-2.22,1.52),(seat.x,seat.y,1.14),41)
close=camera('TESTE | reação',(-.30,-2.15,1.51),(seat.x,seat.y,1.27),58)
screen=bpy.data.objects['Tela do PC | substituir por vídeo'];screen_center=sum((v.co for v in screen.data.vertices),Vector())/len(screen.data.vertices)
monitor=camera('TESTE | jogo no CRT',(-.62,-.83,1.41),screen_center,37)
render_camera=camera('TESTE | câmera animada',host.location,(seat.x,seat.y,1.14),41)
for frame,source in [(1,monitor),(20,monitor),(21,host),(60,host),(61,close),(96,close)]:
    render_camera.location=source.location;render_camera.rotation_euler=source.rotation_euler;render_camera.data.lens=source.data.lens
    render_camera.keyframe_insert('location',frame=frame);render_camera.keyframe_insert('rotation_euler',frame=frame);render_camera.data.keyframe_insert('lens',frame=frame)
for owner in (render_camera,render_camera.data):
    for fc in owner.animation_data.action.fcurves:
        for key in fc.keyframe_points:key.interpolation='CONSTANT'
scene.camera=render_camera;scene.render.resolution_x=270;scene.render.resolution_y=480;scene.render.resolution_percentage=100
scene.render.fps=FPS;scene.frame_start=1;scene.frame_end=N;scene.render.engine='BLENDER_EEVEE_NEXT';scene.eevee.taa_render_samples=1
scene.render.image_settings.file_format='PNG';scene.render.use_compositing=False;scene.render.use_sequencer=False
scene.render.threads_mode='FIXED';scene.render.threads=2
bpy.data.objects['Teto | interiores'].hide_render=False

# Replace only the independent PC display material.
tex=next(n for n in screen.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE')
tex.image=bpy.data.images.load(str(P/'media/Monitor_Driver_6s.mp4'),check_existing=True);tex.interpolation='Closest'
tex.image_user.frame_start=1;tex.image_user.frame_offset=0;tex.image_user.frame_duration=N;tex.image_user.use_auto_refresh=True

def aim_head(point):
    bone=rig.pose.bones['head'];bpy.context.view_layer.update();matrix=bone.matrix.copy();worldq=rig.matrix_world.to_quaternion()
    forward=(worldq@matrix.to_quaternion()@rest['head'].inverted())@Vector((0,-1,0));direction=Vector(point)-(rig.matrix_world@matrix.translation)
    delta=math.atan2(direction.y,direction.x)-math.atan2(forward.y,forward.x)
    q=worldq.inverted()@Quaternion((0,0,1),delta)@worldq
    bone.matrix=Matrix.LocRotScale(matrix.translation,q@matrix.to_quaternion(),matrix.to_scale());bpy.context.view_layer.update()
    value=bone.rotation_quaternion.copy();bone.matrix_basis=bases['head'].copy();bpy.context.view_layer.update();return value
look_host=aim_head(host.location);look_pc=aim_head(screen_center)
shoulders={s:rig.matrix_world@rig.pose.bones['arm_'+s].head for s in ('L','R')}
wrists={};palms={}
for side in ('L','R'):
    wrists[side]=empty('TESTE | punho '+side)
    c=rig.pose.bones['forearm_'+side].constraints.new('IK');c.target=wrists[side];c.chain_count=2;c.use_stretch=False
    palms[side]=empty('TESTE | palma '+side);palms[side].rotation_mode='QUATERNION'
    c=rig.pose.bones['hand_'+side].constraints.new('COPY_ROTATION');c.target=palms[side];c.owner_space='WORLD';c.target_space='WORLD'
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
def curve(keys,t):
    if t<=keys[0][0]:return keys[0][1]
    for (a,x),(b,y)in zip(keys,keys[1:]):
        if t<=b:
            u=smooth((t-a)/(b-a))
            return x+(y-x)*u if isinstance(x,(float,int))else tuple(v+(w-v)*u for v,w in zip(x,y))
    return keys[-1][1]
right=[(0,(.17,.10,-.30,0)),(1.25,(.17,.10,-.30,0)),(1.65,(.25,.12,-.15,.65)),(2.12,(.25,.12,-.15,.65)),(2.70,(.17,.10,-.30,0)),(3.35,(.17,.10,-.30,0)),(3.75,(.21,.14,-.21,.40)),(4.25,(.21,.14,-.21,.40)),(4.8,(.17,.10,-.30,0)),(6,(.17,.10,-.30,0))]
left=[(0,(.19,.10,-.29,0)),(2.35,(.19,.10,-.29,0)),(2.75,(.22,.12,-.23,.25)),(3.10,(.19,.10,-.29,0)),(3.6,(.19,.10,-.29,0)),(3.92,(.20,.12,-.24,.30)),(4.4,(.19,.10,-.29,0)),(6,(.19,.10,-.29,0))]
with wave.open(str(P/'media/Voz_Driver_Trecho.wav'))as w:rate=w.getframerate();voice=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768
faces=[]
for frame in range(1,N+1):
    t=(frame-1)/FPS
    for name,p in rig.pose.bones.items():p.matrix_basis=bases[name].copy()
    gaze=curve([(0,1),(1.1,1),(1.55,0),(2.9,0),(3.2,.12),(3.5,0),(6,0)],t)
    tilt=curve([(0,0),(1.55,-.025),(2.1,0),(3.7,.04),(4.3,.04),(4.9,0),(6,0)],t)
    rig.pose.bones['head'].rotation_quaternion=look_host.slerp(look_pc,gaze)@(rest['head'].inverted()@Quaternion((0,1,0),tilt)@rest['head'])
    lean=curve([(0,0),(1.6,-.025),(2.25,-.025),(2.8,0),(3.7,.025),(4.4,.025),(5,0),(6,0)],t)
    rig.pose.bones['upper_chest'].rotation_quaternion@=rest['upper_chest'].inverted()@Quaternion((1,0,0),lean)@rest['upper_chest']
    forward=Vector((math.sin(yaw),-math.cos(yaw),0));up=Vector((0,0,1))
    for side,sign,keys in [('R',-1,right),('L',1,left)]:
        fw,out,z,roll=curve(keys,t);outward=Vector((math.cos(yaw)*sign,math.sin(yaw)*sign,0))
        wrists[side].location=shoulders[side]+forward*fw+outward*out+up*z;wrists[side].keyframe_insert('location',frame=frame)
        direction=(forward*.75+up*(-.75+2.4*smooth((z+.29)/.33))).normalized();palms[side].rotation_quaternion=direction.to_track_quat('Y','Z')@Quaternion((0,1,0),sign*roll);palms[side].keyframe_insert('rotation_quaternion',frame=frame)
    for p in rig.pose.bones:p.keyframe_insert('rotation_quaternion',frame=frame)
    pulse=frame%3!=0;energy=voice[int(t*rate):int((t+.06)*rate)]
    speaking=t<4.9 and len(energy)>0 and np.sqrt(np.mean(energy*energy))>.03 and pulse
    face=(12 if speaking else 2)if t<3.25 else(24 if speaking else 23)if t<4.9 else 6
    if 2.37<=t<2.50:face=10
    actor['PS1_face_id']=face;actor.keyframe_insert(data_path='["PS1_face_id"]',frame=frame)
    if not faces or faces[-1]['id']!=face:faces.append({'frame':frame,'id':face})
for fc in actor.animation_data.action.fcurves:
    for key in fc.keyframe_points:key.interpolation='CONSTANT'

# Separate, motivated cuts: monitor -> speaking Dery -> dry reaction.
for marker in list(scene.timeline_markers):scene.timeline_markers.remove(marker)
for name,frame,cam in [('Jogo no computador',1,monitor),('Dery explica',21,host),('Reação',61,close)]:
    scene.timeline_markers.new(name,frame=frame)
sys.path.insert(0,str(REPO/'assets/personagens/dery'))
from ps1_precision import add_safe_precision
mod=add_safe_precision(actor,render_camera,width=135,height=240,aspect=9/16)
group=mod.node_group;group.name='TESTE | precisão | câmera animada';mod.name='PS1 | personagem sem fissuras'
scene['Demo | câmera']=render_camera.name
scene['Demo | atores']='Modelo original; pose sentada avaliada preservada e controles de gesto próprios.'
scene['Demo | fala']='Abertura da voz já enviada para O verdadeiro chefe de Driver; nenhum TTS novo.'
scene.frame_set(40);scene.camera=render_camera
for obj in scene.objects:
    if obj.type=='MESH'and obj!=actor:
        modifier=obj.modifiers.get('PS1 | bordas por câmera')
        if modifier:modifier.node_group=group
scene.render.filepath=str(WORK/'Dery_No_Quarto_base.png');bpy.ops.render.render(write_still=True)
actor_points=actor.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh();zvalues=[(actor.matrix_world@v.co).z for v in actor_points.vertices]
actor.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear()
assert mesh_digest==hashlib.sha256(np.asarray([v.co[:]for v in actor.data.vertices],dtype=np.float32).tobytes()).hexdigest()
assert all(sha(REPO/p)==h for p,h in source_hashes.items())
for im in bpy.data.images:
    if im.source=='FILE'and not im.packed_file and im.filepath:im.filepath=bpy.path.abspath(im.filepath)
bpy.ops.file.pack_all();bpy.ops.file.make_paths_relative()
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Dery_No_Quarto_Teste_6s.blend'),compress=True)
record={'duration':6,'fps_animation':FPS,'frames':N,'source_hashes':source_hashes,'source_vertices_unchanged':True,'seated_pose_method':'Full evaluated bone matrices converted with Bone.convert_local_to_pose before gestures; original legs retained.','seat_world':list(seat),'hip_bottom_rig_space':hip_bottom,'rig_location':list(rig.location),'actor_min_z_sample':min(zvalues),'faces':faces,'cuts':[{'frame':m.frame,'label':m.name}for m in scene.timeline_markers],'animated_camera':render_camera.name,'voice_source':'shorts/007-verdadeiro-chefe-driver/production/assets/voz/narracao_completa.wav','gameplay_source':'shorts/007-verdadeiro-chefe-driver/production/assets/gameplay/driver_tutorial_enviado.mp4','approval_pending':True}
(P/'cena.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print('TEST_SCENE',record['seat_world'],record['rig_location'],record['actor_min_z_sample'],flush=True)
