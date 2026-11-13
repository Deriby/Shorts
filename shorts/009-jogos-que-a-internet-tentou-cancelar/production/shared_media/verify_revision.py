"""Validate revised media quality, preserved animation and portable Filmora resources."""
from pathlib import Path
import sys,json,subprocess,zipfile,hashlib,wave,math
from PIL import Image,ImageOps,ImageDraw,ImageFont
import numpy as np
P=Path(sys.argv[1]).resolve();legacy='--legacy'in sys.argv
info=json.loads((P/'timeline.json').read_text());OUT=P/'output/R3_Midias_Limpas'if legacy else P/'output';C=Path('/workspace/attachments/clean_media')/P.name if legacy else Path(info['cache'])
filmora=OUT/'Filmora';manifest=json.loads((OUT/'midias_limpas.json').read_text())
def probe(path):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
def frame(path,time):
 b=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(time),'-i',str(path),'-frames:v','1','-f','image2pipe','-c:v','png','-threads','1','pipe:1']);from io import BytesIO;return Image.open(BytesIO(b)).convert('RGB')
def mse(a,b):x=np.asarray(a,np.float32)-np.asarray(b,np.float32);return float(np.mean(x*x))
files=[P/v for v in manifest['outputs']];reports=[]
for path,size in zip(files,[(1080,1920),(1920,1080),(1080,1920)]):
 d=probe(path);v=next(v for v in d['streams']if v['codec_type']=='video');assert(v['width'],v['height'])==size;assert v['r_frame_rate']=='30/1';assert int(v['nb_frames'])==info['frames'];assert abs(float(d['format']['duration'])-info['duration'])<.035
 if path==files[-1]:assert all(v['codec_type']!='audio'for v in d['streams'])
 reports.append(dict(file=str(path.relative_to(P)),bytes=path.stat().st_size,frames=int(v['nb_frames']),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
# Full decode catches truncation, without re-rendering or changing the edit.
for path in files[:2]:subprocess.run(['ffmpeg','-v','error','-threads','1','-i',str(path),'-map','0:v:0','-map','0:a:0','-f','null','-'],check=True)
project=next(filmora.glob('*.wfp'))
with zipfile.ZipFile(project)as z:
 assert z.testzip()is None;d=json.loads(z.read(next(n for n in z.namelist()if n.endswith('timeline.wesproj'))));main=d['timelineInfos'][0];assert(main['resolutionWidth'],main['resolutionHeight'])==(1080,1920)
 resources={r['sourceUuid']:r for r in d['resources']};clips=0
 for tr in main['trackInfos']:
  for clip in tr['clipList']:
   clips+=1;assert clip['tlEnd']>clip['tlBegin']
   if clip.get('filename'):
    r=resources[clip['sourceUuid']];p=filmora/r['filename'].removeprefix('file:./');assert p.is_file();assert clip['outPoint']<=r['mediaLength']+1
    speed=json.loads(clip['speed']['speedParam']);assert all(k['_value']==1 for k in speed['keyframeSets']);assert not clip['speed']['reverse']
 if not legacy:assert not main['trackInfos'][13]['clipList']
bundle=next(OUT.glob('*Filmora*.zip'))
with zipfile.ZipFile(bundle)as z:assert z.testzip()is None;assert sum(n.endswith('.wfp')for n in z.namelist())==1
# An actual photo on the encoded silent base must match a clean source resized
# with normal interpolation; it must improve over the old pixelated rendering.
photo=next(sh for sh in info['shots']if sh['kind']=='photo'and('jack' in sh['source']or'censur' in sh['source']or'bug' in sh['source']or'weapon_menu' in sh['source']))
t=((photo['start']-1)+min(20,(photo['end']-photo['start'])//2))/info['fps'];source=Image.open(P/'assets/imagens'/photo['source']).convert('RGB');expected=Image.new('RGB',(1080,1920),(31,30,39));fit=ImageOps.contain(source,(1080,round(340/432*1920)),Image.Resampling.LANCZOS);expected.paste(fit,((1080-fit.width)//2,(1920-fit.height)//2));actual=frame(files[-1],t);new_mse=mse(actual,expected)
quality=dict(photo=photo['source'],time=t,new_mse=new_mse,new_psnr=10*math.log10(255**2/max(new_mse,1e-8)))
if legacy:
 plans={'01-gta-san-andreas':('Filmora_R2','GTA_base_R2_9x16.mp4'),'02-bmx-xxx':('Filmora','BMX_base_9x16.mp4'),'03-bully':('Filmora','Bully_base_9x16.mp4')};folder,name=plans[P.name];old=P/'output'/folder/'midias'/name;old_image=frame(old,t);old_mse=mse(old_image,expected);quality.update(old_mse=old_mse,error_ratio=new_mse/max(old_mse,1e-8));assert new_mse<old_mse*.85,quality
 # Pure animation on the base is preserved apart from ordinary H.264 compression.
 host=next(sh for sh in info['shots']if sh['kind']=='host');time=((host['start']-1)+20)/info['fps'];anim_error=mse(frame(old,time),frame(files[-1],time));quality['animation_psnr']=10*math.log10(255**2/max(anim_error,1e-8));assert quality['animation_psnr']>34,quality
 compare=Image.new('RGB',(1080,1000),(24,24,29));left=ImageOps.contain(old_image,(520,940));right=ImageOps.contain(actual,(520,940));compare.paste(left,(0,30));compare.paste(right,(550,30));draw=ImageDraw.Draw(compare);draw.text((20,8),'ANTES',fill='white');draw.text((570,8),'MIDIA LIMPA',fill='white');compare.save(OUT/'Comparativo_Midia.jpg',quality=95)
else:assert quality['new_psnr']>33,quality
# Actual delivered-frame contacts for each format.
for suffix in['9x16','16x9']:
 pictures=sorted(C.glob(f'final_{suffix}_*.jpg'));tile=(216,384)if suffix=='9x16'else(384,216);cols=4 if suffix=='9x16'else 3;rows=math.ceil(len(pictures)/cols);sheet=Image.new('RGB',(cols*tile[0],rows*(tile[1]+24)),(25,26,31));draw=ImageDraw.Draw(sheet)
 for i,p in enumerate(pictures):x=i%cols*tile[0];y=i//cols*(tile[1]+24);sheet.paste(Image.open(p).resize(tile),(x,y));draw.text((x+6,y+tile[1]+3),f'{(int(p.stem.rsplit("_",1)[1])-1)/info["fps"]:.1f}s',fill='white')
 sheet.save(OUT/f'Previa_Cenas_{suffix}.jpg',quality=94)
record=dict(videos=reports,clips=clips,filmora_resources_resolve=True,speed_1x=True,zip_integrity=True,media_quality=quality,media_psx_filter=False,animation_psx=True,filmora_native_open=False)
(OUT/'validacao_midias.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print('CLEAN_MEDIA_VALIDATED',P.name,json.dumps(quality),flush=True)
