"""Compara camadas nos keyframes reais do WFP do usuário; não simula plugins."""
from pathlib import Path
import json,zipfile,math,subprocess
import cv2,numpy as np
P=Path(__file__).resolve().parents[1]
SRC=P.parent/'revisao_v3_cenas/output/Filmora/midias';FIX=P/'output/Filmora/midias_regeneradas'
WFP=P.parent/'edicao_usuario_01/recebido/Massacote_Tube_Sonic_EDITADO_USUARIO.wfp'
with zipfile.ZipFile(WFP)as z:
    d=json.loads(z.read('ProjectFolder/Medias/{204E72A3-B517-44d4-806F-9E9D84D5F904}/timeline.wesproj'))
main=next(t for t in d['timelineInfos']if t['timelineId']==d['currentTimelineId'])
events=[]
for track in main['trackInfos']:
    if track['trackType']!=1:continue
    for c in track['clipList']:
        name=Path(c.get('filename')or'').name
        if name in ['Cabeca.png','Bigode.png']or name.startswith(('Corpo_','Frente_')):
            fx=next(e for ch in c['effectChainList']for e in ch['effectList']if e.get('display')=='transform')
            values={p['name']:p['fxParam']['unValue']for p in fx.get('paramList',[])};curves={}
            for p in fx.get('paramMapList',[]):
                if 'keyFrame'in p:
                    ks=json.loads(p['keyFrame']['parameter'])['keyframeSets'];curves[p['name']]=([k['_time']for k in ks],[k['_value']for k in ks])
            events.append((c['tlBegin']/1e7,c['tlEnd']/1e7,name,values,curves))
images={}
for _,_,name,_,_ in events:
    for variant,folder in [('before',SRC),('after',FIX)]:
        path=folder/(Path(name).stem+'_R3.png')if variant=='after'else folder/name
        if not path.exists():path=SRC/name
        if(variant,name)not in images:
            images[variant,name]=cv2.resize(cv2.imread(str(path),cv2.IMREAD_UNCHANGED),(540,960),interpolation=cv2.INTER_AREA)
cv2.setNumThreads(1)
def frame(t,variant):
    canvas=np.full((960,540,3),(154,91,38),np.uint8)
    for start,end,name,vals,curves in events:
        if not start<=t<end:continue
        def val(k,default):
            if k in curves:return float(np.interp(t-start,*curves[k]))
            return vals.get(k,default)
        x,y=val('Position_x',.5)*540,val('Position_y',.5)*960
        sx,sy=val('Scale_x',100)/100,val('Scale_y',100)/100;rad=math.radians(val('Rotation',0))
        m=np.array([[math.cos(rad)*sx,-math.sin(rad)*sy],[math.sin(rad)*sx,math.cos(rad)*sy]])
        aff=np.column_stack((m,np.array([x,y])-m@np.array([270,480]))).astype('float32')
        layer=cv2.warpAffine(images[variant,name],aff,(540,960),flags=cv2.INTER_LINEAR)
        alpha=layer[:,:,3:4].astype(float)/255;canvas=(layer[:,:,:3]*alpha+canvas*(1-alpha)).astype('uint8')
    return canvas

samples=[3.9,6.4,15.3,18.7,21.5,23.0,24.7,26.4,28.2]
sheet=np.zeros((3*344,6*180,3),np.uint8)
for i,t in enumerate(samples):
    for j,variant in enumerate(['before','after']):
        im=cv2.resize(frame(t,variant),(180,320));x=(i%3*2+j)*180;y=i//3*344
        sheet[y+24:y+344,x:x+180]=im
        cv2.putText(sheet,f'{t:.1f}s '+('ANTES'if j==0 else'NOVAS'),(x+4,y+17),cv2.FONT_HERSHEY_SIMPLEX,.38,(255,255,255),1,cv2.LINE_AA)
cv2.imwrite(str(P/'analise/Conferencia_Poses.jpg'),sheet)

out=P/'analise/Previa_Pecas_Regeneradas.mp4'
proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s','1080x990','-r','30','-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],stdin=subprocess.PIPE)
for i in range(93):
    t=20.9+i/30;pair=np.concatenate([frame(t,'before'),frame(t,'after')],axis=1)
    top=np.zeros((30,1080,3),np.uint8)
    for x,caption in [(12,'ANTES'),(552,'PECAS REGENERADAS')]:cv2.putText(top,caption,(x,22),cv2.FONT_HERSHEY_SIMPLEX,.62,(255,255,255),1,cv2.LINE_AA)
    proc.stdin.write(np.concatenate([top,pair],axis=0).tobytes())
proc.stdin.close();assert proc.wait()==0
report=json.loads((P/'validacao_pecas.json').read_text());report.update(motion_checked=True,motion_source='Keyframes do WFP editado pelo usuario',motion_interval_seconds=[20.9,24.0],pose_checks_seconds=samples,native_effects_simulated=False)
(P/'validacao_pecas.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('Conferidos nove instantes e 93 quadros com os keyframes do usuario.',flush=True)
