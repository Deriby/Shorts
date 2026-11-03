"""Original low-volume foley; voice keeps its original gain and timing."""
from pathlib import Path
import subprocess
import numpy as np
from scipy import signal,ndimage
from scipy.io import wavfile

ROOT=Path(__file__).resolve().parent
SR=48000
voice=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(ROOT/'assets/voz_original.mp3'),'-ac','1','-ar',str(SR),'-f','f32le','-']),dtype='<f4').astype(np.float64)
fx=np.zeros_like(voice)
rng=np.random.default_rng(82)

def add(start,duration,kind,amp):
    n=round(duration*SR); t=np.arange(n)/SR
    if kind=='thud':
        x=np.sin(2*np.pi*68*t)*np.exp(-t*22)+rng.normal(size=n)*.12*np.exp(-t*40)
    elif kind=='metal':
        phase=2*np.pi*(350*t-65*t*t)
        x=(np.sin(phase)+.35*np.sin(phase*2.7))*np.sin(np.linspace(0,np.pi,n))**2
    elif kind=='skid':
        x=np.sin(2*np.pi*(1200*t-270*t*t))*.7+rng.normal(size=n)*.3
        x*=np.sin(np.linspace(0,np.pi,n))**2
    else:
        raw=rng.normal(size=n)
        hi=800 if kind=='surf' else 1400
        sos=signal.butter(3,[100,hi],btype='bandpass',fs=SR,output='sos')
        x=signal.sosfilt(sos,raw)*np.sin(np.linspace(0,np.pi,n))**2
    x=x/(np.max(np.abs(x))+1e-10)*amp
    a=round(start*SR); b=min(len(fx),a+n)
    fx[a:b]+=x[:b-a]

for event in [(.55,.25,'wind',.035),(4.2,.70,'skid',.07),(5.65,.20,'thud',.06),
              (20.8,3.5,'wind',.12),(24.3,5.5,'surf',.12),(32.25,1.3,'metal',.045),
              (32.42,.15,'thud',.07),(37.4,.28,'thud',.085),(40.84,.25,'wind',.035)]:
    add(*event)
rms=np.sqrt(ndimage.uniform_filter1d(voice*voice,size=2400))
duck=np.clip(.07/(rms+.04),.25,1)
fx*=duck
headroom=np.maximum(0,.975-np.abs(voice))
fx=np.clip(fx,-headroom,headroom)
wavfile.write(ROOT/'assets/efeitos_originais.wav',SR,(fx*32767).astype(np.int16))
print('Seconds:',len(voice)/SR,'FX peak:',round(float(np.max(abs(fx))),4),'voice gain: 1.0')
