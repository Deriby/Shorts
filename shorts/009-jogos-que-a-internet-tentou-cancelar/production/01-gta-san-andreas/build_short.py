"""GTA San Andreas: original Dery, the library room, a game shop and hidden files."""
from pathlib import Path
import bpy,sys,math,json,hashlib,wave
import numpy as np
from mathutils import Vector,Matrix,Quaternion
from mathutils.bvhtree import BVHTree

P=Path(__file__).resolve().parent;REPO=next(p for p in P.parents if(p/'AGENTS.md').exists());ROOM=REPO/'assets/cenarios/quarto_gamer_banco_v2'
info=json.loads((P/'timeline.json').read_text());shots=info['shots']
WORK=Path('/workspace/attachments/jogos_cancelar');WORK.mkdir(exist_ok=True)
FPS=info['fps'];N=info['frames']
AVATAR=REPO/'assets/personagens/dery/expressions_ps1/v3/Dery_131_Expressoes_PS1.blend'
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
standing={p.name:p.matrix_basis.copy()for p in rig.pose.bones}
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
scene.camera=render_camera;scene.render.resolution_x=768;scene.render.resolution_y=432;scene.render.resolution_percentage=100
scene.render.fps=FPS;scene.frame_start=1;scene.frame_end=N;scene.render.engine='BLENDER_EEVEE_NEXT';scene.eevee.taa_render_samples=1
scene.render.image_settings.file_format='PNG';scene.render.use_compositing=False;scene.render.use_sequencer=False
scene.render.threads_mode='FIXED';scene.render.threads=2
bpy.data.objects['Teto | interiores'].hide_render=False
# Replace only the independent PC display material.
tex=next(n for n in screen.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE')
tex.image=bpy.data.images.load(str(P/'assets/monitor/monitor_completo.mp4'),check_existing=True);tex.interpolation='Closest'
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

sys.path[:0]=[str(REPO/'assets/personagens/dery/expressions_ps1/v3'),str(REPO/'assets/personagens/dery'),str(REPO/'shorts/003-teste-quarto-gamer/production')]
from setup_faces131 import install as install_faces
from ps1_precision import add_safe_precision
import helpers as H
H.C.s=scene
install_faces(actor)

def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
def curve(keys,t):
    if t<=keys[0][0]:return keys[0][1]
    for (a,x),(b,y)in zip(keys,keys[1:]):
        if t<=b:
            u=smooth((t-a)/(b-a))
            return x+(y-x)*u if isinstance(x,(float,int))else tuple(v+(w-v)*u for v,w in zip(x,y))
    return keys[-1][1]

dark=H.material('GTA | charcoal',(.025,.025,.035),lit=False)
gold=H.material('GTA | yellow',(.95,.61,.08),lit=False)
cream=H.material('GTA | paper',(.82,.78,.62),lit=False)
red=H.material('GTA | restricted',(.67,.06,.04),lit=False)
green=H.material('GTA | unlocked',(.16,.59,.28),lit=False)
stage_objects=[]
def box(name,loc,size,mat):
    o=H.box('GTA | '+name,loc,size,mat);stage_objects.append(o);return o
def text(name,body,loc,size=.10,mat=cream):
    data=bpy.data.curves.new('GTA | '+name,'FONT');data.body=body;data.align_x='CENTER';data.align_y='CENTER'
    data.size=size;data.extrude=.001
    o=bpy.data.objects.new('GTA | '+name,data);scene.collection.objects.link(o)
    o.location=loc;o.rotation_euler=(math.pi/2,0,0);data.materials.append(mat)
    return o
def duplicate(source,name,loc):
    o=source.copy();o.data=source.data.copy();o.name='GTA | '+name;scene.collection.objects.link(o)
    o.location+=Vector(loc)
    for mod in list(o.modifiers):
        if mod.type=='NODES':o.modifiers.remove(mod)
    return o
def place_copy(source,name,target):
    corners=[source.matrix_world@Vector(c)for c in source.bound_box]
    center=Vector(((min(v.x for v in corners)+max(v.x for v in corners))/2,
                   (min(v.y for v in corners)+max(v.y for v in corners))/2,
                   min(v.z for v in corners)))
    return duplicate(source,name,Vector(target)-center)

# Reuse the OFFICE desk/bookcase and the game cases from the supplied bank.
shop_x=20
desk=bpy.data.objects['Mesa principal | madeira gasta'];shelf=bpy.data.objects['Estante de jogos']
place_copy(desk,'balcão da loja',(shop_x,-.35,0))
place_copy(shelf,'estante da loja',(shop_x,1.20,0))
box('piso loja',(shop_x,0,-.04),(8,6,.08),dark)
box('parede loja',(shop_x,1.85,1.5),(8,.12,3),dark)
place_copy(bpy.data.objects['Piso de tábuas'],'piso do banco na loja',(shop_x,-.5,.005))
place_copy(bpy.data.objects['Parede do fundo'],'parede do banco na loja',(shop_x,1.77,0))
text('letreiro loja','GAMES',(shop_x,1.70,2.05),.17,gold)

store_rig=rig.copy();store_rig.data=rig.data.copy();store_rig.name='GTA | Dery lojista rig'
scene.collection.objects.link(store_rig);store_rig.animation_data_clear();store_rig.parent=None
store_rig.matrix_world=Matrix.Translation((shop_x,.20,0))
for pb in store_rig.pose.bones:
    for c in list(pb.constraints):pb.constraints.remove(c)
    pb.matrix_basis=standing[pb.name].copy();pb.rotation_mode='QUATERNION'
store_actor=actor.copy();store_actor.data=actor.data.copy();store_actor.name='GTA | Dery lojista'
scene.collection.objects.link(store_actor);store_actor.animation_data_clear();store_actor.parent=store_rig
store_actor.matrix_parent_inverse=Matrix.Identity(4);store_actor.matrix_basis=Matrix.Identity(4)
for mod in list(store_actor.modifiers):
    if mod.type=='NODES':store_actor.modifiers.remove(mod)
    elif mod.type=='ARMATURE':mod.object=store_rig
install_faces(store_actor)
store_base={p.name:p.matrix_basis.copy()for p in store_rig.pose.bones}
store_cam=camera('GTA | câmera loja',(shop_x,-3.65,1.65),(shop_x,-.05,1.18),39)
stock=[]
for i in range(5):
    source=bpy.data.objects[f'Caixa de jogo {i+1}']
    o=place_copy(source,f'jogo à venda {i+1}',(shop_x-.30+i*.15,-.42,.79))
    stock.append((o,o.location.copy()))
# A large readable M -> AO badge uses a physical card, never adult imagery.
board=box('placa classificação',(shop_x-.25,-.62,1.18),(.34,.045,.40),cream)
m_label=text('M','M',(shop_x-.25,-.65,1.20),.23,dark)
ao_label=text('AO','AO',(shop_x-.25,-.65,1.20),.18,dark)
rating_caption=text('classificação EUA','CLASSIFICAÇÃO\nNOS EUA',(shop_x-.25,-.65,.91),.045,cream)
withdrawn=text('retirada','FORA DAS LOJAS',(shop_x,-.67,.85),.070,gold)
revised=text('revisada','VERSÃO REVISADA',(shop_x,-.67,.85),.065,cream)
original=text('original arquivos','VERSÃO\nORIGINAL',(40,-.52,1.68),.095,gold)

# Hidden-content vignette: a real file cabinet from OFFICE and a drawn folder
# represented by simple PS1 geometry. This is a metaphor, not a fake game menu.
bank=REPO/'assets/biblioteca_psx/originais/Banco 3D para vídeos/OFFICE/OFFICE'
before=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(bank/'file_cabinets/file_cabinet_small_open.glb'))
cabinet=list(set(bpy.data.objects)-before)
meshes=[o for o in cabinet if o.type=='MESH']
if meshes:
    corners=[o.matrix_world@Vector(c)for o in meshes for c in o.bound_box]
    lo=Vector(tuple(min(v[i]for v in corners)for i in range(3)));hi=Vector(tuple(max(v[i]for v in corners)for i in range(3)))
    scale=1.4/max(hi.z-lo.z,.01);center=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
    for o in meshes:
        o.data.transform(o.matrix_world);o.matrix_world=Matrix.Identity(4)
        o.data.transform(Matrix.Scale(scale,4)@Matrix.Translation(-center));o.location=(40,.1,0)
        for mat in o.data.materials:
            if not mat or not mat.use_nodes:continue
            nt=mat.node_tree;bs=next((n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'),None)
            if bs:
                em=nt.nodes.new('ShaderNodeEmission');color=bs.inputs['Base Color']
                if color.is_linked:nt.links.new(color.links[0].from_socket,em.inputs['Color'])
                else:em.inputs['Color'].default_value=color.default_value
                output=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL');nt.links.new(em.outputs[0],output.inputs['Surface'])
            for n in nt.nodes:
                if n.type=='TEX_IMAGE':n.interpolation='Closest'
box('piso arquivos',(40,0,-.04),(8,6,.08),dark)
box('parede arquivos',(40,1.1,1.5),(8,.08,3),dark)
folder=box('pasta Hot Coffee',(40,-.50,1.03),(.68,.06,.50),gold)
tab=box('aba pasta',(39.80,-.50,1.30),(.27,.06,.09),gold)
text('nome arquivo','HOT COFFEE',(40,-.54,1.06),.095,dark)
locked=text('desativado','DESATIVADO',(40,-.56,.75),.09,red)
unlocked=text('desbloqueado','DESBLOQUEADO',(40,-.56,.75),.07,green)
mod_block=box('botão mod',(40,-.54,.43),(.55,.07,.22),green)
text('mod','MOD',(40,-.59,.44),.10,cream)
archive_cam=camera('GTA | câmera arquivos',(40,-3.15,1.50),(40,-.1,1.0),36)

# A second real bank mug joins the first at the punchline; no hand attachment.
cup=bpy.data.objects['Caneca na mesa'];cup2=duplicate(cup,'segunda caneca',(.16,-.11,0))
cup2.rotation_euler.z+=1.1

for marker in list(scene.timeline_markers):scene.timeline_markers.remove(marker)
for sh in shots:
    cam={'monitor':monitor,'host':host,'close':close,'archive':archive_cam,'shop':store_cam}.get(sh['kind'],host)
    for f in [sh['start'],sh['end']]:
        render_camera.location=cam.location;render_camera.rotation_euler=cam.rotation_euler;render_camera.data.lens=cam.data.lens
        render_camera.keyframe_insert('location',frame=f);render_camera.keyframe_insert('rotation_euler',frame=f);render_camera.data.keyframe_insert('lens',frame=f)
    scene.timeline_markers.new(f"{sh['id']:02d} {sh['mood']}",frame=sh['start'])
for owner in (render_camera,render_camera.data):
    for fc in owner.animation_data.action.fcurves:
        for key in fc.keyframe_points:key.interpolation='CONSTANT'

with wave.open(str(P/'assets/voz/voz_timeline.wav'))as w:
    rate=w.getframerate();voice=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768
families=json.loads((REPO/'assets/personagens/dery/expressions_ps1/v3/fala_familias.json').read_text())
speech_shapes=['fechada_mbp','aberta_a','larga_e','estreita_i','redonda_o','pequena_u','labio_fv','lingua_l','entreaberta_dtn','bico_ch']
def speech_face(t,mood):
    sample=voice[int(t*rate):int((t+.045)*rate)]
    energy=np.sqrt(np.mean(sample*sample)) if len(sample)else 0
    if energy<.021:return families[mood]['fechada_mbp']
    # Mouth size follows the actual recording; brief different shapes prevent
    # the old one-open-mouth loop. Each phrase keeps its own emotional family.
    if energy>.13:shape='aberta_a'
    else:shape=['larga_e','entreaberta_dtn','redonda_o','labio_fv','estreita_i','pequena_u','lingua_l','bico_ch'][int(t*8.5)%8]
    return families[mood][shape]
def gesture(t,peaks):
    result=0
    for center,width,height in peaks:
        d=abs(t-center)/width
        if d<1:result=max(result,smooth(1-d)*height)
    return result
right_peaks=[(3.1,.8,.8),(5.25,.7,.5),(7.6,.65,.65),(11.6,1.1,.7),(20.0,.65,.55),(44.5,.8,.75),(47,.9,.55),(49.2,.8,.8),(51.3,.7,.4)]
left_peaks=[(4.5,.65,.35),(8.15,.5,.5),(10.4,.7,.45),(12.9,.8,.35),(20.6,.7,.7),(45.5,.8,.45),(49.8,.7,.6)]
faces=[]
for frame in range(1,N+1):
    t=(frame-1)/FPS
    sh=next(sh for sh in shots if sh['start']<=frame<=sh['end'])
    for name,pb in rig.pose.bones.items():pb.matrix_basis=bases[name].copy()
    # Asymmetric gesture arcs: prepare, emphasize, hold, settle. No arm waving
    # on a repeating sine wave. Gaze shifts lead the conversational beats.
    gaze=curve([(0,.8),(2.2,.8),(2.7,0),(6.3,0),(7,.05),(9,0),(9.5,.7),(13.9,.7),(19,0),(21.7,0),(43.4,0),(48,0),(49,.35),(50,.1),(53.4,0)],t)
    tilt=curve([(0,0),(3,-.025),(6,.02),(7.6,.045),(8.6,.045),(9.1,0),(20,.05),(21,0),(44,.025),(47.5,.025),(49,-.035),(52,.025),(53.4,.025)],t)
    rig.pose.bones['head'].rotation_quaternion=look_host.slerp(look_pc,gaze)@(rest['head'].inverted()@Quaternion((0,1,0),tilt)@rest['head'])
    lean=gesture(t,[(4,1.6,.025),(7.6,1.1,-.025),(20.4,1,.035),(45,1.8,.03),(49.5,1.4,-.025)])
    rig.pose.bones['upper_chest'].rotation_quaternion@=rest['upper_chest'].inverted()@Quaternion((1,0,0),lean)@rest['upper_chest']
    forward=Vector((math.sin(yaw),-math.cos(yaw),0));up=Vector((0,0,1))
    for side,sign,peaks in [('R',-1,right_peaks),('L',1,left_peaks)]:
        g=gesture(t,peaks);fw=.17+.10*g;out=.10+.06*g;z=-.30+.24*g
        outward=Vector((math.cos(yaw)*sign,math.sin(yaw)*sign,0))
        wrists[side].location=shoulders[side]+forward*fw+outward*out+up*z;wrists[side].keyframe_insert('location',frame=frame)
        direction=(forward*.75+up*(-.7+1.8*g)).normalized()
        palms[side].rotation_quaternion=direction.to_track_quat('Y','Z')@Quaternion((0,1,0),sign*.7*g);palms[side].keyframe_insert('rotation_quaternion',frame=frame)
    for pb in rig.pose.bones:pb.keyframe_insert('rotation_quaternion',frame=frame)
    mood='sarcastica'if 6.55<=t<9.2 or t>=48.35 else'irritada'if 18.95<=t<21.85 else'empolgada'if t<6.55 else'neutra'
    face=speech_face(t,mood)
    for a,b,i in [(6.60,6.82,84),(8.85,9.17,107),(19.08,19.30,111),(21.45,21.80,105),(43.45,43.65,118),(47.9,48.25,107),(51.8,52.35,122)]:
        if a<=t<b:face=i
    for blink in [3.55,11.8,20.85,44.65,50.75]:
        if blink<=t<blink+.10:face=10
    actor['PS1_face_id']=face;actor.keyframe_insert(data_path='["PS1_face_id"]',frame=frame)
    if not faces or faces[-1]['id']!=face:faces.append(dict(frame=frame,id=face))
    # The shop uses a separate original rig/material and planted feet.
    for name,pb in store_rig.pose.bones.items():pb.matrix_basis=store_base[name].copy()
    local=t-21.85
    for side,sign,peaks in [('L',1,[(2,.8,.65),(6.4,.9,.8),(9.8,.9,.45)]),('R',-1,[(3.3,.9,.7),(7.6,.8,.6),(11,.9,.6)])]:
        g=gesture(local,peaks)
        for bone,axis,ang in [('arm_'+side,(0,1,0),sign*(-.55*g)),('forearm_'+side,(1,0,0),-.55*g)]:
            pb=store_rig.pose.bones[bone];pb.rotation_quaternion@=rest[bone].inverted()@Quaternion(axis,ang)@rest[bone]
    store_rig.pose.bones['head'].rotation_quaternion@=rest['head'].inverted()@Quaternion((0,0,1),curve([(0,-.03),(23,-.03),(24,.04),(27,.04),(28,-.06),(30,-.06),(31,.02),(53,.02)],t))@rest['head']
    for pb in store_rig.pose.bones:pb.keyframe_insert('rotation_quaternion',frame=frame)
    store_face=speech_face(t,'neutra'if t<24 else'irritada'if t<30.65 else'alegre')
    if 27.7<=t<28.10:store_face=106
    if 29.6<=t<30.15:store_face=115
    if 34.1<=t<34.55:store_face=96
    store_actor['PS1_face_id']=store_face;store_actor.keyframe_insert(data_path='["PS1_face_id"]',frame=frame)
    for o,hide in [(m_label,t>=24.2),(ao_label,t<24.2 or t>=30.65),(rating_caption,t>=30.65),(board,t>=30.65),
                   (withdrawn,not 28<=t<30.65),(revised,t<30.65),(locked,16.65<=t<19),(unlocked,not(16.65<=t<19)),
                   (cup2,t<48.35)]:
        o.hide_render=hide;o.keyframe_insert('hide_render',frame=frame)
    for i,(o,start)in enumerate(stock):
        gone=smooth((t-(28.05+i*.16))/.33) if t<30.65 else 1-smooth((t-30.85-i*.12)/.35)
        o.location=start+Vector((0,0,-1.1*gone));o.keyframe_insert('location',frame=frame)

for obj in [actor,store_actor]:
    for fc in obj.animation_data.action.fcurves:
        for key in fc.keyframe_points:key.interpolation='CONSTANT'
# One camera controls all precision groups across actual cuts, avoiding old
# unused-camera group loss. Face weights remain seam-safe.
mod=add_safe_precision(actor,render_camera,width=384,height=216,aspect=16/9)
group=mod.node_group;group.name='GTA | PS1 precision | active animated camera'
add_safe_precision(store_actor,render_camera,width=384,height=216,aspect=16/9)
for obj in scene.objects:
    if obj.type=='MESH'and obj not in (actor,store_actor):
        for modifier in obj.modifiers:
            if modifier.type=='NODES':modifier.node_group=group
scene['Production | camera']=render_camera.name
scene['Production | preserve']='Original Dery, 131 PNGs; full voice; bank room/desk/bookcase/cases/cabinet.'
scene.frame_set(round(4*FPS)+1);scene.camera=render_camera
for im in bpy.data.images:
    if im.source=='FILE'and not im.packed_file and im.filepath:im.filepath=bpy.path.abspath(im.filepath)
bpy.ops.file.pack_all();bpy.ops.file.make_paths_relative()
assert mesh_digest==hashlib.sha256(np.asarray([v.co[:]for v in actor.data.vertices],dtype=np.float32).tobytes()).hexdigest()
assert all(sha(REPO/p)==h for p,h in source_hashes.items())
outfile=P/'output/Dery_GTA_San_Andreas.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(outfile),compress=True)
(P/'animacao.json').write_text(json.dumps(dict(fps=FPS,frames=N,source_hashes=source_hashes,
   source_vertices_unchanged=True,faces=faces,original_model=True,expression_count=131,
   formats='16:9 with central 9:16 camera-safe composition; per-shot edit framing',
   scenes=['library gamer room','bank-office game shop','bank-office hidden file cabinet'],
   voice_preserved=True,standing_feet_planted=True,personal_gesture_reference_published=False),ensure_ascii=False,indent=2)+'\n')
for f in ([61,122,242,379,445,535,690,753] if '--previas'in sys.argv else []):
    scene.frame_set(f);scene.render.filepath=str(WORK/f'previa_{f:04d}.png');bpy.ops.render.render(write_still=True)
print('GTA_SCENE_READY',str(outfile),flush=True)
