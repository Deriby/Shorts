"""Check project boundaries, native edit preservation, sources and cache metadata."""
from pathlib import Path
import json,zipfile,math,hashlib
from separar import P,OUT,SOURCE,SOURCE_SHA,ROOT,TL,META,MI,sha,timeline_dependencies

with zipfile.ZipFile(SOURCE)as z:original=json.loads(z.read(TL))
source_main=next(t for t in original['timelineInfos']if t['timelineId']==original['currentTimelineId'])
source_clips={c['thisUId']:c for tr in source_main['trackInfos']for c in tr['clipList']}
manifest=json.loads((P/'manifesto.json').read_text());reports=[]
assert len(manifest['projects'])==12
for rec in manifest['projects']:
    path=OUT/rec['project'];checked=0;transform_times=0;portrait_resources=0
    with zipfile.ZipFile(path)as z:
        assert z.testzip() is None
        project=json.loads(z.read(TL));meta=json.loads(z.read(META));items=json.loads(z.read(MI))['media_items']
        main=next(t for t in project['timelineInfos']if t['timelineId']==project['currentTimelineId'])
        assert meta['project_timeline_resolution']==[1080,1920]
        assert meta['project_timeline_ratio']==[9,16]
        assert meta['project_timeline_framerate']==[60,1]
        assert [main['resolutionWidth'],main['resolutionHeight']]==[1080,1920]
        assert meta['project_current_position']==0
        assert len(project['timelineInfos'])==len(original['timelineInfos'])
        assert items[ROOT]['duration']==meta['project_timeline_duration']
        for tr in main['trackInfos']:
            for c in tr['clipList']:
                assert 0<=c['tlBegin']<c['tlEnd']<=meta['project_timeline_duration']
                assert c.get('outPoint',1)>c.get('inPoint',0)
                old=source_clips[c['thisUId']]
                # Every non-transform native effect chain stays byte-equivalent.
                for oldch,newch in zip(old.get('effectChainList',[]),c.get('effectChainList',[])):
                    if oldch['name']!='Basic':assert oldch==newch,(path.name,c['thisUId'],oldch['name'])
                    for oe,ne in zip(oldch.get('effectList',[]),newch.get('effectList',[])):
                        if oe.get('display')!='transform':assert oe==ne
                        else:
                            oldcurves={p['name']:p for p in oe.get('paramMapList',[])if 'keyFrame'in p}
                            for curve in ne.get('paramMapList',[]):
                                if 'keyFrame'not in curve:continue
                                before=json.loads(oldcurves[curve['name']]['keyFrame']['parameter'])
                                after=json.loads(curve['keyFrame']['parameter'])
                                assert [k['_time']for k in before['keyframeSets']]==[k['_time']for k in after['keyframeSets']]
                                assert all(math.isfinite(k['_value'])for k in after['keyframeSets'])
                                transform_times+=1
                for key in ('preTransition','postTransition'):
                    if key not in c:continue
                    assert key in old
                    expected=dict(old[key]);actual=dict(c[key])
                    for field in ('tlBegin','tlEnd'):expected.pop(field,None);actual.pop(field,None)
                    assert expected==actual
                if 'filename'in c and c.get('type')in (1,2):
                    assert 'speed'in c
                    assert c['speed']['speedParam']==old['speed']['speedParam']
                checked+=1
        assert min(c['tlBegin']for tr in main['trackInfos']for c in tr['clipList'])==0
        assert max(c['tlEnd']for tr in main['trackInfos']for c in tr['clipList'])==meta['project_timeline_duration']
        ids=timeline_dependencies(main,project['timelineInfos'])
        assert ids==set(rec['dependent_timelines'])
        # Inspect all native child caches, not only the top-level resource list.
        for name in z.namelist():
            if not name.endswith(('.json','.wesproj')):continue
            data=json.loads(z.read(name))
            if not isinstance(data,dict):continue
            for r in data.get('resources')or[]:
                if not r.get('filename','').endswith('9x16.mp4'):continue
                portrait_resources+=1
                video=r['vidStreamInfo'][0]
                assert [video['width'],video['height']]==[1080,1920]
                assert video['frameRate']=={'num':24,'den':1}
                assert abs(r['mediaLength']/1e7-video['totalFrames']/24)<1e-6
            for tl in data.get('timelineInfos')or[]:
                if any(c.get('filename','').endswith('9x16.mp4')for tr in tl.get('trackInfos',[])for c in tr['clipList']):
                    assert [tl['resolutionWidth'],tl['resolutionHeight']]==[1080,1920]
        for media in rec['bundled_media']:
            media_path=path.parent/'midias'/media['name']
            assert media_path.is_file() and sha(media_path)==media['sha256']
    reports.append({'character':rec['character'],'native_clips_compared':checked,'keyframe_curves_with_original_times':transform_times,'portrait_resource_records_checked':portrait_resources,'zip_integrity':True,'vertical_metadata_consistent':True,'source_media_hashes_passed':True,'non_transform_effects_unchanged':True,'audio_speed_curves_preserved':True,'native_open_test':'Not executed in Filmora; structural checks only.'})
assert sha(SOURCE)==SOURCE_SHA
(P/'verificacao.json').write_text(json.dumps({'project_count':len(reports),'source_original_unchanged':True,'projects':reports},ensure_ascii=False,indent=2)+'\n')
print('VERIFIED',len(reports),'projects;',sum(r['native_clips_compared']for r in reports),'native clips')
