"""Split the completed user edit into 12 editable portrait Filmora projects.

No Filmora renderer or Blender render is invoked. The user's native edit is
retained; the matching original portrait movies replace landscape footage.
"""
from pathlib import Path
from fractions import Fraction
import json,zipfile,copy,hashlib,subprocess,uuid,base64,os,shutil,math

P=Path(__file__).resolve().parent;PROD=P.parent;OUT=P/'output'
SOURCE=PROD/'20-edicao-final-usuario/Massacote_EDICAO_FINAL_USUARIO.wfp'
ROOT='{204E72A3-B517-44d4-806F-9E9D84D5F904}'
TL=f'ProjectFolder/Medias/{ROOT}/timeline.wesproj';MI='ProjectFolder/Medias/medias_info.json'
META='ProjectFolder/project_info.json';TICKS=10_000_000
SOURCE_SHA='5a9d4617a2bc34416087e1125230764d5dea7980b5011c186ebe576648748fbc'
CHARACTERS=[
 ('01-lady-dimitrescu','Lady_Dimitrescu','Lady',2161,4463),
 ('02-tifa','Tifa','Tifa',4711,6396),
 ('03-chun-li','Chun_Li','ChunLi',6644,8978),
 ('04-ankha','Ankha','Ankha',9226,11837),
 ('05-vaporeon','Vaporeon','Vaporeon',12085,14904),
 ('06-2b','2B','2B',15152,17551),
 ('07-tracer','Tracer','07-tracer_video',17797,19302),
 ('08-dva','DVa','08-dva_video',19550,22060),
 ('09-mercy','Mercy','09-mercy_video',22308,24048),
 ('10-lara-croft','Lara_Croft','10-lara-croft_video',24296,26536),
 ('11-peach','Peach','11-peach_video',26784,29019),
 ('12-sonic','Sonic','12-sonic_video',29267,31364),
]

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb')as f:
        while b:=f.read(1024*1024):h.update(b)
    return h.hexdigest()
def dump(value):return json.dumps(value,ensure_ascii=False,separators=(',',':')).encode()
def decode(u):
    try:return base64.b64decode(u['data']).decode().rstrip('\0')
    except (ValueError,UnicodeDecodeError,KeyError):return None
def setdata(u,value):
    b=value.encode();b+=b'\0'*max(0,u.get('size',0)-len(b));u.update(data=base64.b64encode(b).decode(),size=len(b))
def replace(node,mapping):
    if isinstance(node,list):return [replace(x,mapping)for x in node]
    if isinstance(node,dict):
        out={k:replace(v,mapping)for k,v in node.items()}
        # Disabled AI/cached origin-path metadata is also stored as base64 JSON.
        if 'data'in node and 'key'in node and 'size'in node:
            value=decode(node)
            if value and any(k in value for k in mapping):
                try:new=json.dumps(replace(json.loads(value),mapping),ensure_ascii=False,separators=(',',':'))
                except ValueError:
                    new=mapping.get(value,value)
                if new!=value:setdata(out,new)
        return out
    if isinstance(node,str):
        if node in mapping:return mapping[node]
        if node.lstrip().startswith(('{','[')) and any(k in node for k in mapping):
            try:return json.dumps(replace(json.loads(node),mapping),ensure_ascii=False,separators=(',',':'))
            except ValueError:pass
    return node

def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
def audiohash(path):
    return subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-'],text=True).strip()
