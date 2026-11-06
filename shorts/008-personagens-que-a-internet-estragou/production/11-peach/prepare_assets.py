"""Prepare supplied Peach narration, inspected gameplay and authored retro interfaces."""
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
mapping={'images.jpg':'meme_peach.jpg','maxresdefault.jpg':'meme_serio.jpg','princess_peach_absolute_meme_by_joaogvds3221_dmidyno-pre.jpg':'meme_cinema.jpg'}
for src,dest in mapping.items():
 im=Image.open(raw[src]).convert('RGB');im.thumbnail((1280,1280),Image.Resampling.NEAREST);im.save(pics/dest)
pair=Image.open(raw['peach-bowser-bowsette.jpg']).convert('RGB')
pair.crop((0,0,550,540)).save(pics/'peach.png');pair.crop((600,0,1210,540)).save(pics/'bowser.png')
Image.open(raw['images (1).jpg']).convert('RGB').crop((0,25,245,295)).save(pics/'bowsette.png')
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def text(d,xy,value,size=20,fill='white',anchor='mm'):
 d.text(xy,value,font=ImageFont.truetype(font,size),fill=fill,anchor=anchor)
def crown(d,cx,cy,size):
 pts=[(-.48,.25),(-.58,-.38),(-.22,-.13),(0,-.52),(.22,-.13),(.58,-.38),(.48,.25)]
 d.polygon([(cx+x*size,cy+y*size)for x,y in pts],fill=(236,178,52),outline=(255,220,112))
 d.ellipse((cx-8,cy-12,cx+8,cy+8),fill=(225,76,133))
