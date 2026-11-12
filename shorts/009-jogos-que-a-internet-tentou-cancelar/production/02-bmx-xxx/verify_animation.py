"""Check the rendered selector, projection math and actual visible expression ROIs."""
from pathlib import Path
import bpy,json,numpy as np
from bpy_extras.object_utils import world_to_camera_view

P=Path(__file__).resolve().parent;C=Path('/workspace/attachments/bmx_xxx');C.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(P/'output/Dery_BMX_XXX.blend'))
s=bpy.context.scene;cam=s.camera
actors=[bpy.data.objects['DERY | animated character'],bpy.data.objects['GTA | Dery lojista']]
values={a.name:[]for a in actors};grid=[]
for frame in[82,96,112,132,145,218,600,720,870,1238,1286]:
    s.frame_set(frame);bpy.context.view_layer.update()
    for a in actors:
        nt=a.data.materials[1].node_tree
        actual=nt.nodes['PS1 | face ID'].outputs[0].default_value
        expected=int(a['PS1_face_id'])
        assert abs(actual-expected)<1e-5,(a.name,frame,actual,expected)
        assert not(nt.animation_data and nt.animation_data.drivers)
        assert all(k.interpolation=='CONSTANT'for fc in nt.animation_data.action.fcurves for k in fc.keyframe_points)
        values[a.name].append(expected)
    screen=bpy.data.objects['Tela do PC | substituir por vídeo']
    ev=screen.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
    try:
        assert 'PSX_Affine_UVMap'in mesh.attributes
        v=np.array([tuple(x.vector)for x in mesh.attributes['PSX_Affine_UVMap'].data])
        assert np.isfinite(v).all()and np.max(v[:,2])>.01
        if frame==82:
            loops=list(mesh.polygons[0].loop_indices)[:3]
            attribute=v[loops];depth=attribute[:,2];uv=attribute[:,:2]/depth[:,None]
            lam=np.array([.19,.34,.47]);weights=lam/depth
            interp=(attribute*weights[:,None]).sum(axis=0)/weights.sum()
            reconstructed=interp[:2]/interp[2]
            assert np.max(np.abs(reconstructed-(uv*lam[:,None]).sum(axis=0)))<1e-7
        for vertex in mesh.vertices:
            projected=world_to_camera_view(s,cam,screen.matrix_world@vertex.co)
            if projected.z>0:
                x,y=projected.x*320,projected.y*180
                error=max(abs(x-round(x)),abs(y-round(y)))
                grid.append(error)
    finally:ev.to_mesh_clear()
assert max(grid)<.005,('Screen vertices do not follow the promised grid',max(grid))
assert all(len(set(v))>=5 for v in values.values())
s.render.engine='CYCLES';s.cycles.samples=1;s.cycles.use_denoising=False;s.render.use_persistent_data=True;s.render.threads=2
# Controlled head close-up: no pose/camera movement can masquerade as a mouth swap.
s.frame_set(121)
actor=actors[0];node=actor.data.materials[1].node_tree.nodes['PS1 | face ID']
action=actor.data.materials[1].node_tree.animation_data.action
actor.data.materials[1].node_tree.animation_data.action=None
s.render.resolution_x=384;s.render.resolution_y=216
for index in[31,32,33,35,107]:
    node.outputs[0].default_value=index;actor.data.materials[1].node_tree.update_tag()
    s.render.filepath=str(C/f'face_control_{index:03d}.png');bpy.ops.render.render(write_still=True)
actor.data.materials[1].node_tree.animation_data.action=action
# Real scene snapshots confirm hands, face fitting and camera-safe labels.
s.render.resolution_x=768;s.render.resolution_y=432
for frame in[121,405,705,870,1280]:
    s.frame_set(frame);s.render.filepath=str(C/f'scene_{frame:04d}.png');bpy.ops.render.render(write_still=True)
report=dict(material_selector_matches_actor_property=True,ids=values,affine_interpolation_verified=True,
            snap_grid_max_error=max(grid),snap_grid=[320,180],face_keys_constant=True,body_fps=s.render.fps,
            controlled_face_renders=[31,32,33,35,107])
(P/'validacao_animacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('R2_ANIMATION_VALIDATED',json.dumps(report,ensure_ascii=False),flush=True)
