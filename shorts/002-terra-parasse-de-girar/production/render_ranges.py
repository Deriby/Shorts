"""Render disjoint frame ranges from the saved scene; supports parallel CPU workers."""
import bpy,sys,argparse
from pathlib import Path
root=Path(__file__).resolve().parent
p=argparse.ArgumentParser(); p.add_argument('--ranges',required=True); p.add_argument('--threads',type=int,default=2)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
bpy.ops.wm.open_mainfile(filepath=str(root/'output/Dery_Terra_Parou.blend'))
s=bpy.context.scene; s.render.threads_mode='FIXED'; s.render.threads=a.threads
s.render.filepath=str(root/'renders/frame_')
for chunk in a.ranges.split(','):
    start,end=map(int,chunk.split(':')); s.frame_start=start; s.frame_end=end
    bpy.ops.render.render(animation=True)
