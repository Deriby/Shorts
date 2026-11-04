"""Reuse the reviewed Dery scene, with native portrait framing and new acting."""
from pathlib import Path
import sys,math,json,wave,array,bpy
from mathutils import Vector,Quaternion
ROOT=Path(__file__).resolve().parent;PREV=ROOT.parents[1]/'004-crash-apelido/production'
sys.path[:0]=[str(PREV),str(ROOT.parents[1]/'003-teste-quarto-gamer/production')]
import helpers as H
from ps1_nodes import add_contour_modifier
bpy.ops.wm.open_mainfile(filepath=str(PREV/'output/Dery_Crash_Master_R5.blend'))
s=bpy.context.scene;r=bpy.data.objects['Dery_Rig'];a=bpy.data.objects['DERY | animated character'];cam=s.camera
info=json.loads((ROOT/'timeline.json').read_text());N=info['frames'];b=info['part3']
s.frame_set(300);head_monitor=r.pose.bones['head'].rotation_quaternion.copy()
s.frame_set(640);head_front=r.pose.bones['head'].rotation_quaternion.copy()
s.frame_set(1);baseline={p.name:p.rotation_quaternion.copy()for p in r.pose.bones};rest={p.name:p.matrix_local.to_quaternion()for p in r.data.bones}
shoulders={side:r.matrix_world@r.pose.bones['arm_'+side].head for side in ['R','L']}
r.animation_data_clear();a.animation_data_clear();cam.animation_data_clear();cam.data.animation_data_clear()
for side in ['R','L']:
    bpy.data.objects['R3 | '+side+' wrist'].animation_data_clear()
    ik=r.pose.bones['forearm_'+side].constraints['R3 | conversational gesture'];ik.influence=1;ik.use_stretch=False
for mod in list(a.modifiers):
    if mod.type=='NODES'and'PS1'in mod.name:a.modifiers.remove(mod)
cam.data.sensor_fit='VERTICAL';add_contour_modifier(a,cam,width=180,height=320,aspect=9/16)
s.render.resolution_x=360;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.fps=24;s.frame_start=1;s.frame_end=N
s.render.threads_mode='FIXED';s.render.threads=4;s.cycles.samples=1;s.cycles.use_denoising=False
screen=bpy.data.objects['CRT moving picture'];nt=screen.data.materials[0].node_tree;tex=next(n for n in nt.nodes if n.type=='TEX_IMAGE')
tex.image=bpy.data.images.load(str(ROOT/'assets/gameplay/monitor_montado.mp4'));tex.image_user.frame_start=1;tex.image_user.frame_offset=0;tex.image_user.frame_duration=N;tex.image_user.use_auto_refresh=True
next(n for n in nt.nodes if n.type=='EMISSION').inputs['Strength'].default_value=1.30
# Lift only the old occlusion baked into the palms, keeping the room's colors.
groups={g.index for g in a.vertex_groups if g.name in ['hand_R','hand_L']};handverts={v.index for v in a.data.vertices if any(g.group in groups and g.weight>.35 for g in v.groups)}
lighting=a.data.color_attributes['PS1Lighting']
for loop in a.data.loops:
    if loop.vertex_index in handverts:
        c=lighting.data[loop.index].color;lighting.data[loop.index].color=(max(c[0],.18),max(c[1],.14),max(c[2],.13),1)
with wave.open(str(ROOT/'assets/voz/narracao_completa.wav'))as w:sr=w.getframerate();voice=array.array('h',w.readframes(w.getnframes()))
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
def pulse(t,x,y):return math.sin(math.pi*(t-x)/(y-x))if x<t<y else 0
def talking(t):
    t=math.floor(t*8)/8;v=voice[int(t*sr):int((t+.055)*sr)]
    return math.sqrt(sum((x/32768)**2 for x in v)/max(1,len(v)))>.036
