"""Render only the sustained physical-room shot, with resumable atomic frame writes."""
from pathlib import Path
import bpy,json,sys
ROOT=Path(__file__).resolve().parent
info=json.loads((ROOT/'timeline.json').read_text());s=bpy.context.scene
s.render.threads_mode='FIXED';s.render.threads=2;s.render.use_persistent_data=True
out=ROOT/'renders/final';out.mkdir(exist_ok=True)
frames=[f for sh in info['shots']if sh['kind']=='actor'for f in range(sh['start'],sh['end']+1)]
if '--resume'in sys.argv:frames=[f for f in frames if not(out/f'frame_{f:04d}.png').exists()]
for i,f in enumerate(frames):
 s.frame_set(f);temp=out/f'.frame_{f:04d}.tmp.png';s.render.filepath=str(temp);bpy.ops.render.render(write_still=True);temp.replace(out/f'frame_{f:04d}.png')
 if i%40==0:print('PROGRESS',i+1,len(frames),flush=True)
print('INTRO_WORKER_READY',len(frames),flush=True)
