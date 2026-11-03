"""Blender 4.3 / CPU, editable Dery animation with expression PNG texture swaps.
blender -b -t 4 --python build_animation.py -- --preview
blender -b -t 4 --python build_animation.py -- --render
"""
import argparse
import json
import math
import random
import sys
from pathlib import Path
import bpy
from mathutils import Vector, Quaternion, Matrix

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'assets'
OUT=ROOT/'output'
RENDERS=ROOT/'renders'
FPS=15
DURATION=68.377625
END=math.ceil(DURATION*FPS)
parser=argparse.ArgumentParser()
parser.add_argument('--preview',action='store_true')
parser.add_argument('--render',action='store_true')
parser.add_argument('--start',type=int,default=1)
parser.add_argument('--end',type=int,default=END)
opt=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
OUT.mkdir(exist_ok=True)
RENDERS.mkdir(exist_ok=True)
random.seed(2026)
bpy.ops.wm.open_mainfile(filepath=str(ASSETS/'dery_base_limpa.blend'))
s=bpy.context.scene
rig=bpy.data.objects['Dery_Rig']
body=bpy.data.objects['Dery_Body']
head=bpy.data.objects['Dery_Head']
for o in list(s.objects):
    if o not in [rig,body,head]:
        bpy.data.objects.remove(o,do_unlink=True)
rig.animation_data_clear()
for b in rig.pose.bones:
    b.matrix_basis=Matrix.Identity(4)
    b.rotation_mode='QUATERNION'
s.render.engine='CYCLES'
s.cycles.device='CPU'
s.cycles.samples=4
s.cycles.use_denoising=False
s.cycles.use_adaptive_sampling=False
s.cycles.max_bounces=1
s.cycles.diffuse_bounces=0
s.cycles.glossy_bounces=0
s.cycles.use_persistent_data=True
s.render.threads_mode='FIXED'
s.render.threads=4
s.render.resolution_x,s.render.resolution_y=360,640
s.render.resolution_percentage=100
s.render.fps=FPS
s.frame_start,s.frame_end=1,END
s.render.image_settings.file_format='PNG'
s.render.image_settings.color_mode='RGB'
s.render.film_transparent=False
s.render.use_sequencer=False
s.view_settings.view_transform='Standard'
s.view_settings.look='Medium High Contrast'
s.world.use_nodes=True
s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(0,0,0,1)
s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.4


def empty(name,loc=(0,0,0),parent=None):
    o=bpy.data.objects.new(name,None)
    s.collection.objects.link(o)
    o.location=loc
    o.parent=parent
    return o


def mesh(name,verts,faces,material,uv=None,parent=None):
    me=bpy.data.meshes.new(name)
    me.from_pydata(verts,[],faces)
    me.update()
    o=bpy.data.objects.new(name,me)
    s.collection.objects.link(o)
    o.data.materials.append(material)
    o.parent=parent
    if uv:
        layer=me.uv_layers.new(name='UVMap')
        for p in me.polygons:
            for li in p.loop_indices:
                layer.data[li].uv=uv[me.loops[li].vertex_index]
    return o


def emat(name,color,strength=1):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    nt=m.node_tree
    nt.nodes.clear()
    e=nt.nodes.new('ShaderNodeEmission')
    e.inputs['Color'].default_value=(*color,1)
    e.inputs['Strength'].default_value=strength
    out=nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(e.outputs[0],out.inputs['Surface'])
    return m,e


def smooth(x):
    x=max(0,min(1,x))
    return x*x*(3-2*x)


def vlerp(a,b,u):
    return Vector(a).lerp(Vector(b),max(0,min(1,u)))


hero=empty('DERY | world motion')
rig.parent=hero
rig.location=(0,0,0)
rig.rotation_euler=(0,0,0)
for o in [body,head]:
    o.parent=rig
    o.matrix_parent_inverse=Matrix.Identity(4)

