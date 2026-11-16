"""Render de conferência das camadas e dos mesmos keyframes gravados no WFP."""
from pathlib import Path
import json,math,wave,subprocess
import numpy as np,cv2
from scipy.ndimage import gaussian_filter1d
P=Path(__file__).resolve().parent;M=P/'Filmora/midias';CACHE=Path('/workspace/scratch/tube_modular');W,H=1920,1080;FPS=30;N=279;D=N/FPS
cv2.setNumThreads(2)
BODY=[(0,.50,.535,.95,-.8),(.3,.5,.503,1.006,.1),(.6,.5,.505,1.,0),(1.25,.495,.500,1.005,-.3),(2.2,.498,.503,1.,.1),(2.95,.5,.508,.986,.2),(3.1,.495,.508,.986,-.3),(3.3,.493,.5,1.008,-.6),(4.8,.49,.500,1.004,-.2),(6.3,.496,.507,.991,.1),(6.5,.5,.508,.991,.1),(6.7,.5,.501,1.007,0),(7.6,.502,.5,1.,.3),(8.45,.5,.506,.99,.1),(8.6,.5,.506,.99,0),(8.8,.5,.502,1.,0),(9.3,.5,.505,1.,0)]
HEAD=[(0,.6,0),(.6,-.5,-1),(1.2,-.3,-1.5),(1.7,.7,.5),(2.3,0,0),(3.1,-.7,-1),(3.7,.2,0),(4.7,-.8,-1.5),(5.4,.5,0),(6.5,.3,0),(7.2,-.6,-1.5),(8.15,.2,0),(8.6,0,0),(9.3,0,0)]
POSES=[('02_conversando',0,93),('04_apontando',93,195),('05_confuso',195,258),('10_facepalm',258,279)]
EYES=[('00_normal_base',0,40),('02_piscada_meio',40,42),('03_piscada_fechado',42,44),('02_piscada_meio',44,46),('00_normal_base',46,93),('07_desconfiado',93,156),('02_piscada_meio',156,158),('03_piscada_fechado',158,160),('02_piscada_meio',160,162),('07_desconfiado',162,195),('05_confuso',195,258),('12_preocupado',258,279)]
def rot(a):
 a=math.radians(float(a));return np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]])
def curve(points,t):
 for a,b in zip(points,points[1:]):
  if t<=b[0]:
   u=np.clip((t-a[0])/(b[0]-a[0]),0,1);u=u*u*(3-2*u);return np.array(a[1:])*(1-u)+np.array(b[1:])*u
 return np.array(points[-1][1:])
def choose(rows,i):return next((name for name,a,b in rows if a<=i<b),rows[-1][0])
with wave.open(str(M/'voz_teste.wav'))as f:sr=f.getframerate();voice=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(float)/32768
assert sr==48000 and len(voice)==446400
rms=np.array([np.sqrt(np.mean(voice[max(0,int((i/FPS-.016)*sr)):min(len(voice),int((i/FPS+.04)*sr))]**2)+1e-12)for i in range(N+1)])
level=np.percentile(rms,85);energy=gaussian_filter1d(np.clip((rms-.012)/max(.01,level-.012),0,1),.65);energy[rms<.006]=0
frames=[]
for i in range(N+1):
 t=i/FPS;pose=choose(POSES,i);eye=choose(EYES,i);x,y,s,r=curve(BODY,t);hr,hy=curve(HEAD,t)
 if pose=='10_facepalm':hr=0;hy=0
 bp=np.array([x*W,y*H]);hp=bp+rot(r)@np.array([0,hy*s]);theta=r+hr;off=np.array([(468-466)*.64,(515-738)*.64]);e=float(energy[i]);sx=1+.024*e;sy=1+.075*e
 mp=hp+rot(theta)@(s*(off-np.array([sx,sy])*off+np.array([0,-3.4*e])))
 body=dict(x=float(bp[0]/W),y=float(bp[1]/H),sx=float(s*100),sy=float(s*100),rotation=float(r))
 head=dict(x=float(hp[0]/W),y=float(hp[1]/H),sx=float(s*100),sy=float(s*100),rotation=float(theta))
 mouth=dict(x=float(mp[0]/W),y=float(mp[1]/H),sx=float(s*sx*100),sy=float(s*sy*100),rotation=float(theta))
 frames.append(dict(frame=i,time=round(t,8),pose=pose,eyes=eye,speech=e,layers=dict(corpo=body,cabeca=head,olhos=head.copy(),bigode=mouth,frente=body.copy())))
plan=dict(duration=D,fps=30,resolution=[W,H],preview_resolution=[1280,720],voice_source='shorts/008-personagens-que-a-internet-estragou/production/00-intro/assets/voz/narracao_completa.wav',voice_excerpt=[0,9.3],voice_changed_pitch=False,voice_changed_speed=False,segments=[dict(pose=p,start=a/FPS,end=b/FPS)for p,a,b in POSES],eye_segments=[dict(eyes=p,start=a/FPS,end=b/FPS)for p,a,b in EYES],body_authored_keyframes=BODY,head_authored_keyframes=HEAD,frames=frames)
(P/'keyframes.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
w,h=1280,720;bg=cv2.resize(cv2.imread(str(M/'fundo.png')),(w,h),interpolation=cv2.INTER_AREA).astype('float32')/255
planes={}
for f in M.glob('*.png'):
 if f.name=='fundo.png':continue
 a=cv2.imread(str(f),cv2.IMREAD_UNCHANGED);assert a.shape==(H,W,4),f
 a=cv2.resize(a,(w,h),interpolation=cv2.INTER_AREA).astype('float32')/255;a[:,:,:3]*=a[:,:,3:4];planes[f.stem]=a
out=P/'Previa_Modular_Conversando.mp4';log=P/'render.log'
cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{w}x{h}','-r','30','-i','pipe:0','-i',str(M/'voz_teste.wav'),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','fast','-crf','18','-threads','2','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t',str(D),'-movflags','+faststart',str(out)]
with log.open('w')as err:
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=err)
 for f in frames[:-1]:
  canvas=bg.copy();names=dict(corpo='corpo_'+f['pose'],cabeca='cabeca_limpa',olhos='olhos_'+f['eyes'],bigode='bigode_repouso',frente='frente_'+f['pose'])
  for part in ['corpo','cabeca','olhos','bigode','frente']:
   if names[part]not in planes:continue
   tr=f['layers'][part];a=rot(tr['rotation'])@np.diag([tr['sx']/100,tr['sy']/100]);c=np.array([w/2,h/2]);target=np.array([tr['x']*w,tr['y']*h]);matrix=np.column_stack([a,target-a@c]).astype('float32')
   image=cv2.warpAffine(planes[names[part]],matrix,(w,h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0));canvas=image[:,:,:3]+canvas*(1-image[:,:,3:4])
  bgr=np.clip(np.rint(canvas*255),0,255).astype('uint8');proc.stdin.write(bgr.tobytes())
  if f['frame']in[30,43,120,220,270]:cv2.imwrite(str(CACHE/f'previa_{f["frame"]:03d}.jpg'),bgr)
 proc.stdin.close();assert proc.wait()==0,log.read_text()
print('PREVIA_MODULAR_PRONTA',out,D,flush=True)
