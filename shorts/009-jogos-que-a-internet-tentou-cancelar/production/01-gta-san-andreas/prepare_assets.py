"""Build a phrase-timed monitor edit and keep the complete supplied narration."""
from pathlib import Path
import json,subprocess,wave,math,hashlib
from PIL import Image

P=Path(__file__).resolve().parent;A=P/'assets';C=Path('/workspace/attachments/jogos_cancelar');FPS=15
def run(args):subprocess.run([str(x) for x in args],check=True)
with wave.open(str(A/'voz/voz_completa.wav')) as w:
    sr=w.getframerate();voice=w.readframes(w.getnframes());duration=w.getnframes()/sr
N=math.ceil((duration+.3)*FPS);end=N/FPS
with wave.open(str(A/'voz/voz_timeline.wav'),'wb') as w:
    w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr)
    w.writeframes(voice+b'\0\0'*(round(end*sr)-len(voice)//2))
specs=[
 (0,2.1,'monitor','gancho','gameplay_speedrun.mp4',36),
 (2.1,6.55,'host','explica','gameplay_speedrun.mp4',38.1),
 (6.55,9.2,'close','cafeteria','cafe.jpg',0),
 (9.2,14.1,'monitor','hot_coffee','encontro_bar.png',0),
 (14.1,18.95,'archive','mod','gameplay_speedrun.mp4',74),
 (18.95,21.85,'close','serio','cj_classificacao.png',0),
 (21.85,34.55,'shop','classificacao_e_lojas','cj_classificacao.png',0),
 (34.55,38.1,'archive','original','encontro_rua.png',0),
 (38.1,40.35,'game','carro','gameplay_speedrun.mp4',94),
 (40.35,41.7,'photo','atropelar','cj_bug.jpg',0),
 (41.7,43.4,'game','gangues','gameplay_speedrun.mp4',139),
 (43.4,48.35,'close','contraste','encontro_rua.png',0),
 (48.35,52.4,'host','cafe_acompanhado','encontro_rua.png',0),
 (52.4,end,'photo','punch','cj_reacao.png',0),
]
shots=[]
for i,(a,b,kind,mood,src,offset) in enumerate(specs):
    shots.append(dict(id=i,start=round(a*FPS)+1,end=round(b*FPS),kind=kind,mood=mood,
                      source=src,source_start=offset))
shots[-1]['end']=N
assert all(a['end']+1==b['start'] for a,b in zip(shots,shots[1:]))
timeline=dict(title='Jogos que a internet tentou cancelar',chapter='GTA San Andreas',fps=FPS,
              frames=N,duration=end,voice_duration=duration,voice_edited=False,
              render_size=[768,432],portrait_safe_crop=[262.5,0,243,432],shots=shots)
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
run(['ffmpeg','-v','error','-y','-ss','6','-i',A/'gameplay/gameplay_speedrun.mp4','-frames:v','1','-vf','scale=512:288:flags=neighbor',A/'imagens/capa_gta.png'])
print('ASSETS_READY',N,end,duration,flush=True)
