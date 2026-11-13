from pathlib import Path
import json,subprocess,wave,math,concurrent.futures
from PIL import Image,ImageOps
P=Path(__file__).resolve().parent;C=Path('/workspace/attachments/pokemon_swsh');A=P/'assets';(A/'monitor').mkdir(parents=True,exist_ok=True);(P/'output').mkdir(exist_ok=True)
# Keep the GIF animated when regenerating this chapter from its original assets.
if not (A/'gameplay/pikachu_reacao.mp4').is_file():
 subprocess.run(['ffmpeg','-v','error','-y','-stream_loop','-1','-ignore_loop','1','-i',str(A/'imagens/pikachu_surprise.gif'),'-t','6','-an','-vf','fps=30,scale=trunc(iw/2)*2:trunc(ih/2)*2,setsar=1','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',str(A/'gameplay/pikachu_reacao.mp4')],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(A/'voz/voz_original.mp3'),'-ac','1','-ar','44100','-c:a','pcm_s16le',str(A/'voz/voz_completa.wav')],check=True)
with wave.open(str(A/'voz/voz_completa.wav'))as w:rate=w.getframerate();samples=w.getnframes();pcm=w.readframes(samples)
N=math.ceil((samples/rate+.25)*30);duration=N/30
with wave.open(str(A/'voz/voz_timeline.wav'),'wb')as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(pcm+bytes((round(duration*rate)-samples)*2))
def f(t):return round(t*30)+1
spec=[(0,3,'monitor','gancho','overview.mp4',62),(3,5.96,'host','corte_pokedex','overview.mp4',65),(5.96,8.8,'photo','game_freak','gamefreak.jpg',0),(8.8,12.88,'game','transferencia','overview.mp4',166),(12.88,15.7,'close','revolta','overview.mp4',170),(15.7,20.36,'monitor','hashtag','overview.mp4',162),(20.36,24.34,'photo','criticas_memes','meme.png',0),(24.34,28.3,'game','capturando','overview.mp4',62),(28.3,32.48,'monitor','pokedex','overview.mp4',187),(32.48,36.64,'close','galar','overview.mp4',192),(36.64,40.48,'game','limitacao','overview.mp4',35),(40.48,43.95,'host','europa','overview.mp4',39),(43.95,duration,'photo','pikachu_reacao','pikachu_reacao.mp4',0)]
shots=[dict(id=i,start=f(a),end=round(b*30),kind=k,mood=m,source=src,source_start=ss)for i,(a,b,k,m,src,ss)in enumerate(spec)]
for sh in shots:
 if sh['id']in[3,7]:sh['portrait_fit']='contain' # Preserve off-centre Pokémon and the trailer's original text.
assert shots[-1]['end']==N and all(a['end']+1==b['start']for a,b in zip(shots,shots[1:]))
info=dict(title='Jogos que a internet tentou cancelar',chapter='Pokémon Sword and Shield',chapter_order=7,slug='Pokemon_Sword_Shield',model='Dery_Pokemon_Sword_Shield.blend',fps=30,frames=N,duration=duration,voice_duration=samples/rate,voice_edited=False,revision=5,clean_media=True,standing_dery=False,monitor_file='assets/monitor/monitor_completo.mp4',cache=str(C),render_size=[768,432],portrait_safe_crop=[263,0,243,432],shots=shots)
(P/'timeline.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n')
def cut(sh):
 path=C/f"monitor_{sh['id']:02d}.mp4";count=sh['end']-sh['start']+1;cmd=['ffmpeg','-v','error','-y','-threads','1']
 if sh['source'].endswith('.mp4'):cmd+=['-ss',str(sh['source_start']),'-i',str(A/'gameplay'/sh['source'])]
 else:
  image=C/f"image_{sh['id']:02d}.png";Image.open(A/'imagens'/sh['source']).convert('RGB').save(image);cmd+=['-f','image2','-loop','1','-framerate','30','-i',str(image)]
 cmd+=['-an','-vf','fps=30,scale=480:270:force_original_aspect_ratio=decrease,pad=480:270:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1','-frames:v',str(count),'-c:v','libx264','-threads','1','-preset','veryfast','-crf','21','-pix_fmt','yuv420p',str(path)];subprocess.run(cmd,check=True);return path
with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:paths=list(pool.map(cut,shots))
listing=C/'monitor_concat.txt';listing.write_text(''.join(f"file '{p}'\n"for p in paths));subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(listing),'-c','copy',str(P/info['monitor_file'])],check=True)
print('POKEMON_ASSETS_READY',N,duration,samples/rate,flush=True)
