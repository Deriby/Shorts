"""Galeria offline com combinação de pose, olhar e bigode."""
from pathlib import Path
import json, html, subprocess
P=Path(__file__).resolve().parent; S=Path('/workspace/scratch/tube_modular_02/eye_previews');S.mkdir(parents=True,exist_ok=True)
plan=json.loads((P/'plano_lote.json').read_text());cat=json.loads((P/'catalogo.json').read_text())
def run(*args): subprocess.run(['magick',*map(str,args)],check=True)
tiles=[]
for eye in plan['eyes']:
    ident=eye['id'];tile=S/(ident+'.jpg')
    run(P/'rig/cabeca_limpa.png',P/'olhos'/(ident+'.png'),'-compose','over','-composite',P/'bigode/01_bigode_repouso.png','-compose','over','-composite','-crop','630x740+190+20','+repage','-background','#f2eee6','-alpha','remove','-alpha','off','-resize','252x296','-gravity','south','-splice','0x40','-fill','#211b22','-font','DejaVu-Sans','-pointsize','15','-annotate','+0+12',eye['title'],tile)
    tiles.append(tile)
run('montage',*tiles,'-background','#f2eee6','-tile','5x2','-geometry','252x336+8+8',P/'Previa_10_Olhares.jpg')
payload=dict(poses=plan['poses'],eyes=[a for a in cat['assets'] if a['type']=='olhos'],moustaches=[a for a in cat['assets'] if a['type']=='bigode'],rig=cat['rig'])
page='''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Massacote Tube · 30 poses novas</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#17131c;color:#f5eee7;font:16px system-ui}main{max-width:1240px;margin:auto;padding:28px}h1{margin:0 0 8px}p{line-height:1.5;color:#d5c6d4}a{color:#ff8584}label{display:block;margin:14px 0}select,input,button{font:inherit;padding:10px;border:1px solid #79667b;border-radius:6px;background:#2b2230;color:#fff;max-width:100%}select{display:block;width:100%;margin-top:6px}button{cursor:pointer}.editor{display:grid;grid-template-columns:minmax(250px,470px) 1fr;gap:28px;margin:28px 0}.stage{aspect-ratio:2/3;position:relative;background:repeating-conic-gradient(#eee7df 0% 25%,#fffaf3 0% 50%) 0/24px 24px;border-radius:10px;overflow:hidden}.stage img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain}.stage.dark{background:#292333}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:14px}.card{background:#2b2230;padding:0;border:1px solid #4d3b51;text-align:left;overflow:hidden;border-radius:8px}.card img{display:block;width:100%;aspect-ratio:2/3;object-fit:contain;background:#f2eee6}.card span{display:block;padding:12px;font-size:14px}.hint{font-size:14px}#selection a{display:block;margin:12px 0}#filter{width:100%;margin:10px 0 20px}@media(max-width:650px){.editor{grid-template-columns:1fr}.stage{max-width:380px;margin:auto;width:100%}main{padding:16px}}
</style><main><h1>Massacote Tube · lote 02</h1><p>30 poses novas + 10 novos olhares. Monte combinações abaixo. Olhos e bigode continuam em camadas separadas; a boca fica escondida. As novas artes aguardam sua avaliação.</p>
<div class="editor"><div class="stage" id="stage"><img id="base" alt="Base da pose"><img id="eye" alt="Olhos"><img id="must" alt="Bigode"><img id="front" alt="Mão à frente" hidden></div><div><label>Pose<select id="poseSelect"></select></label><label>Olhar<select id="eyeSelect"></select></label><label>Bigode<select id="mustSelect"></select></label><button id="bg">Trocar fundo</button><div id="selection"></div><p class="hint">Abra este HTML após extrair o ZIP inteiro. PNGs 1024 × 1536: mantenha o mesmo enquadramento de todas as camadas no Filmora.</p><p><a href="Previa_30_Poses.jpg">Prancha com as 30 poses</a> · <a href="Previa_10_Olhares.jpg">Prancha dos 10 olhares</a> · <a href="README.md">Guia das camadas</a></p></div></div>
<h2>Escolha uma pose</h2><input id="filter" aria-label="Buscar pose" placeholder="Buscar: apontando, cômica, robô…"><div class="grid" id="grid"></div></main>
<script>const data=__DATA__;
const $=id=>document.getElementById(id),pose=$('poseSelect'),eyes=$('eyeSelect'),must=$('mustSelect');
function opt(select,value,text){let o=new Option(text,value);select.add(o)}
data.poses.forEach(p=>opt(pose,p.id,p.id.slice(0,2)+' · '+p.title));data.eyes.forEach(e=>opt(eyes,e.file,e.title));data.moustaches.forEach(m=>opt(must,m.file,m.title));
function chooseDefault(){let p=data.poses.find(p=>p.id===pose.value),e=data.eyes.find(e=>e.id==='olhos:'+p.default_eyes);if(e)eyes.value=e.file;render()}
function render(){let r=data.rig.find(r=>r.pose_id===pose.value);$('base').src=r.base;$('eye').src=eyes.value;$('must').src=must.value;$('front').hidden=!r.foreground;if(r.foreground)$('front').src=r.foreground;$('selection').replaceChildren();for(let [title,file] of [['PNG da pose sem rosto',r.base],['PNG dos olhos',eyes.value],['PNG do bigode',must.value],['Corpo para animar separado',r.body],['Cabeça limpa',r.head],['Mão à frente',r.foreground]]){if(file){let a=document.createElement('a');a.textContent=title;a.href=file;a.download='';$('selection').append(a)}}}
pose.onchange=chooseDefault;eyes.onchange=must.onchange=render;$('bg').onclick=()=>$('stage').classList.toggle('dark');
const norm=s=>s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase();
function cards(){let q=norm($('filter').value);$('grid').replaceChildren();data.poses.filter(p=>norm(p.title+' '+p.id+' '+p.category).includes(q)).forEach(p=>{let b=document.createElement('button');b.className='card';let im=document.createElement('img');im.src='montados/'+p.id+'.jpg';im.loading='lazy';im.alt=p.title;let t=document.createElement('span');t.textContent=p.id.slice(0,2)+' · '+p.title;b.append(im,t);b.onclick=()=>{pose.value=p.id;chooseDefault();$('stage').scrollIntoView({behavior:'smooth',block:'center'})};$('grid').append(b)})}
$('filter').oninput=cards;chooseDefault();cards();</script></html>'''
(P/'galeria.html').write_text(page.replace('__DATA__',json.dumps(payload,ensure_ascii=False).replace('</','<\\/')))
print('GALERIA E PRANCHA DOS OLHARES PRONTAS')
