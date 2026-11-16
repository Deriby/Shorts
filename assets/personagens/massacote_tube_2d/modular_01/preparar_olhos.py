"""Registro por olho: pares mantêm eixo e espaçamento do rosto aprovado."""
from pathlib import Path
import json,subprocess
import cv2,numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;S=Path('/workspace/scratch/tube_modular');R=P.parent
atlas=P/'fontes/atlas_olhos.png';arr=np.array(Image.open(atlas).convert('RGBA'));h,w=arr.shape[:2]
IDS=['01_normal','02_piscada_meio','03_piscada_fechado','04_bravo','05_confuso','06_pensando','07_desconfiado','08_assustado','09_rindo','10_piscando_esquerdo','11_piscando_direito','12_preocupado']
def run(*args):subprocess.run(['magick',*map(str,args)],check=True)
registration=[]
for n,ident in enumerate(IDS):
    col=n%4;row=n//4;y0=round(row*h/3);y1=round((row+1)*h/3);x0=col*384;cell=arr[y0:y1,x0:x0+384]
    run('-size','1024x1536','xc:none','PNG32:'+str(S/'pair.png'))
    placements=[]
    for k,(left,right,target) in enumerate([(0,192,(405,425)),(192,384,(526,403))]):
        side=cell[:,left:right];alpha=side[:,:,3]>140;white=(side[:,:,0]>190)&(side[:,:,1]>160)&(side[:,:,2]>100)&alpha
        num,lab,stats,cents=cv2.connectedComponentsWithStats(white.astype('uint8'),8);good=[i for i in range(1,num)if stats[i,4]>30]
        if good:i=max(good,key=lambda v:stats[v,4])
        else:
            ink=(side[:,:,0]<100)&(side[:,:,1]<90)&alpha;num,lab,stats,cents=cv2.connectedComponentsWithStats(ink.astype('uint8'),8);good=[i for i in range(1,num)if stats[i,4]>15];assert good;i=max(good,key=lambda v:cents[v,1])
        cx,cy=cents[i];scale=.66;px=round(target[0]-scale*cx);py=round(target[1]-scale*cy)
        run(atlas,'-crop',f'192x{y1-y0}+{x0+left}+{y0}','+repage',S/'half.png');run(S/'half.png','-alpha','extract','-threshold','45%',S/'eye_alpha.png')
        run(S/'half.png',S/'eye_alpha.png','-alpha','off','-compose','CopyOpacity','-composite',S/'half_clean.png')
        run(S/'half_clean.png','-resize','66%','-gravity','northwest','-background','none','-splice',f'{px}x{py}','-gravity','northwest','-extent','1024x1536',S/'half_canvas.png')
        run(S/'pair.png',S/'half_canvas.png','-compose','over','-composite','PNG32:'+str(S/'pair.png'))
        placements.append(dict(side=k,source_center=[float(cx),float(cy)],scale=scale,placement=[px,py],registered_eye_center=list(target)))
    run(S/'pair.png','PNG32:'+str(P/'olhos'/f'{ident}.png'));registration.append(dict(id=ident,eyes=placements))
# Include the exact approved eye/brow drawing as the default open state.
ref=R/'estudos_estilo/samurai_jack_v3/Previa_Massacote_Samurai_Jack_Brasao_M.png'
shape='polygon 342,379 431,377 434,402 341,405 polygon 468,327 582,325 584,363 471,371 polygon 353,407 444,403 450,439 389,441 365,430 polygon 477,400 580,371 565,409 480,432'
run('-size','1024x1536','xc:black','-fill','white','-draw',shape,S/'approved_eye_region.png')
run(ref,'-alpha','off','-fx','((r<0.32&&g<0.27&&b<0.27)||(r>0.78&&g>0.75&&b>0.50))?1:0','-colorspace','gray',S/'eye_colors.png')
run(S/'eye_colors.png',S/'approved_eye_region.png','-compose','Multiply','-composite',S/'approved_eye_mask.png')
run(ref,S/'approved_eye_mask.png','-alpha','off','-compose','CopyOpacity','-composite','PNG32:'+str(P/'olhos/00_normal_base.png'))
(P/'registro_encaixe.json').write_text(json.dumps(dict(canvas=[1024,1536],head_pivot=[466,738],moustache_pivot=[468,515],eyes=registration,default_eyes='00_normal_base.png'),ensure_ascii=False,indent=2)+'\n')
print('13 PARES DE OLHOS REGISTRADOS')
