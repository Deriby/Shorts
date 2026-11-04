"""Validate the delivered encode and preservation of the original recording."""
from pathlib import Path
import subprocess,json,hashlib,wave,array
ROOT=Path(__file__).resolve().parent
info=json.loads((ROOT/'timeline.json').read_text());audio=json.loads((ROOT/'audio.json').read_text())
video=ROOT/'output/Esse_jogo_destruiu_seu_criador_9x16.mp4'
def probe(path):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
p=probe(video);v=next(s for s in p['streams']if s['codec_type']=='video');a=next(s for s in p['streams']if s['codec_type']=='audio')
assert(v['width'],v['height'],v['pix_fmt'])==(1080,1920,'yuv420p')
assert v['codec_name']=='h264'and a['codec_name']=='aac'
assert v['r_frame_rate']=='24/1'and int(v['nb_frames'])==info['frames']
assert abs(float(p['format']['duration'])-info['duration'])<.03
assert float(a['duration'])>=info['voice_duration']
assert hashlib.sha256((ROOT/audio['original']).read_bytes()).hexdigest()==audio['sha256']
feed=next(x for x in probe(ROOT/'assets/gameplay/monitor_montado.mp4')['streams']if x['codec_type']=='video')
assert int(feed['nb_frames'])==info['frames']
scene=json.loads((ROOT/'scene_validation.json').read_text())
assert max(x['max_facial_split_m']for x in scene['face_checks'])<.00005
assert max(x['hand_surface_to_badge_contact_m']for x in scene['badge_contacts'])<.010
def samples(path):
    with wave.open(str(path))as w:return w.getframerate(),array.array('h',w.readframes(w.getnframes()))
sr,original=samples(ROOT/'assets/voz/narracao_completa.wav');mix_sr,mixed=samples(ROOT/'assets/voz/narracao_mix.wav');assert sr==mix_sr
for t0,t1 in [(0,33.24),(33.57,36.17),(36.71,info['voice_duration'])]:
    assert original[round(t0*sr):round(t1*sr)]==mixed[round(t0*sr):round(t1*sr)]
subprocess.run(['ffmpeg','-v','error','-threads','2','-i',str(video),'-f','null','-'],check=True)
result={'video':video.name,'duration':float(p['format']['duration']),'frames':int(v['nb_frames']),'resolution':[v['width'],v['height']],'fps':24,'codec':'H.264 + AAC','size_bytes':video.stat().st_size,'full_decode':'passed','original_mp3_sha256':audio['sha256'],'unmodified_voice_outside_sfx_windows':True,'monitor_frames':int(feed['nb_frames']),'scene_checks':'passed'}
(ROOT/'export_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
