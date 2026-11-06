"""Build a continuous desktop story from the supplied narration and existing episode media."""
from pathlib import Path
import array, hashlib, json, math, shutil, subprocess, wave
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT=Path(__file__).resolve().parent
SERIES=ROOT.parent
REPO=next(p for p in ROOT.parents if(p/'AGENTS.md').exists())
PICS=ROOT/'assets/memes';PICS.mkdir(parents=True,exist_ok=True)
GAME=ROOT/'assets/gameplay';GAME.mkdir(exist_ok=True)
FPS=24;W,H=640,360
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def text(draw,xy,value,size=16,fill='white',anchor='mm'):
 draw.text(xy,value,font=ImageFont.truetype(font,size),fill=fill,anchor=anchor)
def smooth(v):
 v=max(0,min(1,v));return v*v*(3-2*v)
def cursor(im,x,y):
 d=ImageDraw.Draw(im);d.polygon([(x,y),(x+4,y+19),(x+9,y+13),(x+16,y+17),(x+19,y+12),(x+12,y+8),(x+19,y+4)],fill=(251,215,102),outline=(19,22,31))
records=[]
def copy(source,dest):
 source=SERIES/source;target=PICS/dest;shutil.copyfile(source,target)
 records.append(dict(source=str(source.relative_to(REPO)),prepared=dest,sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
 return target
for filename in ['call_normal.png','call_censored.png','call_removed.png']:
 copy(Path('02-tifa/assets/memes')/filename,filename)
items=[('LADY','01-lady-dimitrescu','ladytall2.jpg'),('TIFA','02-tifa','tifa_retrato.jpg'),('CHUN-LI','03-chun-li','chunli_classica.png'),('ANKHA','04-ankha','ankha_retrato.png'),('VAPOREON','05-vaporeon','vaporeon_unite.png'),('2B','06-2b','2b_retrato.jpg'),('TRACER','07-tracer','tracer_retrato.png'),('D.VA','08-dva','dva_piloto.jpg'),('MERCY','09-mercy','mercy_retrato.jpg'),('LARA','10-lara-croft','lara_classica.jpg'),('PEACH','11-peach','peach.png'),('SONIC','12-sonic','meme_anel.jpg')]
portraits=[]
for i,(name,folder,filename)in enumerate(items):
 path=copy(Path(folder)/'assets/memes'/filename,f'personagem_{i+1:02d}'+Path(filename).suffix)
 portraits.append(Image.open(path).convert('RGB'))
first=SERIES/'01-lady-dimitrescu/output/Lady_Dimitrescu_Personagens_que_a_internet_estragou_16x9.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-threads','1','-i',str(first),'-frames:v','1','-vf','scale=640:360:flags=neighbor','-threads','1',str(PICS/'entrada_lady.png')],check=True)
records.append(dict(source=str(first.relative_to(REPO)),prepared='entrada_lady.png',frame=0,description='First published Lady frame, used to motivate the handoff into that episode.'))
calls={name:ImageOps.fit(Image.open(PICS/name).convert('RGB'),(W,H),method=Image.Resampling.NEAREST)for name in ['call_normal.png','call_censored.png','call_removed.png']}
def desktop(title):
 im=Image.new('RGB',(W,H),(18,29,45));d=ImageDraw.Draw(im);d.rectangle((7,7,632,352),outline=(73,122,146),width=3);d.rectangle((10,10,629,35),fill=(43,65,93));text(d,(23,22),title,13,(224,232,228),'lm');text(d,(613,22),'X',15,(232,201,103));return im
