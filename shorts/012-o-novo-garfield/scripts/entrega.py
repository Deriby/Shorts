"""Empacota o editor e confere a exportação horizontal contra a mixagem."""
from pathlib import Path
import json
import subprocess
import sys
import wave
import zipfile

import cv2
import numpy as np
import soundfile as sf

from garfield import W,H,FPS,SR,F,M,OUT,P,TITLE,sha
import montar_filmora as film


def plan():
    return json.loads((P/'timeline.json').read_text())


def package():
    recipe=plan()
    project=F/(TITLE+'_16x9.wfp')
    original=F/'Voz_Original.wav'
    native=P/'validacao_filmora.json'
    report=json.loads(native.read_text())
    media=sorted({event['file'] for event in recipe['events']})
    assert sha(project)==report['sha256']
    assert sha(original)==recipe['voice_sha256']
    assert {p.name for p in M.iterdir()}==set(media)

    notes=F/'LEIA_PRIMEIRO.txt'
    notes.write_text(
        'O NOVO GARFIELD · MASSACOTE TUBE\n\n'
        'Extraia o ZIP inteiro e abra O_Novo_Garfield_16x9.wfp com a pasta midias ao lado.\n'
        'O vídeo está em 1920 × 1080, 30 fps. A voz completa está na timeline em WAV PCM de\n'
        '16 bits, com ganho de mixagem no projeto. Voz_Original.wav é a gravação recebida.\n'
        'Avatar 2D, fontes, painéis, trilha, sons e efeitos estão em faixas separadas.\n'
        'A estrutura e as referências do WFP passaram na conferência. A abertura no Filmora\n'
        'e a renderização dos efeitos proprietários ainda dependem do aplicativo.\n',encoding='utf-8')
    bundle=OUT/(TITLE+'_Filmora.zip')
    members=[project,original,notes,*[M/name for name in media]]
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
        for p in members:
            z.write(p,'Filmora/'+p.relative_to(F).as_posix())
        z.write(native,native.name)
    with zipfile.ZipFile(bundle) as z:
        assert z.testzip() is None
        for p in members:
            assert z.read('Filmora/'+p.relative_to(F).as_posix())==p.read_bytes()
    receipt=dict(name=bundle.name,sha256=sha(bundle),bytes=bundle.stat().st_size,media_count=len(media))
    (P/'pacote.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(receipt,flush=True)


def master(temp, original_zip):
    recipe=plan()
    original=F/'Voz_Original.wav'
    assert sha(original)==recipe['voice_sha256']
    with zipfile.ZipFile(original_zip) as source:
        name=next(k for k in source.namelist() if k.endswith('/1 - VOZ.wav'))
        assert source.read(name)==original.read_bytes()

    mp4=OUT/(TITLE+'_9x16.mp4')
    if not mp4.exists():
        mp4=OUT/(TITLE+'_16x9.mp4')
    exported=film.probe(mp4)
    video=next(s for s in exported['streams'] if s['codec_type']=='video')
    audio=next(s for s in exported['streams'] if s['codec_type']=='audio')
    assert (video['width'],video['height'],video['r_frame_rate'],int(video['nb_frames']))==(W,H,'30/1',recipe['frames'])
    assert (int(audio['sample_rate']),audio['channels'])==(SR,2)
    assert recipe['duration']<180
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(mp4),'-f','null','-'],check=True)
    mix,sr=sf.read(temp/'mix.wav',dtype='float32')
    sound=np.frombuffer(subprocess.check_output([
         'ffmpeg','-v','error','-i',str(mp4),'-vn','-f','f32le','-',
    ]),dtype='<f4').reshape(-1,2)
    assert sr==SR and len(sound)>=len(mix)
    corr=float(np.corrcoef(sound[:len(mix)].ravel(),mix.ravel())[0,1])
    realpeak=float(np.max(np.abs(sound)))
    assert corr>.995 and realpeak<.97
    voice,mic=sf.read(original,dtype='float64')
    edited,project_rate=sf.read(M/'Voz_PCM16.wav',dtype='float64')
    assert len(voice)==7115358 and mic==project_rate==SR
    assert edited.shape==(len(voice),2) and np.max(np.abs(edited-voice[:,None]))<=2**-15
    voice_event=next(e for e in recipe['events'] if e['track']=='voz')
    assert round((voice_event['end']-voice_event['start'])*SR)==len(voice)

    sfx={}
    for name in sorted({e['file'] for e in recipe['events'] if 'mix_gain_db' in e}):
        with wave.open(str(M/name),'rb') as wav:
            assert (wav.getframerate(),wav.getnchannels(),wav.getsampwidth())==(48000,2,2)
        samples,_=sf.read(M/name)
        assert .001<float(np.sqrt(np.mean(samples**2)))<.6
        sfx[name]=len(samples)

    motion={}
    for shot in {e['file'] for e in recipe['events'] if e['file'].endswith('.mp4')}:
        cap=cv2.VideoCapture(str(M/shot))
        count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        seen=[]
        for j in (.24,.53,.72):
            cap.set(cv2.CAP_PROP_POS_FRAMES,round(j*count))
            ok,im=cap.read()
            assert ok
            seen.append(cv2.resize(im,(120,68)).astype(float))
        cap.release()
        delta=max(float(np.mean(np.abs(a-b))) for a,b in zip(seen,seen[1:]))
        assert delta>.32,(shot,delta)
        motion[shot]=round(delta,2)

    final=OUT/(TITLE+'_16x9.mp4')
    if mp4!=final:
        mp4.rename(final)
    verified=dict(file=final.name,resolution=[W,H],fps=FPS,frames=recipe['frames'],
                  seconds=recipe['duration'],sha256=sha(final),voice_samples=len(voice),
                  voice_original_sha256=sha(original),audio_correlation=corr,
                  audio_peak_dbfs=round(20*np.log10(realpeak),2),decoded=True,pcm16_media=sfx,
                  user_reference_motion=motion)
    (P/'validacao.json').write_text(json.dumps(verified,indent=2)+'\n')
    print(json.dumps(verified,indent=2),flush=True)


if __name__=='__main__':
    if sys.argv[1]=='package':
        package()
    else:
        master(Path(sys.argv[2]),Path(sys.argv[3]))
