"""Add native Filmora motion/transitions to the existing complete edit.

No new 3D render, audio edit, captions, replacement media or speed changes.
Native serializers/plugin identifiers come from the user's final first long edit.
"""
from pathlib import Path
import base64
import copy
import hashlib
import importlib.util
import json
import uuid
import zipfile

P = Path(__file__).resolve().parent
L = P.parent
R = next(p for p in P.parents if (p / 'AGENTS.md').exists())
F = L / 'output/Filmora'
SOURCE = F / 'Massacote_Completo.wfp'
REF = R / 'shorts/008-personagens-que-a-internet-estragou/production/20-edicao-final-usuario/Massacote_EDICAO_FINAL_USUARIO.wfp'
OUT = F / 'Massacote_Completo_Editado.wfp'
ROOT = '{204E72A3-B517-44d4-806F-9E9D84D5F904}'
TL = f'ProjectFolder/Medias/{ROOT}/timeline.wesproj'
LIB = 'ProjectFolder/Medias/medias_info.json'
T = 10_000_000


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode()


def load(path):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        return {name: z.read(name) for name in z.namelist()}


def effects(clip):
    return [e for chain in clip.get('effectChainList', []) for e in chain['effectList']]


def set_userdata(item, key, value):
    data = value.encode()
    for u in item.get('userData', []):
        if u['key'] == key:
            data += b'\0' * max(0, u['size'] - len(data))
            u.update(data=base64.b64encode(data).decode(), size=len(data))


# Authoring by spoken idea/scene, not a cyclic list of zooms. Values are extra
# editorial scale on top of the existing picture, not replacement 3D cameras.
# type, maximum percent; source-time curves are clipped to each original cut.
BEATS = {
    '00_intro': {0: ('reveal', 138), 4: ('push', 150), 6: ('punch', 160)},
    '01_gta_san_andreas': {1: ('push', 146), 2: ('punch', 136), 6: ('reveal', 123), 9: ('pull', 142), 15: ('punch', 130), 16: ('push', 140)},
    '02_bmx_xxx': {1: ('reveal', 146), 6: ('punch', 158), 11: ('punch', 142)},
    '03_bully': {1: ('push', 145), 7: ('reveal', 155), 10: ('punch', 143), 14: ('punch', 137)},
    '04_left_4_dead_2': {1: ('punch', 155), 4: ('push', 125), 6: ('punch', 162), 10: ('reveal', 134)},
    '05_saints_row_iv': {1: ('reveal', 130), 3: ('punch', 166), 6: ('push', 146)},
    '06_gta_v': {1: ('push', 149), 3: ('punch', 132), 8: ('reveal', 161)},
    '07_pokemon_sword_shield': {1: ('punch', 146), 4: ('push', 129), 9: ('punch', 138), 11: ('reveal', 159)},
    '08_night_trap': {1: ('push', 129), 6: ('punch', 156), 7: ('reveal', 124), 9: ('punch', 161)},
    '09_dead_or_alive_xtreme_3': {1: ('reveal', 150), 3: ('push', 143), 6: ('punch', 133), 9: ('reveal', 127), 11: ('push', 145), 12: ('punch', 125)},
    '11_minecraft': {2: ('punch', 132), 4: ('push', 147), 8: ('reveal', 161), 11: ('punch', 137)},
    '12_house_party': {1: ('pull', 149), 4: ('punch', 132), 7: ('push', 146), 10: ('reveal', 130)},
    '13_outro': {0: ('push', 138), 1: ('reveal', 123), 2: ('push', 145), 3: ('punch', 130), 4: ('logo', 109)},
}
# Source-media cut time, real native transition, duration in 30 fps frames.
# Gag inserts retain their existing clean entry/exit and visual punch.
SWITCHES = {
    '00_intro': [(3.466667, 'Fast Bounce', 8), (12.4, 'Basic Zoom In', 8), (23.6, 'Warp Zoom 6', 8)],
    '01_gta_san_andreas': [(2.133333, 'Basic Zoom In', 8), (9.2, 'SwingLeft', 6), (21.866667, 'Fast Bounce', 8), (43.4, 'Warp Zoom 6', 8)],
    '02_bmx_xxx': [(2.833333, 'Basic Zoom In', 8), (14.6, 'Fast Bounce', 8), (22.5, 'SwingRight', 6), (34.533333, 'SwingLeft', 6)],
    '03_bully': [(2.9, 'Basic Zoom In', 8), (14.0, 'SwingLeft', 6), (19.966667, 'Fast Bounce', 8), (45.1, 'Warp Zoom 6', 8)],
    '04_left_4_dead_2': [(3.0, 'Basic Zoom In', 8), (14.0, 'Fast Bounce', 8), (21.433333, 'SwingLeft', 6), (36.133333, 'Warp Zoom 6', 8)],
    '05_saints_row_iv': [(3.2, 'Basic Zoom In', 8), (6.366667, 'SwingRight', 6), (11.6, 'Fast Bounce', 8), (31.4, 'Warp Zoom 6', 8)],
    '06_gta_v': [(3.0, 'Basic Zoom In', 8), (11.533333, 'Fast Bounce', 8), (17.133333, 'SwingLeft', 6), (26.0, 'Warp Zoom 6', 8)],
    '07_pokemon_sword_shield': [(3.0, 'Basic Zoom In', 8), (5.966667, 'SwingLeft', 6), (12.866667, 'Fast Bounce', 8), (40.466667, 'Warp Zoom 6', 8)],
    '08_night_trap': [(7.266667, 'SwingRight', 6), (11.5, 'Basic Zoom In', 8), (27.9, 'Warp Zoom 6', 8), (38.7, 'Fast Bounce', 8)],
    '09_dead_or_alive_xtreme_3': [(3.2, 'Basic Zoom In', 8), (14.0, 'SwingLeft', 6), (22.5, 'Fast Bounce', 8), (37.7, 'Warp Zoom 6', 8)],
    '11_minecraft': [(6.9, 'SwingLeft', 6), (12.3, 'Basic Zoom In', 8), (28.0, 'Fast Bounce', 8), (38.3, 'Warp Zoom 6', 8)],
    '12_house_party': [(3.9, 'Basic Zoom In', 8), (13.4, 'SwingLeft', 6), (19.5, 'Fast Bounce', 8), (41.7, 'Warp Zoom 6', 8)],
    '13_outro': [(5.333333, 'Basic Zoom In', 8), (20.333333, 'Fast Bounce', 6)],
}


