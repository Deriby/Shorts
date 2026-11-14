"""Reuse approved landscape streams; create short, separately editable title cards."""
from pathlib import Path
import json,subprocess,hashlib,shutil,wave,math,concurrent.futures,io
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps
P=Path(__file__).resolve().parent;R=next(x for x in P.parents if(x/'AGENTS.md').exists());S=P.parent.parent;O=P/'output';M=O/'Filmora/midias';C=Path('/workspace/attachments/longo009');M.mkdir(parents=True,exist_ok=True);C.mkdir(exist_ok=True)
T=10000000;FPS=30;CARD=60
order=json.loads((S/'ordem_capitulos.json').read_text());chapters=sorted(order['chapters'],key=lambda x:x['order']);assert[c['order']for c in chapters]==[1,2,3,4,5,6,7,8,9,11,12]
intro=next(x for x in order['long_segments']if x['role']=='intro');outro=next(x for x in order['long_segments']if x['role']=='outro');records=[];at=0
font=R/'shorts/009-jogos-que-a-internet-tentou-cancelar/production/01-gta-san-andreas/assets/fontes/Baloo2.ttf';fonts=O/'Filmora/fontes';fonts.mkdir(exist_ok=True);shutil.copyfile(font,fonts/font.name)
license_path=font.parent/'OFL.txt'
if license_path.exists():shutil.copyfile(license_path,fonts/license_path.name)
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def block(n,title,video,prod,role):
 global at
 d=probe(video);v=next(x for x in d['streams']if x['codec_type']=='video');frames=int(v['nb_frames']);assert(v['width'],v['height'],v['r_frame_rate'])==(1920,1080,'30/1');key=f'{n:02d}_{prod.name.split("-",1)[-1].replace("-","_")}'
 folder=video.parent/'Filmora';wfp=next(folder.glob('*.wfp'));dest=M/(key+'_video_16x9.mp4')
 if not dest.exists():subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-map','0:v:0','-c:v','copy','-an','-movflags','+faststart',str(dest)],check=True)
 rec=dict(type='body',role=role,number=n,title=title,key=key,frames=frames,start=at,end=at+frames,source_video=str(video.relative_to(R)),source_sha256=digest(video),source_project=str(wfp.relative_to(R)),source_project_sha256=digest(wfp),production=str(prod.relative_to(R)),media=dest.name,source_folder=str(folder.relative_to(R)));records.append(rec);at+=frames;return rec
block(0,'Intro',S/intro['video'],S/intro['production_path'],'intro')
for ch in chapters:
 video=S/ch['deliveries']['chapter_16x9'];prod=S/ch['production_path'];n=ch['order'];key=f'{n:02d}_vinheta';i=dict(type='card',role='chapter_card',number=n,title=ch['game'],key=key,frames=CARD,start=at,end=at+CARD);records.append(i);at+=CARD
 block(n,ch['game'],video,prod,'chapter')
