"""Extrai planos dos assets existentes; as bases limpas foram produzidas com image_gen."""
from pathlib import Path
import subprocess,re
P=Path(__file__).resolve().parent;R=P.parent;M=P/'Filmora/midias';M.mkdir(parents=True,exist_ok=True)
S=Path('/workspace/scratch/tube_previa');S.mkdir(parents=True,exist_ok=True)
def run(*args):subprocess.run(['magick',*map(str,args)],check=True)
headpoly='polygon 0,0 1024,0 1024,625 676,625 618,665 599,735 589,792 462,792 449,734 418,667 353,625 0,625'
run('-size','1024x1536','xc:black','-fill','white','-draw',headpoly,S/'headmask.png')
run(S/'headmask.png','-negate','-fill','white','-draw','rectangle 463,735 589,793',S/'bodymask.png')
for pose,orig,cx,cy,roi in [('conversando','02_conversando',524,784,(335,495,716,651)),('apontando','04_apontando',490,774,(298,500,667,644))]:
    src=R/'lote_01/poses'/f'{orig}.png';clean=P/'fontes'/f'{pose}_base_limpa.png';x0,y0,x1,y1=roi
    expr=f'(i>={x0}&&i<={x1}&&j>={y0}&&j<={y1}&&r<0.86&&g<0.56&&b<0.49)?1:0'
    mask=S/f'{pose}_mustmask.png';run(src,'-alpha','off','-fx',expr,'-colorspace','gray',mask)
    out=subprocess.check_output(['magick',str(mask),'-define','connected-components:verbose=true','-define','connected-components:mean-color=true','-connected-components','8','null:'],text=True)
    matches=[]
    for line in out.splitlines():
        m=re.match(r'\s*(\d+):\s+\S+\s+\S+\s+(\d+)\s+gray\(255\)',line)
        if m:matches.append((int(m[2]),int(m[1])))
    assert matches,out
    run(mask,'-define','connected-components:mean-color=true','-define',f'connected-components:keep={max(matches)[1]}','-connected-components','8',mask)
    for part,source,mask_ in [('corpo',clean,S/'bodymask.png'),('cabeca',clean,S/'headmask.png'),('bigode',src,mask)]:
        alpha=S/f'{pose}_{part}_alpha.png';cut=S/f'{pose}_{part}.png'
        run(source,'-alpha','extract',mask_,'-compose','Multiply','-composite',alpha)
        run(source,alpha,'-alpha','off','-compose','CopyOpacity','-composite',cut)
        run(cut,'-resize','64%','-gravity','northwest','-background','none','-splice',f'{round(960-cx*.64)}x{round(540-cy*.64)}','-gravity','northwest','-extent','1920x1080','PNG32:'+str(M/f'{pose}_{part}.png'))
run('-size','1920x1080','gradient:#292137-#131e2a','-fill','#30253c','-draw','circle 960,680 1510,680',M/'fundo.png')
repo=next(p for p in P.parents if (p/'AGENTS.md').exists())
subprocess.run(['ffmpeg','-v','error','-y','-i',str(repo/'shorts/008-personagens-que-a-internet-estragou/production/00-intro/assets/voz/narracao_completa.wav'),'-t','9.3','-ar','48000','-ac','1','-c:a','pcm_s16le',str(M/'voz_teste.wav')],check=True)
print('LAYERS_PREPARED')
