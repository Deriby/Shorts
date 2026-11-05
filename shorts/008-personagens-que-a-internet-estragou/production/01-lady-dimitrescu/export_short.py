"""Compose media and actor frames; export sharp PS1 5-bit RGB with ordered dithering."""
from pathlib import Path
import subprocess,json,argparse,shutil
import numpy as np
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parent;p=argparse.ArgumentParser();p.add_argument('--encode-only',action='store_true');args=p.parse_args();info=json.loads((ROOT/'timeline.json').read_text());out=ROOT/'renders/final';out.mkdir(parents=True,exist_ok=True)
if not args.encode_only:
 for sh in info['shots']:
  n=sh['end']-sh['start']+1
  if sh['kind']=='game':
   x=418 if sh['source']=='lady_phone.mp4'else 328
   subprocess.run(['ffmpeg','-v','error','-y','-threads','1','-filter_threads','1','-ss',str(sh['source_start']),'-i',str(ROOT/'assets/gameplay'/sh['source']),'-an','-vf',f'fps=24,crop=304:540:{x}:0,scale=360:640:flags=neighbor','-frames:v',str(n),'-start_number',str(sh['start']),str(out/'frame_%04d.png')],check=True)
  elif sh['kind']=='photo':
   pic=Image.open(ROOT/'assets/memes'/sh['source']).convert('RGB');pic=ImageOps.contain(pic,(360,640),Image.Resampling.NEAREST);frame=Image.new('RGB',(360,640),(17,18,23));frame.paste(pic,((360-pic.width)//2,(640-pic.height)//2));first=out/f"frame_{sh['start']:04d}.png";frame.save(first)
   for f in range(sh['start']+1,sh['end']+1):shutil.copyfile(first,out/f'frame_{f:04d}.png')
 procs=[]
 for worker in range(2):
  log=open(f'/tmp/lady_worker_{worker}.log','w');proc=subprocess.Popen(['blender','-b',str(ROOT/'output/Dery_Lady_Dimitrescu.blend'),'-t','2','--python-exit-code','1','--python',str(ROOT/'render_actor_frames.py'),'--',str(worker),'2'],stdout=log,stderr=subprocess.STDOUT);procs.append((proc,log))
 for proc,log in procs:code=proc.wait();log.close();assert code==0,code
missing=[f for f in range(1,info['frames']+1)if not(out/f'frame_{f:04d}.png').exists()];assert not missing,missing
# A fixed 4x4 Bayer pattern belongs to the native pixel grid, with no random flicker.
bayer=np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]],dtype=np.float32);noise=np.tile((bayer+.5)/16-.5,(160,90))[:,:,None]*8
cmd=['ffmpeg','-v','warning','-nostats','-y','-filter_threads','2','-f','rawvideo','-pixel_format','rgb24','-video_size','360x640','-framerate','24','-i','pipe:0','-i',str(ROOT/'assets/voz/narracao_mix.wav'),'-vf','scale=1080:1920:flags=neighbor','-frames:v',str(info['frames']),'-t',str(info['duration']),'-c:v','libx264','-threads','3','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','44100','-movflags','+faststart',str(ROOT/'output/Lady_Dimitrescu_Personagens_que_a_internet_estragou_9x16.mp4')]
proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
try:
 for f in range(1,info['frames']+1):
  rgb=np.asarray(Image.open(out/f'frame_{f:04d}.png').convert('RGB'),dtype=np.float32);quant=np.clip(np.floor((rgb+noise)/8+.5),0,31)*(255/31);proc.stdin.write(quant.astype(np.uint8).tobytes())
finally:proc.stdin.close()
assert proc.wait()==0;print('LADY_EXPORT_READY',flush=True)
