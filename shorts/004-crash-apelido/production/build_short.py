"""Build the editable 28-second episode from the approved room and real voice.

Lighting is baked once, as a room atlas and vertex illumination, then animated
with emission materials. This preserves the room's colored light without
path-tracing the same lighting hundreds of times.
"""
from pathlib import Path
import sys, math, json, array, wave
import bpy, bmesh
from mathutils import Vector, Quaternion

ROOT=Path(__file__).resolve().parent
BASE=ROOT.parents[1]/'003-teste-quarto-gamer'/'production'
sys.path[:0]=[str(ROOT),str(BASE)]
from render_still_16x9 import prepare
from ps1_nodes import add_contour_modifier
import helpers as H

ASSETS=ROOT/'assets';OUT=ROOT/'output'
FPS=24;FRAMES=672
OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(BASE/'output/Dery_Quarto_Gamer_Teste.blend'))
s=bpy.context.scene;s.frame_set(108)
prepare(s)
rig=bpy.data.objects['Dery_Rig'];hero=bpy.data.objects['DERY | world motion'];cam=s.camera
baseline={b.name:b.rotation_quaternion.copy() for b in rig.pose.bones}
rest={b.name:b.matrix_local.to_quaternion() for b in rig.data.bones}
s.render.resolution_x=640;s.render.resolution_y=360;s.render.resolution_percentage=100
s.render.fps=FPS;s.frame_start=1;s.frame_end=FRAMES
s.render.threads_mode='FIXED';s.render.threads=4
s.cycles.samples=32;s.cycles.use_denoising=False
s.cycles.use_adaptive_sampling=False
s.cycles.max_bounces=2;s.cycles.diffuse_bounces=1
s.use_nodes=False
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
for marker in list(s.timeline_markers):s.timeline_markers.remove(marker)
s.sequence_editor_clear()

def select(objects,active=None):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=active or objects[0]

def source_normals(mesh):
    values=[tuple(n.vector)for n in mesh.corner_normals]
    a=mesh.attributes.get('PS1SourceNormal') or mesh.attributes.new(name='PS1SourceNormal',type='FLOAT_VECTOR',domain='CORNER')
    for item,value in zip(a.data,values):item.vector=value

# Join the actual rigged meshes, keeping the supplied rig, UVs and materials.
parts=[bpy.data.objects[n]for n in ['Dery_Body','Dery_Head']]
for o in parts:source_normals(o.data)
select(parts,parts[0]);bpy.ops.object.join();avatar=parts[0];avatar.name='DERY | animated character'
mesh=avatar.data
bm=bmesh.new();bm.from_mesh(mesh)
before=len(bm.verts)
bmesh.ops.remove_doubles(bm,verts=[v for v in bm.verts if 1.40<v.co.z<1.55],dist=.000002)
bm.to_mesh(mesh);bm.free();mesh.update()
mesh.normals_split_custom_set([tuple(n.vector)for n in mesh.attributes['PS1SourceNormal'].data])
print('WELDED',before-len(mesh.vertices),flush=True)

# Fonts stay geometric, so the channel name remains sharp in the wide framing.
fonts=[o for o in s.objects if o.type=='FONT']
if fonts:
    select(fonts);bpy.ops.object.convert(target='MESH')
