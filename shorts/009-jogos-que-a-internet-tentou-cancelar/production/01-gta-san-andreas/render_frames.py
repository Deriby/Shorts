"""Resume actual 3D frames; use cached CPU kernels and persistent scene data."""
from pathlib import Path
import bpy,sys,json,hashlib,time
P=Path(__file__).resolve().parent
C=Path('/workspace/attachments/jogos_cancelar/frames');C.mkdir(exist_ok=True)
info=json.loads((P/'timeline.json').read_text());model=P/'output/Dery_GTA_San_Andreas.blend'
generation=hashlib.sha256(model.read_bytes()+(P/'assets/monitor/monitor_completo.mp4').read_bytes()).hexdigest()
stamp=C/'source.sha256'
if stamp.exists():assert stamp.read_text().strip()==generation,'The scene changed: invalidate the old frame cache.'
else:stamp.write_text(generation+'\n')
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else['0','1']
worker,total=map(int,args[:2])
bpy.ops.wm.open_mainfile(filepath=str(model));s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.samples=1;s.cycles.use_denoising=False;s.render.use_persistent_data=True
s.render.threads_mode='FIXED';s.render.threads=2;s.render.film_transparent=False
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.compression=10
start=time.monotonic();done=0
for frame in range(1+worker,info['frames']+1,total):
    sh=next(sh for sh in info['shots']if sh['start']<=frame<=sh['end'])
    if sh['kind']in['photo','game']:continue
    dest=C/f'frame_{frame:04d}.png'
    if dest.exists():continue
    s.frame_set(frame);s.camera=bpy.data.objects[s['Production | camera']]
    bpy.context.view_layer.update();s.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
    done+=1
    if done%15==0:print('PROGRESS',worker,frame,done,round(time.monotonic()-start,1),flush=True)
print('RENDER_WORKER_DONE',worker,done,round(time.monotonic()-start,1),flush=True)
