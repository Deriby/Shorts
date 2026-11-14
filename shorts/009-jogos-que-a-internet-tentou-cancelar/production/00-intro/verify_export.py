"""Check media motion/fidelity, full voice, duration and the portable native WFP."""
from pathlib import Path
from io import BytesIO
import json,subprocess,zipfile,hashlib,wave,math
import numpy as np
from PIL import Image,ImageOps,ImageDraw
P=Path(__file__).resolve().parent;O=P/'output';info=json.loads((P/'timeline.json').read_text());ed=json.loads((P/'edicao.json').read_text());C=Path(info['cache']);F=O/'Filmora';N=info['frames'];slug=info['slug']
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
def frame(p,t):return Image.open(BytesIO(subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(t),'-i',str(p),'-frames:v','1','-c:v','png','-threads','1','-f','image2pipe','pipe:1']))).convert('RGB')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mse(a,b):return float(np.mean((np.asarray(a,np.float32)-np.asarray(b,np.float32))**2))
receipt=json.loads((P/'recebimento.json').read_text())
for source in receipt['files']:assert sha(P/source['path'])==source['sha256']
with wave.open(str(P/'assets/voz/voz_completa.wav'))as w:voice=w.readframes(w.getnframes());voice_frames=w.getnframes();rate=w.getframerate()
with wave.open(str(P/'assets/voz/voz_timeline.wav'))as w:padded=w.readframes(w.getnframes());assert padded[:len(voice)]==voice and set(padded[len(voice):])<={0}
assert sha(F/'midias/voz_timeline.wav')==sha(P/'assets/voz/voz_timeline.wav')
tape=probe(P/info['monitor_file']);assert int(next(v for v in tape['streams']if v['codec_type']=='video')['nb_frames'])==N
files=[O/(slug+'_16x9.mp4'),F/'midias'/(slug+'_base_16x9.mp4')];videos=[]
for p,size in zip(files,[(1920,1080),(1920,1080)]):
 d=probe(p);v=next(s for s in d['streams']if s['codec_type']=='video');assert(v['width'],v['height'])==size;assert int(v['nb_frames'])==N and v['r_frame_rate']=='30/1';assert abs(float(d['format']['duration'])-N/30)<.035
 if p==files[1]:assert not any(s['codec_type']=='audio'for s in d['streams'])
 subprocess.run(['ffmpeg','-v','error','-threads','1','-i',str(p),'-f','null','-'],check=True);videos.append(dict(file=p.name,frames=N,sha256=sha(p)))
crt_motion={}
for sh in info['shots']:
 if sh['kind']=='monitor':
  start=(sh['start']-1)/30;images=[frame(files[1],start+t)for t in [.2,.6,1.1]];motion=[mse(a,b)for a,b in zip(images,images[1:])];assert max(motion)>.5;crt_motion[sh['mood']]=motion
# Exact first decoded frame through the same fps path as the composition.
clean_psnr={}
for sh in info['shots']:
 if sh['kind']!='game':continue
 assert sh['portrait_fit']=='contain';source=P/'assets/gameplay'/sh['source'];original=Image.open(BytesIO(subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(sh['source_start']),'-i',str(source),'-vf','fps=30','-frames:v','1','-c:v','png','-threads','1','-f','image2pipe','pipe:1']))).convert('RGB')
 expected=ImageOps.fit(original,(1920,1080),Image.Resampling.LANCZOS);error=mse(expected,frame(files[1],(sh['start']-1)/30));psnr=10*math.log10(255**2/max(error,1e-9));assert psnr>32,(sh['mood'],psnr);clean_psnr[sh['mood']]=psnr
