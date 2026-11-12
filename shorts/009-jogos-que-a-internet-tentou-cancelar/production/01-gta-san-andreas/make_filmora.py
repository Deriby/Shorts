"""Native editable WFPs using the user's completed edit as the style reference.

Produces projects, not a proprietary Filmora render. The MP4s are composed by
export_short.py. Source media, timing, transforms, captions and audio stay editable.
"""
from pathlib import Path
import json,zipfile,copy,uuid,base64,hashlib,subprocess,shutil,struct,wave
from PIL import ImageFont

P=Path(__file__).resolve().parent;REPO=next(p for p in P.parents if(p/'AGENTS.md').exists())
SOURCE=REPO/'shorts/008-personagens-que-a-internet-estragou/production/20-edicao-final-usuario/Massacote_EDICAO_FINAL_USUARIO.wfp'
EXPECTED='5a9d4617a2bc34416087e1125230764d5dea7980b5011c186ebe576648748fbc'
ROOT='{204E72A3-B517-44d4-806F-9E9D84D5F904}';TL=f'ProjectFolder/Medias/{ROOT}/timeline.wesproj'
info=json.loads((P/'timeline.json').read_text());ed=json.loads((P/'edicao.json').read_text());TICKS=10000000
TAG='_R2'if info.get('revision',1)>=2 else''
OUT=P/'output'/('Filmora'+TAG);MEDIA=OUT/'midias';MEDIA.mkdir(parents=True,exist_ok=True)
def uid():return str(uuid.uuid4())
def ticks(t):return round(t*TICKS)
def dump(v):return json.dumps(v,ensure_ascii=False,separators=(',',':')).encode()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SOURCE)==EXPECTED
with zipfile.ZipFile(SOURCE)as z:original={n:z.read(n)for n in z.namelist()}
reference=json.loads(original[TL]);source_main=reference['timelineInfos'][0];main_id=source_main['timelineId']
video_proto=next(c for tr in source_main['trackInfos'][10:13]for c in tr['clipList']
                 if c.get('filename','').endswith('.mp4')and c.get('type')==1
                 and any(e.get('display')=='transform'for ch in c['effectChainList']for e in ch['effectList']))
audio_proto=next(c for tr in source_main['trackInfos'][:10]for c in tr['clipList']if c.get('filename','').endswith('.wav'))
text_proto=next(t for t in reference['timelineInfos']if t['timelineId']==67)['trackInfos'][0]['clipList'][0]
glow_proto=next(e for c in source_main['trackInfos'][19]['clipList']for ch in c['effectChainList']for e in ch['effectList']if e.get('display')=='Glow')
transform_proto=next(e for ch in video_proto['effectChainList']for e in ch['effectList']if e.get('display')=='transform')

def userdata(c,resource=None):
    c['thisUId']=uid()
    c['userData']=[u for u in c.get('userData',[])if u['key']not in [73,74]]
    for u in c['userData']:
        data=None
        if u['key']==3:data=('{'+uid().upper()+'}').encode()
        elif u['key']==6:data=struct.pack('<i',main_id)
        elif resource and u['key']==10:data=('{'+resource['sourceUuid'].upper()+'}').encode()
        elif resource and u['key']==50:data=Path(resource['filename']).stem.encode()
        if data is not None:
            if u['key']in[3,10,50]:data+=b'\0'*max(0,u['size']-len(data))
            u.update(data=base64.b64encode(data).decode(),size=len(data))
    for ch in c.get('effectChainList',[]):
        for effect in ch['effectList']:effect['thisUId']=uid()

def source_speed(c,a,b,total):
    params={'Version':2,'ParameterType':0,'keyframeSets':[
        {'_time':0.,'Interpolation':6,'_value':1.},
        {'_time':float(total),'Interpolation':6,'_value':1.}], '_totalTime':float(total)}
    c['speed']={'offset':float(a),'offsetEnd':float(b),'reverse':False,'speedParam':json.dumps(params,separators=(',',':'))}