# Preserve original UV map and actual supplied geometry; add a second facial UV.
head.data.color_attributes.new(name='ExpressionMask',type='FLOAT_COLOR',domain='CORNER')
head.data.uv_layers.new(name='FaceProjection')
# Adding mesh attributes can invalidate previously cached RNA layer references.
projection=head.data.uv_layers['FaceProjection']
mask=head.data.color_attributes['ExpressionMask']
for poly in head.data.polygons:
    for li in poly.loop_indices:
        v=head.data.vertices[head.data.loops[li].vertex_index]
        x,y,z=v.co
        projection.data[li].uv=((x+.23)/.46,(z-1.37)/.46)
        w=smooth((.110-abs(x))/.028)*smooth((z-1.474)/.025)*smooth((1.647-z)/.025)*smooth((.018-y)/.045)
        mask.data[li].color=(w,w,w,1)


def character_material(name,face=False):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    nt=m.node_tree
    nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial')
    emission=nt.nodes.new('ShaderNodeEmission')
    uv=nt.nodes.new('ShaderNodeUVMap')
    uv.uv_map=body.data.uv_layers[0].name if not face else head.data.uv_layers[0].name
    tex=nt.nodes.new('ShaderNodeTexImage')
    tex.image=bpy.data.images.load(str(ASSETS/'Dery_Material_Diffuse.png'),check_existing=True)
    tex.interpolation='Closest'
    nt.links.new(uv.outputs[0],tex.inputs['Vector'])
    color=tex.outputs['Color']
    weights={}
    if face:
        p_uv=nt.nodes.new('ShaderNodeUVMap')
        p_uv.uv_map='FaceProjection'
        masknode=nt.nodes.new('ShaderNodeVertexColor')
        masknode.layer_name='ExpressionMask'
        for label in ['susto','panico','derrota']:
            exp=nt.nodes.new('ShaderNodeTexImage')
            exp.name='PNG | '+label
            exp.image=bpy.data.images.load(str(ASSETS/('expressao_'+label+'.png')),check_existing=True)
            exp.interpolation='Closest'
            nt.links.new(p_uv.outputs[0],exp.inputs['Vector'])
            weight=nt.nodes.new('ShaderNodeValue')
            weight.name='EXPRESSION | '+label
            weight.outputs[0].default_value=0
            mul=nt.nodes.new('ShaderNodeMath'); mul.operation='MULTIPLY'
            nt.links.new(masknode.outputs['Color'],mul.inputs[0])
            nt.links.new(weight.outputs[0],mul.inputs[1])
            alpha=nt.nodes.new('ShaderNodeMath'); alpha.operation='MULTIPLY'
            nt.links.new(mul.outputs[0],alpha.inputs[0])
            nt.links.new(exp.outputs['Alpha'],alpha.inputs[1])
            blend=nt.nodes.new('ShaderNodeMixRGB')
            nt.links.new(alpha.outputs[0],blend.inputs[0])
            nt.links.new(color,blend.inputs[1])
            nt.links.new(exp.outputs['Color'],blend.inputs[2])
            color=blend.outputs[0]
            weights[label]=weight.outputs[0]
    # Directional, normal-based game lighting without stochastic raytracing noise.
    geom=nt.nodes.new('ShaderNodeNewGeometry')
    dot=nt.nodes.new('ShaderNodeVectorMath'); dot.operation='DOT_PRODUCT'
    dot.inputs[1].default_value=(.25,-.65,.72)
    nt.links.new(geom.outputs['Normal'],dot.inputs[0])
    level=nt.nodes.new('ShaderNodeMath'); level.operation='MULTIPLY_ADD'
    level.inputs[1].default_value=.25
    level.inputs[2].default_value=.80
    nt.links.new(dot.outputs['Value'],level.inputs[0])
    shaded=nt.nodes.new('ShaderNodeMixRGB'); shaded.blend_type='MULTIPLY'; shaded.inputs[0].default_value=1
    nt.links.new(color,shaded.inputs[1])
    nt.links.new(level.outputs[0],shaded.inputs[2])
    nt.links.new(shaded.outputs[0],emission.inputs['Color'])
    nt.links.new(emission.outputs[0],out.inputs['Surface'])
    return m,weights


bm,_=character_material('DERY | original texture + game lighting')
hm,expressions=character_material('DERY | UV expression PNGs',True)
body.data.materials.clear(); body.data.materials.append(bm)
head.data.materials.clear(); head.data.materials.append(hm)

