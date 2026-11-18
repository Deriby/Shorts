"""Revisão do Ted com pontes ópticas, saídas e faixas de áudio editáveis."""
from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile
import argparse
import json
import math
import shutil
import sys

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw
from scipy.signal import butter, sosfilt

P = Path(__file__).resolve().parents[1]
SOURCE = P.parent
OUT = P / 'output'
F = OUT / 'Filmora'
M = F / 'midias'
TITLE = 'TED_virou_DESENHO_R2'
sys.path.insert(0, str(SOURCE/'scripts'))
import produzir as v1

FPS, W, H, SR = v1.FPS, v1.W, v1.H, v1.SR
TL = 'ProjectFolder/Medias/{204E72A3-B517-44d4-806F-9E9D84D5F904}/timeline.wesproj'
VISUAL_TRACKS = v1.VISUAL_TRACKS
AUDIO = {
    'voz': ('Voz_Editavel_PCM16.wav', 5.0), 'musica': ('Stinger_Animacao_PCM16.wav', -17),
    'sfx':('Whoosh_Entrada_PCM16.wav', -5), 'foley':('Clique_PCM16.wav', -3),
    'meme':('A62_Huh_PCM16.wav', 0), 'saida':('Swoosh_Saida_PCM16.wav', -9),
    'impacto':('Impacto_Grave_PCM16.wav', -12),
}
LENSES = {
    'R3': np.array([[465,843],[629,839]],float),
    'Choque': np.array([[321,817],[777,811]],float),
    'Desconfianca': np.array([[292,787],[742,895]],float),
}


def frame(seconds):
    return round(seconds*FPS)


def sec(frames):
    return frames/FPS


