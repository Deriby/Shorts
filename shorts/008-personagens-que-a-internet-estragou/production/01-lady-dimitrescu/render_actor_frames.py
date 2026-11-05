"""Two disjoint render workers; media-only inserts bypass Blender."""
from pathlib import Path
import bpy,json,sys
ROOT=Path(__file__).resolve().parent;args=sys.argv[sys.argv.index('--')+1:];wide='--wide'in args;args=[x for x in args if x!='--wide'];worker,count=map(int,args[:2]);lo,hi=map(int,args[2:4])if len(args)>2 else(1,10**9)
i=json.loads((ROOT/'timeline.json').read_text());s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=2;s.render.use_persistent_data=True;out=ROOT/('renders/final_16x9'if wide else'renders/final');out.mkdir(exist_ok=True)
frames=[f for sh in i['shots']if sh['kind']in ['actor','monitor','castle']for f in range(sh['start'],sh['end']+1)if lo<=f<=hi][worker::count]
for n,f in enumerate(frames):
 s.frame_set(f);s.render.filepath=str(out/f'frame_{f:04d}.png');bpy.ops.render.render(write_still=True)
 if n%40==0:print('PROGRESS',worker,n+1,len(frames),flush=True)
print('LADY_WORKER_READY',worker,len(frames),flush=True)
