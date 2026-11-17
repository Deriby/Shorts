"""Exporta/recorta/registra artes image_gen por ImageMagick, sem desenhar novas poses.

OpenCV lê as imagens para localizar lentes, contornos e mãos. Os recortes, alfa,
registros e composições são operações técnicas executadas pelo ImageMagick.
"""
from pathlib import Path
import json,sys,subprocess,math,shutil,hashlib,os
sys.path.insert(0,'/workspace/tools/shorts_asr')
import cv2,numpy as np
P=Path(__file__).resolve().parent;S=Path('/workspace/scratch/tube_oculos30');S.mkdir(parents=True,exist_ok=True)
MASTER=P.parent/'estudos_estilo/oculos_3d_v1/Previa_Massacote_Oculos_3D.png';W=H=2048;OX,OY=498,200
PLAN=json.loads((P/'plano.json').read_text());REG=[]
def run(*args):subprocess.run(['magick','-limit','thread','2',*map(str,args)],check=True,stdout=subprocess.DEVNULL)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def eyes(a):
    b,g,r,al=cv2.split(a);h,w=a.shape[:2];out=[]
    masks=[((r>180)&(g<90)&(b<90)&(al>180)),((b>170)&(r<100)&(g<180)&(al>180))]
    for mask in masks:
        n,l,st,ct=cv2.connectedComponentsWithStats(mask.astype('uint8'),8);rows=[]
        for k in range(1,n):
            x,y,ww,hh,area=st[k]
            if h*.15<ct[k][1]<h*.48 and area>150 and ww/hh>.8:rows.append((int(area),ct[k]))
        assert rows,(a.shape,'Lentes não localizadas');out.append(max(rows,key=lambda x:x[0])[1])
    return np.array(out)
REF_EYES=eyes(cv2.imread(str(MASTER),-1));TARGET=REF_EYES+np.array([OX,OY])
def align(source_points,target_points):
    x=complex(*(source_points[1]-source_points[0]));y=complex(*(target_points[1]-target_points[0]));z=y/x
    A=np.array([[z.real,-z.imag],[z.imag,z.real]]);t=target_points[0]-A@source_points[0]
    return [z.real,z.imag,-z.imag,z.real,*t]
def warp(src,params,out):
    run(src,'-virtual-pixel','transparent','-define',f'distort:viewport={W}x{H}+0+0','-distort','AffineProjection',','.join(f'{v:.9f}'for v in params),'+repage','-strip','PNG32:'+str(out))
def svgmask(polygons,width,height,out,pad=0):
    paths=[]
    for points in polygons:
        coords=' '.join(f'{float(x):.2f},{float(y):.2f}'for x,y in points)
        paths.append('polygon '+coords)
    command=' '.join(paths)
    args=['-size',f'{width}x{height}','xc:black','-fill','white','-stroke','white','-strokewidth',str(pad*2)]
    if command:args +=['-draw',command]
    run(*args,'-colorspace','gray','-threshold','50%',out)
def alpha_cut(src,mask,out):
    # Multiplica pela transparência existente; não transforma o fundo invisível em pixels.
    alpha=S/'alpha_tmp.png';run(src,'-alpha','extract','-alpha','off',mask,'-alpha','off','-compose','Multiply','-composite','-alpha','off','-type','Grayscale',alpha)
    run(src,alpha,'-alpha','off','-compose','CopyOpacity','-composite','-strip','PNG32:'+str(out))
def clean_sprite(src,out):
    a=cv2.imread(str(src),-1);b,g,r,al=cv2.split(a)
    dark=((r<110)&(g<80)&(b<85)&(al>100)).astype('uint8')*255
    contours,_=cv2.findContours(dark,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE);contour=max(contours,key=cv2.contourArea)
    assert cv2.contourArea(contour)>.15*a.shape[0]*a.shape[1]
    mask=S/'main_mask.png';svgmask([contour.reshape(-1,2)],a.shape[1],a.shape[0],mask,pad=round(a.shape[1]*.023))
    alpha_cut(src,mask,out)
