"""Export two framed formats, plus silent takes for the editable Filmora projects."""
from pathlib import Path
import subprocess,json,argparse,math,hashlib
import numpy as np
from PIL import Image,ImageOps,ImageDraw,ImageFont

P=Path(__file__).resolve().parent;C=Path('/workspace/attachments/jogos_cancelar');A=P/'assets'
info=json.loads((P/'timeline.json').read_text());edit=json.loads((P/'edicao.json').read_text())
FPS=info['fps'];W,H=768,432;OUT=P/'output';MEDIA=OUT/'Filmora/midias';MEDIA.mkdir(parents=True,exist_ok=True)
parser=argparse.ArgumentParser();parser.add_argument('--wide',action='store_true');args=parser.parse_args()
wide=args.wide;suffix='16x9'if wide else'9x16';NW,NH=(W,H)if wide else(243,432);OW,OH=(1920,1080)if wide else(1080,1920)
frames=C/'frames';missing=[f for sh in info['shots']if sh['kind']not in['game','photo']for f in range(sh['start'],sh['end']+1)if not(frames/f'frame_{f:04d}.png').exists()]
assert not missing,missing[:10]
assert (frames/'source.sha256').read_text().strip()==hashlib.sha256((OUT/'Dery_GTA_San_Andreas.blend').read_bytes()+(A/'monitor/monitor_completo.mp4').read_bytes()).hexdigest()

# Decode the already selected/normalized monitor edit once. These source frames
# also supply the two full-screen gameplay cuts, keeping the timing consistent.
decoder=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-i',str(A/'monitor/monitor_completo.mp4'),
                         '-f','rawvideo','-pix_fmt','rgb24','-threads','1','pipe:1'],stdout=subprocess.PIPE)
read_size=480*270*3
game_frames={}
for f in range(1,info['frames']+1):
    b=decoder.stdout.read(read_size)
    assert len(b)==read_size,(f,len(b))
    sh=next(sh for sh in info['shots']if sh['start']<=f<=sh['end'])
    if sh['kind']=='game':game_frames[f]=Image.frombytes('RGB',(480,270),b)
decoder.stdout.close();assert decoder.wait()==0

basefile=MEDIA/f'GTA_base_{suffix}.mp4';finalfile=OUT/f'GTA_San_Andreas_Cancelar_{suffix}.mp4'
base_cmd=['ffmpeg','-v','error','-y','-filter_threads','1','-f','rawvideo','-pix_fmt','rgb24','-s',f'{NW}x{NH}','-r',str(FPS),'-i','pipe:0',
          '-an','-vf',f'scale={OW}:{OH}:flags=neighbor,fps=30','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(basefile)]
final_cmd=['ffmpeg','-v','error','-y','-filter_threads','1','-f','rawvideo','-pix_fmt','rgb24','-s',f'{OW}x{OH}','-r',str(FPS),'-i','pipe:0',
           '-i',str(A/'audio/mix_final.wav'),'-vf','fps=30','-t',str(info['duration']),'-c:v','libx264','-threads','2','-preset','veryfast','-crf','18',
           '-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(finalfile)]
base_encoder=subprocess.Popen(base_cmd,stdin=subprocess.PIPE);final_encoder=subprocess.Popen(final_cmd,stdin=subprocess.PIPE)
bayer=(np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]],dtype=np.float32)+.5)/16-.5
noise=np.tile(bayer,((NH+3)//4,(NW+3)//4))[:NH,:NW,None]*5

def quantize(frame):
    x=np.asarray(frame,dtype=np.float32)
    return Image.fromarray(np.uint8(np.clip(np.floor((x+noise)/8+.5),0,31)*(255/31)))
def crop_portrait(frame,sh):
    if sh['kind']=='photo':
        result=Image.new('RGB',(243,432),(31,30,39))
        fit=ImageOps.contain(frame,(243,340),Image.Resampling.NEAREST)
        result.paste(fit,((243-fit.width)//2,(432-fit.height)//2));return result
    return frame.crop((263,0,506,432))
def font(size):
    f=ImageFont.truetype(str(A/'fontes/Baloo2.ttf'),size)
    try:f.set_variation_by_axes([700])
    except Exception:pass
    return f
title_cache={}
def title_image(title):
    key=title['text']
    if key in title_cache:return title_cache[key]
    max_width=OW*.88;size=round(OW*(.072 if wide else .095))
    f=font(size)
    while f.getlength(key)>max_width:
        size-=1;f=font(size)
    layer=Image.new('RGBA',(OW,OH));d=ImageDraw.Draw(layer)
    x=OW/2;y=OH*title['y']
    stroke=max(3,round(OW/240))
    d.text((x+2,y+5),key,font=f,fill=(126,69,9,255),stroke_width=stroke+2,stroke_fill=(22,18,20,255),anchor='mm')
    d.text((x,y),key,font=f,fill=(255,220,71,255),stroke_width=stroke,stroke_fill=(21,19,23,255),anchor='mm')
    title_cache[key]=layer;return layer

preview_times=[1.1,4,7.5,11.7,17.6,25.2,29.5,35.8,45.7,50.1,52.7]
preview_frames={round(t*FPS)+1 for t in preview_times}
for f in range(1,info['frames']+1):
    t=(f-1)/FPS;sh=next(sh for sh in info['shots']if sh['start']<=f<=sh['end'])
    if sh['kind']=='game':raw=game_frames[f].resize((W,H),Image.Resampling.NEAREST)
    elif sh['kind']=='photo':
        raw=Image.open(A/'imagens'/sh['source']).convert('RGB')
        raw=ImageOps.contain(raw,(W,H),Image.Resampling.NEAREST)
        canvas=Image.new('RGB',(W,H),(31,30,39));canvas.paste(raw,((W-raw.width)//2,(H-raw.height)//2));raw=canvas
    else:raw=Image.open(frames/f'frame_{f:04d}.png').convert('RGB')
    if not wide:raw=crop_portrait(raw,sh)
    raw=quantize(raw);base_encoder.stdin.write(raw.tobytes())
    ed=edit['edits'][sh['id']];u=max(0,min(1,(t-ed['start'])/max(.001,ed['end']-ed['start'])))
    z=1+(ed['zoom_end']if wide else ed['portrait_zoom_end'])-1
    z=1+(z-1)*(u*u*(3-2*u))
    cw,ch=NW/z,NH/z;cx,cy=NW/2,NH/2
    shown=raw.crop((cx-cw/2,cy-ch/2,cx+cw/2,cy+ch/2)).resize((OW,OH),Image.Resampling.NEAREST).convert('RGBA')
    for title in edit['titles']:
        if title['start']<=t<title['end']:
            layer=title_image(title).copy();fade=min(1,(t-title['start'])/.11,(title['end']-t)/.10)
            layer.putalpha(layer.getchannel('A').point(lambda a:round(a*max(0,fade))))
            shown.alpha_composite(layer,(0,round((1-min(1,(t-title['start'])/.13))*OH*.012)))
    shown=shown.convert('RGB');final_encoder.stdin.write(shown.tobytes())
    if f in preview_frames:shown.save(C/f'final_{suffix}_{f:04d}.jpg',quality=94)
    if f%150==0:print('ENCODE_PROGRESS',suffix,f,flush=True)
base_encoder.stdin.close();final_encoder.stdin.close()
assert base_encoder.wait()==0 and final_encoder.wait()==0
print('EXPORTED',suffix,str(finalfile),flush=True)
