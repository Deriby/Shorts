"""Extract the twelve drawn textures from the generated source; no face morphs."""
from pathlib import Path
import json
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
NAMES=['neutro','falando','sorriso','risada','deboche','susto','sem_reacao','bravo','triste','sem_graca','piscando','deboche_falando']
if __name__=='__main__':
    source=Image.open(ROOT/'atlas_source.png').convert('RGB')
    atlas=Image.new('RGB',(512,384))
    sheet=Image.new('RGB',(1024,840),(24,22,31));draw=ImageDraw.Draw(sheet)
    for i,name in enumerate(NAMES):
        x=i%4;y=i//4
        tile=source.crop((x*362,y*362,(x+1)*362,(y+1)*362)).resize((128,128),Image.Resampling.NEAREST)
        tile.save(ROOT/(name+'.png'));atlas.paste(tile,(x*128,y*128))
        sheet.paste(tile.resize((256,256),Image.Resampling.NEAREST),(x*256,y*280))
        draw.text((x*256+8,y*280+259),f'{i:02d}  {name}',fill=(240,236,255))
    atlas.save(ROOT/'atlas_4x3.png');sheet.save(ROOT/'Dery_Expressoes_PS1.png')
    (ROOT/'expressions.json').write_text(json.dumps({'version':1,'columns':4,'rows':3,'tile_size':128,'interpolation':'Closest','animation':'CONSTANT','expressions':[{'id':i,'name':n,'file':n+'.png'}for i,n in enumerate(NAMES)]},indent=2))
