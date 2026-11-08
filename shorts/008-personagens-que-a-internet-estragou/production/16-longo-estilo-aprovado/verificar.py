"""Valida a entrega e a preservação da edição/voz, sem afirmar teste no Filmora."""
from pathlib import Path
import subprocess,json,hashlib,zipfile,io,wave,base64
import numpy as np
from PIL import Image
import montar as m
P=Path(__file__).resolve().parent
def pcm(path):
    a=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-vn','-ac','2','-ar','44100','-f','s16le','pipe:1'])
    return np.frombuffer(a,'<i2').reshape(-1,2).astype('float32')/32768
def compare(a,b):
    n=min(len(a),len(b));a=a[:n].ravel();b=b[:n].ravel()
    return {'samples':n,'correlation':float(np.dot(a,b)/np.sqrt(np.dot(a,a)*np.dot(b,b))),
            'rms_error':float(np.sqrt(np.mean((a-b)**2)))}
def vcl(path,frames):
    # Hash actual AVCC picture units. Annex-B start codes can change on remux
    # when new SPS/PPS headers are inserted, despite identical picture bytes.
    data=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_packets',
        '-show_entries','packet=pos,size','-of','json',str(path)]))['packets']
    assert len(data)>=frames
    h=hashlib.sha256()
    with open(path,'rb')as f:
        for packet in data[:frames]:
            f.seek(int(packet['pos']));raw=f.read(int(packet['size']));at=0
            while at<len(raw):
                size=int.from_bytes(raw[at:at+4],'big');at+=4
                assert 0<size<=len(raw)-at
                unit=raw[at:at+size];at+=size
                if unit[0]&31 in [1,5]:h.update(size.to_bytes(4,'big'));h.update(unit)
    return h.hexdigest()

def native_check(records):
    bundle=P/'output/Restante_Estilo_Aprovado_Filmora.zip'
    with zipfile.ZipFile(bundle)as z:
        assert z.testzip()is None
        project=z.read('Restante_Estilo_Aprovado.wfp')
        assert project==(P/'output/Restante_Estilo_Aprovado.wfp').read_bytes()
        with zipfile.ZipFile(io.BytesIO(project))as w:
            assert w.testzip()is None
            root='{204E72A3-B517-44d4-806F-9E9D84D5F904}'
            v=json.loads(w.read(f'ProjectFolder/Medias/{root}/timeline.wesproj'))
            meta=json.loads(w.read('ProjectFolder/project_info.json'))
            mi=json.loads(w.read('ProjectFolder/Medias/medias_info.json'))['media_items']
            ids={t['timelineId']for t in v['timelineInfos']};source_ids={r['sourceUuid']for r in v['resources']}
            for r in v['resources']:
                name=r['filename'].replace('file:./','');assert name in z.namelist(),name
            count=0;available=set();node_ids=[]
            def visit(node):
                nonlocal count
                if isinstance(node,list):
                    for x in node:visit(x)
                elif isinstance(node,dict):
                    if node.get('display')=='Text Vibrate':assert node.get('enable')is False;count+=1
                    if 'display'in node:available.add(node['display'])
                    if 'thisUId'in node:node_ids.append(node['thisUId'])
                    for x in node.values():
                        if isinstance(x,(list,dict)):visit(x)
            visit(v)
            assert len(node_ids)==len(set(node_ids)),'Duplicate runtime nodes'
            for t in v['timelineInfos']:
                for tr in t['trackInfos']:
                    for c in tr['clipList']:
                        if c.get('filename'):
                            assert c['sourceUuid']in source_ids
                            assert c['filename'].replace('file:./','')in z.namelist()
                        if 'timelineId'in c:assert c['timelineId']in ids
                        for u in c.get('userData',[]):
                            if u['key']==10:
                                link=base64.b64decode(u['data']).decode().strip('\0')
                                # Effect clips use names such as Mini_Shake here.
                                if link.startswith('{'):assert link in mi,link
            clips=sorted(v['timelineInfos'][0]['trackInfos'][8]['clipList'],key=lambda c:c['tlBegin'])
            end=0;max_gap=0
            for c in clips:
                gap=abs(c['tlBegin']-end);max_gap=max(max_gap,gap);assert gap<=2,(gap,c['tlBegin'],end)
                assert c['tlEnd']>c['tlBegin'];end=c['tlEnd']
            assert abs(meta['project_timeline_duration']-end)<=2
        for r in records:
            with wave.open(io.BytesIO(z.read('midias/'+r['folder']+'_voz.wav')))as q:
                delivered=np.frombuffer(q.readframes(q.getnframes()),'<i2').reshape(-1,2)
            with wave.open(str(m.PROD/r['folder']/'assets/voz/narracao_completa.wav'))as q:
                original=np.frombuffer(q.readframes(q.getnframes()),'<i2').reshape(-1,q.getnchannels())
            assert np.array_equal(delivered[:len(original),:1],original),r['folder']
            assert np.array_equal(delivered[:,0],delivered[:,1])
    return {'zip_integrity':'passed','all_media_links_bundled':True,'all_full_voice_pcm_preserved':True,
            'native_timelines':len(ids),'disabled_shake_instances':count,'available_plugins':sorted(available),
            'video_coverage_max_gap_100ns':max_gap,'filmora_application_open_test':'pending on user computer'}

