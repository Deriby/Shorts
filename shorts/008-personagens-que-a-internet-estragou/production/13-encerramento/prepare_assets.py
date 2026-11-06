"""Prepare the supplied closing voice and one coherent archive-to-farewell interface."""
from pathlib import Path
import array,hashlib,json,math,shutil,subprocess,wave
from PIL import Image,ImageDraw,ImageFont,ImageOps
ROOT=Path(__file__).resolve().parent;REPO=next(p for p in ROOT.parents if(p/'AGENTS.md').exists());SERIES=ROOT.parent
PICS=ROOT/'assets/memes';PICS.mkdir(parents=True,exist_ok=True);GAME=ROOT/'assets/gameplay';GAME.mkdir(exist_ok=True)
W,H,FPS=640,360,24;font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def text(d,xy,value,size=20,fill='white',anchor='mm'):d.text(xy,value,font=ImageFont.truetype(font,size),fill=fill,anchor=anchor)
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
def cursor(im,x,y):ImageDraw.Draw(im).polygon([(x,y),(x+4,y+18),(x+9,y+12),(x+16,y+16),(x+19,y+11),(x+12,y+7),(x+19,y+3)],fill=(248,211,99),outline=(12,18,27))
sources=[]
def copy(src,dest):
 src=REPO/src;shutil.copyfile(src,PICS/dest);sources.append(dict(source=str(src.relative_to(REPO)),prepared=dest,sha256=hashlib.sha256(src.read_bytes()).hexdigest()))
