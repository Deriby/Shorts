from pathlib import Path
import json,zipfile,copy,hashlib,subprocess,base64,statistics
import numpy as np
P=Path(__file__).resolve().parent;R=next(p for p in P.parents if(p/'AGENTS.md').exists());V3=P.parent/'revisao_memes_v3';ROOT='{204E72A3-B517-44d4-806F-9E9D84D5F904}';TL=f'ProjectFolder/Medias/{ROOT}/timeline.wesproj';F=P/'output/Filmora';M=F/'midias'
def load(p):
 with zipfile.ZipFile(p)as z:assert z.testzip()is None;return {n:z.read(n)for n in z.namelist()}
old=load(V3/'output/Filmora/Massacote_Completo_MEMES.wfp');new=load(F/'Massacote_Completo_MEMES_TEMPO.wfp') if(F/'Massacote_Completo_MEMES_TEMPO.wfp').exists()else load(F/'Massacote_MEMES_Tempo_Corrigido.wfp')
a=json.loads(old[TL]);b=json.loads(new[TL]);plan=json.loads((P/'plano_corrigido.json').read_text());revision=json.loads((P/'revisao.json').read_text());bank={x['tag']:x for x in json.loads((R/'assets/biblioteca_memes/catalogo.json').read_text())['items']}
assert len(a['timelineInfos'])==len(b['timelineInfos'])==3
for i,(x,y)in enumerate(zip(a['timelineInfos'],b['timelineInfos'])):
 if i:assert x==y
 else:
  assert x['trackInfos'][:-2]==y['trackInfos'][:-2]
  xx={k:v for k,v in x.items()if k!='trackInfos'};yy={k:v for k,v in y.items()if k!='trackInfos'};assert xx==yy
main=b['timelineInfos'][0];oldclips={c['thisUId']:c for c in a['timelineInfos'][0]['trackInfos'][-1]['clipList']};clips={c['thisUId']:c for c in main['trackInfos'][-1]['clipList']};assert set(oldclips)==set(clips)and len(clips)==52
newresources={r['sourceUuid']:r for r in b['resources']};oldresources={r['sourceUuid']:r for r in a['resources']};assert set(newresources)==set(oldresources)
lib=json.loads(new['ProjectFolder/Medias/medias_info.json']);extra=json.loads(new[f'ProjectFolder/Medias/{ROOT}/extra.json']);assert extra==json.loads(old[f'ProjectFolder/Medias/{ROOT}/extra.json'])
video_checks=[];images=[];video_durations=[]
for cue in plan['cues']:
 c=clips[cue['native_clip_id']];oc=oldclips[c['thisUId']];duration=c['outPoint']/1e7;assert c['tlEnd']-c['tlBegin']==c['outPoint']-c['inPoint'];assert duration>oc['outPoint']/1e7
 assert c['speed']['offset']==0 and not c['speed']['reverse'];assert all(k['_value']==1 for k in json.loads(c['speed']['speedParam'])['keyframeSets'])
 for key in set(oc)-{'tlBegin','tlEnd','outPoint','filename','speed','effectChainList'}:assert c[key]==oc[key],key
 for och,nch in zip(oc['effectChainList'],c['effectChainList']):
  for of,nf in zip(och['effectList'],nch['effectList']):
   assert {k:v for k,v in of.items()if k!='paramMapList'}=={k:v for k,v in nf.items()if k!='paramMapList'}
   for op,np_ in zip(of['paramMapList'],nf['paramMapList']):
    ok=json.loads(op['keyFrame']['parameter'])['keyframeSets'];nk=json.loads(np_['keyFrame']['parameter'])['keyframeSets'];assert len(ok)==len(nk)
    assert all(x['_value']==y['_value']and x['Interpolation']==y['Interpolation']for x,y in zip(ok,nk))
    assert all(x==y for x,y in zip(ok,nk)if x['_time']<=.25)
    for x,y in zip(ok,nk):
     assert 0<=y['_time']<=duration+1e-8
     if x['_time']>=oc['outPoint']/1e7-.15-1e-7:assert abs((duration-y['_time'])-(oc['outPoint']/1e7-x['_time']))<1e-7
    assert all(x['_time']<y['_time']for x,y in zip(nk,nk[1:]))
 ud={u['key']:base64.b64decode(u['data']).decode().rstrip('\0')for u in c['userData']if u['key']in[3,10]};assert extra['mediaClipsMapInfo'][ud[3]]['mediaId']==ud[10];assert ud[10]in lib['media_items']
 if cue['asset_tag'].startswith('V'):
  video_durations.append(duration);asset=bank[cue['asset_tag']];assert cue['source_start']+cue['frames']/30<=asset['duration']+.00001
  path=M/cue['prepared_file'];probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(path)]));v=probe['streams'][0];assert int(v['nb_frames'])==cue['frames'];assert newresources[c['sourceUuid']]['mediaLength']==c['outPoint']
  frames=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-i',str(path),'-vf','scale=96:54','-an','-f','rawvideo','-pix_fmt','rgb24','-threads','1','-']);arr=np.frombuffer(frames,np.uint8).reshape(-1,54,96,3);change=float(np.mean(abs(arr[-2].astype(float)-arr[2].astype(float))));assert change>.015
  cache=json.loads(new[f'ProjectFolder/Medias/{ud[10]}/media.json']);assert cache['file_name']=='./midias/'+path.name;assert cache['sourceInfo']['vidStreamInfos'][0]['totalFrames']==cue['frames'];assert lib['media_items'][ud[10]]['src_md5']==hashlib.md5(path.read_bytes()).hexdigest()
  video_checks.append(dict(cue=cue['id'],duration=duration,source_start=cue['source_start'],frames=cue['frames'],frame_change=change,complete_short_source=duration<2.1))
 else:
  assert duration>=1.6;images.append(duration);assert newresources[c['sourceUuid']]==oldresources[c['sourceUuid']]
