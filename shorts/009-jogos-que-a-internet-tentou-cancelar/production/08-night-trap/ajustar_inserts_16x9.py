"""Keep the FMV and camera UI intact in wide inserts, reusing all animation."""
from pathlib import Path
import json,subprocess,os
P=Path(__file__).resolve().parent;info=json.loads((P/'timeline.json').read_text());C=Path(info['cache']);O=P/'output';wide=O/(info['slug']+'_Cancelar_16x9.mp4');tmp=C/'wide_inserts_4x3.mp4';shots=[s for s in info['shots']if s['kind']=='game'];cmd=['ffmpeg','-v','error','-y','-filter_complex_threads','1','-threads','1','-i',str(wide)];filters=[];previous='0:v'
for i,sh in enumerate(shots,1):
 cmd+=['-threads','1','-ss',str(sh['source_start']),'-i',str(P/'assets/gameplay'/sh['source'])]
 count=sh['end']-sh['start']+1;a=(sh['start']-1)/info['fps'];b=sh['end']/info['fps']
 filters.append(f'[{i}:v]fps=30,trim=end_frame={count},setpts=PTS-STARTPTS+{a}/TB,scale=1440:1080:flags=lanczos,pad=1920:1080:240:0:color=0x1f1e27,setsar=1[insert{i}]')
 filters.append(f'[{previous}][insert{i}]overlay=0:0:eof_action=pass:repeatlast=0:enable=\'gte(t,{a})*lt(t,{b})\'[wide{i}]');previous=f'wide{i}'
cmd+=['-filter_complex',';'.join(filters),'-map',f'[{previous}]','-map','0:a:0','-frames:v',str(info['frames']),'-c:v','libx264','-threads','2','-preset','veryfast','-crf','16','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(tmp)];subprocess.run(cmd,check=True);os.replace(tmp,wide)
for t in [12.8,19.3,22]:
 frame=round(t*30)+1;subprocess.run(['ffmpeg','-v','error','-threads','1','-y','-ss',str(t),'-i',str(wide),'-frames:v','1','-threads','1','-q:v','2',str(C/f'final_16x9_{frame:04d}.jpg')],check=True)
p=O/'midias_limpas.json';report=json.loads(p.read_text());report['wide_gameplay_fit']='contain';report['wide_ui_intact']=True;p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('WIDE_FMV_AND_UI_PRESERVED',len(shots),flush=True)
