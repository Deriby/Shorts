"""Registra as poses regeneradas no canvas e produz PNGs prontos para uso."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

import cv2
import numpy as np
from PIL import Image,ImageDraw

HERE=Path(__file__).resolve().parents[1]
REPO=next(p for p in HERE.parents if (p/'AGENTS.md').exists())
SOURCE=HERE/'fontes'
OUT=HERE/'output'
KIT=OUT/'Camadas'
FLAT=OUT/'Poses'
BASE=(REPO/'shorts/010-sonic-memories-beyond/production/recortes_regenerados_01/'
      'output/Filmora/midias_regeneradas')
W,H=1080,1920
SETS=[
    ('04_apontando_esquerda','05_apontando_direita','06_apontando_cima'),
    ('09_joinha','12_deu_de_ombros','15_fazendo_ressalva'),
    ('16_desespero','20_tramando','24_apresentando_lado'),
]


def checksum(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def cut(image,count=3):
    """Extrai o alfa dos sprites desenhados sobre fundo uniforme."""
    p=np.asarray(image.convert('RGB'),dtype=np.float32)
    r,g,b=p.transpose(2,0,1)
    excess=g-np.maximum(r,b)
    alpha=np.clip(1-(excess-12)/50,0,1)
    keep=(alpha>.45).astype('uint8')
    n,label,stats,centroids=cv2.connectedComponentsWithStats(keep,8)
    ids=sorted(sorted(range(1,n),key=lambda i:-stats[i,4])[:count],key=lambda i:centroids[i,0])
    assert len(ids)==count and min(stats[i,4] for i in ids)>18000
    result=[]
    for i in ids:
        selection=cv2.dilate((label==i).astype('uint8'),np.ones((3,3),np.uint8))
        x,y,w,h,_=stats[i]
        lo_x,lo_y=max(0,x-3),max(0,y-3)
        hi_x,hi_y=x+w+3,y+h+3
        local=p[lo_y:hi_y,lo_x:hi_x].copy()
        a=alpha[lo_y:hi_y,lo_x:hi_x]*selection[lo_y:hi_y,lo_x:hi_x]
        # Evita contaminação verde da borda no canal RGB antialias.
        edge=(a>0)&(a<.996)
        local[:,:,1][edge]=np.minimum(local[:,:,1][edge],np.maximum(local[:,:,0][edge],local[:,:,2][edge]))
        rgba=np.dstack([local,a*255])
        result.append(np.rint(rgba).astype('uint8'))
    return result


def neck(img):
    h,w=img.shape[:2]
    r,g,b,a=img.transpose(2,0,1).astype('float32')
    skin=(r>150)&(g>73)&(g<r*.91)&(b<g*.94)&(a>245)
    n,labels,stats,center=cv2.connectedComponentsWithStats(skin.astype('uint8'),8)
    items=[i for i in range(1,n) if abs(center[i,0]-w*.5)<w*.32 and
           stats[i,4]>210 and stats[i,1]<h*.32]
    assert items,('pescoço não localizado',img.shape)
    y0=min(stats[i,1] for i in items)
    ids=[i for i in items if stats[i,1]<y0+h*.07]
    i=min(ids,key=lambda i:stats[i,1]+.18*abs(center[i,0]-w*.5))
    x,y,w,h,_=map(int,stats[i])
    return float(center[i,0]),y,[x,y,w,h]


def place(art,pose,source):
    h,w=art.shape[:2]
    nx,ny,bounds=neck(art)
    top=952
    scale=min((1557-top)/(h-ny),1018/w)
    mid=539.5
    if mid-scale*nx<15 or mid+scale*(w-nx)>W-15:
        scale=min(scale,(mid-15)/nx,(W-15-mid)/(w-nx))
    trans=np.array([[scale,0,mid-scale*nx],[0,scale,top-scale*ny]],dtype='float32')
    pixels=art.astype('float32')
    pixels[:,:,:3]*=pixels[:,:,3:4]/255
    result=cv2.warpAffine(pixels,trans,(W,H),flags=cv2.INTER_LANCZOS4)
    a=np.clip(result[:,:,3:4],0,255)
    rgb=np.divide(result[:,:,:3]*255,a,out=np.zeros_like(result[:,:,:3]),where=a>1e-4)
    comp=np.uint8(np.rint(np.dstack([np.clip(rgb,0,255),a])))
    file=KIT/f'Corpo_{pose}.png'
    Image.fromarray(comp).save(file)
    return file,dict(pose=pose,source=source.name,neck_box=bounds,placement=trans.tolist())


def assemble():
    for folder in (KIT,FLAT):
        folder.mkdir(parents=True,exist_ok=True)
    head=KIT/'Cabeca.png'
    moustache=KIT/'Bigode.png'
    shutil.copy2(BASE/'Cabeca_R3.png',head)
    shutil.copy2(BASE/'Bigode_R3.png',moustache)
    entries=[]
    for idx,poses in enumerate(SETS,1):
        source=SOURCE/f'poses_{idx}.png'
        row=cut(Image.open(source))
        for pose,art in zip(poses,row,strict=True):
            override=SOURCE/f'{pose}.png'
            if override.exists():
                art,=cut(Image.open(override),count=1)
                source_file=override
            else:
                source_file=source
            body,record=place(art,pose,source_file)
            image=Image.new('RGBA',(W,H))
            for part in (body,head,moustache):
                image.alpha_composite(Image.open(part).convert('RGBA'))
            x0,y0,x1,y1=image.getbbox()
            assert 0<x0<x1<W and 0<y0<y1<H
            flat=FLAT/f'{pose}.png'
            image.save(flat)
            record.update(merged=flat.relative_to(OUT).as_posix(),body=body.relative_to(OUT).as_posix(),
                          body_sha256=checksum(body),png_sha256=checksum(flat),bounds=[x0,y0,x1,y1])
            entries.append(record)
    (HERE/'registro.json').write_text(json.dumps({'canvas':[W,H],'poses':entries},ensure_ascii=False,indent=2)+'\n')

    gallery=Image.new('RGB',(1500,1770),'#384661')
    d=ImageDraw.Draw(gallery)
    for i,entry in enumerate(entries):
        p=OUT/entry['merged']
        im=Image.open(p).convert('RGBA')
        im=im.crop(im.getbbox())
        im.thumbnail((473,545),Image.Resampling.LANCZOS)
        x=i%3*500;y=i//3*590
        gallery.paste(im,(x+(500-im.width)//2,y+3),im)
        d.text((x+15,y+558),p.stem.replace('_',' '),fill='white')
    gallery.save(OUT/'Prancha_9_Poses.jpg',quality=93)


def hand_sheet():
    files=sorted(KIT.glob('Corpo_*.png'))
    sheet=Image.new('RGB',(1620,1080),'#526079')
    draw=ImageDraw.Draw(sheet)
    for i,file in enumerate(files):
        image=Image.open(file)
        r,g,b,a=np.asarray(image,dtype='float32').transpose(2,0,1)
        yy,xx=np.ogrid[:H,:W]
        detected=(r>175)&(g>108)&(g<.91*r)&(b>.42*g)&(b<.94*g)&(r-b>46)&(a>240)
        detected &= (yy>981) & ~((xx>440)&(xx<640)&(yy<1127))
        pose=file.stem.split('_')[1]
        if pose=='04':
            detected &= xx<365
        if pose in ('05','06'):
            detected &= xx>700
        if pose=='20':
            detected &= yy>1120
        # Aproxima apenas os componentes de uma mesma mão, como os dedos fechados.
        connected=cv2.dilate(detected.astype('uint8'),np.ones((15,15),np.uint8))
        n,_,stats,_=cv2.connectedComponentsWithStats(connected,8)
        amount=1 if pose in ('04','05','06') else 2
        top=sorted(range(1,n),key=lambda k:-stats[k,4])[:amount]
        top=sorted([k for k in top if stats[k,4]>400],key=lambda k:stats[k,0])
        assert 1<=len(top)<=2, file
        gutter=22
        panel_width=(504-gutter*(len(top)-1))//len(top)
        x,y=i%3*540,i//3*360
        for j,k in enumerate(top):
            l,t,w,h,_=map(int,stats[k])
            crop=image.crop((max(0,l-12),max(0,t-12),min(W,l+w+12),min(H,t+h+12)))
            factor=min(panel_width/crop.width,296/crop.height)
            crop=crop.resize((round(crop.width*factor),round(crop.height*factor)),Image.Resampling.LANCZOS)
            at=x+18+j*(panel_width+gutter)+(panel_width-crop.width)//2
            sheet.paste(crop,(at,y+12+(296-crop.height)//2),crop)
        draw.text((x+18,y+325),file.stem.removeprefix('Corpo_').replace('_',' '),fill='white')
    sheet.save(OUT/'Detalhes_das_maos.jpg',quality=95)


def package():
    paths=[*sorted(KIT.glob('*.png')),*sorted(FLAT.glob('*.png')),OUT/'Prancha_9_Poses.jpg',OUT/'Detalhes_das_maos.jpg']
    assert len(paths)==22
    for p in paths:
        im=Image.open(p)
        if p.suffix=='.png':
            assert im.mode=='RGBA' and im.size==(W,H)
        im.verify()
    result=OUT/'Massacote_2D_5_Dedos_Rev2.zip'
    with zipfile.ZipFile(result,'w',zipfile.ZIP_DEFLATED,compresslevel=4) as z:
        for p in paths:
            z.write(p,p.relative_to(OUT).as_posix())
    with zipfile.ZipFile(result) as z:
        assert z.testzip() is None and all(z.read(p.relative_to(OUT).as_posix())==p.read_bytes() for p in paths)
    print(result,checksum(result),flush=True)


if __name__=='__main__':
    assemble()
    hand_sheet()
    package()
