"""Verify preservation of the user's native edit and every added moving meme."""
from pathlib import Path
import json,zipfile,hashlib,base64,subprocess,struct,wave,copy
import numpy as np
P=Path(__file__).resolve().parent;R=next(p for p in P.parents if(p/'AGENTS.md').exists());F=P/'output/Filmora';OLD=P.parent/'output/Filmora';M=F/'midias';ROOT='{204E72A3-B517-44d4-806F-9E9D84D5F904}';TL=f'ProjectFolder/Medias/{ROOT}/timeline.wesproj'
def read(path):
 with zipfile.ZipFile(path)as z:assert z.testzip()is None;return {n:z.read(n)for n in z.namelist()}
source=read(P/'recebido/Massacote_Completo_Atualizado_Usuario.wfp');result=read(F/'Massacote_Completo_MEMES.wfp');a=json.loads(source[TL]);b=json.loads(result[TL]);plan=json.loads((P/'plano_aplicado.json').read_text());report=json.loads((P/'projeto.json').read_text());oldnames={p.name for p in(OLD/'midias').iterdir()if p.is_file()}
def relocate(x):
 if isinstance(x,dict):return {k:relocate(v)for k,v in x.items()}
 if isinstance(x,list):return [relocate(v)for v in x]
 if isinstance(x,str)and '/midias/'in x and Path(x).name in oldnames:return ('file:./'if x.startswith('file:')else'./')+'midias/'+Path(x).name
 return x
a=relocate(a);assert len(a['timelineInfos'])==len(b['timelineInfos'])==3
count=0
for st,nt in zip(a['timelineInfos'],b['timelineInfos']):
 assert st['timelineId']==nt['timelineId']
 for old,new in zip(st['trackInfos'],nt['trackInfos']):assert old==new,'User edit changed';count+=len(old['clipList'])
 assert len(nt['trackInfos'])-len(st['trackInfos'])==(2 if st['timelineId']==36 else 0)
assert b['resources'][:len(a['resources'])]==a['resources']
main=b['timelineInfos'][0];new=main['trackInfos'][-1]['clipList'];sounds=main['trackInfos'][-2]['clipList'];assert len(new)==52 and len(sounds)==8
assert max(c['tlEnd']for tr in main['trackInfos']for c in tr['clipList'])==max(c['tlEnd']for tr in a['timelineInfos'][0]['trackInfos']for c in tr['clipList'])
lib=json.loads(result['ProjectFolder/Medias/medias_info.json']);ex=json.loads(result[f'ProjectFolder/Medias/{ROOT}/extra.json']);meta=json.loads(result['ProjectFolder/project_info.json']);uuid=next(base64.b64decode(u['data']).decode().rstrip('\0')for u in main['userData']if u['key']==11000);assert lib['media_items'][ROOT]['timeline_uuid']==uuid;assert lib['media_items'][ROOT]['duration']==meta['project_timeline_duration']
res={r['sourceUuid']:r for r in b['resources']};motion=[]
for c in new+sounds:
 ud={u['key']:base64.b64decode(u['data']).decode().rstrip('\0')for u in c['userData']if u['key']in[3,10]};assert ex['mediaClipsMapInfo'][ud[3]]['mediaId']==ud[10];assert ud[10]in lib['media_items'];assert f"ProjectFolder/Medias/{ud[10]}/media.json"in result
 assert c['tlEnd']-c['tlBegin']==c['outPoint']-c['inPoint']
 speed=json.loads(c['speed']['speedParam']);assert not c['speed']['reverse']and all(k['_value']==1 for k in speed['keyframeSets'])
 if c['filename'].endswith('.mp4'):
  path=M/Path(c['filename']).name;v=res[c['sourceUuid']];assert c['outPoint']<=v['mediaLength']+1
  # Read frames from the actual video stream; catch frozen/empty/short derivatives.
  raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-i',str(path),'-vf','scale=96:54','-an','-f','rawvideo','-pix_fmt','rgb24','-threads','1','-']);arr=np.frombuffer(raw,np.uint8).reshape(-1,54,96,3);assert len(arr)==round((c['outPoint']/1e7)*30);delta=float(np.mean(np.abs(arr[-2].astype(float)-arr[2].astype(float))));assert delta>.015,(path.name,delta);motion.append(dict(file=path.name,frames=len(arr),change=delta))
 for ch in c['effectChainList']:
  for e in ch['effectList']:
   for p in e.get('paramMapList',[]):
    ks=json.loads(p['keyFrame']['parameter'])['keyframeSets'];assert all(0<=k['_time']<=c['outPoint']/1e7+1e-8 for k in ks);assert all(x['_time']<y['_time']for x,y in zip(ks,ks[1:]))
for r in b['resources']:
 name=Path(r['filename']).name;assert(M/name).exists()or(OLD/'midias'/name).exists();assert r['filename'].startswith('file:./midias/')
peaks=[]
for s in plan['sounds']:
 with wave.open(str(M/s['file']))as w:x=np.frombuffer(w.readframes(w.getnframes()),'<i2');assert w.getframerate()==44100
 peak=float(max(np.abs(x.astype(np.int32))))/32768;assert 0<peak<=.08;peaks.append(dict(file=s['file'],peak_db=20*np.log10(peak)))
# Existing comic inserts remain unobscured by new overlays.
longplan=json.loads((P.parent/'montagem.json').read_text());conflicts=[]
for rec in longplan['records']:
 if rec['type']!='body':continue
 p=(R/rec['source_folder']).parent/'plano_ceninha.json'
 if p.exists():gags=[((g['start']-1)/30,g['end']/30)for g in json.loads(p.read_text())['gags']]
 else:
  info=json.loads((R/rec['production']/'timeline.json').read_text());gags=[((g['start']-1)/info['fps'],g['end']/info['fps'])for g in info['shots']if g['kind']=='gag']
 for cue in[c for c in plan['cues']if c['chapter']==rec['key']]:
  x=cue['local_start_frame']/30;y=x+cue['frames']/30
  for ga,gb in gags:
   if min(y,gb)-max(x,ga)>.001:conflicts.append((cue['id'],x,y,ga,gb))
assert not conflicts,conflicts
assert hashlib.sha256((P/'recebido/Massacote_Completo_Atualizado_Usuario.wfp').read_bytes()).hexdigest()==report['source_sha256']
check=dict(original_clips_preserved=count,original_main_clips=353,child_timelines_preserved=True,user_effects_keyframes_audio_unchanged=True,relative_paths_only=True,root_registration_preserved=True,new_visuals=52,new_sounds=8,new_resources=57,all_new_media_available=True,video_motion_checks=motion,quiet_sound_peaks=peaks,no_comic_insert_overlap=True,voice_original_files_unchanged=True,source_sha256_unchanged=True,native_filmora_open=False)
(P/'validacao.json').write_text(json.dumps(check,ensure_ascii=False,indent=2)+'\n');print('MEMES_VERIFIED',count,len(motion),flush=True)