def transform(c,values,keys=None):
    effect=copy.deepcopy(transform_proto);effect['thisUId']=uid()
    effect['paramList']=[{'name':'EnableTransform','fxParam':{'paramType':5,'unValue':1}}]
    effect['paramMapList']=[]
    for name,value in values.items():
        effect['paramList'].append({'name':name,'fxParam':{'paramType':3,'unValue':value}})
        if keys and name in keys:
            p={'Version':2,'ParameterType':0,'keyframeSets':[{'_time':float(t),'Interpolation':1,'_value':v}for t,v in keys[name]]}
            effect['paramMapList'].append({'key':3,'name':name,'keyFrame':{'parameter':json.dumps(p,separators=(',',':'))}})
    c['effectChainList']=[{'name':'Basic','effectList':[effect]},{'name':'Effect','effectList':[]}]

def resource(path,prototype):
    r=copy.deepcopy(prototype);r.update(sourceUuid=uid(),filename='file:./midias/'+path.name,createDate=-1,modifyDate=0)
    d=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
    videos=[s for s in d['streams']if s['codec_type']=='video'];audios=[s for s in d['streams']if s['codec_type']=='audio']
    duration=float(d['format']['duration']);r.update(mediaLength=ticks(duration),videoStreamCount=len(videos),audioStreamCount=len(audios),bitRate=int(d['format'].get('bit_rate',0)))
    if videos:
        s=videos[0];v=copy.deepcopy(r['vidStreamInfo'][0]);num,den=map(int,s['r_frame_rate'].split('/'))
        v.update(vidStreamId=s['index'],width=s['width'],height=s['height'],xRatio=s['width']*1000,yRatio=s['height']*1000,
                 frameRate={'num':num,'den':den},maxFrameRate={'num':num,'den':den},totalFrames=int(s['nb_frames']),
                 streamLength=ticks(duration),bitRate=int(s.get('bit_rate',0)))
        v.pop('duration',None);r['vidStreamInfo']=[v]
    else:r.pop('vidStreamInfo',None)
    if audios:
        a=audios[0];channels=a['channels'];sr=int(a['sample_rate']);v=copy.deepcopy(r.get('audStreamInfo',[{}])[0])
        v.update(audStreamId=a['index'],sampleRate=sr,channels=channels,duration=duration,streamLength=ticks(duration),
                 bitDepth=16,bitRate=sr*channels*16,bytesPerSecond=sr*channels*2,description='Uncompressed PCM',fourCC=541278529)
        r['audStreamInfo']=[v];r['streamType']=3
    else:r.pop('audStreamInfo',None)
    for name in ['fileSize','fileLength']:
        if name in r:r[name]=path.stat().st_size
    return r,duration

video_resource_proto=next(r for r in reference['resources']if r.get('filename')==video_proto['filename'])
audio_resource_proto=next((r for r in reference['resources']if r.get('filename','').lower().endswith('.wav')and r.get('audStreamInfo')),None)
if audio_resource_proto is None:
    # The final user edit stores its PCM SFX as installed assets, without a
    # typed library resource. Reuse only a valid PCM descriptor from the earlier
    # user WFP; timing, style, clips and titles still derive from the final edit.
    pcm_reference=REPO/'shorts/008-personagens-que-a-internet-estragou/production/14-montagem-longo/assets/Referencia_Filmora_original.wfp'
    with zipfile.ZipFile(pcm_reference)as z:
        typed=json.loads(z.read(TL))
        audio_resource_proto=next(r for r in typed['resources']if r.get('filename','').lower().endswith('.wav')and r.get('audStreamInfo'))
for src in [P/'assets/voz/voz_timeline.wav',P/'assets/audio/trilha_baixa.wav',*[P/'assets/audio'/e['file']for e in ed['sfx']]]:
    dest=MEDIA/src.name
    if not dest.exists()or sha(src)!=sha(dest):shutil.copyfile(src,dest)
fonts=OUT/'fontes';fonts.mkdir(exist_ok=True)
for name in ['Baloo2.ttf','OFL.txt']:shutil.copyfile(P/'assets/fontes'/name,fonts/name)

