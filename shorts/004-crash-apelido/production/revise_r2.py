"""Revise the cached episode: native face, live gestures, 13 cuts, user gameplay."""
from pathlib import Path
import bpy,sys,math,json,wave,array
from mathutils import Vector,Quaternion
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parents[1]/'003-teste-quarto-gamer/production'
sys.path.insert(0,str(BASE));import helpers as H
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'output/Dery_Crash_Master.blend'))
s=bpy.context.scene;s.frame_set(1)
rig=bpy.data.objects['Dery_Rig'];cam=s.camera;avatar=bpy.data.objects['DERY | animated character']
baseline={b.name:b.rotation_quaternion.copy()for b in rig.pose.bones}
rest={b.name:b.matrix_local.to_quaternion()for b in rig.data.bones}
rig.animation_data_clear();cam.animation_data_clear();cam.data.animation_data_clear()
face=next(m for m in avatar.data.materials if 'VOICE | mouth envelope' in m.node_tree.nodes)
face.node_tree.animation_data_clear();nt=face.node_tree
# Remove the projected eye images that warped the expression. Facial movement
# now comes from small deformations of the supplied mesh and head/body acting.
for n in nt.nodes:
    if n.name.startswith('EXPRESSION | '):n.outputs[0].default_value=0
for n in nt.nodes:
    if n.type=='MATH' and n.operation=='DIVIDE' and abs(n.inputs[1].default_value-.026)<1e-6:n.inputs[1].default_value=.021
    if n.type=='MATH' and n.operation=='MULTIPLY_ADD' and n.inputs[0].is_linked and n.inputs[0].links[0].from_node.name=='VOICE | mouth envelope':
        n.inputs[1].default_value=.0055;n.inputs[2].default_value=.0015
mesh=avatar.data
mask=mesh.color_attributes.new(name='MouthFrontOnly',type='FLOAT_COLOR',domain='CORNER')
for poly in mesh.polygons:
    for li in poly.loop_indices:
        v=mesh.vertices[mesh.loops[li].vertex_index].co
        value=max(0,min(1,(.01-v.y)/.025))
        mask.data[li].color=(value,value,value,1)
for n in list(nt.nodes):
    if n.type=='MIX_RGB' and abs(n.inputs[2].default_value[0]-.016)<1e-5 and abs(n.inputs[2].default_value[1]-.004)<1e-5:
        prior=n.inputs[0].links[0].from_socket
        attr=nt.nodes.new('ShaderNodeVertexColor');attr.layer_name='MouthFrontOnly'
        mul=nt.nodes.new('ShaderNodeMath');mul.operation='MULTIPLY'
        nt.links.new(prior,mul.inputs[0]);nt.links.new(attr.outputs['Color'],mul.inputs[1]);nt.links.new(mul.outputs[0],n.inputs[0])
avatar.shape_key_add(name='Basis')
brow=avatar.shape_key_add(name='Brow emphasis')
smile=avatar.shape_key_add(name='Small smile')
for v in mesh.vertices:
    x,y,z=v.co
    front=max(0,min(1,(.008-y)/.035))
    bw=math.exp(-((abs(x)-.043)/.028)**2-((z-1.608)/.018)**2)*front
    sw=math.exp(-((abs(x)-.026)/.014)**2-((z-1.505)/.012)**2)*front
    brow.data[v.index].co.z+=.004*bw
    smile.data[v.index].co.z+=.003*sw

screen=bpy.data.objects['CRT moving picture'];mt=screen.data.materials[0].node_tree
tex=next(n for n in mt.nodes if n.type=='TEX_IMAGE')
tex.image=bpy.data.images.load(str(ROOT/'assets/gameplay/monitor_feed_r2.mp4'))
tex.image_user.frame_start=1;tex.image_user.frame_offset=0;tex.image_user.frame_duration=672;tex.image_user.use_auto_refresh=True
next(n for n in mt.nodes if n.type=='EMISSION').inputs['Strength'].default_value=1.30
with wave.open(str(ROOT/'assets/voz/narracao_completa.wav'))as w:
    samples=array.array('h',w.readframes(w.getnframes()));sr=w.getframerate()
def rms(t):
    p=samples[int(t*sr):int((t+.045)*sr)]
    return min(.8,max(0,(math.sqrt(sum((v/32768)**2 for v in p)/max(1,len(p)))-.009)*8))
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
def pulse(t,a,b):return math.sin(math.pi*max(0,min(1,(t-a)/(b-a))))if a<t<b else 0
def rotate(name,axis,angle):rig.pose.bones[name].rotation_quaternion=baseline[name]@(rest[name].inverted()@Quaternion(axis,angle)@rest[name])
shots=[(1,62,'close'),(63,105,'medium'),(106,145,'reaction'),(146,211,'wide'),
       (212,268,'monitor'),(269,324,'monitor2'),(325,364,'side'),(365,401,'monitor3'),
       (402,445,'reaction'),(446,500,'wide'),(501,554,'medium'),(555,613,'close'),(614,672,'punch')]
