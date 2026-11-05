"""Validate full decode, exact timing, source audio and the moving monitor feed."""
from pathlib import Path
import subprocess,json,hashlib,wave,array,sys
wide="--wide"in sys.argv;resolution=(1920,1080)if wide else(1080,1920);suffix="16x9"if wide else"9x16"
ROOT=Path(__file__).resolve().parent;i=json.loads((ROOT/'timeline.json').read_text());audio=json.loads((ROOT/'audio.json').read_text());path=ROOT/f'output/Tifa_Personagens_que_a_internet_estragou_{suffix}.mp4'
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
p=probe(path);v=next(x for x in p['streams']if x['codec_type']=='video');a=next(x for x in p['streams']if x['codec_type']=='audio')
assert(v['width'],v['height'],v['pix_fmt'],v['r_frame_rate'])==(*resolution,'yuv420p','24/1');assert v['codec_name']=='h264'and a['codec_name']=='aac';assert int(v['nb_frames'])==i['frames'];assert abs(float(p['format']['duration'])-i['duration'])<.03;assert float(a['duration'])>=i['voice_duration']
assert hashlib.sha256((ROOT/'assets/voz/voz_original.mp3').read_bytes()).hexdigest()==audio['sha256']
def samples(p):
 with wave.open(str(p))as w:return w.getframerate(),array.array('h',w.readframes(w.getnframes()))
sr,voice=samples(ROOT/'assets/voz/narracao_completa.wav');mr,mix=samples(ROOT/'assets/voz/narracao_mix.wav');assert sr==mr and mix[:len(voice)]==voice and all(v==0 for v in mix[len(voice):])
feed=next(x for x in probe(ROOT/'assets/gameplay/monitor_montado.mp4')['streams']if x['codec_type']=='video');assert int(feed['nb_frames'])==i['frames']
scene=json.loads((ROOT/('scene_validation_16x9.json'if wide else'scene_validation.json')).read_text());assert scene['original_geometry_max_displacement_m']==0 and max(x['max_facial_split_m']for x in scene['face_checks'])<.00005
subprocess.run(['ffmpeg','-v','error','-threads','2','-i',str(path),'-f','null','-'],check=True)
r=dict(video=path.name,frames=i['frames'],duration=float(p['format']['duration']),resolution=list(resolution),fps=24,codec='H.264 + AAC',size_bytes=path.stat().st_size,full_decode='passed',voice_original_sha256=audio['sha256'],voice_unmodified=True,monitor_frames=int(feed['nb_frames']),scene_checks='passed',ps1_palette='5-bit RGB with fixed 4x4 ordered Bayer pattern, integer nearest-neighbor upscale')
(ROOT/('export_validation_16x9.json'if wide else'export_validation.json')).write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
