"""Validate export and its zero-offset mix against the original voice plus quiet FX."""
from pathlib import Path
import subprocess,json
import numpy as np

ROOT=Path(__file__).resolve().parent
movie=ROOT/'output/Dery_Terra_Parou.mp4'
info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_name,codec_type,width,height,r_frame_rate,nb_frames,sample_rate,channels','-of','json',str(movie)]))
v=next(x for x in info['streams']if x['codec_type']=='video')
a=next(x for x in info['streams']if x['codec_type']=='audio')
assert (v['width'],v['height'])==(1080,1920)
assert v['r_frame_rate']=='24/1' and int(v['nb_frames'])==1330
assert abs(float(info['format']['duration'])-1330/24)<.08
assert a['channels']==1 and a['sample_rate']=='48000'
subprocess.run(['ffmpeg','-v','error','-i',str(movie),'-f','null','-'],check=True)

def pcm(path):
    return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-ac','1','-ar','48000','-f','f32le','-']),dtype='<f4').astype(np.float64)

voice=pcm(ROOT/'assets/voz_original.mp3')
fx=pcm(ROOT/'assets/efeitos_originais.wav')
encoded=pcm(movie)
assert len(fx)==len(voice) and len(encoded)>=len(voice)
expected=voice+fx
actual=encoded[:len(expected)]
corr=float(np.dot(expected,actual)/np.sqrt(np.dot(expected,expected)*np.dot(actual,actual)))
ratio=float(np.sqrt(np.mean(actual*actual)/np.mean(expected*expected)))
assert corr>.99 and .97<ratio<1.03,(corr,ratio)
report={'movie':info,'full_decode':'passed','source_voice_seconds':len(voice)/48000,
        'mix_correlation_zero_offset':corr,'mix_rms_ratio':ratio,
        'voice_speed_changed':False,'voice_gain':1.0,'captions_added':False,
        'edited_shots':21,'setups':['town street','car exterior and interior','coast','Earth globe','Sun-Earth orbit']}
(ROOT/'output/validacao_video.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False))