for o in fonts:
    for i,m in enumerate(o.data.materials):
        if not m or not m.use_nodes:continue
        out=next(n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL')
        node=out.inputs['Surface'].links[0].from_node
        if node.type=='BSDF_PRINCIPLED':
            m=m.copy();o.data.materials[i]=m;nt=m.node_tree
            shader=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
            em=nt.nodes.new('ShaderNodeEmission')
            if shader.inputs['Base Color'].is_linked:
                nt.links.new(shader.inputs['Base Color'].links[0].from_socket,em.inputs['Color'])
            else:em.inputs['Color'].default_value=shader.inputs['Base Color'].default_value
            out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL')
            nt.links.new(em.outputs[0],out.inputs['Surface'])

screen=bpy.data.objects['CRT moving picture']
def emissive(o):
    for m in o.data.materials:
        if not m or not m.use_nodes:return False
        out=next((n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL'),None)
        if not out or not out.inputs['Surface'].is_linked:return False
        if out.inputs['Surface'].links[0].from_node.type!='EMISSION':return False
    return True

room_objects=[o for o in s.objects if o.type=='MESH' and o!=avatar and o!=screen and not emissive(o)]
deps=bpy.context.evaluated_depsgraph_get()
for o in room_objects:
    me=bpy.data.meshes.new_from_object(o.evaluated_get(deps),preserve_all_data_layers=True,depsgraph=deps)
    mw=o.matrix_world.copy();o.parent=None;o.matrix_world=mw;o.modifiers.clear();o.data=me
select(room_objects,room_objects[0]);bpy.ops.object.join();room=room_objects[0];room.name='ROOM | baked lighting geometry'

# Bake diffuse illumination at the character's vertices, without the albedo.
select([avatar]);attr=mesh.color_attributes.new(name='PS1Lighting',type='FLOAT_COLOR',domain='CORNER')
mesh.color_attributes.active_color_index=mesh.color_attributes.find('PS1Lighting')
s.render.bake.target='VERTEX_COLORS'
bpy.context.view_layer.update()
print('BAKE_CHARACTER_START',flush=True)
bpy.ops.object.bake(type='DIFFUSE',pass_filter={'DIRECT','INDIRECT'})
values=[v for item in mesh.color_attributes['PS1Lighting'].data for v in item.color[:3]]
print('BAKE_CHARACTER_RANGE',min(values),max(values),flush=True)

# Bake the large static surfaces once; live LED geometry and monitor are separate.
select([room]);uv=room.data.uv_layers.new(name='RoomLightUV')
room.data.uv_layers.active=uv;uv.active_render=True
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=1.1519,island_margin=.004,area_weight=.2)
bpy.ops.object.mode_set(mode='OBJECT')
image=bpy.data.images.new('004 | room illumination',width=1024,height=1024,alpha=False)
for material in set(room.data.materials):
    nt=material.node_tree;node=nt.nodes.new('ShaderNodeTexImage');node.image=image
    node.name='004 | bake target';nt.nodes.active=node
s.render.bake.target='IMAGE_TEXTURES';s.render.bake.margin=8
print('BAKE_ROOM_START',flush=True)
bpy.ops.object.bake(type='COMBINED')
image.filepath_raw=str(ASSETS/'room_lightmap.png');image.file_format='PNG';image.save()
print('BAKE_ROOM_READY',flush=True)

roommat=bpy.data.materials.new('004 | baked room color');roommat.use_nodes=True
nt=roommat.node_tree;nt.nodes.clear();uvnode=nt.nodes.new('ShaderNodeUVMap');uvnode.uv_map='RoomLightUV'
tex=nt.nodes.new('ShaderNodeTexImage');tex.image=image;tex.interpolation='Closest'
em=nt.nodes.new('ShaderNodeEmission');out=nt.nodes.new('ShaderNodeOutputMaterial')
nt.links.new(uvnode.outputs[0],tex.inputs['Vector']);nt.links.new(tex.outputs['Color'],em.inputs['Color']);nt.links.new(em.outputs[0],out.inputs['Surface'])
room.data.materials.clear();room.data.materials.append(roommat)
for poly in room.data.polygons:poly.material_index=0

for material in avatar.data.materials:
    nt=material.node_tree
    shader=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
    albedo=shader.inputs['Base Color'].links[0].from_socket
    color=nt.nodes.new('ShaderNodeVertexColor');color.layer_name='PS1Lighting'
    multiply=nt.nodes.new('ShaderNodeMixRGB');multiply.blend_type='MULTIPLY';multiply.inputs[0].default_value=1
    nt.links.new(albedo,multiply.inputs[1]);nt.links.new(color.outputs['Color'],multiply.inputs[2])
    em=nt.nodes.new('ShaderNodeEmission');out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL')
    nt.links.new(multiply.outputs[0],em.inputs['Color']);nt.links.new(em.outputs[0],out.inputs['Surface'])
    for tex in list(nt.nodes):
        if tex.type!='TEX_IMAGE' or not tex.inputs['Vector'].is_linked:continue
        tex.interpolation='Closest';source=tex.inputs['Vector'].links[0].from_socket
        snap=nt.nodes.new('ShaderNodeVectorMath');snap.operation='SNAP';snap.inputs[1].default_value=(1/512,1/512,1)
        center=nt.nodes.new('ShaderNodeVectorMath');center.operation='ADD';center.inputs[1].default_value=(.5/512,.5/512,0)
        nt.links.new(source,snap.inputs[0]);nt.links.new(snap.outputs[0],center.inputs[0]);nt.links.new(center.outputs[0],tex.inputs['Vector'])

monitor_mat=screen.data.materials[0]
tex=next(n for n in monitor_mat.node_tree.nodes if n.type=='TEX_IMAGE')
tex.image=bpy.data.images.load(str(ASSETS/'gameplay/monitor_feed_28s.mp4'))
tex.image_user.frame_duration=FRAMES;tex.image_user.frame_start=1;tex.image_user.frame_offset=0
tex.image_user.use_auto_refresh=True;tex.interpolation='Closest'

# Actual geometry precision in camera space follows the native animation.
add_contour_modifier(avatar,cam)

with wave.open(str(ASSETS/'voz/narracao_completa.wav')) as w:
    samples=array.array('h',w.readframes(w.getnframes()));sr=w.getframerate()
def mouth(t):
    segment=samples[max(0,int(t*sr)):int((t+.045)*sr)]
    rms=math.sqrt(sum((v/32768)**2 for v in segment)/max(1,len(segment)))
    return min(.95,max(0,(rms-.009)*9))
def smooth(x):
    x=max(0,min(1,x));return x*x*(3-2*x)
def rotation(name,axis,angle):
    rig.pose.bones[name].rotation_quaternion=baseline[name]@(rest[name].inverted()@Quaternion(axis,angle)@rest[name])

shots=[
    (1,86,'01 | gancho','close',0),
    (87,144,'02 | apelido','reaction',0),
    (145,211,'03 | plataforma 3D','wide',0),
    (212,278,'04 | câmera por trás','monitor',1),
    (279,401,'05 | costas do protagonista','monitor2',1),
    (402,445,'06 | Sonic’s Ass Game','reaction',0),
    (446,500,'07 | piada interna','wide',0),
    (501,613,'08 | história do projeto','medium',0),
    (614,672,'09 | bundinha tem história','punch',0),
]
for a,b,label,kind,_ in shots:s.timeline_markers.new(label,frame=a)
face_mat=next(m for m in avatar.data.materials if any(n.name=='VOICE | mouth envelope' for n in m.node_tree.nodes))
mouth_socket=face_mat.node_tree.nodes['VOICE | mouth envelope'].outputs[0]
eye_nodes={name:face_mat.node_tree.nodes['EXPRESSION | '+name].outputs[0]for name in ['susto','panico','derrota']}
cam.data.sensor_fit='VERTICAL';cam.data.sensor_height=32
timeline=[]
for frame in range(1,FRAMES+1):
    t=(frame-1)/FPS;pt=math.floor(min(t,27.3)*12)/12
    a,b,label,kind,monitor_focus=next(x for x in shots if x[0]<=frame<=x[1])
    u=(frame-a)/max(1,b-a)
    looking=smooth((t-6.9)/.8)*(1-smooth((t-16.1)/.5))
    head=baseline['head']
    base_yaw=.62*(1-looking)-.50*looking
    rig.pose.bones['head'].rotation_quaternion=rest['head'].inverted()@Quaternion((0,0,1),base_yaw+.025*math.sin(pt*2.4))@rest['head']
    rotation('neck',(1,0,0),.018*math.sin(pt*4.1))
    rotation('upper_chest',(1,0,0),.006*math.sin(pt*2))
    gesture=math.sin(math.pi*max(0,min(1,(pt-5.8)/2.6))) if 5.8<pt<8.4 else 0
    gesture+=.5*math.sin(math.pi*max(0,min(1,(pt-21.3)/2.6))) if 21.3<pt<23.9 else 0
    rotation('arm_R',(0,1,0),-.10*gesture)
    rotation('forearm_R',(1,0,0),-.22*gesture)
    rotation('hand_R',(0,0,1),.05*gesture)
    for name in ['head','neck','upper_chest','arm_R','forearm_R','hand_R']:
        H.record(rig.pose.bones[name],'rotation_quaternion',frame)
    blink=max(max(0,1-abs(t-at)/.11)for at in [.95,5.75,8.65,11.4,16.8,20.95,25.45,27.25])
    deadpan=smooth((t-26.1)/.40)*.65
    eye_nodes['derrota'].default_value=max(blink*.92,deadpan)
    eye_nodes['susto'].default_value=.27*smooth((t-3.6)/.20)*(1-smooth((t-5.4)/.25))
    eye_nodes['panico'].default_value=0
    for socket in eye_nodes.values():H.record(socket,'default_value',frame)
    mouth_socket.default_value=mouth(t);H.record(mouth_socket,'default_value',frame)
    if kind=='wide':
        loc=Vector((1.90,.02,1.65));target=Vector((0,-.15,1.22));lens=44+u
    elif kind=='medium':
        loc=Vector((1.78,-.08,1.61));target=Vector((0,.00,1.28));lens=48+u
    elif kind in ['monitor','monitor2']:
        loc=Vector((1.08,.48,1.56)) if kind=='monitor' else Vector((1.22,.22,1.53))
        target=Vector((.1095,-.7959,1.262));lens=(40 if kind=='monitor' else 43)+u*2
    else:
        loc=Vector((1.24,-.32,1.55));target=Vector((0,.10,1.415))
        lens={'close':65,'reaction':72,'punch':70}[kind]+u*(2 if kind!='punch' else 4)
        if kind=='punch':target.z-=.012*smooth((t-26.6)/.6)
    cam.location=loc;cam.rotation_euler=(target-loc).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
    H.record(cam,'location',frame);H.record(cam,'rotation_euler',frame);H.record(cam.data,'lens',frame)
    timeline.append({'frame':frame,'shot':kind,'monitor_focus':bool(monitor_focus)})
H.commit_curves()
for action in list(bpy.data.actions):
    if action.users==0 or (action.use_fake_user and action.users==1):
        bpy.data.actions.remove(action)
    elif action.name.startswith('003 | '):action.name='004 | '+action.name[6:]

# Fast native rendering: lights already exist as a baked atlas/vertex colors.
s.cycles.samples=1;s.cycles.use_adaptive_sampling=False;s.cycles.max_bounces=1
for obj in s.objects:
    if obj.type=='LIGHT':obj.hide_render=True
for material in bpy.data.materials:material.cycles.emission_sampling='NONE'
s.cycles.use_denoising=False;s.cycles.pixel_filter_type='BOX';s.cycles.filter_width=.01
s.render.use_motion_blur=False;s.render.use_persistent_data=True
s.render.filepath=str(ROOT/'renders/final/frame_')
sound=s.sequence_editor_create().sequences.new_sound('Dery | narração e efeitos',str(ASSETS/'voz/narracao_mix_28s.wav'),channel=1,frame_start=1)
sound.volume=1
s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Dery_Crash_Master.blend'))
bpy.ops.file.make_paths_relative()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Dery_Crash_Master.blend'))
(ROOT/'timeline.json').write_text(json.dumps({'fps':FPS,'frames':FRAMES,'duration':28,'shots':[{'start':a,'end':b,'label':label,'kind':kind}for a,b,label,kind,_ in shots],'frame_focus':timeline},ensure_ascii=False,indent=2))
print('EPISODE_READY',flush=True)
for frame in [36,180,240,336,432,576,648]:
    s.frame_set(frame);s.render.filepath=str(OUT/('preview_%04d.png'%frame));bpy.ops.render.render(write_still=True)
print('EPISODE_STILLS_READY',flush=True)
