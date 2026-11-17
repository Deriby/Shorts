"""Extrai os dez pares gerados e registra cada olho no rosto aprovado."""
from pathlib import Path
import json, subprocess
import cv2, numpy as np
from PIL import Image
P = Path(__file__).resolve().parent
S = Path('/workspace/scratch/tube_modular_02/eyes'); S.mkdir(parents=True, exist_ok=True)
plan = json.loads((P / 'plano_lote.json').read_text())
atlas = P / 'fontes/atlas_olhos.png'
arr = np.array(Image.open(atlas).convert('RGBA')); h,w = arr.shape[:2]
def run(*args): subprocess.run(['magick', *map(str,args)], check=True)
registration=[]
for n, eye in enumerate(plan['eyes']):
    row,col=divmod(n,5); x0=round(col*w/5); x1=round((col+1)*w/5); y0=round(row*h/2); y1=round((row+1)*h/2)
    cell=arr[y0:y1,x0:x1]; mid=(x1-x0)//2
    run('-size','1024x1536','xc:none','PNG32:'+str(S/'pair.png'))
    placements=[]
    for k,(left,right,target) in enumerate([(0,mid,(405,425)),(mid,x1-x0,(526,403))]):
        side=cell[:,left:right]; alpha=side[:,:,3]>140
        white=(side[:,:,0]>190)&(side[:,:,1]>160)&(side[:,:,2]>100)&alpha
        num,lab,stats,cents=cv2.connectedComponentsWithStats(white.astype('uint8'),8)
        good=[i for i in range(1,num) if stats[i,4]>30]; assert good,eye
        i=max(good,key=lambda v:stats[v,4]); cx,cy=cents[i]
        scale=.78; px=round(target[0]-scale*cx); py=round(target[1]-scale*cy)
        run(atlas,'-crop',f'{right-left}x{y1-y0}+{x0+left}+{y0}','+repage',S/'half.png')
        run(S/'half.png','-alpha','extract','-threshold','45%',S/'alpha.png')
        run(S/'half.png',S/'alpha.png','-alpha','off','-compose','CopyOpacity','-composite',S/'clean.png')
        run(S/'clean.png','-resize','78%','-gravity','northwest','-background','none','-splice',f'{px}x{py}','-gravity','northwest','-extent','1024x1536',S/'canvas.png')
        run(S/'pair.png',S/'canvas.png','-compose','over','-composite','PNG32:'+str(S/'pair.png'))
        placements.append(dict(side=k,source_center=[float(cx),float(cy)],scale=scale,placement=[px,py],registered_eye_center=list(target)))
    run(S/'pair.png','PNG32:'+str(P/'olhos'/(eye['id']+'.png')))
    registration.append(dict(id=eye['id'],eyes=placements))
(P/'registro_encaixe.json').write_text(json.dumps(dict(canvas=[1024,1536],head_pivot=[466,738],moustache_pivot=[468,515],eyes=registration,shared_head='../modular_01/rig/cabeca_limpa.png'),ensure_ascii=False,indent=2)+'\n')
print('10 NOVOS OLHARES REGISTRADOS')
