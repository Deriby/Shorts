"""Prepare the supplied recording, inspected media and authored inspection graphics."""
from pathlib import Path
import json,subprocess,math,wave,array,hashlib
from PIL import Image,ImageDraw,ImageFont,ImageOps
ROOT=Path(__file__).resolve().parent;FPS=24
records=json.loads((ROOT/'renders/package_inventory.json').read_text());raw={r['original_filename']:Path(r['local_path'])for r in records}
pics=ROOT/'assets/memes';game=ROOT/'assets/gameplay';pics.mkdir(parents=True,exist_ok=True);game.mkdir(parents=True,exist_ok=True)
for original,dest in [('17092251297035.jpg','chunli_classica.png'),('images.jpg','chunli_fortnite.jpg'),('Jackie-cityhunter.png','jackie_chunli.png'),('legschunli.jpg','meme_pernas.png')]:
 im=Image.open(raw[original]).convert('RGB');im.thumbnail((1280,1280),Image.Resampling.NEAREST);im.save(pics/dest)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def text(d,xy,value,size=20,fill='white',anchor='mm'):d.text(xy,value,font=ImageFont.truetype(font,size),fill=fill,anchor=anchor)
for vertical in [False,True]:
 W,H=(360,640)if vertical else(640,360);suffix='_vertical'if vertical else''
 im=Image.new('RGB',(W,H),(43,48,58));d=ImageDraw.Draw(im);d.rectangle((4,4,W-5,H-5),outline=(176,186,193),width=3);d.rectangle((9,9,W-10,48),fill=(48,65,95));text(d,(20,28),'ARQUIVOS DA INTERNET',15,anchor='lm')
 boxes=[(22,75,338,300),(22,320,338,545)]if vertical else[(20,78,210,294),(225,78,415,294),(430,78,620,294)]
 for i,(x0,y0,x1,y1)in enumerate(boxes):
  d.rectangle((x0,y0,x1,y1),fill=(11,13,18),outline=(120,128,133),width=2);text(d,((x0+x1)/2,(y0+y1)/2),'CENSURADO',21 if vertical else 16,(248,209,52));text(d,((x0+x1)/2,y1+17),'ARQUIVO '+str(i+1),12,(204,210,216))
 im.save(pics/f'gallery_censored{suffix}.png')
 for checked in [False,True]:
  im=Image.new('RGB',(W,H),(26,31,38));d=ImageDraw.Draw(im);margin=28;d.rectangle((margin,28,W-margin,H-28),fill=(224,217,188),outline=(115,100,70),width=3)
  text(d,(W//2,75),'FICHA DE INSPEÇÃO',23 if not vertical else 19,(36,39,38));text(d,(W//2,111),'PRIORIDADES DO JOGADOR',13,(73,76,68))
  y1,y2=(181,253)if not vertical else(255,365);x=58 if not vertical else 44;size=30
  for y in [y1,y2]:d.rectangle((x,y-15,x+size,y+15),outline=(40,48,44),width=3)
  if checked:d.line((x+6,y2,x+14,y2+8,x+27,y2-10),fill=(24,119,69),width=5)
  text(d,(x+size+15,y1),'VENCER A PARTIDA',21 if not vertical else 16,(37,45,39),anchor='lm');text(d,(x+size+15,y2),'CONFERIR A SKIN',21 if not vertical else 16,(37,45,39),anchor='lm')
  im.save(pics/f'inspection_{"checked"if checked else"blank"}{suffix}.png')
sign=Image.new('RGB',(1280,200),(248,202,40));d=ImageDraw.Draw(sign);d.rectangle((6,6,1273,193),outline=(33,35,33),width=9);text(d,(640,100),'FISCALIZAÇÃO DE SKIN',76,(29,32,29));sign.save(pics/'inspection_sign.png')
sign=Image.new('RGB',(640,256),(248,202,40));d=ImageDraw.Draw(sign);d.rectangle((5,5,634,250),outline=(33,35,33),width=6);text(d,(320,82),'FISCALIZAÇÃO',61,(29,32,29));text(d,(320,184),'DE SKIN',65,(29,32,29));sign.save(pics/'inspection_sign_vertical.png')
with wave.open(str(ROOT/'assets/voz/narracao_completa.wav'))as w:sr=w.getframerate();voice=array.array('h',w.readframes(w.getnframes()))
vd=len(voice)/sr;N=math.ceil((vd+.65)*FPS);end=N/FPS
specs=[(0,1.55,'monitor','hook','chunli_fortnite.mp4',.2),(1.55,2.75,'actor','thoughtful','chunli_fortnite.mp4',1.4),(2.75,4,'game','fight','chunli_luta.mp4',6.0),(4,5,'actor','thoughtful','chunli_classica.png',0),(5,5.95,'photo','name','chunli_classica.png',0),(5.95,7.24,'monitor','name','chunli_fortnite.jpg',0),(7.24,9.2,'game','fight','chunli_luta.mp4',3.2),(9.2,11.64,'game','fight','chunli_akuma.mp4',3),(11.64,13.68,'actor','confident','chunli_classica.png',0),(13.68,15.3,'actor','sigh','meme_pernas.png',0),(15.3,17,'photo','meme','meme_pernas.png',0),(17,18,'photo','jackie','jackie_chunli.png',0),(18,19.36,'actor','sarcasm','jackie_chunli.png',0),(19.36,20.9,'photo','classic','chunli_classica.png',0),(20.9,23.46,'photo','gallery','gallery_censored.png',0),(23.46,24.95,'monitor','crossover','chunli_fortnite.jpg',0),(24.95,26.68,'game','fortnite','chunli_fortnite.mp4',3.4),(26.68,27.65,'actor','excited','chunli_fortnite.mp4',.2),(27.65,30.3,'game','dance','chunli_fortnite.mp4',3),(30.3,31.6,'actor','chuckle','chunli_fortnite.mp4',1.4),(31.6,32.8,'inspection','camera','chunli_fortnite.jpg',0),(32.8,35.42,'inspection','reveal','chunli_fortnite.jpg',0),(35.42,36.7,'inspection','annoyed','inspection_blank.png',0),(36.7,37.45,'photo','checklist','inspection_blank.png',0),(37.45,38.1,'photo','checklist','inspection_checked.png',0),(38.1,end,'inspection','final','inspection_checked.png',0)]
shots=[dict(id=i,start=round(t0*FPS)+1,end=round(t1*FPS),kind=k,mood=m,source=src,source_start=at)for i,(t0,t1,k,m,src,at)in enumerate(specs)];shots[-1]['end']=N
assert all(a['end']+1==b['start']for a,b in zip(shots,shots[1:]))
media=ROOT/'renders/media';media.mkdir(exist_ok=True);clips=[]
for sh in shots:
 src=(game if sh['source'].endswith('.mp4')else pics)/sh['source'];dest=media/f"monitor_{sh['id']:02d}.mp4";n=sh['end']-sh['start']+1;args=['ffmpeg','-v','error','-y','-threads','1','-filter_threads','1']
 args+=['-ss',str(sh['source_start']),'-i',str(src)]if src.suffix=='.mp4'else['-f','image2','-loop','1','-framerate','24','-i',str(src)]
 args+=['-an','-vf','fps=24,scale=640:360:force_original_aspect_ratio=decrease:flags=neighbor,pad=640:360:(ow-iw)/2:(oh-ih)/2:color=0x111319','-frames:v',str(n),'-c:v','libx264','-threads','1','-preset','ultrafast','-crf','18','-pix_fmt','yuv420p',str(dest)];subprocess.run(args,check=True);clips.append(dest)
listing=media/'concat.txt';listing.write_text(''.join("file '"+str(p)+"'\n"for p in clips));subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(listing),'-c:v','copy','-movflags','+faststart',str(game/'monitor_montado.tmp.mp4')],check=True);(game/'monitor_montado.tmp.mp4').replace(game/'monitor_montado.mp4')
mixed=array.array('h',voice);mixed.extend([0]*(math.ceil(end*sr)-len(mixed)))
with wave.open(str(ROOT/'assets/voz/narracao_mix.wav'),'wb')as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(mixed.tobytes())
(ROOT/'timeline.json').write_text(json.dumps(dict(fps=FPS,frames=N,duration=end,voice_duration=vd,shots=shots),indent=2))
(ROOT/'audio.json').write_text(json.dumps(dict(original_filename='Voz - 3 Chun Li.mp3',sha256=hashlib.sha256((ROOT/'assets/voz/voz_original.mp3').read_bytes()).hexdigest(),voice_duration_seconds=vd,frames=N,speed_changed=False,pitch_changed=False,trimmed=False,alignment='Original recording; local ASR segment timings and semantic cut alignment; delivery tags are not subtitles.'),indent=2))
public=[{k:v for k,v in r.items()if k not in ['local_path','probe']}for r in records]
(ROOT/'source_manifest.json').write_text(json.dumps(dict(package='3 - Chun-Li.zip',source='User-provided Google Drive archive',files=public,video_derivatives=json.loads((ROOT/'renders/selected_clips.json').read_text()),images_published=['17092251297035.jpg','images.jpg','Jackie-cityhunter.png','legschunli.jpg'],editorial='Street Fighter 6 gameplay is contemporary illustrative footage, not classic-game footage or proof of current Interpol employment. Classic artwork accompanies the career introduction. The gallery and inspection checklist are authored comic illustrations; no adult material is shown.',omitted='Long AV1 meeting scene, fan sprite animation and unused images remain outside the repository. Only selected gameplay excerpts are published.'),ensure_ascii=False,indent=2))
print('CHUNLI_ASSETS_READY',N,end,flush=True)
