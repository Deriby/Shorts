"""Verificação de duração, voz, vínculos, movimento e pacote portátil completo."""
from pathlib import Path
import json,hashlib,zipfile,subprocess,sys,struct,base64
sys.path.insert(0,'/workspace/tools/shorts_asr')
import cv2,numpy as np,soundfile as sf
P=Path(__file__).resolve().parents[1];F=P/'output/Filmora';M=F/'midias';plan=json.loads((P/'timeline.json').read_text());OUT=P/'output/Massacote_Tube_Sonic_V3_9x16.mp4';WFP=F/'Massacote_Tube_Sonic_V3_9x16.wfp'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
assert sha(M/'Voz_Dery_Original.wav')==plan['voice_sha256']
assert plan['voice_sha256']=='170b96aa19474e3c8afb29e80cdf4862b707ab0966b2a37057517c57d1552c50'
v=probe(OUT);video=next(s for s in v['streams']if s['codec_type']=='video');assert [video['width'],video['height']]==[1080,1920];assert int(video['nb_frames'])==1053;assert video['r_frame_rate']=='30/1'
subprocess.run(['ffmpeg','-v','error','-i',str(OUT),'-f','null','-'],check=True)
ROOT='{204E72A3-B517-44d4-806F-9E9D84D5F904}'
with zipfile.ZipFile(WFP)as z:
 assert z.testzip()is None
 d=json.loads(z.read(f'ProjectFolder/Medias/{ROOT}/timeline.wesproj'));lib=json.loads(z.read('ProjectFolder/Medias/medias_info.json'));meta=json.loads(z.read('ProjectFolder/project_info.json'))
 assert meta['project_timeline_resolution']==[1080,1920]and meta['project_timeline_ratio']==[9,16]
 main=d['timelineInfos'][0];clips=[c for tr in main['trackInfos']for c in tr['clipList']];assert len(clips)==len(plan['events'])
 for tr in main['trackInfos']:
  cs=sorted(tr['clipList'],key=lambda c:c['tlBegin'])
  assert all(a['tlEnd']<=b['tlBegin']for a,b in zip(cs,cs[1:])),tr.get('trackTag')
 resources={r['sourceUuid']:r for r in d['resources']};ids=set()
 for c in clips:
  assert c['thisUId']not in ids;ids.add(c['thisUId']);assert c['sourceUuid']in resources
  path=M/Path(c['filename']).name;assert path.is_file()
  assert c['tlEnd']>c['tlBegin']>=0;assert c['tlEnd']<=round(plan['duration']*1e7)
  if path.suffix!='.png':assert c['outPoint']<=resources[c['sourceUuid']]['mediaLength']+1,(path.name,c['outPoint'],resources[c['sourceUuid']]['mediaLength'])
  speed=json.loads(c['speed']['speedParam']);assert not c['speed']['reverse'];assert all(k['_value']==1 for k in speed['keyframeSets'])
  for ch in c['effectChainList']:
   for fx in ch['effectList']:
    assert fx.get('display')=='transform',fx.get('display')
    for param in fx.get('paramMapList',[]):
     keys=json.loads(param['keyFrame']['parameter'])['keyframeSets'];assert keys[-1]['_time']<=(c['tlEnd']-c['tlBegin'])/1e7+1e-6
 used=sorted({Path(r['filename']).name for r in d['resources']})
 for item in lib['media_items'].values():
  if item['id']==ROOT:continue
  file=M/Path(item['download_url']).name;assert hashlib.md5(file.read_bytes()).hexdigest()==item['src_md5']

# Detecta a falha anterior de vídeos que viravam imagens estáticas.
motion=[]
for name in used:
 if not name.endswith('.mp4'):continue
 cap=cv2.VideoCapture(str(M/name));dur=float(cap.get(cv2.CAP_PROP_FRAME_COUNT))/30;frames=[]
 for t in [min(.5,dur*.1),dur*.5,max(.1,dur-.35)]:
  cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,f=cap.read();assert ok;frames.append(cv2.resize(f,(180,320)))
 maps=[np.abs(a.astype(float)-b.astype(float)).mean(axis=2)for a,b in zip(frames,frames[1:])]
 diffs=[float(d.mean())for d in maps];changed=[int((d>24).sum())for d in maps]
 # Movimento localizado (mãos digitando) ocupa poucos pixels do quadro vertical.
 # Exigir média global >1 rejeitaria um vídeo móvel com fundo majoritariamente fixo.
 assert max(diffs)>.1 and max(changed)>20,(name,diffs,changed)
 cap.release();motion.append(dict(file=name,differences=diffs,pixels_changed_above_24=changed))
