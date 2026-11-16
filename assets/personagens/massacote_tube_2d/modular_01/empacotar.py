from pathlib import Path
import json,zipfile,hashlib
P=Path(__file__).resolve().parent;dest=P/'entrega/Massacote_Tube_Modular_01_Completo.zip';dest.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for f in sorted(P.rglob('*')):
  if not f.is_file()or 'entrega'in f.relative_to(P).parts or '__pycache__'in f.parts or f.suffix in ['.log','.pyc']:continue
  z.write(f,Path('Massacote_Tube_Modular_01')/f.relative_to(P))
with zipfile.ZipFile(dest)as z:
 assert z.testzip()is None
 cat=json.loads(z.read('Massacote_Tube_Modular_01/catalogo.json'));assert len(cat['assets'])==39
 for a in cat['assets']:assert hashlib.sha256(z.read('Massacote_Tube_Modular_01/'+a['file'])).hexdigest()==a['sha256']
 assert z.read('Massacote_Tube_Modular_01/previa/Filmora/Massacote_Tube_Modular_Previa.wfp')==(P/'previa/Filmora/Massacote_Tube_Modular_Previa.wfp').read_bytes()
print('PACOTE_VERIFICADO',dest,round(dest.stat().st_size/1e6,2),'MB',flush=True)