# Landscape-only brand frame keeps the original logo and clean pixels.
for sh in info['shots']:
 if sh['kind']!='photo':continue
 original=Image.open(P/'assets/imagens'/sh['source']).convert('RGB');expected=Image.new('RGB',(1920,1080),(31,30,39));fit=ImageOps.contain(original,(1920,1080),Image.Resampling.LANCZOS);expected.paste(fit,((1920-fit.width)//2,(1080-fit.height)//2));psnr=10*math.log10(255**2/max(mse(expected,frame(files[1],(sh['start']-1)/30)),1e-9));assert psnr>32;clean_psnr[sh['source']]=psnr

# Both props and the GIF must remain moving, rather than a flattened still.
motion={}
for sh in info['shots']:
 if sh['kind']=='gag'or sh['mood']in['cafezinho','rodas']:
  a=(sh['start']-1)/30;b=sh['end']/30;images=[frame(files[1],a+(b-a)*u)for u in [.12,.45,.86]];values=[mse(x,y)for x,y in zip(images,images[1:])];assert max(values)>.5;motion[sh['mood']]=values
with zipfile.ZipFile(F/(slug+'_16x9.wfp'))as z:
 assert z.testzip()is None;data=json.loads(z.read(next(n for n in z.namelist()if n.endswith('timeline.wesproj'))));main=data['timelineInfos'][0];assert(main['resolutionWidth'],main['resolutionHeight'])==(1920,1080);resources={r['sourceUuid']:r for r in data['resources']};clips=0
 assert not main['trackInfos'][13]['clipList'];video_clips=main['trackInfos'][11]['clipList'];assert len(video_clips)==len(info['shots']);assert video_clips[0]['tlBegin']==0 and video_clips[-1]['tlEnd']==round(N/30*1e7);assert all(a['tlEnd']==b['tlBegin']for a,b in zip(video_clips,video_clips[1:]))
 for tr in main['trackInfos']:
  for c in tr['clipList']:
   clips+=1;assert c['tlEnd']>c['tlBegin'];assert abs(c['outPoint']-c['inPoint']-(c['tlEnd']-c['tlBegin']))<=1
   if c.get('filename'):
    r=resources[c['sourceUuid']];assert(F/r['filename'].removeprefix('file:./')).is_file();assert c['outPoint']<=r['mediaLength']+1;speed=json.loads(c['speed']['speedParam']);assert all(k['_value']==1 for k in speed['keyframeSets'])and not c['speed']['reverse']
 for sh,c in zip(info['shots'],video_clips):
  if sh['kind']=='gag':
   for chain in c['effectChainList']:
    for effect in chain['effectList']:
     if effect.get('display')=='transform':
      for p in effect.get('paramMapList',[]):assert all(k['_value']==100 for k in json.loads(p['keyFrame']['parameter'])['keyframeSets'])
with zipfile.ZipFile(O/(slug+'_Filmora.zip'))as z:assert z.testzip()is None;assert sum(n.endswith('.wfp')for n in z.namelist())==1;assert all('midias/'+Path(r['filename']).name in z.namelist()for r in resources.values())
actual=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-threads','1','-i',str(files[0]),'-vn','-ac','2','-ar','44100','-f','s16le','pipe:1']),'<i2').reshape(-1,2).astype(np.float32)
with wave.open(str(P/'assets/audio/mix_final.wav'))as w:expected_audio=np.frombuffer(w.readframes(w.getnframes()),'<i2').reshape(-1,2).astype(np.float32)
n=min(len(actual),len(expected_audio));correlation=float(np.corrcoef(actual[:n].ravel(),expected_audio[:n].ravel())[0,1]);assert correlation>.995
build=json.loads((P/'construcao.json').read_text());assert not build['standing_dery']and build['face_ids']>15 and build['gag_count']==sum(sh['kind']=='gag'for sh in info['shots']);assert ed['titles']==[]
for suffix,video in zip(['16x9'],files[:1]):
 times=[(sh['start']-1+(sh['end']-sh['start'])*.55)/30 for sh in info['shots']];tile=(216,384)if suffix=='9x16'else(384,216);cols=4 if suffix=='9x16'else 3;sheet=Image.new('RGB',(cols*tile[0],math.ceil(len(times)/cols)*(tile[1]+25)),(25,26,31));draw=ImageDraw.Draw(sheet)
 for i,t in enumerate(times):
  im=frame(video,t);im.save(C/f'final_{suffix}_{round(t*30)+1:04d}.jpg',quality=95);x=i%cols*tile[0];y=i//cols*(tile[1]+25);sheet.paste(im.resize(tile,Image.Resampling.LANCZOS),(x,y));draw.text((x+5,y+tile[1]+3),f'{t:.1f}s',fill='white')
 sheet.save(O/f'Previa_Cenas_{suffix}.jpg',quality=94)
record=dict(videos=videos,chapter_order=info['chapter_order'],voice_duration=voice_frames/rate,full_voice_pcm_preserved=True,voice_in_package_bit_identical=True,original_uploads_unchanged=True,full_audio_correlation=correlation,crt_motion_mse=crt_motion,clean_media_psnr=clean_psnr,moving_gags_and_gif_mse=motion,delivery_formats=['16x9'],standing_dery=False,gag_count=build['gag_count'],native_titles=0,face_ids=build['face_ids'],animation_fps=30,media_psx=False,psx_animation=True,filmora_clips=clips,resources_resolve=True,speed_1x=True,zip_integrity=True,filmora_native_open=False)
assert not list(O.glob('*9x16*')) and not list((F/'midias').glob('*9x16*'))
(O/'validacao.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print('DOAX3_VERIFIED',json.dumps(record),flush=True)
