"""Validate complete original voice, clean moving CRT and the editable project."""
from pathlib import Path
from io import BytesIO
import json,subprocess,zipfile,hashlib,wave,math
import numpy as np
from PIL import Image,ImageOps,ImageDraw
P=Path(__file__).resolve().parent;O=P/'output';info=json.loads((P/'timeline.json').read_text());ed=json.loads((P/'edicao.json').read_text());C=Path(info['cache']);F=O/'Filmora';N=info['frames'];slug=info['slug']
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
def frame(p,t):return Image.open(BytesIO(subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(t),'-i',str(p),'-frames:v','1','-c:v','png','-threads','1','-f','image2pipe','pipe:1']))).convert('RGB')
def mse(a,b):return float(np.mean((np.asarray(a,np.float32)-np.asarray(b,np.float32))**2))
with wave.open(str(P/'assets/voz/voz_completa.wav'))as w:voice=w.readframes(w.getnframes());voice_frames=w.getnframes();rate=w.getframerate()
with wave.open(str(P/'assets/voz/voz_timeline.wav'))as w:padded=w.readframes(w.getnframes());assert padded[:len(voice)]==voice and set(padded[len(voice):])<={0}
assert hashlib.sha256((F/'midias/voz_timeline.wav').read_bytes()).digest()==hashlib.sha256((P/'assets/voz/voz_timeline.wav').read_bytes()).digest()
tape=probe(P/info['monitor_file']);assert int(next(v for v in tape['streams']if v['codec_type']=='video')['nb_frames'])==N
files=[O/(slug+'_Cancelar_9x16.mp4'),O/(slug+'_Cancelar_16x9.mp4'),F/'midias'/(slug+'_base_9x16.mp4')];videos=[]
for p,size in zip(files,[(1080,1920),(1920,1080),(1080,1920)]):
 d=probe(p);v=next(s for s in d['streams']if s['codec_type']=='video');assert(v['width'],v['height'])==size;assert int(v['nb_frames'])==N and v['r_frame_rate']=='30/1';assert abs(float(d['format']['duration'])-N/30)<.035
 if p==files[2]:assert not any(s['codec_type']=='audio'for s in d['streams'])
 subprocess.run(['ffmpeg','-v','error','-threads','1','-i',str(p),'-f','null','-'],check=True);videos.append(dict(file=p.name,frames=N,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
crt=[frame(files[2],t)for t in [.2,.5,.9,1.3]];crt_motion=[mse(a,b)for a,b in zip(crt,crt[1:])];assert min(crt_motion)>.5,crt_motion
host=[frame(files[2],t)for t in [3.2,3.7,4.3,4.7]];assert len({hashlib.sha256(im.tobytes()).hexdigest()for im in host})==4
photo=Image.open(P/'assets/imagens/group.png').convert('RGB');expected=Image.new('RGB',(1080,1920),(31,30,39));fit=ImageOps.contain(photo,(1080,round(340/432*1920)),Image.Resampling.LANCZOS);expected.paste(fit,((1080-fit.width)//2,(1920-fit.height)//2));error=mse(expected,frame(files[2],24));photo_psnr=10*math.log10(255**2/max(error,1e-9));assert photo_psnr>33,photo_psnr
with zipfile.ZipFile(F/(slug+'_9x16.wfp'))as z:
 assert z.testzip()is None;d=json.loads(z.read(next(n for n in z.namelist()if n.endswith('timeline.wesproj'))));main=d['timelineInfos'][0];assert(main['resolutionWidth'],main['resolutionHeight'])==(1080,1920);resources={r['sourceUuid']:r for r in d['resources']};clips=0
 assert not main['trackInfos'][13]['clipList']
 video_clips=main['trackInfos'][11]['clipList'];assert len(video_clips)==len(info['shots']);assert video_clips[0]['tlBegin']==0 and video_clips[-1]['tlEnd']==round(N/30*1e7);assert all(a['tlEnd']==b['tlBegin']for a,b in zip(video_clips,video_clips[1:]))
 for tr in main['trackInfos']:
  for c in tr['clipList']:
   clips+=1;assert c['tlEnd']>c['tlBegin'];assert abs(c['outPoint']-c['inPoint']-(c['tlEnd']-c['tlBegin']))<=1
   if c.get('filename'):
    r=resources[c['sourceUuid']];assert(F/r['filename'].removeprefix('file:./')).is_file();assert c['outPoint']<=r['mediaLength']+1;speed=json.loads(c['speed']['speedParam']);assert all(k['_value']==1 for k in speed['keyframeSets'])and not c['speed']['reverse']
with zipfile.ZipFile(O/(slug+'_Filmora.zip'))as z:assert z.testzip()is None;assert sum(n.endswith('.wfp')for n in z.namelist())==1;assert all('midias/'+Path(r['filename']).name in z.namelist()for r in resources.values())
actual=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-threads','1','-i',str(files[0]),'-vn','-ac','2','-ar','44100','-f','s16le','pipe:1']),'<i2').reshape(-1,2).astype(np.float32)
with wave.open(str(P/'assets/audio/mix_final.wav'))as w:expected_audio=np.frombuffer(w.readframes(w.getnframes()),'<i2').reshape(-1,2).astype(np.float32)
n=min(len(actual),len(expected_audio));correlation=float(np.corrcoef(actual[:n].ravel(),expected_audio[:n].ravel())[0,1]);assert correlation>.995,correlation
build=json.loads((P/'construcao.json').read_text());assert not build['standing_dery']and build['face_ids']>15;assert ed['titles']==[]
for suffix in ['9x16','16x9']:
 pictures=sorted(C.glob(f'final_{suffix}_*.jpg'));tile=(216,384)if suffix=='9x16'else(384,216);cols=4 if suffix=='9x16'else 3;sheet=Image.new('RGB',(cols*tile[0],math.ceil(len(pictures)/cols)*(tile[1]+25)),(25,26,31));draw=ImageDraw.Draw(sheet)
 for i,p in enumerate(pictures):
  x=i%cols*tile[0];y=i//cols*(tile[1]+25);sheet.paste(Image.open(p).resize(tile,Image.Resampling.LANCZOS),(x,y));draw.text((x+5,y+tile[1]+3),f'{(int(p.stem.rsplit("_",1)[1])-1)/30:.1f}s',fill='white')
 sheet.save(O/f'Previa_Cenas_{suffix}.jpg',quality=94)
record=dict(videos=videos,chapter_order=4,voice_duration=voice_frames/rate,full_voice_pcm_preserved=True,voice_in_package_bit_identical=True,full_audio_correlation=correlation,crt_motion_mse=crt_motion,steam_group_clean_psnr=photo_psnr,standing_dery=False,new_props=False,native_titles=0,face_ids=build['face_ids'],animation_fps=30,media_psx=False,psx_animation=True,filmora_clips=clips,resources_resolve=True,speed_1x=True,zip_integrity=True,filmora_native_open=False)
(O/'validacao.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print('L4D_VERIFIED',json.dumps(record),flush=True)
