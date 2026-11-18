"""Produção horizontal do Massacote Tube com a voz intacta e mídia em camadas."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import shutil
import sys

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

P = Path(__file__).resolve().parents[1]
ROOT = P.parents[1]
TED = P.parent/'011-ted-virou-desenho'
sys.path.insert(0,str(TED/'scripts'))
import produzir as ted

TITLE='O_Novo_Garfield'
OUT=P/'output'
F=OUT/'Filmora'
M=F/'midias'
W,H,FPS,SR=1920,1080,30,48000
CENTER=np.array([W/2,H/2])
RIG=ROOT/'shorts/010-sonic-memories-beyond/production/recortes_regenerados_01/output/Filmora/midias_regeneradas'
MEMES=ROOT/'assets/biblioteca_memes'
CATALOG={e['tag']:e for e in json.loads((MEMES/'catalogo.json').read_text())['items']}
POSES={'esq':'04_apontando_esquerda','dir':'05_apontando_direita','cima':'06_apontando_cima',
       'joinha':'09_joinha','ombros':'12_deu_de_ombros','ressalva':'15_fazendo_ressalva',
       'susto':'16_desespero','tramando':'20_tramando','apresenta':'24_apresentando_lado'}
AUDIO={'voz':('Voz_PCM16.wav',2.0),'musica':('Trilha_Original.wav',0),
       'sfx':('Whoosh_Entrada_PCM16.wav',-8),'saida':('Swoosh_Saida_PCM16.wav',-13),
       'foley':('Clique_PCM16.wav',-8),'meme':('A62_Huh_PCM16.wav',-5)}
PRESS='https://www.paramountpressexpress.com/paramount-plus/shows/garfield/releases/?view=113583-everyones-favorite-lasagna-loving-feline-is-back-new-paramount-original-animated-series-garfield-premieres-december-11'
ANIMAG='https://www.animationmagazine.net/2026/11/new-garfield-2d-series-gets-purring-with-official-trailer-paramount-premiere-date/'

# Fonte, corte e duração útil em segundos. A matriz de mídia preserva a imagem central do trailer.
SHOTS={
    'Lasanha_Movimento':(35.00,2.43), 'Jantar_Animado':(37.66,1.76),
    'Olhos_e_Luz':(42.43,1.63), 'Bolha_Orbita':(44.95,3.87),
    'Garfield_e_Odie_Rua':(64.32,2.27), 'Janelas_Noturnas':(123.14,3.13),
    'Teclado_e_Expressoes':(131.94,2.86), 'Beco_Animado':(33.51,.86),
}
PRESS_IMAGES={
    'Sofa_Jon':'100_0001','Odie_Jardim':'100_0002','Arlene':'100_0003',
    'Garfield_Segunda':'100_0004','Odie_Escada':'101_0005','Cidade_Arlene':'101_0007',
    'Robo_Aspirador':'102_0001','Sofa_Reacao':'102_0014','Garfield_Jon_Susto':'104_0002',
    'Lasanha_Foto':'104_0009',
}
USER_IMAGES={
    'Filme_2024_Capa':'aJ0G','Filme_2024_Dupla':'garfield_3','Serie_3D':'nDVmw',
    'Serie_3D_Quarto':'AAAABX','Live_Action':'compose','Classico':'JU4u',
    'Livro_Tiras':'garfield_1','Tirinha':'Screenshot_2','Elenco_Trecho':'Screenshot_3',
    'Citao_2D':'Screenshot_1','Lamorne':'paramount-confirma','Arte_Roxa':'images.jpg',
    'Arte_Verde':'pw3Vz',
}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def sec(seconds):
    return round(seconds*FPS)/FPS


def canvas():
    return Image.new('RGBA',(W,H))


def graphic(name, palette):
    top,bottom,ink=map(np.array,palette)
    yy,xx=np.mgrid[:H,:W]
    weight=np.clip(.63*yy/H+.37*xx/W,0,1)[...,None]
    art=np.clip(top*(1-weight)+bottom*weight,0,255).astype('uint8')
    art=Image.fromarray(art).convert('RGBA')
    accents=canvas()
    d=ImageDraw.Draw(accents)
    center=(W*.83,H*.79)
    for x in range(-800,3100,245):
        d.polygon((center,(x,-300),(x+77,-300)),fill=(*map(int,ink),20))
    for y in range(22,H,26):
        for x in range(20,W,26):
            if x>W*.75 or y>H*.79:
                d.ellipse((x,y,x+3,y+3),fill=(255,237,205,38))
    for box in [(-120,-49,1450,790),( -107,-33,1466,806)]:
        d.rounded_rectangle(box, radius=64,outline=(*map(int,ink),26),width=3)
    art.alpha_composite(accents)
    art.convert('RGB').save(M/(name+'.png'))


def panel(im,name, limit=(1590,872), stroke='#fff1d0'):
    im=ImageOps.contain(im.convert('RGBA'),limit,Image.Resampling.LANCZOS)
    x,y=(W-im.width)//2,(H-im.height)//2
    shadow=canvas()
    ImageDraw.Draw(shadow).rounded_rectangle((x-12,y-7,x+im.width+18,y+im.height+24),radius=19,fill=(15,13,35,160))
    image=shadow.filter(ImageFilter.GaussianBlur(12))
    ImageDraw.Draw(image).rounded_rectangle((x-8,y-8,x+im.width+8,y+im.height+8),radius=11,fill=stroke)
    image.alpha_composite(im,(x,y))
    image.save(M/(name+'.png'))


def press_card(subject, heading, passage):
    # Trechos literais do comunicado, reformatados para leitura.
    paper=Image.new('RGB',(1460,670),'#fff4dd')
    d=ImageDraw.Draw(paper)
    path=Path('/usr/share/fonts/truetype/dejavu')
    marker=ImageFont.truetype(str(path/'DejaVuSans-Bold.ttf'),31)
    font_size=59
    bold=ImageFont.truetype(str(path/'DejaVuSans-Bold.ttf'),font_size)
    while max(bold.getlength(line) for line in heading.splitlines())>1308:
        font_size-=1
        bold=ImageFont.truetype(str(path/'DejaVuSans-Bold.ttf'),font_size)
    normal=ImageFont.truetype(str(path/'DejaVuSans.ttf'),40)
    d.rectangle((0,0,1460,98),fill='#203b76')
    d.text((76,32),'PARAMOUNT PRESS EXPRESS',font=marker,fill='#f5eddf')
    d.text((1384,32),'16 NOV 2026',font=marker,fill='#f5eddf',anchor='ra')
    d.multiline_text((76,145),heading,font=bold,fill='#1b2235',spacing=15)
    d.line((76,340,1384,340),fill='#cf9856',width=3)
    d.multiline_text((76,393),passage,font=normal,fill='#263951',spacing=16)
    panel(paper,subject,stroke='#fff6de')


def low_score(duration):
    n=round(duration*SR)
    bass=np.zeros(n,np.float32)
    brush=np.zeros_like(bass)
    beat=60/102
    rng=np.random.default_rng(29)

    def note(track,when,length,hz,amplitude,decay):
        i=round(when*SR)
        a=np.arange(min(round(length*SR),n-i))/SR
        env=np.minimum(1,a/.012)*np.exp(-a*decay)*np.minimum(1,(length-a)/.043)
        signal=.76*np.sin(2*np.pi*hz*a)+.24*np.sin(4*np.pi*hz*a)
        track[i:i+len(a)]+=amplitude*signal*env

    for i in range(math.ceil(duration/(4*beat))):
        start=.27+i*4*beat
        root=[65.406,48.999,55,58.270][(i//2)%4]
        if 105.75<start<116.3:
            continue
        for j,interval,strength in [(0,1,.049),(1.5,1.5,.037),(2.5,1.26,.034),(3.5,2,.018)]:
            t=start+j*beat
            if t<duration-.18:
                note(bass,t,.28,root*interval,strength,7.7)
        for j in (1,3):
            t=start+j*beat
            if t<duration-.18:
                i0=round(t*SR); a=np.arange(round(.095*SR))/SR
                wave=np.diff(rng.normal(0,1,len(a)+1))*np.exp(-a*46)*np.minimum(a/.007,1)
                brush[i0:i0+len(a)]+=.013*wave
        if i%4 in (0,2) and start+1.12<duration:
            note(brush,start+1.05,.45,root*6,.025,7.6)
    return np.stack([bass+brush,bass+np.roll(brush,108)*.7],axis=1)


def trailer_asset(ref, name):
    start,length=SHOTS[name]
    # Congela a última imagem do beco para completar o plano antes do corte da referência.
    isolated={'Beco_Animado','Olhos_e_Luz','Teclado_e_Expressoes'}
    if name not in isolated:
        ted.ff('-ss',f'{start-.20:.3f}','-i',ref,'-t',f'{length+.40:.3f}','-an',
               '-vf','crop=1184:666:48:26,scale=1920:1080:flags=lanczos,fps=30,setsar=1',
               '-c:v','libx264','-preset','veryfast','-crf',18,'-threads',2,
               '-pix_fmt','yuv420p',M/(name+'.mp4'))
        return
    span=.50 if name=='Beco_Animado' else length
    filter_chain=(f'trim=duration={span},setpts=PTS-STARTPTS,crop=1184:666:48:26,'
                  f'scale=1920:1080:flags=lanczos,fps=30,setsar=1,'
                  f'tpad=start_mode=clone:start_duration=0.2:stop_mode=clone:stop_duration={length+.214-span:.3f}')
    ted.ff('-ss',f'{start:.3f}','-i',ref,'-t',f'{length+.40:.3f}','-an',
           '-vf',filter_chain,'-c:v','libx264','-preset','veryfast','-crf',18,
           '-threads',2,'-pix_fmt','yuv420p',M/(name+'.mp4'))


def media(sources,press,duration):
    M.mkdir(parents=True,exist_ok=True)
    original=sources/'1 - VOZ.wav'
    shutil.copy2(original,F/'Voz_Original.wav')
    ted.ff('-i',original,'-af','pan=stereo|c0=c0|c1=c0','-ar',SR,'-c:a','pcm_s16le',M/AUDIO['voz'][0])
    old=TED/'revisao_03/output/Filmora/midias'
    for tag in ('sfx','saida','foley','meme'):
        name=AUDIO[tag][0]
        shutil.copy2(old/name,M/name)
    sf.write(M/AUDIO['musica'][0],low_score(duration),SR,subtype='PCM_16')
    for name,hue in {
            'Fundo_Coral':((126,50,41),(227,134,53),(254,199,123)),
            'Fundo_Ocre':((124,74,38),(226,161,86),(246,228,173)),
            'Fundo_Noturno':((35,22,68),(63,72,125),(149,145,247)),
            'Fundo_Verde':((26,62,58),(56,141,118),(175,223,178)),
            'Fundo_Azul':((29,54,96),(61,99,167),(165,211,237)),
    }.items():
        graphic(name,hue)
    for name,key in PRESS_IMAGES.items():
        panel(Image.open(press/f'Garfield_{key}.jpg'),name)
    for name,key in USER_IMAGES.items():
        src,=sources.glob(key+'*')
        panel(Image.open(src),name)
    panel(Image.open(press/'Poster_Garfield_2004.jpg').resize((512,759),Image.Resampling.LANCZOS),
          'Poster_2004',limit=(512,759),stroke='#ffe4b9')
    card=canvas()
    d=ImageDraw.Draw(card)
    d.rounded_rectangle((385,175,1535,905),radius=40,fill='#e6dfc9',outline='#fff8de',width=5)
    d.line((442,218,1453,218),fill='#897f65',width=3)
    d.line((442,872,1453,872),fill='#897f65',width=3)
    card.save(M/'Ficha_RG.png')
    for tag,name in [('I27','Meme_Desconfiado'),('I02','Meme_Madrugada')]:
        item=CATALOG[tag]
        path=MEMES/item['relative_file']
        assert sha(path)==item['sha256']
        panel(Image.open(path),name,limit=(994,790),stroke='#fdd597')

    press_card('Comunicado','NEW PARAMOUNT+ ORIGINAL ANIMATED\nSERIES GARFIELD PREMIERES DECEMBER 11',
               'Garfield will premiere globally Friday, December 11,\nwith all episodes of season one available to stream at launch.')
    press_card('Curtas_Nicktoons','I HATE MONDAYS\nNicktoons YouTube',
               'Beginning November 23, Paramount+ will release a new\nGarfield short every Monday leading up to the series premiere.')
    ref,=sources.glob('*.mp4')
    for name in SHOTS:
        trailer_asset(ref,name)
    for name in ('Cabeca_R3.png','Bigode_R3.png',*(f'Corpo_{v}_R3.png' for v in POSES.values())):
        src=Image.open(RIG/name).convert('RGBA').resize((821,1459),Image.Resampling.LANCZOS)
        artifact=canvas()
        artifact.alpha_composite(src,(550,-242))
        artifact.save(M/name)
    print('Mídias horizontais prontas',flush=True)


def make_plan(duration):
    events=[]

    def add(name, begin, end, track, knots, reason, offset=0.):
        begin,end=sec(begin),sec(end)
        knots=np.asarray(knots,float)
        n=round((end-begin)*FPS)
        times=np.arange(n+1)/max(1,n)
        keys=[]
        for i,t in enumerate(times):
            right=min(max(1,int(np.searchsorted(knots[:,0],t))),len(knots)-1)
            a,b=knots[right-1],knots[right]
            q=float(ted.ease((t-a[0])/(b[0]-a[0])))
            x,y,s,r=a[1:]+(b[1:]-a[1:])*q
            keys.append([i/FPS,x,y,s,s,r])
        events.append(dict(file=name,start=begin,end=end,track=track,keys=keys,offset=offset,reason=reason))

    def card(name,a,b,x=.50,y=.50,s=1.,lane=3,enter=0,leave=0):
        ep=min(.24,.40/(b-a))
        cut=max(.64,1-min(.22,.41/(b-a)))
        rad=enter*3.3
        points=[[0,x+enter*.36,y+.012*abs(enter),s*(.96 if enter else 1),rad],
                [ep,x,y,s,0],[cut,x-.010*enter,y-.011,s*1.024,0],
                [1,x+leave*.78,y-.019,s*(.91 if leave else 1.052),leave*4]]
        add(name+'.png',a,b,lane,points,'Mídia enviada ou imagem de imprensa')

    def clip(name,a,b,x=.5,y=.5,s=1.,transition=None):
        assert sec(b)-sec(a)<=SHOTS[name][1]+.025,(name,b-a)
        add(name+'.mp4',a,b,2,[[0,x,y,s,0],[1,x,y,s,0]],
            f'Recorte sem áudio da mídia do trailer mostrada na referência, origem {SHOTS[name][0]} s',.2)
        if transition:
            events[-1]['transition']=transition

    for i,(a,b,name) in enumerate([(0,25.8,'Coral'),(25.8,50,'Ocre'),(50,58.62,'Noturno'),
                                    (58.62,86.82,'Verde'),(86.82,106.37,'Ocre'),
                                    (106.37,118.1,'Noturno'),(118.1,133.64,'Azul'),(133.64,duration,'Coral')]):
        add('Fundo_'+name+'.png',a,b,0,[[0,.50,.50,1.07,(-1)**i],
                                      [1,.51,.50,1.095,(-1)**(i+1)]],'Fundo em composição')

    card('Live_Action',0,2.87,.248,.48,.60,3,-1,-1)
    card('Serie_3D',.62,3.77,.74,.49,.60,4,1,1)
    card('Filme_2024_Capa',2.87,4.57,.48,.48,.87,3,-1,-1)
    clip('Lasanha_Movimento',4.57,7.00)
    card('Lasanha_Foto',7.00,7.87,.50,.50,1.10)
    card('Sofa_Jon',7.87,10.60,.34,.51,.72,3,-1,-1)
    card('Comunicado',10.37,13.73,.66,.49,.68,4,1,1)
    clip('Olhos_e_Luz',13.73,15.33,transition='Basic Zoom In')
    clip('Jantar_Animado',15.33,17.03)
    card('Tirinha',17.03,19.17,.35,.53,.84,3,-1,0)
    card('Lasanha_Foto',17.67,19.17,.746,.49,.55,4,1,0)
    card('Live_Action',19.17,22.30,.54,.49,1.05)
    card('Meme_Desconfiado',22.30,25.80,.32,.51,.82,3,-1,-1)
    card('Tirinha',25.80,29.23,.283,.52,.91,3,-1,0)
    card('Livro_Tiras',28.23,32.00,.732,.52,.96,4,1,1)
    card('Tirinha',29.23,31.97,.295,.52,.86,3,0,-1)
    card('Classico',32.00,37.13,.49,.50,1.05)
    card('Arte_Roxa',37.13,39.55,.254,.50,.6,3,-1,-1)
    card('Serie_3D_Quarto',37.87,41.08,.745,.49,.57,4,1,1)
    card('Live_Action',41.08,44.53,.35,.49,.73,3,-1,-1)
    card('Poster_2004',41.08,44.53,.79,.50,.98,4,1,1)
    card('Serie_3D',44.53,46.58,.50,.50,1.02)
    card('Filme_2024_Capa',46.58,48.88,.48,.50,1.04,3,-1,-1)
    card('Filme_2024_Dupla',48.88,50,.50,.50,1.01)
    card('Ficha_RG',51.05,58.60,.31,.488,1.02,1,-1,-1)
    for name,a,b in [('Arte_Verde',51.05,52.90),('Live_Action',52.90,54.67),
                     ('Serie_3D',54.67,56.32),('Arte_Roxa',56.32,58.60)]:
        card(name,a,b,.31,.49,.66,3,-1,-1)
    clip('Garfield_e_Odie_Rua',58.60,60.84)
    card('Sofa_Reacao',60.84,64.15,.57,.50,.99)
    card('Meme_Madrugada',64.15,66.87,.66,.50,.82,4,1,1)
    card('Garfield_Segunda',66.87,70.9,.53,.50,1.03)
    clip('Beco_Animado',70.9,71.73)
    card('Cidade_Arlene',71.73,75.25,.51,.51,1.04,3,-1,-1)
    card('Odie_Escada',75.25,77.10,.50,.51,1.06)
    card('Odie_Jardim',77.10,79.35,.27,.50,.59,3,-1,-1)
    card('Arlene',77.73,81.84,.74,.49,.58,4,1,1)
    card('Elenco_Trecho',81.84,86.83,.427,.71,.96,4,1,0)
    clip('Janelas_Noturnas',81.84,84.97,.46,.375,.69)
    card('Robo_Aspirador',84.97,86.83,.35,.374,.67,3,-1,-1)
    clip('Lasanha_Movimento',86.83,89.26)
    card('Citao_2D',89.26,91.32,.52,.61,1.06,4,1,1)
    clip('Garfield_e_Odie_Rua',91.32,93.58,transition='Fast Bounce')
    clip('Teclado_e_Expressoes',93.58,96.43)
    card('Garfield_Jon_Susto',96.43,97.65,.50,.50,1.04)
    card('Tirinha',97.65,101.92,.29,.51,.90,3,-1,-1)
    card('Lasanha_Foto',98.15,101.92,.72,.50,.60,4,1,1)
    clip('Bolha_Orbita',101.92,105.77)
    card('Arte_Verde',105.77,107.68,.59,.50,.83,4,1,0)
    card('Lamorne',107.68,111.13,.33,.52,.72,3,-1,-1)
    card('Garfield_Jon_Susto',111.13,113.80,.69,.50,.66,4,1,1)
    card('Arte_Roxa',114.46,118.10,.70,.50,.63,4,1,1)
    card('Comunicado',118.10,125.77,.52,.50,1.11,3,-1,0)
    card('Curtas_Nicktoons',125.77,132.13,.51,.51,1.10,3,1,0)
    card('Garfield_Segunda',132.13,135.50,.53,.51,1.06)
    card('Robo_Aspirador',135.50,138.95,.54,.50,1.03)
    clip('Jantar_Animado',138.95,140.68)
    card('Lasanha_Foto',140.68,143.30,.54,.49,1.05)
    card('Lasanha_Foto',143.30,duration,.237,.47,.53,3,-1,0)
    card('Filme_2024_Dupla',143.30,duration,.767,.47,.53,4,1,0)

    speech,sr=sf.read(F/'Voz_Original.wav',dtype='float32')
    level=[]
    for i in range(round(duration*FPS)+1):
        idx=round(i*sr/FPS)
        win=speech[max(0,idx-520):min(len(speech),idx+960)]
        level.append(float(np.sqrt(np.mean(win**2))) if len(win) else 0.)
    loud=np.convolve(np.clip((np.array(level)-.018)/.080,0,1),[.2,.6,.2],mode='same')
    poses=[
        (0,.62,'ombros',.50,.612,.52,-2),
        (7.87,10.37,'esq',.79,.58,.69,-1),(10.37,13.73,'dir',.195,.61,.68,2),
        (22.30,25.80,'esq',.795,.58,.72,-2),
        (25.80,28.23,'esq',.75,.60,.60,-1),
        (36.1,37.13,'apresenta',.825,.68,.47,1),
        (37.13,41.08,'ombros',.50,.765,.53,-1),
        (50,51.05,'tramando',.50,.57,.99,-2),(51.05,54.67,'esq',.774,.57,.80,-1),
        (54.67,58.6,'susto',.775,.58,.77,1),
        (64.15,66.87,'dir',.20,.55,.72,1),
        (77.10,81.84,'apresenta',.50,.762,.57,2),
        (81.84,86.83,'ressalva',.885,.50,.49,-1),(89.26,91.32,'cima',.24,.36,.50,1),
        (105.77,107.68,'tramando',.21,.55,.76,-2),
        (107.68,111.13,'esq',.786,.55,.74,-1),(111.13,113.8,'dir',.22,.58,.69,2),
        (113.8,114.46,'ombros',.505,.53,1.04,0),(114.46,118.1,'ressalva',.26,.56,.82,-1),
        (124.7,125.77,'cima',.866,.74,.54,1),(130.1,132.13,'cima',.87,.77,.51,-1),
        (143.30,146.23,'ombros',.50,.70,.69,-2),(146.23,duration,'joinha',.50,.706,.70,-1),
    ]
    neck=np.array([960.,554.]); must=np.array([960.,479.])
    for a,b,pose,x,y,scale,lean in poses:
        a,b=sec(a),sec(b)
        n=round((b-a)*FPS)
        areas=[[],[],[]]
        for i in range(n+1):
            t=i/FPS
            u=i/n
            settle=1-float(ted.ease(t/.22))
            accent=float(ted.ease(u/.34))*(1-.77*float(ted.ease((u-.39)/.56)))
            cx=x*W+lean*8*accent
            cy=y*H+29*settle-7*accent
            s=scale*(1+.029*accent-.025*settle)
            rot=lean*(.40+.67*accent)
            tilt=lean*.48*accent
            body=ted.rotation(rot)*s
            head=ted.rotation(tilt)
            center=np.array([cx,cy])
            nh=center+body@(neck+head@(CENTER-neck)-CENTER)
            en=loud[min(len(loud)-1,round(a*FPS)+i)]
            stretch=np.array([1+.010*en,1+.032*en])
            lip=must+stretch*(CENTER-must)
            mm=center+body@(neck+head@(lip-neck)-CENTER)
            for surface,p,sz,r in zip(areas,(center,nh,mm),((s,s),(s,s),s*stretch),(rot,rot+tilt,rot+tilt)):
                surface.append([t,p[0]/W,p[1]/H,*sz,r])
        for lane,name,keys in zip((5,6,7),(f'Corpo_{POSES[pose]}_R3.png','Cabeca_R3.png','Bigode_R3.png'),areas):
            events.append(dict(file=name,start=a,end=b,track=lane,keys=keys,offset=0.,
                               reason='Massacote 2D · '+pose))

    def sound(tag,start):
        file,db=AUDIO[tag]
        samples=sf.info(M/file).frames
        end=round(start*SR+samples)/SR
        events.append(dict(file=file,start=start,end=end,track=tag,offset=0.,
                           mix_gain_db=db,reason='Narração integral' if tag=='voz' else 'Faixa independente'))

    sound('voz',0)
    sound('musica',0)
    for start in (4.42,7.89,17.,25.79,37.11,58.57,81.69,97.61,118.08,125.71,143.26):
        sound('sfx',start)
    for start in (13.37,24.96,31.64,80.97,117.71):
        sound('saida',start)
    for start in (33.27,51.05,52.90,54.67,56.32,70.88,106.36,125.74):
        sound('foley',start)
    sound('meme',105.98)
    return dict(name='O Novo Garfield',width=W,height=H,fps=FPS,duration=duration,
                frames=round(duration*FPS),voice_sha256=sha(F/'Voz_Original.wav'),
                events=events,preview_seconds=[0.,2.,4.63,8.8,12,17.8,23.15,29.5,33.8,40.1,
                45,52.0,57.2,61.4,66.26,73,76.1,79,83.3,87.3,92.2,95,
                100,104,107,109,115.7,121,128,136.8,144.2,147.0])


def main():
    p=argparse.ArgumentParser()
    p.add_argument('mode',choices=('prepare','preview','render'))
    p.add_argument('root',type=Path)
    p.add_argument('temp',type=Path)
    a=p.parse_args()
    a.temp.mkdir(parents=True,exist_ok=True)
    if a.mode=='prepare':
        sources=a.root/'O NOVO GARFIELD É'
        voice=sf.info(sources/'1 - VOZ.wav')
        assert voice.samplerate==SR
        duration=math.ceil(voice.frames*FPS/SR)/FPS
        media(sources,a.root/'imprensa',duration)
        data=make_plan(duration)
        (P/'timeline.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
        print(len(data['events']),'clipes planejados',flush=True)
    else:
        ted.W,ted.H,ted.CENTER,ted.M,ted.OUT,ted.TITLE=W,H,CENTER,M,OUT,TITLE
        ted.render(json.loads((P/'timeline.json').read_text()),a.temp,a.mode=='preview')


if __name__=='__main__':
    main()
