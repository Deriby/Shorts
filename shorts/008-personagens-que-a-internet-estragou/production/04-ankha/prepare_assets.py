"""Prepare inspected user media, museum labels and authored nonexplicit interfaces."""
from pathlib import Path
import json,subprocess,math,wave,array
from PIL import Image,ImageDraw,ImageFont,ImageOps
ROOT=Path(__file__).resolve().parent;FPS=24
records=json.loads((ROOT/'renders/package_inventory.json').read_text());raw={r['original_filename']:Path(r['local_path'])for r in records};intake=json.loads((ROOT/'renders/audio_intake.json').read_text())
pics=ROOT/'assets/memes';game=ROOT/'assets/gameplay';pics.mkdir(parents=True,exist_ok=True);game.mkdir(parents=True,exist_ok=True)
mapping={'ankha-animal-crossing-j7a4sajfshlbtr9z.jpg':'ankha_retrato.png','Ankha-from-Animal-Crossing.png':'ankha_egito.png','1068689ef8ade0a6f391e4b54bcdf843.jpg':'meme_farao.jpg','Screenshot_2.png':'meme_sabem.png','images (1).jpg':'meme_fogo.jpg'}
for src,dest in mapping.items():
 im=Image.open(raw[src]).convert('RGB');im.thumbnail((1280,1280),Image.Resampling.NEAREST);im.save(pics/dest)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def text(d,xy,value,size=20,fill='white',anchor='mm'):d.text(xy,value,font=ImageFont.truetype(font,size),fill=fill,anchor=anchor)