def interpolate(points, time):
    if time <= points[0][0]:
        return points[0][1]
    for (a, x), (b, y) in zip(points, points[1:]):
        if a <= time <= b:
            return x + (y - x) * (time - a) / (b - a)
    return points[-1][1]


def profile(mode, peak, duration):
    """Intentional holds and short settles; interpolation is native linear."""
    if mode == 'punch':
        hit = min(.65, duration * .28)
        return [(0, 100), (hit, 100), (hit + .10, peak - 2), (hit + .20, peak), (duration, peak)]
    if mode == 'reveal':
        return [(0, 100), (.10, peak + 1), (.23, peak - 2), (.36, peak), (duration, peak + 1)]
    if mode == 'pull':
        return [(0, peak), (.15, peak), (duration * .55, 106), (duration, 102)]
    if mode == 'logo':
        return [(0, peak), (.15, peak), (.40, 100), (duration, 100)]
    # Gentle opening, faster middle, resting final frame: no periodic breathing.
    return [(0, 100), (duration * .12, 100.5), (duration * .72, peak - 2), (duration * .93, peak), (duration, peak)]


source_hash, reference_hash = sha(SOURCE), sha(REF)
raw, reference = load(SOURCE), load(REF)
data = json.loads(raw[TL])
before = copy.deepcopy(data)
ref = json.loads(reference[TL])
main = next(t for t in data['timelineInfos'] if t['timelineId'] == data['currentTimelineId'])
# The previous generator placed the card hero PNGs on an audio-typed track.
# Correct the lane type so these existing image clips render natively.
main['trackInfos'][12]['trackType'] = 1
ref_main = next(t for t in ref['timelineInfos'] if t['timelineId'] == ref['currentTimelineId'])
prototype = next(e for tr in ref_main['trackInfos'] for c in tr['clipList'] for e in effects(c) if e.get('display') == 'transform' and e.get('paramMapList'))
transitions = {}
for tr in ref_main['trackInfos']:
    if tr['trackType'] != 1:
        continue
    for clip in tr['clipList']:
        for side in ('preTransition', 'postTransition'):
            t = clip.get(side, {})
            if t.get('display') and not t.get('scriptBuf'):
                transitions.setdefault(t['display'], t)
plan = json.loads((L / 'montagem.json').read_text())
audit = []
transition_audit = []


