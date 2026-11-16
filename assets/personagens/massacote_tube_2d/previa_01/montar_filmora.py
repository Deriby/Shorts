"""WFP 16:9 com PNGs/camadas e keyframes editáveis. Não executa o Filmora."""
from pathlib import Path
import json,zipfile,copy,uuid,base64,struct,hashlib,wave,importlib.util
P=Path(__file__).resolve().parent;R=next(p for p in P.parents if(p/'AGENTS.md').exists());F=P/'Filmora';M=F/'midias';T=10000000
SOURCE=R/'shorts/009-jogos-que-a-internet-tentou-cancelar/production/14-video-completo/revisao_memes_v4_tempo/output/Filmora/Massacote_MEMES_Tempo_Corrigido.wfp'
ROOT='{204E72A3-B517-44d4-806F-9E9D84D5F904}';TL=f'ProjectFolder/Medias/{ROOT}/timeline.wesproj';EXTRA=f'ProjectFolder/Medias/{ROOT}/extra.json';LIB='ProjectFolder/Medias/medias_info.json';OUT=F/'Massacote_Tube_Previa_Conversando.wfp'
plan=json.loads((P/'keyframes.json').read_text());duration=plan['duration'];ticks=lambda t:round(t*T)
def uid():return str(uuid.uuid4())
def guid():return '{'+uid().upper()+'}'
def dump(x):return json.dumps(x,ensure_ascii=False,separators=(',',':')).encode()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source_sha=sha(SOURCE)
with zipfile.ZipFile(SOURCE)as z:raw={n:z.read(n)for n in z.namelist()}
data=json.loads(raw[TL]);main=next(t for t in data['timelineInfos']if t['timelineId']==data['currentTimelineId']);library=json.loads(raw[LIB]);extra=json.loads(raw[EXTRA]);meta=json.loads(raw['ProjectFolder/project_info.json'])
clips=[c for tr in main['trackInfos']for c in tr['clipList']];image=next(c for c in clips if c.get('filename','').endswith('.png'));audio=next(c for c in clips if c.get('filename','').endswith('.wav'));transform_proto=next(e for ch in image['effectChainList']for e in ch['effectList']if e.get('display')=='transform')
image_res=next(r for r in data['resources']if r['filename']==image['filename']);audio_res=next(r for r in data['resources']if r['filename']==audio['filename'])
root_item=copy.deepcopy(library['media_items'][ROOT]);image_item=copy.deepcopy(next(x for x in library['media_items'].values()if x.get('media_type')==16));audio_item=copy.deepcopy(next(x for x in library['media_items'].values()if x.get('media_type')==4))
files={n:b for n,b in raw.items()if not n.startswith('ProjectFolder/Medias/')}
for key in ['usedTemplateResInfo','mediaClipsMapInfo','pendingMarkersInfo','highlightInfo']:extra[key]={}
extra['allMarkersInfo']={'beatDetectInfo':{}};extra['fontNameInfo']=[];extra['usedBizFont']=[];extra['TextSentence']={'TextSentence':[]}
resources=[];items={};entries={};timeline_uuid=guid()

def setdata(obj,key,value):
    obj.setdefault('userData',[]);u=next((u for u in obj['userData']if u['key']==key),None)
    if u is None:u={'key':key,'size':0,'data':''};obj['userData'].append(u)
    b=value if isinstance(value,bytes)else value.encode();b+=b'\0'*max(0,u['size']-len(b))
    u.update(size=len(b),data=base64.b64encode(b).decode())

main=copy.deepcopy(main);main.update(frameRate={'num':30,'den':1},resolutionWidth=1920,resolutionHeight=1080,aspectRatioX=16,aspectRatioY=9,sampleRate=48000)
setdata(main,11000,timeline_uuid);setdata(main,50,'Massacote Tube — Prévia 2D')
tracks=[dict(trackType=2,uuid=uid(),clipList=[])]
for tag in range(4):
    tracks.append(dict(trackType=1,trackTag=tag+1,uuid=uid(),userData=[{'key':21,'size':4,'data':'AQAAAA=='},{'key':12001,'size':1,'data':'AA=='}],clipList=[]))
