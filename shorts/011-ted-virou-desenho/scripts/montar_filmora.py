"""Reconstrói a timeline do Ted com a estrutura nativa da referência do Tube."""
import base64
import copy
import hashlib
import importlib.util
import json
from math import gcd
from fractions import Fraction
from pathlib import Path
import struct
import subprocess
import uuid
import zipfile

from produzir import F, M, P, R, SONIC, TITLE, W, H, FPS, VOICE, VISUAL_TRACKS, sha

ROOT = '{204E72A3-B517-44d4-806F-9E9D84D5F904}'
BASE = 'ProjectFolder/Medias/'
TL = f'{BASE}{ROOT}/timeline.wesproj'
EXTRA = f'{BASE}{ROOT}/extra.json'
LIB = BASE + 'medias_info.json'
META = 'ProjectFolder/project_info.json'
REFERENCE = next((SONIC/'edicao_usuario_01/recebido').glob('*.wfp'))
OUT = F/f'{TITLE}_9x16.wfp'
REFERENCE_SHA = 'bf145baeebb2087f05023716b7d9f5b351a4fcbda949715a1f000061e427d9c3'
LABELS = {
    'voz':'Voz integral', 'musica':'Trilha original', 'sfx':'Entradas', 'foley':'Acentos',
    'meme':'Banco de memes', 0:'Grafismo em movimento', 'cenario':'Ambiente do trailer', 1:'Molduras',
    2:'Trailer e sofá', 3:'Fotos, fonte e anúncio', 4:'Comparações',
    5:'Massacote · corpo', 6:'Massacote · cabeça', 7:'Massacote · bigode', 8:'Reações cômicas',
}


def uid():
    return str(uuid.uuid4())


def guid():
    return '{' + uid().upper() + '}'


def data(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':')).encode()


def ticks(seconds):
    return round(seconds * 10_000_000)


def values(obj, key, value):
    fields = obj.setdefault('userData', [])
    field = next((item for item in fields if item['key'] == key), None)
    if field is None:
        field = {'key': key, 'size': 0, 'data': ''}
        fields.append(field)
    raw = value if isinstance(value, bytes) else value.encode()
    raw = raw.ljust(field['size'], b'\0')
    field.update(size=len(raw), data=base64.b64encode(raw).decode())


def new_effect(prototype):
    result = copy.deepcopy(prototype)
    result['thisUId'] = uid()
    values(result, 3, guid())
    return result


def effects(clip):
    return [fx for chain in clip['effectChainList'] for fx in chain['effectList']]


def probe(path):
    return json.loads(subprocess.check_output([
        'ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path),
    ]))