def animate(clip, points, focus, description, scene_kind):
    """Filmora transform times are SOURCE times, never absolute timeline times."""
    a, b = clip['inPoint'] / T, clip['outPoint'] / T
    points = [(a, interpolate(points, a))] + [(t, v) for t, v in points if a < t < b] + [(b, interpolate(points, b))]
    values = {'Scale_x': points, 'Scale_y': points,
              'Position_x': [(t, .5 + (v / 100 - 1) * (.5 - focus[0])) for t, v in points],
              'Position_y': [(t, .5 + (v / 100 - 1) * (.5 - focus[1])) for t, v in points],
              '_Anchor_x': [(a, .5)], '_Anchor_y': [(a, .5)], 'Rotation': [(a, 0)]}
    fx = copy.deepcopy(prototype)
    fx['thisUId'] = str(uuid.uuid4())
    set_userdata(fx, 3, '{' + str(uuid.uuid4()).upper() + '}')
    fx['paramMapList'] = []
    for p in fx['paramList']:
        if p['name'] in values:
            p['fxParam']['unValue'] = values[p['name']][0][1]
    for name, keys in values.items():
        native = []
        for i, (time, val) in enumerate(keys):
            k = dict(_time=float(time), Interpolation=1, _value=float(val))
            if i:
                t0, v0 = keys[i - 1]
                k['_leftDerivative'] = (val - v0) / (time - t0)
            if i + 1 < len(keys):
                t1, v1 = keys[i + 1]
                k['_rightDerivative'] = (v1 - val) / (t1 - time)
            native.append(k)
        fx['paramMapList'].append(dict(key=3, name=name, keyFrame=dict(parameter=dump(dict(Version=2, ParameterType=0, keyframeSets=native)).decode())))
    replaced = False
    for chain in clip['effectChainList']:
        for i, e in enumerate(chain['effectList']):
            if e.get('display') == 'transform':
                chain['effectList'][i] = fx
                replaced = True
    assert replaced
    audit.append(dict(clip_id=clip['thisUId'], media=Path(clip['filename']).name, timeline=[clip['tlBegin'] / T, clip['tlEnd'] / T], source=[a, b], kind=scene_kind, motion=description, focus=list(focus), scale=points))


def attach(left, right, name, frames):
    assert abs(left['tlEnd'] - right['tlBegin']) <= 1
    duration = round(frames / 30 * T)
    boundary = left['tlEnd']
    assert duration / 2 < min(left['tlEnd'] - left['tlBegin'], right['tlEnd'] - right['tlBegin'])
    t = copy.deepcopy(transitions[name])
    t.update(thisUId=str(uuid.uuid4()), tlBegin=boundary - duration // 2, tlEnd=boundary + duration // 2)
    set_userdata(t, 3, '{' + str(uuid.uuid4()).upper() + '}')
    left['postTransition'] = t
    transition_audit.append(dict(clip_id=left['thisUId'], boundary=boundary / T, name=name, frames=frames, native_id=t['id'], interval=[t['tlBegin'] / T, t['tlEnd'] / T]))


for rec in plan['records']:
    if rec['type'] != 'body':
        continue
    prod = R / rec['production']
    gagfile = (R / rec['source_folder']).parent / 'plano_ceninha.json'
    gag = json.loads(gagfile.read_text()) if gagfile.exists() else {}
    info = json.loads((R / gag['source_info'] if gag else prod / 'timeline.json').read_text())
    shots, fps = info['shots'], info['fps']
    clips = [c for c in main['trackInfos'][11]['clipList'] if c.get('filename', '').endswith('/' + rec['media'])]
    for c in clips:
        midpoint = (c['inPoint'] + c['outPoint']) / T / 2
        sh = next(s for s in shots if (s['start'] - 1) / fps - 1e-6 <= midpoint < s['end'] / fps + 1e-6)
        is_gag = sh['kind'] == 'gag' or any((g['start'] - 1) / 30 <= midpoint < g['end'] / 30 for g in gag.get('gags', []))
        a, b = (sh['start'] - 1) / fps, sh['end'] / fps
        kind = 'gag' if is_gag else sh['kind']
        choice = BEATS[rec['key']].get(sh['id'])
        if kind == 'gag':
            continue
        if choice:
            mode, peak = choice
            focus = (.5, .25 if kind == 'close' else .26 if kind in ('host', 'seated') else .5)
        elif kind == 'monitor':
            mode, peak, focus = 'push', 103.5, (.5, .49)
        elif kind in ('photo', 'game'):
            # Keep interfaces, memes, screenshots and framing readable.
            # The existing picture already has its own editorial media zoom.
            continue
        else:
            mode, peak, focus = 'push', 109, (.5, .38)
        points = [(a + t, v) for t, v in profile(mode, peak, b - a)]
        animate(c, points, focus, f'{sh.get("label", sh.get("mood", sh["id"]))}: {mode}', kind)
    for cut, name, frames in SWITCHES[rec['key']]:
        pair = next(((left, right) for left, right in zip(clips, clips[1:]) if abs(right['inPoint'] / T - cut) < .001), None)
        assert pair, (rec['key'], cut)
        # Never transition across a comic insert: its reveal depends on the cut.
        assert not any((g['start'] - 1) / 30 - .001 <= cut <= g['end'] / 30 + .001 for g in gag.get('gags', [])), (rec['key'], cut)
        attach(*pair, name, frames)

# Titles/hero retain three independent layers. Native scale settles and slide
# exits add energy to all eleven cards, without replacing the approved design.
for rec in plan['records']:
    if rec['type'] != 'card':
        continue
    for track, filename, focus, peak in ((12, rec['hero'], (.77, .50), 102), (13, rec['title_image'], (.27, .49), 101)):
        clip = next(c for c in main['trackInfos'][track]['clipList'] if c['filename'].endswith('/' + filename))
        animate(clip, [(0, 94 if track == 12 else 98), (.10, peak), (.23, 100), (1.72, 100), (2, 98)], focus, 'vinheta: entrada, assentamento e saída', 'card')
        # Transparent full-canvas PNGs can safely scale below 100; body pictures cannot.
    background = next(c for c in main['trackInfos'][11]['clipList'] if c['filename'].endswith('/' + rec['background']) and abs(c['tlBegin'] / T - rec['start'] / 30) < .001)
    following = next(c for c in main['trackInfos'][11]['clipList'] if abs(c['tlBegin'] - background['tlEnd']) <= 1)
    attach(background, following, 'Basic Zoom In', 8)

name = 'Massacote_Completo_Editado'
data['projectName'] = name
raw[TL] = dump(data)
meta = json.loads(raw['ProjectFolder/project_info.json'])
meta.update(project_file_name=name, proj_zip_save_path=name + '.wfp', project_guid='{' + str(uuid.uuid4()).upper() + '}', project_current_position=0)
raw['ProjectFolder/project_info.json'] = dump(meta)
library = json.loads(raw[LIB])
# Preserve the native library's duplicate media_structure keys verbatim.
old_root_name = library['media_items'][ROOT]['name']
raw[LIB] = raw[LIB].replace(dump(old_root_name), dump('Massacote — Completo editado 16:9'), 1)

# Keep the original native container, root registration and every cache entry.
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_STORED) as z:
    for name, blob in raw.items():
        z.writestr(name, blob)
