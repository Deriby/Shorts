"""Encode only the new inserts in 3D, then reuse the delivered full edits."""
from pathlib import Path
import sys,json,subprocess,math,base64,zlib,wave,concurrent.futures,hashlib
sys.path.insert(0,'/workspace/tools/shorts_asr')
import numpy as np,cv2
from PIL import Image,ImageOps
cv2.setNumThreads(1)
P=Path(__file__).resolve().parent;R=next(p for p in P.parents if(p/'AGENTS.md').exists());plans=json.loads((P/'plano.json').read_text());code=(P.parent/'shared_media/compose_clean.py').read_text();exec(code[code.index('class Reader:'):code.index('class Writer:')]);exec(code[code.index('def cropbox'):code.index('def media_canvas')]);FPS=30
class Writer:
 def __init__(self,p,size):
  self.p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{size[0]}x{size[1]}','-r','30','-i','pipe:0','-an','-c:v','ffv1','-threads','1','-pix_fmt','bgr0',str(p)],stdin=subprocess.PIPE)
 def write(self,im):self.p.stdin.write(im.tobytes())
 def close(self):self.p.stdin.close();assert self.p.wait()==0

def insert(plan):
 global projection
 C=Path(plan['cache']);reader=None
 if plan['kind']=='pokebola':
  projection=json.loads((C/'screen_projection.json').read_text());model=R/plan.get('model',plan['output']+'/'+plan['slug']+'_R6_Cena_Curta.blend');assert projection['model_sha256']==hashlib.sha256(model.read_bytes()).hexdigest();reader=Reader(R/'shorts/009-jogos-que-a-internet-tentou-cancelar/production/07-pokemon-sword-shield/assets/gameplay/overview.mp4',35,plan['count']);writers=[Writer(C/'gag_9x16.mkv',(1080,1920)),Writer(C/'gag_16x9.mkv',(1920,1080))]
 else:writers=[Writer(C/'gag.mkv',(768,432))]
 bayer=(np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]],np.float32)+.5)/16-.5;noise=np.tile(bayer,(108,192))[:,:,None]*5
 for f in range(1,plan['count']+1):
  x=np.asarray(Image.open(C/'frames'/f'frame_{f:04d}.png').convert('RGB'),np.float32);raw=Image.fromarray(np.uint8(np.clip(np.floor((x+noise)/8+.5),0,31)*(255/31)))
  if reader:
   source=reader.read()
   for w,wide in zip(writers,[False,True]):
    im=raw if wide else raw.crop((263,0,506,432));im=im.resize((1920,1080)if wide else(1080,1920),Image.Resampling.NEAREST);w.write(overlay(im,source,f,wide))
  else:writers[0].write(raw)
 for w in writers:w.close()
 if reader:reader.close()
 print('R6_INSERT_ENCODED',plan['episode'],flush=True)

def pcm(p):
 with wave.open(str(p))as w:
  assert w.getframerate()==44100 and w.getsampwidth()==2
  return np.frombuffer(w.readframes(w.getnframes()),'<i2').reshape(-1,w.getnchannels()).astype(np.int32)
def wav(p,x):
 with wave.open(str(p),'wb')as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(44100);w.writeframes(np.int16(x).tobytes())
def prepare_insert(gag):
 C=Path(gag['cache']);model=R/gag['model'];digest=hashlib.sha256(model.read_bytes()).hexdigest();marker=C/'insert.ready.json';outputs=[C/'gag_9x16.mkv',C/'gag_16x9.mkv']if gag['kind']=='pokebola'else[C/'gag.mkv']
 if marker.exists()and json.loads(marker.read_text()).get('model_sha256')==digest and all(p.is_file()and p.stat().st_size>1000 for p in outputs):return
 insert(gag);marker.write_text(json.dumps(dict(model_sha256=digest,frames=gag['count']))+'\n')

