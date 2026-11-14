"""Restore native Filmora library/root registration using a user-opened WFP."""
from pathlib import Path
import json,zipfile,uuid,base64,copy,hashlib,struct,argparse
P=Path(__file__).resolve().parent;R=next(p for p in P.parents if(p/'AGENTS.md').exists());F=P/'output/Filmora';ROOT='{204E72A3-B517-44d4-806F-9E9D84D5F904}';TL=f'ProjectFolder/Medias/{ROOT}/timeline.wesproj';LIB='ProjectFolder/Medias/medias_info.json';EXTRA=f'ProjectFolder/Medias/{ROOT}/extra.json'
SOURCE=F/'Jogos_Que_A_Internet_Tentou_Cancelar_COMPLETO_16x9.wfp';GOOD=R/'shorts/008-personagens-que-a-internet-estragou/production/20-edicao-final-usuario/Massacote_EDICAO_FINAL_USUARIO.wfp';OUT=F/'Massacote_Completo.wfp'
def guid():return '{'+str(uuid.uuid4()).upper()+'}'
def dump(x):return json.dumps(x,ensure_ascii=False,separators=(',',':')).encode()
def decode(u):return base64.b64decode(u['data']).decode().rstrip('\0')
def setdata(u,value):
 raw=value.encode();raw+=b'\0'*max(0,u['size']-len(raw));u.update(data=base64.b64encode(raw).decode(),size=len(raw))
def load(path):
 with zipfile.ZipFile(path)as z:assert z.testzip()is None;return {n:z.read(n)for n in z.namelist()}
old=load(SOURCE);native=load(GOOD);data=json.loads(old[TL]);good_data=json.loads(native[TL]);library=json.loads(old[LIB]);native_library=json.loads(native[LIB]);native_extra=json.loads(native[EXTRA]);before=copy.deepcopy(data);meta=json.loads(old['ProjectFolder/project_info.json']);main=next(t for t in data['timelineInfos']if t['timelineId']==data['currentTimelineId']);tid=main['timelineId'];duration=max(c['tlEnd']for tr in main['trackInfos']for c in tr['clipList']);timeline_uuid=guid()
# Native media IDs are library entries, distinct from decoder source UUIDs.
media_ids={r['sourceUuid']:guid()for r in data['resources']};resources={r['sourceUuid']:r for r in data['resources']};extra=copy.deepcopy(native_extra)
for key in ['usedTemplateResInfo','mediaClipsMapInfo','pendingMarkersInfo','highlightInfo']:extra[key]={}
extra['allMarkersInfo']={'beatDetectInfo':{}};extra['fontNameInfo']=[];extra['usedBizFont']=[];extra['TextSentence']={'TextSentence':[]}
for u in main['userData']:
 if u['key']==11000:setdata(u,timeline_uuid)
 if u['key']==50:setdata(u,'Massacote — Completo 16:9')
for tr in main['trackInfos']:
 for c in tr['clipList']:
  r=resources[c['sourceUuid']];mid=media_ids[r['sourceUuid']];ud={u['key']:u for u in c['userData']}
  if 10 not in ud:
   c['userData'].append(dict(key=10,size=38,data=''));ud[10]=c['userData'][-1]
  setdata(ud[10],mid);assert 3 in ud
  extra['mediaClipsMapInfo'][decode(ud[3])]=dict(mediaId=mid,subClips={})
items={};entries={n:b for n,b in old.items()if not n.startswith('ProjectFolder/Medias/')};root_item=copy.deepcopy(native_library['media_items'][ROOT]);root_item.update(name='Massacote — Completo 16:9',id=ROOT,timeline_uuid=timeline_uuid,duration=duration);items[ROOT]=root_item
# Preserve every root field actually serialized by the working native file.
for r in data['resources']:
 mid=media_ids[r['sourceUuid']];filename=Path(r['filename']).name;path=F/'midias'/filename;assert path.is_file();kind=16 if r['streamType']==5 else 8 if r['videoStreamCount']else 4
 prototype=next(x for x in native_library['media_items'].values()if x.get('media_type')==kind)
 item=copy.deepcopy(prototype);item.update(name=path.stem,id=mid,download_url='./midias/'+filename,media_type=kind,media_length=50000000 if kind==16 else r['mediaLength'],stream_idx=-1 if kind==16 else 0,src_md5=hashlib.md5(path.read_bytes()).hexdigest(),mark_info_list=[dict(mark_in=-1,mark_out=-1)],scence_info=[]);items[mid]=item
 basic={k:r[k]for k in ['streamType','fourCC','mediaLength','programCount','videoStreamCount','audioStreamCount','subPicStreamCount','bitRate','createDate']if k in r};basic.setdefault('programCount',0);basic.setdefault('subPicStreamCount',0);basic.setdefault('createDate',-1)
 video=copy.deepcopy(r.get('vidStreamInfo',[]))
 for stream in video:stream.setdefault('premultiAlphaTypePhoto',-1);stream.setdefault('lastframeRate',copy.deepcopy(stream['frameRate']))
 info=dict(version='1.1.5',file_name='./midias/'+filename,sourceInfo=dict(basicInfo=basic,vidStreamInfos=video,audStreamInfos=copy.deepcopy(r.get('audStreamInfo',[])),recordInfos={}))
 entries[f'ProjectFolder/Medias/{mid}/media.json']=dump(info)
