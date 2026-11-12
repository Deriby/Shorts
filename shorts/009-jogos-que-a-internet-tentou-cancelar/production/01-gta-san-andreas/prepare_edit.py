"""Phrase-led edit metadata and separated voice, supplied backing and retro SFX."""
from pathlib import Path
import json,subprocess,wave,math
import numpy as np

P=Path(__file__).resolve().parent;A=P/'assets';info=json.loads((P/'timeline.json').read_text())
sound=A/'audio';sound.mkdir(exist_ok=True);SR=44100
def save(p,x):
    if x.ndim==1:x=x[:,None]
    with wave.open(str(p),'wb')as w:
        w.setnchannels(x.shape[1]);w.setsampwidth(2);w.setframerate(SR)
        w.writeframes(np.clip(np.round(x*32767),-32768,32767).astype('<i2').tobytes())
def read(p):
    with wave.open(str(p))as w:
        assert w.getframerate()==SR
        return np.frombuffer(w.readframes(w.getnframes()),'<i2').reshape(-1,w.getnchannels()).astype(float)/32768
def effect(name,duration,f0,f1,noise=0):
    t=np.arange(round(duration*SR))/SR
    phase=2*np.pi*(f0*t+(f1-f0)/(2*duration)*t*t)
    envelope=np.minimum(t/.008,1)*np.exp(-t/(duration*.24))
    rng=np.random.default_rng(4401)
    x=(np.sin(phase)*.55+np.sin(phase*2)*.15+rng.uniform(-1,1,len(t))*noise)*envelope*.17
    save(sound/name,x)
effect('ui_desbloqueio.wav',.22,540,1050)
effect('selo_ao.wav',.16,110,65,.7)
effect('caixas.wav',.20,420,180,.25)
effect('plop_comico.wav',.24,290,75)
events=[dict(start=16.65,file='ui_desbloqueio.wav'),dict(start=24.2,file='selo_ao.wav'),
        dict(start=28.15,file='caixas.wav'),dict(start=30.85,file='ui_desbloqueio.wav'),
        dict(start=40.38,file='plop_comico.wav'),dict(start=52.4,file='plop_comico.wav')]
# Backing is supplied audio from the user's mod showcase, very low under voice.
subprocess.run(['ffmpeg','-v','error','-y','-ss','12','-i',str(A/'gameplay/cenarios_mod_grafico.mp4'),
                '-t',str(info['duration']),'-vn','-ar',str(SR),'-ac','2',str(sound/'trilha_fonte.wav')],check=True)
voice=read(A/'voz/voz_timeline.wav');n=len(voice)
music=read(sound/'trilha_fonte.wav')
if len(music)<n:music=np.tile(music,(math.ceil(n/len(music)),1))
music=music[:n]*.035
t=np.arange(n)/SR
music*=np.minimum(t/.3,1)[:,None]*np.minimum(np.maximum(info['duration']-t,0)/.3,1)[:,None]
# Further ducking follows the measured narration envelope; no time/pitch edits.
energy=np.convolve(np.abs(voice[:,0]),np.ones(2205)/2205,mode='same')
music*=np.where(energy[:,None]>.035,.45,1)
save(sound/'trilha_baixa.wav',music)
mix=np.repeat(voice,2,axis=1)+music
for event in events:
    fx=read(sound/event['file']);start=round(event['start']*SR);count=min(len(fx),n-start)
    mix[start:start+count]+=np.repeat(fx[:count],2,axis=1)
peak=float(np.max(np.abs(mix)));gain=min(1,.97/max(peak,.0001))
save(sound/'mix_final.wav',mix*gain)
(sound/'trilha_fonte.wav').unlink()
titles=[dict(start=0,end=2.1,text='GTA SAN ANDREAS',y=.84),
        dict(start=9.2,end=10.55,text='2005',y=.84),
        dict(start=10.55,end=14.1,text='HOT COFFEE',y=.84),
        dict(start=19.0,end=21.25,text='DEU RUIM...',y=.84),
        dict(start=52.4,end=53.4,text='CAFÉ ACOMPANHADO',y=.83)]
edits=[]
for sh in info['shots']:
    kind=sh['kind'];a=(sh['start']-1)/info['fps'];b=sh['end']/info['fps']
    z={'host':1.07,'close':1.055,'archive':1.045,'shop':1.05,'photo':1.08,'game':1.035,'monitor':1.0}[kind]
    edits.append(dict(shot=sh['id'],start=a,end=b,zoom_start=1.,zoom_end=z,
                      portrait_zoom_end=min(z,1.045),focus=[.5,.5]))
data=dict(duration=info['duration'],delivery_fps=30,animation_fps=info['fps'],
          voice_full=True,voice_speed=1,voice_pitch_unchanged=True,mix_gain=gain,
          music_source='Supplied graphics-mod showcase; audio 12 seconds onwards, quiet and ducked',
          sfx=events,titles=titles,edits=edits,whole_frame_shake=False,subtitles=False)
(P/'edicao.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print('EDIT_AUDIO_READY',peak,gain,flush=True)