assert sha(SOURCE) == source_hash and sha(REF) == reference_hash

after = json.loads(load(OUT)[TL])
assert after['resources'] == before['resources']
original_main = before['timelineInfos'][0]
for old_track, new_track in zip(original_main['trackInfos'], main['trackInfos']):
    assert len(old_track['clipList']) == len(new_track['clipList'])
    for old, new in zip(old_track['clipList'], new_track['clipList']):
        if old_track['trackType'] == 2 and old_track is not original_main['trackInfos'][12]:
            assert old == new, 'Audio changed'
        for key in ['filename', 'sourceUuid', 'inPoint', 'outPoint', 'tlBegin', 'tlEnd', 'speed', 'streamId', 'userData']:
            assert old.get(key) == new.get(key), key
        old_fx = [e for e in effects(old) if e.get('display') != 'transform']
        new_fx = [e for e in effects(new) if e.get('display') != 'transform']
        assert old_fx == new_fx
spec = importlib.util.spec_from_file_location('native_registry', L / 'validar_registro_nativo.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
registry = module.validar(OUT, strict=True)
assert registry['media_bindings'] == 296
report = dict(project=str(OUT.relative_to(R)), source_sha256=source_hash, reference_sha256=reference_hash,
              output_sha256=sha(OUT), duration=plan['duration'], total_clips=296, resources=97,
              animated_clips=len(audit), transitions=len(transition_audit), motions=audit, switches=transition_audit,
              source_time_keyframes=True, original_cuts_and_voice_and_audio_unchanged=True,
              media_files_unchanged=True, non_transform_effects_unchanged=True, native_registry=registry,
              original_projects_unchanged=True, full_frame_shake=False, new_subtitles=False,
              chapter_hero_lane_corrected_to_video=True,
              filmora_native_open=False, proprietary_transition_preview_not_native=True)
(P / 'edicao.json').write_bytes(json.dumps(report, ensure_ascii=False, indent=2).encode() + b'\n')
print('NATIVE_EDIT_READY', len(audit), 'animated clips;', len(transition_audit), 'transitions;', OUT.stat().st_size, 'bytes')
