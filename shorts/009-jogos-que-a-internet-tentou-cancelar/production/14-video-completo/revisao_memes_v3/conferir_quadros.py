"""Review actual meme placement over the user's basic transform; plugins omitted."""
from pathlib import Path
import json,zipfile,subprocess
from concurrent.futures import ThreadPoolExecutor
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;OLD=P.parent/'output/Filmora';M=P/'output/Filmora/midias';C=Path('/workspace/attachments/memes009/quadros');C.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(P/'output/Filmora/Massacote_Completo_MEMES.wfp')as z:d=json.loads(z.read('ProjectFolder/Medias/{204E72A3-B517-44d4-806F-9E9D84D5F904}/timeline.wesproj'))
main=d['timelineInfos'][0];plan=json.loads((P/'plano_aplicado.json').read_text());base=main['trackInfos'][11]['clipList'];overlays={c['thisUId']:c for c in main['trackInfos'][-1]['clipList']}
def val(e,name,t,default):
 p=next((p for p in e.get('paramMapList',[])if p['name']==name),None)
 if not p:return next((p['fxParam']['unValue']for p in e['paramList']if p['name']==name),default)
 ks=json.loads(p['keyFrame']['parameter'])['keyframeSets']
 if t<=ks[0]['_time']:return ks[0]['_value']
 for a,b in zip(ks,ks[1:]):
  if a['_time']<=t<=b['_time']:return a['_value']+(b['_value']-a['_value'])*(t-a['_time'])/(b['_time']-a['_time'])
 return ks[-1]['_value']
def transform(im,c,time):
 e=next(e for ch in c['effectChainList']for e in ch['effectList']if e.get('display')=='transform');sx=val(e,'Scale_x',time,100)/100;sy=val(e,'Scale_y',time,100)/100;px=val(e,'Position_x',time,.5);py=val(e,'Position_y',time,.5)
 return im.transform((640,360),Image.Transform.AFFINE,(1/sx,0,640*(.5-px/sx),0,1/sy,360*(.5-py/sy)),Image.Resampling.BILINEAR)
def extract(path,time,dest):subprocess.run(['ffmpeg','-v','error','-threads','1','-ss',str(time),'-i',str(path),'-frames:v','1','-vf','scale=640:360','-threads','1','-y',str(dest)],check=True)
def make(cue):
 time=cue['start_frame']/30+.32;c=next(c for c in base if c['tlBegin']/1e7<=time<c['tlEnd']/1e7);source_time=c['inPoint']/1e7+time-c['tlBegin']/1e7;p=C/(cue['id']+'_base.png');extract(OLD/'midias'/Path(c['filename']).name,source_time,p);bg=transform(Image.open(p).convert('RGBA'),c,source_time)
 path=M/cue['prepared_file']
 if path.suffix=='.mp4':p=C/(cue['id']+'_meme.png');extract(path,.32,p);fg=Image.open(p).convert('RGBA')
 else:fg=Image.open(path).convert('RGBA').resize((640,360))
 fg=transform(fg,overlays[cue['native_clip_id']],.32);bg.alpha_composite(fg);dest=C/(cue['id']+'.jpg');bg.convert('RGB').save(dest,quality=90);return dest
with ThreadPoolExecutor(max_workers=3)as pool:paths=list(pool.map(make,plan['cues']))
for page in range((len(paths)+11)//12):
 sheet=Image.new('RGB',(1280,660),(20,21,26));dr=ImageDraw.Draw(sheet)
 for i,path in enumerate(paths[page*12:(page+1)*12]):
  cue=plan['cues'][page*12+i];x=i%4*320;y=i//4*220;sheet.paste(Image.open(path).resize((320,180)),(x,y));dr.text((x+4,y+183),cue['id']+' '+cue['chapter'][:22],fill='white');dr.text((x+4,y+199),cue['idea'][:39],fill='#ffdc55')
 sheet.save(P/f'Conferencia_Memes_{page+1}.jpg',quality=90)
print('MEME_FRAMES_READY',len(paths))
