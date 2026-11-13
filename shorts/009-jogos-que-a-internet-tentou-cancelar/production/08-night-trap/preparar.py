from pathlib import Path
import json,subprocess,wave,math,concurrent.futures
from PIL import Image,ImageOps
P=Path(__file__).resolve().parent;C=Path('/workspace/attachments/night_trap');A=P/'assets';(A/'monitor').mkdir(parents=True,exist_ok=True);(P/'output').mkdir(exist_ok=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(A/'voz/voz_original.wav'),'-ac','1','-ar','44100','-c:a','pcm_s16le',str(A/'voz/voz_completa.wav')],check=True)
with wave.open(str(A/'voz/voz_completa.wav'))as w:rate=w.getframerate();samples=w.getnframes();pcm=w.readframes(samples)
N=math.ceil((samples/rate+.25)*30);duration=N/30
with wave.open(str(A/'voz/voz_timeline.wav'),'wb')as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(pcm+bytes((round(duration*rate)-samples)*2))
def f(t):return round(t*30)+1
spec=[(0, 3.4, 'monitor', 'gancho', 'ending.mp4', 20.6), (3.4, 7.28, 'close', 'escandalo', 'ending.mp4', 24), (7.28, 11.5, 'photo', 'identidade', 'arte_night_trap.png', 0), (11.5, 15.32, 'game', 'atores_reais', 'ending.mp4', 13), (15.32, 19, 'monitor', 'proteger', 'megan.mp4', 5.4), (19, 23.3, 'game', 'invasores', 'megan.mp4', 17), (23.3, 27.9, 'host', 'surto', 'megan.mp4', 21), (27.9, 33.6, 'close', 'audiencia', 'ending.mp4', 40), (33.6, 38.7, 'photo', 'prateleiras', 'capa_mega_cd.jpg', 0), (38.7, 43.3, 'host', 'retirada', 'ending.mp4', 60)]
spec[-1]=(*spec[-1][:1],duration,*spec[-1][2:])
shots=[dict(id=i,start=f(a),end=round(b*30),kind=k,mood=m,source=src,source_start=ss)for i,(a,b,k,m,src,ss)in enumerate(spec)]
for sh in shots:
 if sh['kind']=='game':sh['portrait_fit']='contain' # Preserve the original 4:3 FMV and the camera interface.
assert shots[-1]['end']==N and all(a['end']+1==b['start']for a,b in zip(shots,shots[1:]))
info=dict(title='Jogos que a internet tentou cancelar',chapter='Night Trap',chapter_order=8,slug='Night_Trap',model='Dery_Night_Trap.blend',fps=30,frames=N,duration=duration,voice_duration=samples/rate,voice_edited=False,revision=5,clean_media=True,standing_dery=False,monitor_file='assets/monitor/monitor_completo.mp4',cache=str(C),render_size=[768,432],portrait_safe_crop=[263,0,243,432],shots=shots)
(P/'timeline.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n')
def cut(sh):
 path=C/f"monitor_{sh['id']:02d}.mp4";count=sh['end']-sh['start']+1;cmd=['ffmpeg','-v','error','-y','-threads','1']
 if sh['source'].endswith('.mp4'):cmd+=['-ss',str(sh['source_start']),'-i',str(A/'gameplay'/sh['source'])]
 else:
  image=C/f"image_{sh['id']:02d}.png";Image.open(A/'imagens'/sh['source']).convert('RGB').save(image);cmd+=['-f','image2','-loop','1','-framerate','30','-i',str(image)]
 cmd+=['-an','-vf','fps=30,scale=480:270:force_original_aspect_ratio=decrease,pad=480:270:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1','-frames:v',str(count),'-c:v','libx264','-threads','1','-preset','veryfast','-crf','21','-pix_fmt','yuv420p',str(path)];subprocess.run(cmd,check=True);return path
with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:paths=list(pool.map(cut,shots))
listing=C/'monitor_concat.txt';listing.write_text(''.join(f"file '{p}'\n"for p in paths));subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(listing),'-c','copy',str(P/info['monitor_file'])],check=True)
print('NIGHT_TRAP_ASSETS_READY',N,duration,samples/rate,flush=True)
