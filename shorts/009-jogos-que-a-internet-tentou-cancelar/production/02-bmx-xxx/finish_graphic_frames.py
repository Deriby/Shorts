"""Fill held platform-card frames after both actual-render workers finish."""
from pathlib import Path
import json,os,hashlib
P=Path(__file__).resolve().parent;info=json.loads((P/'timeline.json').read_text());C=Path(info['cache'])/'frames'
assert(C/'source.sha256').read_text().strip()==hashlib.sha256((P/'output/Dery_BMX_XXX.blend').read_bytes()+(P/info['monitor_file']).read_bytes()).hexdigest()
filled=0
for sh in info['shots']:
 if sh['kind']!='archive':continue
 for f in range(sh['start'],sh['end']+1):
  if(f-sh['start'])%3:
   source=C/f"frame_{f-(f-sh['start'])%3:04d}.png";dest=C/f'frame_{f:04d}.png';assert source.is_file()
   if not dest.exists():os.link(source,dest);filled+=1
missing=[f for sh in info['shots']if sh['kind']not in['game','photo']for f in range(sh['start'],sh['end']+1)if not(C/f'frame_{f:04d}.png').is_file()]
assert not missing,missing[:10]
print('GRAPHIC_HOLDS_READY',filled)
