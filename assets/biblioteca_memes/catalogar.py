"""Apply reviewed visual descriptions and export the reusable searchable library."""
from pathlib import Path
import json,sqlite3,hashlib,html,shutil,re,unicodedata
P=Path(__file__).resolve().parent;C=Path('/workspace/attachments/memes009');data=json.loads((P/'catalogo.json').read_text());items=data['items']
images='hamster aprovacao|homem computador irritacao|gato cadeira gamer|macaco joinha|computador desespero|panda entusiasmo|cachorro suspenso confusao|gato explosao caos|gato sufoco|rato risada malicia|pernalonga calma|senhora computador raiva|gato sorriso|toy story apontando|homem aranha gesto|crianca matrix|bob esponja choro|cachorro malicia|homem choro|gato choro|gato calculo matematica|buzz confusao|camera aprovacao|gato gamer|cachorro trabalho|jerry triste|crianca choro|gato desconfiado|bart cego|pinguim triste|gato espanto|homem feliz|homem sal golpe|pinguim desconfiado|marge dinheiro|homem sorriso ironico|cachorro telefone|gato rezando|cachorro sorriso malicia|friends espanto|sapo arma|lisa computador|cachorro frio triste|gato nerd dedo|homem notebook pensativo|gato encarando cachorro|gato espanto|escola desculpa|gato danca|cachorro ironia|macaco papel|coelho irritado|macaco cafe|macaco boca tapada|macaco desconfiado|guaxinim nerd|gato tecnico computador|gato notebook|cachorro juiz documentos|homem grito desespero|friends bebendo|cavalo gamer|esqueleto paciencia|snoopy tontura|sapo vergonha|digitacao varios computadores|peixe espanto|botao perfect|homem cartao dinheiro|homem segurando riso|grito euforia|bob esponja panico|pinguim julgamento|homem aranha cafe|gato pensativo|gato reacao|cachorro telefone|gato maos|gato dedos|gato fixo|cachorro calma|cachorro desconfiado|gato lingua|peixe indignado|macaco sem graca|gato fogo|menino encarando|cafe incendio tudo bem|homem aranha facepalm|homem aranha duvida|robo neutro|pernalonga julgamento|cachorro espanto|gato revoltado|macaco oh no|gato oh no|homem desconfiado|cachorro nariz|cachorro medo|gato carinho|cachorro calma|cachorro montanha russa|gato computador'
videos='crianca grito|crianca confusao|sobrancelha duvida|cachorro dirigindo|menino gesticulando|sorriso sumindo|tom julgamento|espera sozinho|bob esponja nervoso|jerry malicia|gamer grito|desconforto saindo|criancas danca|stewie malicia|jerry arrogancia|surpresa duvida|gamer grito|homem apavorado|gato espanto|homem explicacao|cachorro espanto|digitacao rapida|desconforto saindo|menino indignado|gato grito|homem desaprovacao|vegeta revolta|gato confuso|crianca assustada|gato revoltado|gato fogo|batman rolando|queda cadeira|apresentador cai|gato julgamento|gamer grito|homem risada|gato leitor|desenho pedindo|homem grito|jimmy neutron|gato cortina|shrek ironia|gato azul|homem porta|cachorro esperando|gamer grito|friends ironia|homem surpreso|olhos arregalados|gato andando|plateia risada|bob esponja feliz|homer danca|hamster surpresa|macaco choro|computador quebrando|homem indignado|falando parede|homem desaprovacao|homem choro|cachorro telefone|tom feliz|desenho asco|lisa vergonha|jake grito|pica pau cansado|matematica calculo|computador digitando|gato grito|gato malicia|aplausos|lula molusco|gato medroso|gato bravo|homer fugindo|cachorro|cachorro assustado|meerkat danca|cris grito|homem agradecendo|abelha fofa|gato gritando|gato agua|homem indignado|homem serio|gamer surpreso|brinde aprovacao|cachorro julgamento|chef receita julgamento|homem risada|homem facepalm|homem protesto|gato raiva|macaco oh no|gato oh no|entrevista desconfianca|cachorro nariz|cachorro susto|gato carinho'
labels={**{f'I{i:02d}':v for i,v in enumerate(images.split('|'))},**{f'V{i:02d}':v for i,v in enumerate(videos.split('|'))}}
# Some old first-page image labels beyond I63 were not semantic; retain honest
# preview status and use the visible named assets/selected cues as stronger tags.
thumbs=P/'miniaturas';thumbs.mkdir(exist_ok=True);seen={}
for x in items:
 x['description']=labels.get(x['tag'],x['name']);x['tags']=list(dict.fromkeys(re.findall(r'[\w]+',x['description'].lower())))
 x['review_status']='visual_preview_reviewed'if x['category']!='audio'else'filename_and_technical_metadata'
 x['duplicate_of']=seen.get(x['sha256']);seen.setdefault(x['sha256'],x['id'])
 old=C/'thumbs'/(x['tag']+'.jpg')
 if old.exists():dest=thumbs/(x['tag']+'.jpg');shutil.copyfile(old,dest);x['thumbnail']=str(dest.relative_to(P))
 elif x.get('thumbnail'):
  src=P/x['thumbnail']
  if src.exists():dest=thumbs/(x['tag']+'.jpg');shutil.copyfile(src,dest) if src!=dest else None;x['thumbnail']=str(dest.relative_to(P))
