"""Prepara substituições de camadas sem modificar o WFP editado pelo usuário.

A arte aprovada é preservada: corpo perde componentes soltos, o pescoço recebe
sobreposição das peças existentes e os traços de rosto ficam na cabeça, separados
do bigode. Um estudo image_gen foi consultado para o contorno do bigode; suas cores,
halo e novo desenho não entram nas mídias finais. Pixels vêm dos PNGs originais.
"""
from pathlib import Path
import hashlib,json,zipfile
from PIL import Image,ImageDraw,ImageFont
import numpy as np,cv2

P=Path(__file__).resolve().parents[1]
SRC=P.parent/'revisao_v3_cenas/output/Filmora/midias'
OUT=P/'output';M=OUT/'midias';M.mkdir(parents=True,exist_ok=True)
PROJECT=P.parent/'edicao_usuario_01/recebido/Massacote_Tube_Sonic_EDITADO_USUARIO.wfp'
EXPECTED='bf145baeebb2087f05023716b7d9f5b351a4fcbda949715a1f000061e427d9c3'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(PROJECT)==EXPECTED
with zipfile.ZipFile(PROJECT)as z:
    assert z.testzip() is None
    root=next(n for n in z.namelist()if n.endswith('timeline.wesproj')and'{204E72A3-B517-44d4-806F-9E9D84D5F904}'in n)
    data=json.loads(z.read(root))
used={Path(r.get('filename','')).name for r in data['resources']}
body_names=sorted(n for n in used if n.startswith('Corpo_')and n.endswith('.png'))

oldhead=np.array(Image.open(SRC/'Cabeca.png').convert('RGBA'));head=oldhead.copy()
region=Image.new('L',(1080,1920),0)
# Região de união com o pescoço, preservando boné, cabelo, rosto e cavanhaque.
points=[(0,0),(1080,0),(1080,982),(680,982),(650,990),(610,1000),
        (600,1040),(590,1080),(570,1106),(560,1115),(510,1115),
        (495,1100),(480,1070),(470,1035),(460,1000),(420,990),(380,982),(0,982)]
ImageDraw.Draw(region).polygon(points,fill=255)
head[:,:,3]=np.minimum(head[:,:,3],np.array(region))
removed=(oldhead[:,:,3].astype(int)>head[:,:,3].astype(int)+1).astype('uint8')
removed=cv2.dilate(removed,np.ones((9,9),np.uint8));removed[:982]=0;removed[1116:]=0

