"""Multi-set PS1 short: actual rigged character, town, car, coast and planet diagrams."""
import bpy, math, random, json, sys, argparse
from pathlib import Path
from mathutils import Vector,Quaternion,Matrix
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import character as C
ASSETS=ROOT/'assets'; OUT=ROOT/'output'; FRAMES=ROOT/'renders'
FPS=24; DURATION=55.4056875; END=math.ceil(DURATION*FPS)
ap=argparse.ArgumentParser(); ap.add_argument('--preview',action='store_true'); ap.add_argument('--render',action='store_true')
args=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
random.seed(208)
bpy.ops.wm.open_mainfile(filepath=str(ASSETS/'dery_base_limpa.blend'))
s=bpy.context.scene
for o in list(s.objects):
    if o.name not in ['Dery_Rig','Dery_Body','Dery_Head']: bpy.data.objects.remove(o,do_unlink=True)
C.setup(ASSETS); C.cache_clips()
hero,rig=C.hero,C.rig
s.render.engine='CYCLES'; s.cycles.samples=2; s.cycles.use_denoising=False; s.cycles.use_adaptive_sampling=False
s.cycles.max_bounces=1; s.cycles.transparent_max_bounces=8; s.cycles.diffuse_bounces=0; s.cycles.glossy_bounces=0
s.cycles.use_persistent_data=True; s.render.threads_mode='FIXED'; s.render.threads=4
s.render.resolution_x,s.render.resolution_y=432,768; s.render.resolution_percentage=100
s.render.fps=FPS; s.frame_start,s.frame_end=1,END
s.render.image_settings.file_format='PNG'; s.render.image_settings.color_mode='RGB'
s.render.film_transparent=False; s.render.use_sequencer=False
s.view_settings.view_transform='Standard'; s.view_settings.look='Medium High Contrast'
s.world.use_nodes=True; s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(0,0,0,1)
lights=[]; anim=[]
smooth=C.smooth; lerp=C.vlerp


def empty(name,loc=(0,0,0),parent=None): return C.empty(name,loc,parent)


def material(name,color=(1,1,1),atlas=None,tile=None,emission=1,lit=True,alpha=1):
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial'); em=nt.nodes.new('ShaderNodeEmission')
    em.inputs['Strength'].default_value=emission
    if atlas:
        tex=nt.nodes.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(str(ASSETS/atlas),check_existing=True); tex.interpolation='Closest'
        colorout=tex.outputs['Color']
    else:
        rgb=nt.nodes.new('ShaderNodeRGB'); rgb.outputs[0].default_value=(*color,1); colorout=rgb.outputs[0]
    if lit:
        geo=nt.nodes.new('ShaderNodeNewGeometry'); dot=nt.nodes.new('ShaderNodeVectorMath'); dot.operation='DOT_PRODUCT'; dot.inputs[1].default_value=(.35,-.55,.76)
        nt.links.new(geo.outputs['Normal'],dot.inputs[0])
        scale=nt.nodes.new('ShaderNodeMath'); scale.operation='MULTIPLY_ADD'; scale.inputs[1].default_value=.30; scale.inputs[2].default_value=.72
        nt.links.new(dot.outputs['Value'],scale.inputs[0])
        mul=nt.nodes.new('ShaderNodeMixRGB'); mul.blend_type='MULTIPLY'; mul.inputs[0].default_value=1
        nt.links.new(colorout,mul.inputs[1]); nt.links.new(scale.outputs[0],mul.inputs[2]); colorout=mul.outputs[0]
        lights.append(em.inputs['Strength'])
    nt.links.new(colorout,em.inputs['Color'])
    if alpha<1:
        tr=nt.nodes.new('ShaderNodeBsdfTransparent'); mix=nt.nodes.new('ShaderNodeMixShader'); mix.inputs[0].default_value=alpha
        nt.links.new(tr.outputs[0],mix.inputs[1]); nt.links.new(em.outputs[0],mix.inputs[2]); nt.links.new(mix.outputs[0],out.inputs[0])
    else: nt.links.new(em.outputs[0],out.inputs[0])
    m['tile']=tile or [0,0,1,1]
    return m


def uv_faces(o,tile=None):
    tile=tile or o.data.materials[0].get('tile',[0,0,1,1]); u0,v0,u1,v1=tile
    layer=o.data.uv_layers.get('UVMap') or o.data.uv_layers.new(name='UVMap')
    for p in o.data.polygons:
        for k,li in enumerate(p.loop_indices):
            layer.data[li].uv=[(u0,v0),(u1,v0),(u1,v1),(u0,v1)][k%4]


def box(name,loc,size,mat,parent=None,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o=bpy.context.object; o.name=name; o.parent=parent; o.location=loc; o.scale=size
    bpy.context.view_layer.objects.active=o; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat); uv_faces(o)
    if bevel:
        b=o.modifiers.new('one-cut game bevel','BEVEL'); b.width=bevel; b.segments=1
        bpy.ops.object.modifier_apply(modifier=b.name)
    return o


def mesh(name,v,f,mat,parent=None,uv=None): return C.mesh(name,v,f,mat,uv,parent)


