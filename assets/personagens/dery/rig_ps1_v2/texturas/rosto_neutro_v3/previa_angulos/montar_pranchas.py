"""Arrange the unchanged Blender views as labeled technical contact sheets."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
report=json.loads((HERE/'vistas.json').read_text())
for group,title,w,h,out in [('corpo','DERY / MASSACOTE — CORPO INTEIRO',540,680,'Corpo_8_Angulos.png'),('rosto','DERY / MASSACOTE — CABEÇA',512,512,'Rosto_8_Angulos.png')]:
 margin=24;gap=12;label=38;header=85
 canvas_w=4*w+3*gap+2*margin;canvas_h=2*(h+label)+gap+2*margin+header
 fig=plt.figure(figsize=(canvas_w/100,canvas_h/100),dpi=100,facecolor='#282a2f')
 fig.text(margin/canvas_w,1-30/canvas_h,title,color='#f1efe8',size=19,weight='bold',va='top')
 fig.text(margin/canvas_w,1-60/canvas_h,'Versão v3 · lados esquerdo/direito do personagem · mesma pose e escala',color='#b7b8bd',size=11,va='top')
 frames=[v for v in report['views'] if v['group']==group]
 for i,view in enumerate(frames):
  row,col=divmod(i,4);left=margin+col*(w+gap);top=header+margin+row*(h+label+gap)
  fig.text((left+w/2)/canvas_w,1-(top+5)/canvas_h,view['label'],color='#f1efe8',size=12,ha='center',va='top')
  bottom=canvas_h-(top+label+h)
  ax=fig.add_axes([left/canvas_w,bottom/canvas_h,w/canvas_w,h/canvas_h])
  ax.imshow(plt.imread(HERE/view['file']),interpolation='nearest');ax.set_axis_off()
 fig.savefig(HERE/out,dpi=100,facecolor=fig.get_facecolor(),edgecolor='none',pad_inches=0)
 plt.close(fig)
 print(out,canvas_w,canvas_h)
