"""Check actual exports, complete voice, moving CRT and editable project timing."""
from pathlib import Path
import json,zipfile,subprocess,hashlib,wave
import numpy as np
from PIL import Image,ImageOps,ImageDraw,ImageFont

P=Path(__file__).resolve().parent;OUT=P/'output'
info=json.loads((P/'timeline.json').read_text());edit=json.loads((P/'edicao.json').read_text())
C=Path(info.get('cache','/workspace/attachments/jogos_cancelar'))
TAG='';FILMORA=OUT/('Filmora'+TAG)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
with wave.open(str(P/'assets/voz/voz_completa.wav'))as w:source=w.readframes(w.getnframes());source_frames=w.getnframes();sr=w.getframerate()
with wave.open(str(P/'assets/voz/voz_timeline.wav'))as w:
    padded=w.readframes(w.getnframes());assert padded[:len(source)]==source
    assert set(padded[len(source):])<={0}
videos=[]
for suffix,size in [('9x16',(1080,1920)),('16x9',(1920,1080))]:
    p=OUT/f'Bully_Cancelar{TAG}_{suffix}.mp4';d=probe(p)
    v=next(s for s in d['streams']if s['codec_type']=='video');a=next(s for s in d['streams']if s['codec_type']=='audio')
    assert (v['width'],v['height'])==size and v['r_frame_rate']=='30/1'
    assert abs(float(d['format']['duration'])-info['duration'])<.035
    assert int(v['nb_frames'])==round(info['duration']*30)
    assert abs(float(a['duration'])-info['duration'])<.04
    if suffix=='9x16':
        base=probe(FILMORA/f'midias/Bully_base{TAG}_{suffix}.mp4')
        assert all(s['codec_type']!='audio'for s in base['streams'])
    videos.append(dict(file=p.name,resolution=list(size),fps=30,frames=int(v['nb_frames']),duration=float(d['format']['duration']),sha256=sha(p)))
    subprocess.run(['ffmpeg','-v','error','-i',str(p),'-map','0:v:0','-map','0:a:0','-f','null','-'],check=True)
frames=C/'frames'
crt=[]
for n in [round(t*info['fps'])+1 for t in [.1,.4,.7,1.,1.3]]:
    im=Image.open(frames/f'frame_{n:04d}.png').convert('RGB').crop((305,153,475,290))
    crt.append(hashlib.sha256(im.tobytes()).hexdigest())
assert len(set(crt))>=4,'The monitor froze'
host=[sha(frames/f'frame_{n:04d}.png')for n in[round(t*info['fps'])+1 for t in[3.1,3.4,3.7,4.0,4.3,4.6]]]
assert len(set(host))>=5,'The host animation froze'
face_changes=None
if info.get('revision',1)>=2:
    # Fixed camera, fixed pose and fixed lighting: only the texture selector
    # changes. This catches the seated-face bug that whole-frame hashes missed.
    images=[np.asarray(Image.open(C/f'face_control_{i:03d}.png').convert('RGB'))[48:96,163:223]for i in[31,32,33,35,107]]
    face_changes=[int(np.count_nonzero(images[0]!=im))for im in images[1:]]
    assert min(face_changes)>100,('Face textures did not visibly change',face_changes)
