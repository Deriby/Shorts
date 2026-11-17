"""Catálogos local e agregado; valida transparência, registro e banco aprovado."""
from pathlib import Path
from collections import Counter
import hashlib, json, sqlite3
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent; ROOT=P.parent; OLD=ROOT/'modular_01'
plan=json.loads((P/'plano_lote.json').read_text())
previous=json.loads((OLD/'catalogo.json').read_text())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write_json(path,value): path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
old_by_hash={a['sha256']:a for a in previous['assets']}
assets=[]
titles={x['id']:x['title'] for x in plan['poses']+plan['eyes']}
categories={x['id']:x['category'] for x in plan['poses']}
for folder,kind in [('poses','pose'),('olhos','olhos'),('olhos_base','olhos'),('bigode','bigode'),('frente','frente'),('rig','rig')]:
    for path in sorted((P/folder).glob('*.png')):
        with Image.open(path) as im:
            assert im.size==(1024,1536),(path,im.size)
            assert im.mode=='RGBA',(path,im.mode)
            alpha=np.array(im)[:,:,3]; assert alpha.min()==0 and alpha.max()==255,path
            assert not alpha[0].any() and not alpha[-1].any() and not alpha[:,0].any() and not alpha[:,-1].any(),('recortado',path)
        digest=sha(path); prior=old_by_hash.get(digest)
        ident=f'{kind}:{path.stem}'
        assets.append(dict(id=ident,type=kind,title=titles.get(path.stem,prior['title'] if prior else path.stem.replace('_',' ')),category=categories.get(path.stem,''),file=path.relative_to(P).as_posix(),width=1024,height=1536,transparent=True,sha256=digest,approval=prior['approval'] if prior else 'aguardando_avaliacao_do_usuario'))
assert len(list((P/'poses').glob('*.png')))==30
assert len(list((P/'olhos').glob('*.png')))==10
assert len(list((P/'olhos_base').glob('*.png')))==13
assert len(list((P/'rig').glob('*_corpo.png')))==30
head=np.array(Image.open(P/'rig/cabeca_limpa.png'))
assert sha(P/'rig/cabeca_limpa.png')==sha(OLD/'rig/cabeca_limpa.png')
for f in (P/'bigode').glob('*.png'): assert sha(f)==sha(OLD/'bigode'/f.name)
rig=[]
for pose in plan['poses']:
    ident=pose['id']; face=np.array(Image.open(P/'poses'/f'{ident}.png'))
    front=P/'frente'/f'{ident}_frente.png'; region=head[380:575,350:575,3]>128
    if front.exists(): region &= np.array(Image.open(front))[380:575,350:575,3]==0
    assert np.array_equal(face[380:575,350:575][region],head[380:575,350:575][region]),('rosto divergente',ident)
    eye=f'olhos/{pose["default_eyes"]}.png'
    if not (P/eye).exists(): eye=f'olhos_base/{pose["default_eyes"]}.png'
    assert (P/eye).exists()
    rig.append(dict(pose_id=ident,base=f'poses/{ident}.png',body=f'rig/{ident}_corpo.png',head='rig/cabeca_limpa.png',eyes=eye,moustache='bigode/01_bigode_repouso.png',foreground=f'frente/{ident}_frente.png' if front.exists() else None))
catalog=dict(character=previous['character'],style=previous['style'],batch='modular_02',canvas=[1024,1536],rules=previous['rules'],assets=assets,rig=rig,counts=dict(new_poses=30,new_eye_states=10,compatible_eye_states=23),approval='aguardando_avaliacao_do_usuario',previews=['Previa_Poses_1.jpg','Previa_Poses_2.jpg','Previa_Poses_3.jpg','Previa_10_Olhares.jpg'],gallery='galeria.html')
write_json(P/'catalogo.json',catalog)

def database(path,data):
    db=sqlite3.connect(path)
    db.executescript('DROP TABLE IF EXISTS assets; DROP TABLE IF EXISTS rig; CREATE TABLE assets (id TEXT PRIMARY KEY,type TEXT,title TEXT,category TEXT,file TEXT,width INTEGER,height INTEGER,transparent INTEGER,sha256 TEXT,approval TEXT); CREATE TABLE rig (pose_id TEXT PRIMARY KEY,base TEXT,body TEXT,head TEXT,eyes TEXT,moustache TEXT,foreground TEXT); CREATE INDEX assets_type ON assets(type); CREATE INDEX assets_category ON assets(category);')
    for a in data['assets']:
        db.execute('INSERT INTO assets VALUES (?,?,?,?,?,?,?,?,?,?)',[a.get(k,'') for k in ['id','type','title','category','file','width','height','transparent','sha256','approval']])
    for r in data['rig']:
        db.execute('INSERT INTO rig VALUES (?,?,?,?,?,?,?)',[r.get(k) for k in ['pose_id','base','body','head','eyes','moustache','foreground']])
    db.commit(); assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok';db.close()
database(P/'catalogo.sqlite',catalog)
merged={}; rigs=[]
for directory,data in [(OLD,previous),(P,catalog)]:
    for a in data['assets']:
        a=dict(a,file=f'{directory.name}/{a["file"]}')
        if a['id'] in merged:
            assert merged[a['id']]['sha256']==a['sha256'],('ID reutilizado',a['id'])
            continue
        merged[a['id']]=a
    rig_rows=([dict(value,pose_id=key) for key,value in data['rig'].items()] if isinstance(data['rig'],dict) else data['rig'])
    for r in rig_rows:
        r=dict(r)
        for key in ['base','body','head','eyes','moustache','foreground']:
            if r.get(key): r[key]=f'{directory.name}/{r[key]}'
        rigs.append(r)
all_data=dict(character=previous['character'],style=previous['style'],canvas=[1024,1536],assets=list(merged.values()),rig=rigs,counts=dict(poses=40,eye_states=23,moustache_states=3),approval_note='Lote 01 aprovado; novas artes do lote 02 aguardam avaliação.')
assert Counter(a['type'] for a in all_data['assets'])['pose']==40
assert Counter(a['type'] for a in all_data['assets'])['olhos']==23
for a in all_data['assets']: assert sha(ROOT/a['file'])==a['sha256']
write_json(ROOT/'banco_catalogo.json',all_data); database(ROOT/'banco_catalogo.sqlite',all_data)
approval=json.loads((OLD/'aprovacao.json').read_text())
for a in previous['assets']: assert sha(OLD/a['file'])==a['sha256'],('asset aprovado alterado',a['id'])
assert sha(OLD/'previa/Previa_Modular_Conversando.mp4')==approval['preview_sha256']
report=dict(result='ok',new_poses=30,new_eye_states=10,combined_poses=40,combined_eye_states=23,new_library_pngs=len(assets),combined_unique_pngs=len(merged),same_head=True,same_moustache=True,previous_approved_assets_unchanged=39,canvas=[1024,1536],native_filmora_tested=False)
write_json(P/'validacao.json',report); print(json.dumps(report,ensure_ascii=False))
