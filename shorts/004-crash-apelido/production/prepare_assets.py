"""Prepare the real narration and a silent, 24 fps CRT feed. No voice synthesis."""
from pathlib import Path
import array, json, math, subprocess, wave

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'assets'
FPS=24
DURATION=28

def run(args):
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',*args],check=True)

def prepare():
    voice=ASSETS/'voz'
    narration=array.array('h')
    for name in ['1-fish-audio-20261103-215858.wav','2-fish-audio-20261103-220144.wav']:
        with wave.open(str(voice/name)) as w:
            assert (w.getnchannels(),w.getsampwidth(),w.getframerate())==(1,2,44100)
            narration.frombytes(w.readframes(w.getnframes()))
    sr=44100
    original_count=len(narration)
    with wave.open(str(voice/'narracao_completa.wav'),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(narration.tobytes())
    narration.extend([0]*(DURATION*sr-len(narration)))
    # Soft, original 8-bit editorial accents sit in the measured speech pauses.
    for at,freq,length,gain in [(3.57,392,.075,290),(8.72,587,.06,210),
                                (16.80,220,.11,370),(25.45,330,.075,220),
                                (27.34,131,.16,390)]:
        start=round(at*sr)
        for i in range(round(length*sr)):
            t=i/sr; envelope=math.sin(math.pi*t/length)**2
            fundamental=math.sin(math.tau*freq*t)
            pulse=.7*fundamental+.3*math.sin(math.tau*freq*3*t)
            narration[start+i]=max(-32767,min(32767,narration[start+i]+round(gain*envelope*pulse)))
    mix=voice/'narracao_mix_28s.wav'
    with wave.open(str(mix),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(narration.tobytes())

    game=ASSETS/'gameplay'
    sequence=game/'Crash_Nsane_sequencia_camera_8s.mp4'
    ranges=[(10.45,13.85),(41.40,42.20),(44.60,45.80),(50.25,51.25),(54.25,55.85)]
    if not sequence.exists():
        source=Path('/tmp/crash_background_source.mp4')
        if not source.exists():
            raise FileNotFoundError('The documented source is needed to regenerate the selected gameplay sequence.')
        # Start inside the gameplay shots, after the trailer's crossfades.
        parts=[]
        for i,(a,b) in enumerate(ranges):
            parts.append(f'[0:v]trim=start={a}:end={b},setpts=PTS-STARTPTS[v{i}]')
        filters=';'.join(parts)+';'+''.join(f'[v{i}]' for i in range(len(ranges)))
        filters+='concat=n=5:v=1:a=0,crop=960:720:160:0,eq=gamma=1.25,scale=640:480:flags=neighbor,fps=24[out]'
        run(['-i',str(source),'-filter_complex',filters,'-map','[out]','-an','-t','8',
             '-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart',str(sequence)])
    info=json.loads((game/'fontes.json').read_text())
    entry={'file':sequence.name,'source_intervals':ranges,
        'audio':'removed','use':'Gameplay 3D selecionada para o monitor; recorte central em 4:3'}
    info['video_source']['selected_clips']=[x for x in info['video_source']['selected_clips']if x.get('file')!=sequence.name]+[entry]
    (game/'fontes.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n')

    freeze=game/'crash_rear_freeze.png'
    run(['-ss','0.55','-i',str(game/'Crash_Nsane_camera_10-14.mp4'),
         '-vf','crop=960:720:160:0,eq=gamma=1.25,scale=640:480:flags=neighbor',
         '-frames:v','1',str(freeze)])
    feed=game/'monitor_feed_28s.mp4'
    run(['-framerate','24','-loop','1','-t','5.875','-i',str(game/'crash_ps1_screenshot.png'),
         '-stream_loop','-1','-i',str(sequence),
         '-framerate','24','-loop','1','-t','5.125','-i',str(freeze),'-filter_complex',
         '[0:v]scale=640:480:flags=neighbor,setsar=1,fps=24,setpts=PTS-STARTPTS[s];'
         '[1:v]split=2[before][after];'
         '[before]trim=duration=5.708333333,setsar=1,setpts=PTS-STARTPTS[g];'
         '[2:v]setsar=1,setpts=PTS-STARTPTS[f];'
         '[after]trim=start=5.708333333:duration=11.291666667,setsar=1,setpts=PTS-STARTPTS[h];'
         '[s][g][f][h]concat=n=4:v=1:a=0[out]',
         '-map','[out]','-t','28','-r','24','-an','-c:v','libx264','-crf','18',
         '-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart',str(feed)])
    print(json.dumps({'original_voice_seconds':original_count/sr,'final_seconds':DURATION,
                      'frames':FPS*DURATION,'feed':str(feed)},ensure_ascii=False))

if __name__=='__main__':
    prepare()
