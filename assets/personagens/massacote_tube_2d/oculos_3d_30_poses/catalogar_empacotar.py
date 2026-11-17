"""Catálogo, conferências e pacote das trinta artes já geradas."""
from pathlib import Path
import json,sqlite3,hashlib,subprocess,zipfile,sys,html
sys.path.insert(0,'/workspace/tools/shorts_asr')
import cv2,numpy as np
P=Path(__file__).resolve().parent;plan=json.loads((P/'plano.json').read_text());reg=json.loads((P/'registro_encaixe.json').read_text());R={x['id']:x for x in reg['poses']}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def magick(*args):
    prefix=['magick','montage','-limit','thread','2']if args and args[0]=='montage'else['magick','-limit','thread','2']
    rest=args[1:]if args and args[0]=='montage'else args
    subprocess.run([*prefix,*map(str,rest)],check=True,stdout=subprocess.DEVNULL)
assets=[];seen=set();checks=[]
assert len(R)==30
for x in plan['poses']:
    ident=x['id'];path=P/'poses'/(ident+'.png');a=cv2.imread(str(path),-1);assert a.shape==(2048,2048,4)
    bbox=cv2.boundingRect((a[:,:,3]>128).astype('uint8'));bx,by,bw,bh=bbox
    assert min(bx,by)>20 and bx+bw<2028 and by+bh<2028,(ident,bbox)
    digest=sha(path);assert digest not in seen;seen.add(digest)
    row={**x,'file':str(path.relative_to(P)),'sha256':digest,'bytes':path.stat().st_size,'canvas':[2048,2048],'alpha_bbox':list(bbox),'body':R[ident]['body'],'front':R[ident]['front'],'head':'camadas/cabeca_sem_bigode.png','moustache':'camadas/bigode_repouso.png','head_fixed':'camadas/cabeca_com_bigode.png','eyes_animation':False,'mouth_hidden':True,'base_style_approved':True,'individual_pose_feedback':'aguardando_usuario'}
    assets.append(row);checks.append(dict(id=ident,rgba=True,transparent_border=True,body_sha256=sha(P/row['body'])))
    # Miniaturas são somente mostruário; os PNGs não perdem suas margens de registro.
    thumb=P/'previas'/(ident+'.jpg')
    magick(path,'-background','#e5ddcf','-alpha','remove','-alpha','off','-resize','340x340','-gravity','south','-background','#e5ddcf','-splice','0x36','-fill','#251c2a','-font','DejaVu-Sans','-pointsize','14','-annotate','+0+11',x['title'],thumb)
for i in range(3):
    files=[P/'previas'/(x['id']+'.jpg')for x in plan['poses'][i*10:i*10+10]]
    magick('montage',*files,'-tile','5x2','-geometry','340x376+8+8','-background','#e5ddcf',P/'previas'/f'Prancha_{i+1}.jpg')
magick(*[P/'previas'/f'Prancha_{i}.jpg'for i in (1,2,3)],'-append',P/'Previa_30_Poses.jpg')
catalog=dict(character='Massacote Tube — óculos 3D',style='cartoon compacto / adesivo',canvas=[2048,2048],count=30,eye_states=0,eye_animation=False,mouth_rule='Boca sempre coberta pelo bigode',base_approved_by_user=True,head_shared=True,head_pivot=reg['head_pivot'],moustache_pivot=reg['moustache_pivot'],poses=assets)
(P/'catalogo.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
db=P/'catalogo.sqlite'
if db.exists():db.unlink()
with sqlite3.connect(db)as c:
    c.execute('CREATE TABLE poses(id TEXT PRIMARY KEY,title TEXT,category TEXT,png TEXT,body TEXT,foreground TEXT,sha256 TEXT)')
    c.executemany('INSERT INTO poses VALUES(?,?,?,?,?,?,?)',[(x['id'],x['title'],x['category'],x['file'],x['body'],x['front'],x['sha256'])for x in assets])
    c.execute('CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT)');c.executemany('INSERT INTO metadata VALUES(?,?)',[(k,json.dumps(v,ensure_ascii=False))for k,v in catalog.items()if k!='poses'])
cards=''.join(f'<article data-category="{x["category"]}"><a href="{x["file"]}"><img loading="lazy" src="{x["file"]}" alt="{html.escape(x["title"])}"></a><b>{x["id"][:2]} · {html.escape(x["title"])}</b><p><a href="{x["file"]}" download>PNG completo</a> · <a href="{x["body"]}" download>Corpo</a></p></article>'for x in assets)
page='''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Massacote — 30 poses</title><style>body{background:#211829;color:#f2e7d6;font:16px system-ui;margin:24px}h1{color:#f4cfc1}input,select{font:inherit;padding:10px;margin:8px;border-radius:8px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:15px}article{background:#e5ddcf;color:#251c2a;border-radius:15px;padding:10px;text-align:center}img{width:100%;display:block}a{color:#963153}header a{color:#ffb9a9}small{display:block;max-width:850px;line-height:1.5}</style><header><h1>Massacote Tube — 30 poses</h1><small>Óculos fixos, corpo/cabeça/bigode em camadas. PNGs transparentes no mesmo canvas 2048×2048. Preserve as margens para trocar as poses sem deslocar o rosto.</small><p><a href="camadas/cabeca_sem_bigode.png">Cabeça sem bigode</a> · <a href="camadas/bigode_repouso.png">Bigode</a> · <a href="camadas/LEIA-ME.txt">Ordem das camadas</a></p><input id="q" placeholder="Buscar gesto..."><select id="cat"><option value="">Todas</option value="fala">Apresentação</option><option value="apontar">Apontar</option><option value="reacao">Reações</option><option value="comica">Cômicas</option></select></header><div class="grid">'''+cards+'''</div><script>function f(){let q=document.querySelector('#q').value.toLocaleLowerCase(),c=document.querySelector('#cat').value;document.querySelectorAll('article').forEach(a=>a.hidden=!a.textContent.toLocaleLowerCase().includes(q)||(c&&a.dataset.category!==c))}document.querySelector('#q').oninput=f;document.querySelector('#cat').onchange=f</script></html>'''
(P/'galeria.html').write_text(page)
report=dict(poses=30,unique_pose_files=30,canvas=[2048,2048],all_rgba=True,all_transparent=True,all_borders_clear=True,shared_head=True,eye_animation=False,originals_preserved=True,shared_layer_files=[f.name for f in (P/'camadas').glob('*.png')if not f.name[:2].isdigit()],checks=checks)
(P/'validacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
bundle=P/'entrega/Massacote_Tube_Oculos_3D_30_Poses.zip';members=[p for folder in ['poses','camadas','previas']for p in (P/folder).rglob('*')if p.is_file()]+[P/f for f in ['galeria.html','catalogo.json','catalogo.sqlite','registro_encaixe.json','validacao.json','Previa_30_Poses.jpg','README.md']]
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED,compresslevel=4)as z:
    for path in members:z.write(path,str(path.relative_to(P)))
with zipfile.ZipFile(bundle)as z:
    assert z.testzip()is None
    for path in members:assert hashlib.sha256(z.read(str(path.relative_to(P)))).hexdigest()==sha(path)
(P/'pacote.json').write_text(json.dumps(dict(file=bundle.name,bytes=bundle.stat().st_size,sha256=sha(bundle),files=len(members),all_member_hashes_verified=True),indent=2)+'\n')
print('BANCO_COMPLETO',len(assets),bundle.stat().st_size,flush=True)
