"""Static framing review of the native transform curves, not a plugin render."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json
import subprocess
from PIL import Image, ImageDraw

P = Path(__file__).resolve().parent
F = P.parent / 'output/Filmora'
C = Path('/workspace/attachments/longo009_edicao_v2/quadros')
C.mkdir(parents=True, exist_ok=True)
edit = json.loads((P / 'edicao.json').read_text())
motions = edit['motions']


def value(points, time):
    for (a, x), (b, y) in zip(points, points[1:]):
        if a <= time <= b:
            return x + (y - x) * (time - a) / (b - a)
    return points[-1][1]


selected = []
for media in dict.fromkeys(m['media'] for m in motions if m['kind'] in ('host', 'seated', 'close')):
    candidates = [m for m in motions if m['media'] == media and m['kind'] in ('host', 'seated', 'close')]
    selected.append(max(candidates, key=lambda m: max(p[1] for p in m['scale'])))


def frame(args):
    index, m = args
    a, b = m['source']
    time = a + (b - a) * .82
    out = C / f'{index:02d}.png'
    subprocess.run(['ffmpeg', '-v', 'error', '-threads', '1', '-ss', str(time), '-i', str(F / 'midias' / m['media']), '-frames:v', '1', '-vf', 'scale=640:360', '-threads', '1', '-y', str(out)], check=True)
    im = Image.open(out).convert('RGB')
    z = value(m['scale'], time) / 100
    focus = m['focus']
    px, py = (.5 + (z - 1) * (.5 - f) for f in focus)
    new = im.transform(im.size, Image.Transform.AFFINE, (1 / z, 0, 640 * (.5 - px / z), 0, 1 / z, 360 * (.5 - py / z)), Image.Resampling.BILINEAR)
    sheet = Image.new('RGB', (640, 204), (20, 21, 26))
    sheet.paste(new.resize((320, 180)), (320, 0))
    sheet.paste(im.resize((320, 180)), (0, 0))
    draw = ImageDraw.Draw(sheet)
    draw.text((6, 184), m['media'].removesuffix('_video_16x9.mp4') + ' | antes', fill='white')
    draw.text((326, 184), f'keyframe {z * 100:.0f}%', fill='#ffd649')
    return sheet


with ThreadPoolExecutor(max_workers=3) as pool:
    sheets = list(pool.map(frame, enumerate(selected)))
contact = Image.new('RGB', (1280, ((len(sheets) + 1) // 2) * 204 + 30), (20, 21, 26))
for index, sheet in enumerate(sheets):
    contact.paste(sheet, ((index % 2) * 640, (index // 2) * 204))
ImageDraw.Draw(contact).text((10, contact.height - 23), 'Conferencia das transformacoes basicas; nao representa render dos plugins/transicoes do Filmora.', fill='white')
contact.save(P / 'Previa_Enquadramentos.jpg', quality=91)
(P / 'quadros_conferidos.json').write_text(json.dumps(dict(note='Basic-transform framing samples; not a native Filmora/plugin render.', shots=selected), ensure_ascii=False, indent=2) + '\n')
print('FRAMING_REVIEW_READY', len(selected))
