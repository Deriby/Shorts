"""Reuse the gamer room, fix facial seams, and animate to the supplied voice."""
from pathlib import Path
import sys,json,math,wave,array,bpy
from mathutils import Vector,Quaternion,Matrix
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[2]
sys.path[:0]=[str(REPO/'shorts/003-teste-quarto-gamer/production'),str(REPO/'assets/personagens/dery'),str(REPO/'assets/personagens/dery/expressions_ps1/v2')]
import helpers as H
from ps1_precision import add_safe_precision
from setup_faces31 import install as install_faces
bpy.ops.wm.open_mainfile(filepath=str(REPO/'shorts/004-crash-apelido/production/output/Dery_Crash_Master_R5.blend'))
s=bpy.context.scene;r=bpy.data.objects['Dery_Rig'];a=bpy.data.objects['DERY | animated character'];cam=s.camera
H.C.s=s
for image in bpy.data.images:
    if image.source=='FILE' and image.filepath:image.filepath=bpy.path.abspath(image.filepath)
info=json.loads((ROOT/'timeline.json').read_text());N=info['frames']
s.frame_set(300);head_monitor=r.pose.bones['head'].rotation_quaternion.copy()
s.frame_set(640);head_front=r.pose.bones['head'].rotation_quaternion.copy()
s.frame_set(1);baseline={p.name:p.rotation_quaternion.copy()for p in r.pose.bones};rest={p.name:p.matrix_local.to_quaternion()for p in r.data.bones}
shoulders={side:r.matrix_world@r.pose.bones['arm_'+side].head for side in ['R','L']}
r.animation_data_clear();a.animation_data_clear();cam.animation_data_clear();cam.data.animation_data_clear()
if a.data.shape_keys:
    a.data.shape_keys.animation_data_clear()
    for key in a.data.shape_keys.key_blocks[1:]:key.value=0
for side in ['R','L']:
    bpy.data.objects['R3 | '+side+' wrist'].animation_data_clear()
    ik=r.pose.bones['forearm_'+side].constraints['R3 | conversational gesture'];ik.influence=1;ik.use_stretch=False
for modifier in list(a.modifiers):
    if modifier.type=='NODES':a.modifiers.remove(modifier)
cam.data.sensor_fit='VERTICAL';add_safe_precision(a,cam,width=180,height=320,aspect=9/16)
# Retain the reviewed palm correction from episode 005.
groups={g.index for g in a.vertex_groups if g.name in ['hand_R','hand_L']}
handverts={v.index for v in a.data.vertices if any(g.group in groups and g.weight>.35 for g in v.groups)}
lighting=a.data.color_attributes['PS1Lighting']
for loop in a.data.loops:
    if loop.vertex_index in handverts:
        c=lighting.data[loop.index].color;lighting.data[loop.index].color=(max(c[0],.18),max(c[1],.14),max(c[2],.13),1)
s.render.resolution_x=360;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.fps=24;s.frame_start=1;s.frame_end=N
s.render.engine='CYCLES';s.cycles.samples=1;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2;s.render.use_persistent_data=True
s.render.use_compositing=False;s.render.use_sequencer=False;s.render.dither_intensity=0
s.sequence_editor_clear()
screen=bpy.data.objects['CRT moving picture'];nt=screen.data.materials[0].node_tree;tex=next(n for n in nt.nodes if n.type=='TEX_IMAGE')
tex.image=bpy.data.images.load(str(ROOT/'assets/gameplay/monitor_montado.mp4'));tex.image_user.frame_start=1;tex.image_user.frame_offset=0;tex.image_user.frame_duration=N;tex.image_user.use_auto_refresh=True
next(n for n in nt.nodes if n.type=='EMISSION').inputs['Strength'].default_value=1.30
with wave.open(str(ROOT/'assets/voz/narracao_completa.wav'))as w:sr=w.getframerate();voice=array.array('h',w.readframes(w.getnframes()))
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
def pulse(t,start,end):return math.sin(math.pi*(t-start)/(end-start))if start<t<end else 0
def talking(t):
    t=math.floor(t*8)/8;v=voice[int(t*sr):int((t+.06)*sr)]
    return math.sqrt(sum((x/32768)**2 for x in v)/max(1,len(v)))>.03
def empty(name):
    obj=bpy.data.objects.new(name,None);s.collection.objects.link(obj);return obj

