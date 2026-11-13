from pathlib import Path
import json,subprocess,wave,math,concurrent.futures
from PIL import Image,ImageOps
P=Path(__file__).resolve().parent;C=Path('/workspace/attachments/gta_v');A=P/'assets';(A/'monitor').mkdir(parents=True,exist_ok=True);(P/'output').mkdir(exist_ok=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(A/'voz/voz_original.mp3'),'-ac','1','-ar','44100','-c:a','pcm_s16le',str(A/'voz/voz_completa.wav')],check=True)
with wave.open(str(A/'voz/voz_completa.wav'))as w:rate=w.getframerate();samples=w.getnframes();pcm=w.readframes(samples)
N=math.ceil((samples/rate+.25)*30);duration=N/30
with wave.open(str(A/'voz/voz_timeline.wav'),'wb')as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(pcm+bytes((round(duration*rate)-samples)*2))
def f(t):return round(t*30)+1
spec=[(0,3.0,'monitor','gancho','franklin.mp4',9),(3.0,7.12,'host','peticao','franklin.mp4',12),(7.12,11.55,'game','campanha_2014','michael.mp4',33),(11.55,13.8,'close','contexto','franklin.mp4',17),(13.8,17.14,'monitor','assinaturas','franklin.mp4',18),(17.14,19.1,'photo','target','target.png',0),(19.1,21.9,'photo','kmart','kmart.png',0),(21.9,26,'monitor','retirada_das_redes','michael.mp4',35),(26,28.55,'host','calma','michael.mp4',39),(28.55,33.08,'game','gta6','gta6_enviado.mp4',39),(33.08,duration,'game','parodia_south_park','south_park.mp4',28)]
shots=[dict(id=i,start=f(a),end=round(b*30),kind=k,mood=m,source=src,source_start=ss)for i,(a,b,k,m,src,ss)in enumerate(spec)]
assert shots[-1]['end']==N and all(a['end']+1==b['start']for a,b in zip(shots,shots[1:]))
info=dict(title='Jogos que a internet tentou cancelar',chapter='GTA V',chapter_order=6,slug='GTA_V',model='Dery_GTA_V.blend',fps=30,frames=N,duration=duration,voice_duration=samples/rate,voice_edited=False,revision=5,clean_media=True,standing_dery=False,monitor_file='assets/monitor/monitor_completo.mp4',cache=str(C),render_size=[768,432],portrait_safe_crop=[263,0,243,432],shots=shots)
(P/'timeline.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n')
def cut(sh):
 path=C/f"monitor_{sh['id']:02d}.mp4";count=sh['end']-sh['start']+1;cmd=['ffmpeg','-v','error','-y','-threads','1']
 if sh['source'].endswith('.mp4'):cmd+=['-ss',str(sh['source_start']),'-i',str(A/'gameplay'/sh['source'])]
 else:
  image=C/f"image_{sh['id']:02d}.png";Image.open(A/'imagens'/sh['source']).convert('RGB').save(image);cmd+=['-f','image2','-loop','1','-framerate','30','-i',str(image)]
 cmd+=['-an','-vf','fps=30,scale=480:270:force_original_aspect_ratio=decrease,pad=480:270:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1','-frames:v',str(count),'-c:v','libx264','-threads','1','-preset','veryfast','-crf','21','-pix_fmt','yuv420p',str(path)];subprocess.run(cmd,check=True);return path
with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:paths=list(pool.map(cut,shots))
listing=C/'monitor_concat.txt';listing.write_text(''.join(f"file '{p}'\n"for p in paths));subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(listing),'-c','copy',str(P/info['monitor_file'])],check=True)
print('GTA_V_ASSETS_READY',N,duration,samples/rate,flush=True)
