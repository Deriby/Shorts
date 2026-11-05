"""Prepare inspected media and fictional document interfaces around the supplied voice."""
from pathlib import Path
import json, subprocess, math, wave, array
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
FPS = 24
records = json.loads((ROOT/'renders/package_inventory.json').read_text())
raw = {r['original_filename']: Path(r['local_path']) for r in records}
intake = json.loads((ROOT/'renders/audio_intake.json').read_text())
pics, game = ROOT/'assets/memes', ROOT/'assets/gameplay'
pics.mkdir(parents=True, exist_ok=True)
mapping = {'contextomeme.jpeg': 'contexto.jpg', 'contextomeme2.png': 'contexto2.png',
           'contextomeme3.jpg': 'contexto3.jpg', 'images (2).jpg': 'fantasia.jpg', 'meme.png': 'meme_gato.png'}
for src, dest in mapping.items():
    im = Image.open(raw[src]).convert('RGB')
    im.thumbnail((1280, 1280), Image.Resampling.NEAREST)
    im.save(pics/dest)
subprocess.run(['ffmpeg','-v','error','-y','-threads','1','-ss','6.8','-i',str(game/'vaporeon_unite.mp4'),
                '-frames:v','1','-vf','scale=640:360:flags=neighbor',str(pics/'vaporeon_unite.png')],check=True)
font = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def text(d, xy, value, size=20, fill='white', anchor='mm'):
    d.text(xy, value, font=ImageFont.truetype(font,size), fill=fill, anchor=anchor)
for title, filename in [('INTRODUÇÃO','folha_intro.png'),('ARGUMENTO','folha_argumento.png'),('CONCLUSÃO','folha_conclusao.png')]:
    im = Image.new('RGB',(384,512),(231,226,202)); d=ImageDraw.Draw(im)
    text(d,(192,57),title,28,(35,43,45))
    for y in range(112,454,35): d.rectangle((29,y,350,y+15),fill=(38,43,43))
    text(d,(192,485),'TEXTO OCULTO',18,(88,86,72)); im.save(pics/filename)