# A single flat badge; only the fingertips and badge move during the push.
badge=empty('CLT | sliding badge')
dark=H.material('CLT | graphite',(.022,.027,.05),lit=False)
white=H.material('CLT | paper',(.88,.90,.84),lit=False)
yellow=H.material('LIMBO | yellow',(.95,.57,.015),lit=False)
H.box('CLT | badge body',(0,0,0),(.15,.095,.006),dark,parent=badge,bevel=.005)
H.box('CLT | face',(0,0,.004),(.135,.080,.002),white,parent=badge)
curve=bpy.data.curves.new('CLT | lettering','FONT');curve.body='CLT';curve.align_x='CENTER';curve.align_y='CENTER';curve.size=.043;curve.extrude=.0005
label=bpy.data.objects.new('CLT | label',curve);s.collection.objects.link(label);label.parent=badge;label.location=(0,0,.006);label.data.materials.append(dark)
badge.location=(-.33,-.255,.824);badge.rotation_euler.z=.18
hand_direction=Vector((0,-.30,-.954)).normalized()
hand_orientation=empty('CLT | right palm orientation');hand_orientation.rotation_mode='QUATERNION';hand_orientation.rotation_quaternion=hand_direction.to_track_quat('Y','Z')
copy=r.pose.bones['hand_R'].constraints.new('COPY_ROTATION');copy.name='CLT | touch badge';copy.target=hand_orientation;copy.owner_space='WORLD';copy.target_space='WORLD';copy.influence=0

# Limbo vignette in a remote part of the same scene: shared identity, own standing rig.
stage=empty('LIMBO | actor motion');stage.location=(20,0,0);stage.rotation_euler.z=.27
r2=r.copy();r2.data=r.data.copy();r2.name='LIMBO | Dery rig';s.collection.objects.link(r2);r2.animation_data_clear();r2.parent=stage;r2.matrix_parent_inverse=Matrix.Identity(4);r2.location=(0,0,0);r2.rotation_euler=(0,0,0)
for bone in r2.pose.bones:
    bone.matrix_basis=Matrix.Identity(4)
    for c in list(bone.constraints):bone.constraints.remove(c)
a2=a.copy();a2.data=a.data.copy();a2.name='LIMBO | Dery';s.collection.objects.link(a2);a2.animation_data_clear();a2.parent=r2;a2.matrix_parent_inverse=Matrix.Identity(4);a2.location=(0,0,0);a2.rotation_euler=(0,0,0)
for modifier in list(a2.modifiers):
    if modifier.type=='NODES':a2.modifiers.remove(modifier)
    elif modifier.type=='ARMATURE':modifier.object=r2
