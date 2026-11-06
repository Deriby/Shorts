"""Validate the sole horizontal export, voice preservation and full decoding."""
from pathlib import Path
import array,hashlib,json,subprocess,wave
ROOT=Path(__file__).resolve().parent;info=json.loads((ROOT/'timeline.json').read_text());audio=json.loads((ROOT/'audio.json').read_text());path=ROOT/'output/Encerramento_Personagens_que_a_internet_estragou_16x9.mp4'
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
p=probe(path);v=next(x for x in p['streams']if x['codec_type']=='video');a=next(x for x in p['streams']if x['codec_type']=='audio')
assert(v['width'],v['height'],v['r_frame_rate'],v['codec_name'],v['pix_fmt'])==(1920,1080,'24/1','h264','yuv420p')
assert a['codec_name']=='aac'and float(a['duration'])>=info['voice_duration'];assert int(v['nb_frames'])==info['frames'];assert abs(float(p['format']['duration'])-info['duration'])<.03
assert hashlib.sha256((ROOT/'assets/voz/voz_original.mp3').read_bytes()).hexdigest()==audio['sha256']
def samples(p):
 with wave.open(str(p))as w:return w.getframerate(),array.array('h',w.readframes(w.getnframes()))
sr,voice=samples(ROOT/'assets/voz/narracao_completa.wav');mr,mix=samples(ROOT/'assets/voz/narracao_mix.wav');assert sr==mr and mix[:len(voice)]==voice and all(x==0 for x in mix[len(voice):])
feed=next(x for x in probe(ROOT/'assets/gameplay/monitor_montado.mp4')['streams']if x['codec_type']=='video');assert int(feed['nb_frames'])==info['frames']
scene=json.loads((ROOT/'scene_validation.json').read_text());assert scene['original_geometry_max_displacement_m']==0 and scene['seated_support_stable']and scene['camera_continuous']
assert len(info['shots'])==2 and info['picture_cuts']==1
subprocess.run(['ffmpeg','-v','error','-threads','2','-i',str(path),'-f','null','-'],check=True)
report=dict(video=path.name,frames=info['frames'],duration=float(p['format']['duration']),resolution=[1920,1080],fps=24,codec='H.264 + AAC',size_bytes=path.stat().st_size,full_decode='passed',voice_original_sha256=audio['sha256'],voice_unmodified=True,scene_checks='passed',picture_shots=2,picture_cuts=1,room_shot_camera='continuous',vertical_export=False,ps1_palette='5-bit RGB with fixed 4x4 Bayer dither and integer nearest-neighbor upscale')
(ROOT/'export_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
