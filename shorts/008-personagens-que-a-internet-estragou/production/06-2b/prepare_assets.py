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
mapping = {'maxresdefault.jpg':'2b_retrato.jpg','meme2b-2.png':'meme_fa.png'}
for src,dest in mapping.items():
 im=Image.open(raw[src]).convert('RGB');im.thumbnail((1280,1280),Image.Resampling.NEAREST);im.save(pics/dest)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def text(d,xy,value,size=20,fill='white',anchor='mm'):
 d.text(xy,value,font=ImageFont.truetype(font,size),fill=fill,anchor=anchor)
for vertical in [False,True]:
 W,H=(360,640)if vertical else(640,360);suffix='_vertical'if vertical else''
 for selected,state in enumerate(['fanart','animacao','mods']):
  im=Image.new('RGB',(W,H),(22,30,43));d=ImageDraw.Draw(im);d.rectangle((8,8,W-9,H-9),outline=(146,163,181),width=3);d.rectangle((12,12,W-13,49),fill=(44,61,84));text(d,(22,30),'ARQUIVO DA INTERNET',15,anchor='lm')
  for i,label in enumerate(['FANART','ANIMAÇÃO','MODS']):
   x,y=(30,92+i*167)if vertical else(20+i*208,97);w,h=(300,140)if vertical else(185,184)
   color=(233,194,53)if i==selected else(86,109,132);d.rectangle((x+7,y,x+77,y+18),fill=color);d.rectangle((x,y+13,x+w,y+h),fill=(47,61,77),outline=color,width=4);text(d,(x+w//2,y+40),label,23 if vertical else 21,(242,224,177));d.rectangle((x+17,y+70,x+w-17,y+h-14),fill=(8,13,20));text(d,(x+w//2,y+99 if vertical else y+120),'PRÉVIA OCULTA',17 if vertical else 15,(166,180,187))
  im.save(pics/f'pastas_{state}{suffix}.png')
 for state in ['maquinas','internet']:
  im=Image.new('RGB',(W,H),(17,27,31));d=ImageDraw.Draw(im);color=(98,213,151)if state=='maquinas'else(241,173,65);d.rectangle((8,8,W-9,H-9),outline=color,width=5);text(d,(W//2,75 if vertical else 53),'TESTE DE COMBATE',25,(219,226,215));text(d,(W//2,195 if vertical else 133),'MÁQUINAS'if state=='maquinas'else'INTERNET',35,color)
  text(d,(W//2,300 if vertical else 215),'PREPARADO'if state=='maquinas'else'SEM TREINAMENTO',30 if not vertical else 27,color)
  text(d,(W//2,H-73),'01 / MÁQUINAS'if state=='maquinas'else'02 / INTERNET',19,(148,168,170));im.save(pics/f'treino_{state}{suffix}.png')
 im=Image.new('RGB',(W,H),(24,31,43));d=ImageDraw.Draw(im);text(d,(W//2,83 if vertical else 57),'2 mm?!',52,(255,213,63));x0,x1=(80,280)if vertical else(90,550);y0,y1=(166,557)if vertical else(130,265);d.rectangle((x0,y0,x1,y1),fill=(219,185,87),outline=(255,224,140),width=5)
 if vertical:
  for i,y in enumerate(range(y0+14,y1-10,16)):d.line((x0+5,y,x0+(86 if i%5==0 else 45),y),fill=(43,47,42),width=4)
 else:
  for i,x in enumerate(range(x0+15,x1-10,17)):d.line((x,y0+4,x,y0+(74 if i%5==0 else 39)),fill=(43,47,42),width=4)
 text(d,(W//2,H-34),'RÉGUA DO FISCAL',20,(196,206,213));im.save(pics/f'regua{suffix}.png')
with wave.open(str(ROOT/'assets/voz/narracao_completa.wav')) as w:
    sr=w.getframerate();voice=array.array('h',w.readframes(w.getnframes()))
vd=len(voice)/sr;N=math.ceil((vd+.65)*FPS);end=N/FPS
specs=[(0,1.45,'monitor','name','2b_retrato.jpg',0),
 (1.45,3.02,'actor','present','combate_2b.mp4',0),
 (3.02,4.5,'game','combat','combate_2b.mp4',.2),
 (4.5,6.02,'game','combat','combate_2b.mp4',5.2),
 (6.02,8.4,'actor','reflect','2b_retrato.jpg',0),
 (8.4,11.02,'photo','reflect','2b_retrato.jpg',0),
 (11.02,13.2,'actor','smirk','pastas_fanart.png',0),
 (13.2,15.16,'photo','meme','meme_fa.png',0),
 (15.16,16.32,'photo','folders','pastas_fanart.png',0),
 (16.32,17.55,'photo','folders','pastas_animacao.png',0),
 (17.55,18.92,'photo','folders','pastas_mods.png',0),
 (18.92,21.52,'actor','resign','pastas_mods.png',0),
 (21.52,25.24,'game','selfdestruct','autodestruicao_2b.mp4',0),
 (25.24,27.2,'actor','annoyed','autodestruicao_2b.mp4',12.5),
 (27.2,28.35,'game','aftermath','autodestruicao_2b.mp4',12.5),
 (28.35,29.6,'graphic','ruler','regua.png',0),
 (29.6,31.28,'photo','reflect','2b_retrato.jpg',0),
 (31.28,34.9,'training','ready','treino_maquinas.png',0),
 (34.9,35.25,'photo','ready','treino_maquinas.png',0),
 (35.25,36.05,'photo','fail','treino_internet.png',0),
 (36.05,end,'training','final','treino_internet.png',0)]
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
 alignment='Provided 2B narration, aligned with local ASR segments. Full original recording preserved; gameplay audio muted.'),ensure_ascii=False,indent=2))
public=[{k:v for k,v in r.items()if k not in ['local_path','probe']} for r in records]
(ROOT/'source_manifest.json').write_text(json.dumps(dict(package='6 - 2B.zip',source='User-provided Google Drive archive',files=public,
 video_derivatives=json.loads((ROOT/'renders/selected_clips.json').read_text()),images_published=list(mapping),
 editorial='Normal NieR:Automata combat and self-destruct gameplay, clothed portrait and fangirl meme. Folder previews are authored opaque graphics. Ruler is a visual joke, not a body measurement. No adult fan animation or unverified director quotation is included.',
 unused='Archive, unselected originals and personal gesture reference remain outside Git.'),ensure_ascii=False,indent=2))
print('TWOB_ASSETS_READY',N,end,flush=True)