main['trackInfos']=tracks

def resource(name,is_audio=False):
    if name in entries:return entries[name]
    path=M/name;r=copy.deepcopy(audio_res if is_audio else image_res);r.update(sourceUuid=uid(),filename='file:./midias/'+name,createDate=-1,modifyDate=0,videoStreamCount=0 if is_audio else 1,audioStreamCount=1 if is_audio else 0)
    if is_audio:
        with wave.open(str(path))as w:dur=w.getnframes()/w.getframerate();sr=w.getframerate();ch=w.getnchannels()
        r.update(mediaLength=ticks(dur),streamType=3,bitRate=sr*ch*16);r.pop('vidStreamInfo',None)
        s=r['audStreamInfo'][0];s.update(audStreamId=0,sampleRate=sr,channels=ch,duration=dur,streamLength=ticks(dur),bitDepth=16,bitRate=sr*ch*16,bytesPerSecond=sr*ch*2,description='Uncompressed PCM',fourCC=541278529)
    else:
        r.update(mediaLength=0,streamType=5,bitRate=0);r.pop('audStreamInfo',None)
        r['vidStreamInfo'][0].update(vidStreamId=0,width=1920,height=1080,xRatio=1920,yRatio=1080,alphaChannel=0 if name=='fundo.png' else 1,bitsDepth=24 if name=='fundo.png' else 32,totalFrames=0,streamLength=0,frameRate={'num':30,'den':1},maxFrameRate={'num':30,'den':1},lastframeRate={'num':30,'den':1},premultiAlphaTypePhoto=-1)
    mid=guid();item=copy.deepcopy(audio_item if is_audio else image_item);item.update(id=mid,name=path.stem,download_url='./midias/'+name,media_type=4 if is_audio else 16,media_length=ticks(duration) if is_audio else 50000000,stream_idx=0 if is_audio else -1,src_md5=hashlib.md5(path.read_bytes()).hexdigest(),mark_info_list=[dict(mark_in=-1,mark_out=-1)],scence_info=[])
    items[mid]=item;resources.append(r)
    basic={k:r[k]for k in ['streamType','fourCC','mediaLength','programCount','videoStreamCount','audioStreamCount','subPicStreamCount','bitRate','createDate']if k in r};basic.setdefault('programCount',0);basic.setdefault('subPicStreamCount',0)
    files[f'ProjectFolder/Medias/{mid}/media.json']=dump(dict(version='1.1.5',file_name='./midias/'+name,sourceInfo=dict(basicInfo=basic,vidStreamInfos=r.get('vidStreamInfo',[]),audStreamInfos=r.get('audStreamInfo',[]),recordInfos={})))
    entries[name]=(r,mid);return r,mid

curves_count=0;point_count=0

