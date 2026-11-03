"""Generic Portuguese TTS for a five-second format test, not a clone of the user."""
from pathlib import Path
import sys,json,os,subprocess
sys.path.insert(0,os.environ.get('DERY_TTS_PYTHON_PATH','/workspace/tools/shorts_asr'))
import sherpa_onnx,numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parent
MODEL=Path(os.environ.get('DERY_TTS_MODEL_DIR','/workspace/tools/models/vits-piper-pt_BR-faber-medium'))
config=sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
    vits=sherpa_onnx.OfflineTtsVitsModelConfig(model=str(MODEL/'pt_BR-faber-medium.onnx'),
         tokens=str(MODEL/'tokens.txt'),data_dir=str(MODEL/'espeak-ng-data'),noise_scale=.55,noise_scale_w=.65),num_threads=2))
tts=sherpa_onnx.OfflineTts(config)
text='Esse jogo roda liso. Quem está travando sou eu.'
audio=tts.generate(text,sid=0,speed=1.08)
samples=np.asarray(audio.samples,dtype=np.float32)
sf.write(ROOT/'assets/voz_bruta.wav',samples,audio.sample_rate)
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(ROOT/'assets/voz_bruta.wav'),
                '-af','atempo=0.74,adelay=180|180,apad','-t','5','-ar','48000',str(ROOT/'assets/voz_teste.wav')],check=True)
print(json.dumps({'text':text,'seconds':len(samples)/audio.sample_rate,'sample_rate':audio.sample_rate}))
