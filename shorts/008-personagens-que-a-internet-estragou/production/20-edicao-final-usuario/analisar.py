"""Read-only inventory of the user's completed Filmora edit and native style."""
from pathlib import Path
import json,zipfile,hashlib,collections,statistics

P=Path(__file__).resolve().parent
SOURCE=P/'Massacote_EDICAO_FINAL_USUARIO.wfp'
with zipfile.ZipFile(SOURCE) as z:
    assert z.testzip() is None
    meta=json.loads(z.read('ProjectFolder/project_info.json'))
    candidates=[(n,json.loads(z.read(n))) for n in z.namelist() if n.endswith('/timeline.wesproj')]
    name,project=max(candidates,key=lambda pair:len(pair[1]['timelineInfos']))
    main=next(t for t in project['timelineInfos'] if t['timelineId']==project['currentTimelineId'])
    embedded_media=[n for n in z.namelist() if Path(n).suffix.lower() in {'.mp4','.mov','.mkv','.mp3','.wav','.m4a'}]
effects=collections.Counter();transitions=collections.Counter();keyframes=collections.Counter()
durations=[];segments=collections.defaultdict(list);speeds=collections.Counter()
for tr in main['trackInfos']:
    for c in tr['clipList']:
        if c.get('filename') and c.get('type') in (1,2):
            speeds['movie_audio_clips']+=1
            if 'speed'in c:speeds['explicit_speed']+=1
        if tr['trackType']==1 and c.get('filename','').endswith('.mp4'):
            durations.append((c['tlEnd']-c['tlBegin'])/1e7)
            segments[c['filename'].rsplit('/',1)[-1]].append([c['tlBegin']/1e7,c['tlEnd']/1e7])
        for key in ('preTransition','postTransition'):
            if key in c:
                transition=c[key];transitions[transition.get('display') or transition.get('id') or '(sem nome)']+=1
        for chain in c.get('effectChainList',[]):
            for effect in chain.get('effectList',[]):
                if effect.get('enable',True):effects[effect.get('display') or effect.get('id')]+=1
                for param in effect.get('paramMapList',[]):
                    try:data=json.loads(param['keyFrame']['parameter'])
                    except (KeyError,ValueError,TypeError):continue
                    keyframes[param['name']]+=len(data.get('keyframeSets',[]))
record={
    'filename_received':'Massacote_EDICAO_RECUPERADA_EXPORT_TESTE.wfp',
    'source_upload_id':'file_000000004bc8820e840ac21e130b8b65',
    'saved_as':SOURCE.name,'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'size_bytes':SOURCE.stat().st_size,'original_upload_preserved':True,'archive_integrity':'passed',
    'duration_seconds':meta['project_timeline_duration']/1e7,
    'fps':meta['project_timeline_framerate'],'resolution':meta['project_timeline_resolution'],
    'ratio':meta['project_timeline_ratio'],'filmora_version':meta['project_editor_modify_version'],
    'root_timeline_file':name,'root_timeline_id':main['timelineId'],
    'timeline_count':len(project['timelineInfos']),'resources':len(project['resources']),
    'main_tracks':len(main['trackInfos']),'main_clips':sum(len(tr['clipList'])for tr in main['trackInfos']),
    'embedded_audiovisual_media_count':len(embedded_media),
    'source_media_filenames':list(dict.fromkeys(r['filename']for r in project['resources'])),
    'main_enabled_effect_occurrences':dict(effects.most_common()),
    'main_transition_occurrences':dict(transitions.most_common()),
    'main_transform_keyframe_points':dict(keyframes),
    'main_video_clip_duration_seconds':{'count':len(durations),'median':statistics.median(durations),'min':min(durations),'max':max(durations)},
    'main_file_backed_clip_speed_counts':dict(speeds),
    'video_intervals':dict(segments),
    'approval_source':'User states this completed edit turned out very good and requests matching short projects/style.',
    'native_filmora_render_test':'Not executed in this Linux environment; visual appearance not verified from a rendered movie.',
    'requested_scope':'Use this editing style for upcoming content and editable Filmora projects.',
    'scope_confirmed_by_user':True,
    'split_existing_long_video_requested':False
}
(P/'recebimento_e_estilo.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:record[k]for k in ('sha256','duration_seconds','timeline_count','resources','main_clips','embedded_audiovisual_media_count','main_video_clip_duration_seconds')},ensure_ascii=False))
