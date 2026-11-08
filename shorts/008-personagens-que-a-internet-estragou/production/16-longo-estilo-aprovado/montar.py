"""Restante do longo no padrão da amostra aprovada, sem oscilar a tela."""
from pathlib import Path
import sys,math,json,subprocess,shutil,copy
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps

P=Path(__file__).resolve().parent;PROD=P.parent
sys.path.insert(0,str(PROD/'15-teste-estilo-filmora'))
import produzir_teste as style
WORK=P/'renders';OUT=P/'output'
for d in [WORK,OUT]:d.mkdir(exist_ok=True)
CARD_FRAMES=248;CARD=CARD_FRAMES/60
CASES=[('07-tracer','TRACER','OVERWATCH','tracer_retrato.png','a'),
 ('08-dva','D.VA','OVERWATCH','dva_piloto.jpg','b'),
 ('09-mercy','MERCY','OVERWATCH','mercy_asas.jpg','a'),
 ('10-lara-croft','LARA CROFT','TOMB RAIDER','lara_classica.jpg','c'),
 ('11-peach','PEACH','SUPER MARIO','peach.png','b'),
 ('12-sonic','SONIC','SONIC THE HEDGEHOG',None,'a'),
 ('13-encerramento','ENCERRAMENTO','MASSACOTE GAMES',None,'b')]
# Intentional reframings of existing shots; gameplay and diagrams keep context.
EVENTS={
 '07-tracer':[(1,58/24,1,1.6,.5,.5),(189/24,226/24,1,1.87,.5,.5)],
 '08-dva':[(91/24,130/24,1,1.45,.5,.5),(336/24,389/24,1,1.65,.5,.5),
   (574/24,633/24,1,1.87,.5,.53),(921/24,948/24,1,1.18,.5,.5),
   (948/24,1004/24,1,2.08,.5,.54)],
 '09-mercy':[(31/24,72/24,1,1.45,.5,.5),(269/24,324/24,1,1.45,.5,.5),
   (485/24,516/24,1,1.30,.5,.52),(628/24,696/24,1,1.75,.5,.52)],
 '10-lara-croft':[(31/24,80/24,1,1.45,.5,.5),(269/24,318/24,1,1.87,.5,.5),
   (366/24,403/24,1,1.3,.5,.5),(708/24,744/24,1,1.25,.27,.52),
   (828/24,896/24,1,1.87,.27,.53)],
 '11-peach':[(160/24,208/24,1,1.5,.5,.5),(302/24,336/24,1,1.87,.5,.5),
   (605/24,658/24,1,1.18,.5,.5),(836/24,894/24,1,2.08,.5,.53)],
 '12-sonic':[(338/24,391/24,1,1.87,.5,.5),(518/24,569/24,1,1.25,.5,.52),
   (797/24,839/24,1,1.25,.5,.53)],
 '13-encerramento':[(15.2,20.125,1,1.06,.5,.5)]}

def run(args):subprocess.run([str(x)for x in args],check=True)
def probe(path):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
def master(folder):return next((PROD/folder/'output').glob('*16x9.mp4'))
def bounds(folder):
    t=json.loads((PROD/folder/'timeline.json').read_text());n=t['frames']*60//t['fps']
    return n,n/60,t
def events(folder,duration):
    ev=list(EVENTS.get(folder,[]))
    if folder=='07-tracer':
        origin=334/24
        for a,b,z0,z1,x,y in style.SHOTS:
            ev.append((origin+a,origin+b,z0,z1,x,y))
        ev.append((origin+style.BODY,duration,2.08,2.08,.6,.52))
    ev=[(round(a*60)/60,min(round(b*60)/60,duration),z0,z1,x,y)for a,b,z0,z1,x,y in ev if a<duration]
    points=sorted({0.,duration,*[s[0]for s in ev],*[s[1]for s in ev]})
    result=[]
    for a,b in zip(points,points[1:]):
        if b<=a:continue
        match=next((s for s in ev if s[0]<=a+1e-6 and s[1]>=b-1e-6),None)
        result.append(match if match and match[:2]==(a,b) else (a,b,1,1,.5,.5))
    return result

