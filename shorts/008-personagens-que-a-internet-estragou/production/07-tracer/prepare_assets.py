"""Prepare inspected media and fictional document interfaces around the supplied voice."""
from pathlib import Path
import json, subprocess, math, wave, array
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
FPS = 24
records = json.loads((ROOT/'renders/package_inventory.json').read_text())
raw = {r['original_filename']: Path(r['local_path']) for r in records}
intake = json.loads((ROOT/'renders/audio_intake.json').read_text())
pics, game = ROOT/'assets/memes', ROOT/'assets/gameplay'
pics.mkdir(parents=True, exist_ok=True)
mapping={'tracerassmeme.jpg':'meme_reacao.jpg','tracermemetraceros.jpeg':'meme_pesquisa.jpg'}
for src,dest in mapping.items():
 im=Image.open(raw[src]).convert('RGB');im.thumbnail((1280,1280),Image.Resampling.NEAREST);im.save(pics/dest)
subprocess.run(['ffmpeg','-v','error','-y','-threads','1','-ss','1.2','-i',str(game/'tracer_apresentacao.mp4'),'-frames:v','1',str(pics/'tracer_retrato.png')],check=True)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def text(d,xy,value,size=20,fill='white',anchor='mm'):
 d.text(xy,value,font=ImageFont.truetype(font,size),fill=fill,anchor=anchor)
