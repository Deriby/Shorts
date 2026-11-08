"""Amostra de 15 s + projeto experimental Filmora com efeitos copiados.

Não altera o longo ou os masters. O render MP4 aproxima os plugins;
o WFP retém as configurações nativas para validação no Filmora do usuário.
"""
from pathlib import Path
import subprocess, json, zipfile, copy, uuid, hashlib, wave, math, base64
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

P=Path(__file__).resolve().parent
PROD=P.parent
OUT=P/'output'; WORK=P/'renders'; MEDIA=WORK/'midias'
for d in [OUT,WORK,MEDIA]:d.mkdir(exist_ok=True)
REFERENCE=PROD/'14-montagem-longo/assets/Referencia_Filmora_original.wfp'
MASTER=PROD/'07-tracer/output/Tracer_Personagens_que_a_internet_estragou_16x9.mp4'
FPS=60; CARD=248/FPS; N_BODY=652; BODY=N_BODY/FPS; SOURCE_START=334/24
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-BoldOblique.ttf'
MONO='/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
MAIN_ID='{204E72A3-B517-44d4-806F-9E9D84D5F904}'
# In/out boundaries follow the approved interview's changes of camera.
SHOTS=[(0,31/24,1,1,.5,.5),(31/24,62/24,1,1.12,.5,.5),
       (62/24,93/24,1,1.87,.60,.52),(93/24,144/24,1.1,1.32,.44,.53),
       (144/24,158/24,1.55,1.55,.60,.52),(158/24,187/24,1.08,1.35,.44,.53),
       (187/24,BODY,1,2.08,.60,.52)]
SHOTS=[(round(a*60)/60,round(b*60)/60,z0,z1,x,y)for a,b,z0,z1,x,y in SHOTS]

def run(args):subprocess.run([str(a)for a in args],check=True)
def ticks(t):return round(t*1e7)
def uid():return str(uuid.uuid4())
def wav(path):
    with wave.open(str(path))as w:
        assert w.getframerate()==44100
        return np.frombuffer(w.readframes(w.getnframes()),'<i2').reshape(-1,w.getnchannels()).astype('float32')/32768
def savewav(path,a):
    with wave.open(str(path),'wb')as w:
        w.setnchannels(a.shape[1]);w.setsampwidth(2);w.setframerate(44100)
        w.writeframes(np.clip(np.round(a*32768),-32768,32767).astype('<i2').tobytes())

