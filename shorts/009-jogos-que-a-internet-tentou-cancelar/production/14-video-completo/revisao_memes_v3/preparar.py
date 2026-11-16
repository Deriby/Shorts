"""Prepare sharp meme cards/popups and short muted videos; originals stay in bank."""
from pathlib import Path
import json,subprocess,hashlib,wave
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from PIL import Image,ImageFilter,ImageEnhance,ImageDraw
P=Path(__file__).resolve().parent;R=next(p for p in P.parents if(p/'AGENTS.md').exists());B=R/'assets/biblioteca_memes';C=Path('/workspace/attachments/memes009/preparo');C.mkdir(parents=True,exist_ok=True)
F=P/'output/Filmora';M=F/'midias';M.mkdir(parents=True,exist_ok=True)
plan=json.loads((P/'plano_memes.json').read_text());bank={x['tag']:x for x in json.loads((B/'catalogo.json').read_text())['items']}
def run(cmd):subprocess.run(cmd,check=True)
def picture(im,style):
 im=im.convert('RGB')
 if style=='popup':
  canvas=Image.new('RGBA',(1920,1080));factor=min(510/im.width,470/im.height);im=im.resize((round(im.width*factor),round(im.height*factor)),Image.Resampling.LANCZOS);x=1390+(510-im.width)//2;y=460+(470-im.height)//2
  shadow=Image.new('RGBA',canvas.size);d=ImageDraw.Draw(shadow);d.rectangle((x+7,y+9,x+im.width+14,y+im.height+16),fill=(0,0,0,160));shadow=shadow.filter(ImageFilter.GaussianBlur(10));canvas.alpha_composite(shadow);d=ImageDraw.Draw(canvas);d.rectangle((x-4,y-4,x+im.width+3,y+im.height+3),fill=(247,205,54,255));canvas.paste(im,(x,y));return canvas
 bg=im.resize((1920,1080),Image.Resampling.BILINEAR).filter(ImageFilter.GaussianBlur(30));bg=ImageEnhance.Brightness(bg).enhance(.23);factor=min(1640/im.width,900/im.height);im=im.resize((round(im.width*factor),round(im.height*factor)),Image.Resampling.LANCZOS);bg.paste(im,((1920-im.width)//2,(1080-im.height)//2));return bg

def prepare(c):
 a=bank[c['asset_tag']];src=B/a['relative_file'];suffix='.mp4'if a['mime'].startswith('video')else'.png';dest=M/(c['id']+'_'+c['asset_tag']+suffix);duration=c['frames']/30
 if dest.exists() and dest.stat().st_size>0:
  c['prepared_file']=dest.name;c['prepared_sha256']=hashlib.sha256(dest.read_bytes()).hexdigest();return c
 if suffix=='.png':picture(Image.open(src),c['style']).save(dest)
 else:
  still=C/(c['id']+'.png');run(['ffmpeg','-v','error','-threads','1','-ss',str(c['source_start']),'-i',str(src),'-frames:v','1','-threads','1','-y',str(still)])
  bg=picture(Image.open(still),'card');# Replace central still with background only.
  base=Image.open(still).convert('RGB').resize((1920,1080)).filter(ImageFilter.GaussianBlur(30));base=ImageEnhance.Brightness(base).enhance(.23);base.save(C/(c['id']+'_bg.png'))
  vf='[1:v]scale=1640:900:force_original_aspect_ratio=decrease,setsar=1[v];[0:v][v]overlay=(W-w)/2:(H-h)/2:shortest=1,format=yuv420p[out]'
  run(['ffmpeg','-v','error','-threads','1','-loop','1','-framerate','30','-i',str(C/(c['id']+'_bg.png')),'-ss',str(c['source_start']),'-i',str(src),'-filter_complex_threads','1','-filter_complex',vf,'-map','[out]','-an','-t',str(duration),'-r','30','-c:v','libx264','-preset','veryfast','-crf','18','-threads','1','-movflags','+faststart','-y',str(dest)])
 c['prepared_file']=dest.name;c['prepared_sha256']=hashlib.sha256(dest.read_bytes()).hexdigest();return c
with ThreadPoolExecutor(max_workers=2)as pool:plan['cues']=list(pool.map(prepare,plan['cues']))
sounds=[]
for tag in sorted({c['sound_tag']for c in plan['cues']if c['sound_tag']}):
 a=bank[tag];dest=M/('som_'+tag+'.wav');length=.35 if tag=='A28'else .65
 run(['ffmpeg','-v','error','-i',str(B/a['relative_file']),'-af',f'silenceremove=start_periods=1:start_threshold=-45dB,atrim=duration={length},asetpts=PTS-STARTPTS,afade=t=out:st={length-.06}:d=0.06','-ar','44100','-ac','2','-c:a','pcm_s16le','-y',str(dest)])
 with wave.open(str(dest))as w:
  params=w.getparams();data=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(np.float32)
 peak=max(1,float(np.max(np.abs(data))));data=np.int16(data*(2603/peak))
 with wave.open(str(dest),'wb')as w:w.setparams(params);w.writeframes(data.tobytes())
 sounds.append(dict(tag=tag,file=dest.name,source_id=a['id']))
plan['sounds']=sounds;(P/'plano_preparado.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n');print('PREPARED',len(plan['cues']),len(sounds),flush=True)