grid=desktop('ARQUIVO DO FANDOM • 12 CASOS');d=ImageDraw.Draw(grid)
text(d,(320,61),'PERSONAGENS QUE',26,(238,207,108));text(d,(320,91),'A INTERNET ESTRAGOU',26,(238,207,108))
for i,((name,_,_),pic)in enumerate(zip(items,portraits)):
 x=22+(i%4)*150;y=116+(i//4)*75
 d.rectangle((x,y,x+143,y+68),fill=(32,44,62),outline=(66,104,127),width=1)
 art=ImageOps.contain(pic,(137,47),Image.Resampling.NEAREST);grid.paste(art,(x+(143-art.width)//2,y+3));text(d,(x+71,y+59),f'{i+1:02d}  {name}',11,(220,224,222))
grid.save(PICS/'arquivo_12.png')
roles=desktop('ARQUIVO DO FANDOM')
rolespecs=[('VILÃ',0,11.5),('HEROÍNA',1,12.8),('PRINCESA',10,13.9),('OURIÇO',11,15.0)]
def role_frame(t):
 im=roles.copy();d=ImageDraw.Draw(im);text(d,(320,70),'TEM MAIS GENTE NESSA HISTÓRIA…',22,(231,205,111))
 for i,(label,idx,at)in enumerate(rolespecs):
  if t<at:continue
  u=smooth((t-at)/.3);x=20+i*155;y=111+round(35*(1-u));d.rectangle((x,y,x+135,y+211),fill=(31,44,62),outline=(165,145,83),width=2)
  art=ImageOps.contain(portraits[idx],(127,159),Image.Resampling.NEAREST);im.paste(art,(x+(135-art.width)//2,y+6));text(d,(x+67,y+187),label,15,(240,215,147))
 return im
lady=Image.open(PICS/'entrada_lady.png').convert('RGB')
def popup(im,t):
 d=ImageDraw.Draw(im);d.rectangle((112,118,528,306),fill=(23,28,42),outline=(222,172,82),width=3);d.rectangle((115,121,525,151),fill=(101,46,60));text(d,(320,136),'ARQUIVOS DE FÃS',17,(250,223,166))
 for i in range(3):
  x=134+i*125;d.rectangle((x,171,x+106,257),fill=(4,7,13),outline=(76,91,112),width=2);text(d,(x+53,213),'OCULTO',13,(229,192,112))
 text(d,(320,283),'PRÉVIAS OCULTAS',14,(201,207,215))
def feed(t):
 if t<6.4:im=calls['call_normal.png'].copy();cursor(im,580,285)
 elif t<7.7:im=calls['call_censored.png'].copy();cursor(im,580,285)
 elif t<11.5:im=calls['call_removed.png'].copy();cursor(im,591,319)
 elif t<16.9:im=role_frame(t)
 elif t<27.5:
  im=grid.copy()
  if 22.0<=t<24.5:popup(im,t)
  if 24.5<=t<26.9:
   # One unwanted folder travels to the bin; the archive remains in place.
   u=smooth((t-24.5)/1.4);x=round(460+u*119);y=round(158+u*134);d=ImageDraw.Draw(im);d.rectangle((569,285,606,326),fill=(99,109,118),outline=(217,219,207),width=2);d.rectangle((565,278,610,285),fill=(160,168,165))
   if u<1:d.rectangle((x-31,y-16,x+31,y+18),fill=(225,181,74));text(d,(x,y+1),'IDEIAS',11,(40,35,36));cursor(im,x+17,y+9)
  else:cursor(im,91,150)
 else:
  u=smooth((t-27.5)/3.8);im=grid.copy();d=ImageDraw.Draw(im);d.rectangle((20,114,166,185),outline=(252,213,84),width=4)
  if t<28.15:cursor(im,99,152)
  else:
   inset=round(42*(1-u));ww=W-2*inset;hh=H-2*inset;art=lady.resize((ww,hh),Image.Resampling.NEAREST);im.paste(art,(inset,inset))
 return im
with wave.open(str(ROOT/'assets/voz/narracao_completa.wav'))as w:sr=w.getframerate();voice=array.array('h',w.readframes(w.getnframes()))
vd=len(voice)/sr;N=math.ceil((vd+.65)*FPS);end=N/FPS
cmd=['ffmpeg','-v','error','-y','-filter_threads','1','-f','rawvideo','-pixel_format','rgb24','-video_size','640x360','-framerate','24','-i','pipe:0','-an','-frames:v',str(N),'-c:v','libx264','-threads','2','-preset','ultrafast','-crf','18','-g','24','-pix_fmt','yuv420p',str(GAME/'monitor_montado.mp4')]
proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
for f in range(N):proc.stdin.write(feed(f/FPS).tobytes())
proc.stdin.close();assert proc.wait()==0
for t in [2,7,9,12.5,15.8,18,23,25.5,28,31.5]:feed(t).save(ROOT/f'renders/feed_{round(t*24):04d}.png')
mix=array.array('h',voice);mix.extend([0]*(math.ceil(end*sr)-len(mix)))
with wave.open(str(ROOT/'assets/voz/narracao_mix.wav'),'wb')as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(mix.tobytes())
shots=[dict(id=0,start=1,end=204,kind='interface',source='monitor_montado.mp4',description='Single illustrated meeting; interruption and removal are states of the same interface.'),dict(id=1,start=205,end=767,kind='actor',source='monitor_montado.mp4',description='Continuous pullback to the presenter, archive action and push into case 01.'),dict(id=2,start=768,end=N,kind='handoff',source='entrada_lady.png',description='Motivated match into the first Lady frame; no audio from that episode is added.')]
(ROOT/'timeline.json').write_text(json.dumps(dict(fps=FPS,frames=N,duration=end,voice_duration=vd,format='16:9 only',picture_cuts=2,shots=shots),indent=2))
(ROOT/'screen_cues.json').write_text(json.dumps(dict(meeting=[0,6.4],interrupted=[6.4,7.7],removed=[7.7,11.5],roles=rolespecs,archive=[16.9,27.5],hidden_previews=[22,24.5],bin=[24.5,26.9],lady_selection=[27.5,31.9],title_overlay=[17.2,21.2]),indent=2))
meta=ROOT/'renders/audio_intake.json'
if not meta.exists():meta=ROOT/'audio.json'
intake={k:v for k,v in json.loads(meta.read_text()).items()if k in ['original_filename','public_filename','sha256','voice_duration']}
(ROOT/'audio.json').write_text(json.dumps(dict(**intake,frames=N,speed_changed=False,pitch_changed=False,trimmed=False,alignment='Supplied intro aligned by phrase. Full original voice; no added speech or episode audio.'),indent=2))
(ROOT/'source_manifest.json').write_text(json.dumps(dict(voice=intake,reused=records,editorial='The illustrated Tifa meeting is labelled ENCENAÇÃO in the reused artwork. Normal portraits form one coherent case archive. Adult-content references use wholly opaque authored previews. The unwanted IDEIAS folder has one move to the bin. The final Lady still is a handoff into case 01, not a new excerpt of its narration. No original episode was changed; no 9:16 export or full compilation is produced.'),ensure_ascii=False,indent=2))
print('INTRO_ASSETS_READY',N,end,flush=True)