def quad(name,verts,mat,parent=None):
    u0,v0,u1,v1=mat.get('tile',[0,0,1,1])
    return mesh(name,verts,[(0,1,2,3)],mat,parent,[(u0,v0),(u1,v0),(u1,v1),(u0,v1)])


def cylinder(name,loc,radius,depth,mat,parent=None,vertices=10,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth)
    o=bpy.context.object; o.name=name; o.parent=parent; o.location=loc; o.rotation_euler=rot; o.data.materials.append(mat); return o


def beam(name,a,b,width,mat,parent=None,depth=None):
    a,b=Vector(a),Vector(b); o=box(name,(a+b)/2,(width,depth or width,(b-a).length),mat,parent)
    o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler(); return o


def torus(name,loc,major,minor,mat,parent=None,rot=(0,0,0),segments=24):
    bpy.ops.mesh.primitive_torus_add(major_segments=segments,minor_segments=6,major_radius=major,minor_radius=minor)
    o=bpy.context.object; o.name=name; o.parent=parent; o.location=loc; o.rotation_euler=rot; o.data.materials.append(mat); return o


def sphere(name,loc,scale,mat,parent=None,segments=24,rings=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,radius=1)
    o=bpy.context.object; o.name=name; o.parent=parent; o.location=loc; o.scale=scale; o.data.materials.append(mat); return o


def key(o,f): C.transform_key(o,f)


turq=material('town | faded turquoise facade',atlas='cidade_atlas.png',tile=(0,.5,.5,1))
coral=material('town | terracotta facade',atlas='cidade_atlas.png',tile=(.5,.5,1,1))
asphalt=material('town | cracked asphalt',atlas='cidade_atlas.png',tile=(0,0,.5,.5))
paving=material('town | concrete paving',atlas='cidade_atlas.png',tile=(.5,0,1,.5))
shutter=material('shop | rusty metal shutter',atlas='detalhes_atlas.png',tile=(0,.5,.5,1))
shop=material('shop | wooden door and glass',atlas='detalhes_atlas.png',tile=(.5,.5,1,1))
dashboard=material('car | photographed dashboard',atlas='detalhes_atlas.png',tile=(0,0,.5,.5))
hazard=material('town | worn hazard steel',atlas='detalhes_atlas.png',tile=(.5,0,1,.5))
roofmat=material('roof | old clay tiles',(.32,.095,.045))
wood=material('wood | weathered brown',(.23,.12,.055))
steel=material('steel | dull warm gray',(.28,.31,.32))
dark=material('rubber | nearly black',(.025,.032,.035))
cream=material('paint | dirty ivory',(.68,.69,.56))
yellow=material('road | old yellow paint',(.82,.57,.07))
carblue=material('car | pale blue paint',(.23,.43,.48))
red=material('tail light',(.6,.035,.018),lit=False)
glass=material('glass | tinted blue',(.17,.35,.45),lit=False,alpha=.13)
green=material('foliage | dark green',(.07,.24,.09))
green2=material('foliage | sunlit green',(.20,.37,.085))
sand=material('coast | pale sand',(.67,.53,.29))
watermat=material('sea | deep teal',(.025,.23,.35))
foam=material('sea | foam',(.68,.84,.79))
shadow=material('blob shadows',(.015,.017,.018),lit=False,alpha=.32)
lamp=material('lamp | warm amber',(1,.58,.12),lit=False,emission=1.5)
night_stars=[]


def blob(parent,loc,scale):
    v=[(math.cos(i*math.tau/18)*scale[0]+loc[0],math.sin(i*math.tau/18)*scale[1]+loc[1],loc[2])for i in range(18)]
    return mesh('baked-style ground shadow',v,[tuple(range(18))],shadow,parent)


def palm(loc,parent,size=1):
    root=empty('palm tree',loc,parent)
    for i in range(5):
        cylinder('segmented palm trunk',(.045*i,0,(i+.5)*.43*size),.085*size,.46*size,wood,root,8)
    for i in range(7):
        a=math.tau*i/7; d=Vector((math.cos(a),math.sin(a),0)); z=2.12*size
        v=[(.2,0,z),Vector((.2,0,z))+d*.60*size+Vector((0,0,.18*size)),Vector((.2,0,z))+d*1.22*size+Vector((0,0,-.35*size)),Vector((.2,0,z))+d*.66*size+Vector((-d.y,d.x,0))*.15*size]
        mesh('angular palm frond',v,[(0,1,3),(1,2,3)],green2 if i%2 else green,root)
    root.scale=(size,size,size); return root


def building(name,loc,w,d,h,mat,parent):
    box(name, (loc[0],loc[1],h/2), (w,d,h),mat,parent)
    for side in [-1,1]:
        beam('facade corner trim',(loc[0]+side*w*.48,loc[1]-d*.51,.05),(loc[0]+side*w*.48,loc[1]-d*.51,h),.07,cream,parent)
    roofv=[(loc[0]-w*.56,loc[1]-d*.56,h),(loc[0]+w*.56,loc[1]-d*.56,h),(loc[0]+w*.56,loc[1],h+.45),(loc[0]-w*.56,loc[1],h+.45),(loc[0]-w*.56,loc[1]+d*.56,h),(loc[0]+w*.56,loc[1]+d*.56,h)]
    mesh('clay roof',roofv,[(0,1,2,3),(3,2,5,4),(0,3,4),(1,5,2)],roofmat,parent)
    box('concrete front step',(loc[0],loc[1]-d*.56,.10),(w*.95,.33,.20),paving,parent)


