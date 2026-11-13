"""Build a phrase-timed monitor edit and keep the complete supplied narration."""
from pathlib import Path
import json,subprocess,wave,math,hashlib
from PIL import Image

P=Path(__file__).resolve().parent;A=P/'assets';C=Path('/workspace/attachments/saints_row_iv');FPS=30
def run(args):subprocess.run([str(x) for x in args],check=True)
with wave.open(str(A/'voz/voz_completa.wav')) as w:
    sr=w.getframerate();voice=w.readframes(w.getnframes());duration=w.getnframes()/sr
N=math.ceil((duration+.3)*FPS);end=N/FPS
with wave.open(str(A/'voz/voz_timeline.wav'),'wb') as w:
    w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr)
    w.writeframes(voice+b'\0\0'*(round(end*sr)-len(voice)//2))
specs=[
 (0,3.2,'monitor','gancho','free_roam.mp4',12),
 (3.2,6.36,'close','sol_nao_bate','free_roam.mp4',80),
 (6.36,11.6,'photo','arma','weapon_menu.png',0),
 (11.6,14.8,'host','pelo_nome','weapon.png',0),
 (14.8,18.9,'game','arma_em_jogo','weapon.mp4',9.5),
 (18.9,20.0,'photo','reacao','meme.png',0),
 (20.0,26.7,'shop','classificacao','weapon.png',0),
 (26.7,31.4,'archive','recusada','weapon.png',0),
 (31.4,34.6,'game','gameplay_ilustrativa','free_roam.mp4',560),
 (34.6,38.4,'shop','versao_modificada','weapon.png',0),
 (38.4,end,'game','punch','funny_walk.mp4',13),
]
shots=[]
for i,(a,b,kind,mood,src,offset) in enumerate(specs):
    shots.append(dict(id=i,start=round(a*FPS)+1,end=round(b*FPS),kind=kind,mood=mood,
                      source=src,source_start=offset))
shots[-1]['end']=N
assert all(a['end']+1==b['start'] for a,b in zip(shots,shots[1:]))
timeline=dict(title='Jogos que a internet tentou cancelar',chapter='Saints Row IV',fps=FPS,
              frames=N,duration=end,voice_duration=duration,voice_edited=False,
              revision=2,clean_media=True,monitor_file='assets/monitor/monitor_completo.mp4',cache=str(C),render_size=[768,432],portrait_safe_crop=[262.5,0,243,432],shots=shots)
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
