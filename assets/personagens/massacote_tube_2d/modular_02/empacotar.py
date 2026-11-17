"""Cria o ZIP autossuficiente e verifica CRC de cada membro."""
from pathlib import Path
import hashlib,json,zipfile
P=Path(__file__).resolve().parent;D=P/'entrega';D.mkdir(exist_ok=True)
out=D/'Massacote_Tube_Modular_02_30_Poses_10_Olhares.zip'
files=sorted(p for p in P.rglob('*') if p.is_file() and 'entrega' not in p.relative_to(P).parts and '__pycache__' not in p.parts)
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files: z.write(p,Path('Massacote_Tube_Modular_02')/p.relative_to(P))
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None; assert len(z.namelist())==len(files)
digest=hashlib.sha256(out.read_bytes()).hexdigest()
(D/'manifesto.json').write_text(json.dumps(dict(file=out.name,bytes=out.stat().st_size,sha256=digest,members=len(files),new_poses=30,new_eyes=10),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(file=str(out),bytes=out.stat().st_size,members=len(files),sha256=digest)))