# Stretch the actual skinned character, anchoring the head and stretching feet away.
latdata=bpy.data.lattices.new('Tidal deformation cage')
latdata.points_u,latdata.points_v,latdata.points_w=2,2,17
latdata.interpolation_type_u=latdata.interpolation_type_v=latdata.interpolation_type_w='KEY_LINEAR'
lat=bpy.data.objects.new('TIDAL STRETCH | editable shape key',latdata)
s.collection.objects.link(lat)
lat.parent=hero
lat.location=(0,0,.90)
lat.scale=(1.8,.9,2.1/(latdata.points_w-1))
lat.shape_key_add(name='Basis')
stretch=lat.shape_key_add(name='Espaguetificacao')
for p in stretch.data:
    x,y,z=p.co
    wz=z*lat.scale.z+lat.location.z
    amount=smooth((1.36-wz)/.85)
    nz=1.36-(1.36-wz)*2.35 if wz<1.36 else wz
    p.co=(x*(1-.40*amount),y*(1-.15*amount),(nz-lat.location.z)/lat.scale.z)
for o in [body,head]:
    mod=o.modifiers.new('Tidal stretch | after skinning','LATTICE')
    mod.object=lat

# Painted astronomical sky plate is an environment asset, not a character animation.
plate_mat,plate_emit=emat('sky | retro photographic black hole',(1,1,1))
nt=plate_mat.node_tree
skytex=nt.nodes.new('ShaderNodeTexImage')
skytex.image=bpy.data.images.load(str(ASSETS/'ceu_buraco_negro.png'))
skytex.interpolation='Closest'
nt.links.new(skytex.outputs['Color'],plate_emit.inputs['Color'])
plate=mesh('SKY | astronomical matte environment',[(-17,20,-12),(13,20,-12),(13,20,8),(-17,20,8)],[(0,1,2,3)],plate_mat,[(0,0),(1,0),(1,1),(0,1)])
uvsky=nt.nodes.new('ShaderNodeTexCoord')
sep=nt.nodes.new('ShaderNodeSeparateXYZ')
nt.links.new(uvsky.outputs['UV'],sep.inputs[0])
edges=[]
for component in ['X','Y']:
    sub=nt.nodes.new('ShaderNodeMath'); sub.operation='SUBTRACT'; sub.inputs[0].default_value=1
    nt.links.new(sep.outputs[component],sub.inputs[1])
    minimum=nt.nodes.new('ShaderNodeMath'); minimum.operation='MINIMUM'
    nt.links.new(sep.outputs[component],minimum.inputs[0]); nt.links.new(sub.outputs[0],minimum.inputs[1])
    edges.append(minimum.outputs[0])
edge=nt.nodes.new('ShaderNodeMath'); edge.operation='MINIMUM'
nt.links.new(edges[0],edge.inputs[0]); nt.links.new(edges[1],edge.inputs[1])
edgegain=nt.nodes.new('ShaderNodeMath'); edgegain.operation='MULTIPLY'; edgegain.inputs[1].default_value=10; edgegain.use_clamp=True
nt.links.new(edge.outputs[0],edgegain.inputs[0])
skymul=nt.nodes.new('ShaderNodeMixRGB'); skymul.blend_type='MULTIPLY'; skymul.inputs[0].default_value=1
nt.links.new(skytex.outputs['Color'],skymul.inputs[1]); nt.links.new(edgegain.outputs[0],skymul.inputs[2])
nt.links.new(skymul.outputs[0],plate_emit.inputs['Color'])

# Real 3D star particles provide parallax and downward motion after the boundary.
starcolors=[(.34,.48,.8),(.65,.75,.9),(.6,.38,.15)]
star_mats=[emat('stars '+str(i),c,1.2)[0] for i,c in enumerate(starcolors)]
verts,faces,inds=[],[],[]
for i in range(900):
    x,y,z=random.uniform(-32,32),random.uniform(6,19),random.uniform(-25,22)
    r=random.choice([.008,.015,.022,.035])
    n=len(verts)
    verts.extend([(x-r,y,z),(x,y,z+r),(x+r,y,z),(x,y,z-r)])
    faces.append((n,n+1,n+2,n+3)); inds.append(random.randrange(3))
