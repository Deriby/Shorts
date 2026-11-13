"""Compose clean original media after the PSX animation, including depth-masked CRTs.

Legacy revisions reuse delivered animation; new chapters use native Blender PNGs.
Only animation is quantized/enlarged with Nearest. Media never passes that stage.
"""
from pathlib import Path
import sys,os,json,argparse,subprocess,hashlib,math,base64,zlib
sys.path.insert(0,'/workspace/tools/shorts_asr')
import numpy as np,cv2
from PIL import Image,ImageOps,ImageDraw,ImageFont
cv2.setNumThreads(1)
parser=argparse.ArgumentParser();parser.add_argument('project');parser.add_argument('--legacy',action='store_true');parser.add_argument('--limit',type=int,default=0);args=parser.parse_args()
P=Path(args.project).resolve();info=json.loads((P/'timeline.json').read_text());ed=json.loads((P/'edicao.json').read_text());N=info['frames'];FPS=info['fps'];A=P/'assets'
legacy={
 '01-gta-san-andreas':('GTA_San_Andreas','Dery_GTA_San_Andreas.blend','Filmora_R2','GTA_base_R2_9x16.mp4','GTA_San_Andreas_Cancelar_R2_16x9.mp4','GTA_San_Andreas_R2_9x16.wfp'),
 '02-bmx-xxx':('BMX_XXX','Dery_BMX_XXX.blend','Filmora','BMX_base_9x16.mp4','BMX_XXX_Cancelar_16x9.mp4','BMX_XXX_9x16.wfp'),
 '03-bully':('Bully','Dery_Bully.blend','Filmora','Bully_base_9x16.mp4','Bully_Cancelar_16x9.mp4','Bully_9x16.wfp')}
if args.legacy:
 slug,model,old_folder,base_name,wide_name,wfp_name=legacy[P.name];OUT=P/'output/R3_Midias_Limpas';C=Path('/workspace/attachments/clean_media')/P.name
 base_source=P/'output'/old_folder/'midias'/base_name;wide_source=P/'output'/wide_name
else:
 slug=info.get('slug','Saints_Row_IV');model=info.get('model','Dery_Saints_Row_IV.blend');OUT=P/'output';C=Path(info['cache']);base_name=slug+'_base_9x16.mp4'
OUT.mkdir(parents=True,exist_ok=True);MEDIA=OUT/'Filmora/midias';MEDIA.mkdir(parents=True,exist_ok=True)
projection=json.loads((C/'screen_projection.json').read_text());assert projection['model_sha256']==hashlib.sha256((P/'output'/model).read_bytes()).hexdigest()
class Reader:
 def __init__(self,path,start=0,count=None,output_fps=30):
  data=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_streams','-of','json',str(path)]))['streams'][0];self.size=(data['width'],data['height'])
  cmd=['ffmpeg','-v','error','-threads','1','-ss',str(start),'-i',str(path),'-an','-vf',f'fps={output_fps}']
  if count:cmd+=['-frames:v',str(count)]
  cmd+=['-f','rawvideo','-pix_fmt','rgb24','-threads','1','pipe:1'];self.p=subprocess.Popen(cmd,stdout=subprocess.PIPE);self.bytes=self.size[0]*self.size[1]*3
 def read(self):
  b=self.p.stdout.read(self.bytes);assert len(b)==self.bytes,('short source',len(b),self.bytes);return Image.frombytes('RGB',self.size,b)
 def close(self):
  self.p.stdout.close();code=self.p.wait();assert code==0,code
