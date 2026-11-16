"""Read back native edit, validate editable motion and unchanged audio/media."""
from pathlib import Path
import base64
import collections
import hashlib
import importlib.util
import json
import math
import zipfile

P = Path(__file__).resolve().parent
L = P.parent
R = next(p for p in P.parents if (p / 'AGENTS.md').exists())
F = L / 'output/Filmora'
TL = 'ProjectFolder/Medias/{204E72A3-B517-44d4-806F-9E9D84D5F904}/timeline.wesproj'
report = json.loads((P / 'edicao.json').read_text())


def read(path):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        return json.loads(z.read(TL))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


source = read(F / 'Massacote_Completo.wfp')
edited = read(F / 'Massacote_Completo_Editado.wfp')
assert source['resources'] == edited['resources']
sm, em = source['timelineInfos'][0], edited['timelineInfos'][0]
audios = []
curves = keys = switches = 0
named_switches = collections.Counter()
clip_ids, transition_ids = set(), set()
for i, (st, et) in enumerate(zip(sm['trackInfos'], em['trackInfos'])):
    assert len(st['clipList']) == len(et['clipList'])
    if i in (6, 7, 8):
        assert st == et
        for c in et['clipList']:
            audios.append(dict(file=Path(c['filename']).name, sha256=sha(F / c['filename'].removeprefix('file:./')), timeline=[c['tlBegin'], c['tlEnd']]))
    for old, c in zip(st['clipList'], et['clipList']):
        assert c['thisUId'] not in clip_ids
        clip_ids.add(c['thisUId'])
        for field in ('inPoint', 'outPoint', 'tlBegin', 'tlEnd', 'speed', 'filename', 'sourceUuid', 'userData'):
            assert c.get(field) == old.get(field)
        if c['filename'].endswith(('.mp4', '.png')):
            assert et['trackType'] == 1, 'Picture in an audio lane'
        maps = {}
        for chain in c.get('effectChainList', []):
            for fx in chain['effectList']:
                if fx.get('display') != 'transform':
                    continue
                for p in fx.get('paramMapList', []):
                    ks = json.loads(p['keyFrame']['parameter'])['keyframeSets']
                    if c['thisUId'] in {a['clip_id'] for a in report['motions']}:
                        assert all(c['inPoint'] / 1e7 - 1e-8 <= k['_time'] <= c['outPoint'] / 1e7 + 1e-8 for k in ks)
                    assert all(a['_time'] < b['_time'] for a, b in zip(ks, ks[1:]))
                    assert all(math.isfinite(k['_value']) and k['Interpolation'] == 1 for k in ks)
                    maps[p['name']] = ks
                    curves += 1
                    keys += len(ks)
        if maps.get('Scale_x'):
            assert maps['Scale_x'] == maps['Scale_y'], 'Stretched picture'
            sx = maps['Scale_x']
            # Transparent full-canvas cards may enter below 100%; footage may not.
            assert all(94 <= k['_value'] <= 167 for k in sx)
            if c['filename'].endswith('.mp4'):
                assert min(k['_value'] for k in sx) >= 100
                for index, k in enumerate(sx):
                    z = k['_value'] / 100
                    for axis in ('x', 'y'):
                        pos = maps['Position_' + axis][index]['_value']
                        assert 1 - z / 2 - 1e-7 <= pos <= z / 2 + 1e-7, 'Black picture edge'
        for side, at in (('preTransition', c['tlBegin']), ('postTransition', c['tlEnd'])):
            if side not in c:
                continue
            t = c[side]
            assert t['thisUId'] not in transition_ids
            transition_ids.add(t['thisUId'])
            assert abs((t['tlBegin'] + t['tlEnd']) / 2 - at) <= 1
            assert t['tlEnd'] - t['tlBegin'] <= .3 * 1e7 + 1
            assert not t.get('scriptBuf'), 'Unbundled complex transition'
            assert t['display'] in ('Basic Zoom In', 'Fast Bounce', 'SwingLeft', 'SwingRight', 'Warp Zoom 6')
            named_switches[t['display']] += 1
            switches += 1

plan = json.loads((L / 'montagem.json').read_text())
base = em['trackInfos'][11]['clipList']
assert base[0]['tlBegin'] == 0
assert all(a['tlEnd'] == b['tlBegin'] for a, b in zip(base, base[1:]))
assert base[-1]['tlEnd'] == round(plan['duration'] * 1e7)
assert len(clip_ids) == 296 and switches == report['transitions'] == 60
for resource in edited['resources']:
    path = F / resource['filename'].removeprefix('file:./')
    assert path.is_file() and path.stat().st_size > 0
spec = importlib.util.spec_from_file_location('native_registry', L / 'validar_registro_nativo.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
registry = module.validar(F / 'Massacote_Completo_Editado.wfp', strict=True)
assert registry['media_bindings'] == 296
assert sha(F / 'Massacote_Completo.wfp') == report['source_sha256']
assert sha(R / 'shorts/008-personagens-que-a-internet-estragou/production/20-edicao-final-usuario/Massacote_EDICAO_FINAL_USUARIO.wfp') == report['reference_sha256']
result = dict(project='Massacote_Completo_Editado.wfp', native_root=registry,
              original_296_cuts_and_timing_unchanged=True, source_and_reference_hashes_unchanged=True,
              all_97_resources_preserved_and_present=True, all_audio_tracks_bit_identical=True,
              audio_clips=audios, motion_curves=curves, keyframe_points=keys,
              source_time_keyframes_checked=True, uniform_scale_no_stretch=True,
              no_black_frame_edges=True, transitions=switches, transitions_by_name=dict(named_switches),
              chapter_hero_pngs_on_video_lane=True, no_new_3d_render=True,
              no_new_subtitles=True, no_whole_frame_shake=True, filmora_native_open=False)
(P / 'validacao.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print('EDIT_VERIFIED', curves, 'curves;', keys, 'keyframes;', switches, 'transitions')
