"""Decode the selected CRT movie once to avoid repeated H.264 seeks in Blender."""
from pathlib import Path
import json,hashlib,subprocess
P=Path(__file__).resolve().parent;info=json.loads((P/'timeline.json').read_text());C=Path(info['cache']);C.mkdir(parents=True,exist_ok=True)
movie=P/info['monitor_file'];fingerprint=hashlib.sha256(movie.read_bytes()).hexdigest();stamp=C/'crt_cache.json'
valid=stamp.exists()and json.loads(stamp.read_text()).get('movie_sha256')==fingerprint
if not valid or not all((C/f'crt_{f:04d}.png').is_file()for f in range(1,info['frames']+1)):
 subprocess.run(['ffmpeg','-v','error','-y','-threads','1','-i',str(movie),'-threads','1','-compression_level','1',str(C/'crt_%04d.png')],check=True)
assert all((C/f'crt_{f:04d}.png').is_file()for f in range(1,info['frames']+1))
stamp.write_text(json.dumps(dict(movie_sha256=fingerprint,frames=info['frames'],source=info['monitor_file'],fps=info['fps']),indent=2)+'\n')
print('CRT_CACHE_READY',info['frames'],flush=True)
