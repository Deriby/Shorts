"""Cut the four drawn sheets; retain all original IDs and pixels unchanged."""
from pathlib import Path
import hashlib
import json
import shutil
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
MOODS = ['neutra', 'alegre', 'irritada', 'sarcastica', 'empolgada']
MOUTHS = [
    ('fechada_mbp', 'Repouso / M B P'), ('aberta_a', 'A aberto'),
    ('larga_e', 'E largo / dentes'), ('estreita_i', 'I estreito / dentes próximos'),
    ('redonda_o', 'O aberto'), ('pequena_u', 'U / bico pequeno'),
    ('labio_fv', 'F V / dentes no lábio'), ('lingua_l', 'L / língua visível'),
    ('entreaberta_dtn', 'D T N / abertura curta'), ('bico_ch', 'CH X / lábios projetados'),
]
REACTIONS = [
    'olhar_direita_desconfiado', 'revirando_olhos', 'vergonha_olhar_baixo',
    'julgando', 'detetive_desconfiado', 'segurando_riso', 'sorriso_de_desespero',
    'labios_comprimidos', 'quase_chorando', 'bocejo_cansado', 'repulsa',
    'incredulo_assimetrico', 'culpado', 'vitoria_silenciosa', 'decepcao',
    'implorando', 'refletindo', 'caiu_a_ficha', 'tentando_entender',
    'mordendo_labio', 'piscada_rindo', 'piscada_deboche', 'bocejo_um_olho',
    'indignacao', 'horror_silencioso',
]
COMICS = [
    'susto_olhos_saltados', 'sorriso_dentao', 'alma_saiu_do_corpo',
    'vesgo_lingua', 'olhos_cada_um_num_canto', 'careta_dentes_travados',
    'risada_escancarada', 'berro_com_lagrimas', 'suando_sorrindo',
    'bochechas_infladas', 'derrotado_boca_caida', 'choro_cachoeira',
    'chorando_de_rir', 'enjoo', 'tonto_espirais', 'raiva_maxima',
    'deboche_absoluto', 'travou_no_oh', 'cara_amassada', 'beijo_piscando',
    'inocente_demais', 'sorriso_de_vilao', 'cerebro_desligou',
    'acabou_a_energia', 'surto_final',
]

def cut_sheet(name):
    im = Image.open(ROOT / 'sources' / name).convert('RGB')
    return [im.crop((round(c*im.width/5), round(r*im.height/5),
                     round((c+1)*im.width/5), round((r+1)*im.height/5)))
            .resize((128,128), Image.Resampling.NEAREST)
            for r in range(5) for c in range(5)]

def main():
    pngs = ROOT / 'png'; pngs.mkdir(exist_ok=True)
    old = json.loads((ROOT.parent/'v2/expressions.json').read_text())['expressions']
    entries = []
    for e in old:
        dest = pngs / f"{e['id']:03d}_{e['name']}.png"
        shutil.copyfile(ROOT.parent/'v2'/e['file'], dest)
        entries.append(dict(e, file='png/'+dest.name, category='original', new=False))
    sheets = [cut_sheet(n) for n in ['01_fala_aeio.png', '02_fala_outras_bocas.png',
                                     '03_reacoes.png', '04_caricatas.png']]
    for batch, tiles in enumerate(sheets):
        for k, tile in enumerate(tiles):
            i = len(entries)
            if batch < 2:
                mood, viseme = MOODS[k//5], MOUTHS[batch*5+k%5]
                name = f'fala_{mood}_{viseme[0]}'
                meta = dict(category='fala', mood=mood, mouth=viseme[0],
                            description=viseme[1], family=f'fala_{mood}')
            else:
                name = (REACTIONS if batch == 2 else COMICS)[k]
                meta = dict(category='reacao' if batch==2 else 'caricata')
            file = f'png/{i:03d}_{name}.png'
            tile.save(ROOT/file)
            entries.append(dict(id=i, name=name, file=file, new=True,
                                source_sheet=batch+1, source_cell=k, **meta))
    assert len(entries) == 131
    atlas = Image.new('RGB',(2048,1152))
    for i in range(144):
        e = entries[i] if i < 131 else entries[0]
        atlas.paste(Image.open(ROOT/e['file']),(i%16*128,i//16*128))
    atlas.save(ROOT/'atlas_131_16x9.png')
    for batch, title in enumerate(['FALA — A E I O', 'FALA — U F/V L D/T/N CH',
                                    'REAÇÕES', 'CARICATAS']):
        sheet = Image.new('RGB',(1000,1140),(28,28,33))
        draw = ImageDraw.Draw(sheet)
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
        for k, e in enumerate(entries[31+batch*25:56+batch*25]):
            x,y=k%5*200,k//5*228
            sheet.paste(Image.open(ROOT/e['file']).resize((200,200),Image.Resampling.NEAREST),(x,y))
            label = f"{e['id']:03d} {e['name']}"
            draw.text((x+4,y+202),label[:25],font=font,fill='white')
            if len(label)>25: draw.text((x+4,y+215),label[25:],font=font,fill='white')
        sheet.save(ROOT/f'Dery_100_{batch+1:02d}.png')
    manifest = dict(version=3,count=131,new_count=100,preserved_count=31,
                    columns=16,rows=9,tile_size=128,interpolation='Closest',
                    animation='CONSTANT',expressions=entries)
    for e in entries:
        e['sha256']=hashlib.sha256((ROOT/e['file']).read_bytes()).hexdigest()
    (ROOT/'expressions.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    families = {m: {e['mouth']:e['id'] for e in entries
                   if e.get('mood')==m} for m in MOODS}
    (ROOT/'fala_familias.json').write_text(json.dumps(families,ensure_ascii=False,indent=2)+'\n')
    print('Ready: 100 new PNGs, 31 exact originals; 50 speech / 25 reaction / 25 comic.')

if __name__=='__main__': main()
