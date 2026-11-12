"""Build a phrase-timed monitor edit and keep the complete supplied narration."""
from pathlib import Path
import json,subprocess,wave,math,hashlib
from PIL import Image

P=Path(__file__).resolve().parent;A=P/'assets';C=Path('/workspace/attachments/bully');FPS=30
def run(args):subprocess.run([str(x) for x in args],check=True)
with wave.open(str(A/'voz/voz_completa.wav')) as w:
    sr=w.getframerate();voice=w.readframes(w.getnframes());duration=w.getnframes()/sr
N=math.ceil((duration+.3)*FPS);end=N/FPS
with wave.open(str(A/'voz/voz_timeline.wav'),'wb') as w:
    w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr)
    w.writeframes(voice+b'\0\0'*(round(end*sr)-len(voice)//2))
specs=[
 (0,2.9,'monitor','jimmy','bully_gameplay.mp4',4),
 (2.9,7.0,'host','escola','bully_gameplay.mp4',10),
 (7.0,12.9,'game','valentoes','bully_gameplay.mp4',138),
 (12.9,14.0,'photo','protestos','meme2.png',0),
 (14.0,19.96,'photo','jack_thompson','jack_thompson.png',0),
 (19.96,23.8,'shop','demonstracao_ao_juiz','bully_gameplay.mp4',5),
 (23.8,26.96,'game','demonstracao','bully_gameplay.mp4',218),
 (26.96,29.94,'shop','juiz_gamer','bully_gameplay.mp4',12),
 (29.94,37.54,'archive','brasil','bully_gameplay.mp4',5),
 (37.54,39.16,'host','vamos_concordar','bully_gameplay.mp4',540),
 (39.16,40.6,'photo','barraquinha','barraquinha.jpg',0),
 (40.6,42.2,'photo','dvds','dvds.jpg',0),
 (42.2,45.1,'game','jogou_tranquilo','bully_gameplay.mp4',540),
 (45.1,end,'close','punch','bully_gameplay.mp4',12),
]
shots=[]
for i,(a,b,kind,mood,src,offset) in enumerate(specs):
    shots.append(dict(id=i,start=round(a*FPS)+1,end=round(b*FPS),kind=kind,mood=mood,
                      source=src,source_start=offset))
shots[-1]['end']=N
assert all(a['end']+1==b['start'] for a,b in zip(shots,shots[1:]))
timeline=dict(title='Jogos que a internet tentou cancelar',chapter='Bully',fps=FPS,
              frames=N,duration=end,voice_duration=duration,voice_edited=False,
              revision=2,monitor_file='assets/monitor/monitor_completo.mp4',cache=str(C),render_size=[768,432],portrait_safe_crop=[262.5,0,243,432],shots=shots)
(P/'timeline.json').write_text(json.dumps(timeline,ensure_ascii=False,indent=2)+'\n')
media=A/'monitor';media.mkdir(exist_ok=True)
normalized=A/'normalizadas';normalized.mkdir(exist_ok=True)
parts=[]
for sh in shots:
    out=media/f"trecho_{sh['id']:02d}.mp4";parts.append(out)
    src=A/('gameplay' if sh['source'].endswith('.mp4') else 'imagens')/sh['source']
    if src.suffix!='.mp4':
        dest=normalized/(src.stem+'.png')
        Image.open(src).convert('RGB').save(dest,format='PNG');src=dest
    cmd=['ffmpeg','-v','error','-y','-threads','1','-filter_threads','1']
    if src.suffix=='.mp4':cmd+=['-ss',str(sh['source_start']),'-i',src]
    else:cmd+=['-f','image2','-loop','1','-framerate',str(FPS),'-i',src]
    cmd+=['-an','-vf',f'fps={FPS},scale=480:270:force_original_aspect_ratio=decrease:flags=neighbor,pad=480:270:(ow-iw)/2:(oh-ih)/2:color=0x16151b',
          '-frames:v',str(sh['end']-sh['start']+1),'-c:v','libx264','-threads','1','-preset','ultrafast','-crf','18','-pix_fmt','yuv420p',out]
    run(cmd)
listing=C/'monitor_concat.txt';listing.write_text(''.join("file '"+str(f)+"'\n" for f in parts))
run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',listing,'-c','copy','-movflags','+faststart',media/'monitor_completo.mp4'])
for part in parts:part.unlink()
print('ASSETS_READY',N,end,duration,flush=True)
