"""Prepare supplied Sonic narration, inspected gameplay and authored retro interfaces."""
from pathlib import Path
import json, subprocess, math, wave, array
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
FPS=24
records=json.loads((ROOT/'renders/package_inventory.json').read_text())
raw={r['original_filename']:Path(r['local_path']) for r in records}
intake=json.loads((ROOT/'renders/audio_intake.json').read_text())
pics,game=ROOT/'assets/memes',ROOT/'assets/gameplay'
pics.mkdir(parents=True,exist_ok=True);game.mkdir(exist_ok=True)
mapping={'Joyful-Sonic-meme-4.jpg':'meme_anel.jpg','Sonic_EXE.png':'sonic_exe.png','my-attempt-to-name-sonic-exe-variants-i-only-know-tripwire-v0-9q0xxqdtvtog1.png':'variantes_fas.png'}
for src,dest in mapping.items():
 im=Image.open(raw[src]).convert('RGB');im.thumbnail((1280,1280),Image.Resampling.NEAREST);im.save(pics/dest)
Image.open(raw['7256p5.jpg']).convert('RGB').crop((0,0,500,470)).save(pics/'fanart_sonic.jpg')
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def text(d,xy,value,size=20,fill='white',anchor='mm'):
 d.text(xy,value,font=ImageFont.truetype(font,size),fill=fill,anchor=anchor)