def patch_resource(r,info):
    video=next(s for s in info['streams']if s['codec_type']=='video');audio=[s for s in info['streams']if s['codec_type']=='audio']
    rate=Fraction(video['r_frame_rate']);duration=int(video['nb_frames'])/float(rate)
    r.update(mediaLength=round(duration*TICKS),bitRate=int(info['format'].get('bit_rate',0)),audioStreamCount=len(audio),videoStreamCount=1)
    vs=r['vidStreamInfo'][0]
    vs.update(width=video['width'],height=video['height'],xRatio=9000,yRatio=16000,
              frameRate={'num':rate.numerator,'den':rate.denominator},maxFrameRate={'num':rate.numerator,'den':rate.denominator},
              totalFrames=int(video['nb_frames']),streamLength=round(duration*TICKS),bitRate=int(video.get('bit_rate',0)),vidStreamId=video['index'])
    vs.pop('duration',None)
    if audio:
        a=audio[0];au=copy.deepcopy(r.get('audStreamInfo',[{}])[0])
        au.update(audStreamId=a['index'],sampleRate=int(a['sample_rate']),channels=a['channels'],duration=float(a['duration']),streamLength=round(float(a['duration'])*TICKS),bitRate=int(a.get('bit_rate',0)))
        au.setdefault('bitDepth',16);au.setdefault('fourCC',541278529);au.setdefault('layout',0)
        r['audStreamInfo']=[au]
    else:r.pop('audStreamInfo',None)
    return duration

def refs(node):
    found=set()
    if isinstance(node,dict):
        if isinstance(node.get('filename'),str):found.add(node['filename'])
        for x in node.values():found.update(refs(x))
    elif isinstance(node,list):
        for x in node:found.update(refs(x))
    return found
def timeline_dependencies(main,alltimelines):
    known={t['timelineId']:t for t in alltimelines};used={main['timelineId']};pending=[main]
    def find(node):
        if isinstance(node,dict):
            for k,v in node.items():
                if k=='timelineId' and isinstance(v,int) and v in known:yield v
                elif isinstance(v,(list,dict)):yield from find(v)
        elif isinstance(node,list):
            for v in node:yield from find(v)
    while pending:
        for i in find(pending.pop().get('trackInfos',[])):
            if i not in used:used.add(i);pending.append(known[i])
    return used

def trim_clip(c,begin,end,record):
    old_a,old_b=c['tlBegin'],c['tlEnd'];a=max(begin,old_a);b=min(end,old_b)
    if b-a<2:return None
    c=copy.deepcopy(c);left=a-old_a;right=old_b-b
    c.update(tlBegin=a-begin,tlEnd=b-begin)
    if left or right:
        if 'inPoint'in c:c['inPoint']+=left
        if 'outPoint'in c:c['outPoint']-=right
        speed=c.get('speed')
        if speed:
            values=json.loads(speed['speedParam']).get('keyframeSets',[])
            assert all(abs(k['_value']-1)<1e-6 for k in values),'Non-1x trimmed clip needs explicit time mapping'
            speed['offset']=c.get('inPoint',0)/TICKS;speed['offsetEnd']=c.get('outPoint',0)/TICKS
    for k in ('preTransition','postTransition'):
        if k not in c:continue
        transition=c[k]
        if 'tlBegin'in transition and 'tlEnd'in transition:
            if transition['tlBegin']<begin-2 or transition['tlEnd']>end+2:
                c.pop(k);record['boundary_transitions_removed']+=1
            else:transition['tlBegin']-=begin;transition['tlEnd']-=begin
    return c

def curves(effect):
    found={}
    for p in effect.get('paramMapList',[]):
        if 'keyFrame'in p:
            try:found[p['name']]=(p,json.loads(p['keyFrame']['parameter']))
            except (KeyError,ValueError):pass
    return found
def value_at(data,time,default):
    ks=sorted(data.get('keyframeSets',[]),key=lambda k:k['_time'])if data else []
    if not ks:return default
    if time<=ks[0]['_time']:return ks[0]['_value']
    for a,b in zip(ks,ks[1:]):
        if a['_time']<=time<=b['_time']:
            q=(time-a['_time'])/max(1e-9,b['_time']-a['_time']);return a['_value']+(b['_value']-a['_value'])*q
    return ks[-1]['_value']

