"""Cria projeto vertical nativo a partir das mesmas camadas e curvas do MP4."""
from pathlib import Path
import json,zipfile,copy,uuid,struct,base64,hashlib,subprocess,importlib.util
P=Path(__file__).resolve().parents[1];R=next(p for p in P.parents if(p/'AGENTS.md').exists());F=P/'output/Filmora';M=F/'midias'
SOURCE=R/'shorts/009-jogos-que-a-internet-tentou-cancelar/production/14-video-completo/revisao_memes_v4_tempo/output/Filmora/Massacote_MEMES_Tempo_Corrigido.wfp'
ROOT='{204E72A3-B517-44d4-806F-9E9D84D5F904}';TL=f'ProjectFolder/Medias/{ROOT}/timeline.wesproj';EXTRA=f'ProjectFolder/Medias/{ROOT}/extra.json';LIB='ProjectFolder/Medias/medias_info.json';OUT=F/'Massacote_Tube_Sonic_V2_9x16.wfp';T=10000000
plan=json.loads((P/'timeline.json').read_text());D=plan['duration'];W,H=plan['width'],plan['height']
def uid():return str(uuid.uuid4())
def guid():return '{'+uid().upper()+'}'
def dump(x):return json.dumps(x,ensure_ascii=False,separators=(',',':')).encode()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ticks(x):return round(x*T)
source_sha=sha(SOURCE)
with zipfile.ZipFile(SOURCE)as z:raw={n:z.read(n)for n in z.namelist()}
data=json.loads(raw[TL]);original_main=next(t for t in data['timelineInfos']if t['timelineId']==data['currentTimelineId']);lib=json.loads(raw[LIB]);extra=json.loads(raw[EXTRA]);meta=json.loads(raw['ProjectFolder/project_info.json'])
clips=[c for tr in original_main['trackInfos']for c in tr['clipList']]
protos={ext:next(c for c in clips if c.get('filename','').endswith(ext))for ext in ['.png','.mp4','.wav']}
resproto={ext:next(r for r in data['resources']if r['filename']==protos[ext]['filename'])for ext in protos}
itemproto={typ:copy.deepcopy(next(x for x in lib['media_items'].values()if x.get('media_type')==typ))for typ in [2,4,16]}
fxproto=next(e for ch in protos['.png']['effectChainList']for e in ch['effectList']if e.get('display')=='transform')
rootitem=copy.deepcopy(lib['media_items'][ROOT]);files={n:b for n,b in raw.items()if not n.startswith('ProjectFolder/Medias/')}
for k in ['usedTemplateResInfo','mediaClipsMapInfo','pendingMarkersInfo','highlightInfo']:extra[k]={}
extra['allMarkersInfo']={'beatDetectInfo':{}};extra['fontNameInfo']=[];extra['usedBizFont']=[];extra['TextSentence']={'TextSentence':[]}
def setdata(obj,key,value):
    obj.setdefault('userData',[]);u=next((u for u in obj['userData']if u['key']==key),None)
    if u is None:u={'key':key,'size':0,'data':''};obj['userData'].append(u)
    b=value if isinstance(value,bytes)else value.encode();b+=b'\0'*max(0,u['size']-len(b));u.update(size=len(b),data=base64.b64encode(b).decode())
main=copy.deepcopy(original_main);main.update(frameRate={'num':30,'den':1},resolutionWidth=W,resolutionHeight=H,aspectRatioX=9,aspectRatioY=16,sampleRate=48000)
timeline_uuid=guid();setdata(main,11000,timeline_uuid);setdata(main,50,'Massacote Tube — Sonic')
audio_tags=['voz','musica','sfx','sfx2','luta'];tracks=[];trackmap={}
for tag in audio_tags+list(range(9)):
    tr=dict(trackType=2 if isinstance(tag,str)else 1,trackTag=len(tracks)+1,uuid=uid(),clipList=[])
    if isinstance(tag,int):tr['userData']=[dict(key=21,size=4,data='AQAAAA=='),dict(key=12001,size=1,data='AA==')]
    setdata(tr,50,str(tag));tracks.append(tr);trackmap[tag]=tr
