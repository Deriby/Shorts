"""Prévia 2D: mesmas transformações numéricas usadas no WFP, sem Blender."""
from pathlib import Path
import json,math,subprocess,wave,hashlib
import cv2,numpy as np
from scipy.ndimage import gaussian_filter1d
P=Path(__file__).resolve().parent;M=P/'Filmora/midias';W,H=1920,1080;FPS=30;N=279;DURATION=N/FPS
cv2.setNumThreads(2)
CACHE=Path('/workspace/scratch/tube_previa');CACHE.mkdir(parents=True,exist_ok=True)
# Poses 2D mudam por ação/frase; curvas de inclinação são autorais, não loop periódico.
BODY=[(0,.50,.538,.945,-1.1),(.30,.50,.504,1.008,.2),(.60,.50,.505,1.,0.),(1.25,.495,.498,1.006,-.35),(2.20,.498,.503,1.,.05),(3.10,.505,.496,1.008,.6),(3.90,.500,.507,.987,.2),(4.10,.492,.509,.987,-.25),(4.30,.492,.500,1.012,-.6),(5.30,.489,.499,1.008,-.3),(6.20,.496,.502,1.,0.),(6.65,.50,.509,.99,.2),(6.85,.50,.508,.99,0.),(7.05,.501,.500,1.008,.2),(8.20,.50,.500,1.,0.),(8.60,.50,.505,1.,-.2),(9.30,.50,.505,1.,0.)]
HEAD=[(0,.8,0.,1.),(.60,-.6,-1.5,1.),(1.20,-.3,-2.,1.),(1.70,.9,1.,1.),(2.30,0.,0.,1.),(3.15,-1.1,-1.,1.),(3.60,-.3,0.,1.),(4.10,.5,1.,1.),(4.70,-1.,-2.,1.),(5.40,.6,0.,1.),(6.50,.2,0.,1.),(6.85,-1.3,-2.,1.),(7.25,.3,1.,1.),(8.15,-.2,0.,1.),(8.60,0.,0.,1.),(9.30,0.,0.,1.)]

def curve(points,t):
    for a,b in zip(points,points[1:]):
        if t<=b[0]:
            u=max(0.,min(1.,(t-a[0])/(b[0]-a[0])));u=u*u*(3-2*u)
            return np.array(a[1:])*(1-u)+np.array(b[1:])*u
    return np.array(points[-1][1:])

def rotation(degrees):
    a=math.radians(float(degrees));return np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]])

with wave.open(str(M/'voz_teste.wav')) as f:
    sr=f.getframerate();raw=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(float)/32768
assert sr==48000 and len(raw)==round(DURATION*sr)
rms=np.array([math.sqrt(np.mean(raw[max(0,int((i/FPS-.016)*sr)):min(len(raw),int((i/FPS+.040)*sr))]**2)+1e-12) for i in range(N+1)])
level=np.percentile(rms,85);energy=np.clip((rms-.012)/max(.01,level-.012),0,1)
energy=gaussian_filter1d(energy,.65);energy[rms<.006]=0
frames=[]
for i in range(N+1):
    t=i/FPS;x,y,s,r=curve(BODY,t);hr,hy,hs=curve(HEAD,t)
    pose='apontando' if 123<=i<201 else 'conversando'
    bp=np.array([x*W,y*H]);hp=bp+rotation(r)@np.array([0,hy*s]);theta=r+hr;parent=s*hs
    off=np.array([0.,(.64*(568-784)) if pose=='conversando' else .64*(568-774)])
    e=float(energy[i]);sx=1+.024*e;sy=1+.075*e;dy=-3.4*e
    mp=hp+rotation(theta)@(parent*(off-np.array([sx,sy])*off+np.array([0.,dy])))
    frames.append(dict(frame=i,time=round(t,8),pose=pose,speech=e,layers={
        'corpo':dict(x=float(bp[0]/W),y=float(bp[1]/H),sx=float(s*100),sy=float(s*100),rotation=float(r)),
        'cabeca':dict(x=float(hp[0]/W),y=float(hp[1]/H),sx=float(parent*100),sy=float(parent*100),rotation=float(theta)),
        'bigode':dict(x=float(mp[0]/W),y=float(mp[1]/H),sx=float(parent*sx*100),sy=float(parent*sy*100),rotation=float(theta))}))
plan=dict(duration=DURATION,fps=FPS,resolution=[W,H],preview_resolution=[1280,720],voice_source='shorts/008-personagens-que-a-internet-estragou/production/00-intro/assets/voz/narracao_completa.wav',voice_source_excerpt=[0,DURATION],voice_changed_pitch=False,voice_changed_speed=False,body_authored_keyframes=BODY,head_authored_keyframes=HEAD,segments=[dict(pose='conversando',start=0,end=4.1),dict(pose='apontando',start=4.1,end=6.7),dict(pose='conversando',start=6.7,end=9.3)],keyframe_space='normalised position, percentage scale, clockwise degrees; neck pivot at image center',frames=frames)
(P/'keyframes.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
# PNGs are separate planes, animated as video layers. Premultiplied alpha avoids dark fringes.
w,h=1280,720;scale=w/W
bg=cv2.resize(cv2.imread(str(M/'fundo.png')),(w,h),interpolation=cv2.INTER_AREA).astype(np.float32)/255
layers={}
for pose in ['conversando','apontando']:
    for part in ['corpo','cabeca','bigode']:
        a=cv2.imread(str(M/f'{pose}_{part}.png'),cv2.IMREAD_UNCHANGED);assert a.shape==(H,W,4)
        a=cv2.resize(a,(w,h),interpolation=cv2.INTER_AREA).astype(np.float32)/255
        a[:,:,:3]*=a[:,:,3:4];layers[pose,part]=a
out=P/'Previa_Conversando_2D.mp4';log=P/'render.log'
cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{w}x{h}','-r',str(FPS),'-i','pipe:0','-i',str(M/'voz_teste.wav'),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','fast','-crf','18','-threads','2','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t',str(DURATION),'-movflags','+faststart',str(out)]
with log.open('w') as stderr:
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=stderr)
    for frame in frames[:-1]:
        canvas=bg.copy()
        for part in ['corpo','cabeca','bigode']:
            tr=frame['layers'][part];A=rotation(tr['rotation'])@np.diag([tr['sx']/100,tr['sy']/100]);center=np.array([w/2,h/2]);target=np.array([tr['x']*w,tr['y']*h]);affine=np.column_stack([A,target-A@center]).astype(np.float32)
            warped=cv2.warpAffine(layers[frame['pose'],part],affine,(w,h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
            canvas=warped[:,:,:3]+canvas*(1-warped[:,:,3:4])
        rendered=np.clip(np.rint(canvas*255),0,255).astype(np.uint8)
        proc.stdin.write(rendered.tobytes())
        if frame['frame'] in [45,129,215]:cv2.imwrite(str(CACHE/f'quadro_{frame["frame"]:03d}.jpg'),rendered)
    proc.stdin.close();status=proc.wait();assert status==0,log.read_text()
print('PREVIEW_RENDERED',out,DURATION,flush=True)