def adapt_transform(clip,shots):
    if clip.get('type')!=1 or not clip.get('filename','').endswith('9x16.mp4'):return None
    midpoint=(clip.get('inPoint',0)+clip.get('outPoint',0))/2/TICKS
    sh=next((s for s in shots if (s['start']-1)/24<=midpoint<s['end']/24),shots[-1])
    kind=sh['kind'];factors={'monitor':(.08,.12,.18),'actor':(.22,.20,.32),'interview':(.18,.22,.30)}
    ks,kx,ky=factors.get(kind,(.28,.25,.40));changed=0
    for chain in clip.get('effectChainList',[]):
        for e in chain.get('effectList',[]):
            if e.get('display')!='transform':continue
            original=copy.deepcopy(e);cs=curves(original)
            defaults={p['name']:p['fxParam'].get('unValue')for p in original.get('paramList',[])}
            def convert(name,val,time):
                if name.startswith('Scale_'):return max(100.,100+ks*(val-100))
                if name in ('Position_x','Position_y'):
                    axis='x'if name.endswith('_x')else'y';factor=kx if axis=='x'else ky
                    sc=value_at(cs.get('Scale_'+axis,(None,{}))[1],time,defaults.get('Scale_'+axis,100.))
                    z=max(100.,100+ks*(sc-100))/100
                    return max(1-z/2,min(z/2,.5+factor*(val-.5)))
                return val
            for p in e.get('paramList',[]):
                if p['name']in ('Scale_x','Scale_y','Position_x','Position_y'):
                    p['fxParam']['unValue']=convert(p['name'],p['fxParam']['unValue'],clip.get('inPoint',0)/TICKS)
            for p,data in curves(e).values():
                if p['name']not in ('Scale_x','Scale_y','Position_x','Position_y'):continue
                factor=ks if p['name'].startswith('Scale')else(kx if p['name'].endswith('_x')else ky)
                for key in data.get('keyframeSets',[]):
                    oldval=key['_value'];val=convert(p['name'],oldval,key['_time']);key['_value']=val
                    naive=(100+factor*(oldval-100))if p['name'].startswith('Scale')else(.5+factor*(oldval-.5))
                    for dk in ('_leftDerivative','_rightDerivative'):
                        if dk in key:key[dk]*=factor if abs(val-naive)<1e-8 else 0
                data.pop('MD5',None)
                p['keyFrame']['parameter']=json.dumps(data,separators=(',',':'))
            changed+=1
    return {'source_midpoint':midpoint,'shot_id':sh['id'],'kind':kind,'scale_factor':ks,'horizontal_factor':kx,'vertical_factor':ky,'transform_count':changed}

def media_structure(items):
    return ('{"media_structure":{"Folder":{'+','.join('"media_item":'+json.dumps(k)for k in items if k!=ROOT)+'},"media_item":'+json.dumps(ROOT)+'},"media_items":'+json.dumps(items,ensure_ascii=False,separators=(',',':'))+'}').encode()
def stage_file(source,target):
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():
        assert sha(target)==sha(source);return
    try:os.link(source,target)
    except OSError:shutil.copyfile(source,target)

