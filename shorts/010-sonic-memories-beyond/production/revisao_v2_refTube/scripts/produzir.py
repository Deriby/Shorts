"""Revisão pela referência do Tube: quadro preenchido, câmeras e novo avatar."""
from pathlib import Path
import json,sys,subprocess,shutil,math,importlib.util,hashlib
sys.path.insert(0,'/workspace/tools/shorts_asr')
import numpy as np,soundfile as sf
from scipy.ndimage import gaussian_filter1d
P=Path(__file__).resolve().parents[1];OLD=P.parent;R=next(p for p in P.parents if(p/'AGENTS.md').exists());M=P/'output/Filmora/midias';M.mkdir(parents=True,exist_ok=True)
BANK=R/'assets/personagens/massacote_tube_2d/oculos_3d_30_poses';SRC=next(Path('/workspace/attachments/tube_sonic/extraido').iterdir());D=35.1;N=1053;W,H=1080,1920
def magick(*args):subprocess.run(['magick','-limit','thread','2',*map(str,args)],check=True,stdout=subprocess.DEVNULL)
def prepare():
    for name in ['Voz_Dery_Original.wav','Musica_Green_Hill_Baixa.wav','Whoosh.wav','Clique.wav','Bonk.wav','Som_Luta_Baixo.wav','Memories_Contexto.mp4','Metal_Sonic_Acao.mp4','Meme_Digitando.mp4','Meme_Metal_Encarando.mp4']:shutil.copy2(OLD/'output/Filmora/midias'/name,M/name)
    # Reenquadra o plano nítido para ocupar mais altura, mantendo o vídeo em 1x.
    for name,height,frames in [('Memories_Contexto.mp4',1000,90),('Metal_Sonic_Acao.mp4',1080,186)]:
        width=round(height*16/9/2)*2;x=(width-1080)//2;y=(1920-height)//2;tmp=P/'analise/reframe.mp4'
        filt=f'[0:v]split[a][b];[b]crop=1080:608:0:656,scale={width}:{height},crop=1080:{height}:{x}:0[fg];[a][fg]overlay=0:{y},setsar=1[v]'
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(M/name),'-filter_complex_threads','1','-filter_complex',filt,'-map','[v]','-frames:v',str(frames),'-an','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p',str(tmp)],check=True);tmp.replace(M/name)
    # Enquadramento da mídia ocupa o quadro; a própria imagem forma o fundo de apoio.
    def photo(src,name):
        bg=P/'analise/photo_bg.png';fg=P/'analise/photo_fg.png'
        magick(src,'-resize','1080x1920^','-gravity','center','-extent','1080x1920','-blur','0x18','-brightness-contrast','-12x0',bg)
        magick(src,'-resize','1030x1740',fg)
        magick(bg,fg,'-gravity','center','-compose','over','-composite','-strip','PNG32:'+str(M/name))
    for src,name in [('print criticando o visual 2.png','Post_Critica_Tela.png'),('print corrigindo o visual.png','Post_Correcao_Tela.png'),('print criticando o visual 3.png','Post_Frame_Tela.png')]:photo(SRC/src,name)
    pair=P/'analise/par_original_fa.png';orig=P/'analise/original.png';fan=P/'analise/fan.png'
    # Mesma área ilustrativa recebida no post, sem transformar a edição de fã em arte oficial.
    probe=json.loads(subprocess.check_output(['magick','identify','-format','{"w":%w,"h":%h}',str(SRC/'print corrigindo o visual.png')]))
    iw,ih=probe['w'],probe['h'];x0,y0,x1,y1=round(iw*.025),round(ih*.207),round(iw*.975),round(ih*.934)
    magick(SRC/'print corrigindo o visual.png','-crop',f'{x1-x0}x{y1-y0}+{x0}+{y0}','+repage',pair)
    half=(x1-x0)//2;ph=y1-y0
    magick(pair,'-crop',f'{half}x{ph}+0+0','+repage',orig);magick(pair,'-crop',f'{half}x{ph}+{half}+0','+repage',fan)
    magick(orig,'-resize','1080x1920^','-gravity','center','-extent','1080x1920','-strip','PNG32:'+str(M/'Sonic_Original_Tela.png'))
    # Dois painéis verticais empilhados: o rosto inteiro continua visível no celular.
    panels=[]
    for i,(image,title)in enumerate([(orig,'ORIGINAL'),(fan,'EDIÇÃO DE FÃ')]):
        upper=P/'analise'/f'face_{i}.png';panel=P/'analise'/f'painel_{i}.png'
        magick(image,'-crop',f'{half}x{round(ph*.57)}+0+0','+repage','-resize','1080x840^','-gravity','center','-extent','1080x840','-gravity','north','-background','#f1e2c8','-splice','0x120','-fill','#241c30','-font','DejaVu-Sans-Bold','-pointsize','42','-annotate','+0+44',title,upper)
        panels.append(upper)
    magick(*panels,'-append','-strip','PNG32:'+str(M/'Comparacao_Paineis.png'))
    for src,name in [('meme1.jpg','Meme_Sonic_Poligonos_Tela.png'),('meme2.jpg','Meme_Sonic_Anel_Tela.png')]:
        magick(SRC/src,'-resize','1080x1920^','-gravity','center','-extent','1080x1920','-strip','PNG32:'+str(M/name))
    magick(M/'Sonic_Original_Tela.png','-blur','0x10','-brightness-contrast','-18x-5','-background','#104b7e','-alpha','remove','-alpha','off','-strip','PNG24:'+str(M/'Fundo_Tube.png'))
    # Peças do novo banco. As margens e a mesma matriz são preservadas em cada plano.
    chosen=['09_joinha','11_bracos_cruzados','20_tramando','03_explicando_duas_palmas','12_deu_de_ombros','21_bracinhos_trex','15_fazendo_ressalva','08_apontando_camera','29_pistolinhas']
    for stale in M.glob('Frente_*.png'):stale.unlink()
    def art(src,name):
        magick(src,'-virtual-pixel','transparent','-define','distort:viewport=1080x1920+0+0','-distort','AffineProjection','0.7,0,0,0.7,-177.5,344','+repage','-strip','PNG32:'+str(M/name))
    art(BANK/'camadas/cabeca_sem_bigode.png','Cabeca_Oculos.png');art(BANK/'camadas/bigode_repouso.png','Bigode.png')
    for ident in chosen:
        art(BANK/'camadas'/(ident+'_corpo.png'),'Corpo_'+ident+'.png')
        front=BANK/'camadas'/(ident+'_frente.png')
        if front.exists():art(front,'Frente_'+ident+'.png')
    print('MIDIAS_V2_PREPARADAS',flush=True)

