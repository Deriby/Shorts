"""The existing clean-media composition, restricted to landscape delivery."""
from pathlib import Path
import sys
P=Path(__file__).resolve().parent;R=next(p for p in P.parents if(p/'AGENTS.md').exists());shared=P.parent/'shared_media/compose_clean.py'
sys.argv=[str(shared),str(P)]
exec(compile(shared.read_text().split('base_writer=Writer(')[0],str(shared),'exec'))
base_name=slug+'_base_16x9.mp4';base_writer=Writer(MEDIA/base_name,(1920,1080));video=OUT/(slug+'_16x9.mp4');writer=Writer(video,(1920,1080),A/'audio/mix_final.wav');processed=0
for sh in info['shots']:
 count=sh['end']-sh['start']+1;needs_media=sh['kind']in['game','photo']or any(str(f)in projection['frames']for f in range(sh['start'],sh['end']+1));source_path=A/('gameplay'if sh['source'].lower().endswith('.mp4')else'imagens')/sh['source'];reader=None;photo=None
 if needs_media:
  if source_path.suffix.lower()=='.mp4':reader=Reader(source_path,sh['source_start'],count)
  else:photo=Image.open(source_path).convert('RGB')
 for f in range(sh['start'],sh['end']+1):
  u=(f-sh['start'])/max(1,sh['end']-sh['start']);ease=u*u*(3-2*u);z=1+(ed['edits'][sh['id']]['zoom_end']-1)*ease;source=reader.read()if reader else photo
  if sh['kind']in['game','photo']:base=media_canvas(source,sh['kind'],True);final=media_canvas(source,sh['kind'],True,z)
  else:
   raw=quantize(Image.open(C/'frames'/f'frame_{f:04d}.png').convert('RGB'));base=animation_canvas(raw,True);final=animation_canvas(raw,True,z)
   if source is not None:base=overlay(base,source,f,True,1);final=base if abs(z-1)<1e-9 else overlay(final,source,f,True,z)
  base_writer.write(base);writer.write(final);processed+=1
  if f in [round((x['start']+x['end'])/2)for x in info['shots']]:final.save(C/f'final_16x9_{f:04d}.jpg',quality=95)
  if processed%150==0:print('LANDSCAPE_COMPOSE',P.name,processed,flush=True)
 if reader:reader.close()
for output in [base_writer,writer]:output.close()
assert processed==N
(OUT/'midias_limpas.json').write_text(json.dumps(dict(frames=processed,delivery_formats=['16x9'],media_psx=False,crt_clean=True,crt_aspect_preserved=True,voice_full=True,no_vertical_outputs=True,outputs=[str(video.relative_to(P)),str((MEDIA/base_name).relative_to(P))]),ensure_ascii=False,indent=2)+'\n');print('LANDSCAPE_READY',P.name,flush=True)