def make_assets():
    # Working source uses exact displayed frames, with no camera effects baked.
    run(['ffmpeg','-v','error','-y','-ss',str(SOURCE_START),'-i',MASTER,'-an','-t',str(BODY),
         '-vf','fps=60','-c:v','libx264','-preset','veryfast','-crf','17','-pix_fmt','yuv420p',
         '-video_track_timescale','60000','-threads','3',MEDIA/'tracer_take.mp4'])
    a=wav(PROD/'07-tracer/assets/voz/narracao_completa.wav')
    start=round(SOURCE_START*44100);n=round(BODY*44100)
    voice=np.zeros((n,2),np.float32);part=a[start:start+n];voice[:len(part)]=part
    savewav(MEDIA/'tracer_voz.wav',voice)
    sting=wav(PROD/'14-montagem-longo/assets/vinheta_referencia.wav')
    savewav(MEDIA/'vinheta.wav',sting)
    # Already prepared from the supplied MP4 using aligned clean Tifa narration.
    music=wav(MEDIA/'musica_referencia.wav')[:n].copy()
    if len(music)<n:raise ValueError('Music reference is too short')
    tt=np.arange(n)/44100
    music*=np.minimum(tt/.15,1)[:,None]
    music*=np.where(tt>7.79,.16,1)[:,None]  # leave the final question exposed
    music*=np.minimum(np.maximum(BODY-tt,0)/.20,1)[:,None]
    savewav(MEDIA/'musica_teste.wav',music)
    body=voice+music
    assert abs(body).max()<1
    savewav(WORK/'audio_teste.wav',np.concatenate([sting,body]))
    # Match the original 2B chapter's source aspect ratios and native transforms.
    portrait=Image.open(PROD/'07-tracer/assets/memes/tracer_retrato.png').convert('RGB')
    portrait=ImageOps.fit(portrait,(2400,3508),method=Image.Resampling.LANCZOS,centering=(.48,.45))
    portrait.save(MEDIA/'tracer_retrato.jpg',quality=94)
    title=Image.new('RGBA',(1536,1024))
    d=ImageDraw.Draw(title)
    # Angular gold extrusion, replacing the flat italic labels of the last test.
    size=285
    while True:
        f=ImageFont.truetype(FONT,size)
        if d.textbbox((0,0),'TRACER',font=f)[2]<1410:break
        size-=2
    x=(1536-d.textbbox((0,0),'TRACER',font=f)[2])//2;y=210
    for depth in range(40,0,-1):
        color=(135+depth,55+depth,8,255)
        d.text((x+depth,y+depth), 'TRACER',font=f,fill=color,stroke_width=8,stroke_fill=(45,27,15,255))
    d.text((x,y),'TRACER',font=f,fill='#ffd532',stroke_width=5,stroke_fill='#ffef6c')
    sub=ImageFont.truetype(FONT,107);text='OVERWATCH'
    sx=(1536-d.textbbox((0,0),text,font=sub)[2])//2
    for depth in range(14,0,-1):d.text((sx+depth,570+depth),text,font=sub,fill='#ba5721',stroke_width=4,stroke_fill='#402a20')
    d.text((sx,570),text,font=sub,fill='#ffe35d',stroke_width=2,stroke_fill='#85531b')
    title.save(MEDIA/'tracer_logo_3d.png')

def zoom_at(t,shot):
    a,b,z0,z1,fx,fy=shot
    if z1>=1.87:
        # Reference's 100 -> 187 in 0.25 s, then a slower creep towards 208.
        q=t-a
        return z0+(min(z1,1.87)-z0)*min(q/.25,1)+max(z1-1.87,0)*max(q-.25,0)/max(b-a-.25,.01)
    return z0+(z1-z0)*np.clip((t-a)/(b-a),0,1)

def global_look(frame,t,card=False):
    f=np.asarray(frame).astype(np.float32)/255
    # Preview approximation only; the WFP retains literal native plugin data.
    bright=np.maximum(f-.55,0)/.45
    glow=np.asarray(Image.fromarray(np.uint8(bright*255)).filter(ImageFilter.GaussianBlur(1.25))).astype(np.float32)/255
    f=np.clip(f+.40*(1-f)*glow,0,1)
    # The user rejected the simulated whole-screen oscillation. The PS1
    # geometry motion is already present in the approved master frames.
    return np.uint8(np.clip(f,0,1)*255)

