"""Reusable four-second Dery bumper. Run with Blender 4.3 in background mode."""
from pathlib import Path
import bpy, math, sys, json
from mathutils import Vector, Matrix, Quaternion

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
SOURCE = REPO / 'shorts/005-gta-postal2/production/output/Dery_GTA_POSTAL2.blend'
sys.path.insert(0, str(REPO / 'shorts/004-crash-apelido/production'))
from ps1_nodes import add_contour_modifier

bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
s = bpy.context.scene
s.frame_set(1)
rig = bpy.data.objects['Dery_Rig']
avatar = bpy.data.objects['DERY | animated character']
# Resolve dependencies before changing the blend file's directory.
for image in bpy.data.images:
    if image.source == 'FILE' and image.filepath:
        image.filepath = bpy.path.abspath(image.filepath)
for obj in list(bpy.data.objects):
    if obj not in (rig, avatar):
        bpy.data.objects.remove(obj, do_unlink=True)
for obj in (rig, avatar):
    obj.animation_data_clear()
    obj.location = (0, 0, 0)
    obj.rotation_euler = (0, 0, 0)
    obj.scale = (1, 1, 1)
    obj.matrix_parent_inverse = Matrix.Identity(4)
rig.parent = None
avatar.parent = rig
for modifier in list(avatar.modifiers):
    if modifier.type != 'ARMATURE':
        avatar.modifiers.remove(modifier)
if avatar.data.shape_keys:
    avatar.data.shape_keys.animation_data_clear()
    for key in avatar.data.shape_keys.key_blocks[1:]:
        key.value = 0
for bone in rig.pose.bones:
    bone.matrix_basis = Matrix.Identity(4)
    bone.rotation_mode = 'QUATERNION'
    for constraint in list(bone.constraints):
        bone.constraints.remove(constraint)
rest = {b.name: b.matrix_local.to_quaternion() for b in rig.data.bones}

def empty(name, parent=None):
    o = bpy.data.objects.new(name, None)
    s.collection.objects.link(o)
    o.parent = parent
    return o

actor = empty('DERY | entrance and comic exit')
rig.parent = actor
payload = empty('M | heavy logo', actor)
titles = empty('BRAND | readable text')

def linear(v):
    return v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4

def material(name, rgb, shaded=False):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    output = nt.nodes.new('ShaderNodeOutputMaterial')
    emit = nt.nodes.new('ShaderNodeEmission')
    emit.inputs['Color'].default_value = tuple(linear(c) for c in rgb) + (1,)
    if shaded:
        geom = nt.nodes.new('ShaderNodeNewGeometry')
        dot = nt.nodes.new('ShaderNodeVectorMath')
        dot.operation = 'DOT_PRODUCT'
        dot.inputs[1].default_value = (.35, -.55, .76)
        nt.links.new(geom.outputs['Normal'], dot.inputs[0])
        level = nt.nodes.new('ShaderNodeMath')
        level.operation = 'MULTIPLY_ADD'
        level.inputs[1].default_value = .60
        level.inputs[2].default_value = .65
        nt.links.new(dot.outputs['Value'], level.inputs[0])
        mix = nt.nodes.new('ShaderNodeMixRGB')
        mix.blend_type = 'MULTIPLY'
        mix.inputs[0].default_value = 1
        mix.inputs[1].default_value = tuple(linear(c) for c in rgb) + (1,)
        nt.links.new(level.outputs[0], mix.inputs[2])
        nt.links.new(mix.outputs[0], emit.inputs['Color'])
    nt.links.new(emit.outputs[0], output.inputs['Surface'])
    return m

yellow = material('Brand yellow', (1, .79, .02))
graphite = material('Graphite | flat shaded 3D', (.24, .25, .26), True)
shadow = material('PS1 contact shadow', (.84, .61, .015))
shadow_outer = material('PS1 outer shadow', (.94, .71, .02))

