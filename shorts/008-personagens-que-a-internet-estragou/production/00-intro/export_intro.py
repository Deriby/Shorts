"""Compose three motivated shots in 16:9, preserving the complete supplied narration."""
from pathlib import Path
import argparse,json,subprocess,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--resume',action='store_true');p.add_argument('--encode-only',action='store_true');args=p.parse_args()
info=json.loads((ROOT/'timeline.json').read_text());out=ROOT/'renders/final';out.mkdir(exist_ok=True)
if not args.encode_only:
 for sh in info['shots']:
  if sh['kind']=='actor':continue
  if args.resume and all((out/f'frame_{f:04d}.png').exists()for f in range(sh['start'],sh['end']+1)):continue
  if sh['kind']=='interface':
   subprocess.run(['ffmpeg','-v','error','-y','-threads','1','-filter_threads','1','-i',str(ROOT/'assets/gameplay/monitor_montado.mp4'),'-an','-frames:v',str(sh['end']),'-start_number','1','-threads','1',str(out/'frame_%04d.png')],check=True)
  else:
   im=Image.open(ROOT/'assets/memes'/sh['source']).convert('RGB');im.save(out/f"frame_{sh['start']:04d}.png")
   for f in range(sh['start']+1,sh['end']+1):shutil.copyfile(out/f"frame_{sh['start']:04d}.png",out/f'frame_{f:04d}.png')
 with open('/tmp/intro_worker.log','w')as log:
  cmd=['blender','-b',str(ROOT/'output/Dery_Intro_Personagens_16x9.blend'),'-t','2','--python-exit-code','1','--python',str(ROOT/'render_actor_frames.py')]
  if args.resume:cmd+=['--','--resume']
  subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
assert all((out/f'frame_{f:04d}.png').exists()for f in range(1,info['frames']+1))
bayer=np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]],dtype=np.float32)
noise=np.tile((bayer+.5)/16-.5,(90,160))[:,:,None]*8
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
cmd=['ffmpeg','-v','warning','-nostats','-y','-filter_threads','2','-f','rawvideo','-pixel_format','rgb24','-video_size','640x360','-framerate','24','-i','pipe:0','-i',str(ROOT/'assets/voz/narracao_mix.wav'),'-vf','scale=1920:1080:flags=neighbor','-frames:v',str(info['frames']),'-t',str(info['duration']),'-c:v','libx264','-threads','3','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','44100','-movflags','+faststart',str(ROOT/'output/Intro_Personagens_que_a_internet_estragou_16x9.mp4')]
proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
try:
 for f in range(1,info['frames']+1):
  t=(f-1)/24;im=Image.open(out/f'frame_{f:04d}.png').convert('RGB')
  if 17.2<=t<21.2:
   ease=smooth((t-17.2)/.3)*(1-smooth((t-20.9)/.3));x=round(-355+369*ease);d=ImageDraw.Draw(im)
   d.rectangle((x,12,x+340,98),fill=(18,29,45),outline=(231,191,83),width=3);d.rectangle((x+3,15,x+337,35),fill=(45,67,95))
   d.text((x+13,25),'ARQUIVO ABERTO',font=ImageFont.truetype(font,11),fill=(225,229,218),anchor='lm')
   d.text((x+170,54),'12 PERSONAGENS',font=ImageFont.truetype(font,24),fill=(246,209,106),anchor='mm')
   d.text((x+170,82),'QUE A INTERNET ESTRAGOU',font=ImageFont.truetype(font,18),fill=(226,231,226),anchor='mm')
  rgb=np.asarray(im,dtype=np.float32);assert rgb.shape==(360,640,3)
  quant=np.clip(np.floor((rgb+noise)/8+.5),0,31)*(255/31);proc.stdin.write(quant.astype(np.uint8).tobytes())
finally:proc.stdin.close()
assert proc.wait()==0
print('INTRO_EXPORT_READY',flush=True)
