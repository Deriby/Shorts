from pathlib import Path
import subprocess,numpy as np,json,wave
from scipy.signal import correlate,correlation_lags
base=Path(__file__).resolve().parent.parent
out=base/'15-teste-estilo-filmora/renders/midias'
out.mkdir(parents=True,exist_ok=True)
def get(path,start,dur,ch):
 b=subprocess.check_output(['ffmpeg','-v','error','-ss',str(start),'-t',str(dur),'-i',str(path),'-vn','-ar','44100','-ac',str(ch),'-f','f32le','pipe:1'])
 return np.frombuffer(b,'<f4').reshape(-1,ch).copy()
y=get(base/'14-montagem-longo/assets/Edicao_usuario_ate_2B.mp4',79.5,12,2)
x=get(base/'02-tifa/output/Tifa_Personagens_que_a_internet_estragou_16x9.mp4',79.5-78.5166667,12,1)[:,0]
mono=y.mean(axis=1)
c=correlate(mono[:200000],x[:200000],mode='full',method='fft');lags=correlation_lags(min(200000,len(mono)),min(200000,len(x)))
valid=abs(lags)<2205;k=np.argmax(c[valid]);lag=int(lags[valid][k])
# x_aligned[t] = x[t-lag]. Trim unpaired edge samples.
start=max(0,lag);end=min(len(y),len(x)+lag)
z=x[start-lag:end-lag];y=y[start:end]
gain=float(np.dot(y.mean(axis=1),z)/np.dot(z,z))
res=y-z[:,None]*gain
# tame AAC difference at high frequencies and use quiet background level
from scipy.signal import butter,sosfilt
res=sosfilt(butter(4,8000,fs=44100,output='sos'),res,axis=0).astype(np.float32)
rms=float(np.sqrt(np.mean(res**2)));res*=10**(-30/20)/max(rms,1e-8)
with wave.open(str(out/'musica_referencia.wav'),'wb')as w:
 w.setnchannels(2);w.setsampwidth(2);w.setframerate(44100);w.writeframes((np.clip(res,-1,.999)*32768).astype('<i2').tobytes())
(out.parent.parent/'recuperacao_trilha.json').write_text(json.dumps({'reference_start':79.5,'length':len(res)/44100,'sample_lag':lag,'voice_gain':gain,'music_original_rms':rms,'method':'Subtract aligned original Tifa master narration, lowpass at 8kHz; extracted stereo music from user reference'}))
print('RECOVERY',lag,gain,rms,flush=True)
subprocess.run(['ffmpeg','-v','error','-i',str(out/'musica_referencia.wav'),'-t','8','-ar','16000','-ac','1','-y','/tmp/recovered_music_asr.wav'],check=True)
