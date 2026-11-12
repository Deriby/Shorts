"""Install the new atlas on the original rig and create true model previews."""
from pathlib import Path
import hashlib,json,sys
import bpy,numpy as np
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[4]
sys.path[:0]=[str(ROOT),str(ROOT.parents[1])]
from setup_faces131 import install,set_face
from ps1_precision import add_safe_precision

SOURCE=REPO/'assets/personagens/dery/roupas/camiseta_preta/Dery_Camiseta_Preta.blend'
OUT=Path('/workspace/attachments/dery100')
OUT.mkdir(parents=True,exist_ok=True)
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
mode=args[0] if args else 'build'

def snapshot(a):
    return dict(positions=np.array([tuple(v.co) for v in a.data.vertices],dtype=np.float32),
                uvs={u.name:np.array([tuple(p.uv) for p in u.data],dtype=np.float32) for u in a.data.uv_layers},
                polygon_materials=[p.material_index for p in a.data.polygons],
                rig=[(p.name,tuple(v for row in p.matrix_basis for v in row)) for p in a.parent.pose.bones])

def unchanged(a,b):
    return bool(np.array_equal(a['positions'],b['positions']) and a['uvs'].keys()==b['uvs'].keys()
                and all(np.array_equal(a['uvs'][n],b['uvs'][n]) for n in a['uvs'])
                and a['polygon_materials']==b['polygon_materials'] and a['rig']==b['rig'])

def camera_setup(s,a):
    cam=s.camera
    cam.name='DERY | expression preview'
    cam.location=(0,-.8,1.59);target=Vector((0,-.025,1.565))
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.type='PERSP';cam.data.lens=72
    cam.data.sensor_fit='VERTICAL';cam.data.sensor_height=38.4
    for mod in list(a.modifiers):
        if mod.type=='NODES':a.modifiers.remove(mod)
    # A stationary close-up checks the painted features without distortions
    # introduced by a camera-grid modifier intended for a different camera.
    # Productions keep using seam-safe ps1_precision.py with their own camera.
    s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=1
    s.render.resolution_x=240;s.render.resolution_y=256;s.render.resolution_percentage=100
    s.render.threads_mode='FIXED';s.render.threads=4
    s.render.image_settings.file_format='PNG';s.render.dither_intensity=0
    s.render.film_transparent=False;s.render.use_compositing=False;s.render.use_sequencer=False
    s.view_settings.view_transform='Standard';s.view_settings.look='None'
    s.world.color=(.035,.035,.045)

if mode=='build':
    before_sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    s=bpy.context.scene;a=bpy.data.objects['DERY | animated character']
    for image in bpy.data.images:
        if image.source=='FILE' and image.filepath:image.filepath=bpy.path.abspath(image.filepath)
    before=snapshot(a);oldmat=a.data.materials[1]
    camera_setup(s,a)
    # Same camera, original material: baseline for visual and pixel regression.
    set_face(a,2);s.render.filepath=str(OUT/'original_002.png');bpy.ops.render.render(write_still=True)
    install(a)
    assert unchanged(before,snapshot(a)), 'Original geometry, UVs or rig changed'
    for face in [2,31,32,33,56,57,58,106,107,109,117,130]:
        set_face(a,face);s.render.filepath=str(OUT/f'check_{face:03d}.png');bpy.ops.render.render(write_still=True)
    set_face(a,31)
    # Save a reusable unanimated original character; media are incorporated.
    add_safe_precision(a,s.camera,width=240,height=256,aspect=240/256)
    s.frame_start=s.frame_end=1;s.frame_set(1)
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Dery_131_Expressoes_PS1.blend'),compress=True)
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==before_sha
    report=dict(original_model=str(SOURCE.relative_to(REPO)),original_sha256=before_sha,
                geometry_uvs_rig_unchanged=True,original_file_unchanged=True,
                original_ids_preserved=list(range(31)),new_ids=[31,130],
                total=131,new=100,speech=50,reactions=25,caricatures=25,
                texture_size=[128,128],atlas_size=[2048,1152],sampling='Closest',
                swap_interpolation='CONSTANT',preview='Actual original mesh and shader; stationary camera')
    (ROOT/'validacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('DERY131_BUILT',flush=True)
elif mode=='all':
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Dery_131_Expressoes_PS1.blend'))
    s=bpy.context.scene;a=bpy.data.objects['DERY | animated character']
    camera_setup(s,a)
    for face in range(31,131):
        set_face(a,face);path=OUT/f'model_{face:03d}.png'
        if not path.exists():
            s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
        print('FACE_RENDERED',face,flush=True)
elif mode=='angles':
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Dery_131_Expressoes_PS1.blend'))
    s=bpy.context.scene;a=bpy.data.objects['DERY | animated character']
    camera_setup(s,a)
    for face in [32,58,107,130]:
        set_face(a,face)
        for name,loc in [('tres_quartos',(.47,-.8,1.59)),('perfil',(.8,-.1,1.59))]:
            s.camera.location=loc
            s.camera.rotation_euler=(Vector((0,-.025,1.565))-s.camera.location).to_track_quat('-Z','Y').to_euler()
            s.render.filepath=str(OUT/f'{name}_{face:03d}.png');bpy.ops.render.render(write_still=True)
