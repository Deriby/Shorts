"""Verifica o áudio importável, a montagem e os dois WFPs antes de empacotar."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import hashlib
import json
import subprocess
import sys
import wave

import cv2
import numpy as np
import soundfile as sf

from revisar import F,M,OUT,P,TITLE,TL,W,H,FPS,SR,write_json
from projeto import BASE,EXTRA,LIB,META,EFFECTS,field,main_timeline,clips,film


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_wfp(file, expects_stock, scale_dB, plan):
    with ZipFile(file) as z:
        assert z.testzip() is None
        d, library, extra, meta = (json.loads(z.read(n)) for n in (TL,LIB,EXTRA,META))
        resources = {r['sourceUuid']:r for r in d['resources']}
        items = library['media_items']
        timeline = main_timeline(d)
        root = items[film.ROOT]
        assert root['timeline_uuid']==field(timeline,11000).decode() and root['duration']==meta['project_timeline_duration']
        assert meta['timeline_mediaId']==film.ROOT
        assert (timeline['resolutionWidth'],timeline['resolutionHeight'],timeline['frameRate']['num'])==(W,H,FPS)
        assert meta['project_timeline_duration']==film.ticks(plan['duration'])
        count, audio, unbound = 0, set(), []
        fx_seen = {}
        for t in timeline['trackInfos']:
            cs=t['clipList']
            assert all(a['tlEnd']<=b['tlBegin'] for a,b in zip(cs,cs[1:]))
            for c in cs:
                assert 0<=c['tlBegin']<c['tlEnd']<=meta['project_timeline_duration']
                assert abs((c['tlEnd']-c['tlBegin'])-(c['outPoint']-c['inPoint']))<=1
                if c['type']==8:
                    effect=next(fx['display'] for fx in film.effects(c) if fx['display'] in EFFECTS)
                    fx_seen[effect]=fx_seen.get(effect,0)+1
                    continue
                r=resources[c['sourceUuid']]
                if c['filename'].endswith('.cof'):
                    assert c['filename']==r['filename'] and not c['filename'].startswith('file:')
                    cfg=json.loads(field(c,12))
                    assert cfg['id']==9221778 and 'geometric_shape_patterns' in cfg['name']
                    assert 'AdjustColor' in [fx['display'] for fx in film.effects(c)]
                    unbound.append(c['filename'])
                    continue
                c_id, media_id = (field(c,k).decode() for k in (3,10))
                assert extra['mediaClipsMapInfo'][c_id]['mediaId']==media_id
                library_item=items[media_id]
                relative=c['filename'].removeprefix('file:')
                assert relative==r['filename'].removeprefix('file:')==library_item['download_url']
                name=Path(relative).name
                assert relative=='./midias/'+name
                data=(M/name).read_bytes()
                assert hashlib.md5(data).hexdigest()==library_item['src_md5']
                assert c['outPoint'] <= r['mediaLength']+1 or not r['mediaLength']
                speed=json.loads(c['speed']['speedParam'])
                assert not c['speed']['reverse'] and all(k['_value']==1 for k in speed['keyframeSets'])
                cache=json.loads(z.read(f'{BASE}{media_id}/media.json'))['sourceInfo']
                count+=1
                if c['type']==2:
                    assert library_item['media_type']==4 and r['fourCC']==7758199 and r['audioStreamCount']==1
                    sri=r['audStreamInfo'][0]
                    assert (sri['sampleRate'],sri['bitDepth'],sri['channels'],sri['fourCC'])==(48000,16,2,541934416)
                    assert cache['audStreamInfos'][0]==sri
                    assert 'volumeKeyframe' in c and 'audioDuckingframe' in c
                    follow=next(ch for ch in c['effectChainList'] if ch['name']=='BasicFollow')
                    names={fx['display']:fx for fx in follow['effectList']}
                    assert {'volume','ducking','fade','change_channel'}<=names.keys()
                    gain=names['volume']['paramList'][0]['fxParam']['unValue']
                    assert gain==scale_dB[name]
                    audio.add(name)
        assert len(unbound)==(3 if expects_stock else 0)
        assert fx_seen=={name:len(ranges) for name,ranges in EFFECTS.items()}
        assert len(audio)==len(scale_dB)
        assert len(set(c['thisUId'] for c in clips(timeline)))==len(clips(timeline))
        return dict(file=file.name,sha256=sha(file),local_bindings=count,
                    native_stock_background=expects_stock,effects=fx_seen,audio=sorted(audio),
                    native_app_tested=False)


def output(temp,ted,sonic):
    plan=json.loads((P/'timeline.json').read_text())
    gain={e['file']:e['mix_gain_db'] for e in plan['events'] if 'mix_gain_db' in e}
    checks={}
    for file in gain:
        with wave.open(str(M/file),'rb') as wav:
            assert (wav.getsampwidth(),wav.getnchannels(),wav.getframerate())==(2,2,48000)
        sound,_=sf.read(M/file)
        energy=float(np.sqrt(np.mean(sound**2)))
        assert 0.001 < energy and np.abs(sound).max() < 1
        rms_db=20*np.log10(energy)
        if file.startswith(('Whoosh_','Swoosh_')):
            assert rms_db+gain[file]>-34, (file,rms_db,gain[file])
        checks[file]=dict(samples=len(sound),rms_dbfs=round(rms_db,2),timeline_rms_dbfs=round(rms_db+gain[file],2))
    voice,_=sf.read(F/'Voz_Original.wav')
    voice_pcm,_=sf.read(M/'Voz_Editavel_PCM16.wav')
    assert sha(F/'Voz_Original.wav')==plan['voice_sha256']
    assert voice_pcm.shape==(len(voice),2) and np.max(np.abs(voice_pcm-voice[:,None]))<2**-15
    assert len(voice)==1883435
    stock=F/(TITLE+'_9x16.wfp')
    portable=F/(TITLE+'_Fundo_Local_9x16.wfp')
    projects=[verify_wfp(stock,True,gain,plan),verify_wfp(portable,False,gain,plan)]

    mp4=OUT/(TITLE+'_9x16.mp4')
    probe=film.probe(mp4)
    video=next(st for st in probe['streams'] if st['codec_type']=='video')
    assert (video['width'],video['height'],video['r_frame_rate'],int(video['nb_frames']))==(W,H,'30/1',1178)
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(mp4),'-f','null','-'],check=True)
    out=np.frombuffer(subprocess.check_output(
        ['ffmpeg','-v','error','-i',str(mp4),'-vn','-f','f32le','-']),dtype='<f4').reshape(-1,2)
    mix,rate=sf.read(temp/'mix.wav')
    assert rate==SR and len(out)>=len(mix)
    match=float(np.corrcoef(out[:len(mix)].ravel(),mix.ravel())[0,1])
    assert match>.995 and np.max(np.abs(out))<.98

    cap=cv2.VideoCapture(str(mp4))
    captures=[]
    for hold in plan['realistic_holds']:
        begin,end=hold['visible']
        assert end-begin>=1.45
        name=f'Reacao_{hold["name"]}.png'
        target=cv2.imread(str(M/name))
        event=next(e for e in plan['events'] if e['file']==name)
        metrics=[]
        for t in (begin+.12,(begin+end)/2,end-.12):
            sample=round(t*FPS)
            cap.set(cv2.CAP_PROP_POS_FRAMES,sample)
            ok,actual=cap.read()
            assert ok
            a=cv2.resize(actual,(120,214)).astype(float).ravel()
            _, x, y, sx, sy, angle = event['keys'][sample-round(begin*FPS)]
            assert angle == 0
            matrix=np.array([[sx,0,x*W-sx*W/2],[0,sy,y*H-sy*H/2]])
            expected=cv2.warpAffine(target,matrix,(W,H))
            b=cv2.resize(expected,(120,214)).astype(float).ravel()
            similarity=float(np.corrcoef(a,b)[0,1])
            assert similarity>.985, (name,t,similarity)
            metrics.append(round(similarity,4))
        captures.append(dict(**hold,correlation=metrics))
    cap.release()
    for e in plan['events']:
        if 'saída animada' in e['reason']:
            p=e['keys'][-1]
            assert any(n<-.4 or n>1.4 for n in p[1:3])

    report=dict(mp4=dict(file=mp4.name,sha256=sha(mp4),frames=1178,seconds=plan['duration'],
                         size=[W,H],fps=FPS,decoded=True,audio_correlation=match),
                projects=projects,holds=captures,verified_pcm16=checks,voice_samples=len(voice),
                source_refs={'ted':sha(ted),'sonic':sha(sonic)})
    report_file=P/'validacao.json'
    write_json(report_file,report)
    readme=F/'LEIA_PRIMEIRO.txt'
    readme.write_text(
        'TED virou DESENHO · Revisão 2\n\n'
        'Extraia o ZIP inteiro antes de abrir o WFP. Mantenha midias junto ao projeto.\n\n'
        'TED_virou_DESENHO_R2_9x16.wfp usa seu fundo geométrico do Filmora, com os ajustes\n'
        'do arquivo que você enviou. Ele depende desse fundo instalado no catálogo.\n'
        'TED_virou_DESENHO_R2_Fundo_Local_9x16.wfp usa o fundo azul/rosa que acompanha\n'
        'a prévia MP4. Use essa versão caso o fundo de catálogo não seja encontrado.\n\n'
        'Whoosh, swoosh, voz, trilha curta, clique, meme e impacto têm faixas de áudio\n'
        'independentes em WAV PCM de 16 bits, estéreo, 48 kHz, com volume e ducking do Filmora.\n'
        'Ducking inicia desligado. O WAV original está na pasta Filmora. O sinal de abertura\n'
        'e a batida grave foram recriados porque os binários de catálogo não vieram no envio.\n\n'
        'O MP4 usa curvas e composição locais. As transições e os efeitos proprietários\n'
        'como Glow, Text Vibrate e Grunge_Jitter estão no WFP. A abertura e a interface\n'
        'do Filmora ainda precisam ser verificadas no aplicativo.\n',
        encoding='utf-8',
    )
    names=sorted({e['file'] for e in plan['events']})
    files=[stock,portable,readme,F/'Voz_Original.wav',*(M/name for name in names)]
    bundle=OUT/(TITLE+'_Filmora_Completo.zip')
    with ZipFile(bundle,'w',ZIP_DEFLATED,compresslevel=4) as z:
        for path in files:
            z.write(path,'Filmora/'+path.relative_to(F).as_posix())
        z.write(report_file,report_file.name)
    with ZipFile(bundle) as z:
        assert z.testzip() is None
        for path in files:
            assert z.read('Filmora/'+path.relative_to(F).as_posix())==path.read_bytes()
    manifest=dict(file=bundle.name,sha256=sha(bundle),bytes=bundle.stat().st_size,
                  local_media=names,wfp_variants=[stock.name,portable.name],verified=True)
    write_json(P/'pacote.json',manifest)
    print(json.dumps({**report,'bundle':manifest['sha256']},ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':
    output(*map(Path,sys.argv[1:]))