def write_json(path, value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def transform_vector(vector, ref, angle):
    return v1.rotation(angle) @ (np.array(vector)*np.array(ref))


def ease(t):
    return float(v1.ease(t))


def samples(event, first, last):
    keys = event['keys']
    s = frame(event['start'])
    out = [keys[min(max(i-s,0),len(keys)-1)][1:] for i in range(first,last+1)]
    return np.array(out, dtype=float)


def rebase(event, first, last):
    result = deepcopy(event)
    result['start'], result['end'] = sec(first), sec(last)
    if 'keys' in event:
        entries = samples(event,first,last)
        result['keys'] = [[sec(i),*map(float,row)] for i,row in enumerate(entries)]
    return result


def card_out(event, exit_axis=None):
    """Retoma a posição e a velocidade da própria entrada e conclui fora do quadro."""
    name = event['file']
    keys = event['keys']
    count = len(keys)-1
    tail = min(12,max(6,round(count*.28)))
    sign = 1 if keys[0][1] > keys[min(12,count)][1] else -1
    # Um painel central usa o eixo vertical; os laterais voltam para seu lado.
    center = abs(keys[0][1]-keys[min(12,count)][1]) < .08
    i0 = count-tail
    start = np.array(keys[i0][1:])
    final = start.copy()
    if center or exit_axis == 'vertical':
        final[1] = -.58 if name.startswith('Anuncio') or name.startswith('Sofa') else 1.58
    else:
        final[0] = 1.51 if sign == 1 else -.51
    final[2:4] *= .87
    if not center:
        final[4] += 7 if sign==1 else -7
    for i in range(i0+1,count+1):
        q = ease((i-i0)/tail)
        keys[i][1:] = list(start + (final-start)*q)
    event['reason'] += ' · saída animada antes do fim'
    return sec(frame(event['start'])+i0)


def read_native(path):
    with ZipFile(path) as z:
        doc=json.loads(z.read(TL))
    return next(t for t in doc['timelineInfos'] if t['timelineId']==doc['currentTimelineId'])


def ted_timing(plan, reference):
    """Mantém os recortes e chaves salvos pelo usuário nos clipes correspondentes."""
    tracks = {6:0,7:'cenario',8:1,9:2,10:3,11:4,12:5,13:6,14:7,15:8}
    native = read_native(reference)
    index = {}
    for tr in native['trackInfos']:
        if tr.get('trackTag') not in tracks or tr['trackType']!=1:
            continue
        for clip in tr['clipList']:
            name = Path(clip.get('filename','')).name
            if not name.endswith(('.png','.mp4')):
                continue
            key = (tracks[tr['trackTag']],name,frame(clip['tlBegin']/1e7))
            index[key] = clip
    events = []
    for event in plan['events']:
        track = event['track']
        if track not in VISUAL_TRACKS:
            continue
        key = (track,event['file'],frame(event['start']))
        matches = [index.get((key[0],key[1],key[2]+delta)) for delta in (0,1,-1)]
        clip = next((c for c in matches if c is not None),None)
        if clip is None:
            if track == 'cenario':
                continue  # O usuário retirou o ambiente do primeiro sofá.
            events.append(event)
            continue
        new_start, new_end = [frame(clip[k]/1e7) for k in ('tlBegin','tlEnd')]
        entry = rebase(event,new_start,new_end)
        entry['offset'] = clip['inPoint']/1e7
        events.append(entry)
    return events


def stage_media(events):
    root = SOURCE/'output/Filmora'
    for name in sorted({row['file'] for row in events if row['track'] in VISUAL_TRACKS and row['track']!=0}):
        shutil.copy2(root/'midias'/name,M/name)
    shutil.copy2(root/'Voz_Original.wav',F/'Voz_Original.wav')


def local_background(events, reference):
    """Aproxima o fundo azul/rosa da miniatura do Ted para o MP4 e o WFP portátil."""
    native = read_native(reference)
    template = next(tr for tr in native['trackInfos'] if tr['trackType']==1 and
                    any(c.get('filename','').endswith('downloadCommonCfg.cof') for c in tr['clipList']))
    measures = [(0, (60,78,247), (238,109,255)),
                (.015, (65,83,247), (240,112,255)),
                (-.02, (58,77,244), (241,114,255))]
    yy, xx = np.mgrid[:H,:W]
    weight = (yy / (H-1))[...,None]**1.13
    for i,(stock,(phase,top,bottom)) in enumerate(zip(template['clipList'],measures,strict=True)):
        name = f'Fundo_Radial_{i+1}.png'
        theta = np.arctan2(xx-557, 2160-yy) + phase
        light = ((theta + .10) % .30 < .146)[...,None]
        gradient = np.array(top)*(1-weight) + np.array(bottom)*weight
        overlay = np.array([-28,-5,-3])*(1-weight) + np.array([-61,-43,-9])*weight
        art = Image.fromarray(np.clip(gradient + overlay*light,0,255).astype(np.uint8))
        d=ImageDraw.Draw(art)
        for x,y,rx,ry in [(-10,1852,220,248),(182,1958,265,264),(491,1993,275,252),
                           (780,1946,258,267),(1054,1881,222,234)]:
            d.ellipse((x-rx,y-ry,x+rx,y+ry),fill=(242,119,248))
        art.save(M/name)
        start,end=[frame(stock[k]/1e7) for k in ('tlBegin','tlEnd')]
        n=end-start
        rows=[]
        for j in range(n+1):
            u=j/n
            sweep=math.sin(math.pi*(u-.5))
            rows.append([sec(j),.5+sweep*.018,.501+.012*math.sin(2*math.pi*u),
                         1.089,1.089,sweep*1.9])
        events.append(dict(file=name,start=sec(start),end=sec(end),track=0,offset=0.,keys=rows,
                           reason='Fundo local derivado da paleta do Ted editado pelo usuário'))


def synthesize():
    rng = np.random.default_rng(772)
    t = np.arange(round(3.1*SR))/SR
    impact = (.42*np.sin(2*np.pi*(38*t+21*(1-np.exp(-5*t))))*np.exp(-4.5*t)
              +.15*np.sin(2*np.pi*64*t)*np.exp(-6*t))
    noise = sosfilt(butter(3,145,fs=SR,output='sos'),rng.normal(size=len(t)))
    impact += .11*noise*np.exp(-5*t)
    impact *= np.minimum(1,t/.015)*np.minimum(1,(3.1-t)/.12)
    sf.write(M/AUDIO['impacto'][0],np.column_stack([impact,impact]),SR,subtype='PCM_16')

    t = np.arange(round(1.2*SR))/SR
    stinger = np.zeros(len(t))
    for n,freq in enumerate([440,587.33,739.99,880]):
        a=np.maximum(0,t-n*.091)
        signal=np.sin(2*np.pi*freq*a)+.27*np.sin(2*np.pi*freq*2*a)
        stinger+=.34*signal*np.exp(-10*a)*np.minimum(1,a/.021)
    stinger *= np.minimum(1,(1.2-t)/.10)
    sf.write(M/AUDIO['musica'][0],np.column_stack([stinger,stinger]),SR,subtype='PCM_16')


def prepare_audio(events):
    old = SOURCE/'output/Filmora/midias'
    for tag,src in [('voz',F/'Voz_Original.wav'),('sfx',old/'Whoosh.wav'),
                    ('foley',old/'Clique.wav'),('meme',old/'A62_Huh.wav')]:
        rematrix = ['-af','pan=stereo|c0=c0|c1=c0'] if tag=='voz' else []
        v1.ff('-i',src,*rematrix,'-ac',2,'-ar',SR,'-c:a','pcm_s16le',M/AUDIO[tag][0])
    # Os efeitos antigos decodificavam, mas a entrada e o clique tinham RMS abaixo de -55 dBFS.
    # O arquivo recebe nível útil e margem de pico; o ganho de mixagem continua no WFP.
    for tag, target_db in [('sfx',-25),('foley',-33),('meme',-36)]:
        target = M/AUDIO[tag][0]
        audio, rate = sf.read(target,always_2d=True)
        rms = np.sqrt(np.mean(audio**2))
        amplification = min(10**(target_db/20)/rms, .68/np.max(np.abs(audio)))
        sf.write(target,audio*amplification,rate,subtype='PCM_16')
    meme=v1.CATALOG['A87']
    path=v1.MEMES/meme['relative_file']
    assert v1.sha(path)==meme['sha256']
    v1.ff('-ss','0.196','-i',path,'-t','0.40','-af','afade=t=out:st=0.25:d=0.15',
          '-ar',SR,'-ac',2,'-c:a','pcm_s16le',M/AUDIO['saida'][0])
    synthesize()

    def sound(tag, at, genre=''):
        name,gain = AUDIO[tag]
        length = sf.info(M/name).frames/SR
        event = dict(file=name,start=at,end=round((at+length)*SR)/SR,track=tag,offset=0.,
                     reason=genre or 'Clip de áudio independente',mix_gain_db=gain)
        events.append(event)
        return event

    sound('voz',0,'Gravação integral do usuário; ganho em VolumeGain')
    sound('musica',0,'Sinal de abertura local no lugar da mídia do catálogo')
    sound('impacto',sec(205),'Impacto grave local no ponto de entrada do efeito salvo pelo usuário')
    for at in (1.,10.45,22.8,24.57,31.8):
        sound('sfx',at)
    for at in (3.54,20.70,34.17):
        sound('foley',at)
    sound('meme',37.00,'Meme A62 “Huh?” do banco')
    for at in (10.63,24.99,33.83,36.42):
        sound('saida',at,'Swoosh A87 do banco, na cauda das janelas')


def close_reaction(events, name, push_start, hold_start, hold_end, pull_end, previous, following):
    """Aplica a mesma câmera ao corpo, cabeça e bigode e registra as lentes entre as duas artes."""
    first, opaque, hold, end = map(frame,(push_start,hold_start,hold_end,pull_end))
    exiting = hold<end
    fade = 6
    target = []
    actors = []
    for track in (5,6,7):
        scene = next(e for e in events if e['track']==track and frame(e['start'])==frame(previous))
        after = next((e for e in events if e['track']==track and following is not None
                      and frame(e['start'])==frame(following)),None)
        events.remove(scene)
        if after is not None:
            events.remove(after)
            events.append(rebase(after,end,frame(after['end'])))
        base_from = samples(scene,first,first)[0]
        base_to = samples(after,end,end)[0] if after is not None else base_from
        actors.append((scene,base_from,base_to))

    pix = np.array([W,H],float)
    center = pix/2
    original_lenses = LENSES['R3']
    realistic = LENSES[name]
    original_delta = original_lenses[1]-original_lenses[0]
    real_delta = realistic[1]-realistic[0]
    ratio = np.linalg.norm(real_delta)/np.linalg.norm(original_delta)
    angle = math.degrees(math.atan2(real_delta[1],real_delta[0]) -
                         math.atan2(original_delta[1],original_delta[0]))
    original_center = original_lenses.mean(axis=0)
    detail_center = realistic.mean(axis=0)
    original_pivot = original_center-center
    native_pivot = detail_center-center

    def real_pose(i):
        progress = np.clip((i-opaque)/max(1,hold-opaque),0,1)
        sc = 1.018 + .035*progress
        x = .504 if name=='Choque' else .5
        return [x,.502-.012*progress,sc,sc,0.]

    def match_pose(i):
        x,y,sc,_,_ = real_pose(i)
        lens = np.array([x,y])*pix+native_pivot*sc
        size = ratio*sc
        headpos = lens-v1.rotation(angle) @ (original_pivot*size)
        return headpos/pix,size,lens

    def stage_pivot(parts):
        x,y,sx,sy,theta = parts
        base = np.array([x,y])*pix
        return base+transform_vector(original_pivot,(sx,sy),theta)

    for i in range(first,end+1):
        pos, size, lens = match_pose(i)
        q_from = ease((i-first)/(opaque-fade-first+2))
        q_to = ease((i-hold-fade+1)/(end-hold-fade+1)) if exiting else 0.
        target.append((pos,size,lens,q_from,q_to))
    for scene,a,b in actors:
        keys = []
        for i in range(frame(scene['start']),end+1):
            if i < first:
                keys.append(samples(scene,i,i)[0].tolist())
                continue
            _,zoom,lens,q_from,q_to = target[i-first]
            head_a,head_b = actors[1][1:]
            start_lens, end_lens = (stage_pivot(k) for k in (head_a,head_b))
            target_lens = (start_lens+(lens-start_lens)*q_from)*(1-q_to)+end_lens*q_to
            sx,sy = (a[2:4]+(zoom-a[2:4])*q_from)*(1-q_to)+b[2:4]*q_to
            rot = (a[4]+(angle-a[4])*q_from)*(1-q_to)+b[4]*q_to
            # Camadas antes/depois conservam deslocamentos relativos e o close converge na lente.
            pa=np.array(a[:2])*pix-start_lens
            pb=np.array(b[:2])*pix-end_lens
            close=-transform_vector(original_pivot,(sx,sy),rot)
            if scene['track']==7:
                close += transform_vector((0,-1.3),(sx,sy),rot)
            relative=(pa+(close-pa)*q_from)*(1-q_to)+pb*q_to
            dest=(target_lens+relative)/pix
            keys.append([float(dest[0]),float(dest[1]),float(sx),float(sy),float(rot)])
        start=frame(scene['start'])
        # A troca de pose acontece atrás do quadro realista.
        if exiting:
            swap = hold-1
            for source, pfrom, pto in [(scene,start,swap),
                                       (next(e for e in events if e['track']==scene['track'] and frame(e['start'])==end),swap,end)]:
                row=deepcopy(source)
                row.update(start=sec(pfrom),end=sec(pto),keys=[[sec(j),*k] for j,k in enumerate(keys[pfrom-start:pto-start+1])])
                events.append(row)
        else:
            scene.update(end=sec(end), keys=[[sec(j),*values] for j,values in enumerate(keys)])
            events.append(scene)

    src = f'Reacao_{name}.png'
    image = Image.open(M/src).convert('RGBA')

    def add(file,a,b,why):
        if b<=a:
            return
        events.append(dict(file=file,start=sec(a),end=sec(b),track=8,offset=0.,reason=why,
                           keys=[[sec(i-a),*real_pose(i)] for i in range(a,b+1)]))

    for j in range(fade):
        alpha = round(255*ease((j+1)/(fade+1)))
        name_plate=f'{name}_Dissolve_{j+1:02d}.png'
        im=image.copy()
        im.putalpha(alpha)
        im.save(M/name_plate)
        add(name_plate,opaque-fade+j,opaque-fade+j+1,'Mistura progressiva com lentes registradas')
        if exiting:
            add(name_plate,hold+fade-1-j,hold+fade-j,'O detalhe volta ao avatar 2D')
    add(src,opaque,hold,'Close realista sustentado com zoom residual')


def prepare(reference):
    plan=json.loads((SOURCE/'timeline.json').read_text())
    events=ted_timing(plan,reference)
    events=[e for e in events if e['track'] not in (0,8)]
    M.mkdir(parents=True,exist_ok=True)
    for name in ('Reacao_Choque.png','Reacao_Desconfianca.png'):
        shutil.copy2(SOURCE/'output/Filmora/midias'/name,M/name)
    stage_media(events)
    local_background(events,reference)
    for e in events:
        if e['track'] in (3,4) or e['file']=='Sofa_Quadro.png' and e['track']==2:
            card_out(e)
        if e['track']==2 and e['file'] in ('Depois_Da_Transformacao.mp4','Maturidade.mp4','Sofa_Filme.mp4'):
            card_out(e, 'vertical')
            for border in events:
                if border['track']==1 and border['start']==e['start'] and border['end']==e['end']:
                    border['keys']=deepcopy(e['keys'])
    close_reaction(events,'Choque',6.47,7.13,8.60,9.03,4.77,7.5)
    close_reaction(events,'Desconfianca',36.57,37.27,plan['duration'],plan['duration'],35.73,None)
    prepare_audio(events)
    plan['events']=events
    plan['voice_sha256']=v1.sha(F/'Voz_Original.wav')
    plan['revision']=2
    plan['preview_seconds']=[6.47,6.60,6.77,6.93,7.03,7.13,7.80,8.50,8.62,8.73,8.87,9.03,10.56,10.70,10.83,24.93,25.1,25.20,25.30,33.82,34.02,34.13,36.57,36.73,36.90,37.07,37.20,37.27,38.65]
    plan['realistic_holds']=[dict(name='Choque',visible=[sec(frame(7.13)),sec(frame(8.60))]),
                             dict(name='Desconfianca',visible=[sec(frame(37.27)),plan['duration']])]
    (P/'timeline.json').write_text(json.dumps(plan,ensure_ascii=False,separators=(',',':'))+'\n')
    print(f'{len(events)} clipes preparados',flush=True)


def render(temp, mode):
    v1.M, v1.OUT, v1.TITLE = M, OUT, TITLE
    plan = json.loads((P/'timeline.json').read_text())
    if mode == 'mix':
        v1.mix_export(plan,temp,temp/'sem_audio.mp4')
    else:
        v1.render(plan,temp,mode=='preview')


def main():
    args=argparse.ArgumentParser()
    args.add_argument('mode',choices=('prepare','render','preview','mix'))
    args.add_argument('reference',type=Path)
    args.add_argument('temp',type=Path)
    opt=args.parse_args()
    opt.temp.mkdir(parents=True,exist_ok=True)
    if opt.mode=='prepare':
        prepare(opt.reference)
    else:
        render(opt.temp,opt.mode)


if __name__=='__main__':
    main()
