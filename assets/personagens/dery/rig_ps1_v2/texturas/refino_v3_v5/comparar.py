"""Compare identical camera renders; no resampling or artistic edits."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent;BEFORE=ROOT.parent/'rosto_neutro_v3'
for part,w,h in [('Corpo',900,1100),('Rosto',640,640)]:
 margin=22;gap=18;label=44;title=68
 width=2*w+gap+2*margin;height=h+label+title+2*margin
 fig=plt.figure(figsize=(width/100,height/100),dpi=100,facecolor='#282a2f')
 fig.text(margin/width,1-25/height,'DERY — MESMAS TEXTURAS, REFINO DE DETALHES',color='#eee',size=18,weight='bold',va='top')
 for column,(folder,name) in enumerate([(BEFORE,'Anterior · v3'),(ROOT,'Refino da textura existente · v5')]):
  left=margin+column*(w+gap);top=title+margin
  fig.text((left+w/2)/width,1-(top+4)/height,name,ha='center',va='top',size=16,color='#eee')
  bottom=height-(top+label+h)
  ax=fig.add_axes([left/width,bottom/height,w/width,h/height]);ax.imshow(plt.imread(folder/('Previa_'+part+'.png')),interpolation='nearest');ax.set_axis_off()
 fig.savefig(ROOT/('Comparativo_'+part+'.png'),dpi=100,facecolor=fig.get_facecolor(),pad_inches=0);plt.close(fig)
 print('Comparativo_'+part+'.png')
