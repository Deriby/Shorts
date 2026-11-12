"""Meaningful content checks on the PNG library and original preservation."""
from pathlib import Path
import hashlib,json
from collections import Counter
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parent
data=json.loads((ROOT/'expressions.json').read_text())
entries=data['expressions'];old=json.loads((ROOT.parent/'v2/expressions.json').read_text())['expressions']
assert [e['id'] for e in entries]==list(range(131))
assert sum(e['new'] for e in entries)==100
assert len({e['name'] for e in entries})==131
atlas=Image.open(ROOT/'atlas_131_16x9.png').convert('RGB')
assert atlas.size==(2048,1152)
pixels=[]
for e in entries:
    path=ROOT/e['file'];tile=Image.open(path).convert('RGB');i=e['id']
    assert tile.size==(128,128)
    assert hashlib.sha256(path.read_bytes()).hexdigest()==e['sha256']
    assert np.array_equal(np.array(tile),np.array(atlas.crop((i%16*128,i//16*128,(i%16+1)*128,(i//16+1)*128))))
    pixels.append(hashlib.sha256(tile.tobytes()).hexdigest())
assert len(set(pixels[31:]))==100, 'Duplicate new artwork'
for e in old:
    assert (ROOT.parent/'v2'/e['file']).read_bytes()==(ROOT/entries[e['id']]['file']).read_bytes()
families=json.loads((ROOT/'fala_familias.json').read_text())
assert len(families)==5 and all(len(v)==10 for v in families.values())
assert set(i for v in families.values() for i in v.values())==set(range(31,81))
model_hash=hashlib.sha256((ROOT.parents[1]/'roupas/camiseta_preta/Dery_Camiseta_Preta.blend').read_bytes()).hexdigest()
assert model_hash=='b0091d85f0e44f30d242ec78a9b191379e2af14d00c551d1fd8060dcdb5cce6a'
cache=Path('/workspace/attachments/dery100')
assert all((cache/f'model_{i:03d}.png').exists() for i in range(31,131))
render_hashes=[hashlib.sha256(Image.open(cache/f'model_{i:03d}.png').tobytes()).hexdigest() for i in range(31,131)]
assert len(set(render_hashes))==100, 'Two face IDs rendered identically'
source=np.array(Image.open(cache/'original_002.png')).astype(int)
extended=np.array(Image.open(cache/'check_002.png')).astype(int)
delta=np.max(np.abs(source[:,:,:3]-extended[:,:,:3]),axis=2)
assert delta.max()<=6 and (delta>0).sum()<100, 'Old smile rendering changed materially'
report=json.loads((ROOT/'validacao.json').read_text())
report.update(png_validation=True,unique_new_artwork=100,unique_model_renders=100,
              all_atlas_cells_match=True,original_pngs_byte_identical=True,
              categories=dict(Counter(e['category'] for e in entries)),
              old_smile_render_regression=dict(changed_pixels=int((delta>0).sum()),
                max_rgb_difference=int(delta.max()),note='Only minor floating point atlas sampling differences allowed.'))
(ROOT/'validacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
