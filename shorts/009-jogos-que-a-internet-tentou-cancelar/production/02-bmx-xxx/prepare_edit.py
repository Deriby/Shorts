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
events=[dict(start=12.8,file='ui_desbloqueio.wav'),dict(start=14.0,file='plop_comico.wav'),
        dict(start=20.2,file='selo_ao.wav'),dict(start=22.8,file='caixas.wav'),
        dict(start=28.1,file='ui_desbloqueio.wav'),dict(start=42.2,file='plop_comico.wav')]
# Original quiet retro synth backing; no extra speech from source gameplay.
note_sr=np.arange(round(info['duration']*SR))/SR
notes=[130.8128,164.8138,195.9977,146.8324]
x=np.zeros((len(note_sr),2))
for k in range(math.ceil(info['duration']/2)):
 start=round(k*2*SR);count=min(2*SR,len(note_sr)-start);tt=np.arange(count)/SR
 env=np.minimum(tt/.035,1)*np.exp(-tt/1.1);freq=notes[k%4]
 soundwave=(np.sin(2*np.pi*freq*tt)+.23*np.sin(2*np.pi*freq*2*tt))*env*.16
 x[start:start+count]=soundwave[:,None]
save(sound/'trilha_fonte.wav',x)
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
titles=[dict(start=0,end=2.84,text='BMX XXX',y=.84),
        dict(start=3.7,end=5.7,text='2002',y=.84),
        dict(start=11.6,end=14.6,text='IDEIA “GENIAL”',y=.84),
        dict(start=19.5,end=21.2,text='DEU RUIM...',y=.84),
        dict(start=42.0,end=info['duration'],text='DUAS RODAS...',y=.85)]
edits=[]
for sh in info['shots']:
    kind=sh['kind'];a=(sh['start']-1)/info['fps'];b=sh['end']/info['fps']
    z={'host':1.07,'close':1.055,'archive':1.045,'shop':1.05,'photo':1.08,'game':1.035,'monitor':1.0}[kind]
    edits.append(dict(shot=sh['id'],start=a,end=b,zoom_start=1.,zoom_end=z,
                      portrait_zoom_end=min(z,1.045),focus=[.5,.5]))
data=dict(duration=info['duration'],delivery_fps=30,animation_fps=info['fps'],
          voice_full=True,voice_speed=1,voice_pitch_unchanged=True,mix_gain=gain,
          music_source='Original quiet retro synth notes; narration ducking',
          sfx=events,titles=titles,edits=edits,whole_frame_shake=False,subtitles=False)
(P/'edicao.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print('EDIT_AUDIO_READY',peak,gain,flush=True)
