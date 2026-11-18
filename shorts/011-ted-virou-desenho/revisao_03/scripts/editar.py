"""Edita os dois trechos de reação dentro dos projetos da revisão 2."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import struct
import sys
from zipfile import ZipFile, ZIP_DEFLATED

P = Path(__file__).resolve().parents[1]
TED = P.parent
R2 = TED/'revisao_02'
OUT = P/'output'
F = OUT/'Filmora'
M = F/'midias'
TITLE = 'TED_virou_DESENHO_R3_2D'
sys.path.insert(0,str(R2/'scripts'))
from revisar import frame, sec, ease, v1, write_json
from projeto import TL, META, LIB, EXTRA, field, load, main_timeline, film, without_stock_library
import entregar as checks

AVATAR = (5,6,7)
WINDOWS = ((4.77,10.5),(35.73,39.27))


def starts_in(seconds, windows=WINDOWS):
    return any(frame(start)<=frame(seconds)<frame(end) for start,end in windows)


def plan():
    baseline=json.loads((TED/'timeline.json').read_text())
    current=json.loads((R2/'timeline.json').read_text())
    events=[e for e in current['events']
            if e['track']!=8 and not (e['track'] in AVATAR and starts_in(e['start']))]
    replacements=[]
    for track in AVATAR:
        def at(seconds):
            return deepcopy(next(e for e in baseline['events']
                                 if e['track']==track and frame(e['start'])==frame(seconds)))
        scare=at(4.77)
        finish=frame(7.50)
        start=frame(scare['start'])
        before=frame(scare['end'])
        _,x,y,sx,sy,angle=scare['keys'][-1]
        for i in range(before+1,finish+1):
            # O personagem mantém a pose e recua um pouco no fim da réplica.
            u=(i-before)/(finish-before)
            lift=ease(u)*(1-.75*ease((u-.52)/.48))
            scare['keys'].append([sec(i-start),x+.008*lift,y-.015*lift,sx*(1+.027*lift),
                                  sy*(1+.027*lift),angle-.55*lift])
        scare.update(end=sec(finish),reason='Susto em 2D, com recuo leve antes da troca de assunto')
        replacements += [scare,at(7.50),at(35.73)]

        shrug=at(0)
        first,last=frame(37.17),frame(current['duration'])
        keys=[]
        prototype=shrug['keys']
        for i in range(last-first+1):
            u=i/(last-first)
            pose=ease(u)
            k=min(round(pose*(len(prototype)-1)),len(prototype)-1)
            _,x,y,sx,sy,angle=prototype[k]
            size=1.28+.055*pose
            keys.append([sec(i),.505+(x-.53)*size,.581+(y-.69)*size,
                         sx*size,sy*size,angle+.60*pose])
        shrug.update(start=sec(first),end=sec(last),keys=keys,
                     reason='Pose de dúvida em 2D durante a pergunta final')
        replacements.append(shrug)
    events.extend(replacements)
    assert all(max(k[3] for k in e['keys'])<1.1 for e in replacements)
    current.pop('realistic_holds',None)
    current.update(revision=3,events=events,
                   preview_seconds=[6.47,6.93,7.27,7.5,8.6,9.03,36.57,37.17,37.55,38.8])
    return current,replacements


def clip_for(template, event, timeline):
    clip=deepcopy(template)
    a,b=(film.ticks(event[k]) for k in ('start','end'))
    length=(b-a)/10_000_000
    clip.update(thisUId=film.uid(),tlBegin=a,tlEnd=b,inPoint=0,outPoint=b-a)
    clip['speed'].update(offset=0.,offsetEnd=length)
    speed=json.loads(clip['speed']['speedParam'])
    assert all(k['_value']==1 for k in speed['keyframeSets'])
    clip['speed']['speedParam']=film.data(speed).decode()
    film.values(clip,3,film.guid())
    film.values(clip,6,struct.pack('<i',timeline['timelineId']))

    motion=next(fx for fx in film.effects(clip) if fx['display']=='transform')
    axes={'Position_x':(1,1),'Position_y':(2,1),'Scale_x':(3,100),'Scale_y':(4,100),'Rotation':(5,1)}
    for p in motion['paramList']:
        if p['name'] in axes:
            i,scale=axes[p['name']]
            p['fxParam']['unValue']=event['keys'][0][i]*scale
    for row in motion['paramMapList']:
        i,scale=axes[row['name']]
        keys=json.loads(row['keyFrame']['parameter'])
        keys['keyframeSets']=[dict(_time=round(k[0],8),Interpolation=1,_value=k[i]*scale)
                              for k in event['keys']]
        row['keyFrame']['parameter']=film.data(keys).decode()
    motion.update(film.new_effect(motion))
    return clip


def edit_project(suffix, replacements):
    src=R2/'output/Filmora'/f'TED_virou_DESENHO_R2{suffix}_9x16.wfp'
    dest=F/f'{TITLE}{suffix}_9x16.wfp'
    files=load(src)
    doc,extra,meta=(json.loads(files[k]) for k in (TL,EXTRA,META))
    timeline=main_timeline(doc)
    bindings=extra['mediaClipsMapInfo']
    labels={f'Massacote · {name}':part for name,part in [('corpo',5),('cabeça',6),('bigode',7)]}
    removed_media,removed_uuids=set(),set()
    untouched=[]
    for track in timeline['trackInfos']:
        clips=track['clipList']
        if not clips:
            continue
        label=field(track,50).decode()
        if label=='Reações cômicas':
            for c in clips:
                removed_media.add(field(c,10).decode())
                removed_uuids.add(c['sourceUuid'])
                del bindings[field(c,3).decode()]
            track['clipList']=[]
            continue
        part=labels.get(label)
        if part is None:
            untouched.append(deepcopy(track))
            continue
        templates={Path(c['filename']).name:c for c in clips}
        keep=[]
        for c in clips:
            if starts_in(c['tlBegin']/10_000_000):
                del bindings[field(c,3).decode()]
            else:
                keep.append(c)
        for e in (e for e in replacements if e['track']==part):
            c=clip_for(templates[e['file']],e,timeline)
            bindings[field(c,3).decode()]={'mediaId':field(c,10).decode(),'subClips':{}}
            keep.append(c)
        track['clipList']=sorted(keep,key=lambda c:c['tlBegin'])
        film.values(track,12000,struct.pack('<i',len(keep)))
        spans=[(c['tlBegin'],c['tlEnd']) for c in keep]
        for a,b in WINDOWS:
            first,last=(film.ticks(sec(frame(t))) for t in (a,b))
            section=[(s,e) for s,e in spans if first<=s<last]
            assert section[0][0]==first and section[-1][1]==last
            assert all(x[1]==y[0] for x,y in zip(section,section[1:]))
    assert len(removed_media)==len(removed_uuids)==14
    timeline['trackInfos']=[t for t in timeline['trackInfos'] if t['clipList']]
    assert all(t in timeline['trackInfos'] for t in untouched)
    doc['resources']=[r for r in doc['resources'] if r['sourceUuid'] not in removed_uuids]
    doc['projectName']=dest.stem
    meta.update(project_file_name=dest.stem,proj_zip_save_path=dest.name,project_guid=film.guid())
    files[LIB]=without_stock_library(files,removed_media)
    files.update({TL:film.data(doc),EXTRA:film.data(extra),META:film.data(meta)})
    with ZipFile(dest,'w',ZIP_DEFLATED,compresslevel=4) as zipped:
        for name,data in files.items():
            zipped.writestr(name,data)
    with ZipFile(dest) as zipped:
        assert all(not any(word in zipped.read(name) for word in (b'Dissolve_', b'Reacao_Choque',b'Reacao_Desconfianca'))
                   for name in zipped.namelist())
    return dest


def build(work):
    current,replacements=plan()
    M.mkdir(parents=True,exist_ok=True)
    work.mkdir(parents=True,exist_ok=True)
    names=sorted({e['file'] for e in current['events']})
    assert not any(name.startswith(('Reacao_','Choque_','Desconfianca_')) for name in names)
    upstream=R2/'output/Filmora'
    for name in names:
        shutil.copy2(upstream/'midias'/name,M/name)
    shutil.copy2(upstream/'Voz_Original.wav',F/'Voz_Original.wav')
    gains={e['file']:e['mix_gain_db'] for e in current['events'] if 'mix_gain_db' in e}
    checks.M=M
    projects=[]
    for suffix in ('','_Fundo_Local'):
        path=edit_project(suffix,replacements)
        projects.append(checks.verify_wfp(path,not suffix,gains,current))
    assert all((M/name).read_bytes()==(upstream/'midias'/name).read_bytes() for name in gains)
    v1.M=M
    v1.render(current,work,preview=True)
    report=P/'validacao.json'
    write_json(report,dict(projects=projects,seconds=current['duration'],revision=3,
                           avatar_media='Massacote 2D',removed_assets_per_wfp=14,
                           all_audio_media_unchanged=True,filmora_native_tested=False))
    instructions=F/'LEIA_PRIMEIRO.txt'
    instructions.write_text(
        'TED virou DESENHO · Revisão 3 · Massacote 2D\n\n'
        'Extraia o ZIP inteiro. Abra TED_virou_DESENHO_R3_2D_9x16.wfp com a pasta midias ao lado.\n'
        'O projeto principal usa o fundo instalado no Filmora. Se o fundo de catálogo não resolver,\n'
        'o WFP Fundo_Local usa o fundo incluído. Os WFPs usam o Massacote 2D nos dois trechos de reação.\n'
        'A validação conferiu os arquivos e vínculos dos dois projetos. A abertura no Filmora segue pendente.\n',
        encoding='utf-8',
    )
    package=OUT/f'{TITLE}_Filmora.zip'
    files=[*(F/p['file'] for p in projects),instructions,F/'Voz_Original.wav',*(M/name for name in names)]
    with ZipFile(package,'w',ZIP_DEFLATED,compresslevel=4) as zipped:
        for p in files:
            zipped.write(p,'Filmora/'+p.relative_to(F).as_posix())
        zipped.write(report,report.name)
    with ZipFile(package) as zipped:
        assert zipped.testzip() is None
        assert all(zipped.read('Filmora/'+p.relative_to(F).as_posix())==p.read_bytes() for p in files)
    write_json(P/'pacote.json',dict(file=package.name,bytes=package.stat().st_size,
                                 sha256=v1.sha(package),media_files=len(names)))
    print(package,flush=True)


if __name__=='__main__':
    build(Path(sys.argv[1]))
