"""Five-second format test. Original supplied avatar, deliberately tiny production.

blender -b -t 4 --python build_scene.py
"""
from pathlib import Path
import sys, math, wave, array
import bpy
from mathutils import Vector, Quaternion

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import character as C
import helpers as H

ASSETS = ROOT / 'assets'
OUT = ROOT / 'output'
OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(ASSETS / 'Dery.glb'))
for action in bpy.data.actions:
    action.use_fake_user = True
hero = C.setup(ASSETS)
C.cache_clips()
C.RECORD = H.record
H.ASSETS = ASSETS
s = bpy.context.scene
s.render.engine = 'CYCLES'
s.cycles.device = 'CPU'
s.cycles.samples = 8
s.cycles.use_denoising = False
s.cycles.max_bounces = 2
s.cycles.diffuse_bounces = 1
s.cycles.glossy_bounces = 1
s.cycles.use_adaptive_sampling = True
s.cycles.adaptive_threshold = .12
s.cycles.adaptive_min_samples = 2
s.render.resolution_x, s.render.resolution_y = 360, 640
s.render.resolution_percentage = 100
s.render.fps = 24
s.frame_start, s.frame_end = 1, 120
s.render.image_settings.file_format = 'PNG'
s.render.image_settings.color_mode = 'RGB'
s.render.film_transparent = False
s.render.threads_mode = 'FIXED'
s.render.threads = 4
s.render.use_file_extension = True
s.render.filepath = str(ROOT / 'renders' / 'frame_')
s.world.use_nodes=True
s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.10,.14,.24,1)
s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.11
s.view_settings.view_transform = 'Standard'
s.view_settings.look = 'None'
s.view_settings.exposure = 0
s.view_settings.gamma = 1
s.render.film_transparent = False

M = {}
def mat(name, color, **kwargs):
    M[name] = H.material(name, color, **kwargs)
    return M[name]

wall = mat('paint | midnight blue', (.048, .057, .105))
sidewall = mat('paint | dusty purple', (.115, .067, .15))
black = mat('plastic | charcoal', (.024, .029, .043))
grey = mat('plastic | warm grey', (.28, .27, .32))
wood = mat('desk | walnut', (.25, .13, .075))
cyan = mat('LED | cyan', (.025, .62, .79), lit=False, emission=3.0)
purple = mat('LED | violet', (.38, .09, .68), lit=False, emission=3.0)
white = mat('warm white', (.78, .79, .74))
red = mat('chair | crimson', (.35, .055, .12))
gold = mat('small warm accents', (.73, .38, .075))
screenoff = mat('CRT | tinted glass', (.014, .035, .04))

# Deliberately built from chunky, flat-shaded polygons, with real room depth.
H.box('floor slab', (0, -.15, -.055), (4.3, 4.5, .10), black)
for row in range(14):
    color = (.19 + .013*(row%3), .11 + .007*(row%4), .074)
    board = mat('floor plank %02d' % row, color)
    H.box('wide floorboard', (0, -2.18 + row*.32, -.0125), (4.26, .305, .025), board)
H.box('rear wall', (0, 1.98, 1.46), (4.3, .12, 2.95), wall)
H.box('left wall', (-2.15, -.2, 1.46), (.12, 4.4, 2.95), sidewall)
H.box('right wall', (2.15, -.2, 1.46), (.12, 4.4, 2.95), wall)
H.box('front wall behind the desk', (0,-2.40,1.46),(4.3,.12,2.95),sidewall)
H.box('ceiling', (0,-.2,2.98),(4.3,4.5,.08),wall)
H.box('rear skirting', (0, 1.89, .11), (4.2, .04, .17), black)
H.box('left skirting', (-2.07, -.2, .11), (.04, 4.3, .17), black)
H.box('cyan wall strip', (-2.075, -.2, 2.5), (.025, 4.3, .027), cyan)
H.box('purple wall strip', (0, 1.90, 2.5), (4.15, .025, .027), purple)

def text(name, value, loc, size, material, rotation=(math.pi/2, 0, 0)):
    curve = bpy.data.curves.new(name, 'FONT')
    curve.body = value
    curve.size = size
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    curve.extrude = .001
    o = bpy.data.objects.new(name, curve)
    s.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = rotation
    o.data.materials.append(material)
    return o

