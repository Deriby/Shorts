"""Monta o short a partir das fontes extraídas e do banco do Tube."""
from pathlib import Path
import argparse
import hashlib
import io
import json
import math
import shutil
import subprocess

import cv2
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter, ImageOps

P = Path(__file__).resolve().parents[1]
R = P.parents[1]
OUT = P / 'output'
F = OUT / 'Filmora'
M = F / 'midias'
FPS, W, H = 30, 1080, 1920
SR = 48000
CENTER = np.array([W / 2, H / 2])
SONIC = R / 'shorts/010-sonic-memories-beyond/production'
RIG = SONIC / 'recortes_regenerados_01/output/Filmora/midias_regeneradas'
FRAMES = R / 'assets/personagens/massacote_tube_2d/frames_comicos/lote_01/9x16'
MEMES = R / 'assets/biblioteca_memes'
CATALOG = {row['tag']: row for row in json.loads((MEMES / 'catalogo.json').read_text())['items']}
TITLE = 'TED_virou_DESENHO'
VOICE = 'Voz_Mix_Integral.wav'
VISUAL_TRACKS = (0, 'cenario', 1, 2, 3, 4, 5, 6, 7, 8)
POSE = {
    'direita': '05_apontando_direita',
    'cima': '06_apontando_cima', 'joinha': '09_joinha', 'ombros': '12_deu_de_ombros',
    'ressalva': '15_fazendo_ressalva', 'assustado': '16_desespero',
    'tramando': '20_tramando', 'apresenta': '24_apresentando_lado',
}

# Tempos na narração; a coluna fonte é o ponto de entrada no trailer oficial.
VIDEOS = [
    ('Sofa_Animado', 1.00, 3.47, 9.87, 'quadro'),
    ('Depois_Da_Transformacao', 4.77, 6.93, 21.06, 'quadro'),
    ('Vizinhos', 12.63, 14.90, 75.34, 'quadro'),
    ('Familia', 14.90, 16.43, 36.04, 'quadro'),
    ('Trabalho', 16.43, 17.40, 64.27, 'quadro'),
    ('Maturidade', 17.40, 20.69, 71.64, 'quadro'),
    ('Sofa_Filme', 29.13, 31.80, 6.81, 'quadro'),
    ('Ted_Aniversario', 34.17, 35.73, 98.65, 'vertical'),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ff(*args):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *map(str, args)], check=True)


def at(t):
    return round(t * FPS) / FPS


def canvas():
    return Image.new('RGBA', (W, H))


def graphic(colors, name):
    base, light, accent, second = colors
    # Composição gráfica em diagonais, com retícula e luz lateral em baixa intensidade.
    layer = Image.new('RGB', (W, H), base)
    shapes = Image.new('RGBA', layer.size)
    d = ImageDraw.Draw(shapes)
    d.ellipse((-710, -840, 1310, 1350), fill=(*light, 125))
    d.ellipse((160, 950, 1630, 2690), fill=(*second, 107))
    layer.paste(shapes, mask=shapes.getchannel('A').filter(ImageFilter.GaussianBlur(175)))
    d = ImageDraw.Draw(layer, 'RGBA')
    d.polygon([(-20, 1530), (1100, 1070), (1100, 1140), (-20, 1600)], fill=(*accent, 20))
    d.polygon([(-20, 280), (1100, -30), (1100, 28), (-20, 340)], fill=(*accent, 27))
    for offset in (0, 28, 65):
        d.line([(-60, 1640 + offset), (1140, 1125 + offset)], fill=(*accent, 52), width=3)
        d.line([(-60, 420 + offset), (1140, 65 + offset)], fill=(*accent, 62), width=3)
    for y in range(36, H, 28):
        for x in range(25, W, 28):
            a = 17 + round(16 * abs(x - W / 2) / (W / 2))
            d.ellipse((x, y, x + 2, y + 2), fill=(245, 229, 201, a))
    layer.save(M / name)


