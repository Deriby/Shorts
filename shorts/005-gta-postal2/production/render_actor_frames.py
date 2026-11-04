from pathlib import Path
import bpy,json
ROOT=Path(__file__).resolve().parent;info=json.loads((ROOT/'timeline.json').read_text());s=bpy.context.scene
for shot in info['shots']:
    if shot['kind']=='game':continue
    for f in range(shot['start'],shot['end']+1):
        s.frame_set(f);s.render.filepath=str(ROOT/'renders/final'/f'frame_{f:04d}.png');bpy.ops.render.render(write_still=True)
print('ACTOR_FRAMES_READY',flush=True)
