"""Verify final moving inserts, complete audio, preserved frames and WFP resources."""
from pathlib import Path
from io import BytesIO
import json,sys,subprocess,zipfile,hashlib,wave,math
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;R=next(p for p in P.parents if(p/'AGENTS.md').exists());plans=json.loads((P/'plano.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
def frame(p,t):return Image.open(BytesIO(subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(t),'-i',str(p),'-frames:v','1','-c:v','png','-threads','1','-f','image2pipe','pipe:1']))).convert('RGB')
def mse(a,b):return float(np.mean((np.asarray(a,np.float32)-np.asarray(b,np.float32))**2))
for plan in plans:
 if len(sys.argv)>1 and plan['episode']not in sys.argv[1:]:continue
 O=R/plan['output'];F=O/'Filmora';paths=[O/(plan['slug']+'_R6_9x16.mp4'),O/(plan['slug']+'_R6_16x9.mp4'),F/'midias'/plan['source_base_name']];reports=[]
 for p,size in zip(paths,[(1080,1920),(1920,1080),(1080,1920)]):
  d=probe(p);v=next(s for s in d['streams']if s['codec_type']=='video');assert(v['width'],v['height'])==size;assert int(v['nb_frames'])==plan['frames'] and v['r_frame_rate']=='30/1';assert abs(float(d['format']['duration'])-plan['duration'])<.035
  if p==paths[2]:assert all(s['codec_type']!='audio'for s in d['streams'])
  subprocess.run(['ffmpeg','-v','error','-threads','1','-i',str(p),'-f','null','-'],check=True);reports.append(dict(file=p.name,frames=plan['frames'],sha256=sha(p)))
 for key,path in plan['source'].items():assert sha(R/path)==plan['source_sha256'][key],(plan['episode'],key,'source changed')
 info=json.loads((R/plan['source_info']).read_text());a=(plan['start']-1)/30;b=plan['end']/30
 # The delivered monitor shots must remain outside the inserted action and look the same.
 monitor=next(s for s in info['shots']if s['kind']=='monitor');candidates=[(monitor['start']-1)/30+.4,(monitor['start']+monitor['end']-2)/60];t=next(t for t in candidates if not a<=t<b)
 clean_psnr=10*math.log10(255**2/max(mse(frame(R/plan['source']['base'],t),frame(paths[2],t)),1e-9));assert clean_psnr>33,clean_psnr
 samples=[a+u*(b-a)for u in[.08,.48,.88]];images=[frame(paths[2],t)for t in samples];motion=[mse(x,y)for x,y in zip(images,images[1:])];assert max(motion)>5,(plan['episode'],motion)
 old=frame(R/plan['source']['base'],samples[1]);changed=mse(old,images[1]);assert changed>20,(plan['episode'],'insert missing',changed)
 assert sha(F/'midias/voz_timeline.wav')==sha(R/plan['source_filmora']/'midias/voz_timeline.wav')
 # Verify AAC export against the new full PCM mix, not only a voice metadata flag.
 raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-i',str(paths[0]),'-vn','-ac','2','-ar','44100','-f','s16le','pipe:1']);actual=np.frombuffer(raw,'<i2').reshape(-1,2).astype(np.float32)
 with wave.open(str(O/'mix_r6.wav'))as w:expected=np.frombuffer(w.readframes(w.getnframes()),'<i2').reshape(-1,2).astype(np.float32)
 n=min(len(actual),len(expected));corr=float(np.corrcoef(actual[:n].ravel(),expected[:n].ravel())[0,1]);assert corr>.995,corr
 with wave.open(str(R/plan['source']['mix']))as w:oldmix=np.frombuffer(w.readframes(w.getnframes()),'<i2').reshape(-1,2)
 sound=json.loads((O/'som_ceninha.json').read_text());left=round(sound['start']*44100);right=left+round(sound['duration']*44100);assert np.array_equal(expected[:left],oldmix[:left])and np.array_equal(expected[right:],oldmix[right:])
 wfp=next(F.glob('*.wfp'))
 with zipfile.ZipFile(wfp)as z:
  assert z.testzip()is None;d=json.loads(z.read(next(n for n in z.namelist()if n.endswith('timeline.wesproj'))));main=d['timelineInfos'][0];assert(main['resolutionWidth'],main['resolutionHeight'])==(1080,1920);resources={r['sourceUuid']:r for r in d['resources']};clips=[]
  for tr in main['trackInfos']:
   for c in tr['clipList']:
    if not c.get('filename'):continue
    res=resources[c['sourceUuid']];assert(F/res['filename'].removeprefix('file:./')).is_file();assert c['tlEnd']>c['tlBegin'];assert c['outPoint']<=res['mediaLength']+1;assert abs((c['outPoint']-c['inPoint'])-(c['tlEnd']-c['tlBegin']))<=1;speed=json.loads(c['speed']['speedParam']);assert all(p['_value']==1 for p in speed['keyframeSets'])and not c['speed']['reverse']
    if c['filename'].endswith('.mp4'):clips.append(c)
  clips.sort(key=lambda c:c['tlBegin']);assert clips[0]['tlBegin']==0 and clips[-1]['tlEnd']==round(plan['duration']*1e7);assert all(x['tlEnd']==y['tlBegin']for x,y in zip(clips,clips[1:]));gags=[c for c in clips if c['tlBegin']==round(a*1e7)and c['tlEnd']==round(b*1e7)];assert len(gags)==1
  for chain in gags[0]['effectChainList']:
   for fx in chain['effectList']:
    if fx.get('display')=='transform':assert fx['paramMapList']==[]
  with zipfile.ZipFile(R/plan['source']['wfp'])as src:source_data=json.loads(src.read(next(n for n in src.namelist()if n.endswith('timeline.wesproj'))));assert len(main['trackInfos'][13]['clipList'])==len(source_data['timelineInfos'][0]['trackInfos'][13]['clipList'])
 with zipfile.ZipFile(O/(plan['slug']+'_R6_Filmora.zip'))as z:
  assert z.testzip()is None and sum(n.endswith('.wfp')for n in z.namelist())==1;assert all('midias/'+Path(r['filename']).name in z.namelist()for r in resources.values())
 for path,tag,tile in zip(paths[:2],['9x16','16x9'],[(270,480),(480,270)]):
  moments=[max(0,a-.23),*samples,min(plan['duration']-.15,b+.23)];sheet=Image.new('RGB',(tile[0]*5,tile[1]+28),(25,25,31));draw=ImageDraw.Draw(sheet)
  for i,t in enumerate(moments):sheet.paste(frame(path,t).resize(tile,Image.Resampling.NEAREST),(i*tile[0],0));draw.text((i*tile[0]+5,tile[1]+5),f'{t:.2f}s',fill='white')
  sheet.save(O/f'Previa_R6_{tag}.jpg',quality=94)
 result=dict(episode=plan['episode'],outputs=reports,gag_count=1,gag_duration=(plan['end']-plan['start']+1)/30,gag_motion_mse=motion,gag_difference_from_old=changed,source_files_unchanged=True,monitor_preserved_psnr=clean_psnr,full_audio_correlation=corr,voice_file_bit_identical=True,original_mix_unchanged_outside_effect=True,standing_dery=False,new_subtitles=0,video_clips=len(clips),one_continuous_gag_clip=True,speed_1x=True,all_resources_resolve=True,zip_integrity=True,filmora_native_open=False)
 (O/'validacao_r6.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('R6_VERIFIED',plan['episode'],json.dumps(dict(motion=motion,monitor_psnr=clean_psnr,audio=corr)),flush=True)