def framed(source, name, size, crop=None, accent='#f5d692'):
    im = Image.open(source) if isinstance(source, Path) else source
    if crop:
        im = im.crop(tuple(round(c * dim) for c, dim in zip(crop, (*im.size, *im.size))))
    im = ImageOps.contain(im.convert('RGBA'), size, Image.Resampling.LANCZOS)
    x, y = (W - im.width) // 2, (H - im.height) // 2
    layer = canvas()
    shadow = canvas()
    ImageDraw.Draw(shadow).rounded_rectangle((x - 18, y - 8, x + im.width + 21, y + im.height + 26), radius=24, fill=(8, 5, 19, 200))
    layer.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle((x - 12, y - 12, x + im.width + 12, y + im.height + 12), radius=14, fill=accent)
    layer.alpha_composite(im, (x, y))
    layer.save(M / (name + '.png'))


def trailer_frame(trailer, time):
    data = subprocess.check_output([
        'ffmpeg', '-v', 'error', '-ss', str(time), '-i', str(trailer),
        '-frames:v', '1', '-threads', '1', '-f', 'image2pipe', '-c:v', 'png', '-',
    ])
    return Image.open(io.BytesIO(data))


def score(duration):
    """Trilha original discreta, com baixo pizzicato e pequenas viradas."""
    rng = np.random.default_rng(11)
    bass = np.zeros(round(SR * duration), dtype=np.float32)
    side = np.zeros_like(bass)

    def note(target, start, length, hz, gain, decay, harmonic):
        first = round(start * SR)
        t = np.arange(min(round(length * SR), len(target) - first)) / SR
        attack = np.minimum(1, t / .014)
        env = attack * np.exp(-t * decay) * np.minimum(1, (length - t) / .07)
        signal = np.sin(2 * np.pi * hz * t) + harmonic * np.sin(4 * np.pi * hz * t)
        target[first:first + len(t)] += gain * env * signal

    beat = 60 / 106
    for bar in range(18):
        start = .19 + bar * 4 * beat
        if start > duration - .65:
            break
        root = [65.41, 55, 58.27, 49][bar % 4]
        for position, interval, gain in [(0, 1, .035), (1.5, 2, .021), (2, 1.5, .027), (3.5, 1.888, .014)]:
            time = start + position * beat
            if time < duration - .44 and not 36.93 < time < 37.84:
                note(bass, time, .32, root * interval, gain, 6.6, .59)
        for position in (1, 2.5, 3):
            time = start + position * beat
            first = round(time * SR)
            if time >= duration - .5 or 36.93 < time < 37.84:
                continue
            t = np.arange(round(.071 * SR)) / SR
            noise = np.diff(rng.normal(size=len(t) + 1)) * np.exp(-t * 68)
            side[first:first + len(t)] += .009 * noise * np.minimum(1, t / .004)
        if bar % 2 and start + 1.9 < duration:
            note(side, start + .75 * beat, .46, root * 6, .014, 9, .14)
            note(side, start + 2.25 * beat, .43, root * 8, .010, 10, .12)
    stereo = np.stack((bass + side, bass + np.roll(side, 82) * .73), axis=1)
    return stereo


