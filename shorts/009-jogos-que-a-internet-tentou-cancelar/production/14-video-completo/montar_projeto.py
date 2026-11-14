"""Portable landscape WFP: approved picture streams, native cuts/audio/card layers."""
from pathlib import Path
import json,zipfile,copy,uuid,base64,struct,wave,math,subprocess,shutil,ast,hashlib
import numpy as np
P=Path(__file__).resolve().parent;R=next(x for x in P.parents if(x/'AGENTS.md').exists());O=P/'output';F=O/'Filmora';M=F/'midias';plan=json.loads((P/'montagem.json').read_text());TICKS=10000000;ROOT='{204E72A3-B517-44d4-806F-9E9D84D5F904}';TL=f'ProjectFolder/Medias/{ROOT}/timeline.wesproj';main_id=36
source=R/'shorts/009-jogos-que-a-internet-tentou-cancelar/production/00-intro/output/Filmora/Intro_Cancelar_16x9.wfp'
with zipfile.ZipFile(source)as z:raw={n:z.read(n)for n in z.namelist()}
data=json.loads(raw[TL]);main=copy.deepcopy(data['timelineInfos'][0]);main.update(resolutionWidth=1920,resolutionHeight=1080,aspectRatioX=16,aspectRatioY=9,frameRate={'num':60,'den':1})
for tr in main['trackInfos']:tr['clipList']=[]
reference_source=R/'shorts/008-personagens-que-a-internet-estragou/production/20-edicao-final-usuario/Massacote_EDICAO_FINAL_USUARIO.wfp'
with zipfile.ZipFile(reference_source)as z:reference=json.loads(z.read(TL))
video_proto=next(c for tr in data['timelineInfos'][0]['trackInfos']for c in tr['clipList']if c.get('filename','').endswith('.mp4'));audio_proto=next(c for tr in data['timelineInfos'][0]['trackInfos']for c in tr['clipList']if c.get('filename','').endswith('.wav'));transform_proto=next(e for ch in video_proto['effectChainList']for e in ch['effectList']if e.get('display')=='transform')
image_proto=next(c for tl in reference['timelineInfos']for tr in tl['trackInfos']for c in tr['clipList']if c.get('filename','').lower().endswith('.png'));image_resource_proto=next(r for r in reference['resources']if r['filename']==image_proto['filename'])
audio_resource_proto=next(r for r in data['resources']if r.get('audioStreamCount'));volume_proto=next(e for tl in reference['timelineInfos']for tr in tl['trackInfos']for c in tr['clipList']for ch in c.get('effectChainList',[])for e in ch['effectList']if e.get('display')=='volume');glow=next(e for tl in reference['timelineInfos']for tr in tl['trackInfos']for c in tr['clipList']for ch in c.get('effectChainList',[])for e in ch['effectList']if e.get('display')=='Glow')
# Reuse proven native resource/timing serializers from the chapter projects.
helper=R/'shorts/009-jogos-que-a-internet-tentou-cancelar/production/00-intro/make_filmora.py';code=helper.read_text();tree=ast.parse(code)
for node in tree.body:
 if isinstance(node,ast.FunctionDef)and node.name in['uid','ticks','dump','sha','userdata','source_speed','transform','resource']:exec(compile(ast.get_source_segment(code,node),str(helper),'exec'))
resources=[];byname={};audit=[];native_mix=np.zeros((plan['frames']*1470,2),np.float64);main_video=main['trackInfos'][11]['clipList'];voices=[];audio_checks=[]
def register(path,proto):
 if path.name not in byname:
  r,duration=resource(path,proto);resources.append(r);byname[path.name]=(r,duration)
 return byname[path.name]
def picture(name):
 if name not in byname:
  r=copy.deepcopy(image_resource_proto);r.update(sourceUuid=uid(),filename='file:./midias/'+name,mediaLength=0,createDate=0,modifyDate=0,videoStreamCount=1,audioStreamCount=0,streamType=5);r.pop('audStreamInfo',None)
  for v in r['vidStreamInfo']:v.update(width=1920,height=1080,xRatio=1920,yRatio=1080,alphaChannel=1,bitsDepth=32,totalFrames=0,streamLength=0,frameRate={'num':30,'den':1},maxFrameRate={'num':30,'den':1})
  resources.append(r);byname[name]=(r,86400)
 return byname[name]
def pcm(path):
 with wave.open(str(path))as w:
  assert(w.getframerate(),w.getsampwidth())==(44100,2);x=np.frombuffer(w.readframes(w.getnframes()),'<i2').reshape(-1,w.getnchannels()).astype(np.float64)/32768
 return np.repeat(x,2,axis=1)if x.shape[1]==1 else x

