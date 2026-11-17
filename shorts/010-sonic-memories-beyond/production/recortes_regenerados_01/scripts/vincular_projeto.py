"""Religa somente as peças regeneradas, preservando a edição nativa do usuário."""
from pathlib import Path
import json,re,zipfile,hashlib,uuid,io,copy
from PIL import Image,ImageOps
P=Path(__file__).resolve().parents[1]
SRC=P.parent/'edicao_usuario_01/recebido/Massacote_Tube_Sonic_EDITADO_USUARIO.wfp'
F=P/'output/Filmora';M=F/'midias_regeneradas';OUT=F/'Massacote_Tube_Sonic_Pecas_Regeneradas.wfp'
EXPECTED='bf145baeebb2087f05023716b7d9f5b351a4fcbda949715a1f000061e427d9c3'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SRC)==EXPECTED
pngs={p.stem.removesuffix('_R3')+'.png':p for p in M.glob('*.png')}
assert len(pngs)==15
token=re.compile(r'"(?:\\.|[^"\\])*"')
md5={};old_md5={};new_md5={};thumbs={};changed_paths={}
with zipfile.ZipFile(SRC)as z:
    assert z.testzip()is None
    infos=z.infolist();raw={i.filename:z.read(i.filename)for i in infos}
library=json.loads(raw['ProjectFolder/Medias/medias_info.json'])
for item in library['media_items'].values():
    basename=Path(item.get('download_url','')).name
    if basename not in pngs:continue
    p=pngs[basename];new=hashlib.md5(p.read_bytes()).hexdigest()
    if item.get('src_md5'):
        md5[item['src_md5']]=new;old_md5[item['src_md5']]=basename;new_md5[new]=basename
    thumbs['ProjectFolder/Medias/'+item['id']+'/thumbnail.png']=p

def rewrite(text):
    def value(match):
        original=json.loads(match.group(0));new=original
        if original in md5:new=md5[original]
        elif not original.startswith(('{','[')):
            basename=Path(original).name
            if basename in pngs:
                p=pngs[basename]
                if original==basename:new=p.name
                else:new=('file:'if original.startswith('file:')else'')+'./midias_regeneradas/'+p.name
                changed_paths[original]=new
        return json.dumps(new,ensure_ascii=False)if new!=original else match.group(0)
    return token.sub(value,text)

files=dict(raw)
changed_json=[]
for name,data in raw.items():
    if not name.endswith(('.json','.wesproj')):continue
    text=data.decode('utf-8-sig');new=rewrite(text)
    if new!=text:files[name]=new.encode('utf-8');changed_json.append(name)

name='ProjectFolder/project_info.json';meta=json.loads(files[name]);oldmeta=copy.deepcopy(meta)
meta.update(project_file_name=OUT.stem,proj_zip_save_path=OUT.name,project_guid='{'+str(uuid.uuid4()).upper()+'}')
files[name]=json.dumps(meta,ensure_ascii=False,separators=(',',':')).encode()
for name,path in thumbs.items():
    if name not in raw:continue
    size=Image.open(io.BytesIO(raw[name])).size
    image=Image.open(path).convert('RGBA');image=ImageOps.contain(image,size,Image.Resampling.LANCZOS)
    canvas=Image.new('RGBA',size);canvas.alpha_composite(image,((size[0]-image.width)//2,(size[1]-image.height)//2));buf=io.BytesIO();canvas.save(buf,format='PNG');files[name]=buf.getvalue()

# Compare every timeline and nested composition, ignoring only image links/hashes.
# This also catches accidental changes to times, keyframes, effects or clip IDs.
reverse={p.name:k for k,p in pngs.items()}
def normalize(obj):
    if isinstance(obj,dict):return {k:normalize(v)for k,v in obj.items()}
    if isinstance(obj,list):return [normalize(v)for v in obj]
    if isinstance(obj,str):
        if obj in old_md5:return 'IMAGE_HASH:'+old_md5[obj]
        if obj in new_md5:return 'IMAGE_HASH:'+new_md5[obj]
        base=Path(obj).name
        if base in pngs:return 'IMAGE:'+base
        if base in reverse:return 'IMAGE:'+reverse[base]
    return obj
timelines=[]
for name in raw:
    if not name.endswith('.wesproj'):continue
    assert normalize(json.loads(raw[name]))==normalize(json.loads(files[name])),name
    timelines.append(name)
assert set(files)==set(raw)
with zipfile.ZipFile(OUT,'w')as z:
    for info in infos:z.writestr(info,files[info.filename])
with zipfile.ZipFile(OUT)as z:assert z.testzip()is None
assert sha(SRC)==EXPECTED
root=json.loads(raw['ProjectFolder/Medias/{204E72A3-B517-44d4-806F-9E9D84D5F904}/timeline.wesproj'])
main=next(t for t in root['timelineInfos']if t['timelineId']==root['currentTimelineId'])
report=dict(source_sha256=EXPECTED,source_file_unchanged=True,project=OUT.name,sha256=sha(OUT),
    timeline_documents_verified=len(timelines),all_timelines_semantically_unchanged_except_image_links=True,
    main_clips_preserved=sum(len(t['clipList'])for t in main['trackInfos']),
    main_tracks_preserved=len(main['trackInfos']),duration_ticks_preserved=meta['project_timeline_duration'],
    cuts_keyframes_effects_audio_and_compositions_preserved=True,
    png_files=len(pngs),new_filenames=True,new_image_hashes=True,thumbnails_updated=len(thumbs),
    untouched_media_paths_preserved=True,native_filmora_executed=False,
    files={k:dict(file=v.name,sha256=sha(v))for k,v in pngs.items()})
(P/'validacao_projeto.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items()if k!='files'},ensure_ascii=False,indent=2),flush=True)