def clip(name,start,end,part=None,frames=None,is_audio=False):
    global curves_count,point_count
    r,mid=resource(name,is_audio);c=copy.deepcopy(audio if is_audio else image)
    for k in ['preTransition','postTransition','stabilization','stabilizeAnalysisData','image_denoise','face_cluster','volumeKeyframe','audioDuckingframe']:c.pop(k,None)
    c.update(filename=r['filename'],sourceUuid=r['sourceUuid'],thisUId=uid(),streamId=0,inPoint=0,outPoint=ticks(end-start),tlBegin=ticks(start),tlEnd=ticks(end),picSequence=False)
    c['userData']=[u for u in c.get('userData',[])if u['key']not in[73,74]]
    cid=guid();setdata(c,3,cid);setdata(c,10,mid);setdata(c,50,Path(name).stem);setdata(c,6,struct.pack('<i',main['timelineId']))
    extra['mediaClipsMapInfo'][cid]=dict(mediaId=mid,subClips={})
    c['speed']=dict(offset=0.,offsetEnd=end-start,reverse=False,speedParam=dump(dict(Version=2,ParameterType=0,keyframeSets=[dict(_time=0.,Interpolation=6,_value=1.),dict(_time=duration,Interpolation=6,_value=1.)],_totalTime=duration)).decode())
    c['pipBuf']=dump(dict(Algorithm='Bilinear',BlendMode=0,BlenderName='video/blender/simple-pip',Enable=True,Opacity=100.)).decode();c['pipBufSize']=len(c['pipBuf'])
    # BlenderName is Filmora's own native compositing identifier, not Blender 3D.
    if is_audio:c['effectChainList']=[dict(name='Basic',effectList=[]),dict(name='Effect',effectList=[])];return c
    fx=copy.deepcopy(transform_proto);fx['thisUId']=uid();fx['paramMapList']=[];setdata(fx,3,guid())
    vals=dict(EnableTransform=1,_Anchor_x=.5,_Anchor_y=.5,Position_x=.5,Position_y=.5,Scale_x=100.,Scale_y=100.,Rotation=0.)
    mapping={'Position_x':'x','Position_y':'y','Scale_x':'sx','Scale_y':'sy','Rotation':'rotation'}
    if frames:
        first=frames[0]['layers'][part]
        vals.update({k:first[v]for k,v in mapping.items()})
        for name_,key in mapping.items():
            points=[dict(_time=round(f['time']-start,8),Interpolation=1,_value=f['layers'][part][key])for f in frames]
            fx['paramMapList'].append(dict(key=3,name=name_,keyFrame=dict(parameter=dump(dict(Version=2,ParameterType=0,keyframeSets=points)).decode())))
            curves_count+=1;point_count+=len(points)
    fx['paramList']=[dict(name=k,fxParam=dict(paramType=5 if k=='EnableTransform'else 3,unValue=v))for k,v in vals.items()]
    c['effectChainList']=[dict(name='Basic',effectList=[fx]),dict(name='Effect',effectList=[])]
    return c

tracks[0]['clipList']=[clip('voz_teste.wav',0,duration,is_audio=True)]
tracks[1]['clipList']=[clip('fundo.png',0,duration)]
for segment in plan['segments']:
    a,b=segment['start'],segment['end'];i0=round(a*30);i1=round(b*30)
    sampled=copy.deepcopy(plan['frames'][i0:i1+1])
    for track,part in zip(tracks[2:],['corpo','cabeca','bigode']):track['clipList'].append(clip(f'{segment["pose"]}_{part}.png',a,b,part,sampled))
for tr in tracks[1:]:setdata(tr,12000,struct.pack('<i',len(tr['clipList'])))
data.update(projectName=OUT.stem,currentTimelineId=main['timelineId'],resources=resources,timelineInfos=[main])
root_item.update(id=ROOT,name='Massacote Tube — Prévia 2D',timeline_uuid=timeline_uuid,duration=ticks(duration));items[ROOT]=root_item
files[TL]=dump(data);files[EXTRA]=dump(extra)
files[LIB]=('{"media_structure":{"Folder":{'+','.join('"media_item":'+json.dumps(mid)for mid in items if mid!=ROOT)+'},"media_item":'+json.dumps(ROOT)+'},"media_items":'+dump(items).decode()+'}').encode()
meta.update(project_file_name=OUT.stem,proj_zip_save_path=OUT.name,project_guid=guid(),project_timeline_duration=ticks(duration),project_current_position=0,project_timeline_framerate=[30,1],project_timeline_resolution=[1920,1080],project_timeline_ratio=[16,9],project_sample_rate=48000,project_custom_cover=False,proj_cover_proj_path='')
files['ProjectFolder/project_info.json']=dump(meta)
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_STORED)as z:
    for n,b in files.items():z.writestr(n,b)
assert sha(SOURCE)==source_sha
spec=importlib.util.spec_from_file_location('native_contract',R/'shorts/009-jogos-que-a-internet-tentou-cancelar/production/14-video-completo/validar_registro_nativo.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
report=module.validar(OUT,strict=True);assert report['media_bindings']==11
report.update(project=OUT.name,sha256=sha(OUT),resources=len(resources),clips=11,visual_tracks=4,audio_tracks=1,transform_curves=curves_count,keyframe_points=point_count,duration=duration,source_template=str(SOURCE.relative_to(R)),source_template_sha256=source_sha,source_template_unchanged=True,filmora_native_executed=False,body_head_moustache_editable_layers=True)
(P/'filmora_validacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
