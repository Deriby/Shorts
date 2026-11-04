"""Render only 3D shots, combine with the supplied gameplay, export portrait."""
from pathlib import Path
import json,subprocess,argparse
ROOT=Path(__file__).resolve().parent;p=argparse.ArgumentParser();p.add_argument('--encode-only',action='store_true');args=p.parse_args()
info=json.loads((ROOT/'timeline.json').read_text());frames=ROOT/'renders/final';frames.mkdir(parents=True,exist_ok=True)
project=ROOT/'output/Dery_GTA_POSTAL2.blend';source=ROOT/'assets/gameplay/san_andreas_postal2_enviado.mp4'
if not args.encode_only:
    for shot in info['shots']:
        if shot['kind']!='game':continue
        x=max(0,min(874,round(shot['focus_x']-202.5)))
        subprocess.run(['ffmpeg','-v','error','-y','-threads','2','-ss',str(shot['source_start']),'-i',str(source),'-an','-vf',f'fps=24,crop=406:720:{x}:0,scale=360:640:flags=neighbor','-frames:v',str(shot['end']-shot['start']+1),'-start_number',str(shot['start']),str(frames/'frame_%04d.png')],check=True)
    subprocess.run(['blender','-b',str(project),'-t','4','--python-exit-code','1','--python',str(ROOT/'render_actor_frames.py')],check=True)
missing=[f for f in range(1,info['frames']+1)if not(frames/f'frame_{f:04d}.png').exists()]
assert not missing,missing
bayer='-3+4*mod(X,2)+6*mod(Y,2)-8*mod(X,2)*mod(Y,2)';channels=':'.join(f"{c}='clip(floor(({c}(X,Y)+({bayer}))/8)*8,0,255)'"for c in'rgb')
subprocess.run(['ffmpeg','-v','warning','-nostats','-y','-framerate','24','-start_number','1','-i',str(frames/'frame_%04d.png'),'-i',str(ROOT/'assets/voz/narracao_mix.wav'),'-vf','format=gbrp,geq='+channels+',scale=1080:1920:flags=neighbor','-frames:v',str(info['frames']),'-t',str(info['duration']),'-c:v','libx264','-threads','3','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','44100','-movflags','+faststart',str(ROOT/'output/Misturaram_GTA_com_POSTAL_2_9x16.mp4')],check=True)
print('POSTAL_EXPORT_READY',flush=True)
