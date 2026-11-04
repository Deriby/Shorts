"""Render and export the five-second directing test in both aspect ratios."""
from pathlib import Path
import json,argparse,subprocess
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--encode-only',action='store_true');args=p.parse_args()
project=ROOT/'output/Dery_Teste_Direcao_5s.blend';frames=ROOT/'renders/direction_test';frames.mkdir(parents=True,exist_ok=True)
if not args.encode_only:
    subprocess.run(['blender','-b',str(project),'-t','4','--python-exit-code','1','-o',str(frames/'frame_'),'-F','PNG','-s','1','-e','120','-a'],check=True)
assert all((frames/f'frame_{f:04d}.png').exists()and(frames/f'frame_{f:04d}.png').stat().st_mtime>=project.stat().st_mtime for f in range(1,121))
shots=json.loads((ROOT/'direction_test_timeline.json').read_text())['shots'];expr=str(shots[-1]['x_end'])
for shot in reversed(shots):
    first=shot['start']-1;last=shot['end']-1;x=shot['x_start'];dx=shot['x_end']-x
    expr=f'if(between(n,{first},{last}),{x}+({dx})*(n-{first})/{max(1,last-first)},{expr})'
bayer='-3+4*mod(X,2)+6*mod(Y,2)-8*mod(X,2)*mod(Y,2)'
channels=':'.join(f"{c}='clip(floor(({c}(X,Y)+({bayer}))/8)*8,0,255)'"for c in'rgb')
filters=f"[0:v]format=gbrp,geq={channels},scale=1920:1080:flags=neighbor,split=2[master][v];[v]crop=608:1080:x='{expr}':y=0,scale=1080:1920:flags=neighbor[short]"
common=['-t','5','-c:v','libx264','-threads','2','-preset','veryfast','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','44100','-movflags','+faststart']
subprocess.run(['ffmpeg','-v','warning','-nostats','-y','-framerate','24','-start_number','1','-i',str(frames/'frame_%04d.png'),'-i',str(ROOT/'assets/voz/teste_direcao_5s.wav'),'-filter_complex',filters,'-map','[master]','-map','1:a',*common,str(ROOT/'output/Dery_Teste_Direcao_5s_16x9.mp4'),'-map','[short]','-map','1:a',*common,str(ROOT/'output/Dery_Teste_Direcao_5s_9x16.mp4')],check=True)
