"""Render alternate frames in two workers using one animated PS1 camera."""
from pathlib import Path
import bpy,json,sys,hashlib

P=Path(__file__).resolve().parent
WORK=Path('/workspace/attachments/quarto_gamer_cena/frames');WORK.mkdir(exist_ok=True)
stamp=WORK/'fonte.sha256'
generation=hashlib.sha256((P/'Dery_No_Quarto_Teste_6s.blend').read_bytes()+(P/'media/Monitor_Driver_6s.mp4').read_bytes()).hexdigest()
if stamp.exists():assert stamp.read_text().strip()==generation,'Cena ou vídeo alterado: invalidar os frames antigos antes de retomar.'
else:stamp.write_text(generation+'\n')
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else['0','1']
worker,total=map(int,args)
bpy.ops.wm.open_mainfile(filepath=str(P/'Dery_No_Quarto_Teste_6s.blend'))
scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=2
actor=bpy.data.objects['DERY | animated character']
for frame in range(1+worker,97,total):
    dest=WORK/f'frame_{frame:04d}.png'
    if dest.exists():continue
    scene.frame_set(frame)
    scene.camera=bpy.data.objects[scene['Demo | câmera']]
    bpy.context.view_layer.update()
    scene.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
    if frame%16==1+worker:print('PROGRESS',worker,frame,flush=True)
