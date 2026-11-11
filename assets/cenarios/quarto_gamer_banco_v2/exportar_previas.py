"""Output the Blender previews as sharp nearest-neighbor RGB555 images."""
from pathlib import Path
import numpy as np
from PIL import Image

P=Path(__file__).resolve().parent
WORK=Path('/workspace/attachments/quarto_gamer_v2')
# A restrained ordered dither, in display RGB, mimics the PS1's 15-bit buffer.
bayer=np.asarray([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]],dtype=float)/16-.5
for name,output in [('Quarto_Completo','Previa_Quarto_Completo.png'),('Quarto_9x16','Previa_Quarto_9x16.png'),('Mesa_CRT','Previa_Mesa_CRT.png')]:
    image=Image.open(WORK/(name+'_base.png')).convert('RGB');a=np.asarray(image,dtype=float)/255
    d=np.tile(bayer,(int(np.ceil(a.shape[0]/4)),int(np.ceil(a.shape[1]/4))))[:a.shape[0],:a.shape[1]]
    q=np.clip(np.floor(a*31+.5+d[...,None]*.65),0,31)/31
    pixels=Image.fromarray(np.uint8(np.round(q*255)))
    pixels=pixels.resize((image.width*4,image.height*4),Image.Resampling.NEAREST)
    pixels.save(P/output)
    print('PREVIEW',output,pixels.size)
