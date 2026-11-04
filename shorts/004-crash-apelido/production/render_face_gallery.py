"""Inspect all 31 actual on-model expressions using the same framing."""
from pathlib import Path
import bpy,sys
ROOT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'output/Dery_Crash_Master_R5.blend'))
s=bpy.context.scene;s.frame_set(110)
a=bpy.data.objects['DERY | animated character'];a.animation_data_clear()
s.render.use_border=True;s.render.use_crop_to_border=True
s.render.border_min_x=.36;s.render.border_max_x=.69;s.render.border_min_y=.12;s.render.border_max_y=.80
for face in range(12 if '--new-only'in sys.argv else 0,31):
    a['PS1_face_id']=face;a.update_tag();bpy.context.view_layer.update()
    s.render.filepath=str(ROOT/'renders/r5_faces'/f'face_{face:02d}.png')
    bpy.ops.render.render(write_still=True)
print('31_ON_MODEL_FACES_READY',flush=True)
