"""Gera as variantes Filmora com efeitos nativos e áudio PCM real."""
import base64
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import struct
import sys
from zipfile import ZipFile, ZIP_DEFLATED

from revisar import P, F, M, TITLE, TL, read_native, v1, frame
import montar_filmora as film

ROOT = film.ROOT
BASE = film.BASE
META = film.META
LIB = film.LIB
EXTRA = film.EXTRA
EFFECTS = {
    'Glow': [(0.92,1.21),(6.92,7.36),(22.73,23.03),(37.10,37.57)],
    'Text Vibrate': [(1.00,1.27),(20.70,20.97),(37.13,37.43)],
    'Grunge_Jitter': [(6.92,7.16),(34.06,34.30),(37.15,37.44)],
}
EMPTY_KEYS = {'parameter':'{"Version": 2,"ParameterType": 0,"keyframeSets": [],"MD5":"d41d8cd98f00b204e9800998ecf8427e"}'}


def load(path):
    with ZipFile(path) as z:
        assert z.testzip() is None
        return {n:z.read(n) for n in z.namelist() if not n.endswith('/')}


def field(item, key):
    return next(base64.b64decode(r['data']).rstrip(b'\0') for r in item['userData'] if r['key']==key)


def clips(timeline):
    return [c for t in timeline['trackInfos'] for c in t['clipList']]


def main_timeline(doc):
    return next(t for t in doc['timelineInfos'] if t['timelineId']==doc['currentTimelineId'])


def fresh_effects(chain):
    fresh=deepcopy(chain)
    for item in fresh:
        item['effectList']=[film.new_effect(e) for e in item['effectList']]
    return fresh


def clip_audio(doc, files, native, plan):
    resources={r['sourceUuid']:r for r in doc['resources']}
    proto=next(c for c in clips(native) if c.get('filename','').endswith('Voz_Original.wav'))
    base_follow=next(ch for ch in proto['effectChainList'] if ch['name']=='BasicFollow')
    fmt_pcm=541934416
    library=json.loads(files[LIB])['media_items']
    for c in clips(main_timeline(doc)):
        if c.get('type')!=2:
            continue
        assert c['filename'].endswith('.wav')
        resource=resources[c['sourceUuid']]
        pcm=resource['audStreamInfo'][0]
        assert (pcm['bitDepth'],pcm['channels'],pcm['sampleRate']) == (16,2,48000)
        pcm['fourCC']=fmt_pcm
        resource.update(fourCC=7758199,bitRate=1536000,programCount=1)
        mid=field(c,10).decode()
        path=f'{BASE}{mid}/media.json'
        cache=json.loads(files[path])
        cache['sourceInfo']['basicInfo'].update(fourCC=7758199,bitRate=1536000,programCount=1)
        cache['sourceInfo']['audStreamInfos']=[pcm]
        assert library[mid]['src_md5']==hashlib.md5((M/Path(c['filename']).name).read_bytes()).hexdigest()
        files[path]=film.data(cache)
        c['volumeKeyframe']=deepcopy(EMPTY_KEYS)
        c['audioDuckingframe']=deepcopy(EMPTY_KEYS)
        c['denoiseV3Strength']=proto['denoiseV3Strength']
        follow,=fresh_effects([base_follow])
        gain=next(e['mix_gain_db'] for e in plan['events'] if e['file']==Path(c['filename']).name)
        vol=next(e for e in follow['effectList'] if e['display']=='volume')
        vol['paramList']=[{'name':'VolumeGain','fxParam':{'paramType':2,'unValue':gain}}]
        duck=next(e for e in follow['effectList'] if e['display']=='ducking')
        duck['enable']=False
        c['effectChainList']=[
            {'name':'Basic','effectList':[]},{'name':'Effect','effectList':[]},follow,
        ]


def change_track(number, name, tr):
    tr['trackTag']=number
    film.values(tr,50,name)
    film.values(tr,12000,struct.pack('<i',len(tr['clipList'])))
    return tr


def add_effects(doc, sonic):
    timeline=main_timeline(doc)
    tracks=timeline['trackInfos']
    visual=next(tr for tr in reversed(tracks) if tr['trackType']==1)
    for label, ranges in EFFECTS.items():
        clip_base=next(c for c in clips(sonic) if c.get('type')==8 and
                       any(fx['display']==label for fx in film.effects(c)))
        tr=deepcopy(visual)
        tr.update(uuid=film.uid(),clipList=[])
        for start,end in ranges:
            start,end=film.ticks(frame(start)/30),film.ticks(frame(end)/30)
            clip=deepcopy(clip_base)
            clip.update(thisUId=film.uid(),tlBegin=start,tlEnd=end,
                        outPoint=clip_base['inPoint']+end-start,
                        effectChainList=fresh_effects(clip_base['effectChainList']))
            film.values(clip,3,film.guid())
            film.values(clip,6,struct.pack('<i',timeline['timelineId']))
            tr['clipList'].append(clip)
        tracks.append(change_track(len(tracks)+1,label+' · nativo',tr))


