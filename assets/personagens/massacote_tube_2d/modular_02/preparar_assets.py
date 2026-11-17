"""Recorta e registra artes feitas com image_gen, sem redesenhar as peças."""
from pathlib import Path
import argparse, json, re, shutil, subprocess

P = Path(__file__).resolve().parent
OLD = P.parent / 'modular_01'
S = Path('/workspace/scratch/tube_modular_02'); S.mkdir(parents=True, exist_ok=True)
PLAN = json.loads((P / 'plano_lote.json').read_text())

def run(*args):
    subprocess.run(['magick', *map(str, args)], check=True)

def mask(shape, path):
    run('-size', '1024x1536', 'xc:black', '-fill', 'white', '-stroke', 'white', '-strokewidth', '1', '-draw', shape, path)

def cut(source, alpha, out):
    run(source, alpha, '-alpha', 'off', '-compose', 'CopyOpacity', '-composite', 'PNG32:' + str(out))

def largest_mask(source, out):
    tmp = S / 'threshold.png'
    run(source, '-alpha', 'extract', '-threshold', '50%', tmp)
    stats = subprocess.check_output(['magick', str(tmp), '-define', 'connected-components:verbose=true', '-define', 'connected-components:mean-color=true', '-connected-components', '8', 'null:'], text=True)
    candidates = []
    for line in stats.splitlines():
        m = re.match(r'\s*(\d+):\s+\S+\s+\S+\s+(\d+)\s+gray\(255\)', line)
        if m:
            candidates.append((int(m[2]), int(m[1])))
    assert candidates, stats
    run(tmp, '-define', 'connected-components:mean-color=true', '-define', f'connected-components:keep={max(candidates)[1]}', '-connected-components', '8', out)

def prepare():
    for folder in ('poses', 'rig', 'frente', 'bigode', 'olhos', 'olhos_base', 'montados'):
        (P / folder).mkdir(exist_ok=True)
    for f in (OLD / 'bigode').iterdir():
        if f.is_file(): shutil.copy2(f, P / 'bigode' / f.name)
    for f in (OLD / 'olhos').glob('*.png'):
        shutil.copy2(f, P / 'olhos_base' / f.name)
    shutil.copy2(OLD / 'rig/cabeca_limpa.png', P / 'rig/cabeca_limpa.png')
    master = OLD / 'fontes/02_conversando.png'
    largest_mask(master, S / 'master_alpha.png')
    cut(master, S / 'master_alpha.png', S / 'master.png')
    mask('polygon 285,40 690,40 800,330 805,455 660,510 600,570 555,615 530,760 395,760 390,635 315,535 305,470 205,440 200,330 250,270', S / 'head_region.png')
    run(S / 'head_region.png', '-negate', S / 'body_region.png')
    mask('rectangle 404,705 519,755', S / 'neck_region.png')
    run(S / 'master_alpha.png', S / 'neck_region.png', '-compose', 'Multiply', '-composite', S / 'neck_alpha.png')
    cut(S / 'master.png', S / 'neck_alpha.png', S / 'neck.png')
    foregrounds = json.loads((P / 'foreground_masks.json').read_text()) if (P / 'foreground_masks.json').exists() else {}
    count = 0
    for pose in PLAN['poses']:
        ident = pose['id']; src = P / 'fontes' / f'{ident}.png'
        if not src.exists(): continue
        largest_mask(src, S / 'alpha.png'); cut(src, S / 'alpha.png', S / 'clean.png')
        full = P / 'poses' / f'{ident}.png'
        run(S / 'clean.png', S / 'master.png', S / 'head_region.png', '-channel', 'RGBA', '-fx', 'u[2].r>0.5?u[1]:u[0]', 'PNG32:' + str(full))
        run(S / 'alpha.png', S / 'body_region.png', '-compose', 'Multiply', '-composite', S / 'body_alpha.png')
        cut(S / 'clean.png', S / 'body_alpha.png', S / 'body.png')
        run(S / 'body.png', S / 'neck.png', '-compose', 'over', '-composite', 'PNG32:' + str(P / 'rig' / f'{ident}_corpo.png'))
        if ident in foregrounds:
            mask(foregrounds[ident], S / 'front_region.png')
            run(S / 'alpha.png', S / 'front_region.png', '-compose', 'Multiply', '-composite', S / 'front_alpha.png')
            front = P / 'frente' / f'{ident}_frente.png'; cut(S / 'clean.png', S / 'front_alpha.png', front)
            run(full, front, '-compose', 'over', '-composite', 'PNG32:' + str(full))
        count += 1
        print(ident, flush=True)
    print('POSES_REGISTRADAS', count, flush=True)

def previews():
    for pose in PLAN['poses']:
        ident = pose['id']; full = P / 'poses' / f'{ident}.png'
        if not full.exists(): continue
        eye = P / 'olhos' / (pose['default_eyes'] + '.png')
        if not eye.exists(): eye = P / 'olhos_base' / (pose['default_eyes'] + '.png')
        if not eye.exists(): eye = P / 'olhos_base/00_normal_base.png'
        args = [full, eye, '-compose', 'over', '-composite', P / 'bigode/01_bigode_repouso.png', '-compose', 'over', '-composite']
        front = P / 'frente' / f'{ident}_frente.png'
        if front.exists(): args += [front, '-compose', 'over', '-composite']
        run(*args, 'PNG32:' + str(P / 'montados' / f'{ident}.png'))
        run(P / 'montados' / f'{ident}.png', '-background', '#f2eee6', '-alpha', 'remove', '-alpha', 'off', P / 'montados' / f'{ident}.jpg')
    for part in range(3):
        group = PLAN['poses'][part*10:(part+1)*10]
        tiles = []
        for pose in group:
            src = P / 'montados' / (pose['id'] + '.jpg')
            if not src.exists(): continue
            tile = S / (pose['id'] + '_tile.jpg')
            run(src, '-resize', '256x384', '-background', '#f2eee6', '-gravity', 'south', '-splice', '0x38', '-fill', '#211b22', '-font', 'DejaVu-Sans', '-pointsize', '13', '-annotate', '+0+12', pose['id'].replace('_', ' '), tile)
            tiles.append(tile)
        if tiles:
            run('montage', *tiles, '-background', '#f2eee6', '-tile', '5x2', '-geometry', '256x422+8+8', P / f'Previa_Poses_{part+1}.jpg')
    sheets = [P / f'Previa_Poses_{i}.jpg' for i in (1,2,3)]
    if all(f.exists() for f in sheets):
        run(*sheets, '-append', P / 'Previa_30_Poses.jpg')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--previews-only', action='store_true'); args = parser.parse_args()
    if not args.previews_only: prepare()
    previews()
