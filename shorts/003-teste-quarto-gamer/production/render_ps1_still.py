"""Render ONE actual Blender frame to review PS1 screen-space vertex precision.

blender -b -t 4 --python shorts/003-teste-quarto-gamer/production/render_ps1_still.py

The approved animation and MP4 are not rebuilt or overwritten by this study.
"""
from pathlib import Path
import math
import subprocess
import bpy
import bmesh
from mathutils import Vector

CONFIG = globals().get('STILL_CONFIG', {})
ROOT = Path(CONFIG.get('project_root', Path(__file__).resolve().parent))
FRAME = CONFIG.get('frame', 108)
WIDTH, HEIGHT = CONFIG.get('resolution', (360, 640))
VERTEX_WIDTH, VERTEX_HEIGHT = CONFIG.get('vertex_grid', (180, 320))
TEXTURE_GRID = CONFIG.get('texture_grid', 512)
OUTPUT = Path(CONFIG.get('output', ROOT / 'output' / 'Dery_PS1_Bordas.png'))
OUTPUT_WIDTH, OUTPUT_HEIGHT = CONFIG.get('output_resolution', (1080, 1920))
RAW = ROOT / 'renders' / 'estudo_ps1' / 'frame.png'
RAW.parent.mkdir(parents=True, exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=str(CONFIG.get('base_blend', ROOT / 'output' / 'Dery_Quarto_Gamer_Teste.blend')))
scene = bpy.context.scene
scene.frame_set(FRAME)
if CONFIG.get('prepare_scene'):
    CONFIG['prepare_scene'](scene)
depsgraph = bpy.context.evaluated_depsgraph_get()

# Freeze only this pose. Join and weld the shared neck seam before quantizing,
# so head and torso cannot drift apart as in the earlier object-space effect.
parts = [bpy.data.objects[name] for name in ('Dery_Body', 'Dery_Head')]
for obj in parts:
    mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(depsgraph),
        preserve_all_data_layers=True, depsgraph=depsgraph)
    source_normals=[tuple(n.vector) for n in mesh.corner_normals]
    saved_normals=mesh.attributes.new(name='PS1SourceNormal',type='FLOAT_VECTOR',domain='CORNER')
    for item,normal in zip(saved_normals.data,source_normals):
        item.vector=normal
    transform = obj.matrix_world.copy()
    obj.parent = None
    obj.matrix_world = transform
    obj.modifiers.clear()
    obj.data = mesh
    obj.animation_data_clear()

bpy.ops.object.select_all(action='DESELECT')
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
avatar = parts[0]
avatar.name = 'DERY | PS1 still study'
mesh = avatar.data
bm = bmesh.new()
bm.from_mesh(mesh)
count_before = len(bm.verts)
neck = [v for v in bm.verts if 1.40 < v.co.z < 1.55]
bmesh.ops.remove_doubles(bm, verts=neck, dist=0.000002)
bm.to_mesh(mesh)
bm.free()
mesh.update()
print('WELDED_NECK_VERTICES', count_before-len(mesh.vertices), flush=True)

# Preserve the pre-snap lighting normals: collapsing tiny triangles onto the
# pixel grid must not create black cracks or noisy lighting on the face.
normals = [tuple(item.vector) for item in mesh.attributes['PS1SourceNormal'].data]
camera = scene.camera
camera.data.dof.use_dof = False
scene.render.resolution_x, scene.render.resolution_y = WIDTH, HEIGHT
scene.render.resolution_percentage = 100
projection = camera.calc_matrix_camera(depsgraph, x=WIDTH, y=HEIGHT,
    scale_x=1.0, scale_y=1.0)