def write_project(plan):
    assert sha(REFERENCE) == REFERENCE_SHA
    divisor = gcd(W,H)
    aspect_x, aspect_y = W // divisor, H // divisor
    project_title = plan.get('name','TED virou DESENHO')
    with zipfile.ZipFile(REFERENCE) as source:
        tl, extra, library, meta = (json.loads(source.read(n)) for n in (TL, EXTRA, LIB, META))
    timeline = next(t for t in tl['timelineInfos'] if t['timelineId'] == tl['currentTimelineId'])
    old_clips = [c for t in timeline['trackInfos'] for c in t['clipList']]
    examples = {
        suffix: next(c for c in old_clips if c.get('filename','').endswith(filename))
        for suffix, filename in {'.png':'Corpo_04_apontando_esquerda.png',
                                 '.wav':'Voz_Dery_Original.wav', '.mp4':'Contexto.mp4'}.items()
    }
    resource_examples = {
        key: next(r for r in tl['resources'] if r['sourceUuid'] == c['sourceUuid'])
        for key,c in examples.items()
    }
    transform = next(fx for fx in effects(examples['.png']) if fx['display'] == 'transform')
    named = {fx['display']:fx for c in old_clips for fx in effects(c)}
    transitions = {c['postTransition']['display']:c['postTransition'] for c in old_clips if c.get('postTransition')}
    item_examples = {
        typ: next(it for it in library['media_items'].values()
                  if it['media_type'] == typ and not it.get('download_url','').endswith('.cof'))
        for typ in (2,4,16)
    }
    timeline_uuid = guid()
    values(timeline,11000,timeline_uuid)
    values(timeline,50,project_title)
    extra.update(mediaClipsMapInfo={}, usedTemplateResInfo={},
                 allMarkersInfo={'beatDetectInfo':{}}, pendingMarkersInfo={},
                 highlightInfo={}, TextSentence={'TextSentence':[]}, fontNameInfo=[], usedBizFont=[])
    tracks, assets, items, files = {}, {}, {}, {}
    for tag, label in LABELS.items():
        audio = tag not in VISUAL_TRACKS
        track = dict(trackType=2 if audio else 1,trackTag=len(tracks)+1,uuid=uid(),clipList=[])
        if not audio:
            values(track,21,struct.pack('<i',1))
            values(track,12001,b'\0')
        values(track,50,label)
        tracks[tag] = track

    def asset(name):
        if name in assets:
            return assets[name]
        path = M/name
        suffix = path.suffix
        typ = {'.mp4':2,'.wav':4,'.png':16}[suffix]
        image, audio = typ == 16, typ == 4
        info = probe(path)
        stream = info['streams'][0]
        seconds = 0 if image else Fraction(stream['time_base']) * int(stream['duration_ts'])
        length = ticks(seconds)
        url = './midias/' + name
        resource = copy.deepcopy(resource_examples[suffix])
        resource.update(sourceUuid=uid(),filename='file:'+url,mediaLength=length,createDate=-1,modifyDate=0,
                        streamType=5 if image else 3 if audio else 1,videoStreamCount=int(not audio),
                        audioStreamCount=int(audio),bitRate=0 if image else int(info['format']['bit_rate']))
        if audio:
            rate, channels, depth = int(stream['sample_rate']), stream['channels'], stream['bits_per_sample']
            ratebits = rate * channels * depth
            resource.pop('vidStreamInfo',None)
            resource['audStreamInfo'][0].update(
                audStreamId=0, sampleRate=rate, channels=channels, duration=float(seconds), streamLength=length,
                bitDepth=depth, bitRate=ratebits, bytesPerSecond=ratebits//8,
                description='Uncompressed PCM', fourCC=541278529,
            )
        else:
            width,height = stream['width'],stream['height']
            alpha = int(image and stream['pix_fmt'] == 'rgba')
            resource.pop('audStreamInfo',None)
            resource['vidStreamInfo'][0].update(
                vidStreamId=0, width=width,height=height,xRatio=width if image else width*1000,
                yRatio=height if image else height*1000, alphaChannel=alpha, bitsDepth=32 if alpha else 24,
                totalFrames=0 if image else int(stream['nb_frames']), streamLength=length,
                frameRate={'num':FPS,'den':1}, maxFrameRate={'num':FPS,'den':1},
                lastframeRate={'num':FPS,'den':1}, premultiAlphaTypePhoto=-1,
            )
        mid = guid()
        item = copy.deepcopy(item_examples[typ])
        item.update(id=mid,name=path.stem,download_url=url,media_type=typ,media_length=length or 50_000_000,
                    stream_idx=-1 if image else 0,src_md5=hashlib.md5(path.read_bytes()).hexdigest(),
                    mark_info_list=[{'mark_in':-1,'mark_out':-1}],scence_info=[])
        items[mid]=item
        basic_fields = ('streamType','fourCC','mediaLength','programCount','videoStreamCount',
                        'audioStreamCount','subPicStreamCount','bitRate','createDate')
        basic = {k:resource.get(k,0) for k in basic_fields}
        files[f'{BASE}{mid}/media.json'] = data(dict(
            version='1.1.5',file_name=url,sourceInfo=dict(
                basicInfo=basic,vidStreamInfos=resource.get('vidStreamInfo',[]),
                audStreamInfos=resource.get('audStreamInfo',[]), recordInfos={}),
        ))
        assets[name] = resource, mid, float(seconds)
        return assets[name]

    def motion(event, resource):
        fx = new_effect(transform)
        keys = event['keys']
        fit = 1.
        if event['file'].endswith('.mp4'):
            # O Filmora ajusta um vídeo horizontal à largura da timeline.
            vid = resource['vidStreamInfo'][0]
            fit = vid['width']/W
        axes = ('Position_x','Position_y','Scale_x','Scale_y','Rotation')
        scales = (1.,1.,100.*fit,100.*fit,1.)
        first = dict(EnableTransform=1,_Anchor_x=.5,_Anchor_y=.5)
        first.update({axis:value*mult for axis,value,mult in zip(axes,keys[0][1:],scales)})
        fx['paramList'] = [
            dict(name=k,fxParam=dict(paramType=5 if k=='EnableTransform' else 3,unValue=v))
            for k,v in first.items()
        ]
        fx['paramMapList'] = []
        for i,(param,scale) in enumerate(zip(axes,scales), start=1):
            frames = [dict(_time=round(key[0],8),Interpolation=1,_value=key[i]*scale) for key in keys]
            fx['paramMapList'].append(dict(
                key=3,name=param,keyFrame=dict(parameter=data(
                    dict(Version=2,ParameterType=0,keyframeSets=frames)).decode()),
            ))
        return fx

    linked_transitions = []
    for e in plan['events']:
        name, start, end, offset = (e[k] for k in ('file','start','end','offset'))
        name_path = Path(name)
        suffix = name_path.suffix
        resource, mid, source_length = asset(name)
        original = examples[suffix]
        c = copy.deepcopy(original)
        for k in ('preTransition','postTransition','stabilization','stabilizeAnalysisData','image_denoise',
                  'face_cluster','volumeKeyframe','audioDuckingframe','humanseg_hair'):
            c.pop(k,None)
        c.update(filename=resource['filename'],sourceUuid=resource['sourceUuid'],thisUId=uid(),streamId=0,
                 inPoint=ticks(offset),outPoint=ticks(offset + end-start),tlBegin=ticks(start),tlEnd=ticks(end))
        if suffix != '.wav':
            c['picSequence'] = False
            c['backgroundFillBluredness'] = 0
        # O clipe novo só recebe IDs e nome vinculados ao Ted.
        c['userData'] = []
        cid = guid()
        for key, value in [(3,cid),(10,mid),(50,name_path.stem),(6,struct.pack('<i',timeline['timelineId']))]:
            values(c,key,value)
        extra['mediaClipsMapInfo'][cid] = dict(mediaId=mid,subClips={})
        total = source_length or plan['duration']
        speed = dict(Version=2,ParameterType=0,_totalTime=total,keyframeSets=[
            dict(_time=t,Interpolation=6,_value=1.) for t in (0.,total)
        ])
        c['speed'] = dict(offset=offset,offsetEnd=offset+end-start,reverse=False,speedParam=data(speed).decode())
        basic = []
        if suffix != '.wav':
            pip = dict(Algorithm='Bilinear',BlendMode=0,BlenderName='video/blender/simple-pip',Enable=True,Opacity=100.)
            c['pipBuf'] = data(pip).decode()
            c['pipBufSize'] = len(c['pipBuf'])
            basic = [motion(e, resource)]
        c['effectChainList'] = [
            dict(name='Basic',effectList=basic),
            dict(name='Effect',effectList=[new_effect(named[label]) for label in e.get('fx',[])]),
        ]
        if e.get('transition'):
            linked_transitions.append((e, c))
        tracks[e['track']]['clipList'].append(c)

    for track in tracks.values():
        track['clipList'].sort(key=lambda c:c['tlBegin'])
        values(track,12000,struct.pack('<i',len(track['clipList'])))
    for e, c in linked_transitions:
        next_clip = next(row for row in tracks[e['track']]['clipList'] if row['tlBegin'] == c['tlEnd'])
        assert next_clip['type'] == c['type']
        handle = 4/FPS if e['transition']=='Fast Bounce' else 5/FPS
        transition = new_effect(transitions[e['transition']])
        transition.update(tlBegin=ticks(e['end']-handle),tlEnd=ticks(e['end']+handle))
        c['postTransition'] = transition

    timeline.update(trackInfos=list(tracks.values()),frameRate={'num':FPS,'den':1},
                    resolutionWidth=W,resolutionHeight=H,aspectRatioX=aspect_x,aspectRatioY=aspect_y,sampleRate=48000)
    tl.update(projectName=OUT.stem,currentTimelineId=timeline['timelineId'],
              resources=[row[0] for row in assets.values()],timelineInfos=[timeline])
    root = copy.deepcopy(library['media_items'][ROOT])
    root.update(name=project_title,timeline_uuid=timeline_uuid,duration=ticks(plan['duration']))
    items[ROOT] = root
    meta.update(project_file_name=OUT.stem,proj_zip_save_path=OUT.name,project_guid=guid(),
                project_timeline_duration=ticks(plan['duration']),project_current_position=0,
                project_timeline_framerate=[FPS,1],project_timeline_resolution=[W,H],
                project_timeline_ratio=[aspect_x,aspect_y],project_sample_rate=48000,project_custom_cover=False,
                proj_cover_proj_path='',project_cover='',project_used_pack_list=[])
    # A biblioteca nativa lista entradas consecutivas com a mesma chave media_item.
    structure = ','.join('"media_item":'+json.dumps(mid) for mid in items if mid!=ROOT)
    files[LIB] = (f'{{"media_structure":{{"Folder":{{{structure}}},"media_item":{json.dumps(ROOT)}}},'
                  f'"media_items":{data(items).decode()}}}').encode()
    files.update({TL:data(tl),EXTRA:data(extra),META:data(meta)})
    with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED,compresslevel=4) as output:
        for n,b in files.items():
            output.writestr(n,b)
    return assets


