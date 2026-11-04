"""Compose clean gameplay cuts and two Blender render partitions, then export MP4."""
from pathlib import Path
import subprocess,json,argparse
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--encode-only',action='store_true');args=p.parse_args()
info=json.loads((ROOT/'timeline.json').read_text());frames=ROOT/'renders/final';frames.mkdir(parents=True,exist_ok=True)
if not args.encode_only:
    source=ROOT/'assets/gameplay/mizzurna_falls_trailer_enviado.mp4'
    for sh in info['shots']:
        if sh['kind']!='game':continue
        x=max(0,min(874,round(sh['focus_x']-203)))
        subprocess.run(['ffmpeg','-v','error','-y','-threads','2','-ss',str(sh['source_start']),'-i',str(source),'-an','-vf',f'fps=24,crop=406:720:{x}:0,scale=360:640:flags=neighbor','-frames:v',str(sh['end']-sh['start']+1),'-start_number',str(sh['start']),str(frames/'frame_%04d.png')],check=True)
    processes=[]
    for worker in range(2):
        log=open(f'/tmp/mizzurna_worker_{worker}.log','w')
        proc=subprocess.Popen(['blender','-b',str(ROOT/'output/Dery_Mizzurna_Falls.blend'),'-t','2','--python-exit-code','1','--python',str(ROOT/'render_actor_frames.py'),'--',str(worker),'2'],stdout=log,stderr=subprocess.STDOUT)
        processes.append((proc,log))
    for proc,log in processes:
        code=proc.wait();log.close();assert code==0,code
missing=[f for f in range(1,info['frames']+1)if not(frames/f'frame_{f:04d}.png').exists()]
assert not missing,missing
palette="format=rgb24,lutrgb=r='floor(val/4)*4':g='floor(val/4)*4':b='floor(val/4)*4'"
subprocess.run(['ffmpeg','-v','warning','-nostats','-y','-filter_threads','2','-framerate','24','-start_number','1','-i',str(frames/'frame_%04d.png'),'-i',str(ROOT/'assets/voz/narracao_mix.wav'),'-vf',palette+',scale=1080:1920:flags=neighbor','-frames:v',str(info['frames']),'-t',str(info['duration']),'-c:v','libx264','-threads','3','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','44100','-movflags','+faststart',str(ROOT/'output/Esse_jogo_destruiu_seu_criador_9x16.mp4')],check=True)
print('MIZZURNA_EXPORT_READY',flush=True)
