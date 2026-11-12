"""Check the actual saved test rig, camera, faces, seating and external media."""
from pathlib import Path
import bpy,json,hashlib,math

P=Path(__file__).resolve().parent;REPO=P.parents[3]
bpy.ops.wm.open_mainfile(filepath=str(P/'Dery_No_Quarto_Teste_6s.blend'))
s=bpy.context.scene;a=bpy.data.objects['DERY | animated character'];r=bpy.data.objects['Dery_Rig']
cam=bpy.data.objects[s['Demo | câmera']]
group=a.modifiers['PS1 | personagem sem fissuras'].node_group
assert any(n.type=='OBJECT_INFO'and n.inputs['Object'].default_value==cam for n in group.nodes)
for o in s.objects:
    if o.type!='MESH':continue
    mod=o.modifiers.get('PS1 | bordas por câmera')
    if mod:assert mod.node_group==group
movie=next(i for i in bpy.data.images if i.source=='MOVIE')
assert Path(bpy.path.abspath(movie.filepath)).is_file()
screen=bpy.data.objects['Tela do PC | substituir por vídeo']
tex=next(n for n in screen.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE')
assert tex.image_user.use_auto_refresh and tex.image_user.frame_duration==96
assert screen.data.materials[0]!=bpy.data.objects['M na parede'].data.materials[0]
for fc in a.animation_data.action.fcurves:
    if 'PS1_face_id'in fc.data_path:assert all(k.interpolation=='CONSTANT'for k in fc.keyframe_points)
samples=[]
for frame in (1,18,30,44,61,80,96):
    s.frame_set(frame);bpy.context.view_layer.update()
    value=a.data.materials[1].node_tree.nodes['PS1 | face ID'].outputs[0].default_value
    assert abs(value-a['PS1_face_id'])<.01
    evaluated=r.evaluated_get(bpy.context.evaluated_depsgraph_get());errors={}
    for side in ('L','R'):
        actual=r.matrix_world@evaluated.pose.bones['forearm_'+side].tail
        target=bpy.data.objects['TESTE | punho '+side].location
        errors[side]=(actual-target).length
        assert errors[side]<.018,(frame,side,errors[side])
    samples.append({'frame':frame,'face':int(a['PS1_face_id']),'lens':cam.data.lens,'wrist_error_m':errors})
source=json.loads((P/'cena.json').read_text())
for ref,digest in source['source_hashes'].items():assert hashlib.sha256((REPO/ref).read_bytes()).hexdigest()==digest
out={'saved_scene_reopened':True,'camera_precision_uses_animated_camera':True,'pc_video_resolves':True,'pc_video_auto_refresh':True,'faces_constant_and_native_driver_checked':True,'original_sources_unchanged':True,'physical_feet_min_z_sample_m':source['actor_min_z_sample'],'samples':samples}
(P/'validacao_cena.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('TEST_VALIDATED',len(samples),'samples',flush=True)
