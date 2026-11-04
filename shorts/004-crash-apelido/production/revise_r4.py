"""Use reusable PNG face swaps on the existing short. No facial morphing."""
from pathlib import Path
import sys,json,shutil,array,wave,math,bpy
ROOT=Path(__file__).resolve().parent
LIBRARY=ROOT.parents[2]/'assets/personagens/dery/expressions_ps1'
sys.path.insert(0,str(LIBRARY));from setup_faces import install
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'output/Dery_Crash_Master_R3.blend'))
s=bpy.context.scene;avatar=bpy.data.objects['DERY | animated character'];install(avatar)
with wave.open(str(ROOT/'assets/voz/narracao_completa.wav'))as w:
    samples=array.array('h',w.readframes(w.getnframes()));sr=w.getframerate()
def talking(t):
    # A pre-drawn open/closed mouth, held for three frames like a PS1 cutscene.
    t=math.floor(t*8)/8;p=samples[int(t*sr):int((t+.055)*sr)]
    return math.sqrt(sum((x/32768)**2 for x in p)/max(1,len(p)))>.036
events=[]
for f in range(1,673):
    t=(f-1)/24;talk=talking(t)
    if 3.3<=t<5.9 or t>=25.4:face=3 if talk else 2
    elif 16.7<=t<18.35:face=5
    elif 18.35<=t<19.2:face=6
    elif .5<=t<3.3 or 21<=t<25.4:face=11 if talk else 4
    else:face=1 if talk else 0
    if any(a<=f<a+3 for a in [59,186,331,484,589]):face=10
    avatar['PS1_face_id']=face;avatar.keyframe_insert(data_path='["PS1_face_id"]',frame=f)
    if not events or events[-1]['id']!=face:events.append({'frame':f,'time':round(t,3),'id':face})
for curve in avatar.animation_data.action.fcurves:
    for point in curve.keyframe_points:point.interpolation='CONSTANT'
(ROOT/'face_cues_r4.json').write_text(json.dumps({'fps':24,'mode':'instant PNG texture swap','events':events},indent=2))
for name in ['timeline','vertical_crops']:
    shutil.copyfile(ROOT/(name+'_r3.json'),ROOT/(name+'_r4.json'))
s.frame_set(1);s.render.filepath=str(ROOT/'renders/r4/frame_')
project=ROOT/'output/Dery_Crash_Master_R4.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(project));bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(project))
# Render an in-model proof sheet before committing to the full animation.
action=avatar.animation_data.action;avatar.animation_data.action=None;s.frame_set(110)
for face in [0,2,3,4,5,6,7,8,9,10,11,1]:
    avatar['PS1_face_id']=face;avatar.update_tag();bpy.context.view_layer.update()
    s.render.filepath=str(ROOT/'output'/f'preview_r4_face_{face:02d}.png');bpy.ops.render.render(write_still=True)
avatar.animation_data.action=action;s.frame_set(1)
print('R4_READY',flush=True)