poster=Image.new('RGB',(384,512),(238,219,165));pic=ImageOps.contain(Image.open(pics/'ankha_retrato.png'),(352,367),Image.Resampling.NEAREST);poster.paste(pic,((384-pic.width)//2,20+(367-pic.height)//2));d=ImageDraw.Draw(poster);text(d,(192,414),'ANKHA',44,(45,40,30));text(d,(192,473),'ANIMAL CROSSING',19,(75,64,39));poster.save(pics/'exhibit_ankha.png')
cassette=Image.new('RGB',(640,400),(41,44,44));d=ImageDraw.Draw(cassette);d.rectangle((14,14,625,385),outline=(187,166,104),width=8);d.rectangle((34,34,605,236),fill=(235,211,145));text(d,(320,85),'CAMEL BY CAMEL',39,(34,39,37));text(d,(320,146),'SANDY MARTON',27,(63,64,49));d.rounded_rectangle((107,181,533,278),radius=24,fill=(23,28,29))
for x in [175,465]:d.ellipse((x-36,190,x+36,262),fill=(182,179,160));d.ellipse((x-13,213,x+13,239),fill=(29,35,35))
text(d,(320,337),'LADO A',22,(234,214,162));cassette.save(pics/'cassette_label.png')
for vertical in [False,True]:
 W,H=(360,640)if vertical else(640,360);suffix='_vertical'if vertical else''
 for state in ['gallery','search','closed','doublekill']:
  im=Image.new('RGB',(W,H),(27,32,39));d=ImageDraw.Draw(im)
  if state=='doublekill':
   text(d,(W//2,45 if not vertical else 55),'DOUBLE KILL',37 if not vertical else 31,(255,212,53));areas=[(20,100,300,305),(340,100,620,305)]if not vertical else[(45,115,315,335),(30,365,330,585)]
   for image,area in zip([poster,cassette],areas):
    p=ImageOps.contain(image,(area[2]-area[0],area[3]-area[1]),Image.Resampling.NEAREST);im.paste(p,(area[0]+(area[2]-area[0]-p.width)//2,area[1]+(area[3]-area[1]-p.height)//2))
  else:
   d.rectangle((7,7,W-8,H-8),outline=(171,179,179),width=3);d.rectangle((12,12,W-13,47),fill=(63,75,87));text(d,(22,30),'ARQUIVO DA INTERNET',14,anchor='lm')
   if state=='gallery':
    boxes=[(25,76,305,283),(335,76,615,283)]if not vertical else[(25,95,335,285),(25,315,335,505)]
    for b in boxes:d.rectangle(b,fill=(6,9,13),outline=(195,173,69),width=2);text(d,((b[0]+b[2])//2,(b[1]+b[3])//2),'CENSURADO',25,(247,210,53))
   elif state=='search':
    text(d,(W//2,96 if not vertical else 140),'PESQUISA',27,(226,222,201));b=(30,133,W-30,242)if not vertical else(25,205,W-25,435);d.rectangle(b,fill=(9,12,16));text(d,(W//2,(b[1]+b[3])//2),'PRÉVIAS OCULTAS',20,(189,195,199))
   else:text(d,(W//2,H//2-20),'JANELA FECHADA',25,(194,209,195))
   y=H-75
   for x0,x1,label in [(25,W//2-10,'ABRIR'),(W//2+10,W-25,'FECHAR')]:
    color=(221,186,51)if(state=='search'and label=='ABRIR')or(state=='closed'and label=='FECHAR')else(82,90,94);d.rectangle((x0,y,x1,y+42),fill=color);text(d,((x0+x1)//2,y+21),label,17,(21,25,27)if color[0]>100 else'white')
  im.save(pics/f'{state}{suffix}.png')
seal=Image.new('RGBA',(512,116),(0,0,0,0));d=ImageDraw.Draw(seal);d.rounded_rectangle((5,5,506,110),radius=10,fill=(240,215,150,255),outline=(53,113,67,255),width=8);text(d,(256,58),'PERDOADO',58,(41,102,58));seal.save(pics/'perdoado.png')
with wave.open(str(ROOT/'assets/voz/narracao_completa.wav'))as w:sr=w.getframerate();voice=array.array('h',w.readframes(w.getnframes()))
vd=len(voice)/sr;N=math.ceil((vd+.65)*FPS);end=N/FPS
specs=[(0,2.1,'monitor','name','ankha_ilha.mp4',0),(2.1,3.8,'actor','present','ankha_ilha.mp4',2),(3.8,5.1,'photo','gallery','gallery.png',0),(5.1,7.72,'actor','sigh','gallery.png',0),(7.72,9.8,'photo','egypt','ankha_egito.png',0),(9.8,12.3,'game','island','ankha_ilha.mp4',4.2),(12.3,14.36,'museum','introduce','exhibit_ankha.png',0),(14.36,16.2,'photo','gallery','gallery.png',0),(16.2,17.4,'photo','meme','meme_farao.jpg',0),(17.4,19.96,'museum','explain','exhibit_ankha.png',0),(19.96,21.8,'museum','cassette','cassette_label.png',0),(21.8,23.0,'game','song','camel_cover.mp4',2),(23.0,25.0,'museum','doublekill','doublekill.png',0),(25.0,26.9,'graphic','doublekill','doublekill.png',0),(26.9,29.62,'museum','laugh','doublekill.png',0),(29.62,31.35,'photo','meme','meme_sabem.png',0),(31.35,32.6,'photo','meme','meme_fogo.jpg',0),(32.6,33.9,'photo','gallery','gallery.png',0),(33.9,35.9,'photo','search','search.png',0),(35.9,39.2,'actor','warning','closed.png',0),(39.2,41.8,'museum','relax','exhibit_ankha.png',0),(41.8,end,'museum','forgive','cassette_label.png',0)]
shots=[dict(id=i,start=round(t0*FPS)+1,end=round(t1*FPS),kind=k,mood=m,source=src,source_start=at)for i,(t0,t1,k,m,src,at)in enumerate(specs)];shots[-1]['end']=N;assert all(a['end']+1==b['start']for a,b in zip(shots,shots[1:]))
media=ROOT/'renders/media';media.mkdir(exist_ok=True);clips=[]
for sh in shots:
 src=(game if sh['source'].endswith('.mp4')else pics)/sh['source'];dest=media/f"monitor_{sh['id']:02d}.mp4";n=sh['end']-sh['start']+1;args=['ffmpeg','-v','error','-y','-threads','1','-filter_threads','1']
 args+=['-ss',str(sh['source_start']),'-i',str(src)]if src.suffix=='.mp4'else['-f','image2','-loop','1','-framerate','24','-i',str(src)]
 args+=['-an','-vf','fps=24,scale=640:360:force_original_aspect_ratio=decrease:flags=neighbor,pad=640:360:(ow-iw)/2:(oh-ih)/2:color=0x111319','-frames:v',str(n),'-c:v','libx264','-threads','1','-preset','ultrafast','-crf','18','-pix_fmt','yuv420p',str(dest)];subprocess.run(args,check=True);clips.append(dest)
listing=media/'concat.txt';listing.write_text(''.join("file '"+str(p)+"'\n"for p in clips));subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(listing),'-c:v','copy','-movflags','+faststart',str(game/'monitor_montado.tmp.mp4')],check=True);(game/'monitor_montado.tmp.mp4').replace(game/'monitor_montado.mp4')
mixed=array.array('h',voice);mixed.extend([0]*(math.ceil(end*sr)-len(mixed)))
with wave.open(str(ROOT/'assets/voz/narracao_mix.wav'),'wb')as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(mixed.tobytes())
(ROOT/'timeline.json').write_text(json.dumps(dict(fps=FPS,frames=N,duration=end,voice_duration=vd,shots=shots),indent=2))
(ROOT/'audio.json').write_text(json.dumps(dict(**intake,frames=N,speed_changed=False,pitch_changed=False,trimmed=False,alignment='Provided narration; local ASR segment timing, actual audio preserved. Source music and game audio are muted.'),ensure_ascii=False,indent=2))
public=[{k:v for k,v in r.items()if k not in ['local_path','probe']}for r in records];(ROOT/'source_manifest.json').write_text(json.dumps(dict(package='4 - Ankha.zip',source='User-provided Google Drive archive',files=public,video_derivatives=json.loads((ROOT/'renders/selected_clips.json').read_text()),images_published=list(mapping),editorial='Singing video is user-supplied fan-edited gameplay; Camel by Camel excerpt is a cover/remake. Museum, labels, censorship, search and pardon are authored illustrations. No adult animation is included.',unused='Unselected originals and archive are retained outside the repository.'),ensure_ascii=False,indent=2));print('ANKHA_ASSETS_READY',N,end,flush=True)
