"""Use the supplied recording and inspected clips; prepare a synchronized monitor."""
from pathlib import Path
import json,subprocess,math,wave,array,hashlib,shutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent;FPS=24
records=json.loads((ROOT/'renders/package_inventory.json').read_text());raw={r['original_filename']:Path(r['local_path'])for r in records};pics=ROOT/'assets/memes';pics.mkdir(parents=True,exist_ok=True)
for name in ['ladygamer.jpg','ladytall.png','ladytall2.jpg','memelady.jpg']:
 shutil.copyfile(raw[name],pics/name)
 if name.endswith('.png'):Image.open(raw[name]).convert('RGB').save(pics/name)
# The supplied website screenshot includes a sexualized banner. Cover the entire
# banner before creating any public asset or monitor feed; retain its search UI.
im=Image.open(raw['Rule34 Print.png']).convert('RGB');draw=ImageDraw.Draw(im);draw.rectangle((0,0,1280,395),fill=(37,40,31));font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
f=ImageFont.truetype(font,95);draw.text((640,130),'CENSURADO',font=f,anchor='mm',fill=(255,221,45));draw.text((640,265),'REGRA 34',font=ImageFont.truetype(font,55),anchor='mm',fill='white');im.save(pics/'rule34_censurado.png')
# Reframe the supplied two-panel reaction for portrait while keeping both faces.
im=Image.open(raw['memelady.jpg']).convert('RGB');stack=Image.new('RGB',(640,1136))
stack.paste(im.crop((0,0,640,568)),(0,0));stack.paste(im.crop((640,0,1280,568)),(0,568));stack.save(pics/'memelady_vertical.png')
cv=Image.new('RGB',(960,540),(28,33,39));d=ImageDraw.Draw(cv);d.rectangle((25,25,935,515),outline=(247,193,37),width=5)
for text,y,size,color in [('CURRÍCULO',85,44,(247,193,37)),('LADY DIMITRESCU',160,42,'white'),('PROFISSÃO: VILÃ',250,30,'white'),('OUTRAS ATIVIDADES:',330,29,'white')]:d.text((480,y),text,font=ImageFont.truetype(font,size),anchor='mm',fill=color)
d.rectangle((125,385,835,465),fill=(5,6,8));d.text((480,424),'CENSURADO',font=ImageFont.truetype(font,42),anchor='mm',fill=(247,193,37));cv.save(pics/'curriculo_lady.png')
with wave.open(str(ROOT/'assets/voz/narracao_completa.wav'))as w:sr=w.getframerate();voice=array.array('h',w.readframes(w.getnframes()))
voice_duration=len(voice)/sr;N=math.ceil((voice_duration+.65)*FPS);end=N/FPS
# Boundaries follow the supplied recording, which differs from the typed draft.
specs=[(0,2.4,'game','threat','lady_claws.mp4',.3),(2.4,4.94,'actor','opposite','lady_phone.mp4',16),(4.94,6.85,'monitor','name','lady_phone.mp4',16),(6.85,9.18,'game','name','lady_phone.mp4',17),(9.18,11.35,'game','claws','lady_claws.mp4',2),(11.35,13.3,'actor','claws','lady_hall.mp4',5),(13.3,16.44,'photo','height','ladytall2.jpg',0),(16.44,18.8,'castle','height','ladytall2.jpg',0),(18.8,20.42,'photo','height_meme','ladytall.png',0),(20.42,23.65,'actor','strange','lady_phone.mp4',17),(23.65,25.82,'photo','reaction','memelady_vertical.png',0),(25.82,28.66,'castle','escape','lady_hall.mp4',6),(28.66,30.2,'photo','rule34','rule34_censurado.png',0),(30.2,31.8,'actor','embarrassed','rule34_censurado.png',0),(31.8,33.7,'photo','gamer','ladygamer.jpg',0),(33.7,36.6,'monitor','career','curriculo_lady.png',0),(36.6,end,'actor','final','curriculo_lady.png',0)]
shots=[]
for i,(t0,t1,kind,mood,src,at)in enumerate(specs):shots.append(dict(id=i,start=round(t0*FPS)+1,end=round(t1*FPS),kind=kind,mood=mood,source=src,source_start=at))
shots[-1]['end']=N;assert all(a['end']+1==b['start']for a,b in zip(shots,shots[1:]))
media=ROOT/'renders/media';media.mkdir(exist_ok=True);clips=[]
for sh in shots:
 src=(ROOT/'assets/gameplay'/sh['source'])if sh['source'].endswith('.mp4')else(pics/sh['source']);dest=media/f"monitor_{sh['id']:02d}.mp4";n=sh['end']-sh['start']+1
 args=['ffmpeg','-v','error','-y','-threads','1','-filter_threads','1']
 if src.suffix=='.mp4':args+=['-ss',str(sh['source_start']),'-i',str(src)]
 else:args+=['-f','image2','-loop','1','-framerate','24','-i',str(src)]
 args+=['-an','-vf','fps=24,scale=640:360:force_original_aspect_ratio=decrease:flags=neighbor,pad=640:360:(ow-iw)/2:(oh-ih)/2:color=0x111319','-frames:v',str(n),'-c:v','libx264','-threads','1','-preset','ultrafast','-crf','18','-pix_fmt','yuv420p',str(dest)]
 subprocess.run(args,check=True);clips.append(dest)
listing=media/'concat.txt';listing.write_text(''.join("file '"+str(p)+"'\n"for p in clips));subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(listing),'-c:v','copy','-movflags','+faststart',str(ROOT/'assets/gameplay/monitor_montado.mp4')],check=True)
mixed=array.array('h',voice);mixed.extend([0]*(math.ceil(end*sr)-len(mixed)))
with wave.open(str(ROOT/'assets/voz/narracao_mix.wav'),'wb')as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(mixed.tobytes())
(ROOT/'timeline.json').write_text(json.dumps(dict(fps=FPS,frames=N,duration=end,voice_duration=voice_duration,shots=shots),indent=2))
(ROOT/'audio.json').write_text(json.dumps(dict(original_filename='Voz - 1 Lady Dimitrescu.mp3',sha256=hashlib.sha256((ROOT/'assets/voz/voz_original.mp3').read_bytes()).hexdigest(),voice_duration_seconds=voice_duration,frames=N,speed_changed=False,pitch_changed=False,trimmed=False,alignment='Actual supplied recording, local ASR segment timing; no generated or added speech.'),indent=2))
public=[]
for r in records:
 public.append({k:v for k,v in r.items()if k not in ['local_path','probe']})
(ROOT/'source_manifest.json').write_text(json.dumps(dict(package='1 - Lady Dimitrescu.zip',source='User-provided Google Drive archive',files=public,video_derivatives={'lady_phone.mp4':{'original':'Lady Dimitrescu Long Dress Black answers the phone','interval':[20,57]},'lady_hall.mp4':{'original':'Spanking Lady Dimitrescu','interval':[48,63]},'lady_claws.mp4':{'original':'Resident Evil Village lady dimitrescu unique death animation','interval':[0,7]}},website_image='Original banner entirely masked in the public derivative; raw screenshot kept outside the repository.'),ensure_ascii=False,indent=2))
print('LADY_ASSETS_READY',N,end,flush=True)
