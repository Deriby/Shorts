"""Check native root registration, independently of edit/media timing checks."""
import zipfile,json,base64
ROOT='{204E72A3-B517-44d4-806F-9E9D84D5F904}'
def validar(path,strict=False):
 with zipfile.ZipFile(path)as z:
  assert z.testzip()is None
  tl=json.loads(z.read(f'ProjectFolder/Medias/{ROOT}/timeline.wesproj'));lib=json.loads(z.read('ProjectFolder/Medias/medias_info.json'));meta=json.loads(z.read('ProjectFolder/project_info.json'))
  assert ROOT in lib['media_items'],'Timeline principal sem registro na biblioteca'
  assert f'ProjectFolder/Medias/{ROOT}/extra.json'in z.namelist(),'Falta extra.json da timeline principal'
  extra=json.loads(z.read(f'ProjectFolder/Medias/{ROOT}/extra.json'));main=next(t for t in tl['timelineInfos']if t['timelineId']==tl['currentTimelineId']);item=lib['media_items'][ROOT]
  uuid=next(base64.b64decode(u['data']).decode().rstrip('\0')for u in main['userData']if u['key']==11000)
  assert item['timeline_uuid']==uuid and item['media_type']==1048576;assert item['duration']==meta['project_timeline_duration'];assert meta['timeline_mediaId']==ROOT
  bindings=0
  if strict:
   for tr in main['trackInfos']:
    for c in tr['clipList']:
     ud={u['key']:base64.b64decode(u['data']).decode().rstrip('\0')for u in c['userData']if u['key']in[3,10]};assert ud[10]in lib['media_items'];assert extra['mediaClipsMapInfo'][ud[3]]['mediaId']==ud[10];cache=json.loads(z.read(f"ProjectFolder/Medias/{ud[10]}/media.json"));assert 'recordInfos'in cache['sourceInfo'];bindings+=1
  return dict(root_registered=True,extra_present=True,timeline_uuid_matches=True,duration_matches=True,media_bindings=bindings)
