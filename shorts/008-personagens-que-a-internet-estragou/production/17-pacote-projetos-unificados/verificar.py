from pathlib import Path
import json,zipfile,io,hashlib,copy
import empacotar as p

def main():
    package=p.OUT/'Seus_Projetos_e_Continuacao_Com_Midias.zip'
    source=p.readzip(p.ORIGINAL);tail=p.readzip(p.CONTINUATION)
    manifest=json.loads((p.P/'manifesto.json').read_text())
    with zipfile.ZipFile(package)as z:
        a=z.read('01_Seu_projeto_original.wfp');b=z.read('02_Continuacao.wfp')
        assert hashlib.sha256(a).hexdigest()==p.sha_file(p.ORIGINAL)
        assert hashlib.sha256(b).hexdigest()==p.sha_file(p.CONTINUATION)
        merged=z.read('03_Video_Completo_Unificado.wfp')
        assert hashlib.sha256(merged).hexdigest()==p.sha_file(p.OUT/'03_Video_Completo_Unificado.wfp')
        assert json.loads(z.read('MANIFESTO.json'))==manifest
        for name,expected in manifest['media_sha256'].items():
            h=hashlib.sha256()
            with z.open(name)as f:
                while data:=f.read(1024*1024):h.update(data)
            assert h.hexdigest()==expected,name
        with zipfile.ZipFile(io.BytesIO(merged))as w:
            assert w.testzip()is None
            graph=json.loads(w.read(p.TL));meta=json.loads(w.read('ProjectFolder/project_info.json'))
            items=json.loads(w.read(p.MI))['media_items']
        old=json.loads(source[p.TL]);new=json.loads(tail[p.TL])
        oldmeta=json.loads(source['ProjectFolder/project_info.json'])
        newmeta=json.loads(tail['ProjectFolder/project_info.json'])
        prefix=oldmeta['project_timeline_duration']
        assert meta['project_timeline_duration']==prefix+newmeta['project_timeline_duration']
        tids=[t['timelineId']for t in graph['timelineInfos']]
        assert len(tids)==len(set(tids))==40
        assert graph['serialNumber']>max(tids)
        mapping={}
        for r in manifest['original_references']:
            if r['available']:
                mapping[r['reference']]='./'+r['package_path']
                mapping['file:/'+r['reference']]='file:./'+r['package_path']
        for oldtrack,newtrack,combined in zip(old['timelineInfos'][0]['trackInfos'],new['timelineInfos'][0]['trackInfos'],graph['timelineInfos'][0]['trackInfos']):
            n=len(oldtrack['clipList'])
            assert combined['clipList'][:n]==p.replace_paths(oldtrack['clipList'],mapping)
            expected=[]
            for clip in newtrack['clipList']:
                c=copy.deepcopy(clip);c['tlBegin']+=prefix;c['tlEnd']+=prefix
                for key in ['preTransition','postTransition']:
                    if key in c:
                        for tk in ['tlBegin','tlEnd']:
                            if tk in c[key]:c[key][tk]+=prefix
                expected.append(c)
            assert combined['clipList'][n:]==expected
        assert graph['timelineInfos'][1:len(old['timelineInfos'])]==p.replace_paths(old['timelineInfos'][1:],mapping)
        assert graph['timelineInfos'][len(old['timelineInfos']):]==new['timelineInfos'][1:]
        external=[];bundled=0
        for resource in graph['resources']:
            name=resource['filename']
            if name.startswith('file:./'):
                assert name.removeprefix('file:./')in z.namelist();bundled+=1
            else:external.append(name.removeprefix('file:').lstrip('/'))
        missing={r['reference']for r in manifest['original_references']if not r['available']}
        assert set(external)==missing
    report={'archive_crc_and_media_sha256':'passed','original_project_byte_preserved':True,
        'continuation_project_byte_preserved':True,'original_edit_clips_preserved_except_relinked_paths':True,
        'original_child_timelines_preserved':True,'continuation_clips_shifted_by_original_duration':True,
        'timelines':len(tids),'media_files_packaged':len(manifest['media_sha256']),
        'unified_active_resources_bundled':bundled,'external_original_resources_not_received':len(external),
        'fully_portable':False,'filmora_application_open_test':'pending on user computer',
        'duration_seconds':meta['project_timeline_duration']/1e7,'package_bytes':package.stat().st_size}
    (p.P/'verificacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print('VERIFIED',json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