main['trackInfos']=tracks;resources=[];items={};entries={};curves=points=0
def resource(name):
    if name in entries:return entries[name]
    path=M/name;ext=path.suffix;isaudio=ext=='.wav';isimg=ext=='.png';typ=4 if isaudio else 16 if isimg else 2
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]));s=probe['streams'][0]
    dur=float(probe['format'].get('duration',0))if not isimg else 0
    r=copy.deepcopy(resproto[ext]);r.update(sourceUuid=uid(),filename='file:./midias/'+name,createDate=-1,modifyDate=0,videoStreamCount=0 if isaudio else 1,audioStreamCount=1 if isaudio else 0)
    if isaudio:
        sr=int(s['sample_rate']);ch=int(s['channels']);bits=int(s['bits_per_sample'])
        r.update(mediaLength=ticks(dur),streamType=3,bitRate=sr*ch*bits);r.pop('vidStreamInfo',None)
        r['audStreamInfo'][0].update(audStreamId=0,sampleRate=sr,channels=ch,duration=dur,streamLength=ticks(dur),bitDepth=bits,bitRate=sr*ch*bits,bytesPerSecond=sr*ch*bits//8,description='Uncompressed PCM',fourCC=541278529)
    else:
        r.pop('audStreamInfo',None);r.update(mediaLength=0 if isimg else ticks(dur),streamType=5 if isimg else 1,bitRate=0 if isimg else int(probe['format']['bit_rate']))
        r['vidStreamInfo'][0].update(vidStreamId=0,width=W,height=H,xRatio=W if isimg else W*1000,yRatio=H if isimg else H*1000,alphaChannel=1 if isimg and name!='Fundo_Tube.png'else 0,bitsDepth=32 if isimg and name!='Fundo_Tube.png'else 24,totalFrames=0 if isimg else int(s['nb_frames']),streamLength=0 if isimg else ticks(dur),frameRate={'num':30,'den':1},maxFrameRate={'num':30,'den':1},lastframeRate={'num':30,'den':1},premultiAlphaTypePhoto=-1)
    mid=guid();item=copy.deepcopy(itemproto[typ]);item.update(id=mid,name=path.stem,download_url='./midias/'+name,media_type=typ,media_length=50000000 if isimg else ticks(dur),stream_idx=-1 if isimg else 0,src_md5=hashlib.md5(path.read_bytes()).hexdigest(),mark_info_list=[dict(mark_in=-1,mark_out=-1)],scence_info=[])
    items[mid]=item;resources.append(r)
    basic={k:r[k]for k in ['streamType','fourCC','mediaLength','programCount','videoStreamCount','audioStreamCount','subPicStreamCount','bitRate','createDate']if k in r};basic.setdefault('programCount',0);basic.setdefault('subPicStreamCount',0)
    files[f'ProjectFolder/Medias/{mid}/media.json']=dump(dict(version='1.1.5',file_name='./midias/'+name,sourceInfo=dict(basicInfo=basic,vidStreamInfos=r.get('vidStreamInfo',[]),audStreamInfos=r.get('audStreamInfo',[]),recordInfos={})))
    entries[name]=(r,mid,dur);return r,mid,dur

for ev in plan['events']:
    name=ev['file'];r,mid,total=resource(name);ext=Path(name).suffix;isaudio=ext=='.wav';c=copy.deepcopy(protos[ext]);start,end=ev['start'],ev['end'];duration=end-start
    for k in ['preTransition','postTransition','stabilization','stabilizeAnalysisData','image_denoise','face_cluster','volumeKeyframe','audioDuckingframe']:c.pop(k,None)
    c.update(filename=r['filename'],sourceUuid=r['sourceUuid'],thisUId=uid(),streamId=0,inPoint=0,outPoint=ticks(duration),tlBegin=ticks(start),tlEnd=ticks(end),picSequence=False)
    c['userData']=[u for u in c.get('userData',[])if u['key']not in[73,74]];cid=guid();setdata(c,3,cid);setdata(c,10,mid);setdata(c,50,Path(name).stem);setdata(c,6,struct.pack('<i',main['timelineId']));extra['mediaClipsMapInfo'][cid]=dict(mediaId=mid,subClips={})
    speedtotal=total if total else max(D,duration)
    c['speed']=dict(offset=0.,offsetEnd=duration,reverse=False,speedParam=dump(dict(Version=2,ParameterType=0,keyframeSets=[dict(_time=0.,Interpolation=6,_value=1.),dict(_time=speedtotal,Interpolation=6,_value=1.)],_totalTime=speedtotal)).decode())
    c['pipBuf']=dump(dict(Algorithm='Bilinear',BlendMode=0,BlenderName='video/blender/simple-pip',Enable=True,Opacity=100.)).decode();c['pipBufSize']=len(c['pipBuf'])
    if isaudio:c['effectChainList']=[dict(name='Basic',effectList=[]),dict(name='Effect',effectList=[])]
    else:
        fx=copy.deepcopy(fxproto);fx.update(thisUId=uid(),paramMapList=[]);setdata(fx,3,guid())
        keys=ev['keys'];first=keys[0];values=dict(EnableTransform=1,_Anchor_x=.5,_Anchor_y=.5,Position_x=first[1],Position_y=first[2],Scale_x=first[3]*100,Scale_y=first[4]*100,Rotation=first[5])
        fx['paramList']=[dict(name=k,fxParam=dict(paramType=5 if k=='EnableTransform'else 3,unValue=v))for k,v in values.items()]
        for index,param in enumerate(['Position_x','Position_y','Scale_x','Scale_y','Rotation'],1):
            scale=100 if param.startswith('Scale')else 1
            ks=[dict(_time=round(k[0],8),Interpolation=1,_value=k[index]*scale)for k in keys]
            assert all(-1e-6<=k['_time']<=duration+1e-6 for k in ks),(name,start,end)
            fx['paramMapList'].append(dict(key=3,name=param,keyFrame=dict(parameter=dump(dict(Version=2,ParameterType=0,keyframeSets=ks)).decode())));curves+=1;points+=len(ks)
        c['effectChainList']=[dict(name='Basic',effectList=[fx]),dict(name='Effect',effectList=[])]
    trackmap[ev['track']]['clipList'].append(c)
for tr in tracks:tr['clipList'].sort(key=lambda c:c['tlBegin']);setdata(tr,12000,struct.pack('<i',len(tr['clipList'])))
data.update(projectName=OUT.stem,currentTimelineId=main['timelineId'],resources=resources,timelineInfos=[main]);rootitem.update(id=ROOT,name='Massacote Tube — Sonic',timeline_uuid=timeline_uuid,duration=ticks(D));items[ROOT]=rootitem
files[TL]=dump(data);files[EXTRA]=dump(extra)
files[LIB]=('{"media_structure":{"Folder":{'+','.join('"media_item":'+json.dumps(mid)for mid in items if mid!=ROOT)+'},"media_item":'+json.dumps(ROOT)+'},"media_items":'+dump(items).decode()+'}').encode()
meta.update(project_file_name=OUT.stem,proj_zip_save_path=OUT.name,project_guid=guid(),project_timeline_duration=ticks(D),project_current_position=0,project_timeline_framerate=[30,1],project_timeline_resolution=[W,H],project_timeline_ratio=[9,16],project_sample_rate=48000,project_custom_cover=False,proj_cover_proj_path='');files['ProjectFolder/project_info.json']=dump(meta)
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_STORED)as z:
    for n,b in files.items():z.writestr(n,b)
assert sha(SOURCE)==source_sha
spec=importlib.util.spec_from_file_location('contract',R/'shorts/009-jogos-que-a-internet-tentou-cancelar/production/14-video-completo/validar_registro_nativo.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
report=module.validar(OUT,strict=True);report.update(project=OUT.name,sha256=sha(OUT),resources=len(resources),clips=len(plan['events']),visual_tracks=9,audio_tracks=len(audio_tags),transform_curves=curves,keyframe_points=points,duration=D,resolution=[W,H],filmora_native_executed=False,avatar_layers_editable=True,voice_sha256=sha(M/'Voz_Dery_Original.wav'),source_template_unchanged=sha(SOURCE)==source_sha)
(P/'validacao_filmora.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
