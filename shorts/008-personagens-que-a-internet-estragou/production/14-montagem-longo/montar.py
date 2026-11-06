"""Continuação da edição recebida; nenhum render Blender é refeito.

Uso: python montar.py. Requer ffmpeg, ffprobe, Pillow e NumPy.
Os masters aprovados são entradas de leitura. A parte do usuário é copiada,
sem recodificar os pacotes de vídeo, para a montagem final.
"""
from pathlib import Path
import json, subprocess, math, wave, hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

HERE = Path(__file__).resolve().parent
PROD = HERE.parent
ASSETS = HERE / 'assets'
OUT = HERE / 'output'
WORK = HERE / 'renders'
for d in (ASSETS, OUT, WORK): d.mkdir(exist_ok=True)
FPS = 60
CARD_FRAMES = 248
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf'
MONO = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'

# Zooms vinculados à intenção da frase, sem fragmentar novamente os planos.
EPISODES = [
    ('07-tracer', 'Tracer', 'OVERWATCH', 'tracer_retrato.png', [(17.8,19.9),(21.7,24.7)], 'a'),
    ('08-dva', 'D.Va', 'OVERWATCH', 'dva_piloto.jpg', [(23.92,26.38),(35.8,38.08)], 'b'),
    ('09-mercy', 'Mercy', 'OVERWATCH', 'mercy_asas.jpg', [(21.5,23.25),(26.17,28.75)], 'a'),
    ('10-lara-croft', 'Lara Croft', 'TOMB RAIDER', 'lara_classica.jpg', [(11.21,13.25),(34.5,37.1)], 'b'),
    ('11-peach', 'Peach', 'SUPER MARIO', 'peach.png', [(12.58,14),(34.83,37)], 'a'),
    ('12-sonic', 'Sonic', 'SONIC THE HEDGEHOG', None, [(14.08,16.29),(21.58,23.71)], 'b'),
]

def run(args):
    subprocess.run([str(x) for x in args], check=True)

def probe(p):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))

def encode_args():
    return ['-c:v','libx264','-preset','veryfast','-crf','18','-profile:v','high','-level:v','4.2',
            '-pix_fmt','yuv420p','-r','60','-g','120','-video_track_timescale','60000',
            '-c:a','aac','-b:a','192k','-ar','44100','-ac','2','-movflags','+faststart','-threads','3']

def master(folder):
    return next((PROD/folder/'output').glob('*16x9.mp4'))

def read_wav(p):
    with wave.open(str(p)) as w:
        assert w.getframerate()==44100
        return np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,w.getnchannels()).astype(np.float32)/32768

def write_wav(p, a):
    with wave.open(str(p),'wb') as w:
        w.setnchannels(a.shape[1]);w.setsampwidth(2);w.setframerate(44100)
        w.writeframes(np.clip(np.round(a*32768),-32768,32767).astype('<i2').tobytes())

def music_mix(folder, key, duration, target):
    """Narration PCM retained at unity. BGM comes from stereo side, no respeed."""
    voice=read_wav(PROD/folder/'assets/voz/narracao_completa.wav')
    n=round(duration*44100)
    v=np.zeros((n,2),np.float32)
    v[:len(voice),:]=voice[:n]
    music=read_wav(ASSETS/f'instrumental_referencia_{key}.wav')[:,0]
    # Overlap edges rather than an abrupt repeated seam.
    rms=np.sqrt(np.mean(music*music))+1e-10
    music=music*(10**(-34/20)/rms)
    overlap=round(.2*44100)
    loop=np.zeros(n+len(music),np.float32)
    env=np.ones(len(music),np.float32)
    env[:overlap]=np.linspace(0,1,overlap)
    env[-overlap:]=np.linspace(1,0,overlap)
    for start in range(0,n,len(music)-overlap): loop[start:start+len(music)]+=music*env
    bg=loop[:n]
    tt=np.arange(n)/44100
    bg*=np.minimum(tt/.18,1)*np.minimum(np.maximum(duration-tt,0)/.45,1)
    if folder=='08-dva': bg[(tt>=23.92)&(tt<=26.38)]*=.24
    if folder=='09-mercy': bg*=np.where(tt>=26.15,0,np.minimum(np.maximum(26.15-tt,0)/.3,1))
    # Sound beneath speech, no compressor/limiter changing the original voice.
    a=v+bg[:,None]
    assert np.max(np.abs(a))<1, f'Audio clipping: {folder}'
    write_wav(target,a)
    return {'voice_samples':len(voice),'voice_gain':1,'voice_speed':1,'voice_pitch_changed':False,
            'music_source':'stereo side of supplied reference, centred for mono compatibility',
            'music_rms_dbfs':-34,'peak':float(np.max(np.abs(a)))}