stars=mesh('SPACE | 900 parallax stars',verts,faces,star_mats[0])
for m in star_mats[1:]: stars.data.materials.append(m)
for p,idx in zip(stars.data.polygons,inds): p.material_index=idx

wiremat,wire_emit=emat('horizon | momentary schematic indicator',(.15,.35,.7),.6)
bpy.ops.mesh.primitive_torus_add(major_segments=96,minor_segments=4,major_radius=1.85,minor_radius=.005,location=(0,0,-.6))
horizon=bpy.context.object
horizon.name='HORIZON | diagram only, no physical wall'
horizon.data.materials.append(wiremat)


def arrow(name,x,z,length,color):
    m,_=emat(name+' color',color,1.1)
    root=empty(name,(x,-.08,z),hero)
    bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=.022,depth=length*.73)
    shaft=bpy.context.object; shaft.name=name+' shaft'; shaft.parent=root; shaft.location=(0,0,-length*.365)
    shaft.data.materials.append(m)
    bpy.ops.mesh.primitive_cone_add(vertices=6,radius1=0,radius2=.075,depth=length*.27)
    tip=bpy.context.object; tip.name=name+' tip'; tip.parent=root; tip.location=(0,0,-length*.865)
    tip.data.materials.append(m)
    return root


footarrow=arrow('FORCE | feet',.48,.33,.68,(1,.48,.08))
headarrow=arrow('FORCE | head',.48,1.68,.24,(.14,.54,1))

camdata=bpy.data.cameras.new('portrait camera')
cam=bpy.data.objects.new('CAMERA | shot animation',camdata)
s.collection.objects.link(cam)
s.camera=cam
camdata.clip_start=.025
camdata.clip_end=160
camdata.lens=35

cuts=[
 (0,'01 | queda / gancho'),(4.23,'02 | supermassivo'),(7.43,'03 | limite invisivel'),
 (12.68,'04 | sem impacto'),(18.35,'05 | tentativa de fuga'),(23.43,'06 | pes primeiro'),
 (28.2,'07 | comparacao de forcas'),(34.9,'08 | alongamento'),(40.6,'09 | espaguetificacao'),
 (45.08,'10 | miojo / reacao'),(48.75,'11 | olhar para o centro'),(53.4,'12 | desconhecido'),
 (58.6,'13 | portal / ironia'),(65.1,'14 | fim')]
for t,name in cuts: s.timeline_markers.new(name,frame=round(t*FPS)+1)
(ROOT/'timing.json').write_text(json.dumps({'duration_audio_seconds':DURATION,'source_fps':FPS,'source_frames':END,'timing_method':'Approved text and measured audio pauses; scene boundaries are editorial estimates, not a word-level ASR transcript.','shots':[{'start':t,'name':n} for t,n in cuts]},ensure_ascii=False,indent=2))

bone_names=['pelvis','waist','chest','upper_chest','neck','head','arm_L','forearm_L','hand_L','arm_R','forearm_R','hand_R','thigh_L','shin_L','foot_L','thigh_R','shin_R','foot_R','CC_Base_JawRoot']
rest={n:rig.data.bones[n].matrix_local.to_quaternion() for n in bone_names}


def delta(name,axis,angle):
    q=Quaternion(axis,angle)
    rig.pose.bones[name].rotation_quaternion=rest[name].inverted()@q@rest[name]


def transform_key(o,f):
    for path in ['location','rotation_euler','scale']:
        o.keyframe_insert(data_path=path,frame=f)


# Whole-frame fade only at the ending; no subtitles or text overlays.
s.use_nodes=True
nodes=s.node_tree.nodes
nodes.clear()
rl=nodes.new('CompositorNodeRLayers')
glare=nodes.new('CompositorNodeGlare'); glare.glare_type='FOG_GLOW'; glare.quality='LOW'; glare.threshold=1.4; glare.size=6; glare.mix=-.97
fade=nodes.new('CompositorNodeMixRGB'); fade.blend_type='MULTIPLY'; fade.inputs[0].default_value=1
comp=nodes.new('CompositorNodeComposite')
s.node_tree.links.new(rl.outputs['Image'],glare.inputs[0])
s.node_tree.links.new(glare.outputs[0],fade.inputs[1])
s.node_tree.links.new(fade.outputs[0],comp.inputs[0])