def verify(plan, assets):
    script = R/'shorts/009-jogos-que-a-internet-tentou-cancelar/production/14-video-completo/validar_registro_nativo.py'
    spec = importlib.util.spec_from_file_location('native',script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    report = module.validar(OUT,strict=True)
    with zipfile.ZipFile(OUT) as archive:
        tl, library = (json.loads(archive.read(n)) for n in (TL,LIB))
    resources = {r['sourceUuid']:r for r in tl['resources']}
    ids, effects_seen, transitions_seen = set(), set(), []
    tracks = tl['timelineInfos'][0]['trackInfos']
    for track in tracks:
        clips = track['clipList']
        assert all(a['tlEnd'] <= b['tlBegin'] for a,b in zip(clips,clips[1:]))
        expected = sorted((e for e in plan['events'] if list(LABELS)[track['trackTag']-1] == e['track']),
                          key=lambda e:e['start'])
        assert len(expected) == len(clips)
        for e,c in zip(expected,clips):
            resource = resources[c['sourceUuid']]
            assert c['filename'] == resource['filename'] == 'file:./midias/'+e['file']
            assert c['thisUId'] not in ids
            ids.add(c['thisUId'])
            assert (c['tlBegin'],c['tlEnd']) == (ticks(e['start']),ticks(e['end']))
            assert c['inPoint'] == ticks(e['offset'])
            assert abs((c['outPoint']-c['inPoint']) - (c['tlEnd']-c['tlBegin'])) <= 1
            if resource['mediaLength']:
                assert c['outPoint'] <= resource['mediaLength']+1, e['file']
            assert c['tlEnd'] <= ticks(plan['duration'])
            speed = json.loads(c['speed']['speedParam'])
            assert not c['speed']['reverse'] and all(k['_value']==1 for k in speed['keyframeSets'])
            assert (M/e['file']).is_file()
            mid = assets[e['file']][1]
            assert library['media_items'][mid]['src_md5'] == hashlib.md5((M/e['file']).read_bytes()).hexdigest()
            for fx in effects(c):
                effects_seen.add(fx['display'])
                for param in fx.get('paramMapList',[]):
                    arr = json.loads(param['keyFrame']['parameter'])['keyframeSets']
                    assert arr[-1]['_time'] <= (c['tlEnd']-c['tlBegin'])/1e7+1e-6
            if e.get('transition'):
                assert c['postTransition']['display'] == e['transition']
                transitions_seen.append(e['transition'])
    assert len(ids) == len(plan['events'])
    assert sha(REFERENCE) == REFERENCE_SHA
    report.update(clips=len(ids),resources=len(assets),tracks=len(tracks),sha256=sha(OUT),
                  effects=sorted(effects_seen),transitions=transitions_seen,
                  filmora_native_executed=False,voice_complete=VOICE in assets)
    (P/'validacao_filmora.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(report,indent=2,ensure_ascii=False),flush=True)


if __name__ == '__main__':
    plan = json.loads((P/'timeline.json').read_text())
    verify(plan,write_project(plan))