for vertical in [False, True]:
    W,H=(360,640) if vertical else (640,360); suffix='_vertical' if vertical else ''
    for state in ['documento','copiar','pseudo','narracoes','post','pergunta','pedra']:
        im=Image.new('RGB',(W,H),(23,33,47)); d=ImageDraw.Draw(im)
        d.rectangle((8,8,W-9,H-9),outline=(164,177,188),width=3)
        d.rectangle((12,12,W-13,49),fill=(47,71,100))
        text(d,(23,30),'ARQUIVO DA INTERNET',15,anchor='lm')
        if state=='pedra':
            text(d,(W//2,93 if vertical else 79),'PEDRA DA ÁGUA',27,(126,220,255))
            cx,cy=(W//2,246) if vertical else (135,214)
            vertices=[(cx-48,cy-53),(cx-11,cy-77),(cx+39,cy-57),(cx+57,cy+3),(cx+26,cy+67),(cx-31,cy+62),(cx-57,cy+8)]
            d.polygon(vertices,fill=(61,135,191),outline=(154,228,244),width=5)
            d.polygon([(cx-42,cy-40),(cx-11,cy-64),(cx+19,cy-42),(cx+8,cy+9),(cx-20,cy+48),(cx-35,cy+8)],fill=(91,195,223))
            d.line([(cx-28,cy-26),(cx-6,cy-11),(cx+20,cy-26)],fill=(198,246,240),width=9)
            pic=ImageOps.contain(Image.open(pics/'vaporeon_unite.png'),(306,173) if vertical else (365,205),Image.Resampling.NEAREST)
            im.paste(pic,((W-pic.width)//2,389) if vertical else (247,112))
            text(d,(W//2,350) if vertical else (219,210),'↓' if vertical else '→',40,(244,213,65))
        elif state=='pergunta':
            text(d,(W//2,H//2-35),'CONTEXTO?',36,(255,221,64))
            d.rectangle((35,H//2+20,W-35,H//2+76),fill=(45,68,91))
            text(d,(W//2,H//2+48),'COMENTAR',22,(218,227,226))
        elif state=='post':
            pic=ImageOps.contain(Image.open(pics/'vaporeon_unite.png'),(W-50,208 if vertical else 118),Image.Resampling.NEAREST)
            im.paste(pic,((W-pic.width)//2,63))
            y0=311 if vertical else 195
            for n in range(3):
                yy=y0+n*(83 if vertical else 47)
                d.rectangle((25+n*4,yy,W-25,yy+(63 if vertical else 36)),fill=(49+n*8,65+n*4,79))
                text(d,(W//2,yy+(31 if vertical else 18)),'TEXTO OCULTO',18,(197,207,204))
        elif state=='narracoes':
            text(d,(W//2,112 if vertical else 88),'NARRAÇÕES E PARÓDIAS',22,(246,215,67))
            mid=H//2+20
            for n in range(23):
                x=30+n*(W-60)/23; h=15+(n*37%91)
                d.rectangle((x,mid-h/2,x+5,mid+h/2),fill=(82,199,212))
            text(d,(W//2,H-66),'COPIAR • COLAR • REPETIR',17,(192,202,210))
        else:
            title={'documento':'COPYPASTA','copiar':'COPIAR + COLAR','pseudo':'PARECE CIÊNCIA?'}[state]
            text(d,(W//2,90 if vertical else 78),title,27,(247,217,76))
            count=3 if state=='copiar' else 1
            for n in range(count):
                x=25+n*17; y=(155 if vertical else 117)+n*19
                d.rectangle((x,y,W-65+n*17,H-80+n*7),fill=(204-n*13,208-n*13,195-n*9),outline=(94,115,127),width=2)
                for yy in range(y+25,H-91,27): d.rectangle((x+14,yy,W-85+n*17,yy+10),fill=(25,34,38))
            d.rectangle((W-29,138,W-23,H-74),fill=(72,88,102));d.rectangle((W-29,139,W-23,149),fill=(246,214,62))
            text(d,(W//2,H-39),'TEXTO OCULTO',18,(204,214,221))
        im.save(pics/f'{state}{suffix}.png')
with wave.open(str(ROOT/'assets/voz/narracao_completa.wav')) as w:
    sr=w.getframerate();voice=array.array('h',w.readframes(w.getnframes()))
vd=len(voice)/sr;N=math.ceil((vd+.65)*FPS);end=N/FPS
specs=[(0,1.5,'monitor','name','vaporeon_unite.mp4',6.3),
 (1.5,3.05,'actor','present','vaporeon_anime.mp4',2),
 (3.05,6.45,'photo','stone','pedra.png',0),
 (6.45,10.35,'actor','skeptic','pedra.png',0),
 (10.35,12.4,'photo','document','documento.png',0),
 (12.4,14.0,'actor','deadpan','documento.png',0),
 (14.0,16.25,'graphic','copy','copiar.png',0),
 (16.25,18.3,'game','unite','vaporeon_unite.mp4',3.0),
 (18.3,21.8,'desk','pseudo','pseudo.png',0),
 (21.8,24.0,'actor','skeptic','pseudo.png',0),
 (24.0,26.9,'photo','costume','fantasia.jpg',0),
 (26.9,29.1,'desk','paperwide','documento.png',0),
 (29.1,31.5,'desk','buried','documento.png',0),
 (31.5,33.3,'graphic','audio','narracoes.png',0),
 (33.3,35.8,'game','unite','vaporeon_unite.mp4',.2),
 (35.8,38.0,'graphic','comments','post.png',0),
 (38.0,40.65,'actor','question','pergunta.png',0),
 (40.65,43.2,'graphic','question','pergunta.png',0),
 (43.2,44.4,'photo','meme','contexto3.jpg',0),
 (44.4,46.0,'photo','meme','contexto2.png',0),
 (46.0,end,'desk','final','contexto.jpg',0)]
shots=[dict(id=i,start=round(t0*FPS)+1,end=round(t1*FPS),kind=k,mood=m,source=src,source_start=at)
       for i,(t0,t1,k,m,src,at) in enumerate(specs)]
shots[-1]['end']=N
assert all(a['end']+1==b['start']for a,b in zip(shots,shots[1:]))
media=ROOT/'renders/media';media.mkdir(exist_ok=True);clips=[]
for sh in shots:
    src=(game if sh['source'].endswith('.mp4') else pics)/sh['source']
    dest=media/f"monitor_{sh['id']:02d}.mp4";n=sh['end']-sh['start']+1
    cmd=['ffmpeg','-v','error','-y','-threads','1','-filter_threads','1']
    cmd+=['-ss',str(sh['source_start']),'-i',str(src)] if src.suffix=='.mp4' else ['-f','image2','-loop','1','-framerate','24','-i',str(src)]
    cmd+=['-an','-vf','fps=24,scale=640:360:force_original_aspect_ratio=decrease:flags=neighbor,pad=640:360:(ow-iw)/2:(oh-ih)/2:color=0x111319',
          '-frames:v',str(n),'-c:v','libx264','-threads','1','-preset','ultrafast','-crf','18','-pix_fmt','yuv420p',str(dest)]
    subprocess.run(cmd,check=True);clips.append(dest)
listing=media/'concat.txt';listing.write_text(''.join("file '"+str(p)+"'\n" for p in clips))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(listing),'-c:v','copy','-movflags','+faststart',str(game/'monitor_montado.tmp.mp4')],check=True)
(game/'monitor_montado.tmp.mp4').replace(game/'monitor_montado.mp4')
mixed=array.array('h',voice);mixed.extend([0]*(math.ceil(end*sr)-len(mixed)))
with wave.open(str(ROOT/'assets/voz/narracao_mix.wav'),'wb') as w:
    w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(mixed.tobytes())
(ROOT/'timeline.json').write_text(json.dumps(dict(fps=FPS,frames=N,duration=end,voice_duration=vd,shots=shots),indent=2))
(ROOT/'audio.json').write_text(json.dumps(dict(**intake,frames=N,speed_changed=False,pitch_changed=False,trimmed=False,
 alignment='Received narration supersedes earlier written outline: stone joke at start; context memes at end. Original voice preserved, source videos muted.'),ensure_ascii=False,indent=2))
public=[{k:v for k,v in r.items()if k not in ['local_path','probe']} for r in records]
(ROOT/'source_manifest.json').write_text(json.dumps(dict(package='5 - Vaporeon.zip',source='User-provided Google Drive archive',files=public,
 video_derivatives=json.loads((ROOT/'renders/selected_clips.json').read_text()),images_published=list(mapping),
 editorial='Only normal Pokémon footage, clothed memes and authored opaque documents. Original copypasta and its sexual arguments are not reproduced. Water Stone card is a stylized illustration, not captured evolution footage.',
 unused='Archive, unselected originals and personal gesture reference remain outside Git.'),ensure_ascii=False,indent=2))
print('VAPOREON_ASSETS_READY',N,end,flush=True)