street=empty('SET 1 | town street')
for ix in range(-5,6):
    for iy in range(-4,5):
        x,y=ix*4,iy*4
        quad('town ground',[(x-2,y-2,-.07),(x+2,y-2,-.07),(x+2,y+2,-.07),(x-2,y+2,-.07)],paving,street)
for ix in range(-7,8):
    x=ix*2
    quad('asphalt section',[(x-1,-1.9,-.018),(x+1,-1.9,-.018),(x+1,1.9,-.018),(x-1,1.9,-.018)],asphalt,street)
    for side in [-1,1]:
        for iy in range(2):
            y=side*(2.05+iy*.55)
            box('concrete sidewalk',(x,y,.045),(2,.55,.09),paving,street)
        box('curb',(x,side*1.85,.055),(2,.11,.12),cream,street)
    if ix%2==0:
        box('road center dash',(x,0,.004),(.95,.065,.01),yellow,street)
for i,x in enumerate([-11.5,-8.0,-4.7,-1.2,2.3,5.8,9.2,12.4]):
    w=random.uniform(2.8,3.25); h=random.choice([2.7,3.2,4.3])
    building('town house %02d'%i,(x,4.15),w,2.7,h,turq if i%2 else coral,street)
    if i in [2,3,5]:
        quad('shopfront',[(x-.9,2.77,.14),(x+.9,2.77,.14),(x+.9,2.77,1.9),(x-.9,2.77,1.9)],shutter if i%2 else shop,street)
        awn=box('shop fabric awning',(x,2.40,2.03),(2.3,.85,.09),green2 if i%2 else roofmat,street)
        awn.rotation_euler.x=-.10
for x in [-10,-6,7,11]:
    building('near side building',(x,-11.5),2.9,2.1,3.1,coral if x>0 else turq,street)
palms=[palm((x,2.1,.10),street,size=.85)for x in [-9,-3.2,4.7,11.3]]
for x in [-7,0,7]:
    for y in [-2.75,2.4]:
        cylinder('utility pole',(x,y,1.8),.055,3.6,steel,street,8)
        beam('lamp arm',(x,y,3.45),(x,y-.45,3.45),.05,steel,street)
        box('lamp fixture',(x,y-.45,3.40),(.25,.40,.09),dark,street)
        box('lamp glass',(x,y-.45,3.345),(.16,.27,.02),lamp,street)
for x in [-7,0]:
    for y in [-2.75,2.4]:
        pts=[(x+k*.7,y,3.5-.16*math.sin(math.pi*k/10))for k in range(11)]
        for a,b in zip(pts,pts[1:]): beam('overhead power cable',a,b,.012,dark,street)
for x in [-4.1,3.8]:
    box('street bench seat',(x,-2.5,.48),(1.3,.4,.08),wood,street)
    box('street bench back',(x,-2.69,.79),(1.3,.07,.52),wood,street)
    for dx in [-.48,.48]: box('bench leg',(x+dx,-2.5,.24),(.065,.28,.48),steel,street)
trash=[]
for x,y in [(-5,-2.1),(5.8,2.25),(-.8,2.25)]:
    o=cylinder('street refuse bin',(x,y,.36),.22,.72,green,street,10); trash.append(o)
    torus('refuse bin rim',(x,y,.72),.22,.025,steel,street,segments=12)


def make_car(loc,parent=None,name='car'):
    root=empty(name,loc,parent)
    box('car lower body',(0,0,.66),(1.54,3.55,.54),carblue,root,.10)
    box('front hood',(0,-1.22,.97),(1.46,1.02,.11),carblue,root,.05)
    box('rear trunk',(0,1.45,1.0),(1.43,.62,.16),carblue,root,.04)
    box('roof',(0,.30,1.61),(1.25,1.36,.09),carblue,root,.03)
    for side in [-1,1]:
        beam('front windshield pillar',(side*.70,-.74,1.0),(side*.60,-.36,1.59),.055,steel,root)
        beam('rear roof pillar',(side*.60,.96,1.59),(side*.71,1.23,1.03),.075,carblue,root)
        beam('door sill',(side*.78,-.74,.99),(side*.78,1.16,.99),.065,steel,root)
        quad('side window',[(side*.68,-.64,1.02),(side*.60,-.31,1.56),(side*.60,.90,1.56),(side*.69,1.16,1.02)],glass,root)
        box('door handle',(side*.79,.44,.89),(.03,.25,.035),steel,root)
        box('wing mirror',(side*.92,-.65,1.1),(.23,.24,.13),carblue,root,.03)
        box('headlight',(side*.50,-1.79,.80),(.40,.035,.20),cream,root)
        box('tail light',(side*.54,1.79,.8),(.30,.035,.15),red,root)
    box('front bumper',(0,-1.85,.48),(1.56,.13,.14),steel,root)
    box('front grille',(0,-1.8,.76),(.50,.02,.20),dark,root)
    box('license plate',(0,-1.925,.51),(.36,.02,.12),cream,root)
    wheels=[]
    for x in [-.77,.77]:
        for y in [-1.10,1.10]:
            wheels.append(cylinder('tire',(x,y,.39),.35,.22,dark,root,12,(0,math.pi/2,0)))
            cylinder('wheel hub',(x*1.13,y,.39),.19,.025,steel,root,10,(0,math.pi/2,0))
    for x in [-.32,.32]:
        box('seat cushion',(x,.11,.50),(.53,.58,.14),dark,root,.04)
        back=box('seat back',(x,.39,.87),(.53,.15,.69),dark,root,.04); back.rotation_euler.x=-.13
        box('head rest',(x,.42,1.29),(.32,.16,.24),dark,root,.035)
    box('dashboard body',(0,-.60,.97),(1.32,.37,.26),dark,root,.035)
    quad('dashboard photographed instruments',[(-.64,-.39,.92),(.64,-.39,.92),(.64,-.39,1.09),(-.64,-.39,1.09)],dashboard,root)
    torus('steering wheel',(-.32,-.43,1.05),.20,.027,dark,root,(math.pi/2+.15,0,0),24)
    for a in [0,math.tau/3,math.tau*2/3]:
        beam('steering wheel spoke',(-.32,-.43,1.05),(-.32+.18*math.cos(a),-.43,1.05+.18*math.sin(a)),.025,steel,root)
    beam('gear stick',(0,.02,.40),(0,-.06,.76),.027,steel,root)
    sphere('gear knob',(0,-.06,.76),(.055,.055,.055),dark,root,8,4)
    blob(root,(0,0,.014),(.92,1.88))
    return root,wheels