def portrait(folder, file):
    if file: return Image.open(PROD/folder/'assets/memes'/file).convert('RGB')
    dst=WORK/'sonic_retrato.jpg'
    run(['ffmpeg','-v','error','-threads','1','-ss','3.5','-i',PROD/folder/'assets/gameplay/sonic_dash.mp4',
         '-frames:v','1','-y',dst])
    return Image.open(dst).convert('RGB')

def card_image(folder, name, series, file):
    """Abertura inspirada na referência: retrato central, amarelo, HUD VHS."""
    im=portrait(folder,file)
    bg=Image.new('RGB',(960,540),(12,12,15))
    im=ImageOps.fit(im,(590,540),method=Image.Resampling.LANCZOS)
    # Fade only the portrait edges. The PS1 body masters remain sharp.
    mask=np.minimum(np.arange(590)/50,(589-np.arange(590))/50).clip(0,1)
    alpha=Image.fromarray(np.tile((mask*225).astype('uint8'),(540,1)))
    bg.paste(im,(185,0),alpha)
    glass=Image.new('RGBA',bg.size,(110,130,150,24))
    bg=Image.alpha_composite(bg.convert('RGBA'),glass)
    scan=Image.new('RGBA',bg.size,(0,0,0,0))
    sd=ImageDraw.Draw(scan)
    for y in range(0,540,4):sd.line((185,y,775,y),fill=(0,0,0,22))
    bg=Image.alpha_composite(bg,scan)
    d=ImageDraw.Draw(bg)
    hud=ImageFont.truetype(MONO,18)
    d.text((206,25),'PLAY ▷',font=hud,fill=(238,238,240,190))
    d.text((206,48),'SP',font=hud,fill=(238,238,240,180))
    d.text((637,25),'VCR TAPE',font=hud,fill=(238,238,240,190))
    d.text((637,48),'00:00:00',font=hud,fill=(238,238,240,180))
    d.text((206,473),'VOLUME',font=hud,fill=(238,238,240,190))
    d.text((206,496),'|||||||||---',font=hud,fill=(238,238,240,180))
    size=72 if len(name)<10 else 57
    font=ImageFont.truetype(FONT,size)
    small=ImageFont.truetype(FONT,25)
    # Orange shadow and dark outline like the received chapter cards.
    for text,y,f in [(name,235,font),(series,316,small)]:
        box=d.textbbox((0,0),text,font=f);x=(960-(box[2]-box[0]))//2
        d.text((x+3,y+5),text,font=f,fill='#b54b28',stroke_width=5,stroke_fill='#492c27')
        d.text((x,y),text,font=f,fill='#ffe65a',stroke_width=2,stroke_fill='#ae7a21')
    dst=ASSETS/f'cartela_{folder}.png';bg.convert('RGB').save(dst)
    return dst

def encode_card(folder,name,series,file):
    image=card_image(folder,name,series,file)
    dst=WORK/f'cartela_{folder}.mp4'
    # 248/60 matches the user's 4.133s cards. Tiny mechanical movement, no strobe.
    vf="scale=976:550:flags=lanczos,crop=960:540:x='8+2*sin(t*5)':y='5+sin(t*4)',fade=t=in:d=0.12,fade=t=out:st=3.97:d=0.16,scale=1920:1080:flags=lanczos,setsar=1"
    run(['ffmpeg','-v','error','-y','-filter_threads','1','-loop','1','-framerate','60','-i',image,
         '-i',ASSETS/'vinheta_referencia.wav','-vf',vf,'-t',str(CARD_FRAMES/FPS),
         *encode_args(),dst])
    return dst

def encode_episode(folder,zooms,music):
    src=master(folder)
    voice_meta=json.loads((PROD/folder/'audio.json').read_text())
    # Keep all spoken samples plus the original reaction tail, at the same speed.
    dur=math.ceil(float(probe(src)['format']['duration'])*60-1e-4)/60
    wav=WORK/f'{folder}_mix.wav'
    audio=music_mix(folder,music,dur,wav)
    expr='+'.join(f'between(t,{a},{b})'for a,b in zooms) or '0'
    # Reframe only already-planned reaction shots. No new arbitrary cuts.
    width=f'if(gt({expr},0),704,640)'
    vf=f"scale=w='{width}':h=-2:eval=frame:flags=neighbor,crop=640:360:(iw-640)/2:(ih-360)/2,scale=1920:1080:flags=neighbor,fps=60,setsar=1"
    dst=WORK/f'{folder}_editado.mp4'
    # Resume completed body encodes; failed/incomplete MP4s are rebuilt.
    valid=False
    if dst.exists():
        try: valid=abs(float(probe(dst)['format']['duration'])-dur)<.1
        except (subprocess.CalledProcessError,KeyError,ValueError): pass
    if not valid:
        run(['ffmpeg','-v','error','-y','-threads','2','-filter_threads','1','-i',src,'-i',wav,
             '-map','0:v:0','-map','1:a:0','-vf',vf,'-t',str(dur),*encode_args(),dst])
    return dst, {'folder':folder,'master':str(src.relative_to(PROD)),'duration':dur,'zooms':zooms,'audio':audio}