for vertical in [False,True]:
 W,H=(360,640)if vertical else(640,360);suffix='_vertical'if vertical else''
 for state in ['tenis','kart','galeria','oficial_a','oficial_b','bowser_card','bowsette_card','bowsette_censurada']:
  im=Image.new('RGB',(W,H),(38,24,57));d=ImageDraw.Draw(im);d.rectangle((8,8,W-9,H-9),outline=(218,162,66),width=4)
  if state in ['tenis','kart']:
   text(d,(W//2,64 if vertical else 35),'SELEÇÃO DE JOGO',21,(245,202,220))
   hero=Image.open(pics/'peach.png').convert('RGB');hero.thumbnail((270,264)if vertical else(230,230),Image.Resampling.NEAREST)
   im.paste(hero,((W-hero.width)//2 if vertical else 38,120 if vertical else 76))
   cx,cy=(W//2,465)if vertical else(450,150)
   if state=='tenis':
    d.ellipse((cx-46,cy-52,cx+22,cy+21),outline=(239,215,131),width=6)
    for v in [-22,-8,6]:d.line((cx+v,cy-44,cx+v,cy+13),fill=(174,204,155),width=2)
    d.line((cx-12,cy+21,cx+16,cy+61),fill=(221,93,149),width=10);d.ellipse((cx+39,cy-15,cx+61,cy+7),fill=(192,223,87))
   else:
    d.ellipse((cx-49,cy-49,cx+49,cy+49),outline=(231,220,198),width=10)
    for xx,yy in [(-40,-10),(40,-10),(0,44)]:d.line((cx,cy,cx+xx,cy+yy),fill=(231,220,198),width=8)
    d.ellipse((cx-14,cy-14,cx+14,cy+14),fill=(221,93,149))
   text(d,(W//2,H-73)if vertical else(450,268),'TÊNIS'if state=='tenis'else'KART',37,(245,205,104))
  elif state in ['galeria','bowsette_censurada']:
   text(d,(W//2,70 if vertical else 40),'ARQUIVOS DE FÃS',27,(242,199,218))
   title='BOWSETTE'if state=='bowsette_censurada'else'FANARTS / ANIMAÇÕES'
   text(d,(W//2,126 if vertical else 85),title,23,(239,194,83))
   bounds=(26,185,W-27,H-110)if vertical else(42,118,W-43,H-65)
   d.rectangle(bounds,fill=(7,9,15),outline=(168,111,149),width=3)
   text(d,(W//2,(bounds[1]+bounds[3])//2),'CENSURADO',30,(239,194,83))
   text(d,(W//2,H-66 if vertical else H-34),'CRIAÇÃO DE FÃS',19,(241,195,218))
  elif state.startswith('oficial'):
   text(d,(W//2,57 if vertical else 30),'NO JOGO',22,(238,198,217));text(d,(W//2,91 if vertical else 60),'DIVULGAÇÃO • 2018',16,(237,193,88))
   crown(d,W//2,205 if vertical else 123,105 if vertical else 70)
   text(d,(W//2,270 if vertical else 180),'SUPER COROA',24,(240,196,84))
   active=state=='oficial_a'
   boxes=[(30,323,W-30,392),(30,464,W-30,533)]if vertical else[(26,219,271,285),(369,219,614,285)]
   for i,(box,label)in enumerate(zip(boxes,['TOADETTE','PEACHETTE'])):
    d.rectangle(box,fill=(168,62,119)if(i==0)==active else(80,49,83),outline=(246,202,216),width=2)
    text(d,((box[0]+box[2])//2,(box[1]+box[3])//2),label,27,(255,225,236))
   if vertical:d.polygon([(W//2-6,409),(W//2+6,409),(W//2+6,431),(W//2+19,431),(W//2,451),(W//2-19,431),(W//2-6,431)],fill=(237,193,88))
   else:d.polygon([(288,245),(326,245),(326,234),(351,252),(326,270),(326,259),(288,259)],fill=(237,193,88))
  else:
   fan=state=='bowsette_card';pic=Image.open(pics/('bowsette.png'if fan else'bowser.png')).convert('RGB');pic.thumbnail((290,330)if vertical else(235,235),Image.Resampling.NEAREST)
   im.paste(pic,((W-pic.width)//2 if vertical else 34,120 if vertical else 74))
   text(d,(W//2,62)if vertical else(446,80),'CRIAÇÃO DE FÃS'if fan else'NO JOGO',23 if vertical else 18,(240,197,88))
   text(d,(W//2,507)if vertical else(447,168),'BOWSETTE'if fan else'BOWSER',38 if vertical else 30,(255,217,233))
   if fan:text(d,(W//2,561)if vertical else(447,230),'VERSÃO NÃO OFICIAL',16,(220,176,200))
  im.save(pics/f'{state}{suffix}.png')
clipspecs=[('peach_luta.mp4','Princess Peach; Showtime! —',80.5,84.0,'Official Princess Peach Showtime: Kung Fu Peach fighting stage enemies, not Bowser.'),
 ('bowsette_fan.mp4','Super Smash Bros.',54.3,58.2,'User-supplied fan-made Bowsette showcase in Smash; not an official Nintendo announcement.')]
derivatives={}
for dest,prefix,start,stop,description in clipspecs:
 src=next(p for n,p in raw.items()if n.startswith(prefix)and p.suffix=='.mp4')
 subprocess.run(['ffmpeg','-v','error','-y','-threads','1','-filter_threads','1','-ss',str(start),'-i',str(src),'-t',str(stop-start),'-an','-vf','fps=24,scale=960:540:flags=neighbor','-c:v','libx264','-threads','1','-g','24','-preset','ultrafast','-crf','18','-pix_fmt','yuv420p',str(game/dest)],check=True)
 derivatives[dest]=dict(original=src.name,interval=[start,stop],description=description,audio_used=False)
with wave.open(str(ROOT/'assets/voz/narracao_completa.wav'))as w:sr=w.getframerate();voice=array.array('h',w.readframes(w.getnframes()))
vd=len(voice)/sr;N=math.ceil((vd+.65)*FPS);end=N/FPS
specs=[(0,1.2,'monitor','name','peach.png',0),
 (1.2,2.25,'actor','present','peach.png',0),
 (2.25,3.3,'photo','tennis','tenis.png',0),
 (3.3,4.3,'photo','kart','kart.png',0),
 (4.3,5.8,'game','fight','peach_luta.mp4',.6),
 (5.8,6.65,'photo','bowser','bowser_card.png',0),
 (6.65,8.65,'actor','aside','galeria.png',0),
 (8.65,10.0,'photo','meme','meme_peach.jpg',0),
 (10.0,12.6,'photo','gallery','galeria.png',0),
 (12.6,14.0,'actor','sarcasm','galeria.png',0),
 (14.0,16.3,'photo','meme','meme_serio.jpg',0),
 (16.3,17.6,'photo','bowser','bowser_card.png',0),
 (17.6,19.2,'showcase','reveal','bowser_card.png',0),
 (19.2,20.7,'showcase','crown','oficial_a.png',0),
 (20.7,23.1,'photo','official','oficial_a.png',0),
 (23.1,25.2,'photo','official','oficial_b.png',0),
 (25.2,27.4,'showcase','fans','bowser_card.png',0),
 (27.4,29.2,'game','fan_game','bowsette_fan.mp4',.2),
 (29.2,30.4,'photo','fan','bowsette_card.png',0),
 (30.4,33.0,'photo','censored','bowsette_censurada.png',0),
 (33.0,34.1,'showcase','reaction','bowsette_card.png',0),
 (34.1,34.85,'photo','bowser','bowser_card.png',0),
 (34.85,end,'showcase','laugh','bowser_card.png',0)]
shots=[dict(id=i,start=round(t0*FPS)+1,end=round(t1*FPS),kind=k,mood=m,source=src,source_start=at)for i,(t0,t1,k,m,src,at)in enumerate(specs)];shots[-1]['end']=N
for sh in shots:
 if sh['mood']=='fan_game':sh['crop_x']='max(360,480-130*t)';sh['fan_badge']=True
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
(ROOT/'audio.json').write_text(json.dumps(dict(**intake,frames=N,speed_changed=False,pitch_changed=False,trimmed=False,alignment='Supplied Peach voice aligned by phrase. Complete source audio; gameplay audio muted.'),ensure_ascii=False,indent=2))
public=[{k:v for k,v in r.items()if k not in ['local_path','probe']}for r in records]
(ROOT/'source_manifest.json').write_text(json.dumps(dict(package='11 - Peach.zip',source='User-provided Google Drive archive',files=public,video_derivatives=derivatives,images_published=list(mapping)+['peach-bowser-bowsette.jpg','images (1).jpg'],editorial='Official Showtime footage illustrates Peach fighting stage enemies; Bowser is identified separately. Tennis and kart use authored game-selection cards because the package contains no such gameplay. The 2018 Super Crown transformation is illustrated with correctly named TOADETTE to PEACHETTE diagrams; the package contains no official transformation footage. Bowsette is consistently labelled fan-made, distinct from Peach and Peachette. Supplied Smash Bowsette footage is fan-made, not an official announcement. Adult-content references use wholly opaque authored cards. Crops of supplied portraits focus on faces.',unused='AI Peach portrait, fan-song animation, the Rosalina animation and unselected originals remain outside Git. Raw archive, ASR and personal gesture reference are not published.' ),ensure_ascii=False,indent=2))
print('PEACH_ASSETS_READY',N,end,flush=True)
