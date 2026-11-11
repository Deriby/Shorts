"""Label and arrange the rendered Blender views, without retouching them."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

ROOT = Path(__file__).resolve().parent
entries = json.loads((ROOT / 'expressoes.json').read_text())['expressions'][1:]
fig, axes = plt.subplots(5, 2, figsize=(8, 20), dpi=128, facecolor='#282b30')
for axis, entry in zip(axes.ravel(), entries):
    axis.imshow(mpimg.imread(ROOT / 'previas' / f"{entry['id']:02d}_{entry['slug']}.png"), interpolation='nearest')
    axis.axis('off'); axis.set_title(f"{entry['id']:02d} · {entry['label']}", color='white', fontsize=15, pad=9)
fig.subplots_adjust(left=.015, right=.985, top=.975, bottom=.008, wspace=.025, hspace=.12)
fig.savefig(ROOT / '10_Expressoes_no_Modelo.png', facecolor=fig.get_facecolor())