def render_preview():
    poster=Image.open(MEDIA/'tracer_retrato.jpg').convert('RGB')
    logo=Image.open(MEDIA/'tracer_logo_3d.png').convert('RGBA');logo.thumbnail((230,154),Image.Resampling.LANCZOS)
    hud=ImageFont.truetype(MONO,9)
    poster_scaled=poster.resize((round(640*2400/3508),640),Image.Resampling.LANCZOS)
    xx,yy=np.meshgrid(np.linspace(-1,1,640),np.linspace(-1,1,360))
    vignette=np.clip(1-.7*np.maximum(abs(xx)-.48,0)/.52,0,1)[...,None]
    out=OUT/'Teste_Tracer_Estilo_15s_16x9.mp4'
    enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','640x360','-r','60','-i','pipe:0',
          '-i',str(WORK/'audio_teste.wav'),'-vf','scale=1920:1080:flags=neighbor','-c:v','libx264','-preset','veryfast',
          '-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','44100','-ac','2','-threads','3',
          '-t','15','-movflags','+faststart',str(out)],stdin=subprocess.PIPE)
    for i in range(248):
        t=i/60
        c=Image.new('RGB',(640,360),(12,12,16))
        c.paste(poster_scaled,((640-poster_scaled.width)//2,round(-235+t/CARD*200)))
        layer=Image.new('RGBA',(640,360));d=ImageDraw.Draw(layer)
        for y in range(0,360,3):d.line((0,y,640,y),fill=(0,0,0,18))
        c=Image.alpha_composite(c.convert('RGBA'),layer)
        c.alpha_composite(logo,((640-logo.width)//2,round(145-logo.height*.4)))
        d=ImageDraw.Draw(c)
        for pos,text in [((164,22),'PLAY ▷'),((164,34),'SP'),((399,22),'VCR TAPE'),((399,34),'00:00:02'),((164,312),'VOLUME'),((164,324),'|||||||||---')]:
            d.text(pos,text,font=hud,fill=(240,240,242,180))
        a=global_look(c.convert('RGB'),t,True).astype(np.float32)*vignette
        fade=min(t/.10,1,(CARD-t)/.10)
        enc.stdin.write(np.uint8(np.clip(a*fade,0,255)).tobytes())
    dec=subprocess.Popen(['ffmpeg','-v','error','-i',str(MEDIA/'tracer_take.mp4'),'-vf','scale=640:360:flags=neighbor',
                          '-pix_fmt','rgb24','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE)
    for i in range(N_BODY):
        raw=dec.stdout.read(640*360*3)
        if len(raw)!=640*360*3:raise ValueError(f'Missing source frame {i}')
        im=Image.frombytes('RGB',(640,360),raw);t=i/60
        shot=next(s for s in SHOTS if s[0]<=t<s[1])
        z=zoom_at(t,shot);cw=640/z;ch=360/z
        x=(640-cw)*shot[4];y=(360-ch)*shot[5]
        im=im.crop((round(x),round(y),round(x+cw),round(y+ch))).resize((640,360),Image.Resampling.NEAREST)
        enc.stdin.write(global_look(im,t+CARD).tobytes())
    dec.stdout.close();assert dec.wait()==0
    enc.stdin.close();assert enc.wait()==0
    return out

def file_resource(proto,path):
    r=copy.deepcopy(proto);r['sourceUuid']=uid();r['filename']='file:./midias/'+path.name
    r['createDate']=-1;r['modifyDate']=0
    for k in ['audStreamInfo','vidStreamInfo']:
        for s in r.get(k,[]):
            s['duration']=BODY if path.suffix=='.mp4'else 0
    return r

def transform(c,z0,z1,fx,fy,start,end):
    basic=c['effectChainList'][0]
    basic['effectList']=[e for e in basic['effectList']if e.get('display')in ['crop-pan-zoom','transform']]
    e=next(e for e in basic['effectList']if e['display']=='transform')
    e['thisUId']=uid();e['paramList']=[{'name':'EnableTransform','fxParam':{'paramType':5,'unValue':1}}]
    keys=[(start,z0)]
    if z1>=1.87:keys.append((min(end,start+.25),min(z1,1.87)))
    keys.append((end,z1))
    values={'Scale_x':[(t,z*100)for t,z in keys],'Scale_y':[(t,z*100)for t,z in keys],
            '_Anchor_x':[(start,.5)],'_Anchor_y':[(start,.5)],
            'Position_x':[(t,.5-(fx-.5)*(z-1))for t,z in keys],
            'Position_y':[(t,.5-(fy-.5)*(z-1))for t,z in keys]}
    e['paramMapList']=[]
    for name,points in values.items():
        e['paramList'].append({'name':name,'fxParam':{'paramType':3,'unValue':points[0][1]}})
        data={'Version':2,'ParameterType':0,'keyframeSets':[{'_time':t,'Interpolation':1,'_value':v}for t,v in points]}
        e['paramMapList'].append({'key':3,'name':name,'keyFrame':{'parameter':json.dumps(data,separators=(',',':'))}})
    for chain in c['effectChainList'][1:]:chain['effectList']=[]

def make_project(total_duration=15.0, project_name='Teste_Tracer_15s'):
    with zipfile.ZipFile(REFERENCE)as z:original={n:z.read(n)for n in z.namelist()}
    main_path=f'ProjectFolder/Medias/{MAIN_ID}/timeline.wesproj'
    v=json.loads(original[main_path]);old=copy.deepcopy(v)
    old_items=json.loads(original['ProjectFolder/Medias/medias_info.json'])['media_items']
    def media_link(c):
        return next((base64.b64decode(u['data']).decode().strip('\0')for u in c.get('userData',[])if u['key']==10),None)
    def link_clip(c,r):
        c['filename']=r['filename'];c['sourceUuid']=r['sourceUuid']
        for u in c.get('userData',[]):
            if u['key'] in [3,10,50]:
                value=('{'+r['sourceUuid'].upper()+'}')if u['key']==10 else ('{'+uid().upper()+'}' if u['key']==3 else Path(r['filename']).stem)
                raw=value.encode();raw+=b'\0'*max(0,u['size']-len(raw))
                u['data']=base64.b64encode(raw).decode();u['size']=len(raw)
        c['userData']=[u for u in c.get('userData',[])if u['key']not in [73,74]]
        for ch in c.get('effectChainList',[]):
            for e in ch.get('effectList',[]):
                if 'thisUId' in e:e['thisUId']=uid()
    main=copy.deepcopy(v['timelineInfos'][0]);tracks=main['trackInfos']
    for tr in tracks:tr['clipList']=[]
    card=copy.deepcopy(next(c for c in old['timelineInfos'][0]['trackInfos'][8]['clipList']if c.get('timelineId')==53))
    card_origin=card['tlBegin']
    for key in ['postTransition','preTransition']:
        if key in card:
            for tk in ['tlBegin','tlEnd']:
                if tk in card[key]:card[key][tk]-=card_origin
    card.update(tlBegin=0,tlEnd=ticks(CARD),inPoint=0,outPoint=ticks(CARD),thisUId=uid())
    tracks[8]['clipList']=[card]
    resources=[]
    # Clone original typed resource metadata; media files are bundled separately.
    def orig_resource(text):return next(r for r in old['resources']if text in r.get('filename',''))
    def add_resource(path,proto,video=False,audio=False,image=False):
        r=file_resource(proto,MEDIA/path)
        if video:
            r['mediaLength']=ticks(BODY)
            for s in r['vidStreamInfo']:
                s.update(frameRate={'num':60,'den':1},maxFrameRate={'num':60,'den':1},totalFrames=N_BODY,
                         streamLength=ticks(BODY),width=1920,height=1080)
            r['audioStreamCount']=0;r.pop('audStreamInfo',None)
        if audio:
            a=wav(MEDIA/path);dur=len(a)/44100
            r.update(mediaLength=ticks(dur),videoStreamCount=0,audioStreamCount=1,streamType=3)
            r.pop('vidStreamInfo',None)
            s=copy.deepcopy(orig_resource('94838.wav')['audStreamInfo'][0])
            s.update(audStreamId=0,sampleRate=44100,channels=2,duration=dur,streamLength=ticks(dur),
                     description='Uncompressed PCM',bitDepth=16,bitRate=1411200,bytesPerSecond=176400)
            r['bitRate']=1411200
            r['audStreamInfo']=[s]
        if image:
            im=Image.open(MEDIA/path);s=r['vidStreamInfo'][0];s.update(width=im.width,height=im.height)
        resources.append(r);return r
    take=add_resource('tracer_take.mp4',orig_resource('2 - Tifa_'),video=True)
    voice=add_resource('tracer_voz.wav',orig_resource('94838.wav'),audio=True)
    music=add_resource('musica_teste.wav',orig_resource('94838.wav'),audio=True)
    sting=add_resource('vinheta.wav',orig_resource('94838.wav'),audio=True)
    portrait=add_resource('tracer_retrato.jpg',orig_resource('enbt8eahlmya1'),image=True)
    logo=add_resource('tracer_logo_3d.png',orig_resource('7b649ea7'),image=True)
    video_proto=old['timelineInfos'][0]['trackInfos'][8]['clipList'][-1]
    for a,b,z0,z1,fx,fy in SHOTS:
        c=copy.deepcopy(video_proto)
        for k in ['postTransition','preTransition','stabilization','stabilizeAnalysisData','face_cluster']:c.pop(k,None)
        c.update(filename=take['filename'],sourceUuid=take['sourceUuid'],thisUId=uid(),
                 inPoint=ticks(a),outPoint=ticks(b),tlBegin=ticks(CARD+a),tlEnd=ticks(CARD+b),streamId=0)
        c.pop('speed',None)
        link_clip(c,take)
        transform(c,z0,z1,fx,fy,a,b);tracks[8]['clipList'].append(c)
    audio_proto=old['timelineInfos'][0]['trackInfos'][1]['clipList'][0]
    for track,r,start,duration in [(6,sting,0,CARD),(7,voice,CARD,BODY),(1,music,CARD,BODY)]:
        c=copy.deepcopy(audio_proto);c.update(filename=r['filename'],sourceUuid=r['sourceUuid'],streamId=0,
                thisUId=uid(),tlBegin=ticks(start),tlEnd=ticks(start+duration),inPoint=0,outPoint=ticks(duration))
        c.pop('speed',None)
        link_clip(c,r)
        for ch in c['effectChainList']:ch['effectList']=[]
        tracks[track]['clipList']=[c]
    exact=[]
    for i in [12,14,16]:
        c=copy.deepcopy(old['timelineInfos'][0]['trackInfos'][i]['clipList'][0])
        c.update(tlBegin=0,tlEnd=ticks(total_duration),outPoint=c['inPoint']+ticks(total_duration))
        tracks[i]['clipList']=[c]
        exact.append(c['effectChainList'])
    nested=[]
    for tid,res in [(53,portrait),(73,logo)]:
        t=copy.deepcopy(next(t for t in old['timelineInfos']if t['timelineId']==tid))
        for tr in t['trackInfos']:
            for c in tr['clipList']:
                if c.get('filename'):
                    link_clip(c,res)
        nested.append(t)
    v.update(resources=resources,timelineInfos=[main,*nested],currentTimelineId=46)
    original[main_path]=json.dumps(v,separators=(',',':')).encode()
    meta=json.loads(original['ProjectFolder/project_info.json'])
    meta.update(project_file_name=project_name,project_timeline_duration=ticks(total_duration),project_current_position=0,
                proj_zip_save_path=project_name+'.wfp',proj_cover_proj_path='',project_custom_cover=False)
    original['ProjectFolder/project_info.json']=json.dumps(meta).encode()
    extra_path=f'ProjectFolder/Medias/{MAIN_ID}/extra.json'
    extra=json.loads(original[extra_path])
    original[extra_path]=json.dumps(extra).encode()
    items={MAIN_ID:{'name':'Teste Tracer 15s','id':MAIN_ID,'timeline_uuid':'{8F460D3A-5E28-481e-A846-4717CCFFE1AB}',
             'media_type':1048576,'duration':ticks(total_duration),'download_url':'','enable_modify_mediaId':0}}
    media_ids=[]
    # Compound clips have media IDs in addition to their timeline IDs.
    compound_ids=[media_link(card)]
    compound_ids.append(next(media_link(c)for tr in nested[0]['trackInfos']for c in tr['clipList']if c.get('timelineId')==73 and media_link(c)))
    for comp_id,tid in zip(compound_ids,[53,73]):
        items[comp_id]=copy.deepcopy(old_items[comp_id]);items[comp_id]['duration']=ticks(CARD)
        sub=copy.deepcopy(v);sub['currentTimelineId']=tid
        sub['timelineInfos']=[t for t in nested if t['timelineId']>=tid]
        sub['resources']=[portrait,logo]if tid==53 else[logo]
        original[f'ProjectFolder/Medias/{comp_id}/timeline.wesproj']=json.dumps(sub,separators=(',',':')).encode()
    for r in resources:
        mid='{'+r['sourceUuid'].upper()+'}';media_ids.append(mid)
        items[mid]={'name':Path(r['filename']).name,'download_url':r['filename'].replace('file:./','./'),
                    'id':mid,'media_type':8 if r.get('videoStreamCount')and r['mediaLength']else(16 if not r.get('audioStreamCount')else 4),
                    'media_length':r['mediaLength'],'stream_idx':0,'mark_info_list':[{'mark_in':-1,'mark_out':-1}]}
        # Native sourceInfo cache, generated from the same typed resource.
        src={'basicInfo':{k:r[k]for k in ['streamType','fourCC','mediaLength','videoStreamCount','audioStreamCount','bitRate']if k in r},
             'vidStreamInfos':r.get('vidStreamInfo',[]),'audStreamInfos':r.get('audStreamInfo',[])}
        original[f'ProjectFolder/Medias/{mid}/media.json']=json.dumps({'version':'1.1.5','file_name':items[mid]['download_url'],
                                                                   'sourceInfo':src}).encode()
    # Filmora serializes repeated media_item keys, not a JSON array. Preserve that convention.
    struct='{"media_structure":{"Folder":{'+','.join('"media_item":'+json.dumps(m)for m in [*media_ids,*compound_ids])+'},"media_item":'+json.dumps(MAIN_ID)+'},"media_items":'+json.dumps(items)+'}'
    original['ProjectFolder/Medias/medias_info.json']=struct.encode()
    project=OUT/(project_name+'.wfp')
    with zipfile.ZipFile(project,'w',zipfile.ZIP_DEFLATED)as z:
        for name,data in original.items():z.writestr(name,data)
    (P/'efeitos_nativos_copiados.json').write_text(json.dumps({'global_effect_chains':exact,'chapter_effect_chain':card['effectChainList'],
        'plugin_execution_in_cloud':False,'filmora_open_test':'pending on user computer'},ensure_ascii=False,indent=2))
    return project

def package(project):
    instructions=('TESTE TRACER — 15 SEGUNDOS\n\nExtraia o ZIP antes de abrir o projeto Teste_Tracer_15s.wfp no Filmora.\n'
      'Se ele pedir arquivos ausentes, localize o primeiro na pasta midias deste pacote. Os demais estão nessa mesma pasta.\n'
      'Os efeitos globais e os da vinheta foram copiados do seu WFP. Requer os mesmos plugins/recursos da sua instalação.\n'
      'A abertura no Filmora ainda precisa ser validada. O MP4 é uma prévia com aproximações dos plugins.\n'
      'O projeto é uma cópia isolada de 15s e não altera o seu projeto original.\n')
    (OUT/'LEIA_PRIMEIRO.txt').write_text(instructions)
    # Deliverable archive (not a duplicated raw download).
    bundle=OUT/'Teste_Tracer_Filmora_15s.zip'
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED)as z:
        z.write(project,project.name);z.writestr('LEIA_PRIMEIRO.txt',instructions)
        for p in MEDIA.iterdir():
            if p.name=='musica_referencia.wav':continue
            z.write(p,'midias/'+p.name)
    return bundle

def main():
    make_assets();print('ASSETS_READY',flush=True)
    project=make_project();print('NATIVE_PROJECT_READY',flush=True)
    preview=render_preview();print('PREVIEW_READY',flush=True)
    bundle=package(project)
    report={'duration':15,'resolution':[1920,1080],'fps':60,'chapter_frames':248,'body_frames':N_BODY,
        'source_start':SOURCE_START,'source_end':SOURCE_START+BODY,'voice_speed':1,'voice_pitch_changed':False,
        'recovered_music':json.loads((P/'recuperacao_trilha.json').read_text()),
        'native_effects_copied':True,'native_project_tested_in_filmora':False,'preview_plugins':'approximated',
        'preview_added_screen_oscillation':False,
        'original_masters_changed':False,'shot_changes':SHOTS,'outputs':[preview.name,project.name,bundle.name]}
    (P/'producao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print('READY',bundle,flush=True)

if __name__=='__main__':main()
