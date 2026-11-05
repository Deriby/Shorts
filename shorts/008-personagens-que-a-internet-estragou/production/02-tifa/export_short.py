"""Compose each format from its own camera renders and media layouts."""
from pathlib import Path
import subprocess,json,argparse,shutil
import numpy as np
from PIL import Image,ImageOps,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent;p=argparse.ArgumentParser();p.add_argument('--encode-only',action='store_true');p.add_argument('--resume',action='store_true');p.add_argument('--wide',action='store_true');args=p.parse_args();info=json.loads((ROOT/'timeline.json').read_text());wide=args.wide;W,H=(640,360)if wide else(360,640);OW,OH=(1920,1080)if wide else(1080,1920);suffix='16x9'if wide else'9x16';out=ROOT/('renders/final_16x9'if wide else'renders/final');out.mkdir(parents=True,exist_ok=True)
def photo_frame(sh):
 source=sh['source']
 if not wide and source.startswith('call_'):source=source.replace('.png','_vertical.png')
 pic=Image.open(ROOT/'assets/memes'/source).convert('RGB');frame=Image.new('RGB',(W,H),(17,18,23))
 if sh['mood']=='news':
  # Keep the supplied headline readable in both formats; its text is a source, not narration subtitles.
  pic=pic.crop((0,0,pic.width,min(pic.height,300)))
  if wide:
   news=ImageOps.contain(pic,(420,320),Image.Resampling.NEAREST);frame.paste(news,(10,(H-news.height)//2));portrait=ImageOps.contain(Image.open(ROOT/'assets/memes/tifa_retrato.jpg').convert('RGB'),(195,300),Image.Resampling.NEAREST);frame.paste(portrait,(440,(H-portrait.height)//2))
  else:
   news=ImageOps.contain(pic,(W,330),Image.Resampling.NEAREST);frame.paste(news,(0,60));portrait=ImageOps.contain(Image.open(ROOT/'assets/memes/tifa_retrato.jpg').convert('RGB'),(W,240),Image.Resampling.NEAREST);frame.paste(portrait,((W-portrait.width)//2,370))
 else:
  pic=ImageOps.contain(pic,(W,H),Image.Resampling.NEAREST);frame.paste(pic,((W-pic.width)//2,(H-pic.height)//2))
 return frame
if not args.encode_only:
 for sh in info['shots']:
  n=sh['end']-sh['start']+1
  if args.resume and all((out/f'frame_{f:04d}.png').exists()for f in range(sh['start'],sh['end']+1)):continue
  if sh['kind']=='game':
   x='328'if sh['source']=='tifa_intro.mp4'else'95';vf='fps=24,scale=640:360:flags=neighbor'if wide else f'fps=24,crop=304:540:{x}:0,scale=360:640:flags=neighbor'
   subprocess.run(['ffmpeg','-v','error','-y','-threads','1','-filter_threads','1','-ss',str(sh['source_start']),'-i',str(ROOT/'assets/gameplay'/sh['source']),'-an','-vf',vf,'-frames:v',str(n),'-start_number',str(sh['start']),str(out/'frame_%04d.png')],check=True)
  elif sh['kind']=='photo':
   first=out/f"frame_{sh['start']:04d}.png";photo_frame(sh).save(first)
   for f in range(sh['start']+1,sh['end']+1):shutil.copyfile(first,out/f'frame_{f:04d}.png')
 procs=[]
 for worker in range(1):
  log=open(f'/tmp/tifa_worker_{suffix}_{worker}.log','w');cmd=['blender','-b',str(ROOT/'output'/('Dery_Tifa_Master_16x9.blend'if wide else'Dery_Tifa.blend')),'-t','2','--python-exit-code','1','--python',str(ROOT/'render_actor_frames.py'),'--',str(worker),'1']
  if wide:cmd+=['--wide']
  if args.resume:cmd+=['--resume']
  proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT);procs.append((proc,log))
 for proc,log in procs:code=proc.wait();log.close();assert code==0,code
missing=[f for f in range(1,info['frames']+1)if not(out/f'frame_{f:04d}.png').exists()];assert not missing,missing
# Fixed ordered dithering stays on the native pixel grid, never a random flicker.
bayer=np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]],dtype=np.float32);noise=np.tile((bayer+.5)/16-.5,((H+3)//4,(W+3)//4))[:H,:W,None]*8
cmd=['ffmpeg','-v','warning','-nostats','-y','-filter_threads','2','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate','24','-i','pipe:0','-i',str(ROOT/'assets/voz/narracao_mix.wav'),'-vf',f'scale={OW}:{OH}:flags=neighbor','-frames:v',str(info['frames']),'-t',str(info['duration']),'-c:v','libx264','-threads','3','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','44100','-movflags','+faststart',str(ROOT/f'output/Tifa_Personagens_que_a_internet_estragou_{suffix}.mp4')]
proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
try:
 for f in range(1,info['frames']+1):
  rgb=np.asarray(Image.open(out/f'frame_{f:04d}.png').convert('RGB'),dtype=np.float32);assert rgb.shape==(H,W,3);quant=np.clip(np.floor((rgb+noise)/8+.5),0,31)*(255/31);proc.stdin.write(quant.astype(np.uint8).tobytes())
finally:proc.stdin.close()
assert proc.wait()==0;print('TIFA_EXPORT_READY',suffix,flush=True)
