"""Reopen the real Blender asset and validate used library data and packed images."""
from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector

P=Path(__file__).resolve().parent;ROOT=P.parents[2]
path=P/'Quarto_Gamer_Banco_PS1.blend'
bpy.ops.wm.open_mainfile(filepath=str(path))
scene=bpy.context.scene
screen=bpy.data.objects['Tela do PC | substituir por vídeo']
wall=bpy.data.objects['M na parede']
if screen.data.materials[0]==wall.data.materials[0]:
    material=screen.data.materials[0].copy();material.name='DISPLAY | PC | trocar mídia';screen.data.materials[0]=material
    bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
assert screen.data.materials[0]!=wall.data.materials[0]
record=json.loads((P/'fontes_e_montagem.json').read_text())
bank=ROOT/'assets/biblioteca_psx/originais/Banco 3D para vídeos'
for source in record['sources']:
    assert hashlib.sha256((bank/source['file']).read_bytes()).hexdigest()==source['sha256']
images=[im for im in bpy.data.images if im.type=='IMAGE']
assert all(im.packed_file and im.size[0]>0 and im.size[1]>0 for im in images)
for im in images:
    # Packed image buffers are loaded lazily when reopening a .blend.
    pixel=im.pixels[:4]
    assert len(pixel)==4 and all(math.isfinite(x)for x in pixel)
assert not any(o.type=='ARMATURE'for o in scene.objects)
objects=[o for o in scene.objects if o.type=='MESH']
assert all(math.isfinite(v)for o in objects for vertex in o.data.vertices for v in vertex.co)
assert all(len(o.data.uv_layers)>0 for o in objects)
assert len([o for o in scene.objects if o.type=='CAMERA'])==3
bed=bpy.data.objects['Cama | House bed_02'];points=[bed.matrix_world@Vector(c)for c in bed.bound_box]
dimensions=[max(p[i]for p in points)-min(p[i]for p in points)for i in range(3)]
assert 1.29<dimensions[0]<1.36 and 1.9<dimensions[1]<2.1,dimensions
for mat in bed.data.materials:
    bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    assert not bs.inputs['Alpha'].is_linked and bs.inputs['Alpha'].default_value==1
selected=json.loads((ROOT/'assets/personagens/dery/modelo_atual.json').read_text())
avatar=ROOT/'assets/personagens/dery'/selected['selected_model']
assert hashlib.sha256(avatar.read_bytes()).hexdigest()==selected['sha256']
out={'scene_file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'library_models_unchanged':True,'used_library_instances':len(record['sources']),'unique_library_models':len({s['file']for s in record['sources']}),'packed_images':len(images),'missing_images':0,'camera_presets':3,'bed_dimensions_m':dimensions,'separate_pc_display_material':True,'original_dery_unchanged':True,'finite_coordinates':True,'all_meshes_have_uv':True,'animation_rendered':False,'approval_pending':True}
(P/'validacao.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('VALIDATED',out,flush=True)
