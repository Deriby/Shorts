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
mapping={'images (1).jpg':'mercy_asas.jpg','images.jpg':'mercy_retrato.jpg','42560a828594e989d123f9f3ade5ad6a.jpg':'meme_suporte.jpg','83fb716bffe2e09a3b0596415f1425de.jpg':'meme_sorriso.jpg'}
for src,dest in mapping.items():
 im=Image.open(raw[src]).convert('RGB');im.thumbnail((1280,1280),Image.Resampling.NEAREST);im.save(pics/dest)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def text(d,xy,value,size=20,fill='white',anchor='mm'):
 d.text(xy,value,font=ImageFont.truetype(font,size),fill=fill,anchor=anchor)
def heart(d,cx,cy,s,color):
 pts=[(cx,cy+s*.42),(cx-s*.48,cy-s*.08),(cx-s*.42,cy-s*.32),(cx-s*.22,cy-s*.42),(cx,cy-s*.20),(cx+s*.22,cy-s*.42),(cx+s*.42,cy-s*.32),(cx+s*.48,cy-s*.08)]
 d.polygon(pts,fill=color)
for vertical in [False,True]:
 W,H=(360,640)if vertical else(640,360);suffix='_vertical'if vertical else''
 for state in ['censurado','verbete','indeferido']:
  im=Image.new('RGB',(W,H),(226,232,214));d=ImageDraw.Draw(im);d.rectangle((8,8,W-9,H-9),outline=(58,111,117),width=5);heart(d,W//2,66 if vertical else 48,50 if vertical else 37,(56,153,170))
  if state=='censurado':
   text(d,(W//2,130 if vertical else 95),'TRIAGEM',28,(42,77,83));box=(28,198,W-28,H-110)if vertical else(55,122,W-55,H-48);d.rectangle(box,fill=(8,15,23),outline=(71,136,148),width=3);text(d,(W//2,(box[1]+box[3])//2),'CENSURADO',31,(231,190,93));text(d,(W//2,H-63 if vertical else H-26),'PRÉVIA OCULTA',18,(56,96,102))
  else:
   text(d,(W//2,124 if vertical else 86),'VERBETE',20,(74,100,100));text(d,(W//2,240 if vertical else 149),'MERCY',60 if vertical else 54,(34,73,80));d.line((30,301 if vertical else 184,W-30,301 if vertical else 184),fill=(91,137,139),width=3);text(d,(W//2,365 if vertical else 225),'MISERICÓRDIA',31 if vertical else 35,(35,87,92))
   if state=='indeferido':
    stamp=Image.new('RGBA',(590,128),(0,0,0,0));sd=ImageDraw.Draw(stamp);sd.rectangle((8,8,581,119),outline=(169,54,64,255),width=9);text(sd,(295,64),'INDEFERIDO',58,(169,54,64,255));stamp=stamp.rotate(-10,resample=Image.Resampling.NEAREST,expand=True);stamp.thumbnail((W-28,182 if vertical else 130),Image.Resampling.NEAREST);im.paste(stamp,((W-stamp.width)//2,440 if vertical else 252),stamp)
  im.save(pics/f'{state}{suffix}.png')
 im=Image.new('RGB',(W,H),(176,205,194));d=ImageDraw.Draw(im)
 for x in range(0,W,32):d.rectangle((x,0,x+15,H),fill=(186,213,201))
 for x in [4,W//3,2*W//3,W-5]:d.rectangle((x,0,x+4,H),fill=(56,105,109))
 d.rectangle((0,7,W,13),fill=(56,105,109));d.rectangle((0,H-14,W,H-8),fill=(56,105,109));heart(d,W//2,H//2,100,(54,140,153));im.save(pics/f'biombo{suffix}.png')
im=Image.new('RGB',(256,256),(224,234,217));d=ImageDraw.Draw(im);heart(d,128,128,179,(50,144,160));im.save(pics/'coracao.png')
with wave.open(str(ROOT/'assets/voz/narracao_completa.wav')) as w:
    sr=w.getframerate();voice=array.array('h',w.readframes(w.getnframes()))
vd=len(voice)/sr;N=math.ceil((vd+.65)*FPS);end=N/FPS
specs=[(0,1.3,'monitor','name','mercy_intro.mp4',0),
 (1.3,3.0,'actor','excited','mercy_intro.mp4',1.3),
 (3.0,4.2,'photo','meme','meme_sorriso.jpg',0),
 (4.2,5.12,'photo','wings','mercy_asas.jpg',0),
 (5.12,8.7,'game','heal','mercy_cura.mp4',1),
 (8.7,11.2,'game','resurrect','mercy_ressurreicao.mp4',.9),
 (11.2,13.5,'actor','explain','mercy_asas.jpg',0),
 (13.5,15.2,'photo','wings','mercy_asas.jpg',0),
 (15.2,16.35,'photo','meme','meme_suporte.jpg',0),
 (16.35,16.65,'graphic','wipe','biombo.png',0),
 (16.65,18.8,'triage','reveal','censurado.png',0),
 (18.8,20.2,'photo','censored','censurado.png',0),
 (20.2,21.5,'triage','awkward','censurado.png',0),
 (21.5,23.25,'triage','present','verbete.png',0),
 (23.25,25.4,'photo','dictionary','verbete.png',0),
 (25.4,26.15,'graphic','stamp','indeferido.png',0),
 (26.15,end,'triage','final','indeferido.png',0)]
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
 alignment='Provided Mercy narration aligned with local ASR segments. Full original voice preserved; gameplay audio muted.'),ensure_ascii=False,indent=2))
public=[{k:v for k,v in r.items()if k not in ['local_path','probe']} for r in records]
(ROOT/'source_manifest.json').write_text(json.dumps(dict(package='9 - Mercy.zip',source='User-provided Google Drive archive',files=public,
 video_derivatives=json.loads((ROOT/'renders/selected_clips.json').read_text()),images_published=list(mapping),
 editorial='Official Mercy introduction, yellow healing beam and actual Resurrect. The two supplied videos contain the same demonstration at different resolutions; the 1080p version is selected. Clinic, dictionary, opaque preview and INDEFERIDO stamp are authored fiction, not patient data or Blizzard documents. No adult fan image or animation is included.',
 unused='Archive, unselected originals and personal gesture reference remain outside Git.'),ensure_ascii=False,indent=2))
print('MERCY_ASSETS_READY',N,end,flush=True)