for marker in list(s.timeline_markers):s.timeline_markers.remove(marker)
for i,(a,b,kind)in enumerate(shots):s.timeline_markers.new(f'{i+1:02d} | {kind}',frame=a)
for f in range(1,673):
    t=(f-1)/24
    a,b,kind=next(x for x in shots if x[0]<=f<=x[1]);u=(f-a)/max(1,b-a)
    look=smooth((t-7.4)/.65)*(1-smooth((t-16.1)/.45))
    head_yaw=.62*(1-look)-.50*look+.045*math.sin(t*2.1)
    rig.pose.bones['head'].rotation_quaternion=(rest['head'].inverted()@Quaternion((0,0,1),head_yaw)@rest['head'])@(rest['head'].inverted()@Quaternion((1,0,0),.035*math.sin(t*4.6))@rest['head'])
    rotate('neck',(0,0,1),.04*math.sin(t*1.8))
    rotate('upper_chest',(1,0,0),.018*math.sin(t*2.3)+.018*pulse(t,25.5,27.8))
    g=min(1,sum(pulse(t,a,b)for a,b in [(.5,2.6),(3.7,5.7),(6,8.7),(11.7,14.5),(16.8,18.5),(21,24),(25.5,27.8)]))
    left=.75*pulse(t,3.7,5.7)+.65*pulse(t,16.8,18.5)+.55*pulse(t,25.5,27.8)
    rotate('arm_R',(0,1,0),.26*g);rotate('forearm_R',(1,0,0),-.46*g);rotate('hand_R',(0,0,1),.18*g)
    rotate('arm_L',(0,1,0),-.21*left);rotate('forearm_L',(1,0,0),-.34*left);rotate('hand_L',(0,0,1),-.16*left)
    for name in ['head','neck','upper_chest','arm_R','forearm_R','hand_R','arm_L','forearm_L','hand_L']:
        H.record(rig.pose.bones[name],'rotation_quaternion',f)
    brow.value=.7*pulse(t,3.5,5.5)+.8*pulse(t,16.7,18.6)+.45*pulse(t,25.5,27.8)
    smile.value=.25*pulse(t,3.8,5.5)+.60*smooth((t-25.7)/.8)
    H.record(brow,'value',f);H.record(smile,'value',f)
    mouth=nt.nodes['VOICE | mouth envelope'].outputs[0];mouth.default_value=rms(t);H.record(mouth,'default_value',f)
    if kind=='wide':loc=Vector((1.90,.02,1.65));target=Vector((0,-.15,1.22));lens=44+u
    elif kind=='medium':loc=Vector((1.78,-.08,1.61));target=Vector((0,0,1.28));lens=49+u*2
    elif kind=='side':loc=Vector((1.80,.37,1.68));target=Vector((0,-.10,1.27));lens=46+u
    elif kind.startswith('monitor'):
        loc=Vector({'monitor':(1.08,.48,1.56),'monitor2':(1.22,.22,1.53),'monitor3':(1.15,.33,1.57)}[kind])
        target=Vector((.1095,-.7959,1.262));lens={'monitor':40,'monitor2':45,'monitor3':48}[kind]+u*2
    else:
        loc=Vector((1.24,-.32,1.55));target=Vector((0,.10,1.415));lens={'close':65,'reaction':72,'punch':70}[kind]+u*3
    cam.location=loc;cam.rotation_euler=(target-loc).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
    H.record(cam,'location',f);H.record(cam,'rotation_euler',f);H.record(cam.data,'lens',f)
H.commit_curves()
out=ROOT/'output/Dery_Crash_Master_R2.blend'
s.render.filepath=str(ROOT/'renders/r2/frame_');s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(out));bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(out))
info={'fps':24,'frames':672,'duration':28,'shots':[{'start':a,'end':b,'kind':k}for a,b,k in shots]}
(ROOT/'timeline_r2.json').write_text(json.dumps(info,indent=2))
crops=[]
for a,b,k in shots:
    xs=[]
    for f in [a,b]:
        s.frame_set(f)
        if k.startswith('monitor'):p=Vector((.1095,-.7959,1.262))
        else:
            bone=rig.pose.bones['head'];p=rig.matrix_world@(bone.matrix@(bone.bone.matrix_local.inverted()@Vector((0,-.085,1.59))))
        xs.append(max(0,min(1312,round(world_to_camera_view(s,cam,p).x*1920-304))))
    crops.append({'start':a,'end':b,'kind':k,'x_start':xs[0],'x_end':xs[1]})
(ROOT/'vertical_crops_r2.json').write_text(json.dumps(crops,indent=2))
for f in [110,300]:
    s.frame_set(f);s.render.filepath=str(ROOT/'output'/f'preview_r2_{f:04d}.png');bpy.ops.render.render(write_still=True)
print('REVISION_R2_READY',flush=True)
