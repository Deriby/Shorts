#!/usr/bin/env python3
"""Exporta o lote a partir dos registros image_gen, sem recortar a arte."""
import argparse
import hashlib
import html
import json
import pathlib
import sqlite3
import unicodedata
import zipfile
from PIL import Image, ImageDraw, ImageFont

WORK = pathlib.Path(__file__).resolve().parent
REPO = pathlib.Path('/workspace/work/sonic-v3')
DEST = REPO / 'assets/personagens/massacote_tube_2d/frames_comicos/lote_01'
SIZES = {'9x16': (1080, 1920), '16x9': (1920, 1080)}

def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def font(size):
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--final', action='store_true')
    args = ap.parse_args()
    plan = json.loads((WORK / 'plano.json').read_text())
    reactions = plan['reactions']
    records = {}
    for path in sorted((WORK / 'meta').glob('*.json')):
        data = json.loads(path.read_text())
        records[(data['id'], data['format'])] = data
    if args.final:
        missing = [(r['id'], fmt) for r in reactions for fmt in SIZES if (r['id'], fmt) not in records]
        assert not missing, f'Faltam imagens: {missing}'
    DEST.mkdir(parents=True, exist_ok=True)
    catalog = []
    errors = []
    for reaction in reactions:
        entry = {k: reaction[k] for k in ('id', 'slug', 'name', 'tags')}
        entry['arquivos'] = {}
        for fmt, size in SIZES.items():
            record = records.get((reaction['id'], fmt))
            if not record:
                continue
            source = pathlib.Path(record['source'])
            try:
                with Image.open(source) as opened:
                    opened.load()
                    native_size = opened.size
                    ratio_error = abs((native_size[0] / native_size[1]) / (size[0] / size[1]) - 1)
                    if ratio_error > 0.025:
                        errors.append({'id': reaction['id'], 'format': fmt, 'size': native_size, 'error': 'aspecto_incorreto'})
                        continue
                    image = opened.convert('RGB')
                stem = f"{reaction['id']:02}_{reaction['slug']}"
                relative = pathlib.Path(fmt) / (stem + '.png')
                target = DEST / relative
                target.parent.mkdir(exist_ok=True)
                source_sha = sha(source)
                cache = DEST / 'fontes' / f'{stem}_{fmt}.json'
                old = json.loads(cache.read_text()) if cache.exists() else {}
                if not target.exists() or old.get('source_sha256') != source_sha:
                    image = image.resize(size, Image.Resampling.LANCZOS)
                    image.save(target, compress_level=6)
                else:
                    image = Image.open(target).convert('RGB')
                thumb_rel = pathlib.Path('miniaturas') / f'{stem}_{fmt}.jpg'
                thumb_path = DEST / thumb_rel
                thumb_path.parent.mkdir(exist_ok=True)
                thumb = image.copy()
                thumb.thumbnail((640, 640), Image.Resampling.LANCZOS)
                thumb.save(thumb_path, quality=87, optimize=True)
                full_record = dict(record)
                full_record.update(source_sha256=source_sha, source_size=list(native_size), exported_size=list(size), export=str(relative), export_sha256=sha(target), export_method='Redimensionamento Lanczos para formato padrao; sem recorte, barras ou composicao adicional.')
                dump(cache, full_record)
                entry['arquivos'][fmt] = {'arquivo': str(relative), 'miniatura': str(thumb_rel), 'largura': size[0], 'altura': size[1], 'sha256': full_record['export_sha256']}
            except Exception as exc:
                errors.append({'id': reaction['id'], 'format': fmt, 'error': str(exc)})
        catalog.append(entry)
    dump(WORK / 'erros_exportacao.json', errors)
    if errors:
        print(json.dumps({'export_errors': errors}, ensure_ascii=False))
    for fmt in SIZES:
        portrait = fmt == '9x16'
        iw, ih = (216, 384) if portrait else (384, 216)
        pad, label = 12, 48
        cw, ch = iw + 2 * pad, ih + label + pad
        sheet = Image.new('RGB', (cw * 5, ch * 4 + 66), '#171722')
        draw = ImageDraw.Draw(sheet)
        draw.text((16, 13), f'MASSACOTE TUBE · 20 REAÇÕES · {fmt.replace("x", ":")}', font=font(25), fill='#fff5dc')
        for idx, entry in enumerate(catalog):
            x, y = idx % 5 * cw + pad, idx // 5 * ch + 66
            file = entry['arquivos'].get(fmt)
            if file:
                with Image.open(DEST / file['arquivo']) as image:
                    image = image.resize((iw, ih), Image.Resampling.LANCZOS)
                    sheet.paste(image, (x, y))
            else:
                draw.rectangle((x, y, x + iw, y + ih), fill='#30303e')
                draw.text((x + 15, y + ih // 2), 'Gerando…', font=font(19), fill='#9999ab')
            title = f"{entry['id']:02} · {entry['name']}"
            size = 19 if portrait else 22
            while draw.textbbox((0, 0), title, font=font(size))[2] > iw:
                size -= 1
            draw.text((x, y + ih + 9), title, font=font(size), fill='white')
        sheet.save(DEST / f'Previa_20_Reacoes_{fmt}.jpg', quality=92, optimize=True)
    available = sum(len(r['arquivos']) for r in catalog)
    print(json.dumps({'imagens_exportadas': available, 'erros': len(errors), 'destino': str(DEST)}, ensure_ascii=False))
    if not args.final:
        return
    assert not errors
    assert available == 40
    assert len({file['sha256'] for r in catalog for file in r['arquivos'].values()}) == 40
    dump(DEST / 'catalogo.json', {'titulo': 'Massacote Tube — 20 reações cômicas', 'total_reacoes': 20, 'total_imagens': 40, 'formatos': SIZES, 'reacoes': catalog})
    dump(DEST / 'fontes' / 'plano.json', plan)
    db_path = DEST / 'catalogo.sqlite'
    if db_path.exists():
        db_path.unlink()
    with sqlite3.connect(db_path) as db:
        db.execute('CREATE TABLE frames(id INTEGER, reacao TEXT, slug TEXT, tags TEXT, formato TEXT, arquivo TEXT, largura INTEGER, altura INTEGER, sha256 TEXT, PRIMARY KEY(id, formato))')
        for entry in catalog:
            for fmt, file in entry['arquivos'].items():
                db.execute('INSERT INTO frames VALUES(?,?,?,?,?,?,?,?,?)', (entry['id'], entry['name'], entry['slug'], ','.join(entry['tags']), fmt, file['arquivo'], file['largura'], file['altura'], file['sha256']))
    (DEST / 'README.md').write_text('''# 20 reações cômicas do Massacote Tube

40 PNGs: uma versão **9:16 (1080×1920)** e uma versão **16:9 (1920×1080)** para cada reação. As artes horizontais foram geradas com enquadramento próprio.

Abra `galeria.html` para procurar por reação e baixar a imagem. As duas pranchas `Previa_20_Reacoes_*.jpg` mostram o conjunto. `catalogo.json` e `catalogo.sqlite` permitem consultar o acervo nas próximas edições.

Use os closes hiper-detalhados como inserts cômicos ligados à fala e ao momento da piada, tanto nos shorts quanto nos vídeos longos. O visual normal do avatar continua disponível separadamente. Boca escondida pelo bigode e lentes opacas vermelho/azul fazem parte do personagem.

O pack de memes recebido do Drive continua em `assets/biblioteca_memes/` no repositório Shorts e também deve ser consultado ao editar. Estes frames são um acervo adicional do avatar.

Os PNGs são quadros completos com fundo, sem transparência. As expressões foram geradas com image_gen a partir da primeira prévia. Registros de origem, prompts e hashes estão em `fontes/`; a exportação para os tamanhos padrão usa redimensionamento sem cortar a arte. O frame vertical 01 reaproveita a prévia inicial. Os 40 arquivos foram conferidos tecnicamente; a avaliação estética individual é do usuário.
''')
    cards = []
    for entry in catalog:
        norm = unicodedata.normalize('NFKD', entry['name'] + ' ' + ' '.join(entry['tags'])).encode('ascii', 'ignore').decode().lower()
        images = []
        for fmt, file in entry['arquivos'].items():
            images.append(f'''<a class="frame {fmt}" href="{file['arquivo']}" target="_blank"><img src="{file['miniatura']}" loading="lazy" alt="{html.escape(entry['name'])} em {fmt.replace('x', ':')}"><span>{fmt.replace('x', ':')} · {file['largura']} × {file['altura']}<b> Abrir PNG ↗</b></span></a>''')
        cards.append(f'''<article data-search="{html.escape(norm)}"><h2>{entry['id']:02} · {html.escape(entry['name'])}</h2><div class="pair">{''.join(images)}</div><p>{html.escape(' · '.join(entry['tags']))}</p></article>''')
    (DEST / 'galeria.html').write_text('''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Massacote Tube · 20 reações</title><style>
*{box-sizing:border-box}body{margin:0;background:#14121d;color:#f8f0e2;font:16px system-ui,sans-serif}header{max-width:1480px;margin:auto;padding:40px 24px 20px}h1{font-size:clamp(27px,5vw,46px);margin:8px 0}header p{color:#c0b7cf;max-width:820px;line-height:1.6}input{width:min(100%,550px);font:inherit;color:inherit;background:#282333;border:1px solid #5e4b70;border-radius:12px;padding:14px;margin:8px 0}main{max-width:1480px;margin:auto;padding:10px 24px 48px;display:grid;grid-template-columns:repeat(auto-fit,minmax(350px,1fr));gap:24px}article{background:#211b2b;border:1px solid #493951;border-radius:18px;padding:16px}h2{font-size:21px;margin:0 0 14px}.pair{display:grid;grid-template-columns:1fr 1.76fr;gap:10px;align-items:center}.frame{display:block;color:#e7d6f7;text-decoration:none;font-size:11px}.frame img{width:100%;display:block;border-radius:8px}.frame span{display:block;margin:8px 0;line-height:1.6}.frame b{display:block;color:#dcacff;font-weight:500}article p{color:#b5a7c0;font-size:13px}article[hidden]{display:none}#count{font-size:14px;color:#c4b4ce}@media(max-width:430px){main{grid-template-columns:1fr;padding:10px 12px}header{padding:25px 16px}article{padding:12px}}
</style><header><div>MASSACOTE TUBE</div><h1>20 reações. Drama em dobro.</h1><p>Closes absurdamente detalhados para pontuar a piada. Escolha o vertical para shorts ou o horizontal para vídeos longos. Toque na imagem para abrir o PNG completo.</p><input id="search" type="search" placeholder="Buscar: nojo, choro, raiva…" aria-label="Buscar reação"><div id="count">20 reações · 40 PNGs</div></header><main>''' + ''.join(cards) + '''</main><script>const q=document.querySelector('#search'),cards=[...document.querySelectorAll('article')];q.addEventListener('input',()=>{const s=q.value.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();let n=0;cards.forEach(c=>{c.hidden=!c.dataset.search.includes(s);if(!c.hidden)n++});document.querySelector('#count').textContent=`${n} reações · ${n*2} PNGs`});</script></html>''')
    manifest = []
    for entry in catalog:
        for fmt, file in entry['arquivos'].items():
            path = DEST / file['arquivo']
            with Image.open(path) as image:
                image.verify()
            manifest.append({'id': entry['id'], 'formato': fmt, **file, 'bytes': path.stat().st_size})
    dump(DEST / 'verificacao.json', {'total_png': 40, 'pares': 20, 'dimensoes_corretas': True, 'decodificacao_png': True, 'hashes_distintos': 40, 'arquivos': manifest})
    entrega = DEST / 'entrega'
    entrega.mkdir(exist_ok=True)
    zip_path = entrega / 'Frames_Comicos_20_Reacoes_9x16_16x9.zip'
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(DEST.rglob('*')):
            if path.is_file() and entrega not in path.parents:
                arcname = pathlib.Path('Massacote_Tube_20_Reacoes') / path.relative_to(DEST)
                archive.write(path, str(arcname), compress_type=zipfile.ZIP_STORED if path.suffix in ('.png','.jpg') else zipfile.ZIP_DEFLATED)
    with zipfile.ZipFile(zip_path) as archive:
        assert archive.testzip() is None
        for file in manifest:
            member = 'Massacote_Tube_20_Reacoes/' + file['arquivo']
            assert hashlib.sha256(archive.read(member)).hexdigest() == file['sha256']
    print(json.dumps({'zip': str(zip_path), 'bytes': zip_path.stat().st_size, 'sha256': sha(zip_path), 'zip_crc_e_hashes': 'OK'}, ensure_ascii=False))

if __name__ == '__main__':
    main()
