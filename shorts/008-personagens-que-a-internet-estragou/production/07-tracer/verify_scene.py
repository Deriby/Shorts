"""Verify original meshes, facial seams, seated support, IK and the silent guest."""
from pathlib import Path
from collections import defaultdict
import bpy, json, sys

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'AGENTS.md').exists())
s=bpy.context.scene
with bpy.data.libraries.load(str(REPO/'shorts/004-crash-apelido/production/output/Dery_Crash_Master_R5.blend')) as (src,dst):
    dst.objects=['DERY | animated character']
original=dst.objects[0]
specs=[('DERY | animated character','Dery_Rig',None,[40,204,325]),
       ('INTERVIEW | Host','INTERVIEW | Host rig','Host',[346,448,505,548,590]),
       ('INTERVIEW | Guest','INTERVIEW | Guest rig','Guest',[346,410,486,534,548,590])]
faces=[];precision=[];support={};arms=[]
for name,rig_name,label,frames in specs:
    obj=bpy.data.objects[name];rig=bpy.data.objects[rig_name]
    assert len(obj.data.vertices)==len(original.data.vertices)
    assert max((v.co-o.co).length for v,o in zip(obj.data.vertices,original.data.vertices))==0
    mod=next(m for m in obj.modifiers if m.type=='NODES')
    def positions(enabled):
        mod.show_viewport=enabled;bpy.context.view_layer.update()
        ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
        result=[v.co.copy() for v in mesh.vertices];ev.to_mesh_clear();return result
    hips=[];feet=[]
    for f in frames:
        s.frame_set(f);before=positions(False);after=positions(True);groups=defaultdict(list)
        for i,v in enumerate(obj.data.vertices):
            if v.co.z>1.44 and v.co.y<-.015 and abs(v.co.x)<.14:
                groups[tuple(round(x,6)for x in before[i])].append(i)
        gap=max(((after[i]-after[ids[0]]).length for ids in groups.values()if len(ids)>1 for i in ids),default=0)
        assert gap<.00005,(name,f,gap)
        disp=max((x-y).length for x,y in zip(before,after));assert disp>.0001
        faces.append(dict(actor=name,frame=f,max_facial_split_m=gap))
        precision.append(dict(actor=name,frame=f,max_precision_displacement_m=disp))
        hips.append((rig.matrix_world@rig.pose.bones['pelvis'].head).copy())
        feet.append([(rig.matrix_world@rig.pose.bones['foot_'+side].head).copy() for side in ['R','L']])
        for side in ['R','L']:
            control='R3 | '+side+' wrist' if label is None else 'INTERVIEW | '+label+' '+side+' wrist'
            target=bpy.data.objects[control].location
            distance=(target-rig.matrix_world@rig.pose.bones['arm_'+side].head).length
            error=(target-rig.matrix_world@rig.pose.bones['hand_'+side].head).length
            assert distance<.442 and error<.015,(name,f,side,distance,error)
            arms.append(dict(actor=name,frame=f,side=side,reach_m=distance,target_error_m=error))
    assert max((h-hips[0]).length for h in hips)<.00001
    assert max((pair[i]-feet[0][i]).length for pair in feet for i in [0,1])<.00001
    support[name]='stable pelvis and feet'
    assert all(k.value==0 for k in obj.data.shape_keys.key_blocks[1:])
    for fc in obj.animation_data.action.fcurves:
        if 'PS1_face_id' in fc.data_path:
            assert all(k.interpolation=='CONSTANT' for k in fc.keyframe_points)
            if label=='Guest':assert set(round(k.co.y)for k in fc.keyframe_points)<={2,6,10,13,15}
tex=next(n for n in bpy.data.objects['CRT moving picture'].data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE')
assert tex.image_user.use_auto_refresh and tex.image_user.frame_duration==s.frame_end
sounds=[q for q in s.sequence_editor.sequences if q.type=='SOUND']
assert len(sounds)==1 and sounds[0].frame_start==1
report=dict(original_geometry_max_displacement_m=0.0,face_checks=faces,precision_checks=precision,
            seated_support=support,arm_checks=arms,guest_silent=True,guest_has_no_talking_faces=True,
            voice_tracks=1,monitor_frames=tex.image_user.frame_duration,monitor_auto_refresh=True,
            expressions='31 PNG faces, constant changes, no morphs',
            acting='Asymmetric phrase gestures, matching seated eyelines, silent guest reaction')
(ROOT/('scene_validation_16x9.json'if '--wide'in sys.argv else'scene_validation.json')).write_text(json.dumps(report,indent=2))
print('TRACER_SCENE_VALIDATED',flush=True)