copy(Path('shorts/008-personagens-que-a-internet-estragou/production/00-intro/assets/memes/arquivo_12.png'),'arquivo_12.png')
copy(Path('assets/marca/massacote-games/logo.png'),'logo.png')
archive=Image.open(PICS/'arquivo_12.png').convert('RGB');logo=Image.open(PICS/'logo.png').convert('RGBA');box=logo.getbbox()
if box:logo=logo.crop(box)
brand=Image.new('RGB',(W,H),(18,22,30));mark=logo.copy();mark.thumbnail((184,170),Image.Resampling.NEAREST);brand.paste(mark,((W-mark.width)//2,49),mark)
draw=ImageDraw.Draw(brand);text(draw,(W//2,254),'MASSACOTE GAMES',28,(242,198,65));text(draw,(W//2,301),'VALEU POR ASSISTIR!',16,(221,227,228));brand.save(PICS/'marca_final.png')
def panel(title):
 im=Image.new('RGB',(W,H),(18,30,47));d=ImageDraw.Draw(im);d.rectangle((8,8,W-9,H-9),outline=(70,126,150),width=3);d.rectangle((11,11,W-12,39),fill=(44,68,96));text(d,(24,25),title,14,(226,230,223),'lm');return im
def feed(t):
 if t<6.2:
  im=archive.copy();d=ImageDraw.Draw(im)
  u=smooth((t-2.4)/.3);yy=round(151-20*(1-u));d.rectangle((105,yy,535,yy+101),fill=(21,38,47),outline=(230,191,79),width=4)
  text(d,(320,yy+36),'MISSÃO CONCLUÍDA',29,(238,204,106));text(d,(320,yy+75),'12 CASOS ENCERRADOS',17,(199,223,212))
 elif t<9.7:
  im=panel('PRÓXIMOS CASOS');d=ImageDraw.Draw(im);text(d,(320,86),'QUEM FALTOU?',32,(237,205,110))
  for i,(name,at)in enumerate([('SUGESTÕES',6.2),('MAIS NOMES',7.2),('CONTINUA…',8.2)]):
   if t<at:continue
   u=smooth((t-at)/.25);x=round(42+i*193+40*(1-u));y=152;d.rectangle((x,y,x+158,y+103),fill=(209,165,66));d.rectangle((x,y-15,x+65,y),fill=(209,165,66));text(d,(x+79,y+53),name,15,(31,38,49))
  text(d,(320,308),'MANDA NOS COMENTÁRIOS',20,(206,220,227));cursor(im,481,284)
 elif t<15.0:
  im=panel('AJUDE O CANAL');d=ImageDraw.Draw(im);text(d,(320,84),'MASSACOTE GAMES',29,(239,205,108))
  labels=['COMENTAR','INSCREVER','CURTIR'];active=1 if t<12.2 else 2
  for i,label in enumerate(labels):
   x=28+i*207;d.rectangle((x,143,x+186,238),fill=(69,97,122)if active==i else(32,48,67),outline=(237,199,91)if active==i else(74,122,144),width=3);text(d,(x+93,190),label,21,(239,223,173)if active==i else(182,204,215))
  cursor(im,28+active*207+164,223)
 else:im=brand.copy()
 return im
with wave.open(str(ROOT/'assets/voz/narracao_completa.wav'))as w:sr=w.getframerate();voice=array.array('h',w.readframes(w.getnframes()))
vd=len(voice)/sr;N=math.ceil((vd+1.25)*FPS);actor_end=math.ceil((vd+.15)*FPS);end=N/FPS
cmd=['ffmpeg','-v','error','-y','-filter_threads','1','-f','rawvideo','-pixel_format','rgb24','-video_size','640x360','-framerate','24','-i','pipe:0','-an','-frames:v',str(N),'-c:v','libx264','-threads','2','-preset','ultrafast','-crf','18','-g','24','-pix_fmt','yuv420p',str(GAME/'monitor_montado.mp4')]
proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
for f in range(N):proc.stdin.write(feed(f/FPS).tobytes())
proc.stdin.close();assert proc.wait()==0
for t in [1,4,7,8.7,11,13.5,17]:feed(t).save(ROOT/f'renders/feed_{round(t*24):04d}.png')
mixed=array.array('h',voice);mixed.extend([0]*(math.ceil(end*sr)-len(mixed)))
with wave.open(str(ROOT/'assets/voz/narracao_mix.wav'),'wb')as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(mixed.tobytes())
meta=ROOT/'renders/audio_intake.json'
if not meta.exists():meta=ROOT/'audio.json'
intake={k:v for k,v in json.loads(meta.read_text()).items()if k in ['original_filename','public_filename','sha256','voice_duration']}
(ROOT/'audio.json').write_text(json.dumps(dict(**intake,frames=N,speed_changed=False,pitch_changed=False,trimmed=False,alignment='User-revised closing voice, preserved completely, including the recorded farewell and kiss. No added voice or sound effects.'),indent=2))
shots=[dict(id=0,start=1,end=actor_end,kind='actor',source='monitor_montado.mp4',description='One sustained room shot: conclude cases, invite suggestions, support the channel and wave goodbye.'),dict(id=1,start=actor_end+1,end=N,kind='brand',source='marca_final.png',description='Approved M logo after the complete recorded farewell.')]
(ROOT/'timeline.json').write_text(json.dumps(dict(fps=FPS,frames=N,duration=end,voice_duration=vd,format='16:9 only',picture_cuts=1,shots=shots),indent=2))
(ROOT/'screen_cues.json').write_text(json.dumps(dict(completed_cases=[0,6.2],suggestions=[6.2,9.7],support=[9.7,15.0],brand_from=15.0,wave=[15.0,19.7],wink=[17.65,17.9],heart=[17.65,18.45]),indent=2))
(ROOT/'source_manifest.json').write_text(json.dumps(dict(voice=intake,reused=sources,editorial='The user replaced the previous proposed closing; the uploaded recording governs the animation. No history-deletion joke is reused. The quoted internet phrase is treated as a comic conclusion, with no weapon or literal shooting. More folders illustrate the colloquial trocentos without a fake statistical count. Support buttons are authored invitations, not real platform interactions. The approved M is reused for the final card; no portrait, episode or intro is altered.'),ensure_ascii=False,indent=2))
print('OUTRO_ASSETS_READY',N,end,'ACTOR_FRAMES',actor_end,flush=True)
