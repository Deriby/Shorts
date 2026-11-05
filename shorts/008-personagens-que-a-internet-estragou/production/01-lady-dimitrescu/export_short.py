"""Compose each format from its own camera renders and media layouts."""
from pathlib import Path
import subprocess,json,argparse,shutil
import numpy as np
from PIL import Image,ImageOps,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent;p=argparse.ArgumentParser();p.add_argument('--encode-only',action='store_true');p.add_argument('--wide',action='store_true');args=p.parse_args();info=json.loads((ROOT/'timeline.json').read_text());wide=args.wide;W,H=(640,360)if wide else(360,640);OW,OH=(1920,1080)if wide else(1080,1920);suffix='16x9'if wide else'9x16';out=ROOT/('renders/final_16x9'if wide else'renders/final');out.mkdir(parents=True,exist_ok=True)
def photo_frame(sh):
 source='memelady.jpg'if wide and sh['mood']=='reaction'else sh['source'];pic=Image.open(ROOT/'assets/memes'/source).convert('RGB');frame=Image.new('RGB',(W,H),(17,18,23))
 if wide and sh['mood']=='height':
  image=ImageOps.contain(pic,(345,350),Image.Resampling.NEAREST);frame.paste(image,((345-image.width)//2,(H-image.height)//2));d=ImageDraw.Draw(frame);font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf';d.line((365,28,365,332),fill=(247,193,37),width=3)
  for y in range(42,319,34):d.line((414,y,435 if y%68 else 447,y),fill=(185,184,175),width=2)
  d.line((414,42,414,314),fill=(185,184,175),width=3);d.text((515,143),'2,90 m',font=ImageFont.truetype(font,40),anchor='mm',fill=(247,193,37));d.text((515,205),'CHAPÉU',font=ImageFont.truetype(font,18),anchor='mm',fill='white');d.text((515,233),'E SALTOS',font=ImageFont.truetype(font,18),anchor='mm',fill='white')
 elif wide and sh['mood']=='height_meme':
  split=720
  for box,area in [((0,0,pic.width,split),(0,0,335,360)),((0,split,pic.width,pic.height),(345,0,640,360))]:
   piece=ImageOps.contain(pic.crop(box),(area[2]-area[0],area[3]-area[1]),Image.Resampling.NEAREST);frame.paste(piece,(area[0]+(area[2]-area[0]-piece.width)//2,(H-piece.height)//2))
  ImageDraw.Draw(frame).line((339,18,339,342),fill=(247,193,37),width=2)
 elif wide and sh['mood']=='gamer':frame=ImageOps.fit(pic,(W,H),Image.Resampling.NEAREST,centering=(.5,.35))
 else:
  pic=ImageOps.contain(pic,(W,H),Image.Resampling.NEAREST);frame.paste(pic,((W-pic.width)//2,(H-pic.height)//2))
 return frame
if not args.encode_only:
 for sh in info['shots']:
  n=sh['end']-sh['start']+1
  if sh['kind']=='game':
   x=418 if sh['source']=='lady_phone.mp4'else 328;vf='fps=24,scale=640:360:flags=neighbor'if wide else f'fps=24,crop=304:540:{x}:0,scale=360:640:flags=neighbor'
   subprocess.run(['ffmpeg','-v','error','-y','-threads','1','-filter_threads','1','-ss',str(sh['source_start']),'-i',str(ROOT/'assets/gameplay'/sh['source']),'-an','-vf',vf,'-frames:v',str(n),'-start_number',str(sh['start']),str(out/'frame_%04d.png')],check=True)
  elif sh['kind']=='photo':
   first=out/f"frame_{sh['start']:04d}.png";photo_frame(sh).save(first)
   for f in range(sh['start']+1,sh['end']+1):shutil.copyfile(first,out/f'frame_{f:04d}.png')
 procs=[]
 for worker in range(2):
  log=open(f'/tmp/lady_worker_{suffix}_{worker}.log','w');cmd=['blender','-b',str(ROOT/'output'/('Dery_Lady_Master_16x9.blend'if wide else'Dery_Lady_Dimitrescu.blend')),'-t','2','--python-exit-code','1','--python',str(ROOT/'render_actor_frames.py'),'--',str(worker),'2']
  if wide:cmd+=['--wide']
  proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT);procs.append((proc,log))
 for proc,log in procs:code=proc.wait();log.close();assert code==0,code
missing=[f for f in range(1,info['frames']+1)if not(out/f'frame_{f:04d}.png').exists()];assert not missing,missing
# Fixed ordered dithering stays on the native pixel grid, never a random flicker.
bayer=np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]],dtype=np.float32);noise=np.tile((bayer+.5)/16-.5,((H+3)//4,(W+3)//4))[:H,:W,None]*8
cmd=['ffmpeg','-v','warning','-nostats','-y','-filter_threads','2','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate','24','-i','pipe:0','-i',str(ROOT/'assets/voz/narracao_mix.wav'),'-vf',f'scale={OW}:{OH}:flags=neighbor','-frames:v',str(info['frames']),'-t',str(info['duration']),'-c:v','libx264','-threads','3','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','44100','-movflags','+faststart',str(ROOT/f'output/Lady_Dimitrescu_Personagens_que_a_internet_estragou_{suffix}.mp4')]
proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
try:
 for f in range(1,info['frames']+1):
  rgb=np.asarray(Image.open(out/f'frame_{f:04d}.png').convert('RGB'),dtype=np.float32);assert rgb.shape==(H,W,3);quant=np.clip(np.floor((rgb+noise)/8+.5),0,31)*(255/31);proc.stdin.write(quant.astype(np.uint8).tobytes())
finally:proc.stdin.close()
assert proc.wait()==0;print('LADY_EXPORT_READY',suffix,flush=True)
