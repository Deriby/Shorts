import bpy
from mathutils import Vector, Matrix
from pathlib import Path
ROOT=Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT.parents[2]/'assets/personagens/dery/Dery.glb'))
s=bpy.context.scene
rig=bpy.data.objects['Dery_Rig']
rig.animation_data_clear()
for tr in list(rig.animation_data.nla_tracks) if rig.animation_data else []:
    rig.animation_data.nla_tracks.remove(tr)
for p in rig.pose.bones:
    p.matrix_basis=Matrix.Identity(4)
for o in list(s.objects):
    if o.type!='ARMATURE' and not o.name.startswith('Dery_'):
        bpy.data.objects.remove(o,do_unlink=True)
for m in bpy.data.materials:
    if not m.use_nodes: continue
    nt=m.node_tree
    p=next((n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'),None)
    out=next((n for n in nt.nodes if n.type=='OUTPUT_MATERIAL'),None)
    if p and out and p.inputs['Base Color'].is_linked:
        col=p.inputs['Base Color'].links[0].from_socket
        e=nt.nodes.new('ShaderNodeEmission')
        nt.links.new(col,e.inputs['Color'])
        nt.links.new(e.outputs[0],out.inputs['Surface'])
s.render.engine='CYCLES'
s.cycles.samples=4
s.cycles.use_denoising=False
s.render.threads_mode='FIXED'
s.render.threads=3
s.world.color=(.04,.04,.04)
s.view_settings.view_transform='Standard'
s.view_settings.look='None'
camdata=bpy.data.cameras.new('inspect')
cam=bpy.data.objects.new('inspect',camdata)
s.collection.objects.link(cam)
s.camera=cam
camdata.type='ORTHO'
camdata.ortho_scale=.46
cam.location=(0,-3,1.60)
cam.rotation_euler=(Vector((0,0,1.60))-cam.location).to_track_quat('-Z','Y').to_euler()
s.render.resolution_x=s.render.resolution_y=768
s.render.resolution_percentage=100
s.render.film_transparent=True
s.render.image_settings.color_mode='RGBA'
s.render.filepath=str(ROOT/'assets/dery_rosto_frente.png')
bpy.ops.render.render(write_still=True)
cam.location=(.55,-3.5,1.20)
cam.rotation_euler=(Vector((0,0,.9))-cam.location).to_track_quat('-Z','Y').to_euler()
camdata.ortho_scale=2.0
s.render.resolution_x,s.render.resolution_y=432,768
s.render.filepath=str(ROOT/'assets/dery_corpo_referencia.png')
bpy.ops.render.render(write_still=True)
head=bpy.data.objects['Dery_Head']
print('HEAD_BOUNDS',[[min(v.co[i] for v in head.data.vertices),max(v.co[i] for v in head.data.vertices)]for i in range(3)])
print('HEAD_MATRIX',list(head.matrix_world))
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets/dery_base_limpa.blend'))
