"""Prepare supplied audio and the moving Driver monitor feed; no generated voice."""
from pathlib import Path
import subprocess,json,math,wave,array,hashlib
ROOT=Path(__file__).resolve().parent
FPS=24
def run(a):subprocess.run(a,check=True,stdout=subprocess.DEVNULL)
with wave.open(str(ROOT/'assets/voz/narracao_completa.wav'))as w:sr=w.getframerate();voice=array.array('h',w.readframes(w.getnframes()))
duration=len(voice)/sr;N=math.ceil((duration+.65)*FPS);end=N/FPS
specs=[(0,2.65,'game','intro',4),(2.65,4.92,'actor','deadpan',35),(4.92,7.4,'actor','explain',6),(7.4,10.88,'game','undercover',5),(10.88,14.28,'actor','test',2),(14.28,17.6,'monitor','list',2),(17.6,19.15,'game','handbrake',12),(19.15,20.8,'game','spin',26.5),(20.8,22.0,'game','slalom',41),(22.0,23.9,'game','reverse',29.5),(23.9,26.62,'garage','brake',12),(26.62,27.8,'monitor','english',3),(27.8,29.1,'actor','confused',3),(29.1,31.5,'actor','small',4),(31.5,34.95,'actor','stunt',5),(34.95,36.14,'game','clock',76),(36.14,37.78,'game','editorial_restart',2),(37.78,39.9,'garage','boss',8),(39.9,41.8,'garage','bonk',8),(41.8,end,'garage','defeat',8)]
shots=[dict(id=i,start=round(x*FPS)+1,end=round(y*FPS),kind=k,mood=m,source_start=src)for i,(x,y,k,m,src)in enumerate(specs)];shots[-1]['end']=N
next(sh for sh in shots if sh['mood']=='spin')['source_speed']=1.6
assert all(a['end']+1==b['start']for a,b in zip(shots,shots[1:]))
media=ROOT/'renders/media';media.mkdir(parents=True,exist_ok=True)
cache=media/'game_24fps.mp4';source=ROOT/'assets/gameplay/driver_tutorial_enviado.mp4'
run(['ffmpeg','-v','error','-y','-threads','2','-i',str(source),'-an','-vf','fps=24,scale=640:360:flags=neighbor','-c:v','libx264','-threads','2','-preset','ultrafast','-crf','18',str(cache)])
clips=[]
for sh in shots:
 out=media/f"monitor_{sh['id']:02d}.mp4";clips.append(out)
 run(['ffmpeg','-v','error','-y','-ss',str(sh['source_start']),'-i',str(cache),'-an','-vf',f"setpts=PTS/{sh.get('source_speed',1)},fps=24",'-frames:v',str(sh['end']-sh['start']+1),'-c:v','libx264','-threads','2','-preset','ultrafast','-crf','18',str(out)])
listing=media/'concat.txt';listing.write_text(''.join("file '"+str(p)+"'\n"for p in clips))
run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(listing),'-c:v','copy','-movflags','+faststart',str(ROOT/'assets/gameplay/monitor_montado.mp4')])
mix=array.array('h',voice);mix.extend([0]*(math.ceil(end*sr)-len(mix)))
def tone(at,dur,f0,f1,level):
 phase=0
 for j in range(round(dur*sr)):
  u=j/(dur*sr);phase+=math.tau*(f0+(f1-f0)*u)/sr;k=round(at*sr)+j
  if k<len(mix):mix[k]=max(-32768,min(32767,mix[k]+round(32767*level*math.sin(phase)*math.sin(math.pi*u)**2)))
tone(25.9,.14,850,180,.06);tone(38.0,.18,150,85,.065);tone(40.55,.14,110,45,.10)
with wave.open(str(ROOT/'assets/voz/narracao_mix.wav'),'wb')as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(mix.tobytes())
(ROOT/'timeline.json').write_text(json.dumps(dict(fps=FPS,frames=N,duration=end,voice_duration=duration,shots=shots),indent=2))
(ROOT/'audio.json').write_text(json.dumps(dict(original_filename='VOZ - O verdadeiro chefe de DRIVER.mp3',sha256=hashlib.sha256((ROOT/'assets/voz/voz_original.mp3').read_bytes()).hexdigest(),voice_duration_seconds=duration,frames=N,speed_changed=False,pitch_changed=False,trimmed=False,sfx_windows=[[25.9,26.04],[38,38.18],[40.55,40.69]]),indent=2))
(ROOT/'gesture_reference.json').write_text(json.dumps(dict(source='Personal talking reference supplied by user; raw video deliberately kept outside public repository.',method='Hand-authored keyframe acting reference, not motion capture.',cues=[{'reference_seconds':[12,21],'gesture':'Two hands in front of chest, small forward emphases.'},{'reference_seconds':[24,30],'gesture':'Both hands pointing toward viewer; eyebrows and head tilt.'},{'reference_seconds':[33,39],'gesture':'Open palms; short forward lean for emphasis.'},{'reference_seconds':[42,45],'gesture':'One hand raised, then asymmetric return.'}],mapping={'explanation':'alternating chest-height beats','small':'hands brought closer together','stunt':'larger open palms and forward lean','confused':'head tilt and single palm up','defeat':'still head, deadpan PNG face'}),ensure_ascii=False,indent=2))
print('DRIVER_ASSETS_READY',N,end,flush=True)
