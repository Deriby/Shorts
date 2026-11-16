from pathlib import Path
import subprocess
P=Path(__file__).resolve().parent;M=P/'previa/Filmora/midias';M.mkdir(parents=True,exist_ok=True)
planes={f'corpo_{p.stem.removesuffix("_corpo")}':p for p in (P/'rig').glob('*_corpo.png')}
planes['cabeca_limpa']=P/'rig/cabeca_limpa.png';planes['bigode_repouso']=P/'bigode/01_bigode_repouso.png'
planes.update({'olhos_'+p.stem:p for p in (P/'olhos').glob('*.png')})
planes.update({'frente_'+p.stem.removesuffix('_frente'):p for p in (P/'frente').glob('*.png')})
for name,p in planes.items():
 subprocess.run(['magick',str(p),'-resize','64%','-gravity','northwest','-background','none','-splice','662x68','-gravity','northwest','-extent','1920x1080','PNG32:'+str(M/(name+'.png'))],check=True)
print('PLANOS_PARA_FILMORA',len(planes))