def make():
    assert sha(SOURCE)==SOURCE_SHA
    OUT.mkdir(exist_ok=True)
    with zipfile.ZipFile(SOURCE)as z:raw={n:z.read(n)for n in z.namelist()}
    master=json.loads(raw[TL]);root=next(t for t in master['timelineInfos']if t['timelineId']==master['currentTimelineId'])
    oldmeta=json.loads(raw[META]);inventory=json.loads((PROD/'20-edicao-final-usuario/inventario_fontes.json').read_text())['references']
    inv={r['reference']:r for r in inventory};allreports=[]
    for folder,label,pattern,start_frame,end_frame in CHARACTERS:
        work=OUT/f'{folder[:2]}_{label}';work.mkdir(exist_ok=True)
        report={'character':folder,'name':label,'source_frames_60fps':[start_frame,end_frame],'boundary_transitions_removed':0,'adapted_video_clips':[],'bundled_media':[],'original_external_sources':[]}
        begin=round(start_frame/60*TICKS);end=round(end_frame/60*TICKS);duration=end-begin
        project=copy.deepcopy(master);main=next(t for t in project['timelineInfos']if t['timelineId']==project['currentTimelineId'])
        for tr in main['trackInfos']:
            tr['clipList']=[out for c in tr['clipList']if(out:=trim_clip(c,begin,end,report))is not None]
        main.update(resolutionWidth=1080,resolutionHeight=1920,aspectRatioX=9,aspectRatioY=16)
        for u in main.get('userData',[]):
            if u['key']==50:setdata(u,label+' | Short 9x16')
        # Keep every original child/cache/library entry: no native template or
        # compound identifier is transplanted from another project version.
        dependency_ids=timeline_dependencies(main,project['timelineInfos'])
        active_timelines=[t for t in project['timelineInfos']if t['timelineId']in dependency_ids]
        used=refs([t['trackInfos']for t in active_timelines])
        portrait=next((PROD/folder/'output').glob('*9x16.mp4'));wide=next((PROD/folder/'output').glob('*16x9.mp4'))
        info=probe(portrait);assert audiohash(portrait)==audiohash(wide)
        report['portrait_wide_audio_packets_identical']=True
        media_name=portrait.name;relative='./midias/'+media_name
        mapping={};mappedresources=[]
        for r in project['resources']:
            name=r['filename'].rsplit('/',1)[-1]
            matches=pattern in name or(folder=='10-lara-croft'and'inicio_43_Lara_'in name)
            if matches and name.lower().endswith('.mp4'):
                old=r['filename'];mapping[old]='file:'+relative;mapping[old.removeprefix('file:/')]=relative
                mapping[old.removeprefix('file:')]=relative
                patch_resource(r,info);mappedresources.append(r['sourceUuid'])
        assert mappedresources,folder
        stage_file(portrait,work/'midias'/media_name)
        report['bundled_media'].append({'name':media_name,'source':str(portrait.relative_to(PROD)),'sha256':sha(portrait),'role':'original portrait animation, no new render'})
        # Bundle already-received exact-name sources needed by this character.
        # All unavailable user/plugin files retain their working PC paths.
        for ref in sorted(used):
            if ref in mapping:continue
            rec=inv.get(ref)
            if not rec or rec['plugin_resource_reference']:
                report['original_external_sources'].append(ref);continue
            source=None
            candidates=[Path(p)for p in rec['local_exact_matches']if Path(p).is_file()]
            if candidates:source=candidates[0]
            if source is None and rec['packaged_exact_matches']:
                hit=rec['packaged_exact_matches'][0];cache=P/'cache_fontes'/rec['filename'];cache.parent.mkdir(exist_ok=True)
                if not cache.exists():
                    with zipfile.ZipFile(hit['zip'])as z,cache.open('wb')as f:f.write(z.read(hit['entry']))
                source=cache
            if source is None:
                report['original_external_sources'].append(ref);continue
            with source.open('rb')as f:prefix=f.read(64)
            if prefix.startswith(b'version https://git-lfs'):
                report['original_external_sources'].append(ref);continue
            target_name=rec['filename'];stage_file(source,work/'midias'/target_name)
            dest='./midias/'+target_name;mapping[ref]='file:'+dest;mapping[ref.removeprefix('file:/')]=dest;mapping[ref.removeprefix('file:')]=dest
            report['bundled_media'].append({'name':target_name,'sha256':sha(source),'role':'received source with exact original basename'})
        project=replace(project,mapping)
        main=next(t for t in project['timelineInfos']if t['timelineId']==project['currentTimelineId'])
        shots=json.loads((PROD/folder/'timeline.json').read_text())['shots']
        for ti,tr in enumerate(main['trackInfos']):
            for ci,c in enumerate(tr['clipList']):
                adapted=adapt_transform(c,shots)
                if adapted:report['adapted_video_clips'].append({'track':ti,'clip':ci,**adapted})
        report['nested_portrait_timelines_adapted']=[]
        for tl in project['timelineInfos']:
            if tl is main:continue
            movieclips=[c for tr in tl['trackInfos']for c in tr['clipList']if c.get('filename','').endswith(media_name)]
            if movieclips:
                tl.update(resolutionWidth=1080,resolutionHeight=1920,aspectRatioX=9,aspectRatioY=16)
                for c in movieclips:adapt_transform(c,shots)
                report['nested_portrait_timelines_adapted'].append(tl['timelineId'])
        updated_resources={r['filename']:r for r in project['resources']if r['sourceUuid']in mappedresources}
        items=replace(json.loads(raw[MI])['media_items'],mapping)
        for mid,item in items.items():
            if mid==ROOT:item.update(name=label+' | Short 9x16',duration=duration)
            filename=item.get('download_url','');r=updated_resources.get('file:'+filename)
            if r:
                item['media_length']=r['mediaLength'];item['width']=1080;item['height']=1920
        filename=f'{folder[:2]}_{label}_Editado_9x16.wfp'
        meta=copy.deepcopy(oldmeta);meta.update(project_file_name=Path(filename).stem,project_timeline_duration=duration,project_current_position=0,
             project_timeline_resolution=[1080,1920],project_timeline_ratio=[9,16],project_guid='{'+str(uuid.uuid4()).upper()+'}',
             proj_zip_save_path=filename,proj_cover_proj_path='',project_custom_cover=False)
        entries={}
        for name,data in raw.items():
            if name.endswith(('.json','.wesproj'))and name not in (TL,MI,META):
                try:
                    d=replace(json.loads(data),mapping)
                    if name.endswith('.wesproj'):
                        for r in d.get('resources')or[]:
                            if r.get('filename','').endswith(media_name):patch_resource(r,info)
                        for tl in d.get('timelineInfos')or[]:
                            movieclips=[c for tr in tl.get('trackInfos',[])for c in tr['clipList']if c.get('filename','').endswith(media_name)]
                            if movieclips:
                                tl.update(resolutionWidth=1080,resolutionHeight=1920,aspectRatioX=9,aspectRatioY=16)
                                for c in movieclips:adapt_transform(c,shots)
                    if name.endswith('/media.json')and isinstance(d,dict):
                        r=updated_resources.get('file:'+d.get('file_name',''))
                        if r:d['sourceInfo']={'basicInfo':{k:r[k]for k in ('streamType','fourCC','mediaLength','videoStreamCount','audioStreamCount','bitRate')},'vidStreamInfos':r.get('vidStreamInfo',[]),'audStreamInfos':r.get('audStreamInfo',[])}
                    data=dump(d)
                except (ValueError,UnicodeDecodeError):pass
            entries[name]=data
        entries[TL]=dump(project);entries[MI]=media_structure(items);entries[META]=dump(meta)
        target=work/filename
        with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
            for name,data in entries.items():z.writestr(name,data)
        report.update(project=str(target.relative_to(OUT)),duration_seconds=duration/TICKS,sha256=sha(target),main_clips=sum(len(tr['clipList'])for tr in main['trackInfos']),dependent_timelines=sorted(dependency_ids),native_application_open_test='not executed; requires Filmora',all_original_nested_timelines_and_plugin_caches_retained=True)
        (work/'FONTES_NO_SEU_PC.txt').write_text('As fontes abaixo mantêm os caminhos do seu projeto original. Se o Filmora pedir, localize o arquivo no seu PC. Plugins continuam dependendo da sua instalação.\n\n'+'\n'.join(report['original_external_sources'])+'\n')
        allreports.append(report);print('READY',folder,report['duration_seconds'],report['main_clips'],flush=True)
    assert sha(SOURCE)==SOURCE_SHA
    (P/'manifesto.json').write_text(json.dumps({'source_sha256':SOURCE_SHA,'source_preserved':True,'projects':allreports},ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':make()