def audio(plan):
 O=R/plan['output'];M=O/'Filmora/midias';M.mkdir(parents=True,exist_ok=True);original=pcm(R/plan['source']['mix']);assert original.shape[1]==2;mix=original.copy();SR=44100;events=[]
 for index,gag in enumerate(plan['gags']):
  duration=.36;t=np.arange(round(SR*duration))/SR;rng=np.random.default_rng(601+plans.index(plan)*10+index);kind=gag['kind'];hit={'cafe':.32,'rodas':.30,'juiz':.65,'sequencia':.61,'recuo':.25,'tecla':.32,'pokebola':.46,'vampiro':.52,'arquivos_cafe':.38,'estrelas_cafe':.36,'bike_x':.48,'disco_grade':.50,'amor_sequencia':.63,'sem_graca':.29,'peticao':.35,'viagem':.34,'surto':.36}[kind];start=(gag['start']-1)/30+hit*gag['count']/30
  noise=rng.uniform(-1,1,len(t));env=np.minimum(t/.004,1)*np.exp(-t/.065)
  if kind in['juiz','sequencia','bike_x']:fx=(np.sin(t*math.tau*(125 if kind=='juiz'else 210))*.65+noise*.35)*env
  elif kind in['tecla','sem_graca']:fx=noise*(np.exp(-t/.012)+.5*np.exp(-np.maximum(t-.16,0)/.012)*(t>=.16))
  elif kind in['rodas','peticao','viagem']:fx=np.convolve(noise,np.ones(23)/23,mode='same')*np.sin(np.pi*t/duration)**2
  elif kind in['recuo','surto','arquivos_cafe']:fx=(.5*np.sin(math.tau*(310*t-230*t*t))+.15*noise)*env
  elif kind in['pokebola','estrelas_cafe']:fx=(np.sin(math.tau*1100*t)+.25*np.sin(math.tau*1733*t))*env
  else:fx=np.sin(math.tau*(430*t-240*t*t))*env
  fx=fx/(np.max(np.abs(fx))+1e-9)*1000;fx=np.repeat(fx[:,None],2,axis=1);a=round(start*SR);n=min(len(fx),len(original)-a);available=np.maximum(0,32200-np.abs(mix[a:a+n]));effect=np.int32(np.round(np.sign(fx[:n])*np.minimum(np.abs(fx[:n]),available)));mix[a:a+n]+=effect;name=f'ceninha_{index+1:02d}.wav';wav(M/name,effect);events.append(dict(start=start,duration=len(effect)/SR,file=name,gag_id=gag['id'],kind=kind))
 assert np.max(np.abs(mix))<=32768;wav(O/'mix_r6.wav',mix);data=dict(events=events,original_mix_unchanged_outside_effects=True,voice_file_unchanged=True);(O/'som_ceninha.json').write_text(json.dumps(data,indent=2)+'\n');return data

def compose(plan,mode):
 O=R/plan['output'];wide=mode=='16x9';silent=mode=='base';source=R/plan['source']['wide'if wide else'base'if silent else'short'];dest=O/'Filmora/midias'/plan['source_base_name']if silent else O/(plan['slug']+'_R6_'+mode+'.mp4');cmd=['ffmpeg','-v','error','-y','-filter_complex_threads','1','-threads','1','-i',str(source)];filters=[];previous='0:v'
 for index,gag in enumerate(plan['gags'],1):
  C=Path(gag['cache']);path=C/(('gag_16x9.mkv'if wide else'gag_9x16.mkv')if gag['kind']=='pokebola'else'gag.mkv');cmd+=['-threads','1','-i',str(path)];a=(gag['start']-1)/30;b=gag['end']/30;chain=f'[{index}:v]fps=30'
  if gag['kind']!='pokebola':
   if not wide:chain+=',crop=243:432:263:0:exact=1'
   chain+=',scale='+('1920:1080'if wide else'1080:1920')+':flags=neighbor'
  chain+=f',settb=1/30,setpts=N+{gag["start"]-1}[gag{index}]';filters.append(chain);filters.append(f'[{previous}][gag{index}]overlay=0:0:eof_action=pass:repeatlast=0:enable=\'gte(t,{a})*lt(t,{b})\'[v{index}]');previous=f'v{index}'
 if not silent:cmd+=['-i',str(O/'mix_r6.wav')]
 cmd+=['-filter_complex',';'.join(filters),'-map',f'[{previous}]']
 if silent:cmd+=['-an']
 else:cmd+=['-map',f'{len(plan["gags"])+1}:a:0','-c:a','aac','-b:a','192k']
 cmd+=['-frames:v',str(plan['frames']),'-r','30','-fps_mode','cfr','-c:v','libx264','-threads','1','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)]
 C=Path(plan['cache'])
 with open(C/f'export_{mode}.log','w')as log:result=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
 assert result.returncode==0,(plan['episode'],mode,(C/f'export_{mode}.log').read_text()[-1600:]);print('R6_EXPORTED',plan['episode'],mode,len(plan['gags']),flush=True)
if __name__=='__main__':
 selected=sys.argv[1:]
 for plan in plans:
  if selected and plan['episode']not in selected:continue
  for gag in plan['gags']:prepare_insert(dict(plan,**gag))
  audio(plan)
  with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:list(pool.map(lambda mode:compose(plan,mode),['base','9x16','16x9']))
