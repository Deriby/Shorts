"""Keep the user's native edit; insert short authored gags and separate cues."""
from pathlib import Path
import json,zipfile,copy,uuid,shutil,hashlib,subprocess,wave,base64,struct,sys
P=Path(__file__).resolve().parent;R=next(p for p in P.parents if(p/'AGENTS.md').exists());plans=json.loads((P/'plano.json').read_text());T=10000000
uid=lambda:str(uuid.uuid4())
def dumps(d):return json.dumps(d,ensure_ascii=False,separators=(',',':')).encode()
def userdata(c,resource=None,main_id=None):
 c['thisUId']=uid();c['userData']=[x for x in c.get('userData',[])if x['key']not in[73,74]]
 for x in c['userData']:
  b=None
  if x['key']==3:b=('{'+uid().upper()+'}').encode()
  elif resource and x['key']==10:b=('{'+resource['sourceUuid'].upper()+'}').encode()
  elif resource and x['key']==50:b=Path(resource['filename']).stem.encode()
  elif main_id is not None and x['key']==6:b=struct.pack('<i',main_id)
  if b is not None:
   if x['key']in[3,10,50]:b+=b'\0'*max(0,x['size']-len(b))
   x.update(size=len(b),data=base64.b64encode(b).decode())
 for chain in c.get('effectChainList',[]):
  for effect in chain['effectList']:effect['thisUId']=uid()
def timing(c,a,b,inpoint,outpoint,total):
 c.update(tlBegin=a,tlEnd=b,inPoint=inpoint,outPoint=outpoint)
 pars={'Version':2,'ParameterType':0,'keyframeSets':[{'_time':0.,'Interpolation':6,'_value':1.},{'_time':float(total),'Interpolation':6,'_value':1.}],'_totalTime':float(total)};c['speed']={'offset':inpoint/T,'offsetEnd':outpoint/T,'reverse':False,'speedParam':json.dumps(pars,separators=(',',':'))}
def identity(c):
 for chain in c.get('effectChainList',[]):
  for fx in chain['effectList']:
   if fx.get('display')=='transform':
    fx['paramMapList']=[]
    for v in fx.get('paramList',[]):
     if v['name']in['Scale_x','Scale_y']:v['fxParam']['unValue']=100.
     elif v['name']in['Position_x','Position_y','_Anchor_x','_Anchor_y']:v['fxParam']['unValue']=.5
 for name in ['preTransition','postTransition']:c.pop(name,None)

