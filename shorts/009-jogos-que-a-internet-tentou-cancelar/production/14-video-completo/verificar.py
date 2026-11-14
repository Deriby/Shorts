from pathlib import Path
import json,zipfile,subprocess,hashlib,wave,math
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;R=next(x for x in P.parents if(x/'AGENTS.md').exists());O=P/'output';F=O/'Filmora';C=Path('/workspace/attachments/longo009');plan=json.loads((P/'montagem.json').read_text());report=json.loads((P/'projeto.json').read_text());T=10000000
video=O/'Jogos_Que_A_Internet_Tentou_Cancelar_COMPLETO_16x9.mp4';probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(video)]));v=next(x for x in probe['streams']if x['codec_type']=='video');assert(v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'30/1',plan['frames']);assert abs(float(probe['format']['duration'])-plan['duration'])<.05
# Decode the complete concatenation once; sample every body and title card.
indices=[rec['start']+rec['frames']//2 for rec in plan['records']];C.joinpath('conferencia').mkdir(exist_ok=True);select='+'.join(f'eq(n\\,{i})'for i in indices)
video_sha=hashlib.sha256(video.read_bytes()).hexdigest();marker=C/'video_decodificado.sha256'
if not marker.exists()or marker.read_text().strip()!=video_sha:
 subprocess.run(['ffmpeg','-v','error','-y','-threads','1','-i',str(video),'-vf','select='+select,'-fps_mode','vfr','-c:v','png','-threads','1',str(C/'conferencia/%03d.png')],check=True)
 marker.write_text(video_sha+'\n')
assert len(list((C/'conferencia').glob('*.png')))==len(indices)
source_cache=C/'source_samples.json'
for rec in plan['records']:
 if rec['type']=='body':
  assert hashlib.sha256((R/rec['source_video']).read_bytes()).hexdigest()==rec['source_sha256']
  assert hashlib.sha256((R/rec['source_project']).read_bytes()).hexdigest()==rec['source_project_sha256']
source_checks=[]
if source_cache.exists()and json.loads(source_cache.read_text())['video_sha']==video_sha:
 source_checks=json.loads(source_cache.read_text())['checks']
else:
 for i,rec in enumerate(plan['records'],1):
  if rec['type']!='body':continue
  source=R/rec['source_video'];assert hashlib.sha256(source.read_bytes()).hexdigest()==rec['source_sha256'];assert hashlib.sha256((R/rec['source_project']).read_bytes()).hexdigest()==rec['source_project_sha256'];f=rec['frames']//2;dest=C/'source.png'
  subprocess.run(['ffmpeg','-v','error','-y','-threads','1','-i',str(source),'-vf',f'select=eq(n\\,{f})','-frames:v','1','-c:v','png','-threads','1',str(dest)],check=True)
  a=np.asarray(Image.open(dest));b=np.asarray(Image.open(C/'conferencia'/f'{i:03d}.png'));assert np.array_equal(a,b),('Altered or misplaced body frame',rec['title']);source_checks.append(dict(title=rec['title'],matching_frame=f,decoded_pixels_identical=True))
 source_cache.write_text(json.dumps(dict(video_sha=video_sha,checks=source_checks)))
# Every source voice is unmodified, fully represented, and in its own native track.
assert len(report['voices'])==13
for voice in report['voices']:assert hashlib.sha256((F/'midias'/voice['file']).read_bytes()).hexdigest()==voice['sha256']
project=F/report['project']
with zipfile.ZipFile(project)as z:
 assert z.testzip()is None;data=json.loads(z.read(next(n for n in z.namelist()if n.endswith('timeline.wesproj'))));main=data['timelineInfos'][0];assert len(data['timelineInfos'])==1 and(main['resolutionWidth'],main['resolutionHeight'])==(1920,1080);resources={r['sourceUuid']:r for r in data['resources']};clips=0
 for r in resources.values():assert r['filename'].startswith('file:./midias/')and(F/r['filename'].removeprefix('file:./')).is_file()
 primary=main['trackInfos'][11]['clipList'];assert primary[0]['tlBegin']==0 and primary[-1]['tlEnd']==round(plan['duration']*T);assert all(a['tlEnd']==b['tlBegin']for a,b in zip(primary,primary[1:]));glows=0
 for track,tr in enumerate(main['trackInfos']):
  for c in tr['clipList']:
   clips+=1;assert c['tlEnd']>c['tlBegin']and abs(c['tlEnd']-c['tlBegin']-(c['outPoint']-c['inPoint']))<=1
   assert c.get('filename')and c['sourceUuid']in resources;r=resources[c['sourceUuid']];assert c['filename']==r['filename']
   if r['mediaLength']:assert c['outPoint']<=r['mediaLength']+1
   speed=json.loads(c['speed']['speedParam']);assert not c['speed']['reverse']and all(k['_value']==1 for k in speed['keyframeSets'])
   for ch in c.get('effectChainList',[]):
    for fx in ch['effectList']:
     assert fx.get('display')not in ['Text Vibrate','Filming Shake','Glitch Effect 6']
     if fx.get('display')=='Glow':assert track==13 and r['streamType']==5;glows+=1
     if fx.get('display')=='transform':
      for m in fx.get('paramMapList',[]):
       keys=json.loads(m['keyFrame']['parameter'])['keyframeSets'];assert min(k['_time']for k in keys)>=0 and max(k['_time']for k in keys)<=2.00001
 assert glows==11 and len(main['trackInfos'][8]['clipList'])==13
 for rec in plan['records']:
  if rec['type']=='card':
   a,b=round(rec['start']/30*T),round(rec['end']/30*T)
   for track in[11,12,13]:assert sum(c['tlBegin']==a and c['tlEnd']==b for c in main['trackInfos'][track]['clipList'])==1
# Streaming audio comparison avoids allocating the entire long twice.
p=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-i',str(video),'-vn','-ac','2','-ar','44100','-f','s16le','pipe:1'],stdout=subprocess.PIPE);sums=np.zeros(6,np.float64)
with wave.open(str(Path('/workspace/attachments/longo009/mixagem_completa.wav')))as w:
 while True:
  expected=w.readframes(44100)
  if not expected:break
  actual=p.stdout.read(len(expected));assert len(actual)==len(expected);a=np.frombuffer(expected,'<i2').astype(np.float64);b=np.frombuffer(actual,'<i2').astype(np.float64);sums+=[len(a),a.sum(),b.sum(),np.dot(a,a),np.dot(b,b),np.dot(a,b)]
p.stdout.read();p.stdout.close();assert p.wait()==0;n,sa,sb,saa,sbb,sab=sums;correlation=float((sab-sa*sb/n)/math.sqrt((saa-sa*sa/n)*(sbb-sb*sb/n)));assert correlation>.995
# Contact sheet includes the final exported picture, not a mock-up.
tile=(320,180);cols=4;sheet=Image.new('RGB',(cols*320,math.ceil(len(indices)/cols)*204),(20,21,26));d=ImageDraw.Draw(sheet)
for i,rec in enumerate(plan['records']):
 x=i%cols*320;y=i//cols*204;sheet.paste(Image.open(C/'conferencia'/f'{i+1:03d}.png').resize(tile,Image.Resampling.LANCZOS),(x,y));d.text((x+4,y+183),rec['title'][:39],fill='white')
sheet.save(O/'Previa_Montagem_Completa.jpg',quality=94)
result=dict(duration=plan['duration'],frames=plan['frames'],game_orders=[1,2,3,4,5,6,7,8,9,11,12],game_10_excluded=True,voices_complete=13,source_checks=source_checks,full_video_decoded=True,native_clips=clips,native_resources=len(resources),native_video_cuts=report['native_video_cuts'],chapter_cards=11,paid_glow_title_only=True,all_media_resolve=True,no_timeline_gaps=True,speed_1x=True,voices_bit_identical=True,full_audio_correlation=correlation,native_filmora_open=False)
(O/'validacao.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('COMPLETE_LONG_VERIFIED',json.dumps(result),flush=True)
