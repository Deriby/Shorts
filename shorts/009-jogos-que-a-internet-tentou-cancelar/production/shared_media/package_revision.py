"""Keep the delivered Filmora edit; replace its silent base and bundle its media."""
from pathlib import Path
import sys,json,zipfile,shutil,subprocess,hashlib
P=Path(sys.argv[1]).resolve()
plans={
 '01-gta-san-andreas':('GTA_San_Andreas','Filmora_R2','GTA_San_Andreas_R2_9x16.wfp'),
 '02-bmx-xxx':('BMX_XXX','Filmora','BMX_XXX_9x16.wfp'),
 '03-bully':('Bully','Filmora','Bully_9x16.wfp')}
slug,source_folder,source_name=plans[P.name];OUT=P/'output/R3_Midias_Limpas';DEST=OUT/'Filmora';MEDIA=DEST/'midias';MEDIA.mkdir(parents=True,exist_ok=True)
source=P/'output'/source_folder/source_name;source_sha=hashlib.sha256(source.read_bytes()).hexdigest()
with zipfile.ZipFile(source)as z:files={n:z.read(n)for n in z.namelist()}
tl=next(n for n in files if n.endswith('timeline.wesproj'));data=json.loads(files[tl]);info=json.loads((P/'timeline.json').read_text());video_resources=[]
for r in data['resources']:
 name=Path(r['filename']).name;dst=MEDIA/name
 if name.lower().endswith('.mp4'):
  assert dst.is_file();probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(dst)]));v=probe['streams'][0];num,den=map(int,v['r_frame_rate'].split('/'));duration=int(v['nb_frames'])*den/num;length=round(duration*1e7)
  r.update(mediaLength=length,bitRate=int(probe['format'].get('bit_rate',0)),audioStreamCount=0,videoStreamCount=1);r.pop('audStreamInfo',None)
  vr=r['vidStreamInfo'][0];vr.update(width=v['width'],height=v['height'],frameRate={'num':num,'den':den},maxFrameRate={'num':num,'den':den},totalFrames=int(v['nb_frames']),streamLength=length,bitRate=int(v.get('bit_rate',0)))
  for key in['fileSize','fileLength']:
   if key in r:r[key]=dst.stat().st_size
  video_resources.append(r['sourceUuid'])
 else:
  choices=[P/'assets/voz'/name,P/'assets/audio'/name,P/'output'/source_folder/'midias'/name]
  src=next((p for p in choices if p.is_file()and p.stat().st_size>200),None);assert src,name;shutil.copyfile(src,dst)
 # Update the matching typed library descriptor, preserving identifiers and paths.
 mid='{'+r['sourceUuid'].upper()+'}';path=f'ProjectFolder/Medias/{mid}/media.json'
 if path in files:
  media=json.loads(files[path]);media['sourceInfo']={'basicInfo':{k:r[k]for k in['streamType','fourCC','mediaLength','videoStreamCount','audioStreamCount','bitRate']if k in r},'vidStreamInfos':r.get('vidStreamInfo',[]),'audStreamInfos':r.get('audStreamInfo',[])};files[path]=json.dumps(media,separators=(',',':')).encode()
assert len(video_resources)==1
project_name=slug+'_Midias_Limpas_9x16';data['projectName']=project_name;files[tl]=json.dumps(data,ensure_ascii=False,separators=(',',':')).encode()
meta=json.loads(files['ProjectFolder/project_info.json']);meta.update(project_file_name=project_name,proj_zip_save_path=project_name+'.wfp');files['ProjectFolder/project_info.json']=json.dumps(meta,separators=(',',':')).encode()
project=DEST/(project_name+'.wfp')
with zipfile.ZipFile(project,'w',zipfile.ZIP_DEFLATED)as z:
 for name,content in files.items():z.writestr(name,content)
font_source=P/'output'/source_folder/'fontes'
if font_source.is_dir():shutil.copytree(font_source,DEST/'fontes',dirs_exist_ok=True)
(DEST/'LEIA_PRIMEIRO.txt').write_text('''REVISÃO — MÍDIAS LIMPAS

Extraia o ZIP inteiro e abra o WFP 9:16. Todas as suas mídias estão em midias/.
Esta revisão preserva a edição anterior e troca apenas o vídeo-base para manter
fotos, memes e gameplay limpos, inclusive dentro do CRT. O visual PSX fica na animação.
Os títulos editáveis das entregas antigas continuam nas faixas originais; não
foram acrescentadas legendas novas. A voz, trilha e sons permanecem separados.

Se você já editou/legendou seu projeto, preserve esse WFP e substitua somente
o vídeo-base pelo arquivo de mesmo nome em midias/. Assim mantém suas alterações.
Os projetos anteriores e a animação original não foram sobrescritos.

Filmora não foi executado neste ambiente. Estrutura, recursos, duração e velocidade
são verificados por código; confira abertura/reprodução na sua instalação.
''')
bundle=OUT/(slug+'_Filmora_Midias_Limpas.zip')
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED,allowZip64=True)as z:
 for f in DEST.rglob('*'):
  if f.is_file():z.write(f,str(f.relative_to(DEST)),compress_type=zipfile.ZIP_STORED if f.suffix in['.mp4','.ttf']else zipfile.ZIP_DEFLATED)
assert zipfile.ZipFile(bundle).testzip()is None;assert hashlib.sha256(source.read_bytes()).hexdigest()==source_sha
projection=Path('/workspace/attachments/clean_media')/P.name/'screen_projection.json';shutil.copyfile(projection,OUT/'projecao_monitor.json')
(OUT/'filmora.json').write_text(json.dumps(dict(source_project=str(source.relative_to(P)),source_sha256=source_sha,source_unchanged=True,project=str(project.relative_to(OUT)),resources=len(data['resources']),editing_preserved=True,video_base_replaced=True,formats=['9:16'],all_media_bundled=True,native_open_test=False,bundle=bundle.name),ensure_ascii=False,indent=2)+'\n')
print('REVISION_PACKAGE_READY',P.name,bundle.stat().st_size,flush=True)
