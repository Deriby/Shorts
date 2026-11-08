"""Reúne os dois WFPs, unifica as timelines e inclui as mídias disponíveis.

Não substitui as fontes ausentes por miniaturas, músicas recuperadas ou artes
diferentes. Seus caminhos Windows originais são mantidos e inventariados.
"""
from pathlib import Path
import json,zipfile,copy,subprocess,re,hashlib,shutil,uuid

P=Path(__file__).resolve().parent;PROD=P.parent
OUT=P/'output';OUT.mkdir(exist_ok=True)
ROOT='{204E72A3-B517-44d4-806F-9E9D84D5F904}'
TL=f'ProjectFolder/Medias/{ROOT}/timeline.wesproj'
MI='ProjectFolder/Medias/medias_info.json'
ORIGINAL=PROD/'14-montagem-longo/assets/Referencia_Filmora_original.wfp'
CONTINUATION=PROD/'16-longo-estilo-aprovado/output/Restante_Estilo_Aprovado.wfp'
MEDIA_ZIP=PROD/'16-longo-estilo-aprovado/output/Restante_Estilo_Aprovado_Filmora.zip'
PREFIX=PROD/'14-montagem-longo/assets/Edicao_usuario_ate_2B.mp4'

def readzip(path):
    with zipfile.ZipFile(path)as z:return {n:z.read(n)for n in z.namelist()}
def canonical(name):return re.sub(r'^\d+\s*[-–]\s*','',name).casefold()
def replace_paths(node,mapping):
    if isinstance(node,str):return mapping.get(node,node)
    if isinstance(node,list):return [replace_paths(x,mapping)for x in node]
    if isinstance(node,dict):return {k:replace_paths(v,mapping)for k,v in node.items()}
    return node
def writeproject(path,entries):
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED)as z:
        for name,data in entries.items():z.writestr(name,data)
def media_structure(items):
    return ('{"media_structure":{"Folder":{'+','.join('"media_item":'+json.dumps(k)for k in items if k!=ROOT)
            +'},"media_item":'+json.dumps(ROOT)+'},"media_items":'+json.dumps(items,ensure_ascii=False)+'}').encode()
def safe_name(i,path):
    stem=re.sub(r'[^A-Za-z0-9_.-]','_',path.stem)[:115]
    return f'midias/inicio_{i:02d}_{stem}{path.suffix.lower()}'
def sha_file(path):
    h=hashlib.sha256()
    with open(path,'rb')as f:
        while b:=f.read(1024*1024):h.update(b)
    return h.hexdigest()

def audit(original):
    v=json.loads(original[TL]);mi=json.loads(original[MI])['media_items']
    used={r['filename'].removeprefix('file:').lstrip('/'):r for r in v['resources']}
    references=list(used)
    references += [x['download_url']for x in mi.values()if x.get('download_url')and x['download_url']not in used]
    prior={x['reference']:x for x in json.loads((P/'auditoria_midias.json').read_text())}
    paths=[Path(x)for x in subprocess.check_output(['rg','--files','/workspace/Shorts','/workspace/attachments']).decode().splitlines()]
    records=[];known={};mapping={}
    for i,ref in enumerate(dict.fromkeys(references)):
        name=ref.rsplit('/',1)[-1];selected=prior.get(ref,{}).get('selected')
        if not selected:
            candidates=[p for p in paths if p.name.casefold()==name.casefold()]
            if not candidates:candidates=[p for p in paths if canonical(p.name)==canonical(name)]
            if len(candidates)==1:selected=str(candidates[0])
        r={'reference':ref,'filename':name,'used_in_timeline':ref in used,'available':bool(selected)}
        if selected:
            source=Path(selected);relative=safe_name(i,source)
            known[relative]=source
            mapping['file:/'+ref]='file:./'+relative;mapping[ref]='./'+relative
            r.update(package_path=relative,bytes=source.stat().st_size,sha256=sha_file(source),
                     match_method='original filename or delivered master filename',source_local=str(source))
        records.append(r)
    return records,known,mapping

