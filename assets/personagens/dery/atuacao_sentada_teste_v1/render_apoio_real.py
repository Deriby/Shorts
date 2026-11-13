from pathlib import Path
import bpy,sys,time,hashlib,json
P=Path(__file__).resolve().parent;C=Path('/workspace/attachments/atuacao_sentada_v3/frames');C.mkdir(parents=True,exist_ok=True);model=P/'output/Dery_Atuacao_Apoio_Real.blend';digest=hashlib.sha256(model.read_bytes()).hexdigest();stamp=C/'source.sha256'
if stamp.exists():assert stamp.read_text().strip()==digest
else:stamp.write_text(digest+'\n')
worker,total=map(int,sys.argv[sys.argv.index('--')+1:][:2]);bpy.ops.wm.open_mainfile(filepath=str(model));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=1;s.cycles.use_denoising=False;s.render.use_persistent_data=True;s.render.threads_mode='FIXED';s.render.threads=2;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.compression=10;start=time.monotonic();done=0
for f in range(1+worker,241,total):
 dest=C/f'frame_{f:04d}.png'
 if dest.exists():continue
 s.frame_set(f);bpy.context.view_layer.update();actor=bpy.data.objects['DERY | animated character'];value=actor.data.materials[1].node_tree.nodes['PS1 | face ID'].outputs[0].default_value;assert abs(value-int(actor['PS1_face_id']))<1e-5
 s.render.filepath=str(dest);bpy.ops.render.render(write_still=True);done+=1
 if done%20==0:print('TEST_PROGRESS',worker,f,round(time.monotonic()-start,1),flush=True)
print('TEST_RENDER_DONE',worker,done,round(time.monotonic()-start,1),flush=True)