def title_png(name,subtitle,path):
    im=Image.new('RGBA',(1536,1024));d=ImageDraw.Draw(im)
    size=285
    while True:
        f=ImageFont.truetype(style.FONT,size)
        if d.textbbox((0,0),name,font=f)[2]<1410:break
        size-=2
    x=(1536-d.textbbox((0,0),name,font=f)[2])//2;y=210
    for depth in range(40,0,-1):
        d.text((x+depth,y+depth),name,font=f,fill=(135+depth,55+depth,8,255),stroke_width=8,stroke_fill=(45,27,15,255))
    d.text((x,y),name,font=f,fill='#ffd532',stroke_width=5,stroke_fill='#ffef6c')
    size=107
    while True:
        f=ImageFont.truetype(style.FONT,size)
        if d.textbbox((0,0),subtitle,font=f)[2]<1420:break
        size-=2
    x=(1536-d.textbbox((0,0),subtitle,font=f)[2])//2
    for depth in range(14,0,-1):d.text((x+depth,570+depth),subtitle,font=f,fill='#ba5721',stroke_width=4,stroke_fill='#402a20')
    d.text((x,570),subtitle,font=f,fill='#ffe35d',stroke_width=2,stroke_fill='#85531b')
    im.save(path)

def prepare(case):
    folder,name,subtitle,portrait_name,music_key=case
    n,duration,timeline=bounds(folder)
    d=WORK/folder;media=d/'midias';media.mkdir(parents=True,exist_ok=True)
    source=media/'tracer_take.mp4'
    if not source.exists():
        # Lossless silent remux for the editable native project, avoiding a second encode.
        run(['ffmpeg','-v','error','-y','-i',master(folder),'-map','0:v:0','-c:v','copy','-an',source])
    a=style.wav(PROD/folder/'assets/voz/narracao_completa.wav');ns=n*735
    assert len(a)<=ns,(folder,len(a),ns)
    voice=np.zeros((ns,2),np.float32);voice[:len(a)]=a
    style.savewav(media/'tracer_voz.wav',voice)
    raw=style.wav(WORK/'trilhas'/f'{music_key}.wav')
    overlap=8820;step=len(raw)-overlap
    music=np.zeros((ns+len(raw),2),np.float32)
    fade=np.ones(len(raw));fade[:overlap]=np.linspace(0,1,overlap);fade[-overlap:]=np.linspace(1,0,overlap)
    for start in range(0,ns,step):music[start:start+len(raw)]+=raw*fade[:,None]
    music=music[:ns];tt=np.arange(ns)/44100
    music*=np.minimum(tt/.15,1)[:,None]*np.minimum(np.maximum(duration-tt,0)/.2,1)[:,None]
    if folder=='07-tracer':music[tt>21.7066667]*=.16
    if folder=='08-dva':music[(tt>=23.92)&(tt<=26.38)]*=.24
    if folder=='09-mercy':music*=np.minimum(np.maximum(26.15-tt,0)/.3,1)[:,None]
    if folder=='12-sonic':music*=np.minimum(np.maximum(25.21-tt,0)/1.51,1)[:,None]
    if folder=='13-encerramento':music*=.7
    # Preserve voice gain. Attenuate only accompaniment if a transient lacks headroom.
    headroom=np.maximum(.999-np.max(abs(voice),axis=1),0)
    scale=np.minimum(1,headroom/np.maximum(np.max(abs(music),axis=1),1e-10))
    music*=scale[:,None]
    style.savewav(media/'musica_teste.wav',music)
    style.savewav(d/'mix.wav',voice+music)
    shutil.copyfile(PROD/'14-montagem-longo/assets/vinheta_referencia.wav',media/'vinheta.wav')
    if folder=='07-tracer':
        for fn in ['tracer_retrato.jpg','tracer_logo_3d.png']:shutil.copyfile(style.MEDIA/fn,media/fn)
    elif portrait_name:
        im=Image.open(PROD/folder/'assets/memes'/portrait_name).convert('RGB')
        ImageOps.fit(im,(2400,3508),method=Image.Resampling.LANCZOS,centering=(.48,.45)).save(media/'tracer_retrato.jpg',quality=94)
        title_png(name,subtitle,media/'tracer_logo_3d.png')
    elif folder=='12-sonic':
        frame=d/'sonic_original.jpg'
        run(['ffmpeg','-v','error','-y','-ss','3.5','-i',PROD/folder/'assets/gameplay/sonic_dash.mp4','-frames:v','1','-threads','1',frame])
        ImageOps.fit(Image.open(frame).convert('RGB'),(2400,3508),method=Image.Resampling.LANCZOS).save(media/'tracer_retrato.jpg',quality=94)
        title_png(name,subtitle,media/'tracer_logo_3d.png')
    else:
        # Placeholder assets are discarded when assembling the card-free outro project.
        for fn in ['tracer_retrato.jpg','tracer_logo_3d.png']:shutil.copyfile(style.MEDIA/fn,media/fn)
    rec={'folder':folder,'name':name,'frames':n,'duration':duration,'voice_samples':len(a),
         'voice_duration':len(a)/44100,'events':events(folder,duration),'music':music_key,
         'voice_gain':1,'voice_speed':1,'voice_pitch_changed':False,'peak':float(abs(voice+music).max()),
         'has_card':folder!='13-encerramento','source_probe':probe(source)}
    (d/'config.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2))
    return rec

def encoder(path,frames):
    return subprocess.Popen(['ffmpeg','-v','error','-y','-filter_threads','1','-f','rawvideo','-pix_fmt','rgb24',
       '-s','640x360','-r','60','-i','pipe:0','-an','-vf','scale=1920:1080:flags=neighbor','-c:v','libx264',
       '-preset','veryfast','-crf','18','-profile:v','high','-level:v','4.2','-pix_fmt','yuv420p','-g','120',
       '-video_track_timescale','60000','-threads','2','-frames:v',str(frames),'-movflags','+faststart',str(path)],stdin=subprocess.PIPE)
def complete(path,frames):
    if not path.exists():return False
    try:return int(next(s for s in probe(path)['streams']if s['codec_type']=='video')['nb_frames'])==frames
    except (KeyError,ValueError,subprocess.CalledProcessError):return False

def render_card(folder):
    d=WORK/folder;out=d/'card.mp4'
    if complete(out,CARD_FRAMES):return out
    poster=Image.open(d/'midias/tracer_retrato.jpg').convert('RGB')
    poster=poster.resize((round(640*2400/3508),640),Image.Resampling.LANCZOS)
    logo=Image.open(d/'midias/tracer_logo_3d.png').convert('RGBA');logo.thumbnail((230,154),Image.Resampling.LANCZOS)
    hud=ImageFont.truetype(style.MONO,9)
    xx=np.tile(np.linspace(-1,1,640),(360,1));vignette=np.clip(1-.7*np.maximum(abs(xx)-.48,0)/.52,0,1)[...,None]
    enc=encoder(out,CARD_FRAMES)
    for i in range(CARD_FRAMES):
        t=i/60;im=Image.new('RGB',(640,360),(12,12,16))
        im.paste(poster,((640-poster.width)//2,round(-235+t/CARD*200)))
        layer=Image.new('RGBA',(640,360));draw=ImageDraw.Draw(layer)
        for y in range(0,360,3):draw.line((0,y,640,y),fill=(0,0,0,18))
        im=Image.alpha_composite(im.convert('RGBA'),layer);im.alpha_composite(logo,((640-logo.width)//2,round(145-logo.height*.4)))
        draw=ImageDraw.Draw(im)
        for pos,text in [((164,22),'PLAY ▷'),((164,34),'SP'),((399,22),'VCR TAPE'),((399,34),'00:00:02'),((164,312),'VOLUME'),((164,324),'|||||||||---')]:
            draw.text(pos,text,font=hud,fill=(240,240,242,180))
        a=style.global_look(im.convert('RGB'),t,True).astype(np.float32)*vignette
        enc.stdin.write(np.uint8(np.clip(a*min(t/.1,1,(CARD-t)/.1),0,255)).tobytes())
    enc.stdin.close();assert enc.wait()==0
    return out

def render_body(rec):
    folder=rec['folder'];d=WORK/folder;out=d/'body.mp4';n=rec['frames']
    if complete(out,n):return out
    dec=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-filter_threads','1','-i',str(d/'midias/tracer_take.mp4'),
       '-vf','scale=640:360:flags=neighbor,fps=60','-frames:v',str(n),'-pix_fmt','rgb24','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE)
    enc=encoder(out,n)
    for i in range(n):
        raw=dec.stdout.read(640*360*3)
        if len(raw)!=640*360*3:raise RuntimeError(f'{folder}: missing frame {i}')
        im=Image.frombytes('RGB',(640,360),raw);t=i/60
        shot=next(s for s in rec['events']if s[0]<=t<s[1])
        z=style.zoom_at(t,shot);cw=640/z;ch=360/z;x=(640-cw)*shot[4];y=(360-ch)*shot[5]
        im=im.crop((round(x),round(y),round(x+cw),round(y+ch))).resize((640,360),Image.Resampling.NEAREST)
        enc.stdin.write(style.global_look(im,t).tobytes())
    dec.stdout.close();assert dec.wait()==0
    enc.stdin.close();assert enc.wait()==0
    return out

def assemble(records):
    segments=[];audio=[];at=0;chapters=[]
    for r in records:
        d=WORK/r['folder'];chapters.append((at,r['name']))
        if r['has_card']:
            segments.append((d/'card.mp4',CARD));audio.append(style.wav(d/'midias/vinheta.wav'));at+=CARD
        segments.append((d/'body.mp4',r['duration']));audio.append(style.wav(d/'mix.wav'));at+=r['duration']
    style.savewav(WORK/'restante_audio.wav',np.concatenate(audio))
    playlist=WORK/'restante.txt';playlist.write_text(''.join(f"file '{p}'\nduration {d:.9f}\n"for p,d in segments))
    tail=OUT/'Restante_Tracer_ao_Encerramento_Estilo_Aprovado_16x9.mp4'
    run(['ffmpeg','-v','warning','-y','-f','concat','-safe','0','-i',playlist,'-i',WORK/'restante_audio.wav',
         '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-t',str(at),'-movflags','+faststart',tail])
    prefix=PROD/'14-montagem-longo/assets/Edicao_usuario_ate_2B.mp4';pdur=17549/60
    playlist=WORK/'completo.txt';playlist.write_text(f"file '{prefix}'\nduration {pdur:.9f}\nfile '{tail}'\n")
    old=[(0,'Introdução'),(31.883333,'Lady Dimitrescu'),(74.383333,'Tifa'),(106.6,'Chun-Li'),
         (149.633333,'Ankha'),(197.283333,'Vaporeon'),(248.4,'2B')]
    chapters=old+[(pdur+t,name)for t,name in chapters]
    meta=WORK/'chapters.ffmeta';txt=';FFMETADATA1\n'
    for i,(t,name)in enumerate(chapters):
        end=chapters[i+1][0]if i+1<len(chapters)else pdur+at
        txt+=f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(t*1000)}\nEND={round(end*1000)}\ntitle={name}\n'
    meta.write_text(txt);(P/'capitulos_youtube.txt').write_text(''.join(f'{int(t)//60:02}:{int(t)%60:02} {name}\n'for t,name in chapters))
    final=OUT/'Personagens_que_a_internet_ESTRAGOU_Estilo_Aprovado_16x9.mp4'
    samples=round(pdur*44100)
    af=f'[1:a]apad=whole_len={samples},atrim=end_sample={samples}[p];[p][2:a]concat=n=2:v=0:a=1[a]'
    run(['ffmpeg','-v','warning','-y','-copyts','-f','concat','-safe','0','-i',playlist,'-i',prefix,'-i',WORK/'restante_audio.wav',
         '-i',meta,'-filter_complex',af,'-map','0:v:0','-map','[a]','-map_chapters','3','-map_metadata','3',
         '-c:v','copy','-c:a','aac','-b:a','192k','-avoid_negative_ts','disabled','-movflags','+faststart',final])
    return final,tail

def main():
    run([sys.executable,P/'recuperar_trilhas.py'])
    records=[]
    for case in CASES:
        r=prepare(case);records.append(r);print('RENDER',r['folder'],flush=True)
        if r['has_card']:render_card(r['folder'])
        render_body(r);print('READY',r['folder'],flush=True)
    final,tail=assemble(records)
    report={'approved_sample_commit':'aee7345eacb48e6d6286b16f8962b2b131ab6656','new_added_screen_oscillation':False,
            'prefix_frames_preserved':17549,'prefix_video_reencoded':False,'records':records,
            'final_probe':probe(final),'tail_probe':probe(tail)}
    (P/'montagem.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print('MP4S_READY',final,tail,flush=True)
if __name__=='__main__':main()
