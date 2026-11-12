"""Assemble actual Blender renders; nearest scaling only, no face repainting."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parent
CACHE=Path('/workspace/attachments/dery100')
entries=json.loads((ROOT/'expressions.json').read_text())['expressions']
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
large=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',25)

def label(draw,entry,x,y,width=240):
    value=f"{entry['id']:03d} {entry['name'].replace('_',' ')}"
    words=value.split();lines=['']
    for word in words:
        if draw.textlength(lines[-1]+word,font=font)>width-12:lines.append('')
        lines[-1]+=word+' '
    for row,line in enumerate(lines[:3]):draw.text((x+6,y+row*17),line,font=font,fill='white')

for batch,title in enumerate(['Fala — A E I O','Fala — outras bocas','Reações','Caricatas']):
    page=Image.new('RGB',(1200,1540),(27,28,33));draw=ImageDraw.Draw(page)
    draw.text((20,15),f'DERY | {title} | 25 novas expressões',font=large,fill=(255,204,48))
    for k,e in enumerate(entries[31+batch*25:56+batch*25]):
        x,y=k%5*240,60+k//5*296
        tile=Image.open(CACHE/f"model_{e['id']:03d}.png").convert('RGB')
        page.paste(tile,(x,y));label(draw,e,x,y+258)
    page.save(ROOT/f'No_Modelo_{batch+1:02d}.png')

chosen=[32,33,57,58,81,86,106,107,109,117,120,130]
page=Image.new('RGB',(1440,1300),(27,28,33));draw=ImageDraw.Draw(page)
draw.text((24,16),'DERY | 100 NOVAS EXPRESSÕES PS1',font=large,fill=(255,204,48))
draw.text((24,52),'50 para fala + 25 reações + 25 caricatas | 31 anteriores preservadas',font=font,fill='white')
for k,i in enumerate(chosen):
    x,y=k%4*360,86+k//4*402
    # 240 -> 360 is a point-sampled enlargement; no blurry interpolation.
    tile=Image.open(CACHE/f'model_{i:03d}.png').convert('RGB')
    page.paste(tile.resize((360,384),Image.Resampling.NEAREST),(x,y))
    label(draw,entries[i],x,y+382,360)
page.save(ROOT/'Previa_Expressoes_No_Dery.png')

page=Image.new('RGB',(960,1212),(27,28,33));draw=ImageDraw.Draw(page)
draw.text((20,12),'Teste de encaixe: frente, três quartos e perfil',font=large,fill=(255,204,48))
for row,i in enumerate([32,58,107,130]):
    for col,view in enumerate(['model','tres_quartos','perfil']):
        x,y=col*320,58+row*288
        tile=Image.open(CACHE/f'{view}_{i:03d}.png').convert('RGB')
        page.paste(tile.resize((270,288),Image.Resampling.NEAREST),(x,y))
        draw.text((x+5,y+268),f'{i:03d} | {view}',font=font,fill='white')
page.save(ROOT/'Conferencia_Angulos.png')
print('Four complete sheets + selected expressions + angle checks ready.')
