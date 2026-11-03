"""Optional local speech recognition; no audio is sent to an external service."""
import sys,json
from pathlib import Path
sys.path.insert(0,'/workspace/tools/shorts_asr')
import sherpa_onnx
import soundfile as sf
ROOT=Path(__file__).resolve().parent
MODEL=Path('/workspace/tools/models/sherpa-onnx-whisper-tiny')
r=sherpa_onnx.OfflineRecognizer.from_whisper(
 encoder=str(MODEL/'tiny-encoder.int8.onnx'),decoder=str(MODEL/'tiny-decoder.int8.onnx'),
 tokens=str(MODEL/'tiny-tokens.txt'),language='pt',task='transcribe',num_threads=2,
 enable_token_timestamps=False,enable_segment_timestamps=True)
samples,sr=sf.read(ROOT/'assets/voz_16k.wav',dtype='float32')
chunks=[]
cuts=[0,16.30,32.18,51.60,len(samples)/sr]
for start,end in zip(cuts,cuts[1:]):
 stream=r.create_stream()
 stream.accept_waveform(sr,samples[round(start*sr):round(end*sr)])
 r.decode_stream(stream)
 result=stream.result
 chunks.append({'start':start,'end':end,'text':result.text,'raw':str(result)})
result={'method':'local sherpa-onnx Whisper tiny; chunks split at measured pauses','chunks':chunks}
(ROOT/'audio_reconhecido.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False))
