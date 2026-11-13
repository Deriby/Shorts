"""Preserve the delivered native Filmora project while revising its actual cuts."""
from pathlib import Path
import json,sys,zipfile,copy,uuid,shutil,hashlib,subprocess
P=Path(__file__).resolve().parent;ROOT=P.parent
for project in ([ROOT/name for name in sys.argv[1:]] if len(sys.argv)>1 else sorted(ROOT.glob('0[1-4]-*'))):
 out=project/'output/R4_Sem_Dery_Em_Pe';info=json.loads((out/'timeline.json').read_text());slug=info['slug'];oldout=project/'output'/(''if project.name.startswith('04-')else'R3_Midias_Limpas');srcdir=oldout/'Filmora';dest=out/'Filmora';media=dest/'midias';source=next(srcdir.glob('*.wfp'));source_sha=hashlib.sha256(source.read_bytes()).hexdigest()
 with zipfile.ZipFile(source)as z:files={n:z.read(n)for n in z.namelist()}
 tl=next(n for n in files if n.endswith('timeline.wesproj'));data=json.loads(files[tl]);main=data['timelineInfos'][0];video_track=next(tr for tr in main['trackInfos']if any(c.get('filename','').endswith('.mp4')for c in tr['clipList']));oldclips=video_track['clipList'];newclips=[]
 for sh in info['shots']:
  original=next(c for c in oldclips if c['tlBegin']<=round((sh['start']-1)/30*1e7)and c['tlEnd']>=round(sh['end']/30*1e7));c=copy.deepcopy(original);c['thisUId']=str(uuid.uuid4());a=(sh['start']-1)/30;b=sh['end']/30;c.update(tlBegin=round(a*1e7),tlEnd=round(b*1e7),inPoint=round(a*1e7),outPoint=round(b*1e7))
  params=json.loads(c['speed']['speedParam']);params['_totalTime']=info['frames']/30;params['keyframeSets']=[{'_time':0.,'Interpolation':6,'_value':1.},{'_time':info['frames']/30,'Interpolation':6,'_value':1.}];c['speed'].update(offset=a,offsetEnd=b,speedParam=json.dumps(params,separators=(',',':')))
  if sh['patch']:
   for ch in c.get('effectChainList',[]):
    for effect in ch['effectList']:
     effect['thisUId']=str(uuid.uuid4())
     if effect.get('display')=='transform':
      effect['paramMapList']=[]
      for p in effect.get('paramList',[]):
       if p['name']in['Scale_x','Scale_y']:p['fxParam']['unValue']=100.
  newclips.append(c)
 video_track['clipList']=newclips
 removed_sounds=[]
 for tr in main['trackInfos']:
  old=tr['clipList'];tr['clipList']=[c for c in old if Path(c.get('filename','')).name not in ['ui_desbloqueio.wav','selo_ao.wav','caixas.wav']];removed_sounds.extend(c.get('filename')for c in old if c not in tr['clipList'])
 for r in data['resources']:
  name=Path(r['filename']).name;target=media/name
  if name.endswith('.mp4'):
   assert target.is_file();d=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(target)]));v=d['streams'][0];ticks=round(info['frames']/30*1e7);r.update(mediaLength=ticks,bitRate=int(d['format'].get('bit_rate',0)),audioStreamCount=0);r.pop('audStreamInfo',None);vr=r['vidStreamInfo'][0];vr.update(totalFrames=info['frames'],streamLength=ticks,bitRate=int(v.get('bit_rate',0)))
   for key in ['fileSize','fileLength']:
    if key in r:r[key]=target.stat().st_size
   path='ProjectFolder/Medias/{'+r['sourceUuid'].upper()+'}/media.json'
   if path in files:
    d=json.loads(files[path]);d['sourceInfo']={'basicInfo':{k:r[k]for k in ['streamType','fourCC','mediaLength','videoStreamCount','audioStreamCount','bitRate']if k in r},'vidStreamInfos':r.get('vidStreamInfo',[]),'audStreamInfos':[]};files[path]=json.dumps(d,separators=(',',':')).encode()
  else:shutil.copyfile(srcdir/'midias'/name,target)
 name=slug+'_R4_9x16';data['projectName']=name;files[tl]=json.dumps(data,ensure_ascii=False,separators=(',',':')).encode();meta=json.loads(files['ProjectFolder/project_info.json']);meta.update(project_file_name=name,proj_zip_save_path=name+'.wfp');files['ProjectFolder/project_info.json']=json.dumps(meta,separators=(',',':')).encode()
 wfp=dest/(name+'.wfp')
 with zipfile.ZipFile(wfp,'w',zipfile.ZIP_DEFLATED)as z:
  for n,b in files.items():z.writestr(n,b)
 if(srcdir/'fontes').exists():shutil.copytree(srcdir/'fontes',dest/'fontes',dirs_exist_ok=True)
 (dest/'LEIA_PRIMEIRO.txt').write_text('''REVISÃO R4 — SEM DERY EM PÉ

Extraia o ZIP inteiro e abra o projeto 9:16. As mídias ficam em midias/.
Todos os apresentadores em pé e os sets extras longos foram removidos.
A fala inteira permanece na faixa de voz; trilha e plops ficam separados.
Sons de caixas, carimbos e botões dos cenários retirados foram removidos.
O PSX fica no Dery/cenário. Gameplay, fotos e memes permanecem limpos.
Os títulos editáveis antigos de GTA/BMX foram preservados; não há legendas novas.

Se você já legendou/editou o seu WFP, substitua somente o vídeo-base de mesmo
nome em midias/ e remova os antigos SFX de caixas/carimbos/botões. Os pontos da
voz e a duração são iguais. Para os novos cortes/zooms, use este novo projeto.
O projeto 16:9 completo continua reservado ao fim da série.

Filmora não foi executado no Linux. Estrutura, recursos, velocidade e duração
foram conferidos; a abertura nativa fica na instalação do usuário.
''')
 bundle=out/(slug+'_R4_Filmora.zip')
 with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED,allowZip64=True)as z:
  for f in dest.rglob('*'):
   if f.is_file():z.write(f,str(f.relative_to(dest)),compress_type=zipfile.ZIP_STORED if f.suffix in ['.mp4','.ttf']else zipfile.ZIP_DEFLATED)
 assert zipfile.ZipFile(bundle).testzip()is None;assert hashlib.sha256(source.read_bytes()).hexdigest()==source_sha
 (out/'filmora.json').write_text(json.dumps(dict(source_project=str(source),source_unchanged=True,project=wfp.name,video_clips=len(newclips),removed_prop_sfx=removed_sounds,resources=len(data['resources']),all_media_bundled=True,only_9x16=True,filmora_native_open=False),ensure_ascii=False,indent=2)+'\n');print('R4_PACKAGED',project.name,flush=True)