H.box('logo backing', (.30, 1.88, 1.95), (1.46, .045, .61), black, bevel=.025)
text('channel sign', 'MASSACOTE', (.30, 1.846, 2.04), .16, white)
text('channel sign small', 'G A M E S', (.30, 1.84, 1.85), .095, cyan)
for ix in range(3):
    for iz in range(2):
        H.box('acoustic foam panel',(-.57+ix*.39,-2.322,1.50+iz*.39),(.31,.045,.31),black,bevel=.025)
        for line in range(3):
            H.box('foam ridges',(-.67+ix*.39+line*.10,-2.285,1.50+iz*.39),(.035,.026,.29),wall)

# Bed and a messy little shelf make this feel like a room rather than a stage.
H.box('bed frame', (-1.45, .3, .28), (1.04, 2.18, .23), black)
H.box('mattress', (-1.45, .3, .45), (1.00, 2.10, .18), grey, bevel=.06)
H.box('purple duvet', (-1.45, -.05, .56), (1.02, 1.42, .12), sidewall, bevel=.03)
for x in [-1.71, -1.35]:
    H.box('duvet pixel stripe', (x, -.05, .625), (.12, 1.4, .014), purple)
H.box('pillow', (-1.45, 1.01, .59), (.75, .36, .19), white, bevel=.07)
H.box('book shelf', (1.43, 1.7, 1.03), (.97, .36, 1.83), black)
for z in [.2, .74, 1.3, 1.88]:
    H.box('shelf board', (1.43, 1.64, z), (.99, .42, .065), wood)
for i, col in enumerate([cyan, red, purple, white, gold, sidewall]):
    H.box('game box %02d' % i, (1.10 + i*.125, 1.62, .98), (.09, .26, .40), col)
    H.box('game spine stripe', (1.10 + i*.125, 1.477, 1.09), (.06, .009, .04), black)
for i in range(3):
    H.box('horizontal game case', (1.43, 1.63, .35+i*.055), (.55, .28, .04), [red, cyan, white][i])
H.box('old console', (1.40, 1.63, 1.43), (.60, .27, .17), grey, bevel=.025)
H.box('console cartridge', (1.4, 1.63, 1.55), (.21, .05, .15), black)

H.box('poster frame', (-1.20, 1.88, 1.80), (.72, .04, 1.03), black)
H.box('pixel art poster',(-1.2,1.85,1.8),(.66,.012,.96),sidewall)
heart=['0110110','1111111','1111111','0111110','0011100','0001000']
for row,line in enumerate(heart):
    for col,pixel in enumerate(line):
        if pixel=='1': H.box('pixel heart',(-1.41+col*.07,1.834,2.05-row*.07),(.066,.012,.066),cyan)

# Desk layout. The monitor faces +Y toward Dery; the avatar faces -Y.
H.box('desk top', (.24, -.69, .77), (1.85, .95, .09), wood, bevel=.025)
for x in [-.60, 1.05]:
    for y in [-1.05, -.31]:
        H.box('desk leg', (x,y,.38), (.075,.075,.75), black)
H.box('keyboard base', (-.03,-.40,.835), (.56,.19,.033), black, bevel=.015)
for row in range(4):
    for col in range(12):
        H.box('chunky keycap', (-.275+col*.045,-.47+row*.043,.859), (.036,.032,.014), grey if row<3 else cyan)
H.box('mouse pad', (.46,-.43,.822), (.35,.29,.012), black)
H.box('mouse', (.46,-.43,.85), (.08,.115,.04), grey, bevel=.02)
H.box('mug', (.85,-.41,.91), (.13,.13,.17), cyan, bevel=.02)
H.torus('mug handle', (.94,-.41,.92), .055,.015,cyan,rot=(math.pi/2,0,0),segments=8)
H.box('PC tower', (.85,-.94,1.05), (.28,.33,.49), black, bevel=.025)
for z in [.94,1.15]:
    H.torus('tower fan LEDs', (.85,-.755,z), .072,.009, purple if z<1 else cyan, rot=(math.pi/2,0,0), segments=12)