for f in range(1,END+1):
    t=(f-1)/FPS
    for n in bone_names: rig.pose.bones[n].rotation_quaternion=Quaternion()
    z=0 if t<7.43 else (-.9*smooth((t-7.43)/5.25) if t<12.68 else (-.9-min(t-12.68,10.75)*.10))
    hero.location=(.04*math.sin(t*.7),0,z)
    hero.rotation_euler=(.035*math.sin(t*.9),.045*math.sin(t*.7),.10*math.sin(t*.55))
    delta('pelvis',(0,1,0),.035*math.sin(t*1.3))
    delta('chest',(0,0,1),.035*math.sin(t*1.6))
    delta('head',(0,0,1),.12*math.sin(t*.9))
    delta('neck',(1,0,0),.04*math.sin(t*1.3))
    arm_angle,bend=.98,.36
    if 12.68<=t<18.35:
        arm_angle=.55+.10*math.sin(t*2)
        bend=1.15
        delta('head',(1,0,0),-.06*math.sin(t*2.4))
    if 18.35<=t<23.43:
        arm_angle=.55
        bend=.75
        hero.rotation_euler.x=.12*math.sin(t*2)
    if 28.2<=t<34.9:
        arm_angle=1.15
        bend=.5
        delta('head',(1,0,0),.25)
    if 34.9<=t<45.08:
        arm_angle=.70
        bend=.45
    if t>=45.08:
        arm_angle=1.16
        bend=.20
    if 53.4<=t<58.6:
        arm_angle=.60
        bend=.85
    if 58.6<=t<65.1:
        nod=Quaternion((0,0,1),.12*math.sin((t-58.6)*3))@Quaternion((0,1,0),-.07)
        rig.pose.bones['head'].rotation_quaternion=rest['head'].inverted()@nod@rest['head']
    for side,suffix in [(1,'L'),(-1,'R')]:
        a=arm_angle+.10*math.sin(t*1.7+side)
        b=bend+.10*math.sin(t*2.1+side)
        if 18.35<=t<23.43:
            a=.75+.55*math.sin(t*4+side*1.57)
            b=.8+.6*math.sin(t*4+side*1.57+.5)
        delta('arm_'+suffix,(0,1,0),side*a)
        delta('forearm_'+suffix,(0,0,1),-side*b)
        delta('hand_'+suffix,(1,0,0),.12*math.sin(t*2+side))
        kick=.25 if 18.35<=t<23.43 else .10
        delta('thigh_'+suffix,(1,0,0),kick*math.sin(t*2.5+side*1.57))
        delta('shin_'+suffix,(1,0,0),.12+kick*.8*(1+math.sin(t*2.5+side*1.57)))
        delta('foot_'+suffix,(1,0,0),-.06)
    strain=smooth((t-34.9)/5.4)
    stretch.value=strain
    stretch.keyframe_insert(data_path='value',frame=f)
    w={'susto':0,'panico':0,'derrota':0}
    if 1.8<t<12.68: w['susto']=.8
    if 18.35<=t<23.43: w['panico']=1
    if 23.43<=t<34.9: w['susto']=.7
    if 34.9<=t<45.08: w['panico']=1
    if 45.08<=t<48.75: w['derrota']=1
    if 48.75<=t<53.4: w['susto']=.65
    if 53.4<=t<65.1: w['derrota']=.8
    if t>=65.1: w['susto']=.7
    for label,value in w.items():
        expressions[label].default_value=value
        expressions[label].keyframe_insert(data_path='default_value',frame=f)
    if t<4.23:
        u=t/4.23
        cp=vlerp((.18,-1.0,1.63),(.32,-1.65,1.58),u)
        target=vlerp((0,0,1.40),(0,0,1.25),u)
        lens=38-6*u
    elif t<7.43:
        cp=Vector((.35,-6.8,2.0)); target=Vector((0,0,.8)); lens=28
    elif t<12.68:
        u=(t-7.43)/5.25
        cp=vlerp((1.2,-3.5,1.8),(.7,-3.0,1.5),u); target=Vector((0,0,.85)); lens=32
    elif t<18.35:
        cp=Vector((.25,-1.4,1.65)); target=Vector((0,0,1.33)); lens=35
    elif t<23.43:
        cp=Vector((.55+.15*math.sin(t),-3.0,1.65)); target=Vector((0,0,.95)); lens=35
    elif t<28.2:
        cp=Vector((.20,-1.15,.48)); target=Vector((0,0,.20)); lens=38
    elif t<34.9:
        cp=Vector((-.20,-2.8,1.0)); target=Vector((.12,0,.85)); lens=32
    elif t<40.6:
        cp=vlerp((.35,-3.0,1.2),(.3,-4.5,.3),strain)
        target=vlerp((0,0,.8),(0,0,-.35),strain); lens=32
    elif t<45.08:
        cp=Vector((.3,-4.5,.3)); target=Vector((0,0,-.35)); lens=32
    elif t<48.75:
        cp=Vector((.10,-.92,1.62)); target=Vector((0,0,1.60)); lens=40
    elif t<53.4:
        cp=Vector((0,-.30,1.66)); target=Vector((0,-.13,-7)); lens=28
    elif t<58.6:
        cp=Vector((.55,-1.6,1.70)); target=Vector((0,0,1.4)); lens=35
    elif t<65.1:
        cp=Vector((.10,-1.1,1.64)); target=Vector((0,0,1.57)); lens=39
    else:
        u=smooth((t-65.1)/3.2)
        hero.location.z-=u*7
        cp=Vector((.3,-3.4,1.1+u*7))
        target=Vector((0,0,.35+u*5))
        lens=30
    cam.location=hero.location+cp
    cam.rotation_euler=(hero.location+target-cam.location).to_track_quat('-Z','Y').to_euler()
    camdata.lens=lens
    # Fixed editorial cuts, moving perspective within each shot.
    for o in [hero,cam]: transform_key(o,f)
    camdata.keyframe_insert(data_path='lens',frame=f)
    for n in bone_names: rig.pose.bones[n].keyframe_insert(data_path='rotation_quaternion',frame=f,group=n)
    visible=28.2<=t<34.9
    for a in [footarrow,headarrow]:
        a.scale=(1,1,1) if visible else (0,0,0)
        a.keyframe_insert(data_path='scale',frame=f)
    horizon.hide_render=not (8.3<=t<12.68)
    horizon.keyframe_insert(data_path='hide_render',frame=f)
    plate_emit.inputs['Strength'].default_value=1-smooth((t-23.43)/13)
    plate_emit.inputs['Strength'].keyframe_insert(data_path='default_value',frame=f)
    stars.location.z=(t*.16)%5
    stars.scale=(1,1,1+.15*smooth((t-23.43)/10))
    transform_key(stars,f)
    gain=1-smooth((t-66.9)/.95)
    fade.inputs[2].default_value=(gain,gain,gain,1)
    fade.inputs[2].keyframe_insert(data_path='default_value',frame=f)

# Per-frame baking avoids camera interpolation across cuts and texture crossfades.
for datablock in [hero,rig,cam,camdata,stars,footarrow,headarrow,horizon,latdata.shape_keys,hm.node_tree,plate_mat.node_tree,s.node_tree]:
    if datablock.animation_data and datablock.animation_data.action:
        for fc in datablock.animation_data.action.fcurves:
            for k in fc.keyframe_points: k.interpolation='CONSTANT'
editor=s.sequence_editor_create()
editor.sequences.new_sound('VOZ | original, sem acelerar',str(ASSETS/'voz_original.mp3'),channel=1,frame_start=1)
s.frame_set(1)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Dery_Buraco_Negro.blend'))
if opt.preview:
    for t in [0.8,5.5,14.8,20,30,38.2,46.8,50.5,60.8,66.2]:
        s.frame_set(round(t*FPS)+1)
        s.render.filepath=str(OUT/('preview_%04d.png'%round(t*10)))
        bpy.ops.render.render(write_still=True)
if opt.render:
    s.frame_start,s.frame_end=opt.start,opt.end
    s.render.filepath=str(RENDERS/'frame_')
    bpy.ops.render.render(animation=True)