def prepare(sources, duration):
    M.mkdir(parents=True, exist_ok=True)
    original = sources / '1 voz.wav'
    trailer, = sources.glob('*.mp4')
    shutil.copy2(original, F / 'Voz_Original.wav')
    audio, sample_rate = sf.read(original, dtype='float64')
    assert sample_rate == SR and audio.ndim == 1 and np.max(np.abs(audio * 2)) < .99
    sf.write(M / VOICE, audio * 2, SR, subtype='PCM_24')
    sf.write(M / 'Trilha_Pizzicato.wav', score(duration), SR, subtype='PCM_24')
    colors = {
        'Fundo_Roxo.png': ((24, 18, 51), (102, 57, 143), (213, 169, 255), (42, 60, 123)),
        'Fundo_Ambar.png': ((48, 24, 34), (158, 73, 36), (255, 191, 93), (108, 30, 65)),
        'Fundo_Verde.png': ((13, 31, 37), (40, 120, 74), (177, 252, 176), (41, 49, 120)),
    }
    for name, palette in colors.items():
        graphic(palette, name)
    for name in ('Cabeca_R3.png', 'Bigode_R3.png', *(f'Corpo_{pose}_R3.png' for pose in POSE.values())):
        shutil.copy2(RIG / name, M / name)
    for src, dst in [('05_choque.png', 'Reacao_Choque.png'), ('02_desconfianca.png', 'Reacao_Desconfianca.png')]:
        shutil.copy2(FRAMES / src, M / dst)
    framed(next(sources.glob('fcb*.jpg')), 'Ted_Live_Action', (930, 1170), accent='#ffdd98')
    framed(sources / 'meme.jpg', 'Ted_Filme_Foto', (950, 885), accent='#f5d692')
    framed(sources / 'Screenshot_1.png', 'Seth_Fonte', (910, 910), (.00, .00, .703, .62), '#f6e7c9')
    framed(next(sources.glob('MV5*.jpg')), 'Family_Guy_Capa', (760, 1140), accent='#fff0c6')
    framed(trailer_frame(trailer, 105.35), 'Anuncio_Original', (942, 875), (.231, .12, .77, .873), '#e2f3cc')
    framed(trailer_frame(trailer, 29.39), 'Sofa_Quadro', (972, 680), accent='#f8e4a8')
    for name, time, tone in [('Cenario_Sala', 17.55, (22, 16, 49)),
                             ('Cenario_Vizinhanca', 0.65, (73, 27, 40)),
                             ('Cenario_Festa', 99.7, (17, 42, 38))]:
        stage = ImageOps.fit(trailer_frame(trailer, time).convert('RGB'), (W,H))
        stage = stage.filter(ImageFilter.GaussianBlur(25))
        Image.blend(stage, Image.new('RGB',(W,H),tone), .68).save(M/(name+'.png'))
    framed(trailer_frame(trailer, 100.8), 'Brinde_Quadro', (938, 665), accent='#f8e4a8')
    # A borda e a imagem móvel permanecem em faixas independentes.
    frame = canvas()
    shadow = canvas()
    ImageDraw.Draw(shadow).rounded_rectangle((0, 645, 1079, 1298), radius=27, fill=(4, 5, 17, 170))
    frame.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(16)))
    ImageDraw.Draw(frame).rounded_rectangle((0, 646, 1079, 1274), radius=15, fill='#f9d586')
    frame.save(M / 'Moldura_Ambar.png')
    for name, start, end, source, layout in VIDEOS:
        # Do pacote ao projeto: 12 quadros de margem em cada ponta.
        crop = 'crop=606:1080:634:0,scale=1080:1920' if layout == 'vertical' else 'scale=1048:590'
        ff('-ss', f'{source - .4:.6f}', '-i', trailer, '-an', '-t', f'{at(end) - at(start) + .8:.6f}',
           '-vf', f'fps=30,{crop},setsar=1', '-c:v', 'libx264', '-preset', 'veryfast',
           '-crf', 17, '-threads', 2, '-pix_fmt', 'yuv420p', M / (name + '.mp4'))
    sfx = SONIC / 'revisao_v3_cenas/output/Filmora/midias'
    for name, length, gain in [('Whoosh', .37, '-8dB'), ('Clique', .20, '-7dB')]:
        ff('-i', sfx / (name + '.wav'), '-t', length, '-af', f'volume={gain},afade=t=out:st={length-.035:.3f}:d=0.035',
           '-ar', SR, '-c:a', 'pcm_s24le', M / (name + '.wav'))
    meme = CATALOG['A62']
    path = MEMES / meme['relative_file']
    assert sha(path) == meme['sha256']
    ff('-i', path, '-t', '0.46',
       '-af', 'volume=-23dB,afade=t=out:st=0.34:d=0.12',
       '-ar', SR, '-c:a', 'pcm_s24le', M / 'A62_Huh.wav')
    print(f'Fontes preparadas em {M}', flush=True)


def rotation(deg):
    theta = math.radians(deg)
    return np.array([[math.cos(theta), -math.sin(theta)], [math.sin(theta), math.cos(theta)]])


def ease(u):
    u = np.clip(u, 0, 1)
    return u * u * (3 - 2 * u)


