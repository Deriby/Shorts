"""Prepare inspected, nonexplicit excerpts and fictional call graphics from the supplied ZIP."""
from pathlib import Path
import json,subprocess,math,wave,array,hashlib,shutil
from PIL import Image,ImageDraw,ImageFont,ImageOps
ROOT=Path(__file__).resolve().parent;FPS=24
records=json.loads((ROOT/'renders/package_inventory.json').read_text());raw={r['original_filename']:Path(r['local_path'])for r in records}
pics=ROOT/'assets/memes';game=ROOT/'assets/gameplay'
pics.mkdir(parents=True,exist_ok=True);game.mkdir(parents=True,exist_ok=True)
for original,dest in [('Meme1.png','meme_fa.png'),('Screenshot_1.png','noticia.png'),('tifa_ffvii_Remake.jpg','tifa_retrato.jpg'),('140532-sephiroth-fictional_character-woman_warrior-costume-video_games-1366x768.jpg','tifa_cloud.jpg')]:
 Image.open(raw[original]).convert('RGB').save(pics/dest)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def text(d,xy,value,size=18,fill='white',anchor='mm'):
 d.text(xy,value,font=ImageFont.truetype(font,size),fill=fill,anchor=anchor)
def interface(state,wide=True):
 W,H=(640,360)if wide else(360,640);im=Image.new('RGB',(W,H),(23,27,35));d=ImageDraw.Draw(im)
 d.rectangle((0,0,W,35),fill=(43,48,58));text(d,(14,17),'REUNIÃO',16,anchor='lm');text(d,(W-12,17),'01 / 2022',13,(187,194,202),anchor='rm')
 # Discreet Italian colors provide context without impersonating an official broadcast.
 for i,c in enumerate([(53,135,93),(226,227,217),(186,62,59)]):d.rectangle((W-66+i*18,42,W-52+i*18,46),fill=c)
 if state=='normal':
  boxes=[(18,58,314,292),(326,58,622,171),(326,181,622,292)]if wide else[(18,60,342,304),(18,316,174,550),(186,316,342,550)]
  for j,b in enumerate(boxes):
   d.rectangle(b,fill=(49,57,66),outline=(89,98,105),width=2)
   if j==0:
    pic=ImageOps.contain(Image.open(pics/'tifa_retrato.jpg'),(b[2]-b[0]-8,b[3]-b[1]-24));im.paste(pic,(b[0]+(b[2]-b[0]-pic.width)//2,b[1]+4));d=ImageDraw.Draw(im)
   else:
    cx=(b[0]+b[2])//2;cy=(b[1]+b[3])//2-10;d.ellipse((cx-15,cy-30,cx+15,cy),fill=(141,150,155));d.rectangle((cx-27,cy+8,cx+27,cy+39),fill=(141,150,155))
   text(d,((b[0]+b[2])//2,b[3]-13),'TIFA'if j==0 else 'PARTICIPANTE',11)
 elif state=='censored':
  b=(18,62,W-18,H-67);d.rectangle(b,fill=(9,11,16),outline=(217,179,49),width=3)
  cx=W//2;cy=H//2-10;d.rectangle((cx-28,cy-70,cx+28,cy-25),outline=(225,185,45),width=5);d.arc((cx-19,cy-95,cx+19,cy-42),180,360,fill=(225,185,45),width=5)
  text(d,(cx,cy+12),'CENSURADO',29 if wide else 27,(255,214,56));text(d,(cx,cy+49),'TRANSMISSÃO INTERROMPIDA',13 if wide else 11,(166,173,182))
 elif state=='removed':
  cx=W//2;cy=H//2;d.ellipse((cx-28,cy-84,cx+28,cy-28),outline=(86,197,133),width=4);d.line((cx-14,cy-56,cx-3,cy-43,cx+16,cy-69),fill=(86,197,133),width=5)
  text(d,(cx,cy+6),'PARTICIPANTE',23,(218,224,229));text(d,(cx,cy+40),'REMOVIDO',28,(86,197,133))
 elif state=='shared':
  # Deliberately illustrative sharing cards, no invented counts or source logos.
  count=3 if wide else 2;cw,ch=(210,160)if wide else(290,175)
  for i in range(count):
   x=15+i*200 if wide else 26+i*15;y=80+i*30 if wide else 130+i*215
   d.rectangle((x+6,y+6,x+cw+6,y+ch+6),fill=(9,11,15));d.rectangle((x,y,x+cw,y+ch),fill=(48,59,62),outline=(130,153,145),width=2)
   text(d,(x+cw//2,y+24),'↪ ENCAMINHADO',13,(133,214,166));d.rectangle((x+12,y+48,x+cw-12,y+ch-13),fill=(5,7,9));text(d,(x+cw//2,y+ch//2+20),'CENSURADO',18,(251,211,54))
 d.rectangle((0,H-42,W,H),fill=(42,46,56));d.ellipse((W//2-11,H-29,W//2+11,H-7),fill=(171,59,65));text(d,(12,H-19),'●',13,(124,193,148),anchor='lm');text(d,(W-12,H-19),'ENCENAÇÃO',10,(169,178,187),anchor='rm')
 return im
for state in ['normal','censored','removed','shared']:
 for wide in [True,False]:interface(state,wide).save(pics/f'call_{state}{""if wide else"_vertical"}.png')
with wave.open(str(ROOT/'assets/voz/narracao_completa.wav'))as w:sr=w.getframerate();voice=array.array('h',w.readframes(w.getnframes()))
vd=len(voice)/sr;N=math.ceil((vd+.65)*FPS);end=N/FPS
specs=[(0,1.5,'monitor','hook','tifa_intro.mp4',0),(1.5,3.3,'actor','thoughtful','tifa_intro.mp4',1.5),(3.3,4.4,'photo','call','call_normal.png',0),(4.4,5.58,'actor','thoughtful','call_normal.png',0),(5.58,6.3,'monitor','name','tifa_intro.mp4',3.4),(6.3,7.24,'game','name','tifa_intro.mp4',4.1),(7.24,8.05,'actor','punch','tifa_fight.mp4',0),(8.05,9.5,'game','combat','tifa_fight.mp4',2.1),(9.5,10.58,'game','combat','tifa_fight.mp4',3.4),(10.58,11.95,'actor','sigh','call_censored.png',0),(11.95,13.36,'photo','fan','meme_fa.png',0),(13.36,14.95,'photo','news','noticia.png',0),(14.95,16.7,'meeting','composed','call_normal.png',0),(16.7,18.5,'meeting','interrupted','call_censored.png',0),(18.5,20.3,'photo','call','call_censored.png',0),(20.3,21.15,'meeting','shock','call_censored.png',0),(21.15,23.45,'meeting','deadpan','call_censored.png',0),(23.45,25.1,'meeting','relief','call_removed.png',0),(25.1,26.4,'photo','call','call_shared.png',0),(26.4,end,'meeting','final','call_shared.png',0)]
shots=[dict(id=i,start=round(t0*FPS)+1,end=round(t1*FPS),kind=k,mood=m,source=src,source_start=at)for i,(t0,t1,k,m,src,at)in enumerate(specs)];shots[-1]['end']=N
assert all(a['end']+1==b['start']for a,b in zip(shots,shots[1:]))
media=ROOT/'renders/media';media.mkdir(exist_ok=True);clips=[]
for sh in shots:
 src=(game if sh['source'].endswith('.mp4')else pics)/sh['source'];dest=media/f"monitor_{sh['id']:02d}.mp4";n=sh['end']-sh['start']+1
 args=['ffmpeg','-v','error','-y','-threads','1','-filter_threads','1']
 args+=['-ss',str(sh['source_start']),'-i',str(src)]if src.suffix=='.mp4'else['-f','image2','-loop','1','-framerate','24','-i',str(src)]
 args+=['-an','-vf','fps=24,scale=640:360:force_original_aspect_ratio=decrease:flags=neighbor,pad=640:360:(ow-iw)/2:(oh-ih)/2:color=0x111319','-frames:v',str(n),'-c:v','libx264','-threads','1','-preset','ultrafast','-crf','18','-pix_fmt','yuv420p',str(dest)]
 subprocess.run(args,check=True);clips.append(dest)
listing=media/'concat.txt';listing.write_text(''.join("file '"+str(p)+"'\n"for p in clips));subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(listing),'-c:v','copy','-movflags','+faststart',str(game/'monitor_montado.tmp.mp4')],check=True);(game/'monitor_montado.tmp.mp4').replace(game/'monitor_montado.mp4')
mixed=array.array('h',voice);mixed.extend([0]*(math.ceil(end*sr)-len(mixed)))
with wave.open(str(ROOT/'assets/voz/narracao_mix.wav'),'wb')as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(mixed.tobytes())
(ROOT/'timeline.json').write_text(json.dumps(dict(fps=FPS,frames=N,duration=end,voice_duration=vd,shots=shots),indent=2))
(ROOT/'audio.json').write_text(json.dumps(dict(original_filename='Voz - 2 Tifa.mp3',sha256=hashlib.sha256((ROOT/'assets/voz/voz_original.mp3').read_bytes()).hexdigest(),voice_duration_seconds=vd,frames=N,speed_changed=False,pitch_changed=False,trimmed=False,alignment='Supplied recording; local ASR segment timing and semantic shot alignment. Delivery tags are not captions.'),indent=2))
public=[{k:v for k,v in r.items()if k not in ['local_path','probe']}for r in records]
(ROOT/'source_manifest.json').write_text(json.dumps(dict(package='2 - Tifa.zip',source='User-provided Google Drive archive',files=public,video_derivatives=json.loads((ROOT/'renders/selected_clips.json').read_text()),images_published=['Meme1.png','Screenshot_1.png','tifa_ffvii_Remake.jpg','140532-sephiroth-fictional_character-woman_warrior-costume-video_games-1366x768.jpg'],omitted='Beach clip, adult-site graphic and other unused sources remain outside the repository. Call graphics are fictional nonexplicit illustrations, not the original adult transmission.'),ensure_ascii=False,indent=2))
print('TIFA_ASSETS_READY',N,end,flush=True)