def add_audio(c,res,resource_duration,offset,gain=1):
 oldstart=c['tlBegin'];c=copy.deepcopy(c);c.update(filename=res['filename'],sourceUuid=res['sourceUuid']);c['tlBegin']=round(offset*TICKS/30+c['tlBegin']);c['tlEnd']=round(offset*TICKS/30+c['tlEnd']);
 if c['outPoint']>res['mediaLength']:
  assert c['outPoint']-res['mediaLength']<=10;c['outPoint']=res['mediaLength'];c['tlEnd']=c['tlBegin']+c['outPoint']-c['inPoint']
 userdata(c,res);source_speed(c,c['inPoint']/TICKS,c['outPoint']/TICKS,resource_duration)
 for chain in c.get('effectChainList',[]):
  for fx in chain['effectList']:
   if fx.get('display')=='volume'and fx.get('paramList'):raise RuntimeError('Inspect an existing volume adjustment before combining')
 if abs(gain-1)>1e-8:
  fx=copy.deepcopy(volume_proto);fx['thisUId']=uid();fx['paramList']=[{'name':'VolumeGain','fxParam':{'paramType':2,'unValue':20*math.log10(gain)}}];c['effectChainList'][-1]['effectList'].append(fx)
 name=Path(res['filename']).name;track=8 if'voz'in name else 6 if'trilha'in name else 7;main['trackInfos'][track]['clipList'].append(c)
 x=pcm(M/name);begin=round(c['inPoint']/TICKS*44100);count=round((c['tlEnd']-c['tlBegin'])/TICKS*44100);start=round(c['tlBegin']/TICKS*44100);x=x[begin:begin+count]*gain;native_mix[start:start+len(x)]+=x
 if'voz'in name:voices.append(dict(file=name,start_frame=offset,sha256=sha(M/name),samples=len(x)))
 return c
for rec in plan['records']:
 start,end=rec['start'],rec['end'];duration=rec['frames']/30
 if rec['type']=='body':
  project=R/rec['source_project'];assert sha(project)==rec['source_project_sha256'];assert sha(R/rec['source_video'])==rec['source_sha256']
  with zipfile.ZipFile(project)as z:old=json.loads(z.read(TL))
  oldmain=old['timelineInfos'][0];assert len(old['timelineInfos'])==1;oldres={r['sourceUuid']:r for r in old['resources']};vr=next(r for r in old['resources']if r['filename'].endswith('.mp4'));new_video,_=register(M/rec['media'],vr);used_audio={}
  for tr in oldmain['trackInfos']:
   for c in tr['clipList']:
    if c.get('filename','').endswith('.mp4'):
     new=copy.deepcopy(c);new.update(filename=new_video['filename'],sourceUuid=new_video['sourceUuid'],streamId=0,tlBegin=round(start*TICKS/30+c['tlBegin']),tlEnd=round(start*TICKS/30+c['tlEnd']));userdata(new,new_video);source_speed(new,c['inPoint']/TICKS,c['outPoint']/TICKS,duration);transform(new,{'Scale_x':100.,'Scale_y':100.,'Position_x':.5,'Position_y':.5,'_Anchor_x':.5,'_Anchor_y':.5})
     for k in['preTransition','postTransition','stabilization','stabilizeAnalysisData']:new.pop(k,None)
     main_video.append(new)
    elif c.get('filename','').endswith('.wav'):
     oldr=oldres[c['sourceUuid']];name=Path(oldr['filename']).name;dest=M/(rec['key']+'_'+name);source_path=R/rec['source_folder']/'midias'/name
     if not dest.exists():shutil.copyfile(source_path,dest)
     r,rd=register(dest,oldr);gain=json.loads((R/rec['production']/'edicao.json').read_text())['mix_gain'];gain=1 if name.startswith('ceninha_')else gain;add_audio(c,r,rd,start,gain)
  rec['video_clip_count']=sum(c['tlBegin']>=ticks(start/30)and c['tlEnd']<=ticks(end/30)for c in main_video)
  ref=(R/rec['source_video']).parent/'mix_r6.wav'
  if not ref.exists():ref=R/rec['production']/'assets/audio/mix_final.wav'
  expected=pcm(ref);actual=native_mix[start*1470:end*1470];assert expected.shape==actual.shape
  correlation=float(np.corrcoef(expected.ravel(),actual.ravel())[0,1]);error=float(np.max(np.abs(expected-actual)));assert correlation>.999,(rec['title'],correlation,error);audio_checks.append(dict(title=rec['title'],correlation=correlation,max_pcm_difference=error))
 else:
  for layer,name,dx,settle in [(11,rec['background'],0,.24),(12,rec['hero'],.04,.30),(13,rec['title_image'],-.04,.24)]:
   r,rd=picture(name);c=copy.deepcopy(image_proto);c.update(filename=r['filename'],sourceUuid=r['sourceUuid'],tlBegin=ticks(start/30),tlEnd=ticks(end/30),inPoint=0,outPoint=ticks(duration),streamId=0);userdata(c,r);source_speed(c,0,duration,rd);a=start/30;b=end/30
   # Native transform key times are source-media times, as on the body clips.
   transform(c,{'Scale_x':100.,'Scale_y':100.,'Position_x':.5,'Position_y':.5,'_Anchor_x':.5,'_Anchor_y':.5},None if not dx else{'Position_x':[(0,.5+dx),(settle,.5),(duration,.5)]})
   if layer==13:
    fx=copy.deepcopy(glow);fx['thisUId']=uid();c['effectChainList'][1]['effectList'].append(fx)
   main['trackInfos'][layer]['clipList'].append(c)
  r,rd=register(M/rec['sound'],audio_resource_proto);c=copy.deepcopy(audio_proto);c.update(filename=r['filename'],sourceUuid=r['sourceUuid'],tlBegin=0,tlEnd=ticks(rd),inPoint=0,outPoint=ticks(rd),streamId=0);add_audio(c,r,rd,start)
  audit.append(dict(game=rec['title'],start=start/30,end=end/30,layered_pngs=True,source_time_keyframes=True,paid_glow_title_only=True))