def mesh(name, vertices, faces, mat, parent=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata(vertices, [], faces)
    me.update()
    obj = bpy.data.objects.new(name, me)
    s.collection.objects.link(obj)
    obj.data.materials.append(mat)
    obj.parent = parent
    return obj

# Extruded silhouette of the approved angular M, not a replacement font glyph.
outline = [(0,0),(0,.80),(.08,.90),(.25,.90),(.50,.55),(.75,.90),(.92,.90),(1,.80),(1,0),(.78,0),(.78,.49),(.54,.22),(.46,.22),(.22,.49),(.22,0)]
n = len(outline)
vertices = [((x-.5)*1.35, y, z*1.03) for y in [-.15,.10] for x,z in outline]
faces = [tuple(range(n-1,-1,-1)), tuple(range(n,2*n))]
faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
logo = mesh('MASSACOTE | extruded M', vertices, faces, graphite, payload)
bevel = logo.modifiers.new('Single segment bevel', 'BEVEL')
bevel.width = .022
bevel.segments = 1
logo.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')

font = bpy.data.fonts.load('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
def text(name, body, width, location):
    curve = bpy.data.curves.new(name, 'FONT')
    curve.body = body
    curve.font = font
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    curve.extrude = .014
    curve.bevel_depth = .003
    curve.bevel_resolution = 0
    obj = bpy.data.objects.new(name, curve)
    s.collection.objects.link(obj)
    obj.data.materials.append(graphite)
    obj.parent = titles
    obj.rotation_euler = (math.pi/2, 0, 0)
    obj.location = location
    bpy.context.view_layer.update()
    obj.scale = (width / obj.dimensions.x,) * 3
    curve.extrude = .030 / obj.scale.x
    curve.bevel_depth = .006 / obj.scale.x
    return obj

text('BRAND | name', 'MASSACOTE GAMES', 1.95, (0,-1.15,.19))
text('BRAND | subscribe', 'inscreva-se', .88, (0,-1.70,.13))

floor = mesh('Endless yellow backdrop', [(-100,-100,-.01),(100,-100,-.01),(100,100,-.01),(-100,100,-.01)], [(0,1,2,3)], yellow)
def ellipse(name, scale, mat, z):
    verts = [(math.cos(i*math.tau/24)*scale[0], math.sin(i*math.tau/24)*scale[1], z) for i in range(24)]
    return mesh(name, verts, [tuple(range(24))], mat)
shadows = [ellipse('PS1 | outer grounding shadow',(.55,.27),shadow_outer,.001), ellipse('PS1 | contact grounding shadow',(.39,.19),shadow,.003)]

camera_data = bpy.data.cameras.new('Portrait camera')
camera = bpy.data.objects.new('Portrait camera', camera_data)
s.collection.objects.link(camera)
camera.location = (.35,-8.5,3.6)
target = Vector((0,-.12,1.28))
camera.rotation_euler = (target-camera.location).to_track_quat('-Z','Y').to_euler()
camera_data.lens = 59
camera_data.sensor_fit = 'VERTICAL'
camera_data.sensor_height = 32
s.camera = camera
add_contour_modifier(avatar, camera, width=216, height=384, aspect=9/16)

wrists = {}
for side, sign in [('L',1),('R',-1)]:
    wrist = empty('GRIP | '+side, actor)
    pole = empty('ELBOW | '+side, actor)
    pole.location = (sign*.75, .05, 1.22)
    ik = rig.pose.bones['forearm_'+side].constraints.new('IK')
    ik.name = 'Carry the M with a stable grip'
    ik.target = wrist
    ik.pole_target = pole
    ik.chain_count = 2
    ik.use_stretch = False
    arm = rig.data.bones['arm_'+side]
    fore = rig.data.bones['forearm_'+side]
    axis = fore.tail_local-arm.head_local
    plane = axis.cross(Vector(pole.location)-arm.head_local)
    projected = plane.cross(arm.tail_local-arm.head_local).normalized()
    ik.pole_angle = arm.x_axis.angle(projected)
    if arm.x_axis.cross(projected).dot(arm.tail_local-arm.head_local) < 0:
        ik.pole_angle *= -1
    wrist.rotation_mode = 'QUATERNION'
    wrist.rotation_quaternion = Vector((0,0,1)).to_track_quat('Y','Z')
    c = rig.pose.bones['hand_'+side].constraints.new('COPY_ROTATION')
    c.target = wrist
    c.owner_space = 'WORLD'
    c.target_space = 'WORLD'
    wrists[side] = wrist

def delta(name, axis, angle):
    rig.pose.bones[name].rotation_quaternion = rest[name].inverted() @ Quaternion(axis,angle) @ rest[name]
def smooth(u):
    u = max(0,min(1,u))
    return u*u*(3-2*u)
def key(obj, prop, f):
    obj.keyframe_insert(data_path=prop, frame=f)

face_cues = []
for f in range(1,97):
    t=(f-1)/24
    enter=smooth((t-.08)/.70)
    leave=max(0,(t-2.38)/.90)
    x=-3.8*(1-enter)+5.8*leave**2
    walking=t<.87
    falling=t>=2.24
    phase=t*math.tau*2.8
    amount=.29 if walking else .64 if falling else .018
    bob=.025*abs(math.sin(phase)) if walking else .012*math.sin(t*7)
    actor.location=(x,0,bob+(.15*smooth((t-2.45)/.25) if falling else 0))
    tilt=.04*math.sin(phase) if walking else -.035
    tilt += .83*smooth((t-2.28)/.70)
    actor.rotation_euler=(0,tilt,0)
    payload.rotation_euler=(0,.035*math.sin(t*10)+.12*smooth((t-2.12)/.35),0)
    payload.location=(0,0,1.78-.045*smooth((t-2.10)/.35))
    payload.scale=(1,1,1)
    for side,sign in [('L',1),('R',-1)]:
        delta('thigh_'+side,(1,0,0),sign*amount*math.sin(phase))
        delta('shin_'+side,(1,0,0),max(0,-sign*math.sin(phase))*amount*1.5)
        delta('foot_'+side,(1,0,0),-sign*amount*.35*math.sin(phase))
        wrist=wrists[side]
        grip=Vector((sign*.425,-.075,1.635-1.78))
        grip=payload.rotation_euler.to_matrix()@grip+payload.location
        wrist.location=grip
        key(wrist,'location',f)
    delta('upper_chest',(1,0,0),-.065 if t<1.2 else -.025)
    delta('head',(0,0,1),-.09 if t<1.05 else .12 if t<2.2 else -.12)
    delta('head',(1,0,0),.05 if t<1.1 else -.05 if t<2.15 else -.13)
    face=25 if t<.88 else 13 if t<1.83 else 10 if t<1.95 else 5 if t<2.48 else 21
    avatar['PS1_face_id']=face
    key(avatar,'["PS1_face_id"]',f)
    if not face_cues or face_cues[-1]['id'] != face:
        face_cues.append({'frame':f,'id':face})
    titles.location=(x,0,0)
    titles.rotation_euler=(0,0,0)
    for sh in shadows:
        sh.location=(x,.02,0)
        sh.scale=(1+.2*smooth((t-2.1)/.5),1,1)
        key(sh,'location',f)
        key(sh,'scale',f)
    for obj in (actor,payload,titles):
        key(obj,'location',f)
        key(obj,'rotation_euler',f)
    for bone in rig.pose.bones:
        key(bone,'rotation_quaternion',f)

for obj in list(bpy.data.objects):
    if obj.animation_data and obj.animation_data.action:
        for curve in obj.animation_data.action.fcurves:
            for point in curve.keyframe_points:
                point.interpolation='CONSTANT' if obj==avatar else 'LINEAR'

s.render.engine='CYCLES'
s.cycles.device='CPU'
s.cycles.samples=1
s.cycles.use_denoising=False
s.cycles.use_adaptive_sampling=False
s.render.threads_mode='FIXED'
s.render.threads=4
s.render.resolution_x=432
s.render.resolution_y=768
s.render.resolution_percentage=100
s.render.fps=24
s.frame_start=1
s.frame_end=96
s.render.image_settings.file_format='PNG'
s.render.image_settings.color_mode='RGB'
s.render.image_settings.compression=15
s.render.film_transparent=False
s.render.dither_intensity=0
s.render.use_compositing=False
s.render.use_sequencer=False
s.sequence_editor_clear()
if s.node_tree:
    s.node_tree.nodes.clear()
s.view_settings.view_transform='Standard'
s.view_settings.look='None'
s.view_settings.exposure=0
s.view_settings.gamma=1
s.world=bpy.data.worlds.new('Unbroken yellow background')
s.world.use_nodes=True
s.world.node_tree.nodes['Background'].inputs['Color'].default_value=tuple(linear(c) for c in (1,.79,.02))+(1,)
s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=1
for marker in list(s.timeline_markers):
    s.timeline_markers.remove(marker)
for f,name in [(1,'EMPTY / entrance'),(22,'PROUD'),(47,'SHOCK'),(56,'LOSS OF BALANCE'),(81,'EMPTY / exit')]:
    s.timeline_markers.new(name,frame=f)
(HERE/'output').mkdir(exist_ok=True)
(HERE/'renders').mkdir(exist_ok=True)
(HERE/'face_cues.json').write_text(json.dumps(face_cues,indent=2))
s.frame_set(34)
s.render.filepath='//../renders/frame_'
bpy.data.orphans_purge(do_recursive=True)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'output/Massacote_Outro_Dery_4s.blend'),compress=True)
if '--render-all' in sys.argv:
    bpy.ops.render.render(animation=True)
else:
    for f in [1,20,34,53,65,88]:
        s.frame_set(f)
        s.render.filepath=str(HERE/f'output/preview_{f:04d}.png')
        bpy.ops.render.render(write_still=True)
print('OUTRO_READY',flush=True)
