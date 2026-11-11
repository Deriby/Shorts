"""Technical layout of the two camera views used in the user's marked guide."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
ROOT = Path(__file__).resolve().parent
fig, axes = plt.subplots(2, 2, figsize=(10, 10.6), dpi=128, facecolor='#282b30')
for row, view in enumerate(['Tres_Quartos', 'Perfil']):
    for col, stage in enumerate(['Antes', 'Depois']):
        axes[row, col].imshow(mpimg.imread(ROOT / (stage + '_' + view + '.png')), interpolation='nearest')
        axes[row, col].axis('off')
        if row == 0:
            axes[row, col].set_title('Contorno anterior' if col == 0 else 'Ajuste pela marcação', color='white', fontsize=16, pad=12)
fig.subplots_adjust(left=.012, right=.988, top=.955, bottom=.012, wspace=.012, hspace=.016)
fig.savefig(ROOT / 'Comparativo_Contorno.png', facecolor=fig.get_facecolor())
plt.close(fig)
fig, axes = plt.subplots(2, 1, figsize=(5, 10), dpi=128, facecolor='#282b30')
for axis, view in zip(axes, ['Tres_Quartos', 'Perfil']):
    axis.imshow(mpimg.imread(ROOT / ('Depois_' + view + '.png')), interpolation='nearest')
    axis.axis('off')
fig.subplots_adjust(left=0, right=1, top=1, bottom=0, hspace=.025)
fig.savefig(ROOT / 'Previa_Duas_Vistas.png', facecolor=fig.get_facecolor())