def prepare_shared():
    common=P/'camadas';common.mkdir(exist_ok=True)
    clean_sprite(MASTER,S/'master_limpo.png')
    # Mesma cabeça aprovada para todas as poses; a máscara deixa gola e ombros no corpo.
    rawhead=[(0,0),(1052,0),(1052,735),(700,735),(635,735),(605,840),(590,878),(558,900),(485,900),(449,878),(438,833),(420,770),(390,735),(0,735)]
    region=[(x+OX,y+OY)for x,y in rawhead];region[0]=(0,0);region[1]=(W,0);region[2]=(W,935);region[-1]=(0,935)
    svgmask([region],W,H,S/'head_region.png');run(S/'head_region.png','-alpha','off','-channel','RGB','-negate','+channel','-alpha','off','-type','Grayscale',S/'body_region.png')
    # Extrai o bigode original por seu contorno. A área sob ele é preenchida por image_gen.
    a=cv2.imread(str(MASTER),-1);roi=a[590:740,280:780];b,g,r,al=cv2.split(roi)
    mask=((r<190)&(g<120)&(b<110)&(al>180)).astype('uint8')*255
    cs,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE);c=max(cs,key=cv2.contourArea).reshape(-1,2)+np.array([280,590])
    assert cv2.contourArea(c)>30000
    svgmask([c],1052,1494,S/'bigode_mask_raw.png',pad=2)
    alpha_cut(MASTER,S/'bigode_mask_raw.png',S/'bigode_raw.png')
    warp(S/'bigode_raw.png',[1,0,0,1,OX,OY],common/'bigode_repouso.png')
    # O resto do rosto continua pixel-idêntico ao aprovado; só a área oculta muda.
    under=P/'fontes/base_sem_bigode.png';params=align(eyes(cv2.imread(str(under),-1)),REF_EYES)
    run(under,'-virtual-pixel','transparent','-define','distort:viewport=1052x1494+0+0','-distort','AffineProjection',','.join(map(str,params)),'+repage',S/'under_aligned.png')
    alpha_cut(S/'under_aligned.png',S/'bigode_mask_raw.png',S/'patch.png')
    run(S/'master_limpo.png',S/'patch.png','-compose','over','-composite',S/'master_sem_bigode.png')
    warp(S/'master_sem_bigode.png',[1,0,0,1,OX,OY],S/'master_canvas.png');alpha_cut(S/'master_canvas.png',S/'head_region.png',common/'cabeca_sem_bigode.png')
    run(common/'cabeca_sem_bigode.png',common/'bigode_repouso.png','-compose','over','-composite',common/'cabeca_com_bigode.png')
    make_body_mask()
    # Estados técnicos alternativos: deformação suave do mesmo PNG, sem redesenho.
    cx,cy=OX+527,OY+667
    for name,sx,sy,dy in [('bigode_fala_a',1.02,1.06,-2),('bigode_fala_b',1.035,.965,1)]:
        warp(common/'bigode_repouso.png',[sx,0,0,sy,cx*(1-sx),cy*(1-sy)+dy],common/(name+'.png'))
    original=cv2.imread(str(S/'master_canvas.png'),-1)
    (common/'LEIA-ME.txt').write_text('Canvas 2048x2048. Ordem: corpo da pose, cabeca_sem_bigode, bigode_repouso (ou fala A/B), frente quando existir. Cabeca_com_bigode e alternativa fixa; nao a some aos outros dois. As lentes ja fazem parte da cabeca: nao ha faixa de olhos. Preserve as margens e use a mesma transformacao nas camadas.\n')

