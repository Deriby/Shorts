"""Projeto nativo editável do restante, com mídias em nomes únicos e plugins pagos.

Validação estrutural não substitui a abertura no Filmora do usuário.
"""
from pathlib import Path
from fractions import Fraction
import importlib.util,json,copy,zipfile,uuid,base64,sys
P=Path(__file__).resolve().parent;PROD=P.parent
WORK=P/'renders';OUT=P/'output';ROOT='{204E72A3-B517-44d4-806F-9E9D84D5F904}'
HELPER=PROD/'15-teste-estilo-filmora/produzir_teste.py'
def guid():return '{'+str(uuid.uuid4()).upper()+'}'
def tick(t):return round(t*1e7)
def textvalue(u):
    try:return base64.b64decode(u['data']).decode().strip('\0')
    except (ValueError,UnicodeDecodeError):return ''
def setvalue(u,value):
    raw=value.encode();raw+=b'\0'*max(0,u.get('size',0)-len(raw))
    u.update(data=base64.b64encode(raw).decode(),size=len(raw))

def temporary_project(rec):
    name='factory_'+rec['folder'].replace('-','_')
    spec=importlib.util.spec_from_file_location(name,HELPER);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    d=WORK/rec['folder'];m.P=d;m.OUT=d;m.MEDIA=d/'midias';m.WORK=d
    m.N_BODY=rec['frames'];m.BODY=rec['duration'];m.SHOTS=rec['events']
    path=m.make_project(total_duration=m.CARD+m.BODY,project_name='temporario')
    with zipfile.ZipFile(path)as z:
        raw={n:z.read(n)for n in z.namelist()}
    main=f'ProjectFolder/Medias/{ROOT}/timeline.wesproj'
    return raw,json.loads(raw[main]),json.loads(raw['ProjectFolder/Medias/medias_info.json'])['media_items']

def rewrite(node,pathmap,tidmap,mediamap,tlmap):
    if isinstance(node,list):
        for x in node:rewrite(x,pathmap,tidmap,mediamap,tlmap)
    elif isinstance(node,dict):
        for key in list(node):
            val=node[key]
            if key=='filename'and isinstance(val,str)and val in pathmap:node[key]=pathmap[val]
            elif key in ['timelineId','currentTimelineId']and val in tidmap:node[key]=tidmap[val]
            elif key in ['thisUId','uuid']and isinstance(val,str):node[key]=str(uuid.uuid4())
            elif isinstance(val,(dict,list)):rewrite(val,pathmap,tidmap,mediamap,tlmap)
        if 'userData'in node:
            for u in node['userData']:
                value=textvalue(u)
                if u['key']==10 and value in mediamap:setvalue(u,mediamap[value])
                if u['key']==11000 and value in tlmap:setvalue(u,tlmap[value])
                if u['key']==50 and node.get('filename'):setvalue(u,Path(node['filename']).stem)
        # Paid plugins stay in the project; screen oscillation is off by default.
        if node.get('display')=='Text Vibrate':node['enable']=False
        for key in ['preTransition','postTransition']:
            if 'Vibrate'in node.get(key,{}).get('display',''):node.pop(key)

