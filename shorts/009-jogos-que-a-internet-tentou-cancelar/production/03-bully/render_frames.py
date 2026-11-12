"""Resume actual 3D frames; use cached CPU kernels and persistent scene data."""
from pathlib import Path
import bpy,sys,json,hashlib,time
P=Path(__file__).resolve().parent
info=json.loads((P/'timeline.json').read_text());model=P/'output/Dery_Bully.blend'
C=Path(info.get('cache','/workspace/attachments/jogos_cancelar'))/'frames';C.mkdir(parents=True,exist_ok=True)
generation=hashlib.sha256(model.read_bytes()+(P/info.get('monitor_file','assets/monitor/monitor_completo.mp4')).read_bytes()).hexdigest()
stamp=C/'source.sha256'
if stamp.exists():assert stamp.read_text().strip()==generation,'The scene changed: invalidate the old frame cache.'
else:stamp.write_text(generation+'\n')
assert json.loads((C.parent/'crt_cache.json').read_text())['movie_sha256']==hashlib.sha256((P/info['monitor_file']).read_bytes()).hexdigest()
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else['0','1']
worker,total=map(int,args[:2]);limit=int(args[2])if len(args)>2 else 0
bpy.ops.wm.open_mainfile(filepath=str(model));s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.samples=1;s.cycles.use_denoising=False;s.render.use_persistent_data=True
s.render.threads_mode='FIXED';s.render.threads=2;s.render.film_transparent=False
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.compression=10
screen=bpy.data.objects['Tela do PC | substituir por vídeo']
tex=next(n for n in screen.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE')
# Avoid re-seeking a long H.264 source for every dependency-graph evaluation.
cache_image=bpy.data.images.load(str(C.parent/'crt_0001.png'),check_existing=False)
tex.image=cache_image;tex.interpolation='Closest'
start=time.monotonic();done=0
for frame in range(1+worker,info['frames']+1,total):
    sh=next(sh for sh in info['shots']if sh['start']<=frame<=sh['end'])
    if sh['kind']in['photo','game']:continue
    if sh['kind']=='archive'and(frame-sh['start'])%3:continue # static graphic stage, held 10 Hz emphasis; actor shots remain 30 Hz
    dest=C/f'frame_{frame:04d}.png'
    if dest.exists():continue
    if sh['kind']in['monitor','host','close']:
        cache_image.filepath=str(C.parent/f'crt_{frame:04d}.png');cache_image.reload()
    s.frame_set(frame);s.camera=bpy.data.objects[s['Production | camera']]
    bpy.context.view_layer.update()
    if info.get('revision',1)>=2:
        for name in['DERY | animated character','GTA | Dery lojista']:
            actor=bpy.data.objects[name]
            selector=actor.data.materials[1].node_tree.nodes['PS1 | face ID'].outputs[0].default_value
            assert abs(selector-int(actor['PS1_face_id']))<1e-5,(name,frame,selector,actor['PS1_face_id'])
    s.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
    done+=1
    if done%15==0:print('PROGRESS',worker,frame,done,round(time.monotonic()-start,1),flush=True)
    if limit and done>=limit:break
print('RENDER_WORKER_DONE',worker,done,round(time.monotonic()-start,1),flush=True)