def title_clip(title,wide):
    width,height=(1920,1080)if wide else(1080,1920)
    c=copy.deepcopy(text_proto);script=json.loads(c['scriptBuf']);oldtext=script['Text']
    oldsize=script['TextData'][0]['Basic']['FontSize'];oldwidth=script['ScaleX']*1920
    measure=ImageFont.truetype(str(P/'assets/fontes/Baloo2.ttf'),100)
    try:measure.set_variation_by_axes([700])
    except Exception:pass
    desired=.36 if len(title['text'])<=4 else .82
    size=oldsize*(desired*width/oldwidth)*(measure.getlength(oldtext)/max(1,measure.getlength(title['text'])))
    scale_y=script['ScaleY']*(size/oldsize)*(1080/height)
    script.update(Aspect='16:9'if wide else'9:16',ViewSize=f'{width}:{height}',Text=title['text'],
                  PosX=.5,PosY=title['y'],ScaleX=desired,ScaleY=scale_y,TextScale=size/100)
    script['Layout']['TextAlign']='center';data=copy.deepcopy(script['TextData'][0]);data['CharData']=title['text']
    data['Basic'].update(FontName='Baloo 2 Bold',FontSize=size,FontHSize=size,FontVSize=size)
    script['TextData']=[data]
    c['scriptBuf']=json.dumps(script,ensure_ascii=False,separators=(',',':'));c['scriptBufSize']=len(c['scriptBuf'].encode())
    duration=title['end']-title['start'];c.update(tlBegin=ticks(title['start']),tlEnd=ticks(title['end']),inPoint=0,outPoint=ticks(duration))
    userdata(c)
    transform(c,{'Scale_x':desired*100,'Scale_y':scale_y*100,'Position_x':.5,'Position_y':title['y'],'_Anchor_x':.5,'_Anchor_y':.5})
    # Native paid Glow is restricted to the title, never the character/image.
    if title['text']in['GTA SAN ANDREAS','HOT COFFEE']:
        glow=copy.deepcopy(glow_proto);glow['thisUId']=uid();c['effectChainList'][1]['effectList']=[glow]
    return c

manifest=[]
for wide in [False,True]:
    suffix='16x9'if wide else'9x16';project_name=f'GTA_San_Andreas{TAG}_{suffix}'
    main=copy.deepcopy(source_main);main.update(resolutionWidth=1920 if wide else 1080,resolutionHeight=1080 if wide else 1920,
        aspectRatioX=16 if wide else 9,aspectRatioY=9 if wide else 16,frameRate={'num':60,'den':1})
    for track in main['trackInfos']:track['clipList']=[]
    resources=[]
    take,total=resource(MEDIA/f'GTA_base{TAG}_{suffix}.mp4',video_resource_proto);resources.append(take)
    for sh,edit in zip(info['shots'],ed['edits']):
        c=copy.deepcopy(video_proto)
        for key in ['postTransition','preTransition','stabilization','stabilizeAnalysisData','face_cluster','image_denoise']:c.pop(key,None)
        a,b=edit['start'],edit['end'];c.update(filename=take['filename'],sourceUuid=take['sourceUuid'],streamId=0,
            tlBegin=ticks(a),tlEnd=ticks(b),inPoint=ticks(a),outPoint=ticks(b))
        userdata(c,take);source_speed(c,a,b,total)
        z=edit['zoom_end']if wide else edit['portrait_zoom_end']
        transform(c,{'Scale_x':100.,'Scale_y':100.,'Position_x':.5,'Position_y':.5,'_Anchor_x':.5,'_Anchor_y':.5},
                  {'Scale_x':[(a,100.),(b,z*100)],'Scale_y':[(a,100.),(b,z*100)]})
        main['trackInfos'][11]['clipList'].append(c)
    audio_resources={}
    for name,start,track in [('voz_timeline.wav',0,8),('trilha_baixa.wav',0,6),*[(e['file'],e['start'],7)for e in ed['sfx']]]:
        if name not in audio_resources:
            r,duration=resource(MEDIA/name,audio_resource_proto);audio_resources[name]=(r,duration);resources.append(r)
        r,duration=audio_resources[name];c=copy.deepcopy(audio_proto)
        c.update(filename=r['filename'],sourceUuid=r['sourceUuid'],streamId=0,tlBegin=ticks(start),tlEnd=ticks(start+duration),inPoint=0,outPoint=ticks(duration))
        for key in ['volumeKeyframe','audioDuckingframe']:c.pop(key,None)
        userdata(c,r);source_speed(c,0,duration,duration)
        for ch in c['effectChainList']:ch['effectList']=[]
        main['trackInfos'][track]['clipList'].append(c)
    main['trackInfos'][13]['clipList']=[title_clip(t,wide)for t in ed['titles']]
    data=copy.deepcopy(reference);data.update(projectName=project_name,resources=resources,timelineInfos=[main],currentTimelineId=main_id)
    files={n:b for n,b in original.items()if not n.startswith('ProjectFolder/Medias/')}
    files[TL]=dump(data)
    meta=json.loads(original['ProjectFolder/project_info.json'])
    meta.update(project_file_name=project_name,project_timeline_duration=ticks(info['duration']),project_current_position=0,
                proj_zip_save_path=project_name+'.wfp',proj_cover_proj_path='',project_custom_cover=False)
    files['ProjectFolder/project_info.json']=dump(meta)
    items={};ids=[]
    for r in resources:
        mid='{'+r['sourceUuid'].upper()+'}';ids.append(mid)
        items[mid]={'name':Path(r['filename']).name,'download_url':r['filename'].replace('file:./','./'),'id':mid,
                    'media_type':8 if r.get('videoStreamCount')else 4,'media_length':r['mediaLength'],'stream_idx':0,
                    'mark_info_list':[{'mark_in':-1,'mark_out':-1}]}
        src={'basicInfo':{k:r[k]for k in ['streamType','fourCC','mediaLength','videoStreamCount','audioStreamCount','bitRate']if k in r},
             'vidStreamInfos':r.get('vidStreamInfo',[]),'audStreamInfos':r.get('audStreamInfo',[])}
        files[f'ProjectFolder/Medias/{mid}/media.json']=dump({'version':'1.1.5','file_name':items[mid]['download_url'],'sourceInfo':src})
    structure='{"media_structure":{"Folder":{'+','.join('"media_item":'+json.dumps(i)for i in ids)+'},"media_item":'+json.dumps(ROOT)+'},"media_items":'+json.dumps(items)+'}'
    files['ProjectFolder/Medias/medias_info.json']=structure.encode()
    project=OUT/(project_name+'.wfp')
    with zipfile.ZipFile(project,'w',zipfile.ZIP_DEFLATED)as z:
        for name,b in files.items():z.writestr(name,b)
    manifest.append(dict(project=project.name,format=suffix,video_clips=len(info['shots']),native_titles=len(ed['titles']),
                         audio_clips=2+len(ed['sfx']),duration=info['duration'],resources=len(resources),sha256=sha(project)))
