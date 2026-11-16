"""Extrai e registra peças geradas com image_gen; não redesenha a arte."""
from pathlib import Path
import subprocess,re,json
from PIL import Image
import numpy as np,cv2
P=Path(__file__).resolve().parent;S=Path('/workspace/scratch/tube_modular');S.mkdir(parents=True,exist_ok=True)
ROOT=P.parent;REF=ROOT/'estudos_estilo/samurai_jack_v3/Previa_Massacote_Samurai_Jack_Brasao_M.png'
IDS=['01_neutro','02_conversando','03_debochado','04_apontando','05_confuso','06_bravo','07_pensando','08_rindo','09_assustado','10_facepalm']
EYES=['01_normal','02_piscada_meio','03_piscada_fechado','04_bravo','05_confuso','06_pensando','07_desconfiado','08_assustado','09_rindo','10_piscando_esquerdo','11_piscando_direito','12_preocupado']
def run(*args):subprocess.run(['magick',*map(str,args)],check=True)
def mask(shape,path):run('-size','1024x1536','xc:black','-fill','white','-stroke','white','-strokewidth','1','-draw',shape,path)
def cut(source,mask_,out):run(source,mask_,'-alpha','off','-compose','CopyOpacity','-composite','PNG32:'+str(out))
def largest_mask(source,out):
    tmp=S/'threshold.png';run(source,'-alpha','extract','-threshold','50%',tmp)
    stats=subprocess.check_output(['magick',str(tmp),'-define','connected-components:verbose=true','-define','connected-components:mean-color=true','-connected-components','8','null:'],text=True)
    candidates=[]
    for line in stats.splitlines():
        m=re.match(r'\s*(\d+):\s+\S+\s+\S+\s+(\d+)\s+gray\(255\)',line)
        if m:candidates.append((int(m[2]),int(m[1])))
    assert candidates,stats
    run(tmp,'-define','connected-components:mean-color=true','-define',f'connected-components:keep={max(candidates)[1]}','-connected-components','8',out)
# Keep geometry and cutouts clean; the head plane is identical across all poses.
master=P/'fontes/02_conversando.png';mastermask=S/'masteralpha.png';largest_mask(master,mastermask);masterclean=S/'master.png';cut(master,mastermask,masterclean)
head_shape='polygon 285,40 690,40 800,330 805,455 660,510 600,570 555,615 530,760 395,760 390,635 315,535 305,470 205,440 200,330 250,270'
headmask=S/'head_region.png';mask(head_shape,headmask)
run(mastermask,headmask,'-compose','Multiply','-composite',S/'head_alpha.png');cut(masterclean,S/'head_alpha.png',P/'rig/cabeca_limpa.png')
front_shapes={
 '07_pensando':'polygon 402,620 430,613 442,640 456,638 510,604 560,590 562,620 510,653 520,667 531,667 540,700 542,746 514,760 482,788 456,828 437,858 388,834 403,798 413,753 406,718 394,713 395,665',
 '10_facepalm':'polygon 450,368 457,338 466,305 478,281 508,271 522,257 554,251 580,277 613,297 633,347 635,431 650,456 678,475 688,488 634,541 597,525 546,484 531,457 522,417 498,398 466,380'
}
for ident in IDS:
    src=P/'fontes'/f'{ident}.png';alpha=S/f'{ident}_alpha.png';largest_mask(src,alpha);clean=S/f'{ident}_clean.png';cut(src,alpha,clean)
    full=P/'poses'/f'{ident}.png'
    run(clean,masterclean,headmask,'-channel','RGBA','-fx','u[2].r>0.5?u[1]:u[0]','PNG32:'+str(full))
    # Body plane excludes the head; duplicate a neck strip under the moving head.
    run(headmask,'-negate',S/'body_region.png');run(alpha,S/'body_region.png','-compose','Multiply','-composite',S/'body_alpha.png');cut(clean,S/'body_alpha.png',S/'body.png')
    mask('rectangle 404,705 519,755',S/'neck_region.png');run(mastermask,S/'neck_region.png','-compose','Multiply','-composite',S/'neck_alpha.png');cut(masterclean,S/'neck_alpha.png',S/'neck.png')
    run(S/'body.png',S/'neck.png','-compose','over','-composite','PNG32:'+str(P/'rig'/f'{ident}_corpo.png'))
    if ident in front_shapes:
        fm=S/f'{ident}_frontmask.png';mask(front_shapes[ident],fm);run(alpha,fm,'-compose','Multiply','-composite',S/'front_alpha.png');front=P/'frente'/f'{ident}_frente.png';cut(clean,S/'front_alpha.png',front)
        run(full,front,'-compose','over','-composite','PNG32:'+str(full))
