"""Archive the user-provided public meme pack and index it for future edits."""
from pathlib import Path
import urllib.request,urllib.parse,urllib.error,re,json,hashlib,sqlite3,time,shutil
from concurrent.futures import ThreadPoolExecutor,as_completed
from html.parser import HTMLParser
P=Path(__file__).resolve().parent;C=Path('/workspace/attachments/memes009');A=P/'arquivos';A.mkdir(exist_ok=True)
FOLDERS={'audio':'1uvOg6VDT3VezRZHiLM6nDZlJfgJLUNwc','image':'1BiAq9vJ_-Ypx72L32tppE5DKsCqV33ZI','video':'1Sfat7nfaDMpCR2xVx8m_HgtSs90Xafpg'}
class Form(HTMLParser):
 def __init__(self):super().__init__();self.fields={}
 def handle_starttag(self,t,a):
  a=dict(a)
  if t=='input'and a.get('type')=='hidden':self.fields[a['name']]=a['value']
headers={'Referer':'https://drive.google.com/','Origin':'https://drive.google.com','User-Agent':'Mozilla/5.0'}
s=(C/'folder.html').read_text();keys=list(dict.fromkeys(re.findall(r'AIza[0-9A-Za-z_-]{30,}',s)));key=keys[int((C/'api_key_index').read_text())]
items=[]
for kind,ident in FOLDERS.items():
 page=''
 while True:
  q=dict(key=key,q=f"'{ident}' in parents and trashed = false",maxResults=1000,fields='items(id,title,mimeType,fileSize,md5Checksum),nextPageToken')
  if page:q['pageToken']=page
  with urllib.request.urlopen(urllib.request.Request('https://clients6.google.com/drive/v2beta/files?'+urllib.parse.urlencode(q),headers=headers),timeout=35)as r:d=json.load(r)
  for x in d.get('items',[]):
   items.append(dict(id=x['id'],name=x['title'],mime=x['mimeType'],expected_bytes=int(x.get('fileSize',0)),source_md5=x.get('md5Checksum'),category=kind,parent=ident,source='https://drive.google.com/file/d/'+x['id']+'/view'))
  page=d.get('nextPageToken')
  if not page:break
 print('LISTED',kind,len([x for x in items if x['category']==kind]),flush=True)
# Preserve the thumbnail labels already inspected in the previous turn.
old=json.loads((C/'catalogo.json').read_text());tags={x['id']:x['tag']for x in old}
for kind,prefix in [('image','I'),('video','V'),('audio','A')]:
 n=50 if kind!='audio'else 0
 for x in [x for x in items if x['category']==kind]:
  if x['id']not in tags:tags[x['id']]=f'{prefix}{n:02d}';n+=1
for x in items:
 ext=Path(x['name']).suffix.lower();x['tag']=tags[x['id']];x['relative_file']='arquivos/'+x['id']+ext
manifest=P/'catalogo.json';manifest.write_text(json.dumps(dict(source_folder='https://drive.google.com/drive/folders/1TyzZ9JY1sLPyZBetqwwRDADzsqpLHRX6',complete_listing=True,items=items),ensure_ascii=False,indent=2))
def download(x):
 dest=P/x['relative_file']
 for attempt in range(3):
  try:
   if not dest.exists()or dest.stat().st_size!=x['expected_bytes']:
    url='https://drive.usercontent.google.com/download?'+urllib.parse.urlencode({'id':x['id'],'export':'download'})
    for step in range(2):
     with urllib.request.urlopen(url,timeout=45)as r:
      if 'text/html'in r.headers.get('Content-Type',''):
       f=Form();f.feed(r.read().decode());assert f.fields.get('id')==x['id'],'No public download form';url='https://drive.usercontent.google.com/download?'+urllib.parse.urlencode(f.fields);continue
      tmp=dest.with_suffix(dest.suffix+'.part')
      with tmp.open('wb')as w:shutil.copyfileobj(r,w,1024*1024)
      tmp.replace(dest);break
   assert dest.exists() and (not x['expected_bytes']or dest.stat().st_size==x['expected_bytes'])
   b=dest.read_bytes();assert not x['source_md5']or hashlib.md5(b).hexdigest()==x['source_md5']
   x.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),downloaded=True)
   return x
  except Exception as e:
   x['error']=str(e)
   if attempt<2:time.sleep(1)
 return x
with ThreadPoolExecutor(max_workers=6)as pool:
 for n,x in enumerate(pool.map(download,items),1):
  if n%20==0:print('ARCHIVED',n,'of',len(items),flush=True);manifest.write_text(json.dumps(dict(source_folder='https://drive.google.com/drive/folders/1TyzZ9JY1sLPyZBetqwwRDADzsqpLHRX6',complete_listing=True,items=items),ensure_ascii=False,indent=2))
manifest.write_text(json.dumps(dict(source_folder='https://drive.google.com/drive/folders/1TyzZ9JY1sLPyZBetqwwRDADzsqpLHRX6',complete_listing=True,items=items),ensure_ascii=False,indent=2))
db=sqlite3.connect(P/'catalogo.sqlite3');db.execute('CREATE TABLE IF NOT EXISTS assets(id TEXT PRIMARY KEY, tag TEXT, name TEXT, category TEXT, mime TEXT, relative_file TEXT, bytes INTEGER, sha256 TEXT, source TEXT, tags TEXT, review_status TEXT)')
for x in items:db.execute('INSERT OR REPLACE INTO assets VALUES(?,?,?,?,?,?,?,?,?,?,?)',(x['id'],x['tag'],x['name'],x['category'],x['mime'],x['relative_file'],x.get('bytes',0),x.get('sha256'),x['source'],'','not_reviewed'))
db.commit();db.close();print('ARCHIVE_DONE',len(items),sum(x.get('bytes',0)for x in items),sum(not x.get('downloaded')for x in items),flush=True)
