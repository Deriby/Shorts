from pathlib import Path
import json,zipfile,hashlib
P=Path(__file__).resolve().parent;F=P/'output/Filmora';O=P/'output';OLD=P.parent/'output/Filmora';V3=P.parent/'revisao_memes_v3/output/Filmora'
notes='''MASSACOTE — MEMES COM TEMPO CORRIGIDO

Abra Massacote_MEMES_Tempo_Corrigido.wfp. A entrada e a saida continuam
rapidas. O tempo de permanencia dos 52 memes aumentou individualmente.
Os videos foram recortados dos originais novamente para incluir a acao e
a reacao. Os poucos arquivos curtos na origem usam o trecho inteiro:
nao foi criado congelamento, repeticao ou camera lenta para alongar.

ATUALIZACAO: requer o pacote com memes anterior. Extraia na mesma pasta e
mescle midias/, conservando os arquivos anteriores. Os 24 videos corrigidos
tem sufixo _R4 para evitar cache do arquivo curto. Use o novo WFP.

COMPLETO: extraia tudo para uma pasta nova e abra o WFP. Nao abra de dentro
do ZIP. Inclui as midias anteriores e os videos com duracao corrigida.

Seu projeto, vozes, musicas, efeitos, composições e duracao do longo foram
preservados. Nao houve outro render 3D. Os novos tempos/curvas, movimento,
recursos e pacotes foram conferidos. Filmora nao executado neste Linux;
a abertura e o resultado nativo dos plugins continuam sem teste aqui.
O MP4 antigo nao inclui esta edicao; exporte este novo WFP no Filmora.
'''
(F/'LEIA_PRIMEIRO.txt').write_text(notes)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
new={str(p.relative_to(F)):p for p in F.rglob('*')if p.is_file()}
old={str(p.relative_to(OLD)):p for p in OLD.rglob('*')if p.is_file()and p.suffix!='.wfp'and p.name not in['LEIA_PRIMEIRO.txt','LEIA_EDITADO.txt']}
v3={str(p.relative_to(V3)):p for p in V3.rglob('*')if p.is_file()and p.suffix!='.wfp'and p.name!='LEIA_PRIMEIRO.txt'}
report=[]
for name,files in [('Massacote_MEMES_Tempo_Atualizacao.zip',new),('Massacote_MEMES_Tempo_Completo.zip',{**old,**v3,**new})]:
 out=O/name
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=5,allowZip64=True)as z:
  for rel,p in files.items():z.write(p,rel,compress_type=zipfile.ZIP_STORED if p.suffix in['.mp4','.png','.wfp','.ttf']else zipfile.ZIP_DEFLATED)
 with zipfile.ZipFile(out)as z:
  assert z.testzip()is None;assert[n for n in z.namelist()if n.endswith('.wfp')]==['Massacote_MEMES_Tempo_Corrigido.wfp']
  for rel,p in files.items():assert hashlib.sha256(z.read(rel)).hexdigest()==sha(p)
 report.append(dict(file=name,bytes=out.stat().st_size,sha256=sha(out),all_member_hashes_checked=True,files=len(files)))
(P/'pacotes.json').write_text(json.dumps(report,indent=2)+'\n');print('TIMING_PACKAGES_READY',[(x['file'],x['bytes'])for x in report],flush=True)