assert edit['titles']==[], 'No narration text overlays authorized'
projects=[]
for suffix in ['9x16']:
    p=FILMORA/f'Bully{TAG}_{suffix}.wfp'
    with zipfile.ZipFile(p)as z:
        assert z.testzip()is None
        n=next(n for n in z.namelist()if n.endswith('timeline.wesproj'));d=json.loads(z.read(n))
        assert len(d['timelineInfos'])==1
        main=d['timelineInfos'][0];resources={r['sourceUuid']:r for r in d['resources']}
        assert d['currentTimelineId']==main['timelineId']
        assert [main['resolutionWidth'],main['resolutionHeight']]==([1080,1920]if suffix=='9x16'else[1920,1080])
        video_clips=main['trackInfos'][11]['clipList'];assert len(video_clips)==len(info['shots'])
        assert video_clips[0]['tlBegin']==0 and video_clips[-1]['tlEnd']==round(info['duration']*1e7)
        assert all(a['tlEnd']==b['tlBegin']for a,b in zip(video_clips,video_clips[1:]))
        count=0
        for track in main['trackInfos']:
            for c in track['clipList']:
                count+=1;assert c['tlEnd']>c['tlBegin']
                assert abs((c['outPoint']-c['inPoint'])-(c['tlEnd']-c['tlBegin']))<=1
                if c.get('filename'):
                    r=resources[c['sourceUuid']];assert c['filename']==r['filename']
                    filename=r['filename'].removeprefix('file:./')
                    media=FILMORA/filename;assert media.is_file(),filename
                    assert c['outPoint']<=r['mediaLength']+1
                    speed=json.loads(c['speed']['speedParam'])
                    assert all(k['_value']==1 for k in speed['keyframeSets'])
                    assert not c['speed']['reverse']
                    assert abs(c['speed']['offsetEnd']-c['outPoint']/1e7)<.000001
                if c['type']==4:
                    script=json.loads(c['scriptBuf'])
                    assert c['scriptBufSize']==len(c['scriptBuf'].encode())
                    assert script['Text']in[t['text']for t in edit['titles']]
        projects.append(dict(file=p.name,clips=count,video_clips=len(video_clips),native_titles=len(main['trackInfos'][13]['clipList']),all_media_resolve=True,explicit_speed_1x=True))
bundle=OUT/f'Bully_Filmora{TAG}.zip'
with zipfile.ZipFile(bundle)as z:
    assert z.testzip()is None and sum(n.endswith('.wfp')for n in z.namelist())==1
    assert all('midias/'+Path(r['filename']).name in z.namelist()for r in resources.values())
# Human-readable contact sheets use actual final frames, separately framed.
for suffix in ['9x16','16x9']:
    pictures=sorted(C.glob(f'final_{suffix}_*.jpg'))
    tile=(216,384)if suffix=='9x16'else(384,216)
    cols=4 if suffix=='9x16'else 3
    rows=(len(pictures)+cols-1)//cols
    sheet=Image.new('RGB',(cols*tile[0],rows*(tile[1]+26)),(25,26,31));draw=ImageDraw.Draw(sheet)
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
    for i,p in enumerate(pictures):
        im=Image.open(p).resize(tile,Image.Resampling.NEAREST);x=i%cols*tile[0];y=i//cols*(tile[1]+26)
        sheet.paste(im,(x,y));time=(int(p.stem.rsplit('_',1)[1])-1)/info['fps']
        draw.text((x+7,y+tile[1]+4),f'{time:05.1f}s',font=font,fill='white')
    sheet.save(OUT/f'Previa_Cenas{TAG}_{suffix}.jpg',quality=94)
record=dict(videos=videos,projects=projects,full_voice_pcm_preserved=True,voice_duration=source_frames/sr,
            timeline_duration=info['duration'],crt_unique_samples=len(set(crt)),host_unique_samples=len(set(host)),
            composited_3d_frames=len(list(frames.glob('frame_*.png'))),
            held_graphic_frames=sum(1 for sh in info['shots']if sh['kind']=='archive'for f in range(sh['start'],sh['end']+1)if(f-sh['start'])%3),
            actual_blender_frames=sum(1 for sh in info['shots']if sh['kind']not in['photo','game']for f in range(sh['start'],sh['end']+1)if sh['kind']!='archive'or(f-sh['start'])%3==0),zip_integrity=True,bundle_sha256=sha(bundle),
            filmora_native_open_test=False,whole_frame_shake=False,revision=info.get('revision',1),
            controlled_seated_face_pixel_changes=face_changes)
(P/'validacao.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('BULLY_DELIVERY_VALIDATED',json.dumps(record,ensure_ascii=False),flush=True)
