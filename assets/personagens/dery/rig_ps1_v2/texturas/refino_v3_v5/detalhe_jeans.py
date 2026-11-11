"""A magnified technical comparison of the same render area, without repainting."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
fig=plt.figure(figsize=(14.4,11.75),dpi=100,facecolor='#282a2f')
fig.text(.02,.975,'DETALHE DO JEANS — A MESMA TEXTURA',color='#eee',size=19,weight='bold',va='top')
fig.text(.02,.94,'Ampliação de 3× com pixels preservados · mesma câmera e iluminação',color='#bbb',size=12,va='top')
for column,(folder,label) in enumerate([(ROOT.parent/'rosto_neutro_v3','Original · v3'),(ROOT,'Refino · v5')]):
 image=plt.imread(folder/'Previa_Corpo.png')[600:945,315:545]
 left=20+column*710;fig.text((left+345)/1440,.905,label,color='#eee',size=16,ha='center',va='top')
 ax=fig.add_axes([left/1440,20/1175,690/1440,1035/1175]);ax.imshow(image,interpolation='nearest');ax.set_axis_off()
fig.savefig(ROOT/'Detalhe_Jeans.png',dpi=100,facecolor=fig.get_facecolor());plt.close(fig)
