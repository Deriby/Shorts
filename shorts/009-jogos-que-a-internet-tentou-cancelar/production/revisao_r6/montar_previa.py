"""A short watchable reel of the 17 delivered scenes; no new 3D rendering."""
from pathlib import Path
import json,subprocess,hashlib
P=Path(__file__).resolve().parent;R=next(p for p in P.parents if(p/'AGENTS.md').exists());C=Path('/workspace/attachments/revisao_r6/previa_cenas');C.mkdir(parents=True,exist_ok=True);plans=json.loads((P/'plano.json').read_text());names=['GTA San Andreas','BMX XXX','Bully','Left 4 Dead 2','Saints Row IV','GTA V','Pokémon Sword and Shield','Night Trap'];font=R/plans[0]['output']/'Filmora/fontes/Baloo2.ttf';output=P/'Previa_17_Ceninhas_9x16.mp4';cmd=['ffmpeg','-v','error','-y','-filter_complex_threads','1'];filters=[];labels=[];cursor=0;timeline=[];source_hashes={}
for i,(plan,title)in enumerate(zip(plans,names)):
 source=R/plan['output']/(plan['slug']+'_R6_9x16.mp4');cmd+=['-threads','1','-i',str(source)];source_hashes[str(source.relative_to(R))]=hashlib.sha256(source.read_bytes()).hexdigest();titlefile=C/f'title_{i}.txt';titlefile.write_text(title);countfile=C/f'count_{i}.txt';countfile.write_text(f'{len(plan["gags"])} ceninhas')
 filters.append(f"color=c=0x19181f:s=1080x1920:r=30:d=0.5,drawtext=fontfile='{font}':textfile='{titlefile}':fontsize=64:fontcolor=0xffd54b:x=(w-tw)/2:y=(h-th)/2-55,drawtext=fontfile='{font}':textfile='{countfile}':fontsize=42:fontcolor=white:x=(w-tw)/2:y=(h-th)/2+65,setsar=1[card{i}]")
 filters.append(f'anullsrc=r=44100:cl=stereo,atrim=end_sample=22050,asetpts=PTS-STARTPTS[ca{i}]');labels.extend([f'[card{i}]',f'[ca{i}]']);cursor+=15
 n=len(plan['gags']);filters.append(f'[{i}:v]split={n}'+''.join(f'[sv{i}_{j}]'for j in range(n)));filters.append(f'[{i}:a]asplit={n}'+''.join(f'[sa{i}_{j}]'for j in range(n)))
 for j,g in enumerate(plan['gags']):
  a=(g['start']-1)/30;b=g['end']/30;duration=g['count']/30
  filters.append(f'[sv{i}_{j}]trim=start_frame={g["start"]-1}:end_frame={g["end"]},setpts=PTS-STARTPTS,setsar=1[v{i}_{j}]')
  filters.append(f'[sa{i}_{j}]atrim=start={a}:end={b},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.008,afade=t=out:st={duration-.008}:d=0.008[a{i}_{j}]');labels.extend([f'[v{i}_{j}]',f'[a{i}_{j}]']);timeline.append(dict(game=title,scene=g['id'],action=g['action'],preview_start=cursor/30,preview_end=(cursor+g['count'])/30,source_start=a,source_end=b));cursor+=g['count']
filters.append(''.join(labels)+f'concat=n={len(labels)//2}:v=1:a=1[outv][outa]');graph=C/'montagem.ffgraph';graph.write_text(';\n'.join(filters));cmd+=['-filter_complex_script',str(graph),'-map','[outv]','-map','[outa]','-frames:v',str(cursor),'-r','30','-fps_mode','cfr','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(output)]
subprocess.run(cmd,check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(output)]));v=next(s for s in probe['streams']if s['codec_type']=='video');assert int(v['nb_frames'])==cursor and(v['width'],v['height'])==(1080,1920)and v['r_frame_rate']=='30/1';assert any(s['codec_type']=='audio'for s in probe['streams']);assert abs(float(probe['format']['duration'])-cursor/30)<.04
subprocess.run(['ffmpeg','-v','error','-threads','1','-i',str(output),'-f','null','-'],check=True)
record=dict(duration=cursor/30,frames=cursor,fps=30,scenes=len(timeline),titles_only_in_preview=True,original_deliveries_unchanged=True,new_3d_render=False,source_sha256=source_hashes,scenes_timeline=timeline,preview_sha256=hashlib.sha256(output.read_bytes()).hexdigest())
(P/'previa_ceninhas.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print('PREVIEW_READY',cursor/30,len(timeline),output.stat().st_size,flush=True)