class Writer:
 def __init__(self,path,size,audio=None):
  cmd=['ffmpeg','-v','error','-y','-filter_threads','1','-f','rawvideo','-pix_fmt','rgb24','-s',f'{size[0]}x{size[1]}','-r',str(FPS),'-i','pipe:0']
  if audio:cmd+=['-i',str(audio),'-c:a','aac','-b:a','192k']
  else:cmd+=['-an']
  cmd+=['-t',str(info['duration']),'-c:v','libx264','-threads','1','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(path)]
  self.p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 def write(self,im):self.p.stdin.write(im.convert('RGB').tobytes())
 def close(self):self.p.stdin.close();assert self.p.wait()==0

def cropbox(w,h,zoom):return tuple(round(v)for v in((w-w/zoom)/2,(h-h/zoom)/2,(w+w/zoom)/2,(h+h/zoom)/2))
def screen_quad(frame,wide=False,zoom=1):
 p=projection['frames'].get(str(frame))
 if not p:return None
 q=np.array(p['quad'],np.float32)
 w,h=(768,432)if wide else(243,432)
 if not wide:q[:,0]-=263
 l,t,r,b=cropbox(w,h,zoom);ow,oh=(1920,1080)if wide else(1080,1920)
 q[:,0]=(q[:,0]-l)*ow/(r-l);q[:,1]=(q[:,1]-t)*oh/(b-t)
 return q

def overlay(canvas,source,frame,wide=False,zoom=1):
 q=screen_quad(frame,wide,zoom)
 if q is None:return canvas
 w,h=canvas.size;x0=max(0,int(np.floor(q[:,0].min()))-1);x1=min(w,int(np.ceil(q[:,0].max()))+2);y0=max(0,int(np.floor(q[:,1].min()))-1);y1=min(h,int(np.ceil(q[:,1].max()))+2)
 if x1<=x0 or y1<=y0:return canvas
 # Preserve image proportions in a 4:3 CRT; letters are never stretched.
 src=Image.new('RGB',(1280,960),(16,16,19));fit=ImageOps.contain(source,(1280,960),Image.Resampling.LANCZOS);src.paste(fit,((1280-fit.width)//2,(960-fit.height)//2))
 dst=q-np.array([x0,y0],np.float32);corners=np.array([[0,0],[1279,0],[1279,959],[0,959]],np.float32);H=cv2.getPerspectiveTransform(corners,dst)
 warped=cv2.warpPerspective(np.asarray(src),H,(x1-x0,y1-y0),flags=cv2.INTER_LANCZOS4,borderMode=cv2.BORDER_CONSTANT)
 mask=projection['frames'][str(frame)]['mask']
 if mask is None:mask=np.full((48,64),255,np.uint8)
 elif isinstance(mask,str):mask=np.frombuffer(zlib.decompress(base64.b64decode(mask)),np.uint8).reshape(48,64)
 else:mask=np.asarray(mask,np.uint8).reshape(48,64)
 HM=cv2.getPerspectiveTransform(np.array([[0,0],[63,0],[63,47],[0,47]],np.float32),dst)
 alpha=cv2.warpPerspective(mask,HM,(x1-x0,y1-y0),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
 alpha=cv2.erode(alpha,np.ones((3,3),np.uint8),iterations=1).astype(np.float32)[:,:,None]/255
 arr=np.array(canvas);old=arr[y0:y1,x0:x1].astype(np.float32);arr[y0:y1,x0:x1]=np.uint8(np.clip(old*(1-alpha)+warped.astype(np.float32)*alpha,0,255));return Image.fromarray(arr)

def media_canvas(source,kind,wide,zoom=1,portrait_fit='crop'):
 size=(1920,1080)if wide else(1080,1920)
 if kind=='game'and(wide or portrait_fit!='contain'):im=ImageOps.fit(source,size,Image.Resampling.LANCZOS,centering=(.5,.5))
 else:
  im=Image.new('RGB',size,(31,30,39));bounds=size if wide else(1080,round(340/432*1920));fit=ImageOps.contain(source,bounds,Image.Resampling.LANCZOS);im.paste(fit,((size[0]-fit.width)//2,(size[1]-fit.height)//2))
 if zoom!=1:im=im.crop(cropbox(*size,zoom)).resize(size,Image.Resampling.LANCZOS)
 return im

def animation_canvas(raw,wide,zoom=1):
 if not wide:raw=raw.crop((263,0,506,432))
 w,h=raw.size;raw=raw.crop(cropbox(w,h,zoom))
 return raw.resize((1920,1080)if wide else(1080,1920),Image.Resampling.NEAREST)

def quantize(raw):
 x=np.asarray(raw,dtype=np.float32);h,w=x.shape[:2];bayer=(np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]],np.float32)+.5)/16-.5
 noise=np.tile(bayer,((h+3)//4,(w+3)//4))[:h,:w,None]*5
 return Image.fromarray(np.uint8(np.clip(np.floor((x+noise)/8+.5),0,31)*(255/31)))

def legacy_titles(im,t,wide):
 # Earlier edits keep their existing editable callouts; the new chapter has none.
 titles=[v for v in ed['titles']if v['start']<=t<v['end']]
 if not titles:return im
 ow,oh=im.size;result=im.convert('RGBA')
 for title in titles:
  size=round(ow*(.072 if wide else.095));font_path=A/'fontes/Baloo2.ttf';font=ImageFont.truetype(str(font_path),size)
  try:font.set_variation_by_axes([700])
  except Exception:pass
  while font.getlength(title['text'])>ow*.88:
   size-=1;font=ImageFont.truetype(str(font_path),size)
   try:font.set_variation_by_axes([700])
   except Exception:pass
  layer=Image.new('RGBA',im.size);draw=ImageDraw.Draw(layer);x=ow/2;y=oh*title['y'];stroke=max(3,round(ow/240))
  draw.text((x+2,y+5),title['text'],font=font,fill=(126,69,9,255),stroke_width=stroke+2,stroke_fill=(22,18,20,255),anchor='mm');draw.text((x,y),title['text'],font=font,fill=(255,220,71,255),stroke_width=stroke,stroke_fill=(21,19,23,255),anchor='mm')
  fade=max(0,min(1,(t-title['start'])/.11,(title['end']-t)/.10));layer.putalpha(layer.getchannel('A').point(lambda a:round(a*fade)));result.alpha_composite(layer,(0,round((1-min(1,(t-title['start'])/.13))*oh*.012)))
 return result.convert('RGB')

base_writer=Writer(MEDIA/base_name,(1080,1920));tag='_R3_Midias_Limpas'if args.legacy else'_Cancelar'
portrait_file=OUT/f'{slug}{tag}_9x16.mp4';wide_file=OUT/f'{slug}{tag}_16x9.mp4'
wp=Writer(portrait_file,(1080,1920),A/'audio/mix_final.wav');ww=Writer(wide_file,(1920,1080),A/'audio/mix_final.wav')
oldp=Reader(base_source)if args.legacy else None;oldw=Reader(wide_source)if args.legacy else None
previews=set(round(t*FPS)+1 for t in([1.1,4,9,13.3,16,21.5,25,28,33.5,38,40.5,46]if args.legacy else[1.1,4.4,8,12.8,16.8,19.3,22,25,28,33,36.5,39.7])if t<info['duration'])
images={};processed=0;movie_source_sizes={}
for sh in info['shots']:
 count=sh['end']-sh['start']+1;needs_media=sh['kind']in['game','photo']or any(str(f)in projection['frames']for f in range(sh['start'],sh['end']+1))
 source_path=A/('gameplay'if sh['source'].lower().endswith('.mp4')else'imagens')/sh['source'];reader=None;photo=None
 if needs_media:
  if source_path.suffix.lower()=='.mp4':reader=Reader(source_path,sh['source_start'],count);movie_source_sizes[source_path.name]=reader.size
  else:photo=Image.open(source_path).convert('RGB')
 for f in range(sh['start'],sh['end']+1):
  t=(f-1)/FPS;u=(f-sh['start'])/max(1,sh['end']-sh['start']);ease=u*u*(3-2*u);edit=ed['edits'][sh['id']];zp=1+(edit['portrait_zoom_end']-1)*ease;zw=1+(edit['zoom_end']-1)*ease
  source=reader.read()if reader else photo
  if oldp:bp=oldp.read();wide_background=oldw.read()
  if sh['kind']in['game','photo']:
   framing=sh.get('portrait_fit','crop');bp=media_canvas(source,sh['kind'],False,portrait_fit=framing);fp=media_canvas(source,sh['kind'],False,zp,framing);fw=media_canvas(source,sh['kind'],True,zw)
   if args.legacy:fp=legacy_titles(fp,t,False);fw=legacy_titles(fw,t,True)
  else:
   if args.legacy:
    fp=bp.crop(cropbox(1080,1920,zp)).resize((1080,1920),Image.Resampling.NEAREST);fw=wide_background
   else:
    raw=quantize(Image.open(C/'frames'/f'frame_{f:04d}.png').convert('RGB'));bp=animation_canvas(raw,False);fp=animation_canvas(raw,False,zp);fw=animation_canvas(raw,True,zw)
   if source is not None:
    bp=overlay(bp,source,f,False,1);fp=bp if abs(zp-1)<1e-9 else overlay(fp,source,f,False,zp);fw=overlay(fw,source,f,True,zw)
   if args.legacy:fp=legacy_titles(fp,t,False)
  base_writer.write(bp);wp.write(fp);ww.write(fw);processed+=1
  if f in previews:
   fp.save(C/f'final_9x16_{f:04d}.jpg',quality=95);fw.save(C/f'final_16x9_{f:04d}.jpg',quality=95)
  if processed%150==0:print('CLEAN_COMPOSE',P.name,processed,flush=True)
  if args.limit and processed>=args.limit:break
 if reader:reader.close()
 if args.limit and processed>=args.limit:break
for obj in[base_writer,wp,ww]:obj.close()
if oldp:oldp.close();oldw.close()
assert processed==N or args.limit
report=dict(chapter=info['chapter'],frames=processed,media_original_resolution=True,media_rgb555=False,media_dither=False,media_nearest=False,media_affine_warp=False,crt_perspective=True,crt_occlusion_mask=True,crt_aspect_preserved=True,psx_animation_preserved=True,legacy_animation_reused=args.legacy,source_sizes=movie_source_sizes,outputs=[str(p.relative_to(P))for p in[portrait_file,wide_file,MEDIA/base_name]],projection_sha256=hashlib.sha256((C/'screen_projection.json').read_bytes()).hexdigest())
(OUT/'midias_limpas.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('CLEAN_COMPOSITION_READY',P.name,processed,flush=True)
