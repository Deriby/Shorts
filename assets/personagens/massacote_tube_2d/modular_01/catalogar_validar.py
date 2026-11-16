"""Valida arquivos finais, registra a biblioteca e constrói a galeria local."""
from pathlib import Path
import json,hashlib,sqlite3,subprocess,wave,html
from PIL import Image
import numpy as np,cv2
P=Path(__file__).resolve().parent;V=P/'previa';M=V/'Filmora/midias'
POSES=['01_neutro','02_conversando','03_debochado','04_apontando','05_confuso','06_bravo','07_pensando','08_rindo','09_assustado','10_facepalm']
LABELS=['Neutro','Conversando','Braços cruzados','Apontando','Confuso','Bravo','Pensando','Rindo','Assustado','Facepalm']
EYELABELS=['Normal do desenho aprovado','Normal alternativo','Piscada — meio fechado','Piscada — fechado','Bravo','Confuso','Pensando','Desconfiado','Assustado','Rindo','Piscando olho esquerdo','Piscando olho direito','Preocupado']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
approval_data=json.loads((P/'aprovacao.json').read_text()) if (P/'aprovacao.json').exists() else {}
approved_hashes=approval_data.get('assets',{})
entries=[]
for folder,kind in [('poses','pose'),('olhos','olhos'),('bigode','bigode'),('frente','frente'),('rig','rig')]:
 for f in sorted((P/folder).glob('*.png')):
  with Image.open(f)as im:
   im.load();assert im.mode=='RGBA' and im.size==(1024,1536),f
   a=np.array(im.getchannel('A'));assert (a==0).sum()>10000 and (a>128).sum()>100,f
  label=LABELS[POSES.index(f.stem)] if kind=='pose' else EYELABELS[int(f.stem.split('_')[0])] if kind=='olhos' else f.stem.replace('_',' ')
  entries.append(dict(id=kind+':'+f.stem,type=kind,title=label,file=f.relative_to(P).as_posix(),width=1024,height=1536,transparent=True,sha256=sha(f),approval='aprovado_pelo_usuario' if approved_hashes.get(kind+':'+f.stem)==sha(f) else 'preparado_para_avaliacao'))
assert sum(e['type']=='pose'for e in entries)==10
assert sum(e['type']=='olhos'for e in entries)==13
assert sum(e['type']=='bigode'for e in entries)==3
assert sum(e['type']=='frente'for e in entries)==2
# All bases share the same clean face, apart from the explicit foreground hands.
master=np.array(Image.open(P/'fontes/02_conversando.png').convert('RGBA'));region=np.zeros(master.shape[:2],dtype=bool);region[390:560,360:560]=True;region &= master[:,:,3]>128
checked=[]
for ident in POSES:
 im=np.array(Image.open(P/'poses'/f'{ident}.png').convert('RGBA'));allowed=region.copy();front=P/'frente'/f'{ident}_frente.png'
 if front.exists():allowed &=np.array(Image.open(front).getchannel('A'))==0
 assert np.array_equal(im[:,:,:3][allowed],master[:,:,:3][allowed]),ident
 checked.append(ident)
# Blink images must actually remove the eye whites; wink sides must differ.
def white_mask(f):
 a=np.array(Image.open(f).convert('RGBA'));return (a[:,:,3]>128)&(a[:,:,0]>190)&(a[:,:,1]>160)&(a[:,:,2]>100)
normal=white_mask(P/'olhos/01_normal.png').sum();half=white_mask(P/'olhos/02_piscada_meio.png').sum();closed=white_mask(P/'olhos/03_piscada_fechado.png').sum();assert 0<half<normal and closed==0
assert white_mask(P/'olhos/09_rindo.png').sum()==0
left=white_mask(P/'olhos/10_piscando_esquerdo.png');right=white_mask(P/'olhos/11_piscando_direito.png');assert left[:,:465].sum()==0 and left[:,465:].sum()>0;assert right[:,465:].sum()==0 and right[:,:465].sum()>0
# Source reference and the previous approved library remain untouched.
old=P.parent/'lote_01';oldcat=json.loads((old/'catalogo.json').read_text())
for e in oldcat['poses']:assert sha(old/e['file'])==e['sha256']
cap=cv2.VideoCapture(str(V/'Previa_Modular_Conversando.mp4'));count=0;prev=None;movement=[]
while True:
 ok,im=cap.read()
 if not ok:break
 assert im.shape==(720,1280,3)
 if prev is not None:movement.append(float(np.abs(im.astype(float)-prev.astype(float)).mean()))
 prev=im;count+=1
