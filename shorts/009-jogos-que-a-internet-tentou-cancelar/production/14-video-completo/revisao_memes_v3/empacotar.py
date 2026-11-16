from pathlib import Path
import zipfile,json,hashlib
P=Path(__file__).resolve().parent;F=P/'output/Filmora';OLD=P.parent/'output/Filmora';O=P/'output'
notes='''MASSACOTE — EDICAO COM MEMES, 16:9

Abra Massacote_Completo_MEMES.wfp. O projeto parte do WFP que voce reenviou.
Os cortes, efeitos, keyframes, composicoes e audios que voce editou foram
preservados. Entraram 52 intervencoes de memes e 8 sons pontuais em faixas
novas, separadas e editaveis. As midias originais nao foram substituidas.

PACOTE DE ATUALIZACAO: extraia ao lado da pasta midias do projeto anterior.
Mescle a pasta midias deste ZIP com a anterior, mantendo os arquivos antigos.
O nome do WFP e novo; seu projeto anterior nao precisa ser sobrescrito.

PACOTE COMPLETO: extraia tudo para uma pasta nova e abra o WFP dessa pasta.
Nao abra o projeto diretamente de dentro do ZIP.

O MP4 antigo nao inclui esta edicao. Para obter o video completo atualizado,
exporte este WFP no Filmora. A estrutura, recursos, movimento dos novos MP4s,
originalidade das trilhas, keyframes e quadros foram conferidos. O Filmora
proprietario nao foi executado neste Linux; os efeitos que voce adicionou
continuam nativos e dependem da sua instalacao, como no projeto original.

Os memes ficam limpos, sem filtro PSX. A voz e a duracao do longo permanecem
inteiras. O novo quarto aprovado vale para producoes futuras; nao houve
novo render 3D deste longo. O banco completo de 303 arquivos foi salvo
separadamente no repositorio, em assets/biblioteca_memes/.
'''
(F/'LEIA_PRIMEIRO.txt').write_text(notes)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
new={str(p.relative_to(F)):p for p in F.rglob('*')if p.is_file()}
old={str(p.relative_to(OLD)):p for p in OLD.rglob('*')if p.is_file()and p.suffix!='.wfp'and p.name not in['LEIA_PRIMEIRO.txt','LEIA_EDITADO.txt']}
reports=[]
for name,files in [('Massacote_MEMES_Atualizacao.zip',new),('Massacote_MEMES_Completo.zip',{**old,**new})]:
 out=O/name
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=5,allowZip64=True)as z:
  for rel,p in files.items():z.write(p,rel,compress_type=zipfile.ZIP_STORED if p.suffix in['.mp4','.png','.wfp','.ttf']else zipfile.ZIP_DEFLATED)
 with zipfile.ZipFile(out)as z:
  assert z.testzip()is None;assert [n for n in z.namelist()if n.endswith('.wfp')]==['Massacote_Completo_MEMES.wfp']
  for rel,p in files.items():assert hashlib.sha256(z.read(rel)).hexdigest()==sha(p)
 reports.append(dict(file=name,bytes=out.stat().st_size,sha256=sha(out),files=len(files),all_member_hashes_checked=True))
(P/'pacotes.json').write_text(json.dumps(reports,indent=2)+'\n');print('PACKAGES_READY',[(r['file'],r['bytes'])for r in reports],flush=True)
