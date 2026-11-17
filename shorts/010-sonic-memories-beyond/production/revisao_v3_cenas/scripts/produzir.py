"""Sonic V3: cenas compartilhadas, apresentador dirigindo elementos e fonte integral.

Fontes locais podem ser indicadas por TUBE_CACHE. Nenhuma arte do personagem é
redesenhada. O plano contém as mesmas transformações usadas no MP4 e no WFP.
"""
from pathlib import Path
import os,sys,json,math,shutil,hashlib,subprocess
import cv2,numpy as np,soundfile as sf
from scipy.ndimage import gaussian_filter1d
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageOps,ImageEnhance

P=Path(__file__).resolve().parents[1]
R=next(p for p in P.parents if (p/'AGENTS.md').exists())
C=Path(os.environ.get('TUBE_CACHE','/workspace/work/reference-comparison'))
V=C/'v2/Filmora/midias';BANK=C/'bank';M=P/'output/Filmora/midias';A=P/'analise'
W,H,FPS,N=1080,1920,30,1053;D=N/FPS
M.mkdir(parents=True,exist_ok=True);A.mkdir(parents=True,exist_ok=True)
cv2.setNumThreads(1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ff(*args):subprocess.run(['ffmpeg','-v','error','-y',*map(str,args)],check=True)
def save(im,name):im.save(M/name);return name
def rgba():return Image.new('RGBA',(W,H))
def background(im,name):
    im=ImageOps.fit(im.convert('RGB'),(270,480)).filter(ImageFilter.GaussianBlur(12)).resize((W,H),Image.Resampling.BICUBIC)
    im=Image.blend(im,Image.new('RGB',(W,H),'#16213c'),.18)
    return save(im,name)
def panel(im,name,size=(780,950),label=None):
    im=ImageOps.contain(im.convert('RGBA'),size,Image.Resampling.LANCZOS)
    margin=5;titleh=66 if label else 0
    x=(W-im.width)//2;y=(H-im.height-titleh)//2
    out=rgba();dr=ImageDraw.Draw(out)
    dr.rectangle((x-margin,y-margin,x+im.width+margin,y+im.height+titleh+margin),fill='#fff7e8')
    out.alpha_composite(im,(x,y+titleh))
    if label:
        f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',32)
        dr.text((W//2,y+titleh/2),label,font=f,fill='#192342',anchor='mm')
    return save(out,name)
def prepare():
    for name in ['Voz_Dery_Original.wav','Musica_Green_Hill_Baixa.wav','Whoosh.wav','Clique.wav','Bonk.wav','Som_Luta_Baixo.wav']:
        shutil.copy2(V/name,M/name)
    for src,name,y in [(C/'context_full.mp4','Contexto.mp4',656),(C/'fight_full.mp4','Luta_Continua.mp4',430)]:
        # Recupera o quadro 16:9 inteiro da v1. A v2 havia ampliado o centro.
        filt=f'[0:v]crop=1080:608:0:656,split[a][b];[a]scale=270:480:force_original_aspect_ratio=increase,crop=270:480,gblur=sigma=14,scale=1080:1920,eq=brightness=-0.08[bg];[bg][b]overlay=0:{y},setsar=1[v]'
        ff('-i',src,'-filter_complex_threads',1,'-filter_complex',filt,'-map','[v]','-an','-c:v','libx264','-preset','veryfast','-crf',17,'-threads',2,'-pix_fmt','yuv420p',M/name)
    shutil.copy2(V/'Meme_Digitando.mp4',M/'Internet_Digitando.mp4')
    cap=cv2.VideoCapture(str(C/'context_full.mp4'));ok,frame=cap.read();assert ok;cap.release()
    stage=Image.fromarray(cv2.cvtColor(frame[656:1264],cv2.COLOR_BGR2RGB))
    background(Image.open(V/'Sonic_Original_Tela.png'),'Fundo_Tube.png')
    # Um cenário comum permite gesto e mídia dividirem o mesmo espaço.
    still=ImageOps.fit(stage.crop((0,0,1080,520)),(W,900));still=ImageEnhance.Brightness(still).enhance(1.3)
    canvas=rgba();canvas.alpha_composite(still.convert('RGBA'),(0,510));save(canvas,'Cenario_Trailer.png')
    pair=Image.open(C/'comparison_full.png')
    original=pair.crop((123,611,580,1171));fan=pair.crop((581,611,1032,1171))
    def poster(im,name,label):
        bg=ImageOps.fit(im.convert('RGB'),(620,1260)).filter(ImageFilter.GaussianBlur(18)).convert('RGBA')
        fg=ImageOps.contain(im.convert('RGBA'),(620,1150),Image.Resampling.LANCZOS)
        bg.alpha_composite(fg,((620-fg.width)//2,(1260-fg.height)//2))
        panel(bg,name,(620,1260),label)
    poster(original,'Original_Painel.png','ORIGINAL')
    poster(fan,'Fa_Painel.png','EDIÇÃO DE FÃ')
    panel(original,'Original_Apontar.png',(440,600),'ORIGINAL')
    # Posts: somente o retângulo nítido, com autoria. Fundo em outra camada.
    crops={'Post_Critica_Tela.png':(25,420,1055,1500),'Post_Correcao_Tela.png':(25,548,1055,1372),'Post_Frame_Tela.png':(25,520,1055,1396)}
    for old,box in crops.items():
        im=Image.open(V/old).crop(box)
        name={'Post_Critica_Tela.png':'Post_Critica.png','Post_Correcao_Tela.png':'Post_Fa.png','Post_Frame_Tela.png':'Post_Frame.png'}[old]
        panel(im,name,(970,1210));background(im,'Fundo_'+name)
    panel(Image.open(V/'Meme_Sonic_Anel_Tela.png'),'Meme_Anel.png',(690,1050))
    panel(Image.open(V/'Meme_Sonic_Poligonos_Tela.png'),'Meme_Poligonos.png',(690,1050))
    # Canvas e matrizes idênticos para todas as peças registradas do banco.
    poses=['04_apontando_esquerda','05_apontando_direita','06_apontando_cima','08_apontando_camera','09_joinha','12_deu_de_ombros','13_ponderando','15_fazendo_ressalva','16_desespero','20_tramando','24_apresentando_lado','29_pistolinhas']
    def art(src,name):
        im=Image.open(src).convert('RGBA').resize((1434,1434),Image.Resampling.LANCZOS)
        out=rgba();out.alpha_composite(im,(-178,344));save(out,name)
    art(BANK/'camadas/cabeca_sem_bigode.png','Cabeca.png');art(BANK/'camadas/bigode_repouso.png','Bigode.png')
    for ident in poses:
        art(BANK/'camadas'/f'{ident}_corpo.png',f'Corpo_{ident}.png')
        front=BANK/'camadas'/f'{ident}_frente.png'
        if front.exists():art(front,'Frente_'+ident+'.png')
    print('MIDIAS_V3_PREPARADAS',flush=True)

def interp(keys,t):
    arr=np.asarray(keys,float);j=int(np.searchsorted(arr[:,0],t,side='right'))
    if j==0:return arr[0,1:]
    if j>=len(arr):return arr[-1,1:]
    a,b=arr[j-1],arr[j];u=np.clip((t-a[0])/max(1e-9,b[0]-a[0]),0,1);u=u*u*(3-2*u)
    return a[1:]*(1-u)+b[1:]*u
def plan():
    events=[]
    def add(file,s,e,tr,knots=None,why=''):
        if isinstance(tr,int):s=round(s*30)/30;e=round(e*30)/30
        dur=e-s
        if knots is None:knots=[[0,.5,.5,1,0],[dur,.5,.5,1,0]]
        if isinstance(tr,int):
            # Densificação partilhada: WFP linear reproduz a curva suave do MP4.
            keys=[]
            for i in range(round(dur*30)+1):
                x,y,sc,rot=interp(knots,i/30);keys.append([round(i/30,8),float(x),float(y),float(sc),float(sc),float(rot)])
        else:keys=[]
        events.append(dict(file=file,start=s,end=e,track=tr,keys=keys,reason=why))
    add('Fundo_Tube.png',0,D,0,why='Ambiente do Sonic, derivado da mídia do tema')
    # Gancho: o original abre espaço para a intervenção do fã no mesmo plano.
    add('Original_Painel.png',0,3.2,3,[[0,.5,.5,1.34,0],[.5,.5,.5,1.27,0],[1.25,.27,.5,.72,0],[2.8,.27,.5,.75,0],[3.2,-.5,.5,.75,0]],'O original cede espaço à comparação')
    add('Fa_Painel.png',.9,3.2,4,[[0,1.4,.5,.72,0],[.36,.75,.5,.72,0],[1.7,.75,.5,.75,0],[2.3,1.6,.5,.75,0]],'Versão do fã entra lateralmente, identificada')
    # A piada acontece no cenário e na direção do dedo; nenhuma miniatura fixa.
    add('Cenario_Trailer.png',3.1,7.8,2,[[0,.5,.5,1,0],[4.7,.48,.5,1.05,0]],'Cenário comum para as reações')
    add('Meme_Anel.png',3.1,5.5,5,[[0,-.6,.49,.94,0],[.24,.31,.49,.94,0],[1.65,.31,.49,1.04,0],[2.4,-.6,.49,1.04,0]],'Harmonização: desenho absurdo apresentado pelo personagem')
    add('Meme_Poligonos.png',5.4,7.8,4,[[0,1.6,.49,.94,0],[.24,.31,.49,.94,0],[1.8,.31,.48,1.04,0],[2.4,.31,.48,1.04,0]],'Segundo tempo da mesma gag, com reação aberta')
    add('Contexto.mp4',7.8,10.8,2,why='Animação original em quadro inteiro e velocidade 1x')
    add('Fundo_Post_Critica.png',10.8,14.0,1)
    add('Post_Critica.png',10.8,14.0,3,[[0,1.5,.5,1,0],[.24,.5,.5,1,0],[1.3,.5,.6,1.12,0],[2.9,.5,.43,1.17,0],[3.2,.5,.43,1.17,0]],'Autoria e texto primeiro; foco no frame ao mencionar a crítica')
    add('Internet_Digitando.mp4',14,16.6,2,[[0,.5,.5,1,0],[2.6,.5,.49,1.08,0]],'Uma ação contínua para a fala sobre a internet')
    add('Fundo_Post_Fa.png',16.6,20.9,1)
    add('Post_Fa.png',16.6,17.9,5,[[0,1.5,.49,1,0],[.22,.5,.49,1,0],[1,.5,.49,1.025,0],[1.3,-.6,.49,1.025,0]],'Mostra o post real antes de destacar as versões')
    add('Original_Painel.png',17.8,20.9,3,[[0,-.6,.40,.68,0],[.24,.27,.40,.68,0],[2.65,.27,.4,.72,0],[3.1,-.6,.4,.72,0]],'Painéis independentes acima do gesto')
    add('Fa_Painel.png',17.8,20.9,4,[[0,1.6,.40,.68,0],[.24,.74,.40,.68,0],[2.65,.74,.4,.72,0],[3.1,1.6,.4,.72,0]],'A edição do fã ocupa o lado indicado pelo gesto')
    add('Cenario_Trailer.png',20.9,28.9,2,[[0,.5,.5,1.05,0],[8,.48,.5,1.09,0]],'Cena do comentário pessoal: apresentador e imagem compartilham o espaço')
    add('Original_Apontar.png',20.9,24.0,3,[[0,1.5,.65,1,0],[.24,.76,.65,1,0],[2.7,.76,.65,1.04,0],[3.1,1.5,.65,1.04,0]],'O personagem aponta ao frame sobre o qual opina')
    add('Post_Frame.png',25.6,28.9,3,[[0,1.5,.65,.54,0],[.23,.76,.65,.54,0],[2.8,.76,.65,.59,0],[3.3,1.5,.65,.59,0]],'Retoma o frame sem cobrir o apresentador')
    add('Luta_Continua.mp4',28.9,35.1,2,why='6,2 s contínuos de luta a partir do elogio; quadro 16:9 inteiro')
    # Atuação: preparação -> indicação do elemento -> opinião -> aprovação -> público.
    acts=[
        ('04_apontando_esquerda',3.2,5.5,.73,.62,.86,-1),
        ('16_desespero',5.5,7.8,.73,.62,.84,1),
        ('20_tramando',14.3,16.6,.25,.69,.78,-1),
        ('06_apontando_cima',18.0,19.5,.73,.78,.79,-1),
        ('06_apontando_cima',19.5,20.9,.28,.78,.79,0),
        ('24_apresentando_lado',20.9,22.5,.28,.59,1.00,-1),
        ('12_deu_de_ombros',22.5,23.9,.28,.59,1.00,1),
        ('15_fazendo_ressalva',23.9,25.6,.43,.58,1.06,-1),
        ('05_apontando_direita',25.6,27.8,.28,.59,1.00,-1),
        ('09_joinha',27.8,28.9,.43,.58,1.06,0),
        ('08_apontando_camera',31.2,33.0,.50,.80,1.04,-1),
        ('29_pistolinhas',33.0,34.1,.50,.80,1.04,1),
        ('09_joinha',34.1,35.1,.50,.80,1.04,0),
    ]
    a,sr=sf.read(M/'Voz_Dery_Original.wav',dtype='float32');a=a.mean(axis=1)if a.ndim>1 else a
    rms=np.asarray([np.sqrt(np.mean(a[max(0,round((i/30-.012)*sr)):min(len(a),round((i/30+.04)*sr))]**2)+1e-12)for i in range(N+1)])
    energy=gaussian_filter1d(np.clip((rms-.012)/max(.01,np.percentile(rms,85)-.012),0,1),.7);energy[rms<.006]=0
    def rot(deg):
        t=math.radians(deg);return np.asarray([[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]])
    for idx,(pose,s,e,x,y,scale,angle)in enumerate(acts):
        s=round(s*30)/30;e=round(e*30)/30;dur=e-s
        sameprev=idx>0 and abs(acts[idx-1][2]-s)<.04 and abs(acts[idx-1][3]-x)<.02 and abs(acts[idx-1][4]-y)<.02
        samenext=idx+1<len(acts) and abs(acts[idx+1][1]-e)<.04 and abs(acts[idx+1][3]-x)<.02 and abs(acts[idx+1][4]-y)<.02
        rows={'body':[],'head':[],'bigode':[]}
        for i in range(round(dur*30)+1):
            lt=i/30;enter=1 if sameprev else min(1,lt/.23);enter=enter*enter*(3-2*enter)
            leave=0 if samenext or e==D else max(0,min(1,(lt-(dur-.17))/.17));leave=leave*leave*(3-2*leave)
            py=y+(1-enter)*.22+leave*.16
            # Inclinação única dirigida ao gesto; sem ciclo de flutuação global.
            gesture=max(0,1-abs(lt-.45)/.42);sc=scale*(1+.015*gesture)
            headangle=-1.7*min(1,lt/.55)+.9*min(1,max(0,lt-.75)/.7)
            center=np.asarray([540.,960.]);hp=np.asarray([539.5,1100.]);mp=np.asarray([539.5,950.9])
            target=np.asarray([x*W,py*H]);B=rot(angle)*sc;HR=rot(headangle)
            hpos=target+B@(hp+HR@(center-hp)-center)
            en=float(energy[min(N,round(s*30)+i)]);sx=1+.020*en;sy=1+.058*en
            mc=mp+np.asarray([sx,sy])*(center-mp)+np.asarray([0,-2.5*en])
            mpos=target+B@(hp+HR@(mc-hp)-center)
            rows['body'].append([lt,x,py,sc,sc,angle]);rows['head'].append([lt,hpos[0]/W,hpos[1]/H,sc,sc,angle+headangle]);rows['bigode'].append([lt,mpos[0]/W,mpos[1]/H,sc*sx,sc*sy,angle+headangle])
        for part,name,tr in [('body','Corpo_'+pose+'.png',6),('head','Cabeca.png',7),('bigode','Bigode.png',8)]:
            events.append(dict(file=name,start=s,end=e,track=tr,keys=rows[part],reason='Atuação contextual: '+pose,part=part))
        front='Frente_'+pose+'.png'
        if(M/front).exists():events.append(dict(file=front,start=s,end=e,track=9,keys=rows['body'],reason='Mão à frente do rosto, registrada à pose',part='body'))
    add('Voz_Dery_Original.wav',0,35.092875,'voz',why='Gravação original completa')
    add('Musica_Green_Hill_Baixa.wav',0,D,'musica')
    # Sons pontuam as entradas de elementos, sem whoosh em cada troca de pose.
    for t in [.9,3.1,5.4,10.8,16.6,17.8,20.9,25.6]:add('Whoosh.wav',t,t+.42,'sfx')
    for t in [1.27,18.12]:add('Clique.wav',t,t+.25,'sfx2')
    add('Bonk.wav',5.65,6.2,'sfx2');add('Som_Luta_Baixo.wav',28.9,D,'luta')
    out=dict(title='Sonic V3 — cenas e atuação pela referência do Tube',width=W,height=H,fps=FPS,frames=N,duration=D,voice_duration=35.092875,voice_sha256=sha(M/'Voz_Dery_Original.wav'),events=events,automatic_captions=False,eyes_animation=False,psx_filter=False,continuous_fight_start=28.9,continuous_fight_seconds=6.2,media_stage='Imagem e personagem dividem o cenário; indicação orientada ao elemento',reference_attachment='file_00000000ac3c820e972f7d870b149bb0')
    (P/'timeline.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('PLANO_V3',len(events),flush=True);return out

def render(p,mode='full'):
    images={};caps={};video_cache={};arrays={}
    visual=sorted([e for e in p['events']if isinstance(e['track'],int)],key=lambda e:e['track'])
    for e in visual:
        n=e['file'];arrays[id(e)]=np.asarray(e['keys'])
        if n in images or n in caps:continue
        if n.endswith('.png'):
            im=cv2.imread(str(M/n),cv2.IMREAD_UNCHANGED)
            if im.shape[2]==4:
                ix,iy,iw,ih=cv2.boundingRect(im[:,:,3]);images[n]=(im[iy:iy+ih,ix:ix+iw].copy(),ix,iy)
            else:images[n]=(im,0,0)
        else:caps[n]=cv2.VideoCapture(str(M/n))
    samples=[0,.6,1.5,2.5,3.7,4.6,5.9,7.0,8.4,11.6,13.2,14.9,16.9,18.7,19.9,21.5,22.9,24.5,26.7,28.35,29.3,30.6,31.9,33.5,34.7]
    chosen={round(t*30)for t in samples}
    selected=range(N)if mode=='full'else sorted(chosen)
    silent=P/'output/.video_sem_audio.mp4'
    if mode=='full':
        log=(A/'render.log').open('w');proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r','30','-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p','-movflags','+faststart',str(silent)],stdin=subprocess.PIPE,stderr=log)
    for i in selected:
        t=i/30;canvas=images['Fundo_Tube.png'][0][:,:,:3].copy()
        for e in visual:
            if e['track']==0 or not(e['start']-1e-8<=t<e['end']-1e-8):continue
            k=arrays[id(e)];q=min(round((t-e['start'])*30),len(k)-1);x,y,sx,sy,deg=k[q,1:]
            n=e['file'];ix=iy=0
            if n in images:im,ix,iy=images[n]
            else:
                cap=caps[n];wanted=round((t-e['start'])*30)
                if n not in video_cache or video_cache[n]!=wanted-1:cap.set(cv2.CAP_PROP_POS_FRAMES,wanted)
                ok,im=cap.read();assert ok,(n,wanted);video_cache[n]=wanted
            rad=math.radians(deg);mat=np.asarray([[math.cos(rad)*sx,-math.sin(rad)*sy],[math.sin(rad)*sx,math.cos(rad)*sy]])
            c=np.asarray([540.,960.]);target=np.asarray([x*W,y*H]);offset=target-mat@c
            corners=np.asarray([[ix,iy],[ix+im.shape[1],iy],[ix,iy+im.shape[0]],[ix+im.shape[1],iy+im.shape[0]]])@mat.T+offset
            x0=max(0,int(np.floor(corners[:,0].min()))-2);y0=max(0,int(np.floor(corners[:,1].min()))-2);x1=min(W,int(np.ceil(corners[:,0].max()))+2);y1=min(H,int(np.ceil(corners[:,1].max()))+2)
            if x1<=x0 or y1<=y0:continue
            aff=np.column_stack((mat,offset+mat@np.asarray([ix,iy])-np.asarray([x0,y0]))).astype('float32')
            layer=cv2.warpAffine(im,aff,(x1-x0,y1-y0),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
            roi=canvas[y0:y1,x0:x1]
            if layer.shape[2]==4:
                alpha=layer[:,:,3:4].astype('float32')/255;roi[:]=(layer[:,:,:3]*alpha+roi*(1-alpha)).astype('uint8')
            else:
                mask=cv2.warpAffine(np.ones(im.shape[:2],np.uint8),aff,(x1-x0,y1-y0),flags=cv2.INTER_NEAREST);roi[mask>0]=layer[mask>0]
        if mode=='full':proc.stdin.write(canvas.tobytes())
        if i in chosen:cv2.imwrite(str(A/f'quadro_{i:04d}.jpg'),canvas)
        if mode=='full'and i%90==0:print('RENDER_V3',i,'/',N,flush=True)
    for cap in caps.values():cap.release()
    if mode!='full':print('QUADROS_V3_PRONTOS',flush=True);return
    proc.stdin.close();assert proc.wait()==0;log.close()
    total=round(D*48000);mix=np.zeros((total,2),dtype=np.float32)
    for e in p['events']:
        if isinstance(e['track'],int):continue
        a,sr=sf.read(M/e['file'],dtype='float32',always_2d=True);assert sr==48000
        if a.shape[1]==1:a=np.repeat(a,2,axis=1)
        start=round(e['start']*sr);n=min(len(a),total-start,round((e['end']-e['start'])*sr));mix[start:start+n]+=a[:n]
    peak=float(np.abs(mix).max());gain=min(1,.98/max(peak,1e-8));mix*=gain
    sf.write(P/'output/.mix.wav',mix,48000,subtype='PCM_24')
    out=P/'output/Massacote_Tube_Sonic_V3_9x16.mp4'
    ff('-i',silent,'-i',P/'output/.mix.wav','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-t',D,'-movflags','+faststart',out)
    (A/'audio_mix.json').write_text(json.dumps(dict(pre_gain_peak=peak,global_gain=gain,voice_original_file_unchanged=True),indent=2)+'\n')
    print('MP4_V3_PRONTO',out.stat().st_size,flush=True)

if __name__=='__main__':
    mode=sys.argv[1]if len(sys.argv)>1 else'all'
    if mode in ['prepare','all']:prepare()
    if mode in ['prepare','plan','all']:p=plan()
    else:p=json.loads((P/'timeline.json').read_text())
    if mode in ['stills','render','all']:render(p,'stills'if mode=='stills'else'full')