for vertical in [False,True]:
 W,H=(360,640)if vertical else(640,360);suffix='_vertical'if vertical else''
 for state in ['viewport','censurado']:
  im=Image.new('RGB',(W,H),(24,31,43));d=ImageDraw.Draw(im);d.rectangle((7,7,W-8,H-8),outline=(145,164,178),width=3);d.rectangle((12,12,W-13,47),fill=(46,62,82));text(d,(22,30),'VIEWPORT 3D',17,anchor='lm')
  horizon=180 if vertical else 135;bottom=H-38
  for x in range(-W,W*2,48):d.line((W//2,horizon,x,bottom),fill=(55,77,86),width=1)
  for u in [.1,.23,.4,.62,.86,1.0]:
   yy=round(horizon+(bottom-horizon)*u*u);d.line((13,yy,W-14,yy),fill=(55,77,86),width=1)
  cx,cy=(W//2,430)if vertical else(172,230);s=48
  pts=[(cx-s,cy-s//2),(cx,cy-s),(cx+s,cy-s//2),(cx+s,cy+s//2),(cx,cy+s),(cx-s,cy+s//2)]
  d.polygon(pts,fill=(58,99,111),outline=(143,215,218),width=3);d.line((pts[0],(cx,cy),pts[2]),fill=(143,215,218),width=3);d.line(((cx,cy),pts[4]),fill=(143,215,218),width=3)
  area=(29,75,W-29,275)if vertical else(340,77,610,276)
  d.rectangle(area,fill=(10,16,23),outline=(217,179,61),width=3)
  if state=='viewport':
   p=ImageOps.contain(Image.open(pics/'tracer_retrato.png'),(area[2]-area[0]-12,area[3]-area[1]-32),Image.Resampling.NEAREST);im.paste(p,((area[0]+area[2]-p.width)//2,area[1]+7));text(d,((area[0]+area[2])//2,area[3]-15),'REFERÊNCIA',17,(227,207,150))
  else:
   d.rectangle((area[0]+5,area[1]+5,area[2]-5,area[3]-5),fill=(4,7,11));text(d,((area[0]+area[2])//2,(area[1]+area[3])//2),'CENSURADO',24 if vertical else 23,(244,205,61))
  text(d,(W//2,H-21),'CENA / OBJETO / ANIMAÇÃO',14,(150,172,184));im.save(pics/f'{state}{suffix}.png')
with wave.open(str(ROOT/'assets/voz/narracao_completa.wav')) as w:
    sr=w.getframerate();voice=array.array('h',w.readframes(w.getnframes()))
vd=len(voice)/sr;N=math.ceil((vd+.65)*FPS);end=N/FPS
specs=[(0,1.0,'monitor','name','tracer_apresentacao.mp4',0),
 (1.0,2.4,'actor','present','tracer_apresentacao.mp4',1),
 (2.4,4.8,'game','blink','tracer_blink.mp4',.2),
 (4.8,7.88,'game','recall','tracer_recall.mp4',1.2),
 (7.88,9.4,'actor','explain','viewport.png',0),
 (9.4,11.48,'photo','viewport','viewport.png',0),
 (11.48,12.4,'photo','censored','censurado.png',0),
 (12.4,13.15,'photo','meme','meme_reacao.jpg',0),
 (13.15,13.9,'actor','sigh','censurado.png',0),
 (13.9,15.2,'interview','wide','tracer_retrato.png',0),
 (15.2,16.5,'photo','meme','meme_pesquisa.jpg',0),
 (16.5,17.8,'interview','guest','tracer_retrato.png',0),
 (17.8,19.9,'interview','host','tracer_retrato.png',0),
 (19.9,20.5,'interview','proud','tracer_retrato.png',0),
 (20.5,21.7,'interview','followup','tracer_retrato.png',0),
 (21.7,end,'interview','final','tracer_retrato.png',0)]
shots=[dict(id=i,start=round(t0*FPS)+1,end=round(t1*FPS),kind=k,mood=m,source=src,source_start=at)
       for i,(t0,t1,k,m,src,at) in enumerate(specs)]
shots[-1]['end']=N
assert all(a['end']+1==b['start']for a,b in zip(shots,shots[1:]))
media=ROOT/'renders/media';media.mkdir(exist_ok=True);clips=[]
for sh in shots:
    src=(game if sh['source'].endswith('.mp4') else pics)/sh['source']
    dest=media/f"monitor_{sh['id']:02d}.mp4";n=sh['end']-sh['start']+1
    cmd=['ffmpeg','-v','error','-y','-threads','1','-filter_threads','1']
    cmd+=['-ss',str(sh['source_start']),'-i',str(src)] if src.suffix=='.mp4' else ['-f','image2','-loop','1','-framerate','24','-i',str(src)]
    cmd+=['-an','-vf','fps=24,scale=640:360:force_original_aspect_ratio=decrease:flags=neighbor,pad=640:360:(ow-iw)/2:(oh-ih)/2:color=0x111319',
          '-frames:v',str(n),'-c:v','libx264','-threads','1','-g','24','-preset','ultrafast','-crf','18','-pix_fmt','yuv420p',str(dest)]
    subprocess.run(cmd,check=True);clips.append(dest)
listing=media/'concat.txt';listing.write_text(''.join("file '"+str(p)+"'\n" for p in clips))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(listing),'-c:v','copy','-movflags','+faststart',str(game/'monitor_montado.tmp.mp4')],check=True)
(game/'monitor_montado.tmp.mp4').replace(game/'monitor_montado.mp4')
mixed=array.array('h',voice);mixed.extend([0]*(math.ceil(end*sr)-len(mixed)))
with wave.open(str(ROOT/'assets/voz/narracao_mix.wav'),'wb') as w:
    w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(mixed.tobytes())
(ROOT/'timeline.json').write_text(json.dumps(dict(fps=FPS,frames=N,duration=end,voice_duration=vd,shots=shots),indent=2))
(ROOT/'audio.json').write_text(json.dumps(dict(**intake,frames=N,speed_changed=False,pitch_changed=False,trimmed=False,
 alignment='Provided Tracer narration, aligned with local ASR segments. Full recording preserved; guest has no additional voice and gameplay audio is muted.'),ensure_ascii=False,indent=2))
public=[{k:v for k,v in r.items()if k not in ['local_path','probe']} for r in records]
(ROOT/'source_manifest.json').write_text(json.dumps(dict(package='7 - Tracer.zip',source='User-provided Google Drive archive',files=public,
 video_derivatives=json.loads((ROOT/'renders/selected_clips.json').read_text()),images_published=list(mapping),
 editorial='Official Overwatch hero introduction, Blink and Recall demonstration. Recall shows position rewind with the original HUD; the selected footage does not demonstrate a changing health value. Viewport and censorship are authored illustrations, not a real fan project. Guest stays silent. No adult fan animation is included.',
 unused='Archive, unselected originals and personal gesture reference remain outside Git.'),ensure_ascii=False,indent=2))
print('TRACER_ASSETS_READY',N,end,flush=True)