H.box('CRT stand', (0,-.94,.87), (.31,.26,.12), grey)
H.box('CRT chassis', (0,-1.02,1.23), (1.03,.40,.79), black, bevel=.04)
H.box('CRT front bevel', (0,-.804,1.25), (.97,.04,.69), grey, bevel=.035)
H.box('CRT screen bezel', (0,-.776,1.26), (.90,.025,.62), screenoff, bevel=.025)
movie = bpy.data.materials.new('monitor | actual moving footage')
movie.use_nodes = True
nt = movie.node_tree
nt.nodes.clear()
tex = nt.nodes.new('ShaderNodeTexImage')
tex.image = bpy.data.images.load(str(ASSETS/'monitor_demo.mp4'))
tex.image_user.frame_duration = 120
tex.image_user.frame_start = 1
tex.image_user.use_auto_refresh = True
tex.interpolation = 'Closest'
em = nt.nodes.new('ShaderNodeEmission')
nt.links.new(tex.outputs['Color'], em.inputs['Color'])
out = nt.nodes.new('ShaderNodeOutputMaterial')
nt.links.new(em.outputs[0], out.inputs['Surface'])
H.mesh('CRT moving picture', [(-.42,-.759,.947),(-.42,-.759,1.577),(.42,-.759,1.577),(.42,-.759,.947)], [(0,1,2,3)], movie,
       uv=[(0,0),(0,1),(1,1),(1,0)])
H.box('power LED', (.40,-.775,.916), (.022,.013,.012), cyan)
for i in range(3):
    H.box('monitor buttons', (.17+i*.06,-.777,.916), (.036,.02,.016), black)

# Cushion surface at .583 m, hips above it and soles on the floor.
H.cylinder('chair pedestal', (0,.10,.24), .055,.35,grey,vertices=8)
H.box('chair seat', (0,.10,.48), (.55,.54,.13), black, bevel=.06)
H.box('seat cushion', (0,.06,.553), (.43,.43,.06), red, bevel=.035)
H.box('chair back', (0,.43,1.04), (.55,.13,.94), black, bevel=.06)
H.box('chair back center', (0,.35,1.07), (.36,.03,.77), red, bevel=.035)
for side in [-1,1]:
    H.beam('chair arm support', (side*.31,.10,.48), (side*.31,.10,.69), .045, black)
    H.box('chair armrest', (side*.31,.03,.72), (.08,.38,.06), black, bevel=.02)
for i in range(5):
    angle=i*math.tau/5
    end=(.34*math.cos(angle),.10+.34*math.sin(angle),.075)
    H.beam('chair five-star base',(0,.10,.105),end,.045,black)
    H.cylinder('caster wheel',(end[0],end[1],.045),.045,.055,black,vertices=8,rot=(math.pi/2,0,angle))

# The head and torso share a jaw/neck boundary. Independent vertex rounding
# separates those matching vertices and makes a visible crack. Keep both meshes
# intact; the PS1 treatment comes from pixel resolution, filtering and palette.
for obj in [C.head,C.body]:
    for poly in obj.data.polygons: poly.use_smooth=True

# A UV-space mouth aperture follows the syllables without moving chin vertices
# or reprojecting another image over the beard.
nt=C.hm.node_tree
emission=next(n for n in nt.nodes if n.type=='EMISSION')
shaded=emission.inputs['Color'].links[0].from_node
source=shaded.inputs[1].links[0].from_socket
uv=nt.nodes.new('ShaderNodeUVMap'); uv.uv_map='FaceProjection'
sep=nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(uv.outputs[0],sep.inputs[0])
amount=nt.nodes.new('ShaderNodeValue'); amount.name='VOICE | mouth envelope'
def mathnode(operation,a,b=None,c=None):
    n=nt.nodes.new('ShaderNodeMath'); n.operation=operation
    for i,v in enumerate([a,b,c]):
        if v is None: continue
        if isinstance(v,(int,float)): n.inputs[i].default_value=v
        else: nt.links.new(v,n.inputs[i])
    return n.outputs[0]
