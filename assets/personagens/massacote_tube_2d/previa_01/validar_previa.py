from pathlib import Path
import json,subprocess,hashlib,wave
import cv2,numpy as np
P=Path(__file__).resolve().parent;M=P/'Filmora/midias'
cap=cv2.VideoCapture(str(P/'Previa_Conversando_2D.mp4'));count=0;delta=[];prev=None
while True:
    ok,im=cap.read()
    if not ok:break
    assert im.shape==(720,1280,3)
    if prev is not None:delta.append(float(np.abs(im.astype(float)-prev.astype(float)).mean()))
    prev=im;count+=1
cap.release();assert count==279 and max(delta)>.2
with wave.open(str(M/'voz_teste.wav')) as f:voice=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(float)/32768;sr=f.getframerate()
decoded=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(P/'Previa_Conversando_2D.mp4'),'-vn','-ac','1','-ar',str(sr),'-f','f32le','pipe:1']),dtype='<f4');n=min(len(voice),len(decoded));corr=float(np.corrcoef(voice[:n],decoded[:n])[0,1]);assert corr>.99
catalog=json.loads((P.parent/'lote_01/catalogo.json').read_text())
for e in catalog['poses']:assert hashlib.sha256((P.parent/'lote_01'/e['file']).read_bytes()).hexdigest()==e['sha256']
report=dict(mp4_decoded_frames=count,duration_seconds=9.3,video_resolution=[1280,720],fps=30,audio_correlation_to_source_excerpt=corr,voice_samples=len(voice),source_excerpt=[0,9.3],new_voice_generated=False,approved_poses_unchanged=True,movement_detected=True,mean_interframe_difference=float(np.mean(delta)),max_interframe_difference=max(delta),filmora_native_executed=False,blender_used=False,visual_review='Quadros das duas poses conferidos; boca coberta pelo bigode, contornos de queixo/pescoco conferidos; aprovacao estetica do movimento pendente.')
(P/'validacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
rig=dict(status='preparado_para_previa_aguarda_avaliacao',editor='Filmora',resolution=[1920,1080],pivot='center canvas at neck',mouth_drawn_on_clean_underlay=False,poses={pose:{part:f'Filmora/midias/{pose}_{part}.png'for part in ['corpo','cabeca','bigode']}for pose in ['conversando','apontando']})
(P/'rig_camadas.json').write_text(json.dumps(rig,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
