"""Five-second directing test using existing Dery assets and recorded voice."""
from pathlib import Path
import bpy,sys,math,json,wave,array,subprocess
from mathutils import Vector,Quaternion
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]/'003-teste-quarto-gamer/production'))
import helpers as H
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'output/Dery_Crash_Master_R5.blend'))
s=bpy.context.scene;rig=bpy.data.objects['Dery_Rig'];a=bpy.data.objects['DERY | animated character'];cam=s.camera
s.frame_set(300);head_monitor=rig.pose.bones['head'].rotation_quaternion.copy()
s.frame_set(640);head_front=rig.pose.bones['head'].rotation_quaternion.copy()
rest=rig.data.bones['upper_chest'].matrix_local.to_quaternion()
with wave.open(str(ROOT/'assets/voz/narracao_completa.wav'))as w:
    sr=w.getframerate();voice=array.array('h',w.readframes(w.getnframes()))
source_start=24.30;source_end=27.30;voice_offset=.80
mixed=array.array('h',[0])*(sr*5)
clip=voice[round(source_start*sr):round(source_end*sr)]
offset=round(voice_offset*sr);mixed[offset:offset+len(clip)]=clip
raw=subprocess.check_output(['ffmpeg','-v','error','-ss','6','-t','0.8','-i',str(ROOT/'assets/gameplay/crash_ps1_enviado.mp4'),'-vn','-ac','1','-ar',str(sr),'-f','s16le','-'])
game=array.array('h',raw)
for i,sample in enumerate(game[:round(.8*sr)]):
    fade=min(1,max(0,(.80-i/sr)/.18));mixed[i]+=int(sample*.065*fade)
for i in range(round(.085*sr)):
    t=i/sr;hz=460 if t<.04 else 230
    sample=round(math.sin(2*math.pi*hz*t)*12)/12
    mixed[round(4.15*sr)+i]+=int(32767*.035*sample*math.exp(-t*24))
audio=ROOT/'assets/voz/teste_direcao_5s.wav'
with wave.open(str(audio),'wb')as w:
    w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(mixed.tobytes())
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
def talking(t):
    st=math.floor(t*8)/8;v=mixed[int(st*sr):int((st+.055)*sr)]
    return math.sqrt(sum((x/32768)**2 for x in v)/max(1,len(v)))>.036
shots=[(1,20,'monitor'),(21,49,'medium'),(50,92,'close'),(93,120,'deadpan')]
a.animation_data_clear()
for marker in list(s.timeline_markers):s.timeline_markers.remove(marker)
for first,last,kind in shots:s.timeline_markers.new(kind,frame=first)
face_events=[]
for f in range(1,121):
    t=(f-1)/24
    src=round((source_start+t-voice_offset)*24)+1 if t>=voice_offset else 280+f
    s.frame_set(max(1,min(672,src)))
    head=rig.pose.bones['head']
    head.rotation_quaternion=head_monitor.slerp(head_front,smooth((t-.73)/.30))
    if .9<t<1.7:head.rotation_quaternion@=Quaternion((1,0,0),.035*math.sin((t-.9)*math.pi/.8))
    chest=rig.pose.bones['upper_chest']
    lean=-.045*smooth((t-.75)/.35)*(1-smooth((t-3.70)/.25))+.035*smooth((t-3.70)/.25)
    chest.rotation_quaternion@=rest.inverted()@Quaternion((1,0,0),lean)@rest
    for side in ['R','L']:
        wrist=bpy.data.objects['R3 | '+side+' wrist']
        if side=='R':wrist.location.z+=.035*max(0,math.sin(math.pi*(t-.85)/1.0)) if .85<t<1.85 else 0
        wrist.location.z-=.12*smooth((t-3.65)/.35)
        H.record(wrist,'location',f)
        ik=rig.pose.bones['forearm_'+side].constraints['R3 | conversational gesture']
        ik.influence=1;H.record(ik,'influence',f)
    for bone in rig.pose.bones:H.record(bone,'rotation_quaternion',f)
    first,last,kind=next(x for x in shots if x[0]<=f<=x[1]);u=(f-first)/max(1,last-first)
    if kind=='monitor':
        loc=Vector((1.22-.10*u,.22-.10*u,1.53));target=Vector((.1095,-.7959,1.262));lens=44+8*u
    elif kind=='medium':loc=Vector((1.78,-.08,1.61));target=Vector((0,0,1.28));lens=49+u
    else:
        loc=Vector((1.24,-.32,1.55));target=Vector((0,.10,1.415));lens=65+5*u if kind=='close' else 78
    cam.location=loc;cam.rotation_euler=(target-loc).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
    H.record(cam,'location',f);H.record(cam,'rotation_euler',f);H.record(cam.data,'lens',f)
    if t<.8:face=20
    elif t<2.10:face=24 if talking(t) else 23
    elif t<3.8:face=11 if talking(t) else 4
    else:face=6
    if 4.34<=t<4.47:face=10
    a['PS1_face_id']=face;a.keyframe_insert(data_path='["PS1_face_id"]',frame=f)
    if not face_events or face_events[-1]['id']!=face:face_events.append({'frame':f,'id':face})
H.commit_curves()
for curve in a.animation_data.action.fcurves:
    for point in curve.keyframe_points:point.interpolation='CONSTANT'
crops=[]
for first,last,kind in shots:
    xs=[]
    for f in [first,last]:
        s.frame_set(f)
        if kind=='monitor':p=Vector((.1095,-.7959,1.262))
        else:
            b=rig.pose.bones['head'];p=rig.matrix_world@(b.matrix@(b.bone.matrix_local.inverted()@Vector((0,-.085,1.59))))
        xs.append(max(0,min(1312,round(world_to_camera_view(s,cam,p).x*1920-304))))
    crops.append({'start':first,'end':last,'kind':kind,'x_start':xs[0],'x_end':xs[1]})
info={'fps':24,'frames':120,'duration':5,'voice_source':'assets/voz/narracao_completa.wav','voice_start':source_start,'voice_end':source_end,'voice_offset':voice_offset,'game_audio_start':6,'game_audio_duration':.8,'beep_time':4.15,'shots':crops,'faces':face_events}
(ROOT/'direction_test_timeline.json').write_text(json.dumps(info,indent=2))
s.frame_start=1;s.frame_end=120;s.render.fps=24;s.frame_set(1);s.render.filepath=str(ROOT/'renders/direction_test/frame_')
out=ROOT/'output/Dery_Teste_Direcao_5s.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
for f in [15,43,106]:
    s.frame_set(f);s.render.filepath=str(ROOT/'output'/f'preview_direction_{f:04d}.png');bpy.ops.render.render(write_still=True)
print('DIRECTION_TEST_READY',flush=True)