front=Vector((math.sin(.6),-math.cos(.6),0));up=Vector((0,0,1))
events=[]
for marker in list(s.timeline_markers):s.timeline_markers.remove(marker)
for sh in info['shots']:s.timeline_markers.new(f"{sh['id']:02d} | {sh['kind']} | {sh['mood']}",frame=sh['start'])
for f in range(1,N+1):
    t=(f-1)/24;sh=next(x for x in info['shots']if x['start']<=f<=x['end']);u=(f-sh['start'])/max(1,sh['end']-sh['start']);mood=sh['mood']
    freeze=b-.30;mt=freeze if freeze<=t<freeze+4/24 else t
    for name,q in baseline.items():r.pose.bones[name].rotation_quaternion=q
    turn=1-smooth((t-2.80)/.35) if t<5 else .07*math.sin(mt*.9)
    r.pose.bones['head'].rotation_quaternion=head_front.slerp(head_monitor,max(0,min(1,turn)))
    r.pose.bones['head'].rotation_quaternion@=rest['head'].inverted()@Quaternion((1,0,0),.025*math.sin(mt*3.3))@rest['head']
    lean=.025*math.sin(mt*1.3)+(.055 if mood=='recoil'else .035 if mood=='trauma'else-.025)
    r.pose.bones['upper_chest'].rotation_quaternion@=rest['upper_chest'].inverted()@Quaternion((1,0,0),lean)@rest['upper_chest']
    for side,sign in [('R',-1),('L',1)]:
        gesture=max(pulse(mt,3.1,4.8),pulse(mt,5.2,7.4),pulse(mt,26.7,28.7),pulse(mt,b+.3,b+1.9),pulse(mt,b+8.8,b+10.7))
        if side=='L':gesture*=.6
        if mood in ['trauma','ending']:gesture*=.35
        out=Vector((math.cos(.6)*sign,math.sin(.6)*sign,0));wrist=bpy.data.objects['R3 | '+side+' wrist']
        wrist.location=shoulders[side]+front*(.20+.06*gesture)+out*(.13+.015*math.sin(mt*2))+up*(-.27+.20*gesture)
        H.record(wrist,'location',f)
        r.pose.bones['hand_'+side].rotation_quaternion=Quaternion((0,1,0),sign*.25*gesture)
    for bone in r.pose.bones:H.record(bone,'rotation_quaternion',f)
    if sh['kind']=='monitor':
        cam.location=(1.15,.28,1.55);target=Vector((.1095,-.7959,1.262));lens=36+2*u if sh['still']else 40+3*u
    elif mood in ['recoil','trauma','awkward','smug','ending']or(sh['id']==3 and u>.4):
        cam.location=(1.24,-.32,1.55);target=Vector((0,.10,1.415));lens=(76 if mood in ['trauma','ending']else 68)+2*u
    else:cam.location=(1.65,-.12,1.62);target=Vector((0,.04,1.32));lens=55+u
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
    H.record(cam,'location',f);H.record(cam,'rotation_euler',f);H.record(cam.data,'lens',f)
    talk=talking(t)
    if mood=='irony':face=11 if talk else 4
    elif mood=='explain':face=12 if talk else 20
    elif mood=='recoil':face=18
    elif mood=='trauma':face=25 if talk else 6
    elif mood=='serious':face=24 if talk else 23
    elif mood=='awkward':face=12 if talk else 25
    elif mood=='smug':face=16 if talk else 13
    else:face=6
    if any(x<=t<x+.125 for x in [4.5,7.6,b-.10,b+1.7,b+10.8]):face=10
    a['PS1_face_id']=face;a.keyframe_insert(data_path='["PS1_face_id"]',frame=f)
    if not events or events[-1]['id']!=face:events.append({'frame':f,'id':face})
H.commit_curves()
for curve in a.animation_data.action.fcurves:
    for key in curve.keyframe_points:key.interpolation='CONSTANT'
(ROOT/'face_cues.json').write_text(json.dumps(events,indent=2))
out=ROOT/'output';out.mkdir(exist_ok=True);s.frame_set(1);s.render.filepath=str(ROOT/'renders/final/frame_')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'Dery_GTA_POSTAL2.blend'),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(out/'Dery_GTA_POSTAL2.blend'),compress=True)
for t in [3.6,6.5,info['part2']+8.9,info['part3']-.6,info['part3']+3,info['voice_duration']+.4]:
    f=round(t*24)+1;s.frame_set(f);s.render.filepath=str(out/f'preview_{f:04d}.png');bpy.ops.render.render(write_still=True)
print('POSTAL_SCENE_READY',flush=True)