def easing(keys,t):
    for a,b in zip(keys,keys[1:]):
        if t<=b[0]+1e-8:
            u=np.clip((t-a[0])/max(1e-8,b[0]-a[0]),0,1);u=u*u*(3-2*u);return np.array(a[1:])*(1-u)+np.array(b[1:])*u
    return np.array(keys[-1][1:])
def plan():
    events=[]
    def add(file,start,end,track,keys=None,reason='',part=None):
        if isinstance(track,int):start=round(start*30)/30;end=round(end*30)/30
        events.append(dict(file=file,start=start,end=end,track=track,keys=keys or [[0,.5,.5,1,1,0],[end-start,.5,.5,1,1,0]],reason=reason,part=part))
    def cam(file,start,end,track,knots,reason):
        start=round(start*30)/30;end=round(end*30)/30;dur=end-start
        dense=[]
        for i in range(round(dur*30)+1):
            t=i/30;x,y,s,r=easing(knots,t);dense.append([round(t,8),float(x),float(y),float(s),float(s),float(r)])
        add(file,start,end,track,dense,reason)
    def slide(file,start,end,track,mid=None,reason=''):
        dur=round(end*30)/30-round(start*30)/30
        ks=[[0,1.62,.51,1.02,1],[.18,.48,.50,1.035,-.5],[.3,.50,.50,1.01,0]]
        ks+=mid or [[dur*.65,.5,.5,1.12,0]]
        ks += [[dur-.17,.5,.5,1.09,0],[dur,-.62,.50,1.10,-1]]
        cam(file,start,end,track,ks,reason)
    cam('Fundo_Tube.png',0,D,0,[[0,.50,.50,1.12,0],[8,.54,.48,1.22,0],[17,.46,.51,1.16,0],[27,.53,.52,1.23,0],[D,.50,.50,1.15,0]],'Fundo da própria mídia em movimento, sem palco vazio')
    cam('Sonic_Original_Tela.png',0,1.4,2,[[0,.5,.5,1.02,0],[.38,.48,.51,1.16,-.4],[1.18,.50,.50,1.12,0],[1.4,-.65,.5,1.13,0]],'Gancho com Sonic ocupando o quadro')
    slide('Comparacao_Paineis.png',1.2,3.2,1,[[1.2,.5,.5,1.035,0]],'Comparação com identificação inequívoca original / edição de fã')
    slide('Meme_Sonic_Anel_Tela.png',3.1,5.45,2,[[.9,.53,.49,1.18,.3],[1.7,.5,.48,1.27,0]],'Piada da harmonização: meme grande com aproximação')
    slide('Meme_Sonic_Poligonos_Tela.png',5.35,7.95,1,[[1.2,.54,.47,1.18,0],[1.9,.5,.49,1.11,0]],'Sonic de polígonos: segundo tempo da piada')
    cam('Memories_Contexto.mp4',7.8,10.8,2,[[0,.5,.5,1.22,0],[.28,.5,.5,1.36,0],[1.5,.53,.51,1.60,0],[2.65,.50,.50,1.42,0],[3,.50,.50,1.42,0]],'Aproximação guiada da animação, à velocidade original')
    slide('Post_Critica_Tela.png',10.65,14.1,1,[[.9,.5,.60,1.15,0],[1.8,.50,.46,1.31,0],[2.8,.50,.48,1.18,0]],'Começa pelo texto/autoria e muda o foco para o Sonic')
    cam('Meme_Digitando.mp4',14,16.6,2,[[0,.50,.50,1.24,0],[.2,.50,.50,1.38,0],[1.5,.48,.49,1.51,0],[2.6,.50,.50,1.42,0]],'Internet criticando: meme animado com punch-in, 2,6 s')
    slide('Post_Correcao_Tela.png',16.5,20.9,1,[[1.1,.5,.59,1.16,0],[2.7,.5,.43,1.27,0],[3.8,.50,.48,1.14,0]],'Post corrigido: leitura inicial e foco na comparação, sem flash')
    cam('Meme_Metal_Encarando.mp4',22.9,24.9,2,[[0,.5,.5,1.30,0],[.20,.5,.5,1.43,0],[1.6,.51,.48,1.59,0],[2,.5,.5,1.46,0]],'Reação cômica ao comentário pessoal, meme do pacote')
    slide('Post_Frame_Tela.png',24.8,27.2,1,[[1.1,.50,.48,1.20,0],[1.7,.50,.48,1.28,0]],'Retoma qual frame causou as críticas antes do elogio')
    cam('Metal_Sonic_Acao.mp4',27,33.2,2,[[0,.5,.5,1.13,0],[.9,.5,.5,1.09,0],[2.4,.52,.50,1.17,0],[4.0,.56,.52,1.29,0],[5.8,.55,.51,1.20,0],[6.2,.54,.51,1.18,0]],'Luta contínua de 6,2 s; câmera reforça o ataque sem cortar a ação')
    a,sr=sf.read(M/'Voz_Dery_Original.wav',dtype='float32');assert sr==48000
    rms=np.array([np.sqrt(np.mean(a[max(0,round((i/30-.012)*sr)):min(len(a),round((i/30+.04)*sr))]**2)+1e-12)for i in range(N+1)])
    energy=gaussian_filter1d(np.clip((rms-.012)/max(.01,np.percentile(rms,85)-.012),0,1),.7);energy[rms<.006]=0
    acts=[('09_joinha',.25,1.08,.18,.82,.62,0),('11_bracos_cruzados',5.55,7.75,.28,.76,.83,-1.1),('20_tramando',14.2,16.55,.75,.81,.63,.8),('03_explicando_duas_palmas',20.85,22.35,.5,.54,1.18,-1.2),('12_deu_de_ombros',22.35,22.95,.5,.54,1.18,.7),('21_bracinhos_trex',22.95,24.85,.75,.82,.64,1),('15_fazendo_ressalva',24.9,27.0,.23,.82,.63,-.7),('08_apontando_camera',33.1,34.35,.5,.54,1.23,-.6),('29_pistolinhas',34.35,D,.5,.54,1.17,.8)]
    def rot(a):
        r=math.radians(a);return np.array([[math.cos(r),-math.sin(r)],[math.sin(r),math.cos(r)]])
    for index,(pose,start,end,x,y,sc,angle)in enumerate(acts):
        start=round(start*30)/30;end=round(end*30)/30;dur=end-start;rows=[]
        for i in range(round(start*30),round(end*30)+1):
            t=i/30;lt=t-start;entr=min(1,lt/.22);entr=entr*entr*(3-2*entr);out=min(1,max(0,(lt-(dur-.16))/.16));out=out*out*(3-2*out)
            y0=y+(1-entr)*.19+out*.12;s=sc*(.965+.035*entr+max(0,1-abs(lt-.45)/.32)*.016)
            center=np.array([540,960]);target=np.array([x*W,y0*H]);B=rot(angle)*s;hp=np.array([540,1100]);mp=np.array([540,950.9]);hr=-2.2*min(1,lt/.65)+1.1*min(1,max(0,(lt-.65)/.8));Hmat=rot(hr)
            hcenter=hp+Hmat@(center-hp);hpos=target+B@(hcenter-center);e=float(energy[min(i,N)]);sx=1+.025*e;sy=1+.075*e
            mc=mp+np.array([sx,sy])*(center-mp)+np.array([0,-2.6*e]);mh=hp+Hmat@(mc-hp);mpos=target+B@(mh-center)
            rows.append(dict(time=t,body=[x,y0,s,s,angle],head=[hpos[0]/W,hpos[1]/H,s,s,angle+hr],bigode=[mpos[0]/W,mpos[1]/H,s*sx,s*sy,angle+hr]))
        for part,name,tr in [('body','Corpo_'+pose+'.png',3),('head','Cabeca_Oculos.png',4),('bigode','Bigode.png',6)]:add(name,start,end,tr,[[round(r['time']-start,8),*r[part]]for r in rows],reason='Atuação '+pose,part=part)
        front='Frente_'+pose+'.png'
        if (M/front).exists():add(front,start,end,7,[[round(r['time']-start,8),*r['body']]for r in rows],part='body')
    add('Voz_Dery_Original.wav',0,35.092875,'voz',reason='Gravação original completa')
    add('Musica_Green_Hill_Baixa.wav',0,D,'musica')
    for t in [.02,1.2,3.1,5.35,7.8,10.65,14,16.5,20.85,22.9,24.8,27,33.1,34.35]:add('Whoosh.wav',t,t+.42,'sfx')
    for t in [1.5,16.8]:add('Clique.wav',t,t+.25,'sfx2')
    add('Bonk.wav',5.7,6.25,'sfx2');add('Som_Luta_Baixo.wav',27,33.2,'luta')
    payload=dict(title='Sonic — revisão pelo Massacote Tube',width=W,height=H,fps=30,frames=N,duration=D,voice_duration=35.092875,voice_sha256=hashlib.sha256((M/'Voz_Dery_Original.wav').read_bytes()).hexdigest(),events=events,eyes_animation=False,automatic_captions=False,psx_filter=False,reference='referencia/Massacote_Tube_Carros_Referencia.mp4')
    (P/'timeline.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n');print('PLANO_V2',len(events),flush=True);return payload
def render(p,stills=False):
    spec=importlib.util.spec_from_file_location('renderer',OLD/'scripts/produzir.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base);base.P=P;base.M=M
    base.render(p,preview=stills)
    if not stills:(P/'output/Massacote_Tube_Sonic_9x16.mp4').replace(P/'output/Massacote_Tube_Sonic_V2_9x16.mp4')
if __name__=='__main__':
    (P/'analise').mkdir(exist_ok=True);mode=sys.argv[1]if len(sys.argv)>1 else'all'
    if mode in ['all','prepare']:prepare()
    if mode in ['all','prepare','plan']:p=plan()
    else:p=json.loads((P/'timeline.json').read_text())
    if mode in ['all','render','stills']:render(p,mode=='stills')
