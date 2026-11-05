"""Render disjoint frame partitions; two workers share only read-only project assets."""
from pathlib import Path
import bpy,json,sys
ROOT=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:]if '--'in sys.argv else ['0','1']
worker,count=map(int,args[:2])
lo,hi=map(int,args[2:4])if len(args)>=4 else (1,10**9)
ranges=[(lo,hi)]+[tuple(map(int,x.split(':')))for x in args[5:]]
info=json.loads((ROOT/'timeline.json').read_text());s=bpy.context.scene
s.render.threads_mode='FIXED';s.render.threads=2;s.render.use_persistent_data=True
frames=[f for shot in info['shots']if shot['kind']!='game'for f in range(shot['start'],shot['end']+1)if any(start<=f<=end for start,end in ranges)][worker::count]
out=Path(args[4])if len(args)>=5 else ROOT/'renders/final';out.mkdir(parents=True,exist_ok=True)
for i,f in enumerate(frames):
    s.frame_set(f);s.render.filepath=str(out/f'frame_{f:04d}.png');bpy.ops.render.render(write_still=True)
    if i%40==0:print('PROGRESS',worker,i+1,len(frames),flush=True)
print('WORKER_READY',worker,len(frames),flush=True)
