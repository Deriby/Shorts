"""Append editable memes to the user-saved WFP, preserving every existing clip."""
from pathlib import Path
import json,zipfile,copy,uuid,base64,hashlib,struct,subprocess,wave
P=Path(__file__).resolve().parent;R=next(p for p in P.parents if(p/'AGENTS.md').exists());F=P/'output/Filmora';M=F/'midias';OLD=P.parent/'output/Filmora';SOURCE=P/'recebido/Massacote_Completo_Atualizado_Usuario.wfp';OUT=F/'Massacote_Completo_MEMES.wfp'
ROOT='{204E72A3-B517-44d4-806F-9E9D84D5F904}';TL=f'ProjectFolder/Medias/{ROOT}/timeline.wesproj';LIB='ProjectFolder/Medias/medias_info.json';EXTRA=f'ProjectFolder/Medias/{ROOT}/extra.json';T=10000000
plan=json.loads((P/'plano_preparado.json').read_text())
def uid():return str(uuid.uuid4())
def guid():return '{'+uid().upper()+'}'
def dump(x):return json.dumps(x,ensure_ascii=False,separators=(',',':')).encode()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source_sha=sha(SOURCE)
with zipfile.ZipFile(SOURCE)as z:raw={n:z.read(n)for n in z.namelist()}
data=json.loads(raw[TL]);original=copy.deepcopy(data);main=next(t for t in data['timelineInfos']if t['timelineId']==data['currentTimelineId']);library=json.loads(raw[LIB]);extra=json.loads(raw[EXTRA]);original_library=copy.deepcopy(library)
old_media={x.name for x in(OLD/'midias').iterdir()if x.is_file()}
def relocate(x):
 if isinstance(x,dict):return {k:relocate(v)for k,v in x.items()}
 if isinstance(x,list):return [relocate(v)for v in x]
 if isinstance(x,str)and '/midias/'in x and Path(x).name in old_media:
  return ('file:./'if x.startswith('file:')else'./')+'midias/'+Path(x).name
 return x