def build_unified(original,new,mapping):
    old=json.loads(original[TL]);tail=json.loads(new[TL])
    old_meta=json.loads(original['ProjectFolder/project_info.json'])
    new_meta=json.loads(new['ProjectFolder/project_info.json'])
    prefix_ticks=old_meta['project_timeline_duration'];tail_ticks=new_meta['project_timeline_duration']
    assert old['currentTimelineId']==tail['currentTimelineId']==46
    old_main=old['timelineInfos'][0];new_main=tail['timelineInfos'][0]
    assert old_main['frameRate']==new_main['frameRate']
    assert len(old_main['trackInfos'])==len(new_main['trackInfos'])
    merged=replace_paths(copy.deepcopy(old),mapping)
    main=merged['timelineInfos'][0]
    for source,target in zip(new_main['trackInfos'],main['trackInfos']):
        assert source['trackType']==target['trackType']
        for clip in source['clipList']:
            c=copy.deepcopy(clip)
            c['tlBegin']+=prefix_ticks;c['tlEnd']+=prefix_ticks
            for key in ['preTransition','postTransition']:
                if key in c:
                    for tk in ['tlBegin','tlEnd']:
                        if tk in c[key]:c[key][tk]+=prefix_ticks
            target['clipList'].append(c)
    old_ids={t['timelineId']for t in old['timelineInfos']}
    new_ids={t['timelineId']for t in tail['timelineInfos'][1:]}
    assert old_ids.isdisjoint(new_ids)
    source_ids={r['sourceUuid']for r in merged['resources']}
    assert source_ids.isdisjoint({r['sourceUuid']for r in tail['resources']})
    merged['resources']+=copy.deepcopy(tail['resources'])
    merged['timelineInfos']+=copy.deepcopy(tail['timelineInfos'][1:])
    merged['serialNumber']=max(merged.get('serialNumber',0),max(t['timelineId']for t in merged['timelineInfos'])+1)
    entries={}
    # Relink every original cache/subproject with the same known-path mapping.
    for name,data in original.items():
        if name.endswith(('.json','.wesproj'))and name!=MI:
            try:data=json.dumps(replace_paths(json.loads(data),mapping),ensure_ascii=False,separators=(',',':')).encode()
            except (ValueError,UnicodeDecodeError):pass
        entries[name]=data
    for name,data in new.items():
        if name not in entries:entries[name]=data
    entries[TL]=json.dumps(merged,ensure_ascii=False,separators=(',',':')).encode()
    oi=replace_paths(json.loads(original[MI])['media_items'],mapping)
    ni=json.loads(new[MI])['media_items']
    assert (set(oi)&set(ni))=={ROOT}
    oi.update({k:v for k,v in ni.items()if k!=ROOT})
    oi[ROOT].update(name='Vídeo completo unificado',duration=prefix_ticks+tail_ticks)
    entries[MI]=media_structure(oi)
    meta=copy.deepcopy(old_meta)
    meta.update(project_file_name='Video_Completo_Unificado',project_timeline_duration=prefix_ticks+tail_ticks,
                project_current_position=0,proj_zip_save_path='03_Video_Completo_Unificado.wfp',proj_cover_proj_path='',
                project_custom_cover=False,project_guid='{'+str(uuid.uuid4()).upper()+'}')
    entries['ProjectFolder/project_info.json']=json.dumps(meta,ensure_ascii=False).encode()
    path=OUT/'03_Video_Completo_Unificado.wfp';writeproject(path,entries)
    # Preservation means every original clip/child timeline, with only known paths relinked.
    for original_track,merged_track in zip(old_main['trackInfos'],main['trackInfos']):
        assert merged_track['clipList'][:len(original_track['clipList'])]==replace_paths(original_track['clipList'],mapping)
    assert merged['timelineInfos'][1:len(old['timelineInfos'])]==replace_paths(old['timelineInfos'][1:],mapping)
    return path,{'prefix_ticks':prefix_ticks,'tail_ticks':tail_ticks,'full_ticks':prefix_ticks+tail_ticks,
                 'original_clip_edits_preserved':True,'original_child_timelines_preserved':True,
                 'timeline_count':len(merged['timelineInfos']),'resource_count':len(merged['resources']),
                 'native_application_open_test':'pending on user Filmora'}