for plan in plans:
 if len(sys.argv)>1 and plan['episode']not in sys.argv[1:]:continue
 O=R/plan['output'];F=O/'Filmora';M=F/'midias';M.mkdir(parents=True,exist_ok=True);source=R/plan['source']['wfp'];ranges=[(round((g['start']-1)/30*T),round(g['end']/30*T))for g in plan['gags']]
 with zipfile.ZipFile(source)as z:files={n:z.read(n)for n in z.namelist()}
 tl=next(n for n in files if n.endswith('timeline.wesproj'));data=json.loads(files[tl]);main=data['timelineInfos'][0];track=next(t for t in main['trackInfos']if any(c.get('filename','').endswith('.mp4')for c in t['clipList']));oldclips=track['clipList'];video_resource=next(r for r in data['resources']if r['filename'].endswith('.mp4'));new=[]
 for old in oldclips:
  fragments=[(old['tlBegin'],old['tlEnd'])]
  for a,b in ranges:
   parts=[]
   for left,right in fragments:
    if right<=a or left>=b:parts.append((left,right))
    else:
     if left<a:parts.append((left,a))
     if right>b:parts.append((b,right))
   fragments=parts
  for start,end in fragments:
   c=copy.deepcopy(old);offset=old['inPoint']-old['tlBegin'];timing(c,start,end,start+offset,end+offset,plan['duration']);userdata(c,video_resource,main['timelineId']);new.append(c)
 for a,b in ranges:
  proto=next(c for c in oldclips if c['tlBegin']<=a<c['tlEnd']);gag=copy.deepcopy(proto);timing(gag,a,b,a,b,plan['duration']);userdata(gag,video_resource,main['timelineId']);identity(gag);new.append(gag)
 new.sort(key=lambda c:c['tlBegin']);track['clipList']=new
 assert new[0]['tlBegin']==0 and new[-1]['tlEnd']==round(plan['duration']*T);assert all(x['tlEnd']==y['tlBegin']for x,y in zip(new,new[1:]));assert all(sum(c['tlBegin']==a and c['tlEnd']==b for c in new)==1 for a,b in ranges)
 for res in data['resources']:
  name=Path(res['filename']).name;dest=M/name
  if name.endswith('.mp4'):
   assert dest.is_file();probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(dest)]));v=next(s for s in probe['streams']if s['codec_type']=='video');assert int(v['nb_frames'])==plan['frames'];ticks=round(plan['duration']*T);res.update(mediaLength=ticks,bitRate=int(probe['format'].get('bit_rate',0)),audioStreamCount=0);res.pop('audStreamInfo',None);res['vidStreamInfo'][0].update(totalFrames=plan['frames'],streamLength=ticks,bitRate=int(v.get('bit_rate',0)))
   for field in ['fileSize','fileLength']:
    if field in res:res[field]=dest.stat().st_size
  else:shutil.copyfile(R/plan['source_filmora']/'midias'/name,dest)
 # Separate original PCM clips for each visual punch; preserve all previous audio.
 resource_proto=copy.deepcopy(next(r for r in data['resources']if r.get('audStreamInfo')and r['audStreamInfo'][0].get('channels')==2));sound=json.loads((O/'som_ceninha.json').read_text());proto=next((c for tr in main['trackInfos']for c in tr['clipList']if Path(c.get('filename','')).name=='plop_comico.wav'),None)
 if proto is None:proto=next(c for tr in main['trackInfos']for c in tr['clipList']if c.get('filename','').endswith('.wav'))
 for event in sound['events']:
  res=copy.deepcopy(resource_proto);res.update(sourceUuid=uid(),filename='file:./midias/'+event['file'],createDate=-1,modifyDate=0)
  with wave.open(str(M/event['file']))as w:length=w.getnframes()/w.getframerate();sr=w.getframerate();channels=w.getnchannels()
  res.update(mediaLength=round(length*T),videoStreamCount=0,audioStreamCount=1,bitRate=sr*channels*16);res.pop('vidStreamInfo',None);res['audStreamInfo'][0].update(sampleRate=sr,channels=channels,duration=length,streamLength=round(length*T),bitDepth=16,bitRate=sr*channels*16,bytesPerSecond=sr*channels*2,description='Uncompressed PCM',fourCC=541278529)
  for field in ['fileSize','fileLength']:
   if field in res:res[field]=(M/event['file']).stat().st_size
  data['resources'].append(res);effect=copy.deepcopy(proto);effect.update(filename=res['filename'],sourceUuid=res['sourceUuid'],streamId=0);start=round(event['start']*T);timing(effect,start,start+res['mediaLength'],0,res['mediaLength'],length);userdata(effect,res,main['timelineId'])
  for field in ['volumeKeyframe','audioDuckingframe']:effect.pop(field,None)
  for chain in effect.get('effectChainList',[]):chain['effectList']=[]
  main['trackInfos'][7]['clipList'].append(effect)
 main['trackInfos'][7]['clipList'].sort(key=lambda c:c['tlBegin'])
 referenced={Path(r['filename']).name for r in data['resources']}
 for f in M.glob('ceninha_*.wav'):
  if f.name not in referenced:f.unlink()
 name=plan['slug']+'_R6_9x16';data['projectName']=name;files[tl]=dumps(data);meta=json.loads(files['ProjectFolder/project_info.json']);meta.update(project_file_name=name,proj_zip_save_path=name+'.wfp',project_timeline_duration=round(plan['duration']*T),project_current_position=0);files['ProjectFolder/project_info.json']=dumps(meta)
 root=tl.split('/')[2];items={};ids=[]
 for res in data['resources']:
  mid='{'+res['sourceUuid'].upper()+'}';ids.append(mid);items[mid]={'name':Path(res['filename']).name,'download_url':res['filename'].replace('file:./','./'),'id':mid,'media_type':8 if res.get('videoStreamCount')else 4,'media_length':res['mediaLength'],'stream_idx':0,'mark_info_list':[{'mark_in':-1,'mark_out':-1}]};sourceinfo={'basicInfo':{k:res[k]for k in ['streamType','fourCC','mediaLength','videoStreamCount','audioStreamCount','bitRate']if k in res},'vidStreamInfos':res.get('vidStreamInfo',[]),'audStreamInfos':res.get('audStreamInfo',[])};files[f'ProjectFolder/Medias/{mid}/media.json']=dumps({'version':'1.1.5','file_name':items[mid]['download_url'],'sourceInfo':sourceinfo})
 files['ProjectFolder/Medias/medias_info.json']=('{"media_structure":{"Folder":{'+','.join('"media_item":'+json.dumps(i)for i in ids)+'},"media_item":'+json.dumps(root)+'},"media_items":'+json.dumps(items)+'}').encode()
 wfp=F/(name+'.wfp')
 with zipfile.ZipFile(wfp,'w',zipfile.ZIP_DEFLATED)as z:
  for n,value in files.items():z.writestr(n,value)
 fonts=R/plan['source_filmora']/'fontes'
 if fonts.exists():shutil.copytree(fonts,F/'fontes',dirs_exist_ok=True)
 (F/'LEIA_PRIMEIRO.txt').write_text('''REVISÃO R6 — CENINHAS CURTAS LIGADAS ÀS FALAS

Extraia o ZIP inteiro. Projeto somente 9:16, com mídias em midias/.
Voz, trilha, sons anteriores e sons discretos das novas cenas ficam separados.
A base de vídeo é silenciosa. Os inserts curtos entram nas falas indicadas;
o restante da montagem, o jogo no PC e a duração continuam preservados.
Dery fica sentado; o PSX é da animação. Gameplay/fotos/memes ficam limpos.
Nenhuma legenda foi acrescentada. Os títulos nativos antigos de GTA/BMX
continuam editáveis, como no projeto recebido.

O nome da base foi mantido para facilitar a troca num projeto já legendado.
Para os novos cortes e o efeito sonoro separado, abra este WFP R6.
O projeto Filmora do longo 16:9 continua reservado ao final da série.
Os MP4s são composições do ambiente; Filmora não foi executado no Linux.
Estrutura/recursos conferidos não substituem a abertura no aplicativo.
''')
 bundle=O/(plan['slug']+'_R6_Filmora.zip')
 with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED,allowZip64=True)as z:
  for f in F.rglob('*'):
   if f.is_file():z.write(f,str(f.relative_to(F)),compress_type=zipfile.ZIP_STORED if f.suffix in['.mp4','.ttf']else zipfile.ZIP_DEFLATED)
 (O/'filmora_r6.json').write_text(json.dumps(dict(source_project=plan['source']['wfp'],source_project_unchanged=True,project=wfp.name,video_clips=len(new),gag_count=len(ranges),each_gag_continuous=True,gag_ranges_ticks=ranges,new_subtitles=0,new_sound_files=[e['file']for e in sound['events']],all_media_bundled=True,only_9x16=True,filmora_native_open=False),ensure_ascii=False,indent=2)+'\n');print('R6_PACKAGED',plan['episode'],len(new),flush=True)
