from pathlib import Path
import bpy,sys,json,hashlib,time
P=Path(__file__).resolve().parent;worker,total=map(int,sys.argv[sys.argv.index('--')+1:][:2]);start=time.monotonic()
for project in sorted(P.parent.glob('0[1-4]-*')):
 out=project/'output/R4_Sem_Dery_Em_Pe';info=json.loads((out/'timeline.json').read_text());data=json.loads((out/'animacao_revisada.json').read_text());model=out/(info['slug']+'_R4_Dery_Sentado.blend');C=Path('/workspace/attachments/revisao_r4')/project.name/'frames';C.mkdir(parents=True,exist_ok=True);stamp=C/'source.sha256';digest=hashlib.sha256(model.read_bytes()).hexdigest()
 if stamp.exists():assert stamp.read_text().strip()==digest
 else:stamp.write_text(digest+'\n')
 bpy.ops.wm.open_mainfile(filepath=str(model));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=1;s.cycles.use_denoising=False;s.render.use_persistent_data=True;s.render.threads_mode='FIXED';s.render.threads=2;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.compression=10
 for i,f in enumerate(data['frames']):
  if i%total!=worker:continue
  dest=C/f'frame_{f:04d}.png'
  if dest.exists():continue
  s.frame_set(f);bpy.context.view_layer.update();actor=bpy.data.objects['DERY | animated character'];assert abs(actor.data.materials[1].node_tree.nodes['PS1 | face ID'].outputs[0].default_value-int(actor['PS1_face_id']))<1e-5
  s.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
 print('CHAPTER_RENDERED',project.name,worker,round(time.monotonic()-start),flush=True)