assert sha(SOURCE)==EXPECTED
(P/'filmora.json').write_text(json.dumps(dict(reference=str(SOURCE.relative_to(REPO)),reference_sha256=EXPECTED,
    source_unchanged=True,projects=manifest,all_media_bundled=True,original_voice_full=True,
    native_titles=True,paid_glow_on_titles_only=True,whole_frame_shake=False,
    filmora_executed=False,native_open_test='Not available in the Linux environment; structural checks are separate.'),ensure_ascii=False,indent=2)+'\n')
instructions='''GTA SAN ANDREAS — JOGOS QUE A INTERNET TENTOU CANCELAR

Extraia o ZIP inteiro antes de abrir. Há projetos 9:16 e 16:9, com mídias em
midias/. Se o Filmora pedir uma fonte de vídeo/áudio, localize-a nessa pasta.
Os mesmos arquivos atendem aos dois projetos. A fonte Baloo 2 e a licença estão
em fontes/; ela já aparece no seu estilo anterior.

Cortes, zooms com keyframes, títulos nativos, voz, trilha e efeitos sonoros
ficam separados e editáveis. O vídeo-base está sem áudio; a voz inteira está
na faixa própria. A animação e o conteúdo dentro do CRT foram renderizados
no Blender; para alterar essa atuação use o projeto Blender da produção.

O estilo usa como fonte seu projeto de edição concluído: tipografia, contorno,
Glow nos títulos e reenquadramentos pela fala. Não há tremido global.
Os MP4s entregues são composições exportadas neste ambiente; o renderizador
proprietário do Filmora não foi executado no Linux. A abertura e a aparência
nativa dos plugins devem ser conferidas na sua instalação do Filmora.
'''
(OUT/'LEIA_PRIMEIRO.txt').write_text(instructions)
bundle=P/f'output/GTA_San_Andreas_Projetos_Filmora{TAG}.zip'
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED,allowZip64=True)as z:
    for p in OUT.rglob('*'):
        if p.is_file():z.write(p,str(p.relative_to(OUT)),compress_type=zipfile.ZIP_STORED if p.suffix in['.mp4','.ttf']else zipfile.ZIP_DEFLATED)
assert zipfile.ZipFile(bundle).testzip()is None
print('FILMORA_PACKAGE_READY',str(bundle),bundle.stat().st_size,flush=True)
