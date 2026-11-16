"""Indexa os arquivos existentes; não modifica as artes."""
from pathlib import Path
import hashlib,json,sqlite3,html,zipfile
from PIL import Image
import numpy as np

ROOT=Path(__file__).resolve().parent
LABELS=[('neutro','Neutro','repouso,apresentador'),('conversando','Conversando','fala,explicando,palma aberta'),('debochado','Debochado','sarcasmo,bracos cruzados'),('apontando','Apontando','indicando,direita'),('confuso','Confuso','duvida,encolher ombros'),('bravo','Bravo','raiva,punhos'),('pensando','Pensando','reflexao,queixo'),('rindo','Rindo','risada,alegria'),('assustado','Assustado','susto,surpresa'),('facepalm','Facepalm','incredulidade,vergonha alheia')]
entries=[]
for i,(slug,title,tags) in enumerate(LABELS,1):
    f=ROOT/'poses'/f'{i:02d}_{slug}.png'
    with Image.open(f) as im:
        im.load();assert im.mode=='RGBA' and im.size==(1024,1536)
        a=np.array(im.getchannel('A'));assert (a==0).sum()>100000 and (a>200).sum()>400000
        ys,xs=np.where(a>128);assert xs.min()>0 and xs.max()<1023 and ys.min()>0 and ys.max()<1535
    entries.append(dict(id=f'MT2D-{i:03d}',title=title,tags=tags.split(','),file=f.relative_to(ROOT).as_posix(),width=1024,height=1536,transparent=True,mouth_visible=False,approval='aguardando_avaliacao',sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
base=np.array(Image.open(ROOT/'fala/01_fala_a.png').convert('RGBA'))
changes=[]
for f in [ROOT/'fala/02_fala_b.png',ROOT/'fala/03_fala_c.png']:
    im=np.array(Image.open(f).convert('RGBA'));d=np.any(base!=im,axis=2);ys,xs=np.where(d)
    assert len(xs)>100 and xs.min()>=337 and xs.max()<=717 and ys.min()>=494 and ys.max()<=651
    outside=d.copy();outside[494:652,337:718]=False;assert not outside.any()
    changes.append(dict(file=f.relative_to(ROOT).as_posix(),changed_pixels=int(d.sum()),changed_bbox=[int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1],outside_moustache_region_changed_pixels=0))
with Image.open(ROOT/'fala/Conversando_Bigode.webp') as im:
    assert im.is_animated and im.n_frames==6
    for i in range(im.n_frames):im.seek(i);im.load();assert im.size==(1024,1536)
report=dict(main_poses=10,transparent_pngs_verified=True,major_silhouette_inside_canvas=True,speech_frames=3,speech_loop_frames=6,speech_loop_seconds=.6,speech_animation=changes,visual_review='10 poses inspecionadas; boca coberta pelo bigode. Aprovacao estetica das poses pendente.')
(ROOT/'validacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
catalog=dict(character='Massacote Tube 2D',batch='lote_01',date='2026-11-16',base_design='Referencia anexada pelo usuario no chat: design aprovado. Os PNGs sao novas poses derivadas, nao uma copia do arquivo original.',rules=['boca sempre coberta pelo bigode','na fala, manter corpo/cabeca/olhos parados','não gerar o lote de 100 antes da avaliação do primeiro lote'],approval='aguardando_avaliacao',poses=entries,speech=dict(frames=['fala/01_fala_a.png','fala/02_fala_b.png','fala/03_fala_c.png'],animation='fala/Conversando_Bigode.webp',preview='fala/Previa_Conversando.gif',loop_ms=600,sequence=['A','B','A','C','B','A'],durations_ms=[120,80,100,80,80,140],note='Edicoes do bigode geradas com image_gen e montadas com mascara fixa. Fora da mascara, os PNGs sao identicos ao frame A. Repetir durante falas e voltar ao A nas pausas; nao sincronizado a uma gravacao.'))
(ROOT/'catalogo.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
con=sqlite3.connect(ROOT/'catalogo.sqlite')
con.execute('CREATE TABLE IF NOT EXISTS poses (id TEXT PRIMARY KEY,title TEXT,tags TEXT,file TEXT,width INTEGER,height INTEGER,transparent INTEGER,mouth_visible INTEGER,approval TEXT,sha256 TEXT)')
with con:
    for e in entries:con.execute('INSERT OR REPLACE INTO poses VALUES (?,?,?,?,?,?,?,?,?,?)',(e['id'],e['title'],','.join(e['tags']),e['file'],e['width'],e['height'],1,0,e['approval'],e['sha256']))
assert con.execute('select count(*) from poses').fetchone()[0]==10
assert con.execute('pragma integrity_check').fetchone()[0]=='ok'
con.close()
cards=''.join(f'<article data-tags="{html.escape(e["title"]+" "+" ".join(e["tags"])).lower()}"><a href="{e["file"]}"><img src="{e["file"]}" alt="{e["title"]}" loading="lazy"></a><p>{e["id"]} · {e["title"]}</p></article>' for e in entries)
(ROOT/'galeria.html').write_text('''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Massacote Tube · Lote 01</title><style>body{margin:0;background:#201b26;color:#fff0db;font:16px system-ui;padding:30px}h1{font-size:28px}p{color:#dbcbd9}input{padding:12px;border-radius:8px;border:1px solid #675269;background:#302637;color:white;width:min(90%,480px)}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:18px;margin-top:26px}article{border-radius:12px;overflow:hidden;background:#3a3044;border:1px solid #55415b}article img{width:100%;display:block;background:repeating-conic-gradient(#eee 0 25%,#ddd 0 50%) 50%/24px 24px}article p{padding:0 12px}section img{width:min(100%,320px);background:#d5d4d6;border-radius:12px}</style><h1>Massacote Tube · 10 poses</h1><p>Primeiro lote para avaliação. PNGs transparentes, 1024 × 1536.</p><input aria-label="Buscar poses" placeholder="Buscar: bravo, duvida, apontando…" id="q"><main>'''+cards+'''</main><h2>Fala · somente região do bigode</h2><section><img src="fala/Conversando_Bigode.webp" alt="Fala com bigode animado"><p>Ciclo de 0,6 s. Boca coberta; sem áudio. PNGs A/B/C na pasta fala.</p></section><script>document.getElementById('q').addEventListener('input',e=>{const v=e.target.value.toLocaleLowerCase('pt-BR').normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');document.querySelectorAll('article').forEach(a=>a.hidden=!a.dataset.tags.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').includes(v))})</script></html>''')
print(json.dumps(report,ensure_ascii=False,indent=2))
