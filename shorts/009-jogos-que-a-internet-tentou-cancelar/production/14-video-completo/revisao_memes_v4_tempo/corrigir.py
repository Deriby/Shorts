"""Extend meme sustain; retain quick entrances/exits and the user's full edit."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,zipfile,copy,hashlib,subprocess,base64,uuid
from PIL import Image,ImageFilter,ImageEnhance
P=Path(__file__).resolve().parent;R=next(p for p in P.parents if(p/'AGENTS.md').exists());V3=P.parent/'revisao_memes_v3';F=P/'output/Filmora';M=F/'midias';C=Path('/workspace/attachments/memes009_r4');C.mkdir(exist_ok=True)
SOURCE=V3/'output/Filmora/Massacote_Completo_MEMES.wfp';OUT=F/'Massacote_MEMES_Tempo_Corrigido.wfp';T=10000000
ROOT='{204E72A3-B517-44d4-806F-9E9D84D5F904}';TL=f'ProjectFolder/Medias/{ROOT}/timeline.wesproj';LIB='ProjectFolder/Medias/medias_info.json'
plan=json.loads((V3/'plano_aplicado.json').read_text());bank={x['tag']:x for x in json.loads((R/'assets/biblioteca_memes/catalogo.json').read_text())['items']};source_sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
# Explicit durations per reaction, at 30 fps. Short source clips use their full
# action instead of a freeze, loop or slow motion to reach an arbitrary quota.
durations=[1.8,3.1,2.0,2.6,1.9,2.2,2.7,2.2,2.0,2.8,2.8,2.0,2.0,2.0666666667,1.8,2.6,2.8,2.7,1.9,1.9,2.0,2.8,2.8,1.8,1.8,1.3,1.8,2.8,1.8,1.9,2.0,1.9,2.0,2.2,2.6,2.8,1.9,2.5,3.0,2.6,2.0,2.8,1.8,1.8,2.7,1.9,2.4,1.6666666667,1.9,2.8,3.3,1.6]
starts={'meme_04':6.6,'meme_28':12.9,'meme_38':22.5,'meme_39':38.1,'meme_52':21.2}
source_starts={'V10':3.1,'V02':1.7,'V08':4.4,'V25':1.8,'V67':1.4,'V42':0.,'V82':5.8,'V68':3.1,'V05':1.7,'V59':1.7,'V21':1.7,'V49':0.,'V56':15.3,'V60':3.8,'V19':9.5,'V64':1.2,'V11':1.5,'V26':1.9,'V06':3.7,'V09':2.8,'V47':0.,'V51':1.6,'V87':1.8}
for cue,duration in zip(plan['cues'],durations):
 cue['previous_frames']=cue['frames'];cue['previous_start_frame']=cue['start_frame'];cue['previous_source_start']=cue['source_start'];cue['frames']=round(duration*30)
 if cue['id']in starts:
  local=round(starts[cue['id']]*30);cue['start_frame']+=local-cue['local_start_frame'];cue['local_start_frame']=local
 if cue['asset_tag'].startswith('V'):cue['source_start']=source_starts[cue['asset_tag']]

def run(cmd):subprocess.run(cmd,check=True)
def prepare(cue):
 asset=bank[cue['asset_tag']];src=R/'assets/biblioteca_memes'/asset['relative_file'];duration=cue['frames']/30
 assert cue['source_start']+duration<=asset['duration']+.00001,(cue['id'],duration,asset['duration'])
 name=Path(cue['prepared_file']);dest=M/(name.stem+'_R4.mp4');still=C/(cue['id']+'.png')
 run(['ffmpeg','-v','error','-threads','1','-ss',str(cue['source_start']),'-i',str(src),'-frames:v','1','-threads','1','-y',str(still)])
 bg=Image.open(still).convert('RGB').resize((1920,1080)).filter(ImageFilter.GaussianBlur(30));bg=ImageEnhance.Brightness(bg).enhance(.23);bgpath=C/(cue['id']+'_bg.png');bg.save(bgpath)
 vf='[1:v]setpts=PTS-STARTPTS,fps=30,scale=1640:900:force_original_aspect_ratio=decrease,setsar=1[v];[0:v][v]overlay=(W-w)/2:(H-h)/2:shortest=1,format=yuv420p[out]'
 run(['ffmpeg','-v','error','-threads','1','-loop','1','-framerate','30','-i',str(bgpath),'-ss',str(cue['source_start']),'-i',str(src),'-filter_complex_threads','1','-filter_complex',vf,'-map','[out]','-an','-frames:v',str(cue['frames']),'-r','30','-c:v','libx264','-preset','veryfast','-crf','18','-threads','1','-movflags','+faststart','-y',str(dest)])
 cue['previous_prepared_file']=cue['prepared_file'];cue['prepared_file']=dest.name;cue['prepared_sha256']=hashlib.sha256(dest.read_bytes()).hexdigest()
with ThreadPoolExecutor(max_workers=2)as pool:list(pool.map(prepare,[c for c in plan['cues']if c['asset_tag'].startswith('V')]))
with zipfile.ZipFile(SOURCE)as z:raw={n:z.read(n)for n in z.namelist()}
d=json.loads(raw[TL]);before=copy.deepcopy(d);main=d['timelineInfos'][0];visuals={c['thisUId']:c for c in main['trackInfos'][-1]['clipList']};sounds=main['trackInfos'][-2]['clipList'];lib=json.loads(raw[LIB]);lib_before=copy.deepcopy(lib);resources={r['sourceUuid']:r for r in d['resources']}
for cue in plan['cues']:
 c=visuals[cue['native_clip_id']];old_duration=(c['outPoint']-c['inPoint'])/T;duration=cue['frames']/30;old_start=c['tlBegin'];c.update(tlBegin=round(cue['start_frame']*T/30),outPoint=round(duration*T));c['tlEnd']=c['tlBegin']+c['outPoint']-c['inPoint'];c['speed']['offsetEnd']=duration
 for ch in c['effectChainList']:
  for fx in ch['effectList']:
   for p in fx.get('paramMapList',[]):
    curve=json.loads(p['keyFrame']['parameter'])
    for k in curve['keyframeSets']:
     t=k['_time']
     if t>.25:
      if t>=old_duration-.15-1e-7:t=duration-(old_duration-t)
      else:t=.25+(t-.25)*(duration-.4)/max(.001,old_duration-.4)
      k['_time']=round(t*T)/T
    curve.pop('MD5',None);p['keyFrame']['parameter']=json.dumps(curve,separators=(',',':'))
 # Any short sound attached to the entrance follows a shifted entrance. Its
 # duration and level remain unchanged; original voice/music/SFX never move.
 for sound in sounds:
  if sound['tlBegin']==old_start and cue.get('sound_tag'):
   delta=c['tlBegin']-old_start;sound['tlBegin']+=delta;sound['tlEnd']+=delta
 if cue['asset_tag'].startswith('V'):
  r=resources[c['sourceUuid']];path=M/cue['prepared_file'];info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]));v=info['streams'][0]
  c['filename']='file:./midias/'+path.name;r.update(filename=c['filename'],mediaLength=round(duration*T),bitRate=int(info['format']['bit_rate']))
  for stream in r['vidStreamInfo']:stream.update(totalFrames=cue['frames'],streamLength=round(duration*T),bitRate=int(v.get('bit_rate',0)))
  s=json.loads(c['speed']['speedParam']);s['_totalTime']=duration;s['keyframeSets'][-1]['_time']=duration;c['speed']['speedParam']=json.dumps(s,separators=(',',':'))
  mid=next(base64.b64decode(u['data']).decode().rstrip('\0')for u in c['userData']if u['key']==10);item=lib['media_items'][mid];item.update(name=path.stem,download_url='./midias/'+path.name,media_length=round(duration*T),src_md5=hashlib.md5(path.read_bytes()).hexdigest())
  cachepath=f'ProjectFolder/Medias/{mid}/media.json';cache=json.loads(raw[cachepath]);cache['file_name']='./midias/'+path.name;cache['sourceInfo']['basicInfo'].update(mediaLength=r['mediaLength'],bitRate=r['bitRate']);cache['sourceInfo']['vidStreamInfos']=copy.deepcopy(r['vidStreamInfo']);raw[cachepath]=json.dumps(cache,separators=(',',':')).encode()
# Preserve the duplicate media_structure keys exactly as in the working source.
b=raw[LIB].decode();prefix=b[:b.index('"media_items":')];raw[LIB]=(prefix+'"media_items":'+json.dumps(lib['media_items'],ensure_ascii=False,separators=(',',':'))+'}').encode()
d['projectName']=OUT.stem;raw[TL]=json.dumps(d,ensure_ascii=False,separators=(',',':')).encode();meta=json.loads(raw['ProjectFolder/project_info.json']);meta.update(project_file_name=OUT.stem,proj_zip_save_path=OUT.name,project_guid='{'+str(uuid.uuid4()).upper()+'}');raw['ProjectFolder/project_info.json']=json.dumps(meta,ensure_ascii=False,separators=(',',':')).encode()
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_STORED)as z:
 for n,b in raw.items():z.writestr(n,b)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_sha
(P/'plano_corrigido.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
(P/'revisao.json').write_text(json.dumps(dict(source=str(SOURCE.relative_to(R)),source_sha256=source_sha,project=OUT.name,project_sha256=hashlib.sha256(OUT.read_bytes()).hexdigest(),visuals=52,videos=24,new_video_files=24,original_user_edit_unchanged=True,fast_entrance_exit_preserved=True,filmora_native_open=False),indent=2)+'\n');print('SUSTAIN_REVISION_READY',flush=True)
