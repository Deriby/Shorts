"""Sonic: composição 2D e plano compartilhado com o projeto nativo Filmora."""
from pathlib import Path
import json, math, subprocess, shutil, hashlib, sys
sys.path.insert(0, '/workspace/tools/shorts_asr')
import cv2, numpy as np, soundfile as sf
from scipy.ndimage import gaussian_filter1d
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

P=Path(__file__).resolve().parents[1]; R=next(p for p in P.parents if (p/'AGENTS.md').exists())
M=P/'output/Filmora/midias'; M.mkdir(parents=True,exist_ok=True)
A=R/'assets/personagens/massacote_tube_2d/modular_01'
SRC=next(Path('/workspace/attachments/tube_sonic/extraido').iterdir())
W,H,FPS=1080,1920,30; N=1053; D=N/FPS
cv2.setNumThreads(1)
def run(args): subprocess.run(['ffmpeg','-v','error','-y',*map(str,args)],check=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(s): return ImageFont.truetype(fontpath,s)
def save(im,name): im.save(M/name); return name
def plane(im,box,rounded=True):
    im=ImageOps.contain(im.convert('RGBA'),(box[2]-box[0],box[3]-box[1]),Image.Resampling.LANCZOS)
    x=box[0]+(box[2]-box[0]-im.width)//2;y=box[1]+(box[3]-box[1]-im.height)//2
    canvas=Image.new('RGBA',(W,H)); shadow=Image.new('RGBA',(W,H));sd=ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x-11,y-11,x+im.width+11,y+im.height+11),20,fill=(0,0,0,190))
    canvas.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(15)))
    ImageDraw.Draw(canvas).rounded_rectangle((x-5,y-5,x+im.width+5,y+im.height+5),12,fill='#e8daca')
    canvas.alpha_composite(im,(x,y));return canvas
def framed(name,src,box): return save(plane(Image.open(src),box),name)