entries[TL]=dump(data);entries[EXTRA]=dump(extra);entries[LIB]=('{"media_structure":{"Folder":{'+','.join('"media_item":'+json.dumps(mid)for mid in media_ids.values())+'},"media_item":'+json.dumps(ROOT)+'},"media_items":'+json.dumps(items,ensure_ascii=False,separators=(',',':'))+'}').encode()
meta.update(project_file_name='Massacote_Completo',proj_zip_save_path='Massacote_Completo.wfp',project_guid=guid(),project_timeline_duration=duration,project_current_position=0,project_custom_cover=False,proj_cover_proj_path='');entries['ProjectFolder/project_info.json']=dump(meta)
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_STORED)as z:
 for name,blob in entries.items():z.writestr(name,blob)
# A/B contract: the delivered broken WFP fails; the real native reference and
# repaired container must pass root/library/cache consistency checks.
def contract(files):
 assert EXTRA in files,'Missing native root extra.json'
 d=json.loads(files[TL]);lib=json.loads(files[LIB]);e=json.loads(files[EXTRA]);m=next(t for t in d['timelineInfos']if t['timelineId']==d['currentTimelineId']);root_item=lib['media_items'][ROOT];uid=next(decode(u)for u in m['userData']if u['key']==11000);assert root_item['media_type']==1048576 and root_item['timeline_uuid']==uid
 assert set(native_extra)<=set(e);assert root_item['duration']==json.loads(files['ProjectFolder/project_info.json'])['project_timeline_duration']
 return d,lib,e
contract(native)
try:contract(old)
except(AssertionError,KeyError):pass
else:raise AssertionError('Expected broken deliverable to fail the native contract')
fixed=load(OUT);d,lib,e=contract(fixed);assert len(d['resources'])==len(before['resources'])==97;assert d['resources']==before['resources'];count=0
for oldtr,newtr in zip(before['timelineInfos'][0]['trackInfos'],d['timelineInfos'][0]['trackInfos']):
 for oldc,newc in zip(oldtr['clipList'],newtr['clipList']):
  oc=copy.deepcopy(oldc);nc=copy.deepcopy(newc);oc['userData']=[u for u in oc['userData']if u['key']!=10];nc['userData']=[u for u in nc['userData']if u['key']!=10];assert oc==nc,'Edit changed while repairing registration';count+=1
  ud={u['key']:u for u in newc['userData']};mid=decode(ud[10]);assert mid in lib['media_items'];assert e['mediaClipsMapInfo'][decode(ud[3])]['mediaId']==mid;cache=json.loads(fixed[f'ProjectFolder/Medias/{mid}/media.json']);assert(F/cache['file_name'].removeprefix('./')).is_file();assert struct.unpack('<i',base64.b64decode(ud[6]['data']))[0]==tid
assert count==296 and len(e['mediaClipsMapInfo'])==count
result=dict(source=SOURCE.name,source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),reference=str(GOOD.relative_to(R)),reference_sha256=hashlib.sha256(GOOD.read_bytes()).hexdigest(),repaired=OUT.name,repaired_sha256=hashlib.sha256(OUT.read_bytes()).hexdigest(),root_library_registration_restored=True,root_extra_restored=True,independent_library_media_ids=True,native_media_caches_restored=True,compression='ZIP_STORED as in user-saved WFP',new_project_guid=True,all_296_edits_unchanged_except_library_binding=True,all_97_resources_unchanged=True,source_files_unchanged=True,working_reference_passes=True,broken_delivery_rejected=True,repaired_contract_passes=True,filmora_native_open=False)
(P/'output/reparo_abertura.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('WFP_REGISTRATION_REPAIRED',OUT.name,OUT.stat().st_size,flush=True)

report_path=P/'projeto.json'
report=json.loads(report_path.read_text());report['project_before_open_repair']=SOURCE.name;report['project']=OUT.name;report['native_root_registration_repaired']=True;report['native_root_extra_restored']=True;report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
