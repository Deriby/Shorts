"""Encode the real six-second Blender test with crisp RGB555 portrait frames."""
from pathlib import Path
import subprocess,json,hashlib
import numpy as np
from PIL import Image

P=Path(__file__).resolve().parent;WORK=Path('/workspace/attachments/quarto_gamer_cena/frames')
frames=sorted(WORK.glob('frame_*.png'));assert len(frames)==96,len(frames)
bayer=np.asarray([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]],float)/16-.5
def process(frame):
    im=Image.open(frame).convert('RGB');a=np.asarray(im,dtype=float)/255
    d=np.tile(bayer,(int(np.ceil(a.shape[0]/4)),int(np.ceil(a.shape[1]/4))))[:a.shape[0],:a.shape[1]]
    result=np.uint8(np.round(np.clip(np.floor(a*31+.5+d[...,None]*.65),0,31)/31*255))
    return Image.fromarray(result)
video=P/'Previa_Dery_Quarto_6s_9x16.mp4'
cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','270x480','-r','16','-i','pipe:0','-i',str(P/'media/Voz_Driver_Trecho.wav'),'-vf','scale=1080:1920:flags=neighbor,fps=24','-c:v','libx264','-preset','veryfast','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-t','6','-movflags','+faststart','-threads','3',str(video)]
encoder=subprocess.Popen(cmd,stdin=subprocess.PIPE)
for f in frames:encoder.stdin.write(process(f).tobytes())
encoder.stdin.close();assert encoder.wait()==0
process(WORK/'frame_0032.png').resize((1080,1920),Image.Resampling.NEAREST).save(P/'Previa_Dery_No_Quarto.png')
info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
v=next(x for x in info['streams']if x['codec_type']=='video');a=next(x for x in info['streams']if x['codec_type']=='audio')
assert [v['width'],v['height']]==[1080,1920]and v['r_frame_rate']=='24/1'and int(v['nb_frames'])==144
assert abs(float(info['format']['duration'])-6)<.05
framehashes=[hashlib.sha256(Image.open(WORK/f'frame_{i:04d}.png').tobytes()).hexdigest()for i in [2,6,12,18]]
assert len(set(framehashes))>=3,'Monitor/camera intro should visibly change'
record={'video':video.name,'duration_seconds':float(info['format']['duration']),'width':1080,'height':1920,'delivery_fps':24,'source_animation_fps':16,'rendered_blender_frames':len(frames),'output_frames':int(v['nb_frames']),'audio_codec':a['codec_name'],'intro_frame_hashes':framehashes,'distinct_intro_frames':len(set(framehashes)),'new_tts_generated':False,'subtitles':False,'artificial_full_frame_shake':False}
(P/'exportacao.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print('EXPORTED',record,flush=True)