# Keep the approved audio headroom. Only native volume parameters change level.
peak=float(np.max(np.abs(native_mix)));assert peak<1.001,peak
with wave.open(str(Path('/workspace/attachments/longo009/mixagem_completa.wav')),'wb')as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(44100);w.writeframes(np.int16(np.clip(np.round(native_mix*32768),-32768,32767)).tobytes())
for tr in main['trackInfos']:tr['clipList'].sort(key=lambda c:(c['tlBegin'],c['tlEnd']))
# Reconcile one 100 ns tick from independently rounded chapter boundaries.
for left,right in zip(main_video,main_video[1:]):
 if left['tlEnd']!=right['tlBegin']:
  assert abs(left['tlEnd']-right['tlBegin'])<=1;left['tlEnd']=right['tlBegin']
name='Jogos_Que_A_Internet_Tentou_Cancelar_COMPLETO_16x9';data.update(projectName=name,currentTimelineId=main_id,timelineInfos=[main],resources=resources);files={n:b for n,b in raw.items()if not n.startswith('ProjectFolder/Medias/')};files[TL]=dump(data);meta=json.loads(files['ProjectFolder/project_info.json']);meta.update(project_file_name=name,proj_zip_save_path=name+'.wfp',project_timeline_duration=ticks(plan['duration']),project_current_position=0,proj_cover_proj_path='',project_custom_cover=False);files['ProjectFolder/project_info.json']=dump(meta)
items={};ids=[]
for r in resources:
 mid='{'+r['sourceUuid'].upper()+'}';ids.append(mid);items[mid]=dict(id=mid,name=Path(r['filename']).name,download_url=r['filename'].replace('file:./','./'),media_type=16 if r.get('streamType')==5 else 8 if r.get('videoStreamCount')else 4,media_length=r['mediaLength'],stream_idx=0,mark_info_list=[dict(mark_in=-1,mark_out=-1)]);si=dict(basicInfo={k:r[k]for k in ['streamType','fourCC','mediaLength','videoStreamCount','audioStreamCount','bitRate']if k in r},vidStreamInfos=r.get('vidStreamInfo',[]),audStreamInfos=r.get('audStreamInfo',[]));files[f'ProjectFolder/Medias/{mid}/media.json']=dump(dict(version='1.1.5',file_name=items[mid]['download_url'],sourceInfo=si))
files['ProjectFolder/Medias/medias_info.json']=('{"media_structure":{"Folder":{'+','.join('"media_item":'+json.dumps(i)for i in ids)+'},"media_item":'+json.dumps(ROOT)+'},"media_items":'+json.dumps(items)+'}').encode()
with zipfile.ZipFile(F/(name+'.wfp'),'w',zipfile.ZIP_DEFLATED)as z:
 for n,b in files.items():z.writestr(n,b)
report=dict(project=name+'.wfp',duration=plan['duration'],frames=plan['frames'],native_video_cuts=len(main_video),audio_clips=sum(len(main['trackInfos'][i]['clipList'])for i in[6,7,8]),resources=len(resources),chapter_cards=audit,voices=voices,audio_reconstruction=audio_checks,peak=peak,body_zooms_already_in_video=True,body_native_transform_identity=True,existing_sources_unchanged=True,filmora_native_open=False);(P/'projeto.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');(P/'montagem.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n');print('COMPLETE_PROJECT_READY',name,plan['duration'],flush=True)
