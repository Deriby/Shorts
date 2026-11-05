"""Create the reusable black-shirt Dery asset and a real Blender preview."""
from pathlib import Path
import bpy,sys,math,json
from mathutils import Vector,Quaternion,Matrix
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[4]
sys.path[:0]=[str(HERE),str(REPO/'assets/personagens/dery')]
from aplicar import aplicar
from ps1_precision import add_safe_precision
source=REPO/'shorts/006-mizzurna-falls/production/output/Dery_Mizzurna_Falls.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
s.frame_set(123);r=bpy.data.objects['Dery_Rig'];a=bpy.data.objects['DERY | animated character']
for image in bpy.data.images:
    if image.source=='FILE'and image.filepath:image.filepath=bpy.path.abspath(image.filepath)
original=[v.co.copy()for v in a.data.vertices]
count=aplicar(a)
# Keep a self-contained model, the reviewed face system and the original rig.
for obj in list(bpy.data.objects):
    if obj not in (a,r):bpy.data.objects.remove(obj,do_unlink=True)
r.parent=None;r.matrix_parent_inverse=Matrix.Identity(4);r.location=(0,0,0);r.rotation_euler=(0,0,0);r.scale=(1,1,1)
r.animation_data_clear();a.animation_data_clear();a.parent=r;a.matrix_parent_inverse=Matrix.Identity(4);a.location=(0,0,0);a.rotation_euler=(0,0,0)
for p in r.pose.bones:
    p.matrix_basis=Matrix.Identity(4)
    for c in list(p.constraints):p.constraints.remove(c)
rest={b.name:b.matrix_local.to_quaternion()for b in r.data.bones}
for side,sign in [('L',1),('R',-1)]:
    for name,axis,angle in [('arm_'+side,(0,1,0),sign*.93),('forearm_'+side,(0,0,1),sign*.16)]:
        r.pose.bones[name].rotation_quaternion=rest[name].inverted()@Quaternion(axis,angle)@rest[name]
a['PS1_face_id']=2
for mod in list(a.modifiers):
    if mod.type=='NODES':a.modifiers.remove(mod)
cd=bpy.data.cameras.new('Preview camera');cam=bpy.data.objects.new('Preview camera',cd);s.collection.objects.link(cam)
cam.location=(1.05,-3.40,1.92);target=Vector((0,0,1.27));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=65;cd.sensor_fit='VERTICAL';cd.sensor_height=32;s.camera=cam
add_safe_precision(a,cam,width=270,height=480,aspect=9/16)
s.sequence_editor_clear();s.render.use_sequencer=False;s.render.use_compositing=False
if s.node_tree:s.node_tree.nodes.clear()
s.world=bpy.data.worlds.new('Wardrobe preview background');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.10,.10,.12,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8
s.render.resolution_x=720;s.render.resolution_y=1280;s.render.resolution_percentage=100;s.render.fps=24;s.frame_start=1;s.frame_end=1
s.render.engine='CYCLES';s.cycles.samples=2;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=4;s.render.dither_intensity=0;s.view_settings.view_transform='Standard';s.view_settings.look='None'
geometry_error=max(((v.co-old).length for v,old in zip(a.data.vertices,original)),default=0)
assert geometry_error==0,geometry_error
report={'garment_faces':count,'geometry_changed':False,'max_vertex_displacement_m':geometry_error,'shirt_material':'Plain neutral black, no stripes or logo','fit':'Original garment shape, body proportions and sleeves preserved','face':'Original 31 PNG expression system and seam-safe precision retained','source':'Original model and textures preserved unchanged'}
(HERE/'modelo.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
bpy.data.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();s.render.filepath='//previa.png'
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'Dery_Camiseta_Preta.blend'),compress=True)
s.render.filepath=str(HERE/'previa.png');bpy.ops.render.render(write_still=True)
print('BLACK_SHIRT_READY',json.dumps(report),flush=True)
