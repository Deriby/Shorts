from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,subprocess,sqlite3
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;C=Path('/workspace/attachments/memes009');D=P/'miniaturas';D.mkdir(exist_ok=True)
d=json.loads((P/'catalogo.json').read_text())
def probe(x):
 p=P/x['relative_file']
 try:
  info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]));x['duration']=float(info['format'].get('duration',0));x['streams']=[{k:s[k]for k in ('codec_type','codec_name','width','height','r_frame_rate','sample_rate','channels','nb_frames')if k in s}for s in info['streams']]
  if x['category']!='audio':
   thumb=D/(x['tag']+'.jpg')
   if any(s['codec_type']=='video'and s['codec_name']not in ('mjpeg','png','webp')for s in info['streams']):
    subprocess.run(['ffmpeg','-v','error','-threads','1','-ss',str(min(.25,x['duration']/3)),'-i',str(p),'-frames:v','1','-vf','scale=310:173:force_original_aspect_ratio=decrease','-threads','1','-y',str(thumb)],check=True)
   else:
    im=Image.open(p).convert('RGB');im.thumbnail((310,173));im.save(thumb,quality=86)
   x['thumbnail']=str(thumb.relative_to(P))
  x['probe_ok']=True
 except Exception as e:x['probe_error']=str(e)
 return x
with ThreadPoolExecutor(max_workers=2)as pool:d['items']=list(pool.map(probe,d['items']))
(P/'catalogo.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
items=sorted([x for x in d['items']if x.get('thumbnail')],key=lambda x:(x['tag'][0],int(x['tag'][1:])))
for page in range((len(items)+19)//20):
 im=Image.new('RGB',(1280,1000),(23,24,29));dr=ImageDraw.Draw(im)
 for j,x in enumerate(items[page*20:(page+1)*20]):
  px=j%4*320;py=j//4*200;t=Image.open(P/x['thumbnail']);im.paste(t,(px+(320-t.width)//2,py+(173-t.height)//2));dr.text((px+6,py+176),x['tag']+' '+x['name'][:26],fill='white')
 im.save(C/f'banco_prancha_{page+1:02d}.jpg',quality=87)
db=sqlite3.connect(P/'catalogo.sqlite3')
for sql in ['ALTER TABLE assets ADD COLUMN duration REAL','ALTER TABLE assets ADD COLUMN width INTEGER','ALTER TABLE assets ADD COLUMN height INTEGER','ALTER TABLE assets ADD COLUMN thumbnail TEXT']:
 try:db.execute(sql)
 except sqlite3.OperationalError:pass
for x in d['items']:
 v=next((s for s in x.get('streams',[])if s['codec_type']=='video'),{});db.execute('UPDATE assets SET duration=?,width=?,height=?,thumbnail=?,review_status=? WHERE id=?',(x.get('duration'),v.get('width'),v.get('height'),x.get('thumbnail'),'probed'if x.get('probe_ok')else'probe_failed',x['id']))
db.commit();db.close();print('INDEXED',len(items),'visual assets;',sum(x.get('probe_ok',False)for x in d['items']),'of',len(d['items']))
