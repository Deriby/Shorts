"""Native FFmpeg assembly: clean media, short seated reactions, original audio."""
from pathlib import Path
import json,sys,subprocess,wave,concurrent.futures,time
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;ROOT=P.parent
sources={
'01-gta-san-andreas':('R3_Midias_Limpas','GTA_San_Andreas_R3_Midias_Limpas','GTA_base_R2_9x16.mp4'),
'02-bmx-xxx':('R3_Midias_Limpas','BMX_XXX_R3_Midias_Limpas','BMX_base_9x16.mp4'),
'03-bully':('R3_Midias_Limpas','Bully_R3_Midias_Limpas','Bully_base_9x16.mp4'),
'04-saints-row-iv':('','Saints_Row_IV_Cancelar','Saints_Row_IV_base_9x16.mp4')}
def run(cmd,log):
 with open(log,'w')as f:result=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
 assert result.returncode==0,(log,Path(log).read_text()[-1600:])
def readwav(path):
 with wave.open(str(path))as w:assert w.getsampwidth()==2 and w.getframerate()==44100;return np.frombuffer(w.readframes(w.getnframes()),'<i2').reshape(-1,w.getnchannels()).astype(np.int32)
def prepare(project,info,out,C):
 C.mkdir(parents=True,exist_ok=True);media=out/'Filmora/midias';media.mkdir(parents=True,exist_ok=True)
 voice=readwav(project/'assets/voz/voz_timeline.wav');music=readwav(project/'assets/audio/trilha_baixa.wav');mix=np.repeat(voice,2,axis=1)+music
 edits=json.loads((project/'edicao.json').read_text());events=[e for e in edits['sfx']if e['file']=='plop_comico.wav']
 for e in events:
  sound=readwav(project/'assets/audio'/e['file']);start=round(e['start']*44100);n=min(len(sound),len(mix)-start);mix[start:start+n]+=sound[:n]
 mix=np.int16(np.clip(mix,-32768,32767))
 with wave.open(str(out/'mix_revisado.wav'),'wb')as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(44100);w.writeframes(mix.tobytes())
 (out/'audio_revisado.json').write_text(json.dumps(dict(voice_full=True,original_voice_file_unchanged=True,sfx=events,removed_prop_sfx=[e for e in edits['sfx']if e not in events]),ensure_ascii=False,indent=2)+'\n')
 bayer=(np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]],np.float32)+.5)/16-.5;noise=np.tile(bayer,(108,192))[:,:,None]*5
 for sh in info['shots']:
  if sh['kind']!='seated':continue
  dest=C/f"sentado_{sh['start']:04d}.mkv"
  if dest.exists():continue
  cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','768x432','-r','30','-i','pipe:0','-an','-c:v','ffv1','-threads','1','-pix_fmt','bgr0',str(dest)]
  proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
  for f in range(sh['start'],sh['end']+1):
   src=C/'frames'/f'frame_{f:04d}.png';assert src.is_file(),src;x=np.asarray(Image.open(src).convert('RGB'),np.float32);x=np.uint8(np.clip(np.floor((x+noise)/8+.5),0,31)*(255/31));proc.stdin.write(x.tobytes())
  proc.stdin.close();assert proc.wait()==0

