"""31-face library, approved fitting, instantaneous PS1 texture acting."""
from pathlib import Path
import sys,json,shutil,array,wave,math,bpy
ROOT=Path(__file__).resolve().parent
LIB=ROOT.parents[2]/'assets/personagens/dery/expressions_ps1/v2'
sys.path.insert(0,str(LIB));from setup_faces31 import install
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'output/Dery_Face_Fit_Study.blend'))
s=bpy.context.scene;a=bpy.data.objects['DERY | animated character'];a.animation_data_clear();install(a)
with wave.open(str(ROOT/'assets/voz/narracao_completa.wav'))as w:
    samples=array.array('h',w.readframes(w.getnframes()));sr=w.getframerate()
def talking(t):
    t=math.floor(t*8)/8;p=samples[int(t*sr):int((t+.055)*sr)]
    return math.sqrt(sum((x/32768)**2 for x in p)/max(1,len(p)))>.036
events=[]
for f in range(1,673):
    t=(f-1)/24;talk=talking(t)
    if t<1.5:face=24 if talk else 23
    elif t<3.15:face=12 if talk else 13
    elif t<3.6:face=11 if talk else 4
    elif t<5.8:face=3 if talk else 2
    elif t<8.8:face=12 if talk else 20
    elif t<16.7:face=24 if talk else 23
    elif t<18.35:face=5
    elif t<19.2:face=6
    elif t<21:face=12 if talk else 20
    elif t<23.1:face=24 if talk else 23
    elif t<25.4:face=16 if talk else 4
    elif t<26.4:face=12 if talk else 13
    elif t<27.45:face=14 if talk else 2
    else:face=27
    if 5.25<t<5.4:face=17
    if any(a0<=f<a0+3 for a0 in [59,186,331,484,589]):face=10
    a['PS1_face_id']=face;a.keyframe_insert(data_path='["PS1_face_id"]',frame=f)
    if not events or events[-1]['id']!=face:events.append({'frame':f,'time':round(t,3),'id':face})
for curve in a.animation_data.action.fcurves:
    for key in curve.keyframe_points:key.interpolation='CONSTANT'
(ROOT/'face_cues_r5.json').write_text(json.dumps({'fps':24,'library_count':31,'mode':'instant PNG texture swap','events':events},indent=2))
for name in ['timeline','vertical_crops']:shutil.copyfile(ROOT/(name+'_r4.json'),ROOT/(name+'_r5.json'))
s.frame_set(1);s.render.filepath=str(ROOT/'renders/r5/frame_')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'output/Dery_Crash_Master_R5.blend'));bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'output/Dery_Crash_Master_R5.blend'))
for f in [110,160,423,640]:
    s.frame_set(f);s.render.filepath=str(ROOT/'output'/f'preview_r5_{f:04d}.png');bpy.ops.render.render(write_still=True)
print('R5_READY',flush=True)
