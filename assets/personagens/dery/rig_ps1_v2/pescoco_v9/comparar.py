"""Arrange the original render frames for anatomical comparison."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
ROOT = Path(__file__).resolve().parent
fig, axes = plt.subplots(3, 2, figsize=(10, 15.2), dpi=128, facecolor='#282b30')
for row, view in enumerate(['Frente', 'Tres_Quartos', 'Perfil']):
    for col, stage in enumerate(['Antes', 'Depois']):
        axes[row, col].imshow(mpimg.imread(ROOT / (stage + '_' + view + '.png')), interpolation='nearest')
        axes[row, col].axis('off')
        if row == 0:
            axes[row, col].set_title('Pescoço anterior' if col == 0 else 'Proposta de ajuste', color='white', fontsize=16, pad=12)
fig.subplots_adjust(left=.012, right=.988, top=.968, bottom=.008, wspace=.012, hspace=.018)
fig.savefig(ROOT / 'Comparativo_Pescoco.png', facecolor=fig.get_facecolor())
