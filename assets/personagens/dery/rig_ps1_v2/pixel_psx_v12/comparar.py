"""Technical layouts of unchanged Blender render frames for face sampling review."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
ROOT = Path(__file__).resolve().parent
cases = [(0, 'Neutro'), (2, 'Risada'), (3, 'Surpresa')]
fig, axes = plt.subplots(3, 2, figsize=(10, 15.2), dpi=128, facecolor='#282b30')
for row, (index, name) in enumerate(cases):
    for col, stage in enumerate(['Antes', 'Depois']):
        axes[row, col].imshow(mpimg.imread(ROOT / f'{stage}_{index:02d}_{name}.png'), interpolation='nearest')
        axes[row, col].axis('off')
        if row == 0:
            axes[row, col].set_title('Anterior · 128' if col == 0 else 'Grade PSX · 64', color='white', fontsize=16, pad=12)
fig.subplots_adjust(left=.012, right=.988, top=.968, bottom=.008, wspace=.012, hspace=.018)
fig.savefig(ROOT / 'Comparativo_Pixels.png', facecolor=fig.get_facecolor()); plt.close(fig)
fig, axes = plt.subplots(2, 2, figsize=(8, 8.5), dpi=128, facecolor='#282b30')
for axis, (index, name) in zip(axes.ravel(), cases + [(4, 'Raiva')]):
    axis.imshow(mpimg.imread(ROOT / f'Depois_{index:02d}_{name}.png'), interpolation='nearest')
    axis.axis('off'); axis.set_title(name, color='white', fontsize=16, pad=10)
fig.subplots_adjust(left=.012, right=.988, top=.945, bottom=.008, wspace=.012, hspace=.09)
fig.savefig(ROOT / 'Previa_Rostos_PSX.png', facecolor=fig.get_facecolor())
plt.close(fig)
fig, axes = plt.subplots(1, 2, figsize=(10, 5.4), dpi=128, facecolor='#282b30')
for axis, filename, label in zip(axes, ['Antes_04_Pescoco.png', 'Depois_04_Raiva.png'], ['Antes · frontal', 'Contorno frontal']):
    axis.imshow(mpimg.imread(ROOT / filename), interpolation='nearest'); axis.axis('off')
    axis.set_title(label, color='white', fontsize=16, pad=12)
fig.subplots_adjust(left=.012, right=.988, top=.90, bottom=.012, wspace=.012)
fig.savefig(ROOT / 'Comparativo_Contorno_Frontal.png', facecolor=fig.get_facecolor())