# Exact moustache artwork from the approved reference; isolate ink/brown inside its contour.
shape='polygon 287,477 294,507 307,520 330,523 353,510 385,486 412,473 432,470 451,476 468,487 490,470 508,459 531,454 550,458 578,475 598,487 611,477 617,458 613,444 626,456 633,478 632,493 621,516 601,531 574,544 548,550 526,549 500,540 480,531 469,522 448,543 424,560 396,571 366,578 338,578 313,571 296,558 285,543 280,524 281,502'
mask(shape,S/'must_region.png')
run(REF,'-alpha','off','-fx','(r<0.90&&g<0.55&&b<0.43)?1:0','-colorspace','gray',S/'must_colors.png')
run(S/'must_region.png',S/'must_colors.png','-compose','Multiply','-composite',S/'must_mask.png');cut(REF,S/'must_mask.png',P/'bigode/01_bigode_repouso.png')
run(P/'bigode/01_bigode_repouso.png','-virtual-pixel','transparent','-define','distort:viewport=1024x1536+0+0','-distort','AffineProjection','1.024,0,0,1.075,-11.232,-42.025','+repage','PNG32:'+str(P/'bigode/02_bigode_levantado.png'))
run(P/'bigode/01_bigode_repouso.png','-virtual-pixel','transparent','-define','distort:viewport=1024x1536+0+0','-distort','AffineProjection','0.99,0,0,0.965,4.68,20.025','+repage','PNG32:'+str(P/'bigode/03_bigode_comprimido.png'))
run('-dispose','Background','-delay','12',P/'bigode/01_bigode_repouso.png','-delay','8',P/'bigode/02_bigode_levantado.png','-delay','10',P/'bigode/01_bigode_repouso.png','-delay','8',P/'bigode/03_bigode_comprimido.png','-delay','8',P/'bigode/02_bigode_levantado.png','-delay','14',P/'bigode/01_bigode_repouso.png','-loop','0','-define','webp:lossless=true',P/'bigode/Previa_Bigode.webp')
subprocess.run([__import__('sys').executable,str(P/'preparar_olhos.py')],check=True)
# User-facing assembled thumbnails are previews; delivered pose bases remain faceless.
expression_for_pose=[0,0,6,0,4,3,5,8,7,11]
for ident,ei in zip(IDS,expression_for_pose):
    args=[P/'poses'/f'{ident}.png',P/'olhos'/('00_normal_base.png' if ei==0 else f'{EYES[ei]}.png'),'-compose','over','-composite',P/'bigode/01_bigode_repouso.png','-compose','over','-composite']
    if ident in front_shapes:args += [P/'frente'/f'{ident}_frente.png','-compose','over','-composite']
    run(*args,'-background','#f2eee6','-alpha','remove','-alpha','off',P/'montados'/f'{ident}.jpg')
run('montage',*[P/'montados'/f'{ident}.jpg'for ident in IDS],'-thumbnail','240x360','-background','#f2eee6','-tile','5x2','-geometry','240x360+10+10',P/'Previa_10_Poses_Montadas.jpg')
print('ASSETS_MODULARES_PRONTOS',len(IDS),len(EYES)+1,flush=True)
