"""Plan the per-shot vertical crop from the native Blender cameras."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
root=Path(__file__).resolve().parent
s=bpy.context.scene;rig=bpy.data.objects['Dery_Rig']
info=json.loads((root/'timeline.json').read_text());crop=[]
for shot in info['shots']:
 xs=[]
 for frame in [shot['start'],shot['end']]:
  s.frame_set(frame)
  if shot['kind'].startswith('monitor'):p=Vector((.1095,-.7959,1.262))
  else:
   b=rig.pose.bones['head'];p=rig.matrix_world@(b.matrix@(b.bone.matrix_local.inverted()@Vector((0,-.085,1.59))))
  x=world_to_camera_view(s,s.camera,p).x*1920
  xs.append(max(0,min(1312,round(x-304))))
 crop.append({'start':shot['start'],'end':shot['end'],'kind':shot['kind'],'x_start':xs[0],'x_end':xs[1]})
(root/'vertical_crops.json').write_text(json.dumps(crop,indent=2))
print(json.dumps(crop))