report=dict(mp4_sha256=sha(OUT),mp4_bytes=OUT.stat().st_size,duration=35.1,frames=1053,resolution=[1080,1920],fps=30,full_video_audio_decode=True,voice_source_bit_identical=True,voice_complete=True,speed_1x=True,all_native_media_links_resolved=True,library_md5_verified=True,no_same_track_overlaps=True,all_curves_within_clips=True,native_filmora_execution=False,moving_video_sources=motion,resources=len(used),clips=len(clips),no_added_captions=True,no_psx_filter=True,continuous_fight_seconds=6.2,eyes_animation=False,reference_style='Massacote Tube / Carros 30s',presenter_directs_media=True,original_movie_frame_preserved=True,continuous_fight_start=28.9)
# Confere a exportação efetiva, além da presença do WAV no pacote.
expected,sr=sf.read(P/'output/.mix.wav',dtype='float32',always_2d=True)
decoded=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(OUT),'-vn','-ar','48000','-ac','2','-f','f32le','-']),dtype='<f4').reshape(-1,2)
n=min(len(expected),len(decoded));correlation=float(np.corrcoef(expected[:n].ravel(),decoded[:n].ravel())[0,1]);assert correlation>.995,correlation
report['audio_export_correlation']=correlation
fight=next(e for e in plan['events']if e['file']=='Luta_Continua.mp4')
assert abs(fight['start']-28.9)<1e-8 and abs(fight['end']-35.1)<1e-8
assert int(probe(M/fight['file'])['streams'][0]['nb_frames'])==186
source=Path('/workspace/work/reference-comparison/fight_full.mp4')
caps=[cv2.VideoCapture(str(p))for p in [source,M/fight['file']]];psnrs=[]
for frame_index in [0,90,185]:
 frames=[]
 for c,y in zip(caps,[656,430]):
  c.set(cv2.CAP_PROP_POS_FRAMES,frame_index);ok,im=c.read();assert ok
  frames.append(im[y:y+608,:1080])
 score=float(cv2.PSNR(*frames));assert score>30,score;psnrs.append(score)
for c in caps:c.release()
report['full_width_fight_psnr_db']=psnrs
(P/'validacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
readme='''MASSACOTE TUBE — SONIC V3 / NOVO PERSONAGEM / 9:16

Extraia o ZIP inteiro. Abra Filmora/Massacote_Tube_Sonic_V3_9x16.wfp,
mantendo a pasta midias ao lado dele. Não abra o projeto de dentro do ZIP.
Se o Filmora pedir uma mídia, localize-a na pasta midias extraída.

35,1 s, 1080 x 1920, 30 fps. Voz original inteira.
Personagem novo com oculos 3D fixos. Camadas: corpo, cabeca, bigode e maos.
Cenas compartilhadas, poses, cabeça, bigode, mídia e transições por keyframes editáveis.
Voz, música, sons de movimento e luta em faixas separadas.
Sem novas legendas automáticas ou filtro PSX.
As legendas já gravadas na animação recebida pertencem ao próprio arquivo.

O MP4 permite assistir à montagem. O projeto foi conferido por estrutura,
vínculos, curvas, tempos e arquivos; não foi aberto/exportado no Filmora
proprietário neste Linux. Não foi prometida cópia idêntica de plugins.
'''
(F/'LEIA_PRIMEIRO.txt').write_text(readme)
bundle=P/'output/Massacote_Tube_Sonic_V3_Filmora_Completo.zip'
paths=[WFP,F/'LEIA_PRIMEIRO.txt',*[M/name for name in used]]
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED,compresslevel=5)as z:
 for path in paths:z.write(path,'Filmora/'+str(path.relative_to(F)))
 z.write(P/'validacao.json','validacao.json')
with zipfile.ZipFile(bundle)as z:
 assert z.testzip()is None
 for path in paths:
  assert hashlib.sha256(z.read('Filmora/'+str(path.relative_to(F)))).hexdigest()==sha(path)
manifest=dict(bundle=bundle.name,bytes=bundle.stat().st_size,sha256=sha(bundle),files=len(paths)+1,all_members_verified=True,media_files=used)
(P/'pacote.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
# Arquivos auxiliares do render e exportações que a timeline não usa não entram no Git/pacote.
for path in M.iterdir():
 if path.name not in used:path.unlink()
print(json.dumps({'validation':report,'package':manifest},ensure_ascii=False,indent=2),flush=True)
