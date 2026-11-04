"""Render changed acting takes only; the approved monitor takes are cached."""
from pathlib import Path
import json,bpy
ROOT=Path(__file__).resolve().parent
reuse=set(json.loads((ROOT/'reuse_r3.json').read_text())['frames'])
s=bpy.context.scene
project_time=Path(bpy.data.filepath).stat().st_mtime
for frame in range(1,673):
    image=ROOT/'renders/r3'/f'frame_{frame:04d}.png'
    if frame in reuse and image.exists() and image.stat().st_mtime>=project_time:continue
    s.frame_set(frame);s.render.filepath=str(image)
    bpy.ops.render.render(write_still=True)
print('R3_CHANGED_FRAMES_READY',flush=True)