def prepare():
    voice=SRC/'1 - Voz.wav';shutil.copy2(voice,M/'Voz_Dery_Original.wav')
    a,sr=sf.read(voice,dtype='float32'); assert sr==48000 and len(a)==1684458
    # Base gráfica; sem filtros PSX/glitch sobre o novo personagem ou as mídias.
    yy,xx=np.mgrid[0:H,0:W];v=np.clip(1-np.sqrt(((xx-W*.48)/W)**2+((yy-H*.42)/H)**2),0,1)
    bg=np.stack([19+16*v,16+11*v,37+29*v],axis=-1).astype('uint8')
    base=Image.fromarray(bg);bd=ImageDraw.Draw(base,'RGBA')
    for x in [-1050,-350,350,1050]:bd.line((x,0,x+1400,H),fill=(125,67,110,19),width=65)
    save(base,'Fundo_Tube.png')
    rawscale=.93;ox,oy=106,430
    def art(src,name):
        im=Image.open(src).convert('RGBA');im=im.resize((round(1024*rawscale),round(1536*rawscale)),Image.Resampling.LANCZOS)
        c=Image.new('RGBA',(W,H));c.alpha_composite(im,(ox,oy));save(c,name)
    for src in (A/'rig').glob('*_corpo.png'):art(src,'Corpo_'+src.stem.removesuffix('_corpo')+'.png')
    art(A/'rig/cabeca_limpa.png','Cabeca.png');art(A/'bigode/01_bigode_repouso.png','Bigode.png')
    for src in (A/'olhos').glob('*.png'):art(src,'Olhos_'+src.stem+'.png')
    for src in (A/'frente').glob('*.png'):art(src,'Frente_'+src.stem.removesuffix('_frente')+'.png')
    image=Image.open(SRC/'print corrigindo o visual.png').convert('RGB');iw,ih=image.size
    pair=image.crop((round(iw*.025),round(ih*.207),round(iw*.975),round(ih*.934)))
    comp=plane(pair,(48,470,1032,1310));draw=ImageDraw.Draw(comp)
    draw.text((100,405),'ORIGINAL',font=font(32),fill='#f5ebda')
    draw.text((570,405),'EDIÇÃO DE FÃ',font=font(32),fill='#ed858c')
    save(comp,'Comparacao_Original_Fa.png')
    framed('Critica_Azure.png',SRC/'print criticando o visual 2.png',(65,315,1015,1450))
    framed('Critica_Batman.png',SRC/'print criticando o visual 3.png',(60,320,1020,1340))
    framed('Post_Correcao_Fa.png',SRC/'print corrigindo o visual.png',(46,260,1034,1390))
    framed('Meme_Sonic_Poligonos.png',SRC/'meme1.jpg',(385,280,1025,990))
    framed('Meme_Sonic_Anel.png',SRC/'meme2.jpg',(365,250,1025,990))
    # Mantém o post inteiro legível; o avatar ocupa somente a faixa inferior.
    clean=next(f for f in SRC.glob('*.mp4')if f.name.startswith('Sonic the'))
    def video(src,start,dur,name):
        if (M/name).exists() and (M/name).stat().st_size>10000:
            info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(M/name)]))['streams'][0]
            if int(info.get('nb_frames',0))==round(dur*30):return
        # Nenhuma alteração de velocidade. Fundo de suporte desfocado; imagem principal íntegra.
        filt='[0:v]setpts=PTS-STARTPTS,fps=30,split=2[a][b];[a]scale=270:480:force_original_aspect_ratio=increase,crop=270:480,gblur=sigma=18,scale=1080:1920,eq=brightness=-0.13[bg];[b]scale=1080:840:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[v]'
        run(['-ss',start,'-i',src,'-frames:v',round(dur*30),'-filter_complex_threads','1','-filter_complex',filt,'-map','[v]','-an','-c:v','libx264','-preset','veryfast','-crf','19','-threads','2','-pix_fmt','yuv420p',M/name])
    video(clean,15.0,3.0,'Memories_Contexto.mp4')
    video(clean,535.9,6.2,'Metal_Sonic_Acao.mp4')
    # Meme de digitação do banco aprovado, com tempo de ação suficiente.
    typing=R/'assets/biblioteca_memes/arquivos/15dpIaSDSPLGA2e0K210I6X9RI4eSVY8r.mp4'
    video(typing,2.0,2.6,'Meme_Digitando.mp4')
    video(SRC/'memegif3.gif',0,3.8,'Meme_Metal_Encarando.mp4')
    music=next(SRC.glob('*.mp3'))
    run(['-i',music,'-t',D,'-af',f'loudnorm=I=-29:TP=-9:LRA=7,afade=t=in:d=0.25,afade=t=out:st={D-.75}:d=0.75','-ar','48000','-ac','2','-c:a','pcm_s16le',M/'Musica_Green_Hill_Baixa.wav'])
    sounds=[('Whoosh.wav','1hcO_kLWpcF9dOSkfJmx9Bu7Q5yGFjQZI.wav',.05,.42,-25),('Clique.wav','1Pr5Vh7hg-S-UJhFQIXE4TdrkjgyH6XM_.wav',0,.25,-22),('Bonk.wav','1iwe6DT1c95NxfCKPX1wXfZ5nZG3VAu1C.mp3',0,.55,-24)]
    for name,source,start,dur,peak in sounds:
        path=R/'assets/biblioteca_memes/arquivos'/source
        buf=subprocess.check_output(['ffmpeg','-v','error','-ss',str(start),'-i',str(path),'-t',str(dur),'-ar','48000','-ac','2','-f','f32le','-'])
        y=np.frombuffer(buf,dtype='<f4').reshape(-1,2).copy();y*=10**(peak/20)/max(np.max(np.abs(y)),1e-6)
        fade=min(480,len(y)//3);y[:fade]*=np.linspace(0,1,fade)[:,None];y[-fade:]*=np.linspace(1,0,fade)[:,None]
        sf.write(M/name,y,48000,subtype='PCM_16')
    run(['-ss','535.9','-i',clean,'-t','6.2','-vn','-af','volume=0.16,afade=t=in:d=0.12,afade=t=out:st=5.9:d=0.3','-ar','48000','-ac','2','-c:a','pcm_s16le',M/'Som_Luta_Baixo.wav'])
    print('MIDIAS_PREPARADAS',flush=True)

def plan():
    a,sr=sf.read(M/'Voz_Dery_Original.wav',dtype='float32');a=a.mean(axis=1)if a.ndim>1 else a
    rms=np.array([np.sqrt(np.mean(a[max(0,round((i/FPS-.012)*sr)):min(len(a),round((i/FPS+.04)*sr))]**2)+1e-12)for i in range(N+1)])
    e=gaussian_filter1d(np.clip((rms-.012)/max(.01,np.percentile(rms,85)-.012),0,1),.7);e[rms<.006]=0
    events=[]
    def add(file,start,end,track,keys=None,why='',part=None):
        s=round(start*30)/30 if isinstance(track,int)else start
        b=round(end*30)/30 if isinstance(track,int)else end
        events.append(dict(file=file,start=s,end=b,track=track,keys=keys or [[0,.5,.5,1,1,0],[b-s,.5,.5,1,1,0]],reason=why,part=part))
    def card(file,start,end,track=2,why='',slide=True):
        dur=round(end*30)/30-round(start*30)/30
        if slide:ks=[[0,1.60,.52,.96,.96,2],[.20,.48,.5,1.015,1.015,-.4],[.32,.5,.5,1,1,0],[dur-.22,.5,.5,1.025,1.025,0],[dur,-.65,.49,1.025,1.025,-2]]
        else:ks=[[0,.5,.5,1,1,0],[dur,.5,.5,1.035,1.035,0]]
        add(file,start,end,track,ks,why)
    add('Fundo_Tube.png',0,D,0)
    card('Comparacao_Original_Fa.png',0,3.2,why='Gancho: deixa explícita a diferença original / edição de fã',slide=False)
    card('Meme_Sonic_Anel.png',3.25,5.45,8,'Harmonização facial: reação absurda enviada pelo usuário')
    card('Meme_Sonic_Poligonos.png',5.45,7.9,8,'Segundo Sonic deformado sustenta a piada; não é flash')
    card('Memories_Contexto.mp4',7.8,10.8,2,'Contextualiza a animação; fonte recebida',False)
    card('Critica_Azure.png',10.65,14.1,1,'Exemplo de crítica com autor visível')
    card('Meme_Digitando.mp4',14.0,16.6,2,'A internet faz o que sabe fazer: digitação',True)
    card('Post_Correcao_Fa.png',16.5,20.85,1,'Post com as versões original e corrigida de fã')
    card('Meme_Metal_Encarando.mp4',22.1,24.8,2,'Não vi nada demais: pausa de julgamento com meme do pacote',True)
    card('Critica_Batman.png',24.65,27.25,1,'Retoma qual frame recebeu críticas antes de elogiar a animação')
    card('Metal_Sonic_Acao.mp4',27.0,33.2,2,'Seis segundos contínuos da luta durante o elogio, com som próprio',False)
    # Poses aprovadas; microgestos e troca de expressão por intenção, em vez de ciclo genérico.
    acts=[('04_apontando','00_normal_base',.15,3.1,.53,.835,.57,-1),('03_debochado','07_desconfiado',3.1,5.5,.29,.69,.94,1),('09_assustado','08_assustado',5.5,7.8,.31,.70,.94,-1),('04_apontando','00_normal_base',7.9,10.6,.77,.84,.46,0),('07_pensando','06_pensando',10.8,14.0,.74,.84,.46,-1),('10_facepalm','12_preocupado',14.05,16.6,.78,.84,.49,0),('04_apontando','07_desconfiado',16.7,20.8,.76,.84,.47,-1),('05_confuso','05_confuso',20.8,22.2,.50,.56,1.04,-1),('05_confuso','05_confuso',22.2,24.8,.72,.85,.50,1),('02_conversando','00_normal_base',24.9,27.0,.74,.84,.49,0),('02_conversando','10_piscando_esquerdo',33.1,D,.51,.56,1.04,-1)]
    for idx,(pose,eye,start,end,x,y,scale,tilt)in enumerate(acts):
        start=round(start*30)/30;end=round(end*30)/30;frames=[]
        for i in range(round(start*30),round(end*30)+1):
            t=i/30;local=t-start;dur=end-start
            enter=min(1,local/.22);enter=enter*enter*(3-2*enter)
            leave=min(1,max(0,(local-(dur-.18))/.18));leave=leave*leave*(3-2*leave)
            # Uma ênfase no começo, descanso e retorno. Nada de tremido/oscilação permanente.
            emphasis=max(0,1-abs(local-.48)/.35)*.014
            s=scale*(.975+.025*enter+emphasis);px=x;py=y+(1-enter)*.085+leave*.08
            angle=tilt*(.4+.6*enter);hr=0 if pose=='10_facepalm'else(-1.4*math.sin(min(1,local/1.0)*math.pi/2)+.5*min(1,local/2))
            th=math.radians(angle);B=np.array([[math.cos(th),-math.sin(th)],[math.sin(th),math.cos(th)]])*s
            center=np.array([W/2,H/2]);target=np.array([px*W,py*H]);hp=np.array([539.38,1116.34]);mp=np.array([541.24,908.95])
            htheta=math.radians(hr);Hmat=np.array([[math.cos(htheta),-math.sin(htheta)],[math.sin(htheta),math.cos(htheta)]])
            # Matriz em coordenadas nativas; cada parte vira cinco curvas Filmora independentes.
            hcenter=hp+Hmat@(center-hp);hpos=target+B@(hcenter-center)
            base=[px,py,s,s,angle];head=[hpos[0]/W,hpos[1]/H,s,s,angle+hr]
            energy=float(e[min(i,N)]);sx=1+.025*energy;sy=1+.075*energy
            mcenter=mp+np.array([sx,sy])*(center-mp)+np.array([0,-3.5*energy])
            mhp=hp+Hmat@(mcenter-hp);mpos=target+B@(mhp-center)
            must=[mpos[0]/W,mpos[1]/H,s*sx,s*sy,angle+hr]
            frames.append(dict(time=t,body=base,head=head,bigode=must))
        for part,filename,tr in [('body','Corpo_'+pose+'.png',3),('head','Cabeca.png',4),('bigode','Bigode.png',6)]:
            add(filename,start,end,tr,[[round(f['time']-start,8),*f[part]]for f in frames],why='Atuação: '+pose,part=part)
        front='Frente_'+pose+'.png'
        if (M/front).exists():add(front,start,end,7,[[round(f['time']-start,8),*f['body']]for f in frames],part='body')
        # Piscar em duas aparições longas, sem alterar o desenho de olhos/rosto.
        blink=(idx in [1,6,10]and end-start>1.5)
        eyes=[(start,end,eye)]
        if blink:
            b=start+1.1;eyes=[(start,b,eye),(b,b+2/30,'02_piscada_meio'),(b+2/30,b+4/30,'03_piscada_fechado'),(b+4/30,b+6/30,'02_piscada_meio'),(b+6/30,end,eye)]
        for a,b,state in eyes:
            a=round(a*30)/30;b=round(b*30)/30;ks=[[round(f['time']-a,8),*f['head']]for f in frames if a-1e-6<=f['time']<=b+1e-6]
            add('Olhos_'+state+'.png',a,b,5,ks,why='Expressão: '+state,part='head')
    add('Voz_Dery_Original.wav',0,35.092875,'voz',why='Arquivo original integral, sem corte/velocidade/tom')
    add('Musica_Green_Hill_Baixa.wav',0,D,'musica')
    for t in [3.10,7.78,10.65,14.0,16.5,20.8,22.1,24.65,27.0,33.1]:add('Whoosh.wav',t,t+.42,'sfx')
    for t in [.25,16.75]:add('Clique.wav',t,t+.25,'sfx2')
    add('Bonk.wav',5.7,6.25,'sfx2');add('Som_Luta_Baixo.wav',27,33.2,'luta')
    payload=dict(title='Sonic e a harmonização facial',width=W,height=H,fps=FPS,frames=N,duration=D,voice_duration=35.092875,events=events,voice_sha256=sha(M/'Voz_Dery_Original.wav'),source_archive_sha256='b01d0e5c6c1eac474f0020d5335b762fd4486ab4a8212e861de75e7ed961cc3e',psx_filter=False,automatic_captions=False)
    (P/'timeline.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n');print('PLANO',len(events),D,flush=True);return payload

def interpolate(keys,t):
    for a,b in zip(keys,keys[1:]):
        if t<=b[0]+1e-8:
            u=np.clip((t-a[0])/max(1e-9,b[0]-a[0]),0,1);u=u*u*(3-2*u)
            return np.array(a[1:])*(1-u)+np.array(b[1:])*u
    return np.array(keys[-1][1:])

def render(p,preview=False):
    out=P/'output/Massacote_Tube_Sonic_9x16.mp4';silent=P/'output/.video_sem_audio.mp4'
    # PNGs, composições e curvas são os mesmos usados no WFP. Sem Blender.
    images={};captures={}
    for ev in p['events']:
        file=ev['file']
        if not isinstance(ev['track'],int)or file in images or file in captures:continue
        if file.endswith('.png'):
            im=cv2.imread(str(M/file),cv2.IMREAD_UNCHANGED)
            if im.shape[2]==4:
                bx,by,bw,bh=cv2.boundingRect(im[:,:,3]);images[file]=(im[by:by+bh,bx:bx+bw].copy(),bx,by)
            else:images[file]=(im,0,0)
        else:captures[file]=cv2.VideoCapture(str(M/file))
    cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r','30','-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p','-movflags','+faststart',str(silent)]
    if not preview:
        log=(P/'analise/render.log').open('w');proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
    cache={};visual=sorted([ev for ev in p['events']if isinstance(ev['track'],int)],key=lambda e:e['track'])
    chosen={0,40,112,180,260,360,450,550,645,720,810,855,930,1015}
    for i in range(N):
        if preview and i not in chosen:continue
        t=i/30;canvas=images['Fundo_Tube.png'][0][:,:,:3].copy()
        for ev in visual:
            if ev['track']==0 or not ev['start']-1e-8<=t<ev['end']-1e-8:continue
            file=ev['file'];x,y,sx,sy,angle=interpolate(ev['keys'],t-ev['start'])
            if file in images:im,ix,iy=images[file]
            else:
                cap=captures[file];wanted=round((t-ev['start'])*30)
                if file not in cache or wanted!=cache[file][0]+1:cap.set(cv2.CAP_PROP_POS_FRAMES,wanted)
                ok,im=cap.read();assert ok,(file,wanted);cache[file]=(wanted,im)
            theta=math.radians(angle);mat=np.array([[math.cos(theta)*sx,-math.sin(theta)*sy],[math.sin(theta)*sx,math.cos(theta)*sy]])
            c=np.array([W/2,H/2]);target=np.array([x*W,y*H]);aff=np.column_stack((mat,target-mat@c)).astype('float32')
            if im.shape[2]==4:
                corners=np.array([[ix,iy],[ix+im.shape[1],iy],[ix,iy+im.shape[0]],[ix+im.shape[1],iy+im.shape[0]]])@mat.T+aff[:,2]
                x0=max(0,int(np.floor(corners[:,0].min()))-2);y0=max(0,int(np.floor(corners[:,1].min()))-2)
                x1=min(W,int(np.ceil(corners[:,0].max()))+2);y1=min(H,int(np.ceil(corners[:,1].max()))+2)
                if x1<=x0 or y1<=y0:continue
                local=aff.copy();local[:,2]+=mat@np.array([ix,iy])-np.array([x0,y0])
                layer=cv2.warpAffine(im,local,(x1-x0,y1-y0),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
                alpha=layer[:,:,3:4].astype('float32')/255;roi=canvas[y0:y1,x0:x1]
                roi[:]=(layer[:,:,:3]*alpha+roi*(1-alpha)).astype('uint8')
            else:
                layer=cv2.warpAffine(im,aff,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
                # Vídeos de tela inteira possuem fundo próprio; a margem durante a entrada é transparente.
                mask=cv2.warpAffine(np.ones((H,W),dtype='uint8'),aff,(W,H),flags=cv2.INTER_NEAREST)
                canvas[mask>0]=layer[mask>0]
        if not preview:proc.stdin.write(canvas.tobytes())
        if i in chosen:cv2.imwrite(str(P/'analise'/f'quadro_{i:04d}.jpg'),canvas)
        if i%180==0:print('RENDER',i,'/',N,flush=True)
    if preview:return
    proc.stdin.close();assert proc.wait()==0;log.close()
    # Mixagem fora da imagem e em faixas separadas no Filmora.
    total=round(D*48000);mix=np.zeros((total,2),dtype='float32')
    for ev in p['events']:
        if isinstance(ev['track'],int):continue
        a,sr=sf.read(M/ev['file'],dtype='float32',always_2d=True);assert sr==48000
        if a.shape[1]==1:a=np.repeat(a,2,axis=1)
        start=round(ev['start']*sr);length=min(len(a),total-start,round((ev['end']-ev['start'])*sr));mix[start:start+length]+=a[:length]
    peak=float(np.max(np.abs(mix)));gain=min(1.,.98/max(peak,1e-8));mix*=gain
    sf.write(P/'output/.mix.wav',mix,48000,subtype='PCM_24')
    run(['-i',silent,'-i',P/'output/.mix.wav','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-t',D,'-movflags','+faststart',out])
    (P/'analise/audio_mix.json').write_text(json.dumps(dict(pre_gain_peak=peak,global_gain=gain,voice_unmodified_file=True,music_I=-29,sfx_peak_dBFS=[-25,-22,-24]),indent=2)+'\n')
    print('MP4_PRONTO',out,out.stat().st_size,flush=True)

if __name__=='__main__':
    mode=sys.argv[1]if len(sys.argv)>1 else'all'
    if mode in ['all','prepare']:prepare()
    if mode in ['all','prepare','plan']:p=plan()
    else:p=json.loads((P/'timeline.json').read_text())
    if mode in ['all','render','stills']:render(p,preview=mode=='stills')