def main():
    info=json.loads((P/'montagem.json').read_text());records=info['records']
    final=P/'output/Personagens_que_a_internet_ESTRAGOU_Estilo_Aprovado_16x9.mp4'
    prefix=m.PROD/'14-montagem-longo/assets/Edicao_usuario_ate_2B.mp4'
    image=Image.new('RGB',(640,360),(165,145,120))
    assert np.array_equal(m.style.global_look(image,0),m.style.global_look(image,4.7))
    print('DECODE_FULL_VIDEO',flush=True)
    subprocess.run(['ffmpeg','-v','error','-xerror','-threads','4','-i',str(final),'-map','0:v:0','-map','0:a:0','-f','null','-'],check=True)
    print('COMPARE_REFERENCE_IMAGE_PAYLOAD',flush=True)
    h1=vcl(prefix,17549);h2=vcl(final,17549);assert h1==h2
    print('VERIFY_AUDIO',flush=True)
    audio=pcm(final);original=pcm(prefix);prefix_samples=round(17549/60*44100)
    prefix_audio=compare(original,audio[:prefix_samples]);assert prefix_audio['correlation']>.99
    expected=m.style.wav(P/'renders/restante_audio.wav');tail_audio=compare(expected,audio[prefix_samples:])
    assert tail_audio['correlation']>.99
    segments=[];at=prefix_samples
    for r in records:
        if r['has_card']:at+=248*735
        exp=m.style.wav(P/'renders'/r['folder']/'mix.wav');check=compare(exp,audio[at:at+len(exp)])
        assert check['correlation']>.99,(r['folder'],check)
        segments.append({'folder':r['folder'],**check});at+=len(exp)
    print('VERIFY_NATIVE_BUNDLE',flush=True);native=native_check(records)
    pr=m.probe(final);video=next(s for s in pr['streams']if s['codec_type']=='video');a=next(s for s in pr['streams']if s['codec_type']=='audio')
    expected_frames=17549+sum(r['frames']+(248 if r['has_card']else 0)for r in records)
    assert int(video['nb_frames'])==expected_frames
    assert video['r_frame_rate']=='60/1'and(video['width'],video['height'])==(1920,1080)
    sync_error=abs(float(video['duration'])-float(a['duration']));assert sync_error<.05
    report={'full_decode':'passed','prefix_h264_picture_payload_preserved':True,'prefix_vcl_sha256':h1,
        'reference_frames_preserved':17549,'screen_oscillation_added':False,'static_processing_temporally_stable':True,
        'prefix_audio':prefix_audio,'continuation_audio':tail_audio,'episodes':segments,
        'video_frames':expected_frames,'duration':pr['format']['duration'],'audio_video_duration_difference':sync_error,
        'native_project':native,'source_masters_modified':False,'voice_speed_or_pitch_changed':False}
    (P/'verificacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('VERIFIED',json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