data=relocate(data);main=next(t for t in data['timelineInfos']if t['timelineId']==data['currentTimelineId']);library=relocate(library)
clips=[c for tr in main['trackInfos']for c in tr['clipList']]
video=next(c for c in clips if c.get('filename','').endswith('.mp4'));image=next(c for c in clips if c.get('filename','').endswith('.png'));audio=next(c for c in clips if c.get('filename','').endswith('.wav'))
def fxes(c):return [e for ch in c.get('effectChainList',[])for e in ch['effectList']]
transform_proto=next(e for e in fxes(video)if e.get('display')=='transform')
video_res=next(r for r in data['resources']if r.get('videoStreamCount')and r['filename'].endswith('.mp4'));image_res=next(r for r in data['resources']if r['filename'].endswith('.png'));audio_res=next(r for r in data['resources']if r.get('audioStreamCount'))
new_ids=[];resources={};new_clips=[];new_sounds=[]
max_tag=max(t.get('trackTag',0)for t in main['trackInfos'])
sound_track=copy.deepcopy(main['trackInfos'][6]);sound_track.update(clipList=[],uuid=uid(),trackTag=max_tag+1)
visual_track=copy.deepcopy(main['trackInfos'][11]);visual_track.update(clipList=[],uuid=uid(),trackTag=max_tag+2)
main['trackInfos'] += [sound_track,visual_track]
def resource(path):
 if path.name in resources:return resources[path.name]
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
 isimg=path.suffix=='.png';isaudio=path.suffix=='.wav';r=copy.deepcopy(image_res if isimg else audio_res if isaudio else video_res);r.update(sourceUuid=uid(),filename='file:./midias/'+path.name,createDate=-1,modifyDate=0)
 if isimg:
  dur=86400.;r.update(mediaLength=0,streamType=5,videoStreamCount=1,audioStreamCount=0);r.pop('audStreamInfo',None)
  r['vidStreamInfo'][0].update(width=1920,height=1080,xRatio=1920,yRatio=1080,alphaChannel=1,bitsDepth=32,totalFrames=0,streamLength=0)
 elif isaudio:
  with wave.open(str(path))as w:dur=w.getnframes()/w.getframerate();channels=w.getnchannels();sr=w.getframerate()
  r.update(mediaLength=round(dur*T),streamType=3,videoStreamCount=0,audioStreamCount=1,bitRate=sr*channels*16);r.pop('vidStreamInfo',None)
  r['audStreamInfo'][0].update(audStreamId=0,sampleRate=sr,channels=channels,duration=dur,streamLength=round(dur*T),bitDepth=16,bitRate=sr*channels*16,bytesPerSecond=sr*channels*2,description='Uncompressed PCM',fourCC=541278529)
 else:
  v=probe['streams'][0];num,den=map(int,v['r_frame_rate'].split('/'));dur=int(v['nb_frames'])*den/num
  r.update(mediaLength=round(dur*T),streamType=1,videoStreamCount=1,audioStreamCount=0,bitRate=int(probe['format']['bit_rate']));r.pop('audStreamInfo',None)
  r['vidStreamInfo'][0].update(vidStreamId=0,width=1920,height=1080,xRatio=1920000,yRatio=1080000,frameRate={'num':num,'den':den},maxFrameRate={'num':num,'den':den},lastframeRate={'num':num,'den':den},totalFrames=int(v['nb_frames']),streamLength=round(dur*T),bitRate=int(v.get('bit_rate',0)),alphaChannel=0)
 data['resources'].append(r);mid=guid();new_ids.append(mid)
 typ=16 if isimg else 4 if isaudio else 2;item=copy.deepcopy(next(x for x in library['media_items'].values()if x.get('media_type')==typ));item.update(id=mid,name=path.stem,download_url='./midias/'+path.name,media_type=typ,media_length=50000000 if isimg else r['mediaLength'],stream_idx=-1 if isimg else 0,src_md5=hashlib.md5(path.read_bytes()).hexdigest(),mark_info_list=[{'mark_in':-1,'mark_out':-1}],scence_info=[]);library['media_items'][mid]=item
 basic={k:r[k]for k in ['streamType','fourCC','mediaLength','programCount','videoStreamCount','audioStreamCount','subPicStreamCount','bitRate','createDate']if k in r};basic.setdefault('programCount',0);basic.setdefault('subPicStreamCount',0)
 raw[f'ProjectFolder/Medias/{mid}/media.json']=dump(dict(version='1.1.5',file_name='./midias/'+path.name,sourceInfo=dict(basicInfo=basic,vidStreamInfos=r.get('vidStreamInfo',[]),audStreamInfos=r.get('audStreamInfo',[]),recordInfos={})))
 resources[path.name]=(r,mid,dur);return resources[path.name]
def setdata(c,k,value):
 b=value if isinstance(value,bytes)else value.encode();u=next((u for u in c['userData']if u['key']==k),None)
 if u is None:u={'key':k,'size':len(b),'data':''};c['userData'].append(u)
 if not isinstance(value,bytes):b+=b'\0'*max(0,u['size']-len(b))
 u.update(size=len(b),data=base64.b64encode(b).decode())
def make_clip(proto,r,mid,start,duration,total):
 c=copy.deepcopy(proto)
 for k in ['preTransition','postTransition','stabilization','stabilizeAnalysisData','image_denoise','face_cluster','volumeKeyframe','audioDuckingframe']:c.pop(k,None)
 c.update(filename=r['filename'],sourceUuid=r['sourceUuid'],thisUId=uid(),streamId=0,inPoint=0,outPoint=round(duration*T),tlBegin=round(start*T),tlEnd=round(start*T)+round(duration*T));c['userData']=[u for u in c.get('userData',[])if u['key']not in[73,74]]
 clipguid=guid();setdata(c,3,clipguid);setdata(c,10,mid);setdata(c,50,Path(r['filename']).stem);setdata(c,6,struct.pack('<i',main['timelineId']));extra['mediaClipsMapInfo'][clipguid]=dict(mediaId=mid,subClips={})
 c['speed']=dict(offset=0.,offsetEnd=duration,reverse=False,speedParam=dump(dict(Version=2,ParameterType=0,keyframeSets=[{'_time':0.,'Interpolation':6,'_value':1.},{'_time':total,'Interpolation':6,'_value':1.}],_totalTime=total)).decode())
 c['pipBuf']='{"Algorithm":"Bilinear","BlendMode":0,"BlenderName":"video/blender/simple-pip","Enable":true,"Opacity":100.0}';c['pipBufSize']=len(c['pipBuf']);return c

