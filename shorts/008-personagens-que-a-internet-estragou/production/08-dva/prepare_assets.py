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
mapping={'download.jpg':'dva_meka.jpg','sVrD5CL2a9EeUXB5jJEEBJ.jpg':'dva_piloto.jpg','images.jpg':'meme_susto.jpg','l26bkvdgi4pc1.jpeg':'meme_jogador.jpg'}
for src,dest in mapping.items():
 im=Image.open(raw[src]).convert('RGB');im.thumbnail((1280,1280),Image.Resampling.NEAREST);im.save(pics/dest)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def text(d,xy,value,size=20,fill='white',anchor='mm'):
 d.text(xy,value,font=ImageFont.truetype(font,size),fill=fill,anchor=anchor)
poster=Image.new('RGB',(640,400),(28,40,52));im=ImageOps.contain(Image.open(pics/'dva_piloto.jpg'),(612,323),Image.Resampling.NEAREST);poster.paste(im,((640-im.width)//2,12));d=ImageDraw.Draw(poster);text(d,(320,368),'HANA SONG',35,(241,190,213));poster.save(pics/'piloto_poster.png')
for side,title in [('left','PROPULSÃO'),('right','COMBATE')]:
 im=Image.new('RGB',(512,320),(15,29,40));d=ImageDraw.Draw(im);d.rectangle((7,7,504,312),outline=(229,104,171),width=9);text(d,(256,50),title,32,(137,227,239));text(d,(256,100),'SISTEMA MEKA',19,(208,213,220))
 for i in range(3):
  y=146+i*43;d.rectangle((34,y,476,y+23),fill=(47,64,79));d.rectangle((38,y+4,290+i*43,y+19),fill=(94,191,209)if side=='left'else(215,102,166))
 im.save(pics/f'painel_{side}.png')
for vertical in [False,True]:
 W,H=(360,640)if vertical else(640,360);suffix='_vertical'if vertical else''
 im=Image.new('RGB',(W,H),(26,32,46));d=ImageDraw.Draw(im);d.rectangle((7,7,W-8,H-8),outline=(210,107,166),width=4);text(d,(W//2,64 if vertical else 40),'D.VA / HANA SONG',26,(241,197,220));p=ImageOps.contain(Image.open(pics/'dva_meka.jpg'),(W-28,330 if vertical else 214),Image.Resampling.NEAREST);im.paste(p,((W-p.width)//2,141 if vertical else 69));text(d,(W//2,H-106 if vertical else H-57),'GAMER • PILOTO MEKA',20,(153,222,235));text(d,(W//2,H-57 if vertical else H-25),'COREIA DO SUL',19,(231,215,168));im.save(pics/f'perfil{suffix}.png')
 im=Image.new('RGB',(W,H),(24,30,43));d=ImageDraw.Draw(im);d.rectangle((8,8,W-9,H-9),outline=(112,194,214),width=4);text(d,(W//2,65 if vertical else 43),'ARQUIVO DOS FÃS',24,(229,179,206));b=(27,145,W-27,H-112)if vertical else(44,100,W-44,H-58);d.rectangle(b,fill=(4,7,12),outline=(221,109,175),width=4);text(d,(W//2,(b[1]+b[3])//2),'CENSURADO',32,(241,203,74));text(d,(W//2,H-62 if vertical else H-29),'PRÉVIA OCULTA',18,(170,189,201));im.save(pics/f'censurado{suffix}.png')
 im=Image.new('RGB',(W,H),(22,33,46));d=ImageDraw.Draw(im);text(d,(W//2,90 if vertical else 63),'MÍSSEIS',48,(136,224,236))
 for i in range(3):
  cx=(W//2)if vertical else(140+i*180);cy=(230+i*125)if vertical else(215);d.polygon([(cx-50,cy-22),(cx+39,cy-22),(cx+69,cy),(cx+39,cy+22),(cx-50,cy+22)],fill=(188,200,201),outline=(239,225,193),width=4);d.polygon([(cx-48,cy-15),(cx-73,cy-43),(cx-59,cy-8)],fill=(228,113,172));d.polygon([(cx-48,cy+15),(cx-73,cy+43),(cx-59,cy+8)],fill=(228,113,172));d.rectangle((cx-47,cy-14,cx-30,cy+14),fill=(96,190,211));d.polygon([(cx-52,cy-12),(cx-82,cy),(cx-52,cy+12)],fill=(244,174,62))
 im.save(pics/f'misseis{suffix}.png')
with wave.open(str(ROOT/'assets/voz/narracao_completa.wav')) as w:
    sr=w.getframerate();voice=array.array('h',w.readframes(w.getnframes()))
vd=len(voice)/sr;N=math.ceil((vd+.65)*FPS);end=N/FPS
specs=[(0,1.58,'monitor','name','dva_intro.mp4',0),
 (1.58,3.8,'photo','profile','perfil.png',0),
 (3.8,5.4,'actor','present','perfil.png',0),
 (5.4,7.2,'game','hero','dva_intro.mp4',1),
 (7.2,9.34,'photo','profile','perfil.png',0),
 (9.34,10.32,'game','boosters','dva_voo.mp4',.3),
 (10.32,10.98,'photo','missiles','misseis.png',0),
 (10.98,12.1,'game','eject','dva_bomba.mp4',2),
 (12.1,14.0,'game','bomb','dva_bomba.mp4',5.5),
 (14.0,16.2,'actor','resign','dva_piloto.jpg',0),
 (16.2,18.6,'photo','pilot','dva_piloto.jpg',0),
 (18.6,20.5,'photo','pilot','dva_piloto.jpg',0),
 (20.5,21.8,'photo','censor','censurado.png',0),
 (21.8,22.6,'photo','meme','meme_susto.jpg',0),
 (22.6,23.9,'photo','censor','censurado.png',0),
 (23.9,26.36,'actor','whisper','censurado.png',0),
 (26.36,28.3,'cockpit','confident','dva_combate.mp4',0),
 (28.3,29.9,'game','combat','dva_combate.mp4',.3),
 (29.9,31.8,'cockpit','present','dva_combate.mp4',1),
 (31.8,33.7,'cockpit','anticipate','piloto_poster.png',0),
 (33.7,35.1,'cockpit','opening','piloto_poster.png',0),
 (35.1,35.8,'photo','pilot','dva_piloto.jpg',0),
 (35.8,38.1,'cockpit','knowing','piloto_poster.png',0),
 (38.1,39.5,'photo','meme','meme_jogador.jpg',0),
 (39.5,end,'cockpit','final','piloto_poster.png',0)]
shots=[dict(id=i,start=round(t0*FPS)+1,end=round(t1*FPS),kind=k,mood=m,source=src,source_start=at)
       for i,(t0,t1,k,m,src,at) in enumerate(specs)]
shots[-1]['end']=N
for sh in shots:
 if sh['id']==3:sh['crop_x']=350
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
 alignment='Provided D.Va narration, aligned with local ASR segments. Full original voice preserved; source videos muted.'),ensure_ascii=False,indent=2))
public=[{k:v for k,v in r.items()if k not in ['local_path','probe']} for r in records]
(ROOT/'source_manifest.json').write_text(json.dumps(dict(package='8 - DVa.zip',source='User-provided Google Drive archive',files=public,
 video_derivatives=json.loads((ROOT/'renders/selected_clips.json').read_text()),images_published=list(mapping),
 editorial='Normal official D.Va and MEKA footage, original Boosters and Self-Destruct, and clothed user images/memes. Missiles use an authored schematic: the legacy ability video shows Fusion Cannons, not the newer Micro Missiles ability. Cockpit movement removes panels and frame, never clothing. No adult fan animation or fabricated gameplay values are included.',
 unused='Archive, unselected originals and personal gesture reference remain outside Git.'),ensure_ascii=False,indent=2))
print('DVA_ASSETS_READY',N,end,flush=True)