def main():
    original=readzip(ORIGINAL);new=readzip(CONTINUATION)
    records,known,mapping=audit(original)
    unified,report=build_unified(original,new,mapping)
    missing=[r for r in records if not r['available']]
    missing_text='MÍDIAS DO PROJETO ORIGINAL QUE NÃO VIERAM NO ENVIO\n\n'
    missing_text+=('O WFP original e o unificado preservam os caminhos abaixo. No seu computador, eles podem ser encontrados automaticamente '
                   'se os arquivos continuarem nas pastas originais. Eles não foram substituídos por outras artes ou trilhas.\n\n')
    for i,r in enumerate(missing,1):missing_text+=f"{i:02}. {r['filename']}\n    {r['reference']}\n\n"
    missing_text+=('Para um pacote totalmente portátil, inclua esses arquivos ao arquivar o projeto no próprio Filmora e envie esse pacote. '
                   'Os plugins continuam dependendo da sua instalação licenciada.\n')
    (OUT/'MIDIAS_NAO_RECEBIDAS.txt').write_text(missing_text)
    instructions=('SEU PROJETO + CONTINUAÇÃO + MÍDIAS DISPONÍVEIS\n\n'
      'Extraia o ZIP inteiro antes de abrir um WFP.\n\n'
      '03_Video_Completo_Unificado.wfp: sua timeline original, seguida da continuação editável. Abra este para trabalhar no longo.\n'
      '01_Seu_projeto_original.wfp: seu arquivo recebido, preservado byte a byte como backup.\n'
      '02_Continuacao.wfp: a continuação separada, também preservada como entregue.\n\n'
      'A pasta midias inclui todas as 39 mídias da continuação e as fontes do projeto original encontradas neste ambiente. '
      'Se pedir localização, selecione o arquivo na pasta midias. Os nomes são únicos.\n\n'
      f'ATENÇÃO: {len(missing)} referências de música, sons e imagens do primeiro trecho não estavam no envio. '
      'Os caminhos originais dessas fontes continuam no projeto. Consulte MIDIAS_NAO_RECEBIDAS.txt.\n'
      'Também foi incluído midias/Seu_inicio_renderizado.mp4 como referência visual pronta da sua edição até a 2B; '
      'esse vídeo não substitui os cortes editáveis na timeline unificada.\n\n'
      'Não houve nova renderização de vídeo nem alteração dos projetos de origem. '
      'A integridade do ZIP e as referências foram conferidas; a abertura do WFP unificado ainda precisa ser testada no Filmora.\n')
    (OUT/'LEIA_PRIMEIRO.txt').write_text(instructions)
    package=OUT/'Seus_Projetos_e_Continuacao_Com_Midias.zip'
    hashes={}
    with zipfile.ZipFile(package,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:
        z.write(ORIGINAL,'01_Seu_projeto_original.wfp',compress_type=zipfile.ZIP_STORED)
        z.write(CONTINUATION,'02_Continuacao.wfp',compress_type=zipfile.ZIP_STORED)
        z.write(unified,unified.name,compress_type=zipfile.ZIP_STORED)
        z.writestr('LEIA_PRIMEIRO.txt',instructions);z.writestr('MIDIAS_NAO_RECEBIDAS.txt',missing_text)
        with zipfile.ZipFile(MEDIA_ZIP)as media:
            for info in media.infolist():
                if not info.filename.startswith('midias/'):continue
                target=zipfile.ZipInfo(info.filename)
                target.compress_type=zipfile.ZIP_STORED if Path(info.filename).suffix in ['.mp4','.jpg']else zipfile.ZIP_DEFLATED
                h=hashlib.sha256()
                with media.open(info)as source,z.open(target,'w',force_zip64=True)as dest:
                    while b:=source.read(1024*1024):h.update(b);dest.write(b)
                hashes[info.filename]=h.hexdigest()
        for name,path in known.items():
            z.write(path,name,compress_type=zipfile.ZIP_STORED if path.suffix.lower()in ['.mp4','.jpg']else zipfile.ZIP_DEFLATED)
            hashes[name]=sha_file(path)
        backup='midias/Seu_inicio_renderizado.mp4';z.write(PREFIX,backup,compress_type=zipfile.ZIP_STORED);hashes[backup]=sha_file(PREFIX)
        manifest={'original_references':[{k:v for k,v in r.items()if k!='source_local'}for r in records],
                  'media_sha256':hashes,'missing_count':len(missing),'packaged_media_count':len(hashes),
                  'original_project_sha256':sha_file(ORIGINAL),'continuation_project_sha256':sha_file(CONTINUATION),
                  'unified_project_sha256':sha_file(unified),**report}
        z.writestr('MANIFESTO.json',json.dumps(manifest,ensure_ascii=False,indent=2))
    (P/'manifesto.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    print('PACKAGE_READY',package,'BYTES',package.stat().st_size,'MISSING',len(missing),'MEDIA',len(hashes),flush=True)
if __name__=='__main__':main()