block(13,'Outro',S/outro['video'],S/outro['production_path'],'outro')
# Reuse the short sonic signature from the user's approved chapter transitions.
source=R/'shorts/008-personagens-que-a-internet-estragou/production/14-montagem-longo/assets/vinheta_referencia.wav'
raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(source),'-t','2','-ac','2','-ar','44100','-f','f32le','pipe:1']);audio=np.frombuffer(raw,'<f4').reshape(-1,2).copy();audio*=.20/max(np.max(np.abs(audio)),.001);audio[:1323]*=np.linspace(0,1,min(1323,len(audio)))[:,None];audio[-8820:]*=np.linspace(1,0,min(8820,len(audio)))[:,None]
with wave.open(str(M/'vinheta_2s.wav'),'wb')as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(44100);w.writeframes(np.int16(np.clip(audio,-1,1)*32767).tobytes())
logo=Image.open(R/'assets/marca/massacote-games/logo.png').convert('RGBA');logo.thumbnail((105,105),Image.Resampling.LANCZOS)
background=Image.new('RGB',(1920,1080),(18,20,29));draw=ImageDraw.Draw(background)
for x in range(-1000,2400,160):draw.polygon([(x,1080),(x+760,0),(x+820,0),(x+60,1080)],fill=(23,25,34))
draw.rectangle((0,0,15,1080),fill=(248,193,25));draw.rectangle((1090,270,1094,810),fill=(79,66,32));background.paste(logo,(92,90),logo);small=ImageFont.truetype(str(font),34);draw.text((215,118),'MASSACOTE GAMES',font=small,fill=(243,196,51));draw.text((105,950),'JOGOS QUE A INTERNET TENTOU CANCELAR',font=small,fill=(153,151,143));background.save(M/'vinheta_fundo.png')
names={1:'GTA SAN\nANDREAS',2:'BMX XXX',3:'BULLY',4:'LEFT 4 DEAD 2',5:'SAINTS ROW IV',6:'GTA V',7:'POKÉMON\nSWORD & SHIELD',8:'NIGHT TRAP',9:'DEAD OR ALIVE\nXTREME 3',11:'MINECRAFT',12:'HOUSE PARTY'}
def card(i):
 rec=next(x for x in records if x['type']=='body'and x['number']==i['number']);prod=R/rec['production'];tl=json.loads((prod/'timeline.json').read_text());shot=next((x for x in tl['shots']if x['kind']=='game'and x['source'].endswith('.mp4')),next(x for x in tl['shots']if x['source'].endswith('.mp4')));src=prod/'assets/gameplay'/shot['source'];time=shot['source_start']+.5
 image=Image.open(io.BytesIO(subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(time),'-i',str(src),'-frames:v','1','-c:v','png','-threads','1','-f','image2pipe','pipe:1']))).convert('RGB')
 covers={1:R/'shorts/009-jogos-que-a-internet-tentou-cancelar/production/01-gta-san-andreas/assets/imagens/capa_gta.png',8:R/'shorts/009-jogos-que-a-internet-tentou-cancelar/production/08-night-trap/assets/imagens/capa_mega_cd.jpg'}
 if i['number']in covers:src=covers[i['number']];time=None;image=Image.open(src).convert('RGB')
 hero=Image.new('RGBA',(1920,1080));hd=ImageDraw.Draw(hero);hd.rounded_rectangle((1166,319,1814,713),radius=13,fill=(5,6,9,255),outline=(247,196,36,255),width=5);fitted=ImageOps.contain(image,(620,360),Image.Resampling.LANCZOS);hero.paste(fitted,(1180+(620-fitted.width)//2,335+(360-fitted.height)//2));hero.save(M/(i['key']+'_imagem.png'))
 title=Image.new('RGBA',(1920,1080));d=ImageDraw.Draw(title);d.text((112,307),'PRÓXIMO JOGO',font=ImageFont.truetype(str(font),32),fill=(171,170,161));text=names[i['number']];size=142
 while True:
  f=ImageFont.truetype(str(font),size);box=d.multiline_textbbox((0,0),text,font=f,spacing=0)
  if box[2]-box[0]<930:break
  size-=2
 y=408 if '\n'in text else 442
 for depth in range(18,0,-1):d.multiline_text((112+depth,y+depth),text,font=f,spacing=0,fill=(121+depth*2,67+depth,7,255),stroke_width=3,stroke_fill=(39,27,13,255))
 d.multiline_text((112,y),text,font=f,spacing=0,fill=(255,213,47,255),stroke_width=2,stroke_fill=(255,239,143,255));title.save(M/(i['key']+'_titulo.png'))
 i.update(background='vinheta_fundo.png',hero=i['key']+'_imagem.png',title_image=i['key']+'_titulo.png',sound='vinheta_2s.wav',image_source=str(src.relative_to(R)),image_source_start=time)
 def render():
  dest=C/'vinhetas'/(i['key']+'_preview.mp4');dest.parent.mkdir(exist_ok=True);cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','pipe:0','-an','-c:v','libx264','-threads','1','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',str(dest)];p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
  for frame in range(CARD):
   t=frame/30;u=min(1,t/.24);v=min(1,t/.30);canvas=background.convert('RGBA');canvas.alpha_composite(hero,(round(77*(1-v)),0));canvas.alpha_composite(title,(round(-77*(1-u)),0));p.stdin.write(canvas.convert('RGB').tobytes())
  p.stdin.close();assert p.wait()==0
 render();i['preview']=i['key']+'_preview.mp4';print('CARD_READY',i['title'],flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:list(pool.map(card,[x for x in records if x['type']=='card']))
plan=dict(title='Jogos que a internet tentou cancelar',fps=30,frames=at,duration=at/30,resolution=[1920,1080],game_count=len(chapters),card_frames=CARD,omitted=[10],records=records,existing_3d_renders_reused=True,source_voice_intact=True,source_sting=str(source.relative_to(R)),source_sting_sha256=digest(source));(P/'montagem.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n');print('LONG_ASSETS_READY',at/30,flush=True)