roadcar,roadwheels=make_car((-5,.5,.02),street,'CAR | street braking example'); roadcar.rotation_euler.z=math.pi/2
carset=empty('SET 2 | car cabin',(100,0,0))
interior,insidewheels=make_car((0,0,.02),carset,'CAR | interior hero vehicle')
quad('car set road',[(-12,-16,-.02),(12,-16,-.02),(12,18,-.02),(-12,18,-.02)],asphalt,carset)
for y in range(-14,17,3): box('car set road line',(1.6,y,.004),(.07,1.5,.01),yellow,carset)
for x in [-3.2,3.2]:
    for j in range(6): building('car window passing houses',(x,-10+j*5),2.5,2.5,3.0,turq if j%2 else coral,carset)

# A breakable lamppost, then an identical carried prop parented to the actor.
postbase=empty('POST | fixed foundation',(2,-1.5,0),street)
def pole(root):
    cylinder('steel pole shaft',(0,0,1.65),.052,3.3,steel,root,10)
    beam('curved lamp top',(0,0,3.24),(.46,0,3.40),.052,steel,root)
    box('lamp top housing',(.53,0,3.35),(.36,.20,.12),dark,root,.03)
    box('lamp top glass',(.53,-.005,3.282),(.27,.14,.025),lamp,root)
    box('pole base plate',(0,0,.04),(.23,.23,.08),steel,root)
pole(postbase)
carriedpost=empty('POST | held by Dery',(.05,-.28,0),hero); pole(carriedpost)
for x in [1.83,2.12]: box('cracked foundation',(x,-1.5,.035),(.21,.28,.07),paving,street)

# Wind debris are actual moving meshes, not an overlay on the whole frame.
debris=[]
for i in range(28):
    x,y,z=random.uniform(-9,9),random.uniform(-1.8,2.5),random.uniform(.15,2.7)
    o=box('wind | paper or leaf',(x,y,z),(.10,.16,.005),cream if i%3 else green2,street)
    debris.append((o,x,y,z,random.uniform(.7,1.8)))

# Coastal set, with a genuinely moving mesh crest and a separate shore town.
coast=empty('SET 3 | coast and breaking wave',(200,0,0))
quad('coast sand',[(-10,-13,.01),(10,-13,.01),(10,2,.01),(-10,2,.01)],sand,coast)
quad('ocean base',[(-30,0,-.02),(30,0,-.02),(30,40,-.02),(-30,40,-.02)],watermat,coast)
for i,x in enumerate([-6,-2.2,1.4,5.2]):
    building('shorefront house',(x,-6),2.6,2.8,2.2,coral if i%2 else turq,coast)
coastpalms=[palm((x,-2.5,0),coast,.9)for x in [-7,0,7]]
wave=empty('WAVE | moving curling water',(0,5,0),coast)
wv,wf=[],[]; nx,nz=38,17
for j in range(nz):
    a=(j/(nz-1))*math.pi*.78
    for i in range(nx):
        x=-13+26*i/(nx-1)
        y=-1.8*math.sin(a)
        z=.10+3.7*math.sin(a*.72)+.14*math.sin(x*1.6+a*2)
        wv.append((x,y,z))
for j in range(nz-1):
    for i in range(nx-1):
        a=j*nx+i; wf.extend([(a,a+1,a+nx+1),(a,a+nx+1,a+nx)])
mesh('wave | triangulated curling face',wv,wf,watermat,wave)
foam_points=[]
for i in range(35):
    x=-13+i*26/34
    o=sphere('crest foam',(x,-1.2,3.05+random.uniform(-.1,.2)),(.35,.22,.17),foam,wave,8,4)
    foam_points.append(o)
