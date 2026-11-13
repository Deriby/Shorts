from pathlib import Path
import bpy,sys,json,hashlib,shutil
P=Path(__file__).resolve().parent;info=json.loads((P/'timeline.json').read_text());data=json.loads((P/'construcao.json').read_text());C=Path(info['cache'])/'frames';C.mkdir(parents=True,exist_ok=True);model=P/'output'/info['model'];digest=hashlib.sha256(model.read_bytes()).hexdigest();stamp=C/'source.sha256'
if stamp.exists():assert stamp.read_text().strip()==digest
else:stamp.write_text(digest+'\n')
worker,total=map(int,sys.argv[sys.argv.index('--')+1:][:2]);bpy.ops.wm.open_mainfile(filepath=str(model));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=1;s.cycles.use_denoising=False;s.render.use_persistent_data=True;s.render.threads_mode='FIXED';s.render.threads=2;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.compression=10
screen=bpy.data.objects['Tela do PC | substituir por vídeo'];placeholder=bpy.data.images.new('Render only | clean media placeholder',width=1,height=1);placeholder.generated_color=(.02,.02,.02,1)
for n in screen.data.materials[0].node_tree.nodes:
 if n.type=='TEX_IMAGE':n.image=placeholder
for i,f in enumerate(data['frames_to_render']):
 if i%total!=worker:continue
 dest=C/f'frame_{f:04d}.png'
 if not dest.exists():
  s.frame_set(f);bpy.context.view_layer.update();a=bpy.data.objects['DERY | animated character'];assert abs(a.data.materials[1].node_tree.nodes['PS1 | face ID'].outputs[0].default_value-int(a['PS1_face_id']))<1e-5;s.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
 for alias in data['monitor_background_aliases'].get(str(f),[]):shutil.copyfile(dest,C/f'frame_{alias:04d}.png')
print('GTA_V_RENDER_DONE',worker,flush=True)
