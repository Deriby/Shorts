"""Verificação de entrega: decodificação, continuidade e preservação da referência."""
from pathlib import Path
import subprocess,json,hashlib
import numpy as np
import montar

P=Path(__file__).resolve().parent
ref=P/'assets/Edicao_usuario_ate_2B.mp4'
final=P/'output/Personagens_que_a_internet_ESTRAGOU_Completo_16x9.mp4'
tail=P/'output/Continuacao_Tracer_ao_Encerramento_16x9.mp4'
info=json.loads((P/'montagem.json').read_text())

def pcm(path):
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-vn','-ar','44100','-ac','2','-f','s16le','pipe:1'])
    return np.frombuffer(raw,dtype='<i2').reshape(-1,2).astype(np.float32)/32768

def vcl_hash(path,frames):
    # Ignore parameter-set/AUD/SEI packaging that a lossless remux can insert.
    args=['ffmpeg','-v','error','-i',str(path),'-map','0:v:0','-an','-c:v','copy',
          '-frames:v',str(frames),'-bsf:v','h264_mp4toannexb,filter_units=pass_types=1|5','-f','h264','pipe:1']
    p=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    h=hashlib.sha256()
    while block:=p.stdout.read(1024*1024):h.update(block)
    err=p.stderr.read();assert p.wait()==0,err.decode()
    return h.hexdigest()

def compare(a,b):
    n=min(len(a),len(b));a=a[:n].ravel();b=b[:n].ravel()
    err=float(np.sqrt(np.mean((a-b)**2)))
    correlation=float(np.dot(a,b)/np.sqrt(np.dot(a,a)*np.dot(b,b)))
    return {'samples_per_channel':n,'correlation':correlation,'rms_error':err}

def main():
    print('VERIFY_VIDEO',flush=True)
    r=subprocess.run(['ffmpeg','-v','error','-xerror','-threads','4','-i',str(final),
                      '-map','0:v:0','-map','0:a:0','-f','null','-'],capture_output=True)
    assert r.returncode==0,r.stderr.decode()
    frames=17549
    print('VERIFY_PREFIX_BITSTREAM',flush=True)
    a=vcl_hash(ref,frames);b=vcl_hash(final,frames)
    assert a==b,'Reference image bitstream was changed'
    print('VERIFY_AUDIO',flush=True)
    audio=pcm(final);original=pcm(ref)
    prefix_samples=round(frames/60*44100)
    pr=compare(original,audio[:prefix_samples])
    expected=montar.read_wav(P/'renders/continuacao_audio_continuo.wav')
    ar=compare(expected,audio[prefix_samples:])
    assert pr['correlation']>.99,pr
    assert ar['correlation']>.99,ar
    by_episode=[];at=prefix_samples
    for note in info['episodes']:
        if note['folder']!='13-encerramento':at+=round(248/60*44100)
        clip=montar.read_wav(P/'renders'/f"{note['folder']}_mix.wav")
        result=compare(clip,audio[at:at+len(clip)])
        assert result['correlation']>.99,(note['folder'],result)
        by_episode.append({'episode':note['folder'],**result})
        at+=len(clip)
    p=montar.probe(final)
    video=next(s for s in p['streams']if s['codec_type']=='video')
    audio_stream=next(s for s in p['streams']if s['codec_type']=='audio')
    assert (video['width'],video['height'])==(1920,1080)
    assert video['r_frame_rate']=='60/1'
    assert abs(float(video['duration'])-float(audio_stream['duration']))<.05
    report={'full_decode':'passed','prefix_h264_image_payload_preserved':True,
            'reference_vcl_sha256':a,'final_prefix_vcl_sha256':b,
            'reference_frames_preserved':frames,'prefix_audio':pr,'continuation_audio':ar,
            'episodes':by_episode,'video_frames':video['nb_frames'],
            'duration':p['format']['duration'],'video_audio_duration_difference':abs(float(video['duration'])-float(audio_stream['duration'])),
            'original_episode_masters_modified':False,
            'voice_speed_changed':False,'voice_pitch_changed':False,
            'native_filmora_plugins_executed':False}
    (P/'verificacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print('VERIFIED',json.dumps(report,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
