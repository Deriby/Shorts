"""Inspect only the library assets needed for the new room."""
from pathlib import Path
import bpy,json
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[3]
BANK=ROOT/'assets/biblioteca_psx/originais/Banco 3D para vídeos'
OUT=Path('/workspace/attachments/quarto_gamer_v2')
office=BANK/'OFFICE/OFFICE'
selections=['desks/desk1_weathered.glb','desks/desk2.glb','chairs/office_chair_fancy.glb','chairs/office_chair_black.glb','computers/computer_monitor.glb','computers/computer_keyboard.glb','computers/computer_mouse.glb','computers/computer_tower.glb','computers/TV.glb','book_things/book_case.glb','book_things/books.glb','extras/circular_desklamp.glb','extras/mug.glb','couches/beanbag_blue.glb']
record={'glb':[],'blend_libraries':[]}
for relative in selections:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    source=office/relative;bpy.ops.import_scene.gltf(filepath=str(source))
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
    bounds=[o.matrix_world@Vector(c)for o in objects for c in o.bound_box]
    lo=[min(v[i]for v in bounds)for i in range(3)];hi=[max(v[i]for v in bounds)for i in range(3)]
    record['glb'].append({'file':relative,'objects':[(o.name,len(o.data.polygons))for o in objects],'min':lo,'max':hi,'size':[hi[i]-lo[i]for i in range(3)],'images':[(im.name,list(im.size))for im in bpy.data.images if im.type=='IMAGE']})
    print('ASSET',record['glb'][-1],flush=True)
pal=BANK/'LowPolyAssetPack_Free/LowPolyAssetPack_Free/FBX and Blend Files'
for rel in ['Technology Props/Games Consoles/Free_Mesh_GamesConsoles_Mutliple.blend','Technology Props/Audio Equipment/Free_Mesh_Audio_Equipment.blend','Technology Props/Misc Tech Props/Free_Mesh_MiscTechProps.blend','Furniture/Chairs/Free_Mesh_Chairs_Multiple.blend','Furniture/Tables/Free_Mesh_Tables_Desks_Multiple.blend']:
    with bpy.data.libraries.load(str(pal/rel),link=False)as(src,dst):names=list(src.objects)
    record['blend_libraries'].append({'file':rel,'objects':names})
    print('LIBRARY',record['blend_libraries'][-1],flush=True)
# Houses may contain a bed/wardrobe not offered as separate files.
for name,path in [('Quequis',BANK/'Quequis_House/Quequis_House/Models/Quequis_House_Props.glb'),('House',BANK/'House/House/Models/House.fbx')]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if path.suffix=='.glb':bpy.ops.import_scene.gltf(filepath=str(path))
    else:bpy.ops.import_scene.fbx(filepath=str(path))
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
    record[name]=[(o.name,tuple(round(x,3)for x in o.dimensions),len(o.data.polygons))for o in objects]
    print('HOUSE_OBJECTS',name,record[name],flush=True)
(OUT/'banco_inspecionado.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