def make_project():
    configs=[json.loads(p.read_text())for p in sorted(WORK.glob('*/config.json'))]
    assert len(configs)==7,'Wait for all seven prepared blocks'
    native=None;merged=None;items={};assets={};all_resources=[];nested=[];subs=[];at=0
    root_item=None;root_meta=None;root_extra=None
    for index,rec in enumerate(configs):
        print('NATIVE',rec['folder'],flush=True)
        raw,v,mi=temporary_project(rec)
        if native is None:
            native={k:b for k,b in raw.items()if '/Anon/'in k}
            merged=copy.deepcopy(v);merged['resources']=[];merged['timelineInfos']=[copy.deepcopy(v['timelineInfos'][0])]
            for tr in merged['timelineInfos'][0]['trackInfos']:tr['clipList']=[]
            root_meta=json.loads(raw['ProjectFolder/project_info.json'])
            root_extra=raw[f'ProjectFolder/Medias/{ROOT}/extra.json']
            root_item=copy.deepcopy(mi[ROOT])
        main=v['timelineInfos'][0]
        children=v['timelineInfos'][1:]
        comp=[(mid,x)for mid,x in mi.items()if mid!=ROOT and x.get('media_type')==1048576]
        if not rec['has_card']:
            # Factory creates a card; the outro uses only its continuous shot.
            main['trackInfos'][8]['clipList']=[c for c in main['trackInfos'][8]['clipList']if 'timelineId'not in c]
            main['trackInfos'][6]['clipList']=[];children=[];comp=[]
            for tr in main['trackInfos']:
                for c in tr['clipList']:
                    if c['type']==8:
                        c.update(tlBegin=0,tlEnd=tick(rec['duration']),outPoint=c['inPoint']+tick(rec['duration']))
                    else:c['tlBegin']-=tick(248/60);c['tlEnd']-=tick(248/60)
            used={c['sourceUuid']for tr in main['trackInfos']for c in tr['clipList']if c.get('filename')}
            v['resources']=[r for r in v['resources']if r['sourceUuid']in used]
        tidmap={53:1000+2*index,73:1001+2*index}
        mediamap={mid:guid()for mid,_ in comp}
        tlmap={x['timeline_uuid']:guid()for _,x in comp}
        pathmap={}
        aliases={'tracer_take.mp4':'video.mp4','tracer_voz.wav':'voz.wav','musica_teste.wav':'musica.wav',
                 'vinheta.wav':'vinheta.wav','tracer_retrato.jpg':'retrato.jpg','tracer_logo_3d.png':'logo.png'}
        for r in v['resources']:
            old=r['filename'];fn=Path(old).name
            fn=rec['folder']+'_'+aliases[fn];new='file:./midias/'+fn
            pathmap[old]=new;assets['midias/'+fn]=WORK/rec['folder']/'midias'/Path(old).name
        for t in [main,*children]:rewrite(t,pathmap,tidmap,mediamap,tlmap)
        for r in v['resources']:
            r['filename']=pathmap[r['filename']]
            if r['filename'].endswith('.mp4'):
                # The bundled source is a lossless 24fps remux, not the 60fps delivery.
                s=next(s for s in rec['source_probe']['streams']if s['codec_type']=='video')
                rate=Fraction(s['r_frame_rate']);duration=int(s['nb_frames'])/float(rate)
                r['mediaLength']=tick(duration)
                for vs in r['vidStreamInfo']:
                    vs.update(frameRate={'num':rate.numerator,'den':rate.denominator},
                        maxFrameRate={'num':rate.numerator,'den':rate.denominator},
                        totalFrames=int(s['nb_frames']),streamLength=tick(duration),width=s['width'],height=s['height'])
                    vs.pop('duration',None)
            mid='{'+r['sourceUuid'].upper()+'}'
            item=copy.deepcopy(mi[mid]);item.update(name=Path(r['filename']).stem,
                download_url=r['filename'].replace('file:./','./'),media_length=r['mediaLength'])
            items[mid]=item
            source={'basicInfo':{k:r[k]for k in ['streamType','fourCC','mediaLength','videoStreamCount','audioStreamCount','bitRate']if k in r},
                    'vidStreamInfos':r.get('vidStreamInfo',[]),'audStreamInfos':r.get('audStreamInfo',[])}
            native[f'ProjectFolder/Medias/{mid}/media.json']=json.dumps({'version':'1.1.5',
                'file_name':item['download_url'],'sourceInfo':source},ensure_ascii=False).encode()
        for mid,item in comp:
            new=mediamap[mid];item=copy.deepcopy(item)
            item.update(id=new,name='Vinheta '+rec['name'],timeline_uuid=tlmap[item['timeline_uuid']])
            items[new]=item
            # Match this compound's timeline UUID to its rewritten timeline.
            child=next(t for t in children if any(u['key']==11000 and textvalue(u)==item['timeline_uuid']for u in t.get('userData',[])))
            tlist=[child]
            if child['timelineId']==tidmap[53]:tlist=children
            sub=copy.deepcopy(v);sub.update(currentTimelineId=child['timelineId'],resources=v['resources'],timelineInfos=tlist)
            subs.append((new,sub))
            old_extra=f'ProjectFolder/Medias/{mid}/extra.json'
            if old_extra in raw:native[f'ProjectFolder/Medias/{new}/extra.json']=raw[old_extra]
        for i,tr in enumerate(main['trackInfos']):
            for c in tr['clipList']:
                c['tlBegin']+=tick(at);c['tlEnd']+=tick(at)
                for key in ['preTransition','postTransition']:
                    if key in c:
                        for tk in ['tlBegin','tlEnd']:
                            if tk in c[key]:c[key][tk]+=tick(at)
            merged['timelineInfos'][0]['trackInfos'][i]['clipList'].extend(tr['clipList'])
        nested.extend(children);all_resources.extend(v['resources'])
        at+=rec['duration']+(248/60 if rec['has_card']else 0)
    merged.update(resources=all_resources,timelineInfos=[merged['timelineInfos'][0],*nested])
    native[f'ProjectFolder/Medias/{ROOT}/timeline.wesproj']=json.dumps(merged,separators=(',',':')).encode()
    native[f'ProjectFolder/Medias/{ROOT}/extra.json']=root_extra
    root_item.update(name='Restante — estilo aprovado',duration=tick(at));items[ROOT]=root_item
    root_meta.update(project_file_name='Restante_Estilo_Aprovado',project_timeline_duration=tick(at),project_current_position=0,
                     proj_zip_save_path='Restante_Estilo_Aprovado.wfp',proj_cover_proj_path='',project_custom_cover=False)
    native['ProjectFolder/project_info.json']=json.dumps(root_meta,ensure_ascii=False).encode()
    for mid,sub in subs:
        native[f'ProjectFolder/Medias/{mid}/timeline.wesproj']=json.dumps(sub,separators=(',',':')).encode()
    structure='{"media_structure":{"Folder":{'+','.join('"media_item":'+json.dumps(k)for k in items if k!=ROOT)+'},"media_item":'+json.dumps(ROOT)+'},"media_items":'+json.dumps(items,ensure_ascii=False)+'}'
    native['ProjectFolder/Medias/medias_info.json']=structure.encode()
    project=OUT/'Restante_Estilo_Aprovado.wfp'
    with zipfile.ZipFile(project,'w',zipfile.ZIP_DEFLATED)as z:
        for name,data in native.items():z.writestr(name,data)
    instructions=('RESTANTE DO LONGO — ESTILO APROVADO\n\n'
        'Este projeto contém Tracer, D.Va, Mercy, Lara Croft, Peach, Sonic e o encerramento.\n'
        'Extraia o ZIP e abra Restante_Estilo_Aprovado.wfp no Filmora. Se pedir arquivos, localize o primeiro na pasta midias.\n'
        'Todos têm nomes únicos. Voz, música, retrato, logo e vídeo estão separados.\n'
        'Plugins pagos foram preservados. Text Vibrate e transições de tremido ficam desativados para seguir a amostra aprovada.\n'
        'O aplicativo Filmora não está disponível no ambiente de produção: a abertura deste WFP ainda requer validação no seu PC.\n'
        'O MP4 completo já inclui a sua edição até a 2B. Este WFP é somente o restante para facilitar os ajustes.\n'
        'Para usar no seu projeto anterior, exporte o restante ajustado e acrescente em 4:52,483.\n')
    (OUT/'LEIA_PRIMEIRO.txt').write_text(instructions)
    bundle=OUT/'Restante_Estilo_Aprovado_Filmora.zip'
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
        z.write(project,project.name);z.writestr('LEIA_PRIMEIRO.txt',instructions)
        for name,path in assets.items():
            assert path.exists(),path
            z.write(path,name,compress_type=zipfile.ZIP_STORED if path.suffix in ['.mp4','.jpg']else zipfile.ZIP_DEFLATED)
    report={'duration':at,'native_timelines':len(merged['timelineInfos']),'resources':len(all_resources),
            'media_items':len(items),'files_bundled':len(assets),'paid_plugins_preserved':True,
            'screen_shake_disabled_by_default':True,'native_application_open_test':'pending on user Filmora',
            'media_files':list(assets),'project':project.name,'bundle':bundle.name}
    (P/'projeto_filmora.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print('NATIVE_BUNDLE_READY',json.dumps(report,ensure_ascii=False),flush=True)
    return project,bundle
if __name__=='__main__':make_project()