def add_native_bg(doc, native_doc, extra):
    """Reaproveita o recurso instalado e o ajuste que o usuário salvou no Ted."""
    native_tl=main_timeline(native_doc)
    timeline=main_timeline(doc)
    source_track=next(tr for tr in native_tl['trackInfos'] if tr['trackType']==1 and
                      any(c.get('filename','').endswith('downloadCommonCfg.cof') for c in tr['clipList']))
    target_track=next(tr for tr in timeline['trackInfos'] if tr['trackType']==1 and
                      all(c.get('filename','').split('/')[-1].startswith('Fundo_') for c in tr['clipList']))
    old_uuids={c['sourceUuid'] for c in target_track['clipList']}
    old_mids={field(c,10).decode() for c in target_track['clipList']}
    for c in target_track['clipList']:
        extra['mediaClipsMapInfo'].pop(field(c,3).decode(),None)
    target_track['clipList']=[]
    stock=deepcopy(next(c for c in native_doc['resources'] if c['sourceUuid']==source_track['clipList'][0]['sourceUuid']))
    # O arquivo COF resolve pelo nome do recurso instalado e seus metadados nativos.
    stock['filename']=source_track['clipList'][0]['filename']
    doc['resources']=[r for r in doc['resources'] if r['sourceUuid'] not in old_uuids]+[stock]
    for source in source_track['clipList']:
        c=deepcopy(source)
        c['thisUId']=film.uid()
        c['effectChainList']=fresh_effects(c['effectChainList'])
        for k in ('preTransition','postTransition'):
            if c.get(k):
                c[k]=film.new_effect(c[k])
        # Caminhos absolutos de efeitos IA desabilitados no computador que salvou o arquivo.
        c['userData']=[u for u in c['userData'] if u['key'] not in (73,74)]
        film.values(c,3,film.guid())
        film.values(c,6,struct.pack('<i',timeline['timelineId']))
        target_track['clipList'].append(c)
    change_track(target_track['trackTag'],'Fundo do seu Ted · Filmora',target_track)
    return old_mids


def without_stock_library(files, remove):
    lib=json.loads(files[LIB])
    for mid in remove:
        del lib['media_items'][mid]
        files.pop(f'{BASE}{mid}/media.json',None)
    structure=','.join('"media_item":'+json.dumps(mid) for mid in lib['media_items'] if mid!=ROOT)
    return (f'{{"media_structure":{{"Folder":{{{structure}}},"media_item":{json.dumps(ROOT)}}},'
            f'"media_items":{film.data(lib["media_items"]).decode()}}}').encode()


def build(ted, sonic, temp):
    plan=json.loads((P/'timeline.json').read_text())
    film.P,film.F,film.M,film.OUT = P,F,M,temp/'base.wfp'
    film.LABELS.update(saida='Swooshes de saída',impacto='Impacto da reação')
    # As novas faixas de som ficam junto do restante da mixagem.
    film.LABELS = dict(sorted(film.LABELS.items(),key=lambda row:row[0] in v1.VISUAL_TRACKS))
    film.write_project(plan)
    source=load(film.OUT)
    doc=json.loads(source[TL])
    user_files=load(ted)
    ted_doc=json.loads(user_files[TL])
    native=main_timeline(ted_doc)
    clip_audio(doc,source,native,plan)
    add_effects(doc,read_native(sonic))
    for stock in (True,False):
        files=source.copy()
        result=deepcopy(doc)
        extra=json.loads(files[EXTRA])
        meta=json.loads(files[META])
        file=F/(TITLE+('' if stock else '_Fundo_Local')+'_9x16.wfp')
        if stock:
            removed=add_native_bg(result,ted_doc,extra)
            files[LIB]=without_stock_library(files,removed)
        else:
            background=next(tr for tr in main_timeline(result)['trackInfos'] if tr['trackType']==1)
            change_track(background['trackTag'],'Fundo local',background)
        result['projectName']=file.stem
        meta.update(project_file_name=file.stem,proj_zip_save_path=file.name,project_guid=film.guid())
        for key in ('project_color_space','project_player_quality','project_player_zoom_level','project_player_safe_zone'):
            v=json.loads(user_files[META]).get(key)
            if v is not None:
                meta[key]=v
        files.update({TL:film.data(result),EXTRA:film.data(extra),META:film.data(meta)})
        with ZipFile(file,'w',ZIP_DEFLATED,compresslevel=4) as z:
            for n,data in files.items():
                z.writestr(n,data)
        print(file.name,flush=True)


if __name__=='__main__':
    build(*map(Path,sys.argv[1:]))
