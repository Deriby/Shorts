"""Export just the reusable garage/car geometry, without voice or personal reference."""
from pathlib import Path
import bpy
from mathutils import Matrix
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[2];s=bpy.context.scene;s.frame_set(1)
collection=bpy.data.collections.new('Massacote | garagem low poly');root=bpy.data.objects.new('GARAGE | reusable origin',None);collection.objects.link(root);root.location=(0,0,0)
objects=[o for o in s.objects if o.name.startswith(('CAR |','GARAGE |','BOSS |'))and not any(n in o.name for n in ['Dery','wrist','elbow','palm'])]
for o in objects:
 collection.objects.link(o);o.animation_data_clear();o.hide_render=False
 if o.parent is None:
  o.parent=root;o.matrix_parent_inverse=Matrix.Identity(4);o.location.x-=20
root.location=(0,0,0)
path=REPO/'assets/cenarios/garagem_driver/Garagem_Driver.blend';bpy.data.libraries.write(str(path),{collection},fake_user=True,compress=True)
print('GARAGE_ASSET_SAVED',path,flush=True)
