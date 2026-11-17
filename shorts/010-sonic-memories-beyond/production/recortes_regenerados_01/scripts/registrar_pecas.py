from pathlib import Path
from PIL import Image,ImageFilter
import cv2,numpy as np,json
P=Path(__file__).resolve().parents[1];O=P/'output/Filmora/midias_regeneradas';O.mkdir(parents=True,exist_ok=True)
FILES={k:k+'.png'for k in ['head','moustache','body_a','body_b','body_c']}
def read(key,count=1):
 a=np.array(Image.open(P/'fontes'/FILES[key]).convert('RGBA'))
 n,l,st,ct=cv2.connectedComponentsWithStats((a[:,:,3]>=245).astype('uint8'),8)
 ids=sorted(range(1,n),key=lambda i:st[i,4],reverse=True)[:count]
 ids=sorted(ids,key=lambda i:ct[i,0]);result=[]
 for i in ids:
  x,y,w,h,area=st[i];assert area>10000
  mask=(l==i).astype('uint8')*255
  # Antialias only the already generated silhouette; no head/body masking.
  smooth=cv2.GaussianBlur(mask,(3,3),.45);b=a.copy();b[:,:,3]=smooth
  result.append(b[y:y+h,x:x+w].copy())
 return result

def render(a,M):return cv2.warpAffine(a,np.asarray(M,np.float32),(1080,1920),flags=cv2.INTER_LANCZOS4,borderMode=cv2.BORDER_CONSTANT)
def save(a,name):Image.fromarray(a).save(O/(Path(name).stem+'_R3.png'))
head=read('head')[0];r,g,b,al=[head[:,:,i]for i in range(4)]
centers=[]
for mask in [(r>180)&(g<100)&(b<100)&(al>240),(b>170)&(r<100)&(g<190)&(al>240)]:
 n,l,st,c=cv2.connectedComponentsWithStats(mask.astype('uint8'),8);ids=[i for i in range(1,n)if st[i,4]>300 and head.shape[0]*.3<c[i,1]<head.shape[0]*.85];i=max(ids,key=lambda i:st[i,4]);centers.append(c[i])
source=np.asarray(centers);target=np.asarray([[466.173,843.401],[629.158,839.344]])
z=complex(*(target[1]-target[0]))/complex(*(source[1]-source[0]));A=np.asarray([[z.real,-z.imag],[z.imag,z.real]]);off=target[0]-A@source[0];h=render(head,np.column_stack([A,off]));save(h,'Cabeca.png')
y,x=np.where(h[:,:,3]>240);headbottom=int(y[(x>510)&(x<570)].max());necktop=headbottom-135
big=read('moustache')[0];bw=350;bh=big.shape[0]*bw/big.shape[1];s=bw/big.shape[1];bm=[[s,0,539.5-bw/2],[0,s,950.9-bh/2]];save(render(big,bm),'Bigode.png')
pose_ids={'body_a':['04_apontando_esquerda','05_apontando_direita','06_apontando_cima'],'body_b':['09_joinha','12_deu_de_ombros','15_fazendo_ressalva'],'body_c':['16_desespero','20_tramando','24_apresentando_lado']}
reg={'head_lenses_source':source.tolist(),'head_lenses_target':target.tolist(),'head_bottom':headbottom,'neck_top':necktop,'poses':[]}
for key,names in pose_ids.items():
 for a,name in zip(read(key,3),names):
  H,W=a.shape[:2];r,g,b,al=[a[:,:,i].astype(float)for i in range(4)]
  mask=((r>150)&(g>75)&(g<r*.88)&(b<g*.93)&(al>240)).astype('uint8')
  n,l,st,c=cv2.connectedComponentsWithStats(mask,8)
  ids=[i for i in range(1,n)if abs(c[i,0]-W/2)<W*.22 and st[i,4]>200]
  i=min(ids,key=lambda i:st[i,1]);xx,yy,ww,hh,area=st[i]
  # Plain neck is the topmost central skin region, never a face.
  neckcx=c[i,0];source_top=yy
  scale=(1555-necktop)/(H-source_top);scale=min(scale,1030/W)
  mat=[[scale,0,539.5-scale*neckcx],[0,scale,necktop-scale*source_top]]
  out=render(a,mat);save(out,'Corpo_'+name+'.png')
  reg['poses'].append(dict(id=name,neck_skin_bbox=[int(xx),int(yy),int(ww),int(hh)],scale=scale,matrix=mat))
for name in ['Frente_12_deu_de_ombros.png','Frente_15_fazendo_ressalva.png','Frente_16_desespero.png','Frente_20_tramando.png']:save(np.zeros((1920,1080,4),np.uint8),name)
(P/'registro_encaixe.json').write_text(json.dumps(reg,indent=2))
frame=Image.new('RGBA',(1080,1920),'#265b9a')
for name in ['Corpo_09_joinha.png','Cabeca.png','Bigode.png']:frame.alpha_composite(Image.open(O/(Path(name).stem+'_R3.png')))
frame.crop((170,400,920,1630)).resize((600,984)).convert('RGB').save(P/'analise/Previa_Regenerada.jpg')
print('REGISTRO',headbottom,necktop,'15 PNGs')
