from pathlib import Path
import bpy,sys,json,hashlib
P=Path(__file__).resolve().parent;R=next(p for p in P.parents if(p/'AGENTS.md').exists());plans=json.loads((P/'plano.json').read_text());plans=[dict(ep,**g)for ep in plans for g in ep.get('gags',[{}])];worker,total=map(int,sys.argv[sys.argv.index('--')+1:][:2])
for plan in plans:
 model=R/plan.get('model',plan['output']+'/'+plan['slug']+'_R6_Cena_Curta.blend');cache=Path(plan['cache']);stamp=cache/'model.sha256';digest=hashlib.sha256(model.read_bytes()).hexdigest()
 if stamp.exists():assert stamp.read_text().strip()==digest
 else:stamp.write_text(digest+'\n')
 bpy.ops.wm.open_mainfile(filepath=str(model));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=1;s.cycles.use_denoising=False;s.render.use_persistent_data=True;s.render.threads_mode='FIXED';s.render.threads=2
 for f in range(1,plan['count']+1):
  if(f-1)%total!=worker:continue
  dest=cache/'frames'/f'frame_{f:04d}.png'
  if dest.exists():continue
  s.frame_set(f);bpy.context.view_layer.update()
  if plan['kind']in['recuo','sem_graca','surto']:
   actor=bpy.data.objects['DERY | animated character'];assert abs(actor.data.materials[1].node_tree.nodes['PS1 | face ID'].outputs[0].default_value-int(actor['PS1_face_id']))<1e-5
  s.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
 print('R6_RENDER_DONE',worker,plan['episode'],flush=True)