def transform(c,style,duration):
 fx=copy.deepcopy(transform_proto);fx['thisUId']=uid();fx['paramMapList']=[]
 values={'EnableTransform':1,'_Anchor_x':.5,'_Anchor_y':.5,'Position_x':.5,'Position_y':.5,'Scale_x':100.,'Scale_y':100.,'Rotation':0.}
 fx['paramList']=[dict(name=k,fxParam=dict(paramType=5 if k=='EnableTransform'else 3,unValue=v))for k,v in values.items()]
 if style=='popup':
  points={'Position_x':[(0,.85),(.10,.49),(.20,.5),(duration-.13,.5),(duration,.83)],'Scale_x':[(0,94),(.12,103),(.23,100),(duration,100)],'Rotation':[(0,3),(.15,-1),(.25,0),(duration,0)]}
 else:points={'Scale_x':[(0,104),(.13,100),(duration-.07,101.5),(duration,101.5)]}
 points['Scale_y']=points['Scale_x']
 for name,ks in points.items():
  fx['paramMapList'].append(dict(key=3,name=name,keyFrame=dict(parameter=dump(dict(Version=2,ParameterType=0,keyframeSets=[dict(_time=round(t*T)/T,Interpolation=1,_value=v)for t,v in ks])).decode())))
 c['effectChainList']=[{'name':'Basic','effectList':[fx]},{'name':'Effect','effectList':[]}]
for cue in plan['cues']:
 path=M/cue['prepared_file'];r,mid,total=resource(path);duration=cue['frames']/30;c=make_clip(image if path.suffix=='.png'else video,r,mid,cue['start_frame']/30,duration,total);transform(c,cue['style'],duration);visual_track['clipList'].append(c);cue['native_clip_id']=c['thisUId'];new_clips.append(c)
 if cue['sound_tag']:
  info=next(s for s in plan['sounds']if s['tag']==cue['sound_tag']);r,mid,total=resource(M/info['file']);c=make_clip(audio,r,mid,cue['start_frame']/30,total,total)
  c['effectChainList']=[{'name':'Basic','effectList':[]},{'name':'Effect','effectList':[]}];sound_track['clipList'].append(c);new_sounds.append(c)
for t in[sound_track,visual_track]:t['clipList'].sort(key=lambda c:c['tlBegin'])
# Relocate only JSON paths on copies; keep all native timelines, effects and cache entries.
for name,b in list(raw.items()):
 if name.endswith('.json')and name not in[LIB,EXTRA]:
  try:raw[name]=dump(relocate(json.loads(b)))
  except json.JSONDecodeError:pass
data['projectName']=OUT.stem;raw[TL]=dump(data);raw[EXTRA]=dump(extra)
oldlib=raw[LIB].decode();prefix=oldlib[:oldlib.index('"media_items":')];pos=prefix.index('},"media_item":');addition=','.join('"media_item":'+json.dumps(x)for x in new_ids);prefix=prefix[:pos]+(','+addition if addition else'')+prefix[pos:];raw[LIB]=(prefix+'"media_items":'+dump(library['media_items']).decode()+'}').encode()
meta=json.loads(raw['ProjectFolder/project_info.json']);meta.update(project_file_name=OUT.stem,proj_zip_save_path=OUT.name,project_guid=guid());raw['ProjectFolder/project_info.json']=dump(meta)
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_STORED)as z:
 for n,b in raw.items():z.writestr(n,b)
assert sha(SOURCE)==source_sha
report=dict(source=str(SOURCE.relative_to(R)),source_sha256=source_sha,project=OUT.name,project_sha256=sha(OUT),original_timelines=3,original_main_clips=353,added_visual_clips=len(new_clips),added_sound_clips=len(new_sounds),new_resources=len(resources),duration=plan['duration'],all_original_edits_preserved_except_portable_paths=True,filmora_native_open=False,visual_track=len(main['trackInfos'])-1,sound_track=len(main['trackInfos'])-2)
(P/'projeto.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');(P/'plano_aplicado.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n');print('MEME_PROJECT_READY',len(new_clips),len(new_sounds),len(resources),OUT.stat().st_size,flush=True)