cap.release();assert count==279 and max(movement)>.2
with wave.open(str(M/'voz_teste.wav'))as f:voice=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(float)/32768;sr=f.getframerate()
dec=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(V/'Previa_Modular_Conversando.mp4'),'-vn','-ac','1','-ar',str(sr),'-f','f32le','pipe:1']),dtype='<f4');n=min(len(voice),len(dec));corr=float(np.corrcoef(voice[:n],dec[:n])[0,1]);assert corr>.99
all_approved=all(e['approval']=='aprovado_pelo_usuario' for e in entries) and approval_data.get('preview_sha256')==sha(V/'Previa_Modular_Conversando.mp4')
report=dict(poses=10,eye_states=13,moustache_png_states=3,foreground_layers=2,rgba_canvas=[1024,1536],registered_clean_faces_verified=checked,blink_white_pixel_counts=dict(normal=int(normal),half=int(half),closed=int(closed)),left_right_winks_verified=True,old_approved_library_unchanged=True,video_frames=count,video_duration=9.3,audio_correlation=corr,source_voice_excerpt=[0,9.3],new_voice_created=False,filmora_native_executed=False,blender_used=False,visual_review='Conjunto e previa aprovados pelo usuario.' if all_approved else 'Nova versao aguarda avaliacao.',user_approved=all_approved)
(P/'validacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
rig={ident:dict(base='poses/'+ident+'.png',body='rig/'+ident+'_corpo.png',head='rig/cabeca_limpa.png',eyes='olhos/00_normal_base.png',moustache='bigode/01_bigode_repouso.png',foreground='frente/'+ident+'_frente.png'if(P/'frente'/f'{ident}_frente.png').exists()else None)for ident in POSES}
catalog=dict(character='Massacote Tube 2D',style='Samurai Jack com acabamento digital amador',batch='modular_01',canvas=[1024,1536],rules=['olhos estreitos/alongados','boca nunca desenhada','bigode em camada independente','M vermelho em brasao','mesmo registro para encaixe','downloads pelo GitHub'],assets=entries,rig=rig,preview='previa/Previa_Modular_Conversando.mp4',filmora='previa/Filmora/Massacote_Tube_Modular_Previa.wfp',approval='aprovado_pelo_usuario' if all_approved else 'preparado_para_avaliacao')
(P/'catalogo.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
con=sqlite3.connect(P/'catalogo.sqlite');con.execute('CREATE TABLE IF NOT EXISTS assets (id TEXT PRIMARY KEY,type TEXT,title TEXT,file TEXT,width INTEGER,height INTEGER,transparent INTEGER,sha256 TEXT,approval TEXT)');con.execute('CREATE TABLE IF NOT EXISTS rig (pose_id TEXT PRIMARY KEY,base TEXT,body TEXT,head TEXT,eyes TEXT,moustache TEXT,foreground TEXT)')
with con:
 for e in entries:con.execute('INSERT OR REPLACE INTO assets VALUES (?,?,?,?,?,?,?,?,?)',(e['id'],e['type'],e['title'],e['file'],1024,1536,1,e['sha256'],e['approval']))
 for ident,r in rig.items():con.execute('INSERT OR REPLACE INTO rig VALUES (?,?,?,?,?,?,?)',(ident,*[r[k]for k in ['base','body','head','eyes','moustache','foreground']]))
assert con.execute('SELECT count(*) FROM assets').fetchone()[0]==39;assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok';con.close()
# Thumbnails are user-facing catalogue views; source PNGs remain untouched.
thumbdir=P/'montados/olhos';thumbdir.mkdir(exist_ok=True)
for e in [e for e in entries if e['type']=='olhos']:
 subprocess.run(['magick',str(P/e['file']),'-crop','330x210+305+280','+repage','-background','#f2eee6','-alpha','remove','-alpha','off',str(thumbdir/(Path(e['file']).stem+'.jpg'))],check=True)
cards=''.join(f'<article data-name="{html.escape(e["title"].lower())}"><a href="{e["file"]}"><img loading="lazy" src="montados/{Path(e["file"]).stem}.jpg" alt="{e["title"]}"></a><p>{e["title"]}</p><a href="{e["file"]}">PNG com rosto limpo</a></article>'for e in entries if e['type']=='pose')
eyecards=''.join(f'<article data-name="{html.escape(e["title"].lower())}"><a href="{e["file"]}"><img loading="lazy" src="montados/olhos/{Path(e["file"]).stem}.jpg" alt="{e["title"]}"></a><p>{e["title"]}</p></article>'for e in entries if e['type']=='olhos')
(P/'galeria.html').write_text('''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Massacote Tube · banco modular</title><style>body{margin:0;padding:28px;background:#262134;color:#f7ecdc;font:16px system-ui}main{max-width:1400px;margin:auto}video{width:min(100%,900px);border-radius:12px}section{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px}article{background:#3d3049;border-radius:12px;overflow:hidden;padding-bottom:14px}article img{width:100%;display:block}article p,article>a:last-child{margin:12px}a{color:#ffbbb7}input{padding:12px;width:min(90%,500px);margin:20px 0;background:#f2eee6;border:0;border-radius:8px}h2{margin-top:38px}</style><main><h1>Massacote Tube · banco modular</h1><p>10 poses com rosto limpo · 13 olhos e expressões · bigode independente. Mostruário montado para conferir o encaixe.</p><video controls preload="metadata" src="previa/Previa_Modular_Conversando.mp4"></video><p><a href="previa/Filmora/Massacote_Tube_Modular_Previa.wfp">Projeto Filmora</a> · <a href="LEIA-ME.md">Instruções</a></p><input id="q" placeholder="Buscar: bravo, piscada, pensando…" aria-label="Buscar assets"><h2>Poses</h2><section>'''+cards+'''</section><h2>Olhos e sobrancelhas</h2><section>'''+eyecards+'''</section><h2>Bigode</h2><p><a href="bigode/01_bigode_repouso.png">Repouso</a> · <a href="bigode/02_bigode_levantado.png">Levantado</a> · <a href="bigode/03_bigode_comprimido.png">Comprimido</a> · <a href="bigode/Previa_Bigode.webp">Ciclo demonstrativo</a></p></main><script>q.addEventListener('input',()=>{const norm=s=>s.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');document.querySelectorAll('article').forEach(a=>a.hidden=!norm(a.dataset.name).includes(norm(q.value)))})</script></html>''')
print(json.dumps(report,ensure_ascii=False,indent=2))