def compose(project,info,out,C,mode):
 folder,oldslug,base=sources[project.name];oldout=project/'output'/folder
 wide=mode=='16x9';silent=mode=='base';W,H=(1920,1080)if wide else(1080,1920)
 oldfile=oldout/'Filmora/midias'/base if silent else oldout/(oldslug+('_16x9.mp4'if wide else'_9x16.mp4'))
 dest=out/'Filmora/midias'/base if silent else out/(info['slug']+'_R4_9x16.mp4'if not wide else info['slug']+'_R4_16x9.mp4')
 cmd=['ffmpeg','-v','error','-y','-filter_complex_threads','1'];filters=[];ed=json.loads((project/'edicao.json').read_text());labels=[]
 for i,sh in enumerate(info['shots']):
  count=sh['end']-sh['start']+1;dur=(count+1)/30;patch=sh['patch'];kind=sh['kind'];a=(sh['start']-1)/30
  if not patch:src=oldfile;cmd+=['-threads','1','-ss',f'{a:.9f}','-t',f'{dur:.9f}','-i',str(src)]
  elif kind=='seated':cmd+=['-threads','1','-t',f'{dur:.9f}','-i',str(C/f"sentado_{sh['start']:04d}.mkv")]
  elif kind=='photo':
   src=C/('photo_'+sh['source']+'.png')
   if not src.exists():Image.open(project/'assets/imagens'/sh['source']).convert('RGB').save(src)
   cmd+=['-f','image2','-loop','1','-framerate','30','-t',f'{dur:.9f}','-i',str(src)]
  else:cmd+=['-threads','1','-ss',str(sh['source_start']),'-t',f'{dur:.9f}','-i',str(project/'assets/gameplay'/sh['source'])]
  chain=f'[{i}:v]fps=30,trim=end_frame={count},setpts=PTS-STARTPTS'
  if patch:
   if kind=='seated':
    if not wide:chain+=',crop=243:432:263:0:exact=1'
    chain+=f',scale={W}:{H}:flags=neighbor'
   elif kind=='photo':
    # Keep all original meme text visible, with normal interpolation.
    chain+=f',scale={W}:{H}:force_original_aspect_ratio=decrease:force_divisible_by=2:flags=lanczos,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0x1f1e27'
   else:chain+=f',scale={W}:{H}:force_original_aspect_ratio=increase:force_divisible_by=2:flags=lanczos,crop={W}:{H}'
   if kind!='seated':chain+=f",zoompan=z='1+0.025*on/{max(1,count-1)}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={W}x{H}:fps=30"
   if not silent:
    for j,title in enumerate(ed['titles']):
     ta=max(0,title['start']-a);tb=min(count/30,title['end']-a)
     if ta>=tb:continue
     txt=C/f'title_{j}.txt';txt.write_text(title['text']);font=project/'assets/fontes/Baloo2.ttf';size=round(W*(.072 if wide else .095));stroke=max(3,round(W/240))
     chain+=f",drawtext=fontfile='{font}':textfile='{txt}':fontsize={size}:fontcolor=0xffdc47:borderw={stroke}:bordercolor=0x151317:x=(w-tw)/2:y=h*{title['y']}-th/2:enable='gte(t,{ta})*lt(t,{tb})'"
  chain+=f',setsar=1,format=yuv420p[v{i}]';filters.append(chain);labels.append(f'[v{i}]')
 filters.append(''.join(labels)+f'concat=n={len(labels)}:v=1:a=0[out]')
 graph=C/f'filter_{mode}.txt';graph.write_text(';\n'.join(filters))
 if not silent:cmd+=['-i',str(out/'mix_revisado.wav')]
 cmd+=['-filter_complex_script',str(graph),'-map','[out]']
 if not silent:cmd+=['-map',f'{len(labels)}:a:0','-c:a','aac','-b:a','192k']
 else:cmd+=['-an']
 cmd+=['-frames:v',str(info['frames']),'-r','30','-fps_mode','cfr','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)]
 run(cmd,C/f'encode_{mode}.log');print('R4_EXPORTED',project.name,mode,flush=True)
if __name__=='__main__':
 episodes=sys.argv[1:] or list(sources)
 for ep in episodes:
  project=ROOT/ep;out=project/'output/R4_Sem_Dery_Em_Pe';info=json.loads((out/'timeline.json').read_text());C=Path('/workspace/attachments/revisao_r4')/ep;prepare(project,info,out,C)
  with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:list(pool.map(lambda mode:compose(project,info,out,C,mode),['base','9x16','16x9']))