def main():
    segments=[];notes=[];audio_parts=[]
    for folder,name,series,file,zooms,music in EPISODES:
        print('BUILD',folder,flush=True)
        card=encode_card(folder,name,series,file)
        body,note=encode_episode(folder,zooms,music)
        segments += [card,body];notes.append(note)
        audio_parts += [read_wav(ASSETS/'vinheta_referencia.wav'),read_wav(WORK/f'{folder}_mix.wav')]
    body,note=encode_episode('13-encerramento',[], 'b')
    segments.append(body);notes.append(note)
    audio_parts.append(read_wav(WORK/'13-encerramento_mix.wav'))
    continuous_wav=WORK/'continuacao_audio_continuo.wav'
    write_wav(continuous_wav,np.concatenate(audio_parts))
    concat=WORK/'continuacao.txt'
    # Explicit video durations avoid accumulated AAC priming at every episode.
    def video_duration(p):
        s=next(s for s in probe(p)['streams']if s['codec_type']=='video')
        return int(s['nb_frames'])/60
    concat.write_text(''.join(f"file '{p}'\nduration {video_duration(p):.9f}\n" for p in segments))
    tail=OUT/'Continuacao_Tracer_ao_Encerramento_16x9.mp4'
    run(['ffmpeg','-v','warning','-y','-f','concat','-safe','0','-i',concat,'-i',continuous_wav,
         '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k',
         '-t',str(len(read_wav(continuous_wav))/44100),'-movflags','+faststart',tail])
    prefix=ASSETS/'Edicao_usuario_ate_2B.mp4'
    full_list=WORK/'completo.txt'
    pdur=video_duration(prefix)
    full_list.write_text(f"file '{prefix}'\nduration {pdur:.9f}\nfile '{tail}'\n")
    final=OUT/'Personagens_que_a_internet_ESTRAGOU_Completo_16x9.mp4'
    chapters=[(0.,'Introdução'),(36.0166667,'Lady Dimitrescu'),(78.5166667,'Tifa'),
              (110.7333333,'Chun-Li'),(153.7666667,'Ankha'),(201.4166667,'Vaporeon'),(252.5333334,'2B')]
    at=pdur
    for note,(_,name,_,_,_,_) in zip(notes,EPISODES):
        chapters.append((at,name));at+=CARD_FRAMES/60+note['duration']
    chapters.append((at,'Encerramento'))
    end=at+notes[-1]['duration']
    metadata=WORK/'chapters.ffmeta'
    text=';FFMETADATA1\n'
    for i,(start,title) in enumerate(chapters):
        stop=chapters[i+1][0]if i+1<len(chapters)else end
        text+=f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(start*1000)}\nEND={round(stop*1000)}\ntitle={title}\n'
    metadata.write_text(text)
    (HERE/'capitulos_youtube.txt').write_text(''.join(f'{int(t)//60:02}:{int(t)%60:02} {title}\n'for t,title in chapters))
    # Copy the complete video bitstream. Mix a single continuous audio stream;
    # the reference's sound is retained, with only AAC delivery re-encoding.
    prefix_samples=round(pdur*44100)
    af=f'[1:a]apad=whole_len={prefix_samples},atrim=end_sample={prefix_samples}[p];[p][2:a]concat=n=2:v=0:a=1[a]'
    run(['ffmpeg','-v','warning','-y','-f','concat','-safe','0','-i',full_list,
         '-i',prefix,'-i',continuous_wav,'-i',metadata,'-filter_complex',af,'-map','0:v:0','-map','[a]',
         '-map_metadata','3','-map_chapters','3',
         '-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',final])
    info={'reference_drive_id':'1AyEhvIPAr8xLV-faK39wtdA9NVkE4XDJ','reference_duration':292.483,
          'reference_video_reencoded':False,'reference_audio_reencoded_for_delivery':True,
          'reference_exact_frames':round(pdur*60),'fps':60,'resolution':[1920,1080],
          'chapter_card_seconds':CARD_FRAMES/FPS,'episodes':notes,'segments':[p.name for p in segments],
          'final_probe':probe(final),'tail_probe':probe(tail)}
    (HERE/'montagem.json').write_text(json.dumps(info,ensure_ascii=False,indent=2))
    print('COMPLETE',final,flush=True)

if __name__=='__main__':main()