wash=box('advancing shallow surge',(0,6,.06),(26,8,.10),watermat,coast)
for j in range(12):
    y=2+j*2.4
    beam('sea foam stripe',(-17,y,.025),(17,y,.025),.028,foam,coast)

# Planet diagrams built from geometry. Continents are intentionally stylized.
space=empty('SET 4 | rotating Earth',(300,0,0))
orbitset=empty('SET 5 | Sun and orbit',(400,0,0))
oceanblue=material('Earth | ocean',(.025,.20,.46),lit=False)
land=material('Earth | continents',(.16,.38,.13),lit=False)
ice=material('Earth | polar ice',(.65,.78,.83),lit=False)
equatormat=material('Earth | Equator highlight',(1,.52,.08),lit=False,emission=1.2)
sunmat=material('Sun | pale gold',(1,.57,.08),lit=False,emission=1.4)
earthlights=[]


def planet_lighting(mat):
    nt=mat.node_tree; em=next(n for n in nt.nodes if n.type=='EMISSION')
    old=em.inputs['Color'].links[0].from_socket
    g=nt.nodes.new('ShaderNodeNewGeometry'); dot=nt.nodes.new('ShaderNodeVectorMath'); dot.operation='DOT_PRODUCT'
    vec=nt.nodes.new('ShaderNodeCombineXYZ'); vec.name='SUN DIRECTION'
    vec.inputs[0].default_value=-.65; vec.inputs[1].default_value=-.65; vec.inputs[2].default_value=.35
    nt.links.new(g.outputs['Normal'],dot.inputs[0]); nt.links.new(vec.outputs[0],dot.inputs[1])
    level=nt.nodes.new('ShaderNodeMapRange'); level.clamp=True; level.inputs['From Min'].default_value=-.1; level.inputs['From Max'].default_value=.7
    level.inputs['To Min'].default_value=.08; level.inputs['To Max'].default_value=1
    nt.links.new(dot.outputs['Value'],level.inputs['Value'])
    mul=nt.nodes.new('ShaderNodeMixRGB'); mul.blend_type='MULTIPLY'; mul.inputs[0].default_value=1
    nt.links.new(old,mul.inputs[1]); nt.links.new(level.outputs[0],mul.inputs[2]); nt.links.new(mul.outputs[0],em.inputs['Color'])
    return vec


sun_nodes=[planet_lighting(m) for m in [oceanblue,land,ice]]
continents=[
 [(-168,65),(-130,72),(-55,52),(-80,26),(-100,18),(-120,30),(-155,55)],
 [(-80,10),(-65,11),(-50,5),(-35,-8),(-45,-25),(-60,-55),(-75,-40),(-75,-15)],
 [(-17,37),(10,37),(35,30),(50,12),(43,-15),(25,-35),(12,-30),(-5,5)],
 [(-10,35),(-10,60),(25,72),(90,70),(140,55),(145,30),(105,5),(80,10),(45,20),(35,36)],
 [(112,-10),(138,-12),(154,-28),(145,-40),(120,-32)],
 [(-55,60),(-25,70),(-30,83),(-60,80)]
]
def lonlat(lon,lat,r=1.37):
    a,b=math.radians(lon),math.radians(lat)
    return Vector((r*math.cos(b)*math.sin(a),-r*math.cos(b)*math.cos(a),r*math.sin(b)))