for vertical in [False,True]:
 W,H=(360,640)if vertical else(640,360);suffix='_vertical'if vertical else''
 for state in ['arquivo_a','arquivo_b','arquivo_c','arquivo_d','busca','terror_menu','terror_exit','terror_closed','creepypastas']:
  horror=state.startswith('terror')or state=='creepypastas';bg=(23,17,28)if horror else(20,32,53);border=(173,58,70)if horror else(63,157,192)
  im=Image.new('RGB',(W,H),bg);d=ImageDraw.Draw(im);d.rectangle((8,8,W-9,H-9),outline=border,width=4)
  if state.startswith('arquivo'):
   text(d,(W//2,65 if vertical else 36),'ARQUIVO DO FANDOM',24,(231,210,130));active=ord(state[-1])-ord('a')
   for i,label in enumerate(['FANART','FAN GAME','ANIMAÇÃO','FANFIC']):
    x=24+(i%2)*(W//2);y=(180 if vertical else 109)+(i//2)*(195 if vertical else 106);bw=W//2-48;bh=102 if vertical else 57
    color=(234,188,76)if active==i else(88,121,148)
    d.rectangle((x,y,x+bw,y+bh),fill=color);d.rectangle((x,y-13,x+bw*.42,y),fill=color)
    text(d,(x+bw//2,y+bh+26),label,20,(239,221,159)if active==i else(174,200,211))
  elif state=='busca':
   text(d,(W//2,70 if vertical else 40),'PESQUISA',28,(209,229,240));d.rectangle((27,135 if vertical else 90,W-28,185 if vertical else 137),fill=(190,212,219))
   text(d,(45,160 if vertical else 113),'Sonic',25,(18,34,46),'lm')
   for i in range(3):
    yy=(236 if vertical else 166)+i*(92 if vertical else 44);d.rectangle((29,yy,W-30,yy+(64 if vertical else 32)),fill=(6,12,20),outline=(60,111,134),width=2)
   text(d,(W//2,564 if vertical else 322),'RESULTADOS OCULTOS',22,(235,197,99))
  else:
   text(d,(W//2,59 if vertical else 32),'SONIC.EXE',41 if vertical else 34,(235,96,105));text(d,(W//2,103 if vertical else 66),'FEITO POR FÃS',18,(224,182,136))
   if state=='terror_closed':
    text(d,(W//2,H//2-24),'SESSÃO',38,(209,216,224));text(d,(W//2,H//2+27),'ENCERRADA',38,(209,216,224));text(d,(W//2,H-74 if vertical else H-40),'VOLTAR',20,(216,180,107))
   else:
    pic=Image.open(pics/'sonic_exe.png').convert('RGB');pic.thumbnail((270,270)if vertical else(220,220),Image.Resampling.NEAREST);im.paste(pic,((W-pic.width)//2 if vertical else 33,142 if vertical else 98))
    labels=['HISTÓRIAS','CREEPYPASTAS','FANGAMES']if state=='creepypastas'else['HISTÓRIAS','FANGAMES','SAIR']
    for i,label in enumerate(labels):
     xx=W//2 if vertical else 442;yy=(453 if vertical else 151)+i*(48 if vertical else 58);highlight=state=='terror_exit'and i==2
     if highlight:d.rectangle((xx-103,yy-18,xx+103,yy+18),fill=(169,55,62))
     text(d,(xx,yy),('> 'if highlight else'')+label,24,(244,217,147)if highlight else(217,204,207))
  im.save(pics/f'{state}{suffix}.png')
clipspecs=[('sonic_dash.mp4','Sonic Dash -',20,25.5,'Official Sonic Dash: normal blue Sonic running through a coastal level.'),
 ('sonic_freedom.mp4','Sonic Freedom -',26.4,30.0,'Neutral example of a fan game, used for the category rather than as adult or bizarre content.')]
derivatives={}
for dest,prefix,start,stop,description in clipspecs:
 src=next(p for n,p in raw.items()if n.startswith(prefix)and p.suffix=='.mp4')
 subprocess.run(['ffmpeg','-v','error','-y','-threads','1','-filter_threads','1','-ss',str(start),'-i',str(src),'-t',str(stop-start),'-an','-vf','fps=24,scale=960:540:flags=neighbor','-c:v','libx264','-threads','1','-g','24','-preset','ultrafast','-crf','18','-pix_fmt','yuv420p',str(game/dest)],check=True)
 derivatives[dest]=dict(original=src.name,interval=[start,stop],description=description,audio_used=False)
with wave.open(str(ROOT/'assets/voz/narracao_completa.wav'))as w:sr=w.getframerate();voice=array.array('h',w.readframes(w.getnframes()))
vd=len(voice)/sr;N=math.ceil((vd+.65)*FPS);end=N/FPS
specs=[(0,1.2,'monitor','name','sonic_dash.mp4',0),
 (1.2,3.0,'actor','present','sonic_dash.mp4',1.2),
 (3.0,5.56,'game','normal','sonic_dash.mp4',2.6),
 (5.56,7.2,'actor','list','arquivo_a.png',0),
 (7.2,9.1,'photo','fanart','fanart_sonic.jpg',0),
 (9.1,10.7,'game','fangame','sonic_freedom.mp4',.5),
 (10.7,12.4,'photo','animation','meme_anel.jpg',0),
 (12.4,14.1,'photo','fanfic','arquivo_d.png',0),
 (14.1,16.3,'actor','awkward','arquivo_d.png',0),
 (16.3,18.4,'actor','confused','busca.png',0),
 (18.4,21.6,'photo','search','busca.png',0),
 (21.6,23.7,'actor','disbelief','busca.png',0),
 (23.7,25.2,'actor','brain','busca.png',0),
 (25.2,26.8,'arcade','reveal','terror_menu.png',0),
 (26.8,28.7,'photo','horror','terror_menu.png',0),
 (28.7,30.2,'arcade','recoil','terror_menu.png',0),
 (30.2,31.7,'photo','variants','variantes_fas.png',0),
 (31.7,32.5,'photo','stories','creepypastas.png',0),
 (32.5,33.2,'arcade','exit','terror_exit.png',0),
 (33.2,end,'arcade','final','terror_closed.png',0)]
shots=[dict(id=i,start=round(t0*FPS)+1,end=round(t1*FPS),kind=k,mood=m,source=src,source_start=at)for i,(t0,t1,k,m,src,at)in enumerate(specs)];shots[-1]['end']=N
for sh in shots:
 if sh['mood']=='fangame':sh['fan_badge']=True;sh['crop_x']=328
 if sh['mood']=='variants':sh['fan_badge']=True
 if sh['mood']=='brain':sh['brain_fx']=True
assert all(a['end']+1==b['start']for a,b in zip(shots,shots[1:]))
media=ROOT/'renders/media';media.mkdir(exist_ok=True);clips=[]
for sh in shots:
 src=(game if sh['source'].endswith('.mp4')else pics)/sh['source'];dest=media/f"monitor_{sh['id']:02d}.mp4";n=sh['end']-sh['start']+1
 cmd=['ffmpeg','-v','error','-y','-threads','1','-filter_threads','1']
 cmd+=['-ss',str(sh['source_start']),'-i',str(src)]if src.suffix=='.mp4'else['-f','image2','-loop','1','-framerate','24','-i',str(src)]
 cmd+=['-an','-vf','fps=24,scale=640:360:force_original_aspect_ratio=decrease:flags=neighbor,pad=640:360:(ow-iw)/2:(oh-ih)/2:color=0x111319','-frames:v',str(n),'-c:v','libx264','-threads','1','-g','24','-preset','ultrafast','-crf','18','-pix_fmt','yuv420p',str(dest)]
 subprocess.run(cmd,check=True);clips.append(dest)
listing=media/'concat.txt';listing.write_text(''.join("file '"+str(p)+"'\n"for p in clips))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(listing),'-c:v','copy','-movflags','+faststart',str(game/'monitor_montado.mp4')],check=True)
mixed=array.array('h',voice);mixed.extend([0]*(math.ceil(end*sr)-len(mixed)))
with wave.open(str(ROOT/'assets/voz/narracao_mix.wav'),'wb')as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(mixed.tobytes())
(ROOT/'timeline.json').write_text(json.dumps(dict(fps=FPS,frames=N,duration=end,voice_duration=vd,shots=shots),indent=2))
(ROOT/'audio.json').write_text(json.dumps(dict(**intake,frames=N,speed_changed=False,pitch_changed=False,trimmed=False,alignment='Supplied Sonic voice aligned by phrase. Complete source audio; gameplay audio muted.'),ensure_ascii=False,indent=2))
public=[{k:v for k,v in r.items()if k not in ['local_path','probe']}for r in records]
(ROOT/'source_manifest.json').write_text(json.dumps(dict(package='12 - Sonic.zip',source='User-provided Google Drive archive',files=public,video_derivatives=derivatives,images_published=list(mapping)+['7256p5.jpg'],editorial='Normal Sonic is illustrated with official Sonic Dash gameplay. Sonic Freedom is a neutral example for the fangame category, not a claim that this particular game is adult or bizarre. Search and archive interfaces are authored, with fully hidden results and no fetish images or foot closeups. The three question cards are a single comic metaphor. Sonic.exe and the variant montage are fan creations, not official SEGA versions. The arcade and its exit menu are authored illustrations, not footage of the original Sonic.exe game.',unused='Sonic Colors footage, Shin Sonic animation, fetish images, orphan-violence meme, the failure meme and other unused images remain outside Git. No old Ugly Sonic story is included. Raw archive, ASR and personal gesture reference are not published.' ),ensure_ascii=False,indent=2))
print('SONIC_ASSETS_READY',N,end,flush=True)
