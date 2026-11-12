"""Reopen the delivered .blend; check packing, driver, geometry and hard keys."""
from pathlib import Path
import json,sys
import bpy,numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from setup_faces131 import install,set_face

bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Dery_131_Expressoes_PS1.blend'))
a=bpy.data.objects['DERY | animated character']
assert a.parent.name=='Dery_Rig'
assert a.data.materials[1].get('DeryExpressionVersion')==3
assert 'DeryFacePS1' in a.data.uv_layers
assert a.id_properties_ui('PS1_face_id').as_dict()['max']==130
nt=a.data.materials[1].node_tree
atlas=nt.nodes['PS1 | 131 drawn PNGs']
assert atlas.interpolation=='Closest' and tuple(atlas.image.size)==(2048,1152)
assert all(im.packed_file for im in bpy.data.images if im.source=='FILE' and im.users)
assert all(not mod.show_viewport or mod.node_group for mod in a.modifiers if mod.type=='NODES')
for i in [0,30,31,55,56,80,81,105,106,130]:
    set_face(a,i)
    assert abs(nt.nodes['PS1 | face ID'].outputs[0].default_value-i)<.001
    evaluated=a.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
    coords=np.array([tuple(v.co) for v in evaluated.vertices])
    assert np.isfinite(coords).all()
    a.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear()
set_face(a,31,frame=1);set_face(a,130,frame=8)
action=a.animation_data.action
curve=next(c for c in action.fcurves if c.data_path=='["PS1_face_id"]')
assert all(k.interpolation=='CONSTANT' for k in curve.keyframe_points)
bpy.context.scene.frame_set(7)
assert int(a['PS1_face_id'])==31
bpy.context.scene.frame_set(8)
assert int(a['PS1_face_id'])==130
original_material=a.data.materials[1]
assert install(a)==original_material
clone=a.copy();clone.data=a.data.copy();clone.animation_data_clear()
bpy.context.scene.collection.objects.link(clone)
install(clone);set_face(clone,106)
assert clone.data.materials[1]!=a.data.materials[1]
assert int(a['PS1_face_id'])==130
assert clone.data.materials[1].node_tree.nodes['PS1 | face ID'].outputs[0].default_value==106
report=json.loads((ROOT/'validacao.json').read_text())
report.update(blend_reopened=True,active_images_packed=True,driver_boundary_ids_verified=True,
              evaluated_mesh_finite=True,constant_keyframes_verified=True,
              duplicated_character_independent_driver=True)
(ROOT/'validacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('BLENDER_131_VALIDATED',flush=True)
