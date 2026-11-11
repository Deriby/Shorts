"""Format conversion only: split generated cells and pack a nearest-sampled atlas."""
from pathlib import Path
from PIL import Image
import json
import numpy as np

ROOT = Path(__file__).resolve().parent
data = json.loads((ROOT / 'expressoes.json').read_text())
sheet = Image.open(ROOT / 'Folha_Fonte.png').convert('RGBA')
target = ROOT / 'png'; target.mkdir(exist_ok=True)
neutral = Image.open(ROOT.parent / 'texturas/rosto_neutro_v3/Rosto_Neutro_128.png').convert('RGBA')
neutral.save(target / '00_neutro.png')
atlas = Image.new('RGBA', (512, 384))
for index in range(12):
    if 1 <= index <= 10:
        cell = index - 1
        x, y = cell % 4, cell // 4
        bounds = (round(x * sheet.width / 4), round(y * sheet.height / 3),
                  round((x + 1) * sheet.width / 4), round((y + 1) * sheet.height / 3))
        image = sheet.crop(bounds).resize((128, 128), Image.Resampling.NEAREST)
        # Native PS1 RGB555 color precision, matching the existing face asset.
        pixels = np.array(image)
        pixels[:, :, :3] = np.rint(np.rint(pixels[:, :, :3].astype(float) / 255 * 31) / 31 * 255).astype('uint8')
        image = Image.fromarray(pixels)
        item = data['expressions'][index]
        image.save(ROOT / item['file'])
    else:
        image = neutral
    atlas.paste(image, ((index % 4) * 128, (index // 4) * 128))
atlas.save(ROOT / 'Atlas_Expressoes_4x3.png')
print('10 generated expressions + original neutral packed at 128px per cell.')