install_faces(a2);add_safe_precision(a2,cam,width=180,height=320,aspect=9/16)
H.box('LIMBO | platform rim',(20,0,-.10),(1.85,1.35,.16),dark)
H.box('LIMBO | platform top',(20,0,-.01),(1.79,1.29,.025),yellow)
void=H.material('LIMBO | charcoal void',(.008,.010,.018),lit=False)
H.quad('LIMBO | background',[(12,4,-20),(28,4,-20),(28,4,20),(12,4,20)],void)
front=Vector((math.sin(.6),-math.cos(.6),0));up=Vector((0,0,1));events=[]
for marker in list(s.timeline_markers):s.timeline_markers.remove(marker)
for sh in info['shots']:s.timeline_markers.new(f"{sh['id']:02d} | {sh['kind']} | {sh['mood']}",frame=sh['start'])
for f in range(1,N+1):
    t=(f-1)/24;sh=next(x for x in info['shots']if x['start']<=f<=x['end']);u=(f-sh['start'])/max(1,sh['end']-sh['start']);mood=sh['mood']
    mt=31.65 if 31.65<=t<31.90 else t
    for name,q in baseline.items():r.pose.bones[name].rotation_quaternion=q
    turn=.75*(1-smooth((t-4.262)/.45)) if 4.262<=t<7.121 else .45 if mood=='bichim' and u<.3 else .24 if mood=='clt' else .08*math.sin(mt*.9)
    r.pose.bones['head'].rotation_quaternion=head_front.slerp(head_monitor,max(0,min(1,turn)))
    r.pose.bones['head'].rotation_quaternion@=rest['head'].inverted()@Quaternion((1,0,0),.025*math.sin(mt*3.4))@rest['head']
    lean=.025*math.sin(mt*1.7)+(.08*smooth((t-49.0)/.55)if mood=='clt'else .045 if mood in ['recoil','waiting']else-.025)
    r.pose.bones['upper_chest'].rotation_quaternion@=rest['upper_chest'].inverted()@Quaternion((1,0,0),lean)@rest['upper_chest']
    grip=smooth((t-47.35)/.45)*(1-smooth((t-49.25)/.45))
    slide=smooth((t-48.0)/1.10);badge.location=(-.33-.12*slide,-.255-.010*slide,.824);H.record(badge,'location',f)
    for side,sign in [('R',-1),('L',1)]:
        gesture=max(pulse(mt,4.45,6.7),pulse(mt,14.65,17.5),pulse(mt,17.95,19.3),pulse(mt,27.7,29.1),pulse(mt,29.4,31.2),pulse(mt,39.3,41.5),pulse(mt,44.3,46.6))
        if side=='L':gesture*=.65
        outward=Vector((math.cos(.6)*sign,math.sin(.6)*sign,0));wrist=bpy.data.objects['R3 | '+side+' wrist']
        position=shoulders[side]+front*(.20+.05*gesture)+outward*(.13+.03*gesture)+up*(-.27+.19*gesture)
        if mood=='bichim':position=shoulders[side]+front*.27+outward*.07+up*(-.12+.045*math.sin(mt*4))
        if mood=='drive':position=shoulders[side]+front*.28+outward*.09+up*(-.10+sign*.035*math.sin(mt*6))
        if mood=='waiting' and side=='R':position=shoulders[side]+front*.22+outward*.09+up*(-.26+.018*math.sin(mt*20))
        if side=='R':
            # The supplied hand mesh ends before its unusually long hand bone.
            # Match the actual fingertip surface, not the bone's tail position.
            contact=Vector(badge.location)+Vector((.055,.020,.009))-hand_direction*.133
            position=position.lerp(contact,grip)
        wrist.location=position;H.record(wrist,'location',f)
        r.pose.bones['hand_'+side].rotation_quaternion=Quaternion((0,1,0),sign*(.25*gesture+.22*math.sin(mt*6)if mood=='drive'else .25*gesture))
    copy.influence=grip;H.record(copy,'influence',f)
    for bone in r.pose.bones:H.record(bone,'rotation_quaternion',f)
    talk=talking(t)
    if mood in ['bichim','recoil']:face=11 if talk else 4
    elif mood in ['explain','scale','drive','setup']:face=12 if talk else 26 if mood=='scale'else 20
    elif mood in ['slow','waiting']:face=12 if talk else 25
    elif mood=='clt':face=(16 if talk else 13)if t<info['voice_duration']else 4
    else:face=24 if talk else 23
    if any(x<=t<x+.125 for x in [6.3,15.5,21.6,28.4,32.2,39.3,43.5,50.0]):face=10
    a['PS1_face_id']=face;a.keyframe_insert(data_path='["PS1_face_id"]',frame=f)
    if not events or events[-1]['id']!=face:events.append({'frame':f,'id':face})
    # The fall moves the complete rig; no tearing, scaling, or simulated joints.
    elapsed=min(1.5,max(0,t-info['fall_start']));stage.location=(20+.03*math.sin(t*6),0,-12*elapsed*elapsed)
    a2.hide_render=sh['kind']!='limbo';a2.keyframe_insert(data_path='hide_render',frame=f)
    H.record(stage,'location',f)
    shock=smooth((t-35.90)/.25)
    for side,sign in [('L',1),('R',-1)]:
        for name,axis,angle in [('arm_'+side,(0,1,0),sign*(.95-1.45*shock)),('forearm_'+side,(0,0,1),sign*.20),('thigh_'+side,(1,0,0),sign*.12*math.sin(t*8)),('shin_'+side,(1,0,0),.12)]:
            r2.pose.bones[name].rotation_quaternion=rest[name].inverted()@Quaternion(axis,angle)@rest[name];H.record(r2.pose.bones[name],'rotation_quaternion',f)
    a2['PS1_face_id']=21 if t>=36.15 else 5;a2.keyframe_insert(data_path='["PS1_face_id"]',frame=f)
    if sh['kind']=='limbo':cam.location=(21.2,-4.2,2.4);target=Vector((20,0,.72));lens=45
    elif sh['kind']=='monitor':cam.location=(1.15,.28,1.55);target=Vector((.1095,-.7959,1.262));lens=39
    elif mood=='clt' and 48.0<=t<49.5:cam.location=(.10,-.75,1.45);target=Vector((-.40,-.26,.84));lens=55
    elif mood=='clt':cam.location=(1.40,-1.00,1.80);target=Vector((-.07,-.16,1.10));lens=37
    elif mood in ['serious','recoil','director','slow']:cam.location=(1.24,-.32,1.55);target=Vector((0,.10,1.415));lens=68 if mood!='slow'else 60
    else:cam.location=(1.65,-.12,1.62);target=Vector((0,.04,1.32));lens=53
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
    H.record(cam,'location',f);H.record(cam,'rotation_euler',f);H.record(cam.data,'lens',f)
H.commit_curves()
for obj in (a,a2):
    for curve in obj.animation_data.action.fcurves:
        for key in curve.keyframe_points:key.interpolation='CONSTANT'
(ROOT/'face_cues.json').write_text(json.dumps(events,indent=2))
editor=s.sequence_editor_create();editor.sequences.new_sound('VOZ | supplied recording + SFX',str(ROOT/'assets/voz/narracao_mix.wav'),channel=1,frame_start=1)
s.frame_set(120);s.render.filepath='//../renders/final/frame_'
bpy.data.orphans_purge(do_recursive=True);bpy.ops.file.pack_all()
project=ROOT/'output/Dery_Mizzurna_Falls.blend';bpy.ops.wm.save_as_mainfile(filepath=str(project),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(project),compress=True)
for t in ([48.6,49.2,50.15]if '--final-check'in sys.argv else [5.1,15.4,23.65,33.5,36.2,48.6,50.15]):
    s.frame_set(round(t*24)+1);s.render.filepath=str(ROOT/f'output/preview_{round(t*24)+1:04d}.png');bpy.ops.render.render(write_still=True)
print('MIZZURNA_SCENE_READY',flush=True)
