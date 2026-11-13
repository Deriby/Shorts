from pathlib import Path
import json,hashlib,subprocess,wave
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;C=Path('/workspace/attachments/atuacao_sentada_v3/frames');OUT=P/'output';model=OUT/'Dery_Atuacao_Apoio_Real.blend'
assert(C/'source.sha256').read_text().strip()==hashlib.sha256(model.read_bytes()).hexdigest();assert all((C/f'frame_{f:04d}.png').is_file()for f in range(1,241))
dest=OUT/'Teste_Apoio_Real_8s_9x16.mp4';cmd=['ffmpeg','-v','error','-y','-filter_threads','1','-f','rawvideo','-pix_fmt','rgb24','-s','243x432','-r','30','-i','pipe:0','-i',str(P/'assets/voz_teste.wav'),'-vf','scale=1080:1920:flags=neighbor','-t','8','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(dest)]
encoder=subprocess.Popen(cmd,stdin=subprocess.PIPE);bayer=(np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]],np.float32)+.5)/16-.5;noise=np.tile(bayer,(108,61))[:432,:243,None]*5;sheet=Image.new('RGB',(729,912),(25,26,31));draw=ImageDraw.Draw(sheet);samples=[1,31,70,91,145,222]
for f in range(1,241):
 im=Image.open(C/f'frame_{f:04d}.png').convert('RGB').crop((263,0,506,432));x=np.asarray(im,np.float32);im=Image.fromarray(np.uint8(np.clip(np.floor((x+noise)/8+.5),0,31)*(255/31)));encoder.stdin.write(im.tobytes())
 if f in samples:
  i=samples.index(f);px=i%3*243;py=i//3*456;sheet.paste(im,(px,py));draw.text((px+7,py+436),f'{(f-1)/30:.2f}s',fill='white')
encoder.stdin.close();assert encoder.wait()==0;sheet.save(OUT/'Quadros_Apoio_Real.jpg',quality=95)
d=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(dest)]));v=next(x for x in d['streams']if x['codec_type']=='video');assert[v['width'],v['height']]==[1080,1920];assert v['r_frame_rate']=='30/1'and int(v['nb_frames'])==240;assert abs(float(d['format']['duration'])-8)<.035
subprocess.run(['ffmpeg','-v','error','-i',str(dest),'-map','0:v:0','-map','0:a:0','-f','null','-'],check=True)
source=Path('/workspace/Shorts/shorts/009-jogos-que-a-internet-tentou-cancelar/production/04-saints-row-iv/assets/voz/voz_completa.wav')
with wave.open(str(source))as w:sr=w.getframerate();prefix=w.readframes(round(6.4*sr))
with wave.open(str(P/'assets/voz_teste.wav'))as w:audio=w.readframes(w.getnframes());assert len(audio)==8*sr*2;assert audio[:len(prefix)]==prefix;assert set(audio[len(prefix):])<={0}
report=dict(file=dest.name,duration=8,fps=30,frames=240,resolution=[1080,1920],full_decode=True,audio_excerpt_seconds=[0,6.4],reaction_pause_seconds=1.6,original_excerpt_pcm_preserved=True,new_voice=False,subtitles=False,music=False,psx_animation=True,source_shorts_changed=False,sha256=hashlib.sha256(dest.read_bytes()).hexdigest())
(P/'validacao_export_apoio_real.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('ACTING_TEST_EXPORTED',json.dumps(report),flush=True)