x=mathnode('MULTIPLY_ADD',sep.outputs['X'],.46,-.23)
z=mathnode('MULTIPLY_ADD',sep.outputs['Y'],.46,1.37-1.504)
width=mathnode('DIVIDE',x,.026)
height=mathnode('MULTIPLY_ADD',amount.outputs[0],.010,.002)
y=mathnode('DIVIDE',z,height)
distance=mathnode('ADD',mathnode('MULTIPLY',width,width),mathnode('MULTIPLY',y,y))
aperture=mathnode('MULTIPLY',mathnode('SUBTRACT',1,distance),5)
clamp=nt.nodes.new('ShaderNodeClamp'); nt.links.new(aperture,clamp.inputs[0])
gate=mathnode('GREATER_THAN',amount.outputs[0],.13)
alpha=mathnode('MULTIPLY',clamp.outputs[0],gate)
mix=nt.nodes.new('ShaderNodeMixRGB')
nt.links.new(alpha,mix.inputs[0]); nt.links.new(source,mix.inputs[1]); mix.inputs[2].default_value=(.016,.004,.006,1)
nt.links.new(mix.outputs[0],shaded.inputs[1])

# Replace the old self-lit avatar shader with real light response, keeping every
# source texture and expression connection before the fake lighting multiplier.
for material in [C.bm,C.hm]:
    nodes=material.node_tree.nodes; links=material.node_tree.links
    em=next(n for n in nodes if n.type=='EMISSION')
    fake=em.inputs['Color'].links[0].from_node
    albedo=fake.inputs[1].links[0].from_socket
    shader=nodes.new('ShaderNodeBsdfPrincipled')
    shader.inputs['Roughness'].default_value=.88
    shader.inputs['Specular IOR Level'].default_value=.15
    links.new(albedo,shader.inputs['Base Color'])
    output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL')
    links.new(shader.outputs[0],output.inputs['Surface'])
for poly in C.head.data.polygons: poly.use_smooth=True

def area(name,loc,target,power,color,size):
    data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.color=color; data.shape='DISK'; data.size=size
    o=bpy.data.objects.new(name,data); s.collection.objects.link(o); o.location=loc
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    return o
area('monitor spill | cool cyan',(0,-.69,1.35),(0,.11,1.25),8,(.30,.73,1.0),.70)
area('face key | soft warm light',(.65,-1.25,2.15),(0,.10,1.35),45,(1.0,.78,.60),1.3)
area('cyan side light',(-1.85,-.35,1.85),(0,.12,1.15),40,(.06,.62,1.0),1.6)
area('violet rim light',(1.80,.85,2.05),(0,.10,1.3),65,(.57,.12,1.0),1.2)
area('ceiling soft fill',(0,.10,2.78),(0,0,.6),20,(.38,.44,.75),2.1)
area('back wall violet wash',(.80,1.65,2.4),(.10,1.90,1.5),35,(.48,.07,1.0),1.6)
for material in bpy.data.materials:
    # The area lights provide the spill. Tiny LED keycaps and letters remain
    # visible without becoming dozens of noisy mesh light sources.
    material.cycles.emission_sampling='NONE'
s.use_nodes=True
comp=s.node_tree; comp.nodes.clear()
render=comp.nodes.new('CompositorNodeRLayers')
glare=comp.nodes.new('CompositorNodeGlare'); glare.glare_type='FOG_GLOW'; glare.quality='MEDIUM'; glare.threshold=1.1; glare.size=6; glare.mix=-.88
output=comp.nodes.new('CompositorNodeComposite')
comp.links.new(render.outputs['Image'],glare.inputs['Image']); comp.links.new(glare.outputs['Image'],output.inputs['Image'])

with wave.open(str(ASSETS/'voz_teste.wav')) as audio:
    samples=array.array('h', audio.readframes(audio.getnframes()))
    sr=audio.getframerate()
def energy(t):
    part=samples[max(0,int(t*sr)):int((t+1/24)*sr)]
    rms=math.sqrt(sum((v/32768)**2 for v in part)/max(1,len(part)))
    return min(.92,max(0,(rms-.012)*10))

