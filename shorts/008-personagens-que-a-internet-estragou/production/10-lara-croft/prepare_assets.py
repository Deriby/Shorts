"""Prepare supplied Lara narration, inspected gameplay and authored retro interfaces."""
from pathlib import Path
import json, subprocess, math, wave, array
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
FPS=24
records=json.loads((ROOT/'renders/package_inventory.json').read_text())
raw={r['original_filename']:Path(r['local_path']) for r in records}
intake=json.loads((ROOT/'renders/audio_intake.json').read_text())
pics,game=ROOT/'assets/memes',ROOT/'assets/gameplay'
pics.mkdir(parents=True,exist_ok=True);game.mkdir(exist_ok=True)
mapping={'BdHt0R9.jpg':'lara_classica.jpg','137fd0450efdaebbe2a287e6bc1c39b5.jpg':'meme_rosto.jpg','mGNNxEaeKU6AJBXu.png':'meme_pensando.png'}
for src,dest in mapping.items():
 im=Image.open(raw[src]).convert('RGB');im.thumbnail((1280,1280),Image.Resampling.NEAREST);im.save(pics/dest)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def text(d,xy,value,size=20,fill='white',anchor='mm'):
 d.text(xy,value,font=ImageFont.truetype(font,size),fill=fill,anchor=anchor)