clip_from_local = projection @ camera.matrix_world.inverted() @ avatar.matrix_world
local_from_clip = clip_from_local.inverted()
max_pixel_shift = 0.0
snapped_vertices = 0
vertex_normals=[v.normal.copy() for v in mesh.vertices]
world_matrix=avatar.matrix_world.copy()
normal_matrix=world_matrix.to_3x3()
camera_position=camera.matrix_world.translation.copy()
for vertex in mesh.vertices:
    clip = clip_from_local @ Vector((*vertex.co, 1.0))
    if clip.w <= 0:
        continue
    px = (clip.x/clip.w*.5+.5)*VERTEX_WIDTH
    py = (clip.y/clip.w*.5+.5)*VERTEX_HEIGHT
    sx, sy = math.floor(px+.5), math.floor(py+.5)
    # Concentrate this style study on the silhouette. The full-console integer
    # projection also distorts tiny facial triangles on this much denser avatar.
    world=world_matrix@vertex.co
    view=(camera_position-world).normalized()
    normal=(normal_matrix@vertex_normals[vertex.index]).normalized()
    facing=abs(normal.dot(view))
    strength=max(0,min(1,(.60-facing)/.30))
    if strength==0:
        continue
    snapped_vertices+=1
    max_pixel_shift = max(max_pixel_shift, abs(sx-px), abs(sy-py))
    snapped = Vector(((sx/VERTEX_WIDTH*2-1)*clip.w,
                      (sy/VERTEX_HEIGHT*2-1)*clip.w, clip.z, clip.w))
    local = local_from_clip @ snapped
    vertex.co = vertex.co.lerp(local.xyz/local.w,strength)
mesh.update()
mesh.normals_split_custom_set(normals)
print('SCREEN_GRID', VERTEX_WIDTH, VERTEX_HEIGHT,
    'MAX_SHIFT_VIRTUAL_PX', round(max_pixel_shift, 4),
    'CONTOUR_VERTICES',snapped_vertices,flush=True)

# Quantize texture sampling coordinates instead of blurring/downsampling an
# already rendered face. The original texture files and their UVs stay intact.
for material in mesh.materials:
    if not material or not material.use_nodes:
        continue
    nt = material.node_tree
    for tex in list(nt.nodes):
        if tex.type != 'TEX_IMAGE' or not tex.image:
            continue
        tex.interpolation = 'Closest'
        if not tex.inputs['Vector'].is_linked:
            continue
        source = tex.inputs['Vector'].links[0].from_socket
        snap = nt.nodes.new('ShaderNodeVectorMath')
        snap.operation = 'SNAP'
        snap.label = 'PS1 texture texels'
        snap.inputs[1].default_value = (1/TEXTURE_GRID, 1/TEXTURE_GRID, 1)
        center = nt.nodes.new('ShaderNodeVectorMath')
        center.operation = 'ADD'
        center.inputs[1].default_value = (.5/TEXTURE_GRID, .5/TEXTURE_GRID, 0)
        nt.links.new(source, snap.inputs[0])
        nt.links.new(snap.outputs['Vector'], center.inputs[0])
        nt.links.new(center.outputs['Vector'], tex.inputs['Vector'])

# Hard pixel coverage, without the old spatial smoothing or bloom. The real
# cyan/violet lights and the corrected seating pose are read from the base scene.
scene.render.engine = 'CYCLES'
scene.cycles.samples = CONFIG.get('samples', 64)
scene.cycles.adaptive_min_samples = 16
scene.cycles.adaptive_threshold = .035
scene.cycles.use_denoising = False
scene.cycles.pixel_filter_type = 'BOX'
scene.cycles.filter_width = .01
scene.render.use_motion_blur = False
scene.render.threads_mode = 'FIXED'
scene.render.threads = 4
scene.use_nodes = False
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.render.filepath = str(RAW)
bpy.ops.render.render(write_still=True)

# One image only. No low-resolution resampling pass: enlarge this render
# exactly three times, with ordered RGB555 color dithering at its native pixels.
bayer = '-3+4*mod(X,2)+6*mod(Y,2)-8*mod(X,2)*mod(Y,2)'
channels = ':'.join(f"{c}='clip(floor(({c}(X,Y)+({bayer}))/8)*8,0,255)'" for c in 'rgb')
filters = 'format=gbrp,geq='+channels+f',scale={OUTPUT_WIDTH}:{OUTPUT_HEIGHT}:flags=neighbor'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(RAW),
    '-vf',filters,'-frames:v','1',str(OUTPUT)], check=True)
print('SINGLE_IMAGE_READY', OUTPUT, flush=True)
