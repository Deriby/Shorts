"""Facial acting and chest-height conversational gestures on the R2 edit.

Approved monitor-focused takes remain identical and reuse their R2 frames.
"""
from pathlib import Path
import bpy,sys,math,json,shutil
from mathutils import Vector,Quaternion
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]/'003-teste-quarto-gamer/production'))
import helpers as H
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'output/Dery_Crash_Master_R2.blend'))
s=bpy.context.scene;s.frame_set(1)
rig=bpy.data.objects['Dery_Rig'];avatar=bpy.data.objects['DERY | animated character']
mesh=avatar.data;keys=mesh.shape_keys
face=next(m for m in mesh.materials if 'VOICE | mouth envelope'in m.node_tree.nodes)
nt=face.node_tree
old_actions={owner:owner.animation_data.action.copy()for owner in [rig,keys,nt]if owner.animation_data and owner.animation_data.action}

def gaussian(v,x,z,sx,sz):
    return math.exp(-((abs(v.x)-x)/sx)**2-((v.z-z)/sz)**2)*max(0,min(1,(.01-v.y)/.035))
names=['Full smile','Happy eyes','Cheek lift','Friendly brows','One eyebrow','Wide eyes']
shapes={name:avatar.shape_key_add(name=name)for name in names}
for v in mesh.vertices:
    x,y,z=v.co
    a=gaussian(v.co,.028,1.504,.018,.018)
    shapes['Full smile'].data[v.index].co.z+=.011*a
    shapes['Full smile'].data[v.index].co.x+=math.copysign(.004*a,x)
    eye=gaussian(v.co,.046,1.574,.025,.018)
    shapes['Happy eyes'].data[v.index].co.z+=(1.574-z)*.70*eye
    shapes['Wide eyes'].data[v.index].co.z+=(z-1.574)*.60*eye
    cheek=gaussian(v.co,.065,1.548,.028,.025)
    shapes['Cheek lift'].data[v.index].co.z+=.009*cheek
    shapes['Cheek lift'].data[v.index].co.y-=.002*cheek
    brow=gaussian(v.co,.038,1.609,.035,.015)
    shapes['Friendly brows'].data[v.index].co.z+=.010*brow
    shapes['One eyebrow'].data[v.index].co.z+=(.016 if x>0 else -.002)*brow

# A broad mouth and visible upper teeth follow the smiling mesh, rather than
# leaving the original straight mouth beneath a subtle corner deformation.
def mathnode(op,a,b=None,c=None):
    n=nt.nodes.new('ShaderNodeMath');n.operation=op
    for i,val in enumerate([a,b,c]):
        if val is None:continue
        if isinstance(val,(int,float)):n.inputs[i].default_value=val
        else:nt.links.new(val,n.inputs[i])
    return n.outputs[0]
def value(name):
    n=nt.nodes.new('ShaderNodeValue');n.name=name;return n.outputs[0]