(P/'catalogo.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
db=sqlite3.connect(P/'catalogo.sqlite3')
for sql in ['ALTER TABLE assets ADD COLUMN description TEXT','ALTER TABLE assets ADD COLUMN duplicate_of TEXT']:
 try:db.execute(sql)
 except sqlite3.OperationalError:pass
for x in items:db.execute('UPDATE assets SET tags=?,review_status=?,description=?,duplicate_of=?,thumbnail=? WHERE id=?',(json.dumps(x['tags'],ensure_ascii=False),x['review_status'],x['description'],x['duplicate_of'],x.get('thumbnail'),x['id']))
db.commit();db.close()
rows=[]
for x in items:
 title=html.escape(x['tag']+' — '+x['description']);url=html.escape(x['relative_file']);name=html.escape(x['name'])
 if x['mime'].startswith('audio'):media=f'<audio controls preload="none" src="{url}"></audio>'
 elif x['mime'].startswith('video'):media=f'<video controls preload="none" poster="{x.get("thumbnail","")}" src="{url}"></video>'
 else:media=f'<img loading="lazy" src="{x.get("thumbnail",url)}">'
 search=unicodedata.normalize('NFKD',(x['description']+' '+x['name']+' '+x['category']).lower()).encode('ascii','ignore').decode()
 rows.append(f'<article data-search="{html.escape(search)}">{media}<h3>{title}</h3><p>{name}</p><a href="{url}" download>Arquivo</a> · <a href="{x["source"]}">Origem</a></article>')
(P/'index.html').write_text('''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>Banco de memes — Massacote</title><style>body{background:#17191e;color:#eee;font:15px sans-serif;margin:32px}h1{color:#ffd54c}input{padding:14px;width:60%;font-size:17px}main{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:20px;margin-top:20px}article{background:#252830;padding:12px;border-radius:9px}img,video{width:100%;height:190px;object-fit:contain}audio{width:100%}a{color:#ffd54c}p{overflow-wrap:anywhere}h3{font-size:15px}</style><h1>Banco de memes — Massacote Games</h1><p>Originais preservados. Categorias e descrições pesquisáveis; áudio/vídeo só carregam ao reproduzir.</p><input id="q" placeholder="Buscar: gato, confusao, computador, choro, audio…"><span id="n"></span><main>'''+''.join(rows)+'''</main><script>const q=document.querySelector('#q'),cards=[...document.querySelectorAll('article')];q.oninput=()=>{let s=q.value.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');let n=0;cards.forEach(c=>{let ok=s.split(' ').every(w=>c.dataset.search.includes(w));c.hidden=!ok;if(ok)n++});document.querySelector('#n').textContent=' '+n+' arquivos'};q.oninput()</script></html>''')
print('CATALOG_READY',len(items),'files',len(seen),'unique')
