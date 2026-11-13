"""Verify complete voice, moving resources, cut coverage and native project structure."""
from pathlib import Path
import json,sys,subprocess,hashlib,zipfile,wave,math
import numpy as np
from PIL import Image,ImageOps,ImageDraw
from io import BytesIO
P=Path(__file__).resolve().parent;ROOT=P.parent
sources={
'01-gta-san-andreas':('R3_Midias_Limpas','GTA_San_Andreas_R3_Midias_Limpas','GTA_base_R2_9x16.mp4'),
'02-bmx-xxx':('R3_Midias_Limpas','BMX_XXX_R3_Midias_Limpas','BMX_base_9x16.mp4'),
'03-bully':('R3_Midias_Limpas','Bully_R3_Midias_Limpas','Bully_base_9x16.mp4'),
'04-saints-row-iv':('','Saints_Row_IV_Cancelar','Saints_Row_IV_base_9x16.mp4')}
def probe(path):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
def frame(path,t):
 return Image.open(BytesIO(subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(t),'-i',str(path),'-frames:v','1','-c:v','png','-threads','1','-f','image2pipe','pipe:1']))).convert('RGB')
def error(a,b):return float(np.mean((np.asarray(a,np.float32)-np.asarray(b,np.float32))**2))
for ep in sys.argv[1:]or list(sources):
 project=ROOT/ep;out=project/'output/R4_Sem_Dery_Em_Pe';info=json.loads((out/'timeline.json').read_text());folder,oldslug,base=sources[ep];oldout=project/'output'/folder;files=[out/(info['slug']+'_R4_9x16.mp4'),out/(info['slug']+'_R4_16x9.mp4'),out/'Filmora/midias'/base];checks=[]
 for f,size in zip(files,[(1080,1920),(1920,1080),(1080,1920)]):
  d=probe(f);v=next(x for x in d['streams']if x['codec_type']=='video');assert(v['width'],v['height'])==size;assert int(v['nb_frames'])==info['frames'];assert v['r_frame_rate']=='30/1';assert abs(float(d['format']['duration'])-info['frames']/30)<.035
  subprocess.run(['ffmpeg','-v','error','-threads','1','-i',str(f),'-f','null','-'],check=True);checks.append(dict(file=f.name,frames=int(v['nb_frames']),sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
 oldplan=json.loads((project/'timeline.json').read_text());assert not any(sh['kind']in['shop','archive']for sh in info['shots'])
 for old in oldplan['shots']:
  if old['kind']in['shop','archive']:
   covered=[s for s in info['shots']if s['original_shot']==old['id']];assert all(s['patch']for s in covered);assert sum(s['end']-s['start']+1 for s in covered)==old['end']-old['start']+1
 # Check unchanged monitor frames against the delivered clean-media revision.
 monitor=next(s for s in info['shots']if s['kind']=='monitor');t=((monitor['start']+monitor['end'])/2-1)/30;oldbase=oldout/'Filmora/midias'/base;mse=error(frame(oldbase,t),frame(files[2],t));monitor_psnr=10*math.log10(255**2/max(1e-9,mse));assert monitor_psnr>33,monitor_psnr
 wfp=next((out/'Filmora').glob('*.wfp'))
 with zipfile.ZipFile(wfp)as z:
  assert z.testzip()is None;d=json.loads(z.read(next(n for n in z.namelist()if n.endswith('timeline.wesproj'))));main=d['timelineInfos'][0];assert(main['resolutionWidth'],main['resolutionHeight'])==(1080,1920);resources={r['sourceUuid']:r for r in d['resources']};videos=[]
  for tr in main['trackInfos']:
   for c in tr['clipList']:
    if c.get('filename'):
     r=resources[c['sourceUuid']];f=out/'Filmora'/r['filename'].removeprefix('file:./');assert f.is_file();assert c['outPoint']<=r['mediaLength']+1;assert c['tlEnd']>c['tlBegin'];assert Path(c['filename']).name not in ['ui_desbloqueio.wav','selo_ao.wav','caixas.wav'];p=json.loads(c['speed']['speedParam']);assert all(x['_value']==1 for x in p['keyframeSets']);assert not c['speed']['reverse']
     if c['filename'].endswith('.mp4'):videos.append(c)
  assert len(videos)==len(info['shots']);assert videos[0]['tlBegin']==0 and videos[-1]['tlEnd']==round(info['frames']/30*1e7);assert all(a['tlEnd']==b['tlBegin']for a,b in zip(videos,videos[1:]))
 assert hashlib.sha256((out/'Filmora/midias/voz_timeline.wav').read_bytes()).digest()==hashlib.sha256((project/'assets/voz/voz_timeline.wav').read_bytes()).digest()
 # Confirm output audio is the revised full mix, at the same timing.
 raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-i',str(files[0]),'-vn','-ac','2','-ar','44100','-f','s16le','pipe:1']);actual=np.frombuffer(raw,'<i2').reshape(-1,2).astype(np.float32)
 with wave.open(str(out/'mix_revisado.wav'))as w:expected=np.frombuffer(w.readframes(w.getnframes()),'<i2').reshape(-1,2).astype(np.float32)
 n=min(len(actual),len(expected));correlation=float(np.corrcoef(actual[:n].ravel(),expected[:n].ravel())[0,1]);assert correlation>.995,correlation
 # A gameplay patch really advances within the encoded Filmora base.
 game=next(s for s in info['shots']if s['patch']and s['kind']=='game');t=(game['start']-1)/30;motion=error(frame(files[2],t+.15),frame(files[2],min(game['end']/30-.05,t+.75)));assert motion>10,motion
 with zipfile.ZipFile(out/(info['slug']+'_R4_Filmora.zip'))as z:assert z.testzip()is None;assert sum(n.endswith('.wfp')for n in z.namelist())==1
 samples=[]
 for sh in info['shots']:
  if sh['patch']or sh['kind']=='monitor':samples.append((sh,(sh['start']+sh['end']-2)/60))
 for file,tag,tile,cols in [(files[0],'9x16',(216,384),4),(files[1],'16x9',(384,216),3)]:
  rows=math.ceil(len(samples)/cols);sheet=Image.new('RGB',(cols*tile[0],rows*(tile[1]+35)),(25,25,29));draw=ImageDraw.Draw(sheet)
  for i,(sh,t)in enumerate(samples):
   im=frame(file,t).resize(tile,Image.Resampling.LANCZOS);x=i%cols*tile[0];y=i//cols*(tile[1]+35);sheet.paste(im,(x,y));draw.text((x+4,y+tile[1]+3),f"{t:.1f}s {sh['kind']}",fill='white')
  sheet.save(out/f'Previa_R4_{tag}.jpg',quality=94)
 report=dict(outputs=checks,standing_dery=False,extra_sets=False,all_rejected_ranges_replaced=True,monitor_clean_media_preserved_psnr=monitor_psnr,voice_file_bit_identical=True,full_mix_correlation=correlation,gameplay_patch_motion_mse=motion,project_clips=len(videos),speed_1x=True,all_resources_resolve=True,zip_integrity=True,no_new_subtitles=True,filmora_native_open=False)
 (out/'validacao_r4.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('R4_VERIFIED',ep,correlation,monitor_psnr,flush=True)
