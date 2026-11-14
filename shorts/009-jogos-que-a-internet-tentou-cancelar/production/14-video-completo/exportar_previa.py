"""Mux approved video streams with the complete native audio reconstruction."""
from pathlib import Path
import json,subprocess
P=Path(__file__).resolve().parent;O=P/'output';M=O/'Filmora/midias';C=Path('/workspace/attachments/longo009');plan=json.loads((P/'montagem.json').read_text())
files=[]
for rec in plan['records']:
 path=M/rec['media']if rec['type']=='body'else C/'vinhetas'/rec['preview'];assert path.exists();files.append((path,rec['frames']/30))
listing=C/'completo.ffconcat';listing.write_text('ffconcat version 1.0\n'+''.join(f"file '{path}'\nduration {duration:.12f}\n"for path,duration in files))
video=O/'Jogos_Que_A_Internet_Tentou_Cancelar_COMPLETO_16x9.mp4';subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(listing),'-i',str(Path('/workspace/attachments/longo009/mixagem_completa.wav')),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-t',str(plan['duration']),'-movflags','+faststart',str(video)],check=True)
# A compact chapter-card sample for review, with the same separate sting.
cards=[r for r in plan['records']if r['type']=='card'];listing=C/'vinhetas.ffconcat';listing.write_text('ffconcat version 1.0\n'+''.join(f"file '{C/'vinhetas'/r['preview']}'\nduration 2.0\n"for r in cards));subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(listing),'-stream_loop','-1','-i',str(M/'vinheta_2s.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-t',str(len(cards)*2),'-movflags','+faststart',str(O/'Previa_Vinhetas_16x9.mp4')],check=True)
print('FULL_PREVIEW_READY',video,flush=True)