data=bpy.data.cameras.new('Camera | three cuts')
camera=bpy.data.objects.new('Camera | three cuts',data)
s.collection.objects.link(camera); s.camera=camera
data.sensor_fit='VERTICAL'; data.sensor_height=32
camera.rotation_mode='XYZ'
shots=[(1,22,'01 | quarto e monitor'),(23,43,'02 | detalhe do monitor'),(44,120,'03 | reação do Dery')]
for start,end,name in shots:
    marker=s.timeline_markers.new(name,frame=start); marker.camera=camera

for f in range(1,121):
    t=(f-1)/24
    frozen=t>=3.65
    pt=min(t,3.65)
    C.pose('talk',pt,.64)
    for bone in ['waist','spine','chest','upper_chest','neck_upper']:
        C.delta(bone,(1,0,0),0)
    hero.location=(0,.10,-.17)
    hero.rotation_euler=(0,0,0)
    for suffix in ['L','R']:
        C.delta('thigh_'+suffix,(1,0,0),-1.16)
        C.delta('shin_'+suffix,(1,0,0),1.23)
        C.delta('foot_'+suffix,(1,0,0),-.08)
    # Rest elbows near the chair; only the right arm makes a short palm-up shrug.
    C.delta('arm_L',(0,1,0),1.20)
    C.delta('arm_R',(0,1,0),-1.13)
    C.delta('forearm_L',(1,0,0),-.88)
    C.delta('forearm_R',(1,0,0),-.83)
    gesture=math.sin(max(0,min(1,(pt-1.9)/1.1))*math.pi)*.28
    # Compose the shrug with elbow flexion rather than erasing that flexion.
    forearm=C.rig.pose.bones['forearm_R']
    forearm.rotation_quaternion=forearm.rotation_quaternion @ (C.rest['forearm_R'].inverted() @ Quaternion((0,0,1),-gesture) @ C.rest['forearm_R'])
    # Turns from monitor toward the lens on the second sentence.
    turn=C.smooth((pt-1.55)/.40)
    C.delta('head',(0,0,1),turn*.28)
    C.delta('neck',(1,0,0),-.035+math.sin(pt*5)*.025)
    C.key(f); C.transform_key(hero,f)
    C.expression('derrota',f,.82 if t>3.55 else 0)
    amount.outputs[0].default_value=energy(t) if t<3.9 else 0
    H.record(amount.outputs[0],'default_value',f)
    if f<=22:
        u=(f-1)/21
        loc=Vector((1.65,1.42,1.94)).lerp(Vector((1.49,1.29,1.86)),u)
        target=Vector((-.04,-.40,1.07)); lens=23
    elif f<=43:
        u=(f-23)/20
        loc=Vector((.87,-.05,1.44)).lerp(Vector((.76,-.13,1.42)),u)
        target=Vector((0,-.77,1.24)); lens=25
    else:
        u=(f-44)/76
        loc=Vector((.25,-.64,1.48)).lerp(Vector((.22,-.59,1.47)),min(1,u*.65))
        target=Vector((0,.10,1.32)); lens=28+u*4
        # Tiny camera hitch punctuates the frozen NPC at the end.
        if 91<=f<=94: loc.x+=.012 if f%2 else -.012
    camera.location=loc
    camera.rotation_euler=(target-loc).to_track_quat('-Z','Y').to_euler()
    data.lens=lens
    C.transform_key(camera,f); H.record(data,'lens',f)

H.commit_curves()
s.frame_set(1)
# Keep relative external assets and an editable five-second audio strip.
seq=s.sequence_editor_create()
sound=seq.sequences.new_sound('Voz brasileira | teste', str(ASSETS/'voz_teste.wav'),channel=1,frame_start=1)
sound.volume=1
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Dery_Quarto_Gamer_Teste.blend'))
bpy.ops.file.make_paths_relative()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Dery_Quarto_Gamer_Teste.blend'))
print('PREVIEW_SCENE_READY',flush=True)
if '--skip-stills' not in sys.argv:
    for frame in [12,32,70,108]:
        s.frame_set(frame)
        s.render.filepath=str(OUT/('preview_%04d.png'%frame))
        bpy.ops.render.render(write_still=True)
print('PREVIEW_STILLS_READY',flush=True)