grin=value('R3 | grin');shock=value('R3 | surprise');enabled=value('R3 | facial overlay')
uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map='FaceProjection'
sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(uv.outputs[0],sep.inputs[0])
x=mathnode('MULTIPLY_ADD',sep.outputs['X'],.46,-.23)
z=mathnode('MULTIPLY_ADD',sep.outputs['Y'],.46,1.37-1.504)
voice=nt.nodes['VOICE | mouth envelope'].outputs[0]
width=mathnode('ADD',mathnode('MULTIPLY_ADD',grin,.014,.022),mathnode('MULTIPLY',shock,.002))
height=mathnode('ADD',mathnode('ADD',mathnode('MULTIPLY_ADD',voice,.006,.003),mathnode('MULTIPLY',grin,.004)),mathnode('MULTIPLY',shock,.015))
dx=mathnode('DIVIDE',x,width);dy=mathnode('DIVIDE',z,height)
distance=mathnode('ADD',mathnode('MULTIPLY',dx,dx),mathnode('MULTIPLY',dy,dy))
alpha=mathnode('MULTIPLY',mathnode('SUBTRACT',1,distance),10)
clamp=nt.nodes.new('ShaderNodeClamp');nt.links.new(alpha,clamp.inputs[0])
front=nt.nodes.new('ShaderNodeVertexColor');front.layer_name='MouthFrontOnly'
alpha=mathnode('MULTIPLY',mathnode('MULTIPLY',clamp.outputs[0],enabled),front.outputs['Color'])
alpha=mathnode('MULTIPLY',alpha,mathnode('GREATER_THAN',mathnode('ADD',grin,shock),.15))
teeth=mathnode('MULTIPLY',mathnode('GREATER_THAN',z,.0005),mathnode('LESS_THAN',z,.0045))
teeth=mathnode('MULTIPLY',teeth,mathnode('GREATER_THAN',grin,.30))
teeth=mathnode('MULTIPLY',teeth,mathnode('LESS_THAN',shock,.20))
mouthcolor=nt.nodes.new('ShaderNodeMixRGB')
mouthcolor.inputs[1].default_value=(.012,.003,.004,1);mouthcolor.inputs[2].default_value=(.82,.78,.66,1)
nt.links.new(teeth,mouthcolor.inputs[0])
out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL')
em=out.inputs['Surface'].links[0].from_node
lighting=em.inputs['Color'].links[0].from_node
old_albedo=lighting.inputs[1].links[0].from_socket
overlay=nt.nodes.new('ShaderNodeMixRGB')
nt.links.new(old_albedo,overlay.inputs[1]);nt.links.new(mouthcolor.outputs[0],overlay.inputs[2]);nt.links.new(alpha,overlay.inputs[0])
nt.links.new(overlay.outputs[0],lighting.inputs[1])

# Two-bone IK raises the wrists to the chest so the gestures actually appear
# in the close/medium framing. Targets stay within the supplied arm lengths.
frontdir=Vector((math.sin(.60),-math.cos(.60),0));up=Vector((0,0,1))
controls={}
for side,sign in [('R',-1),('L',1)]:
    arm=rig.pose.bones['arm_'+side];forearm=rig.pose.bones['forearm_'+side]
    shoulder=rig.matrix_world@arm.head
    outward=Vector((math.cos(.60)*sign,math.sin(.60)*sign,0))
    target=bpy.data.objects.new('R3 | '+side+' wrist',None);s.collection.objects.link(target)
    pole=bpy.data.objects.new('R3 | '+side+' elbow',None);s.collection.objects.link(pole)
    pole.location=shoulder+outward*.50+frontdir*.08-up*.18
    target.location=shoulder+frontdir*.22+outward*.14-up*.24
    ik=forearm.constraints.new('IK');ik.name='R3 | conversational gesture';ik.target=target;ik.pole_target=pole;ik.chain_count=2
    inv=rig.matrix_world.inverted();polelocal=inv@pole.location
    restarm=rig.data.bones['arm_'+side];restforearm=rig.data.bones['forearm_'+side]
    axis=restforearm.tail_local-restarm.head_local
    plane=axis.cross(polelocal-restarm.head_local)
    projected=plane.cross(restarm.tail_local-restarm.head_local).normalized()
    ik.pole_angle=restarm.x_axis.angle(projected)
    if restarm.x_axis.cross(projected).dot(restarm.tail_local-restarm.head_local)<0:ik.pole_angle=-ik.pole_angle
    controls[side]=(target,ik,shoulder,outward)