# No overlapping memes or chapters, and preserve the 3D comic reveals.
seq=sorted(clips.values(),key=lambda c:c['tlBegin']);assert all(x['tlEnd']<=y['tlBegin']for x,y in zip(seq,seq[1:]))
long=json.loads((P.parent/'montagem.json').read_text());gags={}
for rec in long['records']:
 if rec['type']!='body':continue
 q=(R/rec['source_folder']).parent/'plano_ceninha.json'
 if q.exists():gags[rec['key']]=[((x['start']-1)/30,x['end']/30)for x in json.loads(q.read_text())['gags']]
 else:
  info=json.loads((R/rec['production']/'timeline.json').read_text());gags[rec['key']]=[((x['start']-1)/info['fps'],x['end']/info['fps'])for x in info['shots']if x['kind']=='gag']
 for cue in[c for c in plan['cues']if c['chapter']==rec['key']]:
  x=cue['local_start_frame']/30;y=x+cue['frames']/30;assert y<=rec['frames']/30+1e-7
  assert all(min(y,gb)-max(x,ga)<.00001 for ga,gb in gags[rec['key']]),(cue['id'],x,y)
assert max(c['tlEnd']for t in main['trackInfos']for c in t['clipList'])==round(plan['duration']*1e7)
assert hashlib.sha256((V3/'output/Filmora/Massacote_Completo_MEMES.wfp').read_bytes()).hexdigest()==revision['source_sha256']
report=dict(source_unchanged=True,original_user_edit_and_audio_unchanged=True,original_three_timelines_preserved=True,same_52_memes=True,all_durations_increased=True,quick_entrance_exit_preserved=True,images_range=[min(images),max(images)],video_duration_median=statistics.median(video_durations),videos=video_checks,no_loop_freeze_or_slow_motion=True,no_meme_overlap=True,no_gag_overlap=True,same_total_duration=True,native_filmora_open=False)
(P/'validacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('TIMING_CHECKS_PASSED',len(images),len(video_checks),statistics.median(video_durations),flush=True)