def plan(duration):
    events = []

    def row(name, start, end, track, why, offset=0, **extra):
        event = dict(file=name, start=start, end=end, track=track, offset=offset, reason=why, **extra)
        events.append(event)
        return event

    def visual(name, start, end, track, poses, why, offset=0, **extra):
        start, end = at(start), at(end)
        n = round((end - start) * FPS)
        axes = np.asarray(poses, dtype=float)
        keys = []
        for i in range(n + 1):
            u = i / n
            right = max(1, min(np.searchsorted(axes[:, 0], u), len(axes)-1))
            a, b = axes[right-1], axes[right]
            vals = a[1:] + (b[1:] - a[1:]) * ease((u-a[0])/(b[0]-a[0]))
            x, y, sc, rot = map(float, vals)
            keys.append([i / FPS, x, y, sc, sc, rot])
        row(name, start, end, track, why, offset, keys=keys, **extra)

    def card(name, start, end, x, y, scale, direction, why, track=3, transition=None):
        # A mídia já visível ocupa o primeiro quadro; itens laterais entram no plano.
        pos = [(0, x + direction * .24, y + .023, scale * .92, direction * 5),
               (.16, x - direction * .013, y, scale * 1.013, -direction * 1.45),
               (.74, x, y - .008, scale * 1.025, -direction * 1.15),
               (1, x, y - .015, scale * 1.067, -direction * .88)]
        visual(name+'.png', start, end, track, pos, why, transition=transition)

    for s, e, f, bend in [(0, 7.5,'Roxo',1),(7.5,20.7,'Ambar',-1),(20.7,31.8,'Roxo',1),(31.8,duration,'Verde',-1)]:
        visual('Fundo_'+f+'.png', s, e, 0,
               [(0,.5+bend*.028,.48,1.16,-bend*2),(.53,.5,.52,1.10,bend*.9),(1,.5-bend*.029,.49,1.15,bend*2)],
               'Grafismo em movimento')

    for name, start, end, x, y, zoom in [
        ('Cenario_Sala', 4.77, 6.93, .51, .51, 1.08),
        ('Cenario_Vizinhanca', 12.63, 16.43, .51, .53, 1.19),
        ('Cenario_Sala', 17.4, 20.7, .53, .50, 1.16),
        ('Cenario_Sala', 29.13, 31.8, .47, .54, 1.17),
        ('Cenario_Festa', 35.73, 37.17, .51, .54, 1.15),
    ]:
        visual(name+'.png',start,end,'cenario',
               [(0,x,y,zoom,0),(1,.5,.5,zoom+.06,0)],'Ambiente do próprio trailer')
    fits = {
        'Sofa_Animado': (.50,.374,.97,'Ambar',None),
        'Depois_Da_Transformacao': (.50,.381,.99,'Ambar',None),
        'Vizinhos': (.50,.343,.97,'Ambar','Basic Zoom In'),
        'Familia': (.46,.416,.84,'Ambar','Fast Bounce'),
        'Trabalho': (.55,.416,.88,'Ambar',None),
        'Maturidade': (.50,.453,1.01,None,None),
        'Sofa_Filme': (.50,.398,.92,'Ambar',None),
        'Ted_Aniversario': (.50,.49,1.04,None,None),
    }
    for name, start, end, source, layout in VIDEOS:
        x, y, sc, frame, transition = fits[name]
        keys = [(0,x,y,sc,0),(.18,x,y-.007,sc*1.012,0),(1,x,y-.019,sc*1.048,0)]
        visual(name+'.mp4', start, end, 2, keys, f'Trailer oficial a partir de {source:.2f} s', .4, transition=transition)
        if frame:
            visual(f'Moldura_{frame}.png', start, end, 1, keys, 'Borda independente')
    card('Ted_Live_Action', 0, 1.00, .50, .407, 1.0, 0, 'Ted de pelúcia → Ted animado', track=2, transition='Basic Zoom In')
    card('Sofa_Quadro', 3.47, 4.77, .49, .385, .99, 0, 'O apresentador interrompe para a ressalva', track=2)
    card('Ted_Filme_Foto', 7.50, 10.87, .48, .375, .91, -1, 'Imagem ilustrativa do Ted em live-action')
    card('Sofa_Quadro', 10.45, 12.63, .526, .485, .91, 1, 'O desenho entra e completa a comparação', track=4)
    card('Seth_Fonte', 22.80, 25.33, .50, .365, .95, 1, 'Seth MacFarlane, com a imagem enviada', track=3)
    card('Family_Guy_Capa', 24.57, 27.01, .68, .436, .66, 1, 'Capa de Family Guy, ligada ao criador', track=4)
    card('Ted_Live_Action', 26.73, 29.13, .46, .371, .94, -1, 'A fala volta à criação de Ted e à voz do urso', track=3)
    card('Anuncio_Original', 31.80, 34.17, .50, .387, 1.02, 0, 'Cartela de estreia original do trailer')
    card('Brinde_Quadro', 35.73, 37.17, .49, .367, .86, 1, 'Ted anima o fecho antes da pergunta')

    def reaction(name, start, end, sc, why, fx=None, transition=None):
        visual(name+'.png', start, end, 8,
               [(0,.5,.50,sc,0),(.20,.5,.50,sc+0.044,0),(1,.5,.49,sc+.080,0)],
               why, fx=fx or [], transition=transition)

    reaction('Reacao_Choque', 6.93, 7.50, 1.04, 'Frame cômico 05 na pausa da ressalva', ['Glow'])
    reaction('Reacao_Desconfianca', 37.17, duration, 1.04, 'Frame cômico 02, close seco na pergunta final', ['Text Vibrate', 'Grunge_Jitter'])

    audio, sr = sf.read(F / 'Voz_Original.wav', dtype='float32')
    energy = np.array([np.sqrt(np.mean(audio[max(0, round(t*sr)-240):round(t*sr)+1440]**2))
                       if t*sr < len(audio) else 0 for t in np.arange(round(duration * FPS)+1) / FPS])
    energy = np.convolve(np.clip((energy - .024) / .098, 0, 1), [.2,.6,.2], mode='same')

    # Os movimentos seguem intenções. A cabeça articula no encaixe da gola;
    # o bigode se move pouco e se mantém sobre a região inteira da boca.
    acts = [
        (0,1,'ombros',.53,.686,.71,-2,'Surpresa da pergunta de abertura'),
        (1,3.47,'cima',.53,.720,.67,1,'Indica a versão animada'),
        (3.47,4.77,'ressalva',.51,.695,.79,-2,'Interrompe com a ressalva'),
        (4.77,6.93,'assustado',.51,.713,.69,0,'Reage ao trecho do sofá'),
        (7.50,10.50,'apresenta',.52,.705,.72,-1,'Apresenta o contexto dos filmes'),
        (10.50,12.63,'cima',.44,.766,.69,2,'O gesto acompanha a entrada do quadro animado'),
        (12.63,14.90,'cima',.55,.689,.79,0,'Entrega a mudança para a vizinhança'),
        (14.90,17.40,'ombros',.40,.754,.73,-1,'Comenta família e trabalho'),
        (17.40,20.70,'ressalva',.65,.762,.77,1,'Pontua a maturidade de quinta série'),
        (20.70,22.80,'tramando',.49,.483,1.23,-2,'Segura a revelação do criador'),
        (22.80,24.57,'cima',.50,.715,.68,1,'Apresenta Seth em imagem'),
        (24.57,27.01,'direita',.30,.693,.66,-2,'Liga o criador à capa de Family Guy'),
        (27.01,29.13,'apresenta',.53,.713,.68,1,'Volta ao urso'),
        (29.13,31.80,'cima',.50,.733,.65,-1,'Remete à imagem do primeiro filme'),
        (31.80,34.17,'cima',.51,.728,.66,1,'Aponta a data fornecida pelo trailer'),
        (35.73,37.17,'joinha',.50,.720,.72,-1,'Convida quem assiste a comentar'),
    ]
    neck = np.array([540, 1043])
    moustache = np.array([540, 950])
    for s, e, pose, x, y, scale, tilting, why in acts:
        start, end = at(s), at(e)
        n = round((end-start)*FPS)
        rows = ([], [], [])
        for i in range(n+1):
            t = i / FPS
            u = min(1, t / max((end-start)*.50,.22))
            gesture = float(ease(u) * (1 - .73 * ease((t-(end-start)*.47)/max((end-start)*.47,.12))))
            settle = float(1 - ease(t / .28))
            target = np.array([x*W + 9*tilting*gesture, y*H + 42*settle - 8*gesture])
            size = scale * (1 + .033*gesture - .025*settle)
            angle = tilting * (.32 + .65*gesture)
            head_angle = (tilting * -.58 - .9) * gesture
            body = rotation(angle) * size
            head = rotation(head_angle)
            tilt_center = target + body @ (neck + head @ (CENTER - neck) - CENTER)
            en = float(energy[round(start*FPS)+i])
            stretch = np.array([1+.012*en, 1+.040*en])
            must_center = moustache + stretch * (CENTER-moustache) + np.array([0, -.7*en])
            motion_center = target + body @ (neck + head @ (must_center - neck) - CENTER)
            for out, pos, scales, rot in zip(
                rows, (target, tilt_center, motion_center), ((size,size),(size,size),size*stretch),
                (angle, angle+head_angle, angle+head_angle),
            ):
                out.append([t, float(pos[0]/W), float(pos[1]/H), float(scales[0]), float(scales[1]), rot])
        for track, name, keys in zip((5,6,7),(f'Corpo_{POSE[pose]}_R3.png','Cabeca_R3.png','Bigode_R3.png'),rows):
            row(name, start, end, track, why, keys=keys)

    row(VOICE, 0, len(audio)/SR, 'voz', 'Tomada integral, com ganho linear de +6,02 dB')
    row('Trilha_Pizzicato.wav', 0, duration, 'musica', 'Trilha original em nível baixo')
    for t in (1, 10.45, 22.8, 24.57, 31.8):
        row('Whoosh.wav', t, t+.37, 'sfx', 'Entrada motivada da mídia')
    for t in (3.54, 20.70, 34.17):
        row('Clique.wav', t, t+.20, 'foley', 'Acento curto de troca')
    row('A62_Huh.wav', 37.00, 37.46, 'meme', 'Banco A62, Huh? sob a pausa da pergunta',
        catalog='A62', source_id=CATALOG['A62']['id'], source_in=0, source_out=.46, gain_db=-23)

    return dict(width=W,height=H,fps=FPS,frames=round(duration*FPS),duration=duration,
                voice_sha256=sha(F/'Voz_Original.wav'),no_added_captions=True,events=events)


