"""Disjoint frame workers; one per format by default. Media inserts bypass Blender."""
from pathlib import Path
import bpy,json,sys
ROOT=Path(__file__).resolve().parent;args=sys.argv[sys.argv.index('--')+1:];wide='--wide'in args;resume='--resume'in args;args=[x for x in args if x not in ['--wide','--resume']];worker,count=map(int,args[:2]);lo,hi=map(int,args[2:4])if len(args)>2 else(1,10**9)
i=json.loads((ROOT/'timeline.json').read_text());s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=2;s.render.use_persistent_data=True;out=ROOT/('renders/final_16x9'if wide else'renders/final');out.mkdir(exist_ok=True)
frames=[f for sh in i['shots']if sh['kind']in ['actor','monitor','museum']for f in range(sh['start'],sh['end']+1)if lo<=f<=hi and(not resume or not(out/f'frame_{f:04d}.png').exists())][worker::count]
meshes=[o for o in s.objects if o.type=='MESH'];old_kind=None
for n,f in enumerate(frames):
 kind=next(sh['kind']for sh in i['shots']if sh['start']<=f<=sh['end']);museum=kind=='museum'
 if kind!=old_kind:
  for o in meshes:o.hide_render=(not museum)if o.name.startswith('MUSEUM |')else museum
  old_kind=kind
 s.frame_set(f);dest=out/f'frame_{f:04d}.png';temp=out/f'.frame_{f:04d}.tmp.png';s.render.filepath=str(temp);bpy.ops.render.render(write_still=True);temp.replace(dest)
 if n%40==0:print('PROGRESS',worker,n+1,len(frames),flush=True)
print('ANKHA_WORKER_READY',worker,len(frames),flush=True)
