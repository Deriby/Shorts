"""Recupera acompanhamento estéreo usando as narrações limpas já disponíveis."""
from pathlib import Path
import subprocess,json,wave
import numpy as np
from scipy.signal import correlate,correlation_lags,butter,sosfilt
P=Path(__file__).resolve().parent;PROD=P.parent
OUT=P/'renders/trilhas';OUT.mkdir(parents=True,exist_ok=True)
REFERENCE=PROD/'14-montagem-longo/assets/Edicao_usuario_ate_2B.mp4'
CASES=[('a','02-tifa',79.5,78.5166667,12,'Cooped Up'),
       ('b','04-ankha',156,153.7666667,24,'The Scuffler'),
       ('c','03-chun-li',112,110.7333333,12,'Bully — Searching')]
def get(path,start,duration,channels):
    b=subprocess.check_output(['ffmpeg','-v','error','-ss',str(start),'-t',str(duration),'-i',str(path),
                               '-vn','-ar','44100','-ac',str(channels),'-f','f32le','pipe:1'])
    return np.frombuffer(b,'<f4').reshape(-1,channels).copy()
def main():
    report=[]
    for key,folder,start,origin,duration,title in CASES:
        target=OUT/(key+'.wav')
        if target.exists():continue
        source=next((PROD/folder/'output').glob('*16x9.mp4'))
        y=get(REFERENCE,start,duration,2);x=get(source,start-origin,duration,1)[:,0]
        corr=correlate(y[:200000].mean(axis=1),x[:200000],mode='full',method='fft')
        lags=correlation_lags(min(200000,len(y)),min(200000,len(x)));ok=abs(lags)<2205
        lag=int(lags[ok][np.argmax(corr[ok])]);lo=max(0,lag);hi=min(len(y),len(x)+lag)
        x=x[lo-lag:hi-lag];y=y[lo:hi]
        gain=float(np.dot(y.mean(axis=1),x)/np.dot(x,x))
        residual=y-x[:,None]*gain
        residual=sosfilt(butter(4,8000,fs=44100,output='sos'),residual,axis=0).astype('float32')
        rms=float(np.sqrt(np.mean(residual**2)));residual*=10**(-30/20)/max(rms,1e-8)
        with wave.open(str(target),'wb')as w:
            w.setnchannels(2);w.setsampwidth(2);w.setframerate(44100)
            w.writeframes((np.clip(residual,-1,.999)*32768).astype('<i2').tobytes())
        record={'id':key,'title_from_user_project':title,'reference_start':start,'duration':len(residual)/44100,
                'voice_alignment_samples':lag,'voice_subtraction_gain':gain,'original_residual_rms':rms}
        report.append(record);print('MUSIC',json.dumps(record),flush=True)
    if report:(P/'trilhas.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