def render(p, temp, preview):
    cv2.setNumThreads(1)
    sources, keys = {}, {}
    visual = sorted((e for e in p['events'] if e['track'] in VISUAL_TRACKS), key=lambda e:VISUAL_TRACKS.index(e['track']))
    for e in visual:
        name = e['file']
        keys[id(e)] = np.asarray(e['keys'])
        if name in sources:
            continue
        if name.endswith('.mp4'):
            sources[name] = [cv2.VideoCapture(str(M/name)), None]
            continue
        im = cv2.imread(str(M/name), cv2.IMREAD_UNCHANGED)
        if im.shape[2] == 4:
            x,y,w,h = cv2.boundingRect(im[:,:,3])
            sources[name] = im[y:y+h,x:x+w].copy(), float(x), float(y)
        else:
            sources[name] = im, 0., 0.

    checkpoints = {round(at(t)*FPS) for t in (
        0,.5,.98,1.4,3.60,4.84,6.95,7.55,8.35,10.55,11.49,12.7,14.98,16.57,17.48,
        18.66,20.72,22.33,22.86,23.76,24.64,25.66,27.4,29.33,31.87,33.15,34.5,35.8,36.7,37.28,38.9
    )}
    video = temp/'sem_audio.mp4'
    if not preview:
        proc = subprocess.Popen([
            'ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}',
            '-r', str(FPS), '-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','17',
            '-pix_fmt','yuv420p','-threads','3',str(video),
        ], stdin=subprocess.PIPE)

    for i in sorted(checkpoints) if preview else range(p['frames']):
        t = i/FPS
        frame = np.zeros((H,W,3), dtype=np.uint8)
        for e in visual:
            if not (e['start'] <= t < e['end']):
                continue
            name = e['file']
            local = round((t-e['start'])*FPS)
            _, x, y, sx, sy, angle = keys[id(e)][local]
            src = sources[name]
            if name.endswith('.mp4'):
                cap, prior = src
                wanted = local + round(e['offset']*FPS)
                if prior != wanted-1:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, wanted)
                ok, im = cap.read()
                assert ok, (name, wanted)
                src[1] = wanted
                ox, oy = (W-im.shape[1])/2, (H-im.shape[0])/2
            else:
                im, ox, oy = src
            mat = rotation(angle) @ np.diag([sx,sy])
            offset = np.array([x*W, y*H]) + mat @ (np.array([ox,oy]) - CENTER)
            ih,iw = im.shape[:2]
            box = np.array([[0,0],[iw,0],[0,ih],[iw,ih]]) @ mat.T + offset
            lo = np.maximum(0, np.floor(box.min(axis=0)).astype(int)-1)
            hi = np.minimum([W,H], np.ceil(box.max(axis=0)).astype(int)+1)
            if np.any(hi<=lo):
                continue
            affine = np.column_stack((mat,offset-lo))
            # Os vídeos retangulares recebem máscara independente só na rotação.
            if im.shape[2] == 3 and name.endswith('.mp4') and angle:
                im = cv2.cvtColor(im, cv2.COLOR_BGR2BGRA)
            warped = cv2.warpAffine(im, affine, tuple(hi-lo), flags=cv2.INTER_LINEAR,
                                    borderMode=cv2.BORDER_CONSTANT)
            dest = frame[lo[1]:hi[1],lo[0]:hi[0]]
            if warped.shape[2] == 4:
                alpha = warped[:,:,3:4].astype(np.float32) / 255
                dest[:] = warped[:,:,:3] * alpha + dest * (1-alpha)
            else:
                dest[:] = warped
        if preview:
            cv2.imwrite(str(temp/f'previa_{i:04d}.jpg'), frame)
        else:
            proc.stdin.write(frame.tobytes())
            if i % 180 == 0:
                print(f'Render: {i}/{p["frames"]}', flush=True)

    for name, src in sources.items():
        if name.endswith('.mp4'):
            src[0].release()
    if preview:
        return
    proc.stdin.close()
    assert proc.wait() == 0
    mix = np.zeros((round(p['duration']*SR), 2), dtype=np.float64)
    for e in p['events']:
        if e['track'] in VISUAL_TRACKS:
            continue
        samples, rate = sf.read(M/e['file'], always_2d=True)
        assert rate == SR
        start = round(e['start']*SR)
        n = round((e['end']-e['start'])*SR)
        assert n <= len(samples) and n + start <= len(mix), (e, len(samples))
        mix[start:start+n] += samples[:n]
    assert abs(mix).max() < .98
    sf.write(temp/'mix.wav', mix, SR, subtype='PCM_24')
    ff('-i',video,'-i',temp/'mix.wav','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac',
       '-b:a','256k','-movflags','+faststart',OUT/f'{TITLE}_9x16.mp4')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('fontes', type=Path)
    parser.add_argument('temporarios', type=Path)
    parser.add_argument('mode', choices=('prepare','preview','render'))
    opt = parser.parse_args()
    opt.temporarios.mkdir(parents=True, exist_ok=True)
    info = sf.info(opt.fontes/'1 voz.wav')
    duration = math.ceil(info.frames * FPS / info.samplerate) / FPS
    if opt.mode == 'prepare':
        prepare(opt.fontes, duration)
        (P/'timeline.json').write_text(json.dumps(plan(duration), ensure_ascii=False, separators=(',', ':'))+'\n')
    else:
        render(json.loads((P/'timeline.json').read_text()), opt.temporarios, opt.mode == 'preview')


if __name__ == '__main__':
    main()