info=json.loads((ROOT/'timeline_r2.json').read_text())
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def pulse(t,a,b):return math.sin(math.pi*(t-a)/(b-a))if a<t<b else 0
for frame in range(1,673):
    s.frame_set(frame);t=(frame-1)/24
    kind=next(x['kind']for x in info['shots']if x['start']<=frame<=x['end'])
    visible=not kind.startswith('monitor')
    smile=.90*pulse(t,3.3,5.8)+.4*pulse(t,18.5,21)+.95*smooth((t-25.4)/.9)
    surprise=.90*pulse(t,16.65,18.6)
    sly=.80*pulse(t,.1,3.3)+.6*pulse(t,21,25)
    if not visible:smile=surprise=sly=0
    shapes['Full smile'].value=smile
    shapes['Happy eyes'].value=smile*.80
    shapes['Cheek lift'].value=smile*.90
    shapes['Friendly brows'].value=smile*.70+surprise*.85
    shapes['One eyebrow'].value=sly
    shapes['Wide eyes'].value=surprise
    for shape in shapes.values():H.record(shape,'value',frame)
    grin.default_value=smile;shock.default_value=surprise;enabled.default_value=float(visible)
    for socket in [grin,shock,enabled]:H.record(socket,'default_value',frame)
    # Phrase-driven beats, with alternating emphasis and a two-handed shrug.
    right=max(pulse(t,.25,2.8),pulse(t,3.6,5.8),pulse(t,6,8.75),pulse(t,16.8,18.5),pulse(t,20.9,23.6),pulse(t,25.5,27.8))
    left=max(.75*pulse(t,1.3,3.1),.9*pulse(t,3.7,5.8),.8*pulse(t,6.3,8.7),.9*pulse(t,16.8,18.5),.85*pulse(t,23,25.3),.85*pulse(t,25.5,27.8))
    for side,g in [('R',right),('L',left)]:
        target,ik,shoulder,outward=controls[side]
        ik.influence=1 if visible else 0;H.record(ik,'influence',frame)
        target.location=shoulder+frontdir*(.20+.075*g)+outward*(.13+.035*math.sin(t*2.4))+up*(-.27+.255*g)
        H.record(target,'location',frame)
        for name in ['arm_'+side,'forearm_'+side]:
            bone=rig.pose.bones[name]
            if visible:bone.rotation_quaternion=(1,0,0,0)
            H.record(bone,'rotation_quaternion',frame)
        hand=rig.pose.bones['hand_'+side]
        if visible:hand.rotation_quaternion=Quaternion((0,1,0),(.55 if side=='R'else -.55)*g)
        H.record(hand,'rotation_quaternion',frame)

H.commit_curves()
# Keep the R2 head, torso, lips, cameras, and original tiny shape movements.
for owner,old in old_actions.items():
    action=owner.animation_data.action
    paths={(f.data_path,f.array_index)for f in action.fcurves}
    for f in old.fcurves:
        if (f.data_path,f.array_index)in paths:continue
        new=action.fcurves.new(f.data_path,index=f.array_index)
        coords=[n for p in f.keyframe_points for n in p.co]
        new.keyframe_points.add(len(f.keyframe_points));new.keyframe_points.foreach_set('co',coords)
        for p in new.keyframe_points:p.interpolation='CONSTANT'
        new.update()

out=ROOT/'output/Dery_Crash_Master_R3.blend'
s.frame_set(1);s.render.filepath=str(ROOT/'renders/r3/frame_')
bpy.ops.wm.save_as_mainfile(filepath=str(out));bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(out))
(ROOT/'timeline_r3.json').write_text(json.dumps(info,indent=2))
shutil.copyfile(ROOT/'vertical_crops_r2.json',ROOT/'vertical_crops_r3.json')
frames=ROOT/'renders/r3';frames.mkdir(parents=True,exist_ok=True)
reuse=[]
for shot in info['shots']:
    if shot['kind'].startswith('monitor'):
        for f in range(shot['start'],shot['end']+1):
            source=ROOT/'renders/r2'/f'frame_{f:04d}.png'
            if source.exists():
                shutil.copyfile(source,frames/f'frame_{f:04d}.png');reuse.append(f)
(ROOT/'reuse_r3.json').write_text(json.dumps({'source':'R2','frames':reuse,'reason':'Approved monitor-focused takes; original facial layer and arm animation retained'},indent=2))
for f in [110,535,640]:
    s.frame_set(f);s.render.filepath=str(ROOT/'output'/f'preview_r3_{f:04d}.png');bpy.ops.render.render(write_still=True)
print('R3_READY',flush=True)
