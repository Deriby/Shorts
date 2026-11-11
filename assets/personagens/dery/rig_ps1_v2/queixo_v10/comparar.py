"""Technical comparison of the rendered chin and profile frames."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
ROOT = Path(__file__).resolve().parent
fig, axes = plt.subplots(2, 2, figsize=(10, 10.6), dpi=128, facecolor='#282b30')
for row, view in enumerate(['Detalhe', 'Perfil']):
    for col, stage in enumerate(['Antes', 'Depois']):
        axes[row, col].imshow(mpimg.imread(ROOT / (stage + '_' + view + '.png')), interpolation='nearest')
        axes[row, col].axis('off')
        if row == 0:
            axes[row, col].set_title('Queixo anterior' if col == 0 else 'Base arredondada', color='white', fontsize=16, pad=12)
fig.subplots_adjust(left=.012, right=.988, top=.955, bottom=.012, wspace=.012, hspace=.016)
fig.savefig(ROOT / 'Comparativo_Queixo.png', facecolor=fig.get_facecolor())