def earth(parent,name,scale=1,equator=False):
    e=empty(name,parent=parent); e.scale=(scale,scale,scale)
    globe=sphere('Earth ocean and land mesh',(0,0,0),(1.35,)*3,oceanblue,e,72,36)
    globe.data.materials.append(land); globe.data.materials.append(ice)
    def inside(x,y,outline):
        hit=False
        for i,(a,b) in enumerate(outline):
            c,d=outline[(i+1)%len(outline)]
            if (b>y)!=(d>y) and x<(c-a)*(y-b)/(d-b)+a: hit=not hit
        return hit
    for p in globe.data.polygons:
        center=sum((globe.data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices)
        lon=math.degrees(math.atan2(center.x,-center.y)); lat=math.degrees(math.asin(center.z/center.length))
        p.material_index=2 if abs(lat)>75 else (1 if any(inside(lon,lat,o)for o in continents)else 0)
    if equator: torus('Equator line',(0,0,0),1.385,.019,equatormat,e,segments=80)
    return e


earth_main=earth(space,'EARTH | initial rotation and Equator',1,True)
marker=empty('Equator marker',parent=earth_main)
sphere('Equator glowing point',(0,-1.43,0),(.07,.07,.07),sunmat,marker,10,6)
beam('Equator marker stem',(0,-1.42,0),(0,-1.85,0),.025,equatormat,marker)
orbit_earth=earth(orbitset,'EARTH | fixed orientation in orbit',.47)
sun=sphere('SUN',(0,0,0),(.70,.70,.70),sunmat,orbitset,32,16)
torus('orbit path',(0,0,0),3.0,.009,cream,orbitset,segments=100)
starsmat=material('space stars',(.6,.70,1),lit=False,emission=1.2)
for base in [space,orbitset]:
    v,f=[],[]
    for i in range(300):
        x,y,z=random.uniform(-15,15),random.uniform(7,18),random.uniform(-12,15)
        r=random.choice([.008,.015,.025]); n=len(v)
        v.extend([(x-r,y,z),(x,y,z+r),(x+r,y,z),(x,y,z-r)]); f.append((n,n+1,n+2,n+3))
    mesh('space | star field',v,f,starsmat,base)

# Large textured sky domes keep the street and coast spatially complete.
sky_mat=material('sky | photographic retro clouds',atlas='ceu_dia.png',lit=False)
skyem=next(n for n in sky_mat.node_tree.nodes if n.type=='EMISSION')
for base in [street,carset,coast]:
    sphere('sky dome',(0,0,0),(45,45,30),sky_mat,base,48,24)
    # Photo texture uses the primitive sphere UVs, rather than a single flat scene image.
    sky=bpy.context.object
    # sphere() preserves primitive UV data; use full texture range.

# Wrist targets for driving and grasping; constraints stay editable in the .blend.
targets={}; iks={}
for side,suffix in [(1,'L'),(-1,'R')]:
    target=empty('IK | wrist '+suffix,(side*.14,-.34,1.38),hero)
    pole_target=empty('IK | elbow '+suffix,(side*.65,-.10,1.02),hero)
    ik=rig.pose.bones['forearm_'+suffix].constraints.new('IK'); ik.name='Grip steering / lamppost'
    ik.target=target; ik.pole_target=pole_target; ik.chain_count=2; ik.influence=0
    ik.pole_angle=side*math.pi/2
    targets[suffix]=target; iks[suffix]=ik

camdata=bpy.data.cameras.new('cinema portrait camera'); cam=bpy.data.objects.new('CAMERA | edited shots',camdata); s.collection.objects.link(cam); s.camera=cam
camdata.clip_start=.025; camdata.clip_end=120; camdata.lens=35
for shot in json.loads((ROOT/'timing.json').read_text())['shots']:
    s.timeline_markers.new(shot['name'],frame=round(shot['start']*FPS)+1)

# Animation is appended below so geometry can be inspected independently.

# A street sun/moon and stars support the months-long lighting illustration.
sun_street=sphere('street | sun',(-10,24,17),(1.2,1.2,1.2),sunmat,street,20,10)
moonmat=material('moon | pale gray',(.55,.64,.74),lit=False,emission=.9)
moon=sphere('street | moon',(9,27,16),(.85,.85,.85),moonmat,street,16,8)
v,f=[],[]
for i in range(160):
    x,y,z=random.uniform(-25,25),random.uniform(27,34),random.uniform(4,21)
    r=random.choice([.015,.025,.035]); n=len(v)
    v.extend([(x-r,y,z),(x,y,z+r),(x+r,y,z),(x,y,z-r)]); f.append((n,n+1,n+2,n+3))
streetstars=mesh('street | night starfield',v,f,starsmat,street)

# Ending fade; no captions or title cards are burned into the picture.
s.use_nodes=True; nodes=s.node_tree.nodes; nodes.clear()
rl=nodes.new('CompositorNodeRLayers'); fade=nodes.new('CompositorNodeMixRGB'); fade.blend_type='MULTIPLY'; fade.inputs[0].default_value=1
comp=nodes.new('CompositorNodeComposite'); s.node_tree.links.new(rl.outputs['Image'],fade.inputs[1]); s.node_tree.links.new(fade.outputs[0],comp.inputs[0])

def camera_at(pos,target,lens):
    cam.location=pos; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler(); camdata.lens=lens

def street_camera(pos,target,lens): camera_at(pos,target,lens)

for f in range(1,END+1):
    t=(f-1)/FPS
    if f%240==1: print('BAKING PERFORMANCE',f,'/',END,flush=True)
    hero.location=(0,-1.25,0); hero.rotation_euler=(0,0,0); hero.scale=(1,1,1)
    C.pose('idle',t)
    exp=''; exw=1
    for ik in iks.values(): ik.influence=0
    for side,suffix in [(1,'L'),(-1,'R')]: targets[suffix].location=(side*.14,-.34,1.38)
    postbase.scale=(1,1,1) if t<32.18 else (0,0,0)
    carriedpost.scale=(0,0,0)
    roadcar.location=(-5+min(t,5)*.9,.5,.02)
    roadcar.rotation_euler=(0,0,math.pi/2)
    for w in roadwheels: w.rotation_euler=(t*3,math.pi/2,0)
    day=1
    if 45.34<=t<48.62: day=1-.94*smooth((t-45.34-.45)/1.9)
    if t>=51.6: day=.53
    for value in lights:
        value.default_value=day; value.keyframe_insert(data_path='default_value',frame=f)
    for mat in [C.bm,C.hm]:
        em=next(n for n in mat.node_tree.nodes if n.type=='EMISSION')
        em.inputs['Strength'].default_value=.4+.6*day
        em.inputs['Strength'].keyframe_insert(data_path='default_value',frame=f)
    skyem.inputs['Strength'].default_value=.035+.88*day
    skyem.inputs['Strength'].keyframe_insert(data_path='default_value',frame=f)
    sun_street.scale=(day,day,day)
    moon.scale=(1-day,)*3
    streetstars.scale=(1,1,1) if day<.25 else (0,0,0)
    # Initial Earth spins, freezes, then the explanatory shot demonstrates the old rotation.
    a=.95*t if t<.55 else .95*.55
    if 6.84<=t<16.3: a=.65+(t-6.84)*.65
    earth_main.rotation_euler=(math.radians(12),0,a)
    marker.scale=(1,1,1) if t>=8.95 else (0,0,0)
    # Orbiting Earth keeps a fixed inertial orientation, instead of facing the Sun.
    orbit_a=(t-40.84)/4.5*math.tau*.65
    orbit_earth.location=(3*math.cos(orbit_a),3*math.sin(orbit_a),0)
    orbit_earth.rotation_euler=(0,0,0)
    sun_dir=-Vector(orbit_earth.location).normalized() if 40.84<=t<45.34 else Vector((-.6,-.7,.4)).normalized()
    for node in sun_nodes:
        for k,val in enumerate(sun_dir):
            node.inputs[k].default_value=val; node.inputs[k].keyframe_insert(data_path='default_value',frame=f)
    # Coast: mesh crest and shallow water advance toward the buildings.
    wu=smooth((t-24.3)/5.5)
    wave.location=(0,8-12*wu,0); wave.scale=(1,1,.65+.6*wu)
    wash.location=(0,8-12*wu,.055); wash.scale=(1,1+wu*.7,1)
    wind=smooth((t-20.8)/2)
    for i,(o,x,y,z,speed) in enumerate(debris):
        if t<20.8:
            o.scale=(0,0,0)
        elif t<24.3:
            o.scale=(1,1,1); o.location=(x+((t-20.8)*speed*2.2)%12-3,y+.1*math.sin(t+i),z+.20*math.sin(t*3+i)); o.rotation_euler=(t*3+i,t*2,i+t)
        else:
            o.scale=(1,1,1); o.location=(x+3,y,.035); o.rotation_euler=(0,0,i)
        key(o,f)
    for i,p in enumerate(palms):
        p.rotation_euler=(.06*wind*math.sin(t*3+i),.33*wind,0); key(p,f)
    # Every branch is a real scene cut, not an image transition.
    if t<1.45:
        hero.location=(0,0,-30)
        camera_at((300+.3,-4.5,1.9),(300,0,0),36)
    elif t<3.44:
        u=(t-1.45)/1.99
        C.pose('walk',t,1.15); hero.location=(-1.2+u*2.5,-1.3,0); hero.rotation_euler=(0,.22*u,.75)
        C.delta('head',(0,0,1),-.55)
        street_camera((hero.location.x+1.3,-4.0,1.6),(hero.location.x,-1.3,1.0),34); exp='susto'
    elif t<5.10:
        u=smooth((t-3.44)/1.66)
        hero.location=(100-.32,-.07,-.38)
        C.pose('carry',t)
        roadcar.location=(-5+u*4,.5,.02)
        for w in roadwheels: w.rotation_euler=(u*16,math.pi/2,0)
        street_camera((1.7,-5.6,2.1),(-2,.4,.85),32)
    elif t<6.84 or 48.62<=t<51.6:
        v=t-5.1 if t<6.84 else t-48.62
        C.pose('carry',v)
        hero.location=(100-.32,-.07,-.38)
        C.delta('thigh_L',(1,0,0),-1.35); C.delta('thigh_R',(1,0,0),-1.35)
        C.delta('shin_L',(1,0,0),1.55); C.delta('shin_R',(1,0,0),1.55)
        C.delta('chest',(1,0,0),.15+.27*math.sin(min(v,1)*math.pi))
        for ik in iks.values(): ik.influence=1
        camera_at((100+.56,-1.02,1.40),(100-.27,-.05,1.18),30)
        exp='susto'
    elif t<8.95:
        hero.location=(0,0,-30)
        camera_at((300+1.1,-4.8,2.0),(300,0,0),34)
    elif t<13.2:
        hero.location=(0,0,-30)
        camera_at((300+.65,-4.2,1.1),(300,0,0),36)
    elif t<16.3:
        hero.location=(0,0,-30)
        camera_at((300+.55,-3.2,.48),(300,0,0),38)
    elif t<18.4:
        u=(t-16.3)/2.1
        C.pose('run',t); hero.location=(-2.8+u*4.2,-1.20,.04); hero.rotation_euler=(0,.18,.90)
        C.delta('head',(0,0,1),-.45)
        roadcar.location=(-3+u*5,.5,.02)
        street_camera((hero.location.x+1.8,-6.2,2.3),(hero.location.x,-.4,1.05),32); exp='panico'
    elif t<20.8:
        u=(t-18.4)/2.4
        C.pose('startled',t-18.4); hero.location=(1.4+u*2.6,-1.20,.15*math.sin(u*math.pi)); hero.rotation_euler=(0,.35,.30)
        street_camera((hero.location.x+.65,-3.5,1.6),(hero.location.x,-1.2,1.22),34); exp='panico'
    elif t<22.5:
        C.pose('startled',t-20.8); hero.location=(.2,-1.3,0); hero.rotation_euler=(.05,.10,0)
        street_camera((5.5,-8.0,3.1),(.5,.5,1.05),30); exp='panico'
    elif t<24.3:
        C.pose('carry',t); hero.location=(.2,-1.3,0)
        C.delta('arm_L',(0,1,0),.20); C.delta('forearm_L',(0,0,1),-1.4)
        C.delta('head',(0,0,1),-.2)
        street_camera((1.15,-3.4,1.70),(.2,-1.3,1.40),38); exp='susto'
    elif t<26.5:
        hero.location=(0,0,-30)
        camera_at((200+8,-13,7),(200,1,1.4),29)
    elif t<29.8:
        hero.location=(0,0,-30)
        u=(t-26.5)/3.3
        camera_at((200+7,-7,3.3),(200,2-4*u,1.4),32)
    elif t<32.18:
        C.pose('idle',t); hero.location=(1.95,-1.22,0)
        for suffix,ik in iks.items():
            ik.influence=smooth((t-29.8)/.55)
            targets[suffix].location=(.05,-.24,1.17 if suffix=='L' else 1.29)
        street_camera((3.0,-3.6,1.8),(1.98,-1.25,1.33),37)
        exp='' if t>30.65 else 'susto'
    elif t<34.64:
        u=smooth((t-32.35)/2.1)
        C.pose('startled',t-32.18); hero.location=lerp((1.95,-1.22,0),(4.4,-1.22,.45),u); hero.rotation_euler=(0,.72*u,0)
        carriedpost.scale=(1,1,1)
        for suffix,ik in iks.items():
            ik.influence=1; targets[suffix].location=(.05,-.24,1.17 if suffix=='L' else 1.29)
        street_camera((6.8,-6.5,2.8),(3.1,-1.2,1.6),29); exp='panico'
    elif t<37.78:
        u=smooth((t-34.64)/3.14)
        C.pose('startled',t-34.64); hero.location=lerp((4.4,-1.22,.45),(5.2,-1.22,.03),u); hero.rotation_euler=(0,.72+.84*u,0)
        carriedpost.scale=(1,1,1)
        for suffix,ik in iks.items():
            ik.influence=1; targets[suffix].location=(.05,-.24,1.17 if suffix=='L' else 1.29)
        street_camera((8,-6,2.3),(6.1,-1.2,.60),31); exp='susto'
    elif t<40.84:
        C.pose('idle_tired',t); hero.location=(5.2,-1.22,.035); hero.rotation_euler=(0,math.pi/2,0)
        street_camera((7.6,-3.5,1.2),(6.8,-1.2,.45),36); exp='derrota'
    elif t<45.34:
        hero.location=(0,0,-30)
        camera_at((400+.2,-8.4,7.2),(400,0,0),31)
    elif t<48.62:
        C.pose('idle_tired',t); hero.location=(.0,-1.25,0)
        C.delta('head',(1,0,0),-.18)
        street_camera((3.0,-7.0,2.5),(0,.8,1.65),29); exp='susto'; exw=.45
    elif t>=51.6:
        C.pose('idle_tired',t); hero.location=(1.95,-1.22,0); hero.rotation_euler=(0,0,.10)
        carriedpost.scale=(1,1,1)
        for suffix,ik in iks.items():
            ik.influence=1; targets[suffix].location=(.05,-.24,1.17 if suffix=='L' else 1.29)
        C.delta('head',(0,0,1),.22)
        u=(t-51.6)/(DURATION-51.6)
        street_camera(lerp((3.4,-3.2,1.9),(2.9,-2.8,1.72),u),(1.95,-1.22,1.38),38); exp='derrota'
    C.expression(exp,f,exw)
    C.key(f)
    for o in [hero,cam,roadcar,carriedpost,postbase,wave,wash,earth_main,marker,orbit_earth,sun_street,moon,streetstars]: key(o,f)
    for suffix,target in targets.items(): key(target,f); iks[suffix].keyframe_insert(data_path='influence',frame=f)
    for w in roadwheels: key(w,f)
    camdata.keyframe_insert(data_path='lens',frame=f)
    gain=1-smooth((t-54.65)/.65)
    fade.inputs[2].default_value=(gain,gain,gain,1); fade.inputs[2].keyframe_insert(data_path='default_value',frame=f)

# No interpolation over camera cuts. Smooth source motion is already sampled at 24 fps.
for db in list(bpy.data.objects)+list(bpy.data.materials)+[camdata,s.node_tree]:
    target=db.node_tree if isinstance(db,bpy.types.Material) and db.use_nodes else db
    if target.animation_data and target.animation_data.action:
        for fc in target.animation_data.action.fcurves:
            for k in fc.keyframe_points: k.interpolation='CONSTANT'
editor=s.sequence_editor_create(); editor.sequences.new_sound('VOZ | original',str(ASSETS/'voz_original.mp3'),1,1)
s.frame_set(1)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Dery_Terra_Parou.blend'))
if args.preview:
    for t in [.35,2.3,4.1,5.8,10.5,17.4,22.0,25.5,28.0,30.8,33.7,36.7,39.3,42.8,47.9,53.3]:
        s.frame_set(round(t*FPS)+1); s.render.filepath=str(OUT/('preview_%04d.png'%round(t*10))); bpy.ops.render.render(write_still=True)
if args.render:
    s.render.filepath=str(FRAMES/'frame_'); bpy.ops.render.render(animation=True)