for vertical in [False,True]:
 W,H=(360,640)if vertical else(640,360);suffix='_vertical'if vertical else''
 for state in ['codigo','boato','pc_mod']:
  im=Image.new('RGB',(W,H),(22,75,73));d=ImageDraw.Draw(im)
  d.rectangle((12,50,W-13,H-40),fill=(187,188,178),outline=(222,220,204),width=4)
  d.rectangle((17,55,W-18,97),fill=(29,40,93))
  text(d,(28,76),'PC'if state=='pc_mod'else'CÓDIGO SECRETO?',22,'white','lm')
  text(d,(W-40,76),'X',23,'white')
  if state=='pc_mod':
   y=H//2-35
   d.rectangle((38,y-53,112,y-8),fill=(224,172,54));d.rectangle((38,y-62,72,y-45),fill=(224,172,54))
   text(d,(W//2,140 if vertical else 128),'Nude Raider',29,(24,29,41))
   text(d,(W//2,180 if vertical else 164),'MOD DE FÃS • PC',17,(45,53,61))
   d.rectangle((31,H//2+20,W-32,H-104),fill=(9,12,17),outline=(62,69,72),width=2)
   text(d,(W//2,(H//2+20+H-104)//2),'CENSURADO',27,(240,190,67))
   text(d,(W//2,H-72),'PRÉVIA OCULTA',17,(37,44,51))
  else:
   text(d,(W//2,H//2-25),'***  ???  ***',35,(27,36,40))
   text(d,(W//2,H//2+35),'SEGREDO DOS ANOS 90',18,(52,57,60))
   if state=='boato':
    d.rectangle((26,H//2-72,W-27,H//2+76),fill=(151,44,41),outline=(246,199,98),width=5)
    text(d,(W//2,H//2-8),'BOATO',57,(255,230,159))
    text(d,(W//2,H//2+47),'NÃO ERA CÓDIGO OFICIAL',16,(255,230,159))
  im.save(pics/f'{state}{suffix}.png')
 # Authored T-Rex warning: the supplied clips do not demonstrate the dinosaur encounter.
 im=Image.new('RGB',(W,H),(29,37,31));d=ImageDraw.Draw(im)
 y0=(H-330)//2;scale=min((W-38)/300,1)
 d.rectangle((15,15,W-16,H-16),outline=(230,178,58),width=5)
 text(d,(W//2,70 if vertical else 36),'T-REX',41,(242,190,65))
 pts=[(18,205),(80,180),(115,145),(139,102),(158,70),(244,70),(265,91),(263,123),(213,123),(206,141),(245,141),(245,156),(201,156),(191,184),(164,205),(156,248),(178,260),(134,260),(128,220),(111,220),(99,250),(116,260),(72,260),(80,208)]
 ox=W/2-150*scale;oy=H/2-160*scale
 d.polygon([(ox+x*scale,oy+y*scale)for x,y in pts],fill=(225,177,62))
 d.rectangle((ox+237*scale,oy+85*scale,ox+243*scale,oy+91*scale),fill=(29,37,31))
 text(d,(W//2,H-67 if vertical else H-37),'RECOMENDAÇÃO: CORRA',20,(242,190,65))
 im.save(pics/f'dinossauro{suffix}.png')

clipspecs=[('lara_exploracao.mp4','Tomb Raider - Kingdom',14.0,19.0,'Supplied fan-level trailer: clothed Lara exploring a stone walkway.'),
 ('lara_mecanismo.mp4','Insane Details',109.5,115.0,'Supplied classic Tomb Raider footage: Lara climbing a lattice gate, used as traversal context during the narration about puzzles.')]
derivatives={}
for dest,prefix,start,stop,description in clipspecs:
 src=next(p for n,p in raw.items()if n.startswith(prefix)and p.suffix=='.mp4')
 subprocess.run(['ffmpeg','-v','error','-y','-threads','1','-filter_threads','1','-ss',str(start),'-i',str(src),'-t',str(stop-start),'-an','-vf','fps=24,scale=960:540:flags=neighbor','-c:v','libx264','-threads','1','-g','24','-preset','ultrafast','-crf','18','-pix_fmt','yuv420p',str(game/dest)],check=True)
 derivatives[dest]=dict(original=src.name,interval=[start,stop],description=description,audio_used=False)
with wave.open(str(ROOT/'assets/voz/narracao_completa.wav'))as w:sr=w.getframerate();voice=array.array('h',w.readframes(w.getnframes()))
vd=len(voice)/sr;N=math.ceil((vd+.65)*FPS);end=N/FPS
specs=[(0,1.3,'monitor','name','lara_classica.jpg',0),
 (1.3,3.35,'actor','intro','lara_classica.jpg',0),
 (3.35,5.32,'photo','old','meme_rosto.jpg',0),
 (5.32,8.3,'game','explore','lara_exploracao.mp4',.4),
 (8.3,9.7,'game','puzzle','lara_mecanismo.mp4',1.0),
 (9.7,11.2,'photo','dino','dinossauro.png',0),
 (11.2,13.25,'actor','sarcasm','lara_classica.jpg',0),
 (13.25,15.25,'photo','meme','meme_pensando.png',0),
 (15.25,16.8,'actor','curious','codigo.png',0),
 (16.8,19.2,'photo','code','codigo.png',0),
 (19.2,21.4,'photo','expectation','lara_classica.jpg',0),
 (21.4,23.1,'graphic','debunk','boato.png',0),
 (23.1,24.9,'photo','pc','pc_mod.png',0),
 (24.9,26.5,'ruins','reveal','pc_mod.png',0),
 (26.5,28.3,'photo','censored','pc_mod.png',0),
 (28.3,29.5,'photo','meme','meme_rosto.jpg',0),
 (29.5,31.0,'ruins','annoyed','pc_mod.png',0),
 (31.0,32.2,'ruins','treasure','pc_mod.png',0),
 (32.2,34.5,'ruins','contrast','pc_mod.png',0),
 (34.5,end,'ruins','final','pc_mod.png',0)]
shots=[dict(id=i,start=round(t0*FPS)+1,end=round(t1*FPS),kind=k,mood=m,source=src,source_start=at)for i,(t0,t1,k,m,src,at)in enumerate(specs)];shots[-1]['end']=N
assert all(a['end']+1==b['start']for a,b in zip(shots,shots[1:]))
media=ROOT/'renders/media';media.mkdir(exist_ok=True);clips=[]
for sh in shots:
 src=(game if sh['source'].endswith('.mp4')else pics)/sh['source'];dest=media/f"monitor_{sh['id']:02d}.mp4";n=sh['end']-sh['start']+1
 cmd=['ffmpeg','-v','error','-y','-threads','1','-filter_threads','1']
 cmd+=['-ss',str(sh['source_start']),'-i',str(src)]if src.suffix=='.mp4'else['-f','image2','-loop','1','-framerate','24','-i',str(src)]
 cmd+=['-an','-vf','fps=24,scale=640:360:force_original_aspect_ratio=decrease:flags=neighbor,pad=640:360:(ow-iw)/2:(oh-ih)/2:color=0x111319','-frames:v',str(n),'-c:v','libx264','-threads','1','-g','24','-preset','ultrafast','-crf','18','-pix_fmt','yuv420p',str(dest)]
 subprocess.run(cmd,check=True);clips.append(dest)
listing=media/'concat.txt';listing.write_text(''.join("file '"+str(p)+"'\n"for p in clips))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(listing),'-c:v','copy','-movflags','+faststart',str(game/'monitor_montado.mp4')],check=True)
mixed=array.array('h',voice);mixed.extend([0]*(math.ceil(end*sr)-len(mixed)))
with wave.open(str(ROOT/'assets/voz/narracao_mix.wav'),'wb')as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(mixed.tobytes())
(ROOT/'timeline.json').write_text(json.dumps(dict(fps=FPS,frames=N,duration=end,voice_duration=vd,shots=shots),indent=2))
(ROOT/'audio.json').write_text(json.dumps(dict(**intake,frames=N,speed_changed=False,pitch_changed=False,trimmed=False,alignment='Supplied Lara voice aligned by phrase. Complete source audio; gameplay audio muted.'),ensure_ascii=False,indent=2))
public=[{k:v for k,v in r.items()if k not in ['local_path','probe']}for r in records]
(ROOT/'source_manifest.json').write_text(json.dumps(dict(package='10 - Lara Croft.zip',source='User-provided Google Drive archive',files=public,video_derivatives=derivatives,images_published=list(mapping),editorial='The Kingdom trailer is a fan level; the details clip shows Tomb Raider III. Both show normal clothed gameplay and are illustrative. The T-Rex warning is an authored illustration because the supplied clips do not establish a dinosaur encounter. The secret-code window is explicitly debunked; the Nude Raider folder is labelled PC and fan-made, with a fully opaque preview. No official nude code or PS1 mod demonstration is implied.',unused='Shower cinematic, torso-focused meme, modern portrait and unselected originals are not published. Raw archive, ASR and personal gesture reference remain outside Git.'),ensure_ascii=False,indent=2))
print('LARA_ASSETS_READY',N,end,flush=True)
