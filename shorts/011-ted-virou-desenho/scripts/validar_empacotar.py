"""Confere o master e coloca o projeto e as suas mídias no ZIP de entrega."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import cv2
import numpy as np
import soundfile as sf

from montar_filmora import LIB, OUT as WFP, probe
from produzir import F, M, OUT, P, TITLE, VOICE, W, H, FPS, SR, sha


def package(temp, source_zip):
    plan = json.loads((P/'timeline.json').read_text())
    native = json.loads((P/'validacao_filmora.json').read_text())
    master = OUT/f'{TITLE}_9x16.mp4'
    original = F/'Voz_Original.wav'
    assert sha(WFP) == native['sha256']
    assert sha(original) == plan['voice_sha256']
    with zipfile.ZipFile(source_zip) as source:
        assert source.testzip() is None
        wav = next(n for n in source.namelist() if n.endswith('/1 voz.wav'))
        assert source.read(wav) == original.read_bytes()
    source_audio, rate = sf.read(original)
    timeline_audio, rate_in_timeline = sf.read(M/VOICE)
    assert rate == rate_in_timeline == SR
    assert len(source_audio) == len(timeline_audio)
    assert np.max(np.abs(source_audio*2 - timeline_audio)) <= 2**-23
    assert np.abs(timeline_audio).max() < 1

    info = probe(master)
    vid = next(s for s in info['streams'] if s['codec_type']=='video')
    aud = next(s for s in info['streams'] if s['codec_type']=='audio')
    assert (vid['width'],vid['height'],vid['r_frame_rate']) == (W,H,f'{FPS}/1')
    assert int(vid['nb_frames']) == plan['frames']
    assert int(aud['sample_rate'])==SR and aud['channels']==2
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(master),'-f','null','-'],check=True)
    decoded = np.frombuffer(subprocess.check_output([
        'ffmpeg','-v','error','-i',str(master),'-vn','-f','f32le','-',
    ]),dtype='<f4').reshape(-1,2)
    expected, expected_rate = sf.read(temp/'mix.wav')
    assert expected_rate==SR and len(decoded)>=len(expected)
    correlation = float(np.corrcoef(decoded[:len(expected)].ravel(),expected.ravel())[0,1])
    assert correlation>.995 and np.abs(decoded).max()<.98

    # Confere movimento em todos os clipes de trailer editados e no master.
    moves = {}
    for e in (row for row in plan['events'] if row['file'].endswith('.mp4')):
        cap = cv2.VideoCapture(str(M/e['file']))
        frames = []
        for frac in (.12,.48,.81):
            pos = e['offset'] + (e['end']-e['start'])*frac
            cap.set(cv2.CAP_PROP_POS_FRAMES,round(pos*FPS))
            ok, im = cap.read()
            assert ok, (e['file'],pos)
            frames.append(cv2.resize(im,(160,180)).astype(np.float32))
        cap.release()
        delta = max(float(np.abs(a-b).mean()) for a,b in zip(frames,frames[1:]))
        assert delta>.4, (e['file'],delta)
        moves[e['file']] = round(delta,3)

    cap = cv2.VideoCapture(str(master))
    previous = None
    motion = 0
    for frame in range(plan['frames']):
        ok, image = cap.read()
        assert ok
        thumb = cv2.resize(image,(80,142)).astype(np.float32)
        if previous is not None:
            motion += np.abs(thumb-previous).mean()>.2
        previous = thumb
    cap.release()
    assert motion > plan['frames']*.55
    report = {
        'master':master.name, 'sha256':sha(master), 'resolution':[W,H], 'fps':FPS, 'frames':plan['frames'],
        'seconds':plan['duration'], 'voice_seconds':len(source_audio)/SR, 'voice_sha256':sha(original),
        'voice_complete':True, 'voice_source_included_bit_exact':True, 'narration_gain_db':6.0206,
        'audio_export_correlation':correlation,
        'audio_true_peak_note':'Pico das amostras decodificadas, sem oversampling',
        'decoded_peak_dbfs':round(float(20*np.log10(np.max(np.abs(decoded)))),2),
        'decoded_video_and_audio':True, 'adjacent_frame_changes':int(motion), 'trailer_motion':moves,
        'no_added_captions':True, 'native_project':native,
    }
    validation = P/'validacao.json'
    validation.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')

    instructions = F/'LEIA_PRIMEIRO.txt'
    instructions.write_text(
        'TED virou DESENHO · MASSACOTE TUBE\n\n'
        'Extraia o ZIP por inteiro. Abra TED_virou_DESENHO_9x16.wfp dentro de Filmora.\n'
        'Mantenha a pasta midias ao lado do WFP. Se precisar religar um arquivo,\n'
        'indique a pasta midias extraída.\n\n'
        'A faixa de voz tem a tomada inteira, com ganho linear de +6,02 dB.\n'
        'Voz_Original.wav é a gravação intacta recebida. Trilha, sons, trailer,\n'
        'molduras, reações e camadas do avatar têm faixas independentes.\n\n'
        'O WFP inclui Basic Zoom In, Fast Bounce, Glow, Text Vibrate e Grunge_Jitter.\n'
        'O MP4 usa o grafismo e as curvas da montagem. O Filmora não foi executado\n'
        'neste Linux para abrir o WFP ou reproduzir os efeitos proprietários.\n',
        encoding='utf-8',
    )
    with zipfile.ZipFile(WFP) as z:
        items = json.loads(z.read(LIB))['media_items']
        media = []
        for item in items.values():
            if item['media_type'] not in (2,4,16):
                continue
            name = Path(item['download_url']).name
            assert hashlib.md5((M/name).read_bytes()).hexdigest() == item['src_md5'], name
            media.append(name)
        media.sort()
    paths = [WFP,instructions,original,*(M/name for name in media)]
    bundle = OUT/f'{TITLE}_Filmora_Completo.zip'
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED,compresslevel=4) as z:
        for path in paths:
            z.write(path,'Filmora/'+str(path.relative_to(F)))
        z.write(validation,validation.name)
    with zipfile.ZipFile(bundle) as z:
        assert z.testzip() is None
        for path in paths:
            assert z.read('Filmora/'+str(path.relative_to(F))) == path.read_bytes()
    manifest = {'bundle':bundle.name,'bytes':bundle.stat().st_size,'sha256':sha(bundle),
                'media_files':media,'all_zip_members_verified':True}
    (P/'pacote.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'master':report,'package':manifest},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    package(Path(sys.argv[1]),Path(sys.argv[2]))