records=[]
for name in body_names:
    before=np.array(Image.open(SRC/name).convert('RGBA'));a=before.copy()
    n,labels,stats,centers=cv2.connectedComponentsWithStats((a[:,:,3]>4).astype('uint8'),8)
    main=1+int(np.argmax(stats[1:,4]));keep=(labels==main).astype('uint8')
    keep=cv2.dilate(keep,np.ones((3,3),np.uint8));a[:,:,3]*=keep
    # Preserva as mãos conectadas ao corpo; as mãos de frente são outras mídias.
    contours,_=cv2.findContours((a[:,:,3]>4).astype('uint8'),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    hull=cv2.convexHull(max(contours,key=cv2.contourArea));hm=np.zeros(a.shape[:2],np.uint8)
    cv2.fillConvexPoly(hm,hull,1)
    # Transfere as partes de gola antes presas à cabeça, dentro da silhueta do corpo.
    # Isso fecha a união e impede que sobras de gola acompanhem a rotação do rosto.
    patch=oldhead.copy();patch[:,:,3]=patch[:,:,3]*hm*removed
    out=Image.fromarray(patch);out.alpha_composite(Image.fromarray(a));out.save(M/name)
    after=np.array(out)
    assert np.array_equal(before[:,:,:3][before[:,:,3]>4],a[:,:,:3][before[:,:,3]>4])
    records.append(dict(file=name,before_sha256=sha(SRC/name),after_sha256=sha(M/name),
        removed_floating_pixels=int(((before[:,:,3]>4)&(after[:,:,3]<=4)).sum()),
        neck_underlap_pixels=int(((before[:,:,3]<=4)&(after[:,:,3]>4)).sum()),
        dimensions=[1080,1920],body_color_preserved=True))

old=np.array(Image.open(SRC/'Bigode.png').convert('RGBA'));r,g,b=[old[:,:,i].astype(float)for i in range(3)]
brown=((r>36)&(r>g*1.32)&(g<125)&(b<115)&(old[:,:,3]>100)).astype('uint8')
n,labels,stats,centers=cv2.connectedComponentsWithStats(brown,8)
brown=np.isin(labels,[i for i in range(1,n)if stats[i,4]>500]).astype('uint8')
distance=cv2.distanceTransform(1-brown,cv2.DIST_L2,5)
weight=np.clip((6.2-distance)/.8,0,1)
weight[(r>185)&(g>125)&(b>70)&(distance>1.3)]=0
mustache=old.copy();mustache[:,:,3]=np.rint(old[:,:,3]*weight).astype('uint8')
assert np.array_equal(mustache[:,:,:3],old[:,:,:3])
assert np.all(mustache[:,:,3]<=old[:,:,3])
Image.fromarray(mustache).save(M/'Bigode.png')

# Traços da bochecha/queixo não devem vibrar com o bigode: voltam à cabeça,
# limitados à área já opaca da face. Não há nova pintura nem nova boca.
extra=old.copy()
extra[:,:,3]=np.minimum(np.maximum(0,old[:,:,3].astype(int)-mustache[:,:,3].astype(int)),head[:,:,3]).astype('uint8')
headimage=Image.fromarray(head);headimage.alpha_composite(Image.fromarray(extra));headimage.save(M/'Cabeca.png')
for name in ['Cabeca.png','Bigode.png']:
    records.append(dict(file=name,before_sha256=sha(SRC/name),after_sha256=sha(M/name),dimensions=[1080,1920]))

# Comprova que olhos, cabelo e boné não mudaram.
fixed=np.array(headimage)
assert np.array_equal(fixed[:885],oldhead[:885])
assert sha(PROJECT)==EXPECTED
report=dict(source_project_sha256=EXPECTED,source_project_byte_identical=True,
    original_project_unmodified=True,canvas_preserved=[1080,1920],
    eyes_hair_cap_pixels_unchanged=True,mustache_rgb_unchanged=True,
    no_new_art_in_final_assets=True,native_filmora_executed=False,
    current_user_edit_duration_seconds=48.9333333,
    replaces_only_referenced_pngs=True,files=records)
(P/'validacao_recortes.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')

# Prancha técnica em fundo contrastante; não simula os plugins da edição do usuário.
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',23)
sheet=Image.new('RGB',(1220,790),'#203955');draw=ImageDraw.Draw(sheet)
for i,(label,folder)in enumerate([('ANTES',SRC),('RECORTES CORRIGIDOS',M)]):
    frame=Image.new('RGBA',(1080,1920),'#265b9a')
    for name in ['Corpo_09_joinha.png','Cabeca.png','Bigode.png']:
        frame.alpha_composite(Image.open(folder/name).convert('RGBA'))
    frame=frame.crop((240,455,850,1180)).convert('RGB')
    sheet.paste(frame,(i*610,50));draw.text((i*610+18,12),label,font=font,fill='white')
sheet.save(P/'analise/Comparativo_Recortes.jpg',quality=94)

readme='''ATUALIZACAO DOS RECORTES — SONIC / EDICAO DO USUARIO

Este ZIP tem somente PNGs corrigidos. Nao e um projeto completo.
Feche o Filmora e guarde uma copia da pasta midias atual.
Copie os PNGs da pasta midias deste ZIP para a pasta midias que seu WFP ja usa,
substituindo somente esses mesmos nomes. Reabra o seu WFP reeditado.
As demais midias continuam na pasta original. Nenhum WFP e sobrescrito.

Corrigidos: fragmentos acima do bone nas camadas do corpo, sobras de gola
na cabeca, encaixe do pescoco e isolamento do bigode. As cores e desenhos
vem das pecas originais, com canvas 1080x1920 e alinhamento preservados.
Bochecha/queixo ficam na cabeca; somente o bigode acompanha a fala.
Olhos, cabelo e bone permanecem identicos aos originais.

Sua edicao (cortes, duracao, som, bordas, fundos e efeitos nativos) fica intacta.
O WFP recebido foi preservado com hash em recebido/, no repositorio.
Os recortes foram conferidos por sobreposicao e em movimento; os plugins
proprietarios nao foram renderizados neste Linux.
'''
(OUT/'LEIA_PRIMEIRO.txt').write_text(readme)
bundle=OUT/'Atualizacao_Recortes_Sonic.zip'
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
    z.write(OUT/'LEIA_PRIMEIRO.txt','LEIA_PRIMEIRO.txt')
    for name in sorted(p.name for p in M.glob('*.png')):z.write(M/name,'midias/'+name)
    z.write(P/'validacao_recortes.json','validacao_recortes.json')
with zipfile.ZipFile(bundle)as z:
    assert z.testzip()is None
    for name in sorted(p.name for p in M.glob('*.png')):
        assert hashlib.sha256(z.read('midias/'+name)).hexdigest()==sha(M/name)
(P/'pacote.json').write_text(json.dumps(dict(file=bundle.name,bytes=bundle.stat().st_size,
    sha256=sha(bundle),png_count=len(records),zip_all_members_verified=True,
    source_project_unmodified=True),ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'package':bundle.name,'bytes':bundle.stat().st_size,'pngs':len(records),'project_unchanged':True},ensure_ascii=False),flush=True)