def handmask(raw,redblue,out):
    a=cv2.imread(str(raw),-1);hsv=cv2.cvtColor(a[:,:,:3],cv2.COLOR_BGR2HSV);alpha=a[:,:,3]
    skin=((hsv[:,:,0]>7)&(hsv[:,:,0]<31)&(hsv[:,:,1]>65)&(hsv[:,:,2]>155)&(alpha>180)).astype('uint8')
    n,labels,stats,cents=cv2.connectedComponentsWithStats(skin,8);polys=[];rx,ry=redblue[0];bx,by=redblue[1]
    for k in range(1,n):
        x,y,w,h,area=stats[k];cx,cy=cents[k]
        if area<180 or cy<ry+78:continue
        # O rosto fica entre as lentes; as mãos têm componentes de pele separados.
        if rx-50<cx<bx+45 and cy<ry+190:continue
        component=(labels==k).astype('uint8')*255;cs,_=cv2.findContours(component,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        if cs:polys.append(max(cs,key=cv2.contourArea).reshape(-1,2))
    svgmask(polys,a.shape[1],a.shape[0],out,pad=10)

def make_body_mask():
    # Retira a silhueta da cabeça, preservando mangas elevadas no espaço ao lado dela.
    run(P/'camadas/cabeca_com_bigode.png','-alpha','extract','-alpha','off','-threshold','1%','-morphology','Dilate','Disk:12',S/'head_silhouette.png')
    run(S/'head_silhouette.png','-crop','2048x935+0+0','+repage',S/'remove_top.png')
    run(S/'head_region.png','-crop','2048x1113+0+935','+repage',S/'remove_bottom.png')
    run(S/'remove_top.png',S/'remove_bottom.png','-append','-alpha','off','-type','Grayscale',S/'remove_head_region.png')
    run(S/'remove_head_region.png','-alpha','off','-channel','RGB','-negate','+channel','-alpha','off','-type','Grayscale',S/'body_region.png')

def process_pose(pose):
    ident=pose['id'];source=P/'fontes'/f'lote_{pose["batch"]:02d}.png';a=cv2.imread(str(source),-1);h,w=a.shape[:2];col=pose['column'];x0=round(col*w/3);x1=round((col+1)*w/3)
    if pose.get('crop_bounds'):x0,x1=pose['crop_bounds']
    raw=S/(ident+'_raw.png');run(source,'-crop',f'{x1-x0}x{h}+{x0}+0','+repage',raw)
    clean=S/(ident+'_limpo.png');clean_sprite(raw,clean)
    pts=eyes(cv2.imread(str(clean),-1));params=align(pts,TARGET);full=S/(ident+'_registrado.png');warp(clean,params,full)
    body=P/'camadas'/(ident+'_corpo.png');alpha_cut(full,S/'body_region.png',body)
    handmask(clean,pts,S/'hand_region.png');warp(S/'hand_region.png',params,S/'hand_warp.png')
    run(S/'hand_warp.png','-alpha','off',S/'remove_head_region.png','-alpha','off','-compose','Multiply','-composite','-alpha','off','-type','Grayscale',S/'front_mask.png')
    front=P/'camadas'/(ident+'_frente.png');alpha_cut(full,S/'front_mask.png',front)
    fa=cv2.imread(str(front),-1)[:,:,3];hasfront=int((fa>128).sum())>200
    if not hasfront:front.unlink()
    out=P/'poses'/(ident+'.png');args=[body,P/'camadas/cabeca_com_bigode.png','-compose','over','-composite']
    if hasfront:args +=[front,'-compose','over','-composite']
    run(*args,'-strip','PNG32:'+str(out))
    REG.append(dict(id=ident,source=str(source.relative_to(P)),crop=[x0,0,x1-x0,h],source_lens_centers=pts.tolist(),target_lens_centers=TARGET.tolist(),affine=params,body=str(body.relative_to(P)),front=str(front.relative_to(P))if hasfront else None,pose=str(out.relative_to(P))))
    print('POSE',ident,flush=True)

def refresh_fronts():
    make_body_mask()
    data=json.loads((P/'registro_encaixe.json').read_text())
    for row in data['poses']:
        ident=row['id'];clean=S/(ident+'_limpo.png');full=S/(ident+'_registrado.png');params=row['affine'];pts=np.array(row['source_lens_centers']);body=P/row['body']
        alpha_cut(full,S/'body_region.png',body)
        handmask(clean,pts,S/'hand_region.png');warp(S/'hand_region.png',params,S/'hand_warp.png')
        run(S/'hand_warp.png','-alpha','off',S/'remove_head_region.png','-alpha','off','-compose','Multiply','-composite','-alpha','off','-type','Grayscale',S/'front_mask.png')
        front=P/'camadas'/(ident+'_frente.png');alpha_cut(full,S/'front_mask.png',front)
        hasfront=int((cv2.imread(str(front),-1)[:,:,3]>128).sum())>200
        if not hasfront:front.unlink()
        row['front']=str(front.relative_to(P))if hasfront else None
        args=[body,P/'camadas/cabeca_com_bigode.png','-compose','over','-composite']
        if hasfront:args +=[front,'-compose','over','-composite']
        run(*args,'-strip','PNG32:'+str(P/row['pose']))
        print('FRENTE',ident,flush=True)
    (P/'registro_encaixe.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':
    if '--frentes' in sys.argv:refresh_fronts();raise SystemExit
    start=int(sys.argv[2])if len(sys.argv)>2 else 0
    if start==0:prepare_shared()
    else:REG.extend(json.loads((P/'registro_encaixe.json').read_text())['poses'])
    limit=int(sys.argv[1])if len(sys.argv)>1 else 30
    for pose in PLAN['poses'][start:limit]:process_pose(pose)
    (P/'registro_encaixe.json').write_text(json.dumps(dict(canvas=[W,H],shared_head=True,head_pivot=[OX+527,OY+880],moustache_pivot=[OX+527,OY+667],eye_animation=False,poses=REG),ensure_ascii=False,indent=2)+'\n')
