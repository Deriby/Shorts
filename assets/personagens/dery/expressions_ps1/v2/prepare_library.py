"""Register and extract 31 drawn expressions; preserve the approved twelve."""
from pathlib import Path
import json,shutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
NEW=['explicando','orgulhoso','gargalhada','olhando_esquerda','sarcasmo_falando','piscadinha','constrangido','ofendido','pensativo','gritando','confuso','serio','serio_falando','nervoso','impressionado','contente','lingua_fora','nojo','chorando']
def register(tile,src):
    # Normalize eye/nose/mouth registration across sheets with different cells.
    if len(src)==7:
        # Different mouth shapes move the drawn moustache. Keep that identity
        # feature registered independently instead of clipping it at the nose.
        candidates=[]
        for y in range(int(tile.height*.48),int(tile.height*.73)):
            dark=sum(max(tile.getpixel((x,y)))<85 for x in range(int(tile.width*.16),int(tile.width*.84)))
            if dark>tile.width*.22:candidates.append(y)
        moustache=(candidates[0]+tile.height*.012)/tile.height if candidates else(src[3]+src[4])/2
        moustache=min(src[4]-.045,max(src[2]+.12,moustache))
        src=[src[0],src[1],src[2],min(src[3],moustache-.035),moustache,src[4],src[5],src[6]]
    target=[0,.14,.28,.58,.67,.76,.91,1]if len(src)==8 else[0,.14,.28,.58,.76,.91,1]
    out=Image.new('RGB',(128,128))
    tile=tile.resize((128,tile.height),Image.Resampling.NEAREST)
    for y in range(128):
        p=(y+.5)/128
        k=next(k for k in range(len(target)-1)if p<=target[k+1])
        sy=src[k]+(src[k+1]-src[k])*(p-target[k])/(target[k+1]-target[k])
        row=max(0,min(tile.height-1,round(sy*tile.height)))
        out.paste(tile.crop((0,row,128,row+1)),(0,y))
    return out
if __name__=='__main__':
    old=json.loads((ROOT.parent/'expressions.json').read_text())['expressions']
    entries=[]
    for e in old:
        shutil.copyfile(ROOT.parent/e['file'],ROOT/e['file']);entries.append(dict(e))
    image=Image.open(ROOT/'sources/additional_sheet.png').convert('RGB')
    cells=[]
    third=[(0,663,362,907),(369,663,629,907),(627,663,887,907),(866,663,1134,907),(1152,663,1440,907)]
    for y0,y1,cols,landmarks in [(0,333,4,[0,.13,.30,.58,.79,.94,1]),(333,663,4,[0,.13,.31,.60,.81,.94,1]),(663,907,5,[0,.13,.30,.57,.73,.93,1])]:
        for x in range(cols):
            rect=(round(x*image.width/cols),y0,round((x+1)*image.width/cols),y1)
            if y0==663:rect=third[x]
            registration=[0,.13,.30,.53,.60,.79,.94,1]if y0==0 and x==2 else landmarks
            cells.append(register(image.crop(rect),registration))
    image=Image.open(ROOT/'sources/additional_six.png').convert('RGB')
    for row in range(2):
        for col in range(3):
            rect=(col*image.width//3,row*image.height//2,(col+1)*image.width//3,(row+1)*image.height//2)
            cells.append(register(image.crop(rect),[0,.16,.31,.58,.78,.90,1]))
    assert len(cells)==len(NEW)==19
    for name,tile in zip(NEW,cells):
        tile.save(ROOT/(name+'.png'));entries.append({'id':len(entries),'name':name,'file':name+'.png'})
    atlas=Image.new('RGB',(1024,512));sheet=Image.new('RGB',(1536,896),(25,20,33))
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12)
    draw=ImageDraw.Draw(sheet)
    for e in entries:
        i=e['id'];tile=Image.open(ROOT/e['file']);x=i%8;y=i//8
        atlas.paste(tile,(x*128,y*128));sheet.paste(tile.resize((192,192),Image.Resampling.NEAREST),(x*192,y*224))
        draw.text((x*192+5,y*224+197),f"{i:02d} {e['name']}",font=font,fill='white')
    atlas.paste(Image.open(ROOT/'neutro.png'),(7*128,3*128))
    atlas.save(ROOT/'atlas_31_8x4.png');sheet.save(ROOT/'Dery_31_Expressoes.png')
    (ROOT/'expressions.json').write_text(json.dumps({'version':2,'count':31,'columns':8,'rows':4,'tile_size':128,'interpolation':'Closest','animation':'CONSTANT','expressions':entries},indent=2))
    print('31 distinct drawn PNGs and registered 8x4 atlas ready.')
