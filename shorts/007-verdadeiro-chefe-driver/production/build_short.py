"""Driver: reusable room, clean shirt/skin, hand-authored acting and low-poly garage."""
from pathlib import Path
import sys,json,math,wave,array,bpy
from mathutils import Vector,Quaternion,Matrix
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[2]
sys.path[:0]=[str(REPO/'shorts/003-teste-quarto-gamer/production'),str(REPO/'assets/personagens/dery'),str(REPO/'assets/personagens/dery/expressions_ps1/v2'),str(REPO/'assets/personagens/dery/roupas/camiseta_preta')]
import helpers as H
from ps1_precision import add_safe_precision
from setup_faces31 import install as install_faces
from aplicar import aplicar
from limpar import light as neutral_light
bpy.ops.wm.open_mainfile(filepath=str(REPO/'shorts/004-crash-apelido/production/output/Dery_Crash_Master_R5.blend'))
s=bpy.context.scene;H.C.s=s;r=bpy.data.objects['Dery_Rig'];a=bpy.data.objects['DERY | animated character'];cam=s.camera
for im in bpy.data.images:
 if im.source=='FILE' and im.filepath:im.filepath=bpy.path.abspath(im.filepath)
info=json.loads((ROOT/'timeline.json').read_text());N=info['frames']
s.frame_set(300);head_monitor=r.pose.bones['head'].rotation_quaternion.copy()
s.frame_set(640);head_front=r.pose.bones['head'].rotation_quaternion.copy()
s.frame_set(1);base={p.name:p.rotation_quaternion.copy()for p in r.pose.bones};rest={p.name:p.matrix_local.to_quaternion()for p in r.data.bones}
shoulders={side:r.matrix_world@r.pose.bones['arm_'+side].head for side in ['R','L']}
r.animation_data_clear();a.animation_data_clear();cam.animation_data_clear();cam.data.animation_data_clear()
if a.data.shape_keys:
 a.data.shape_keys.animation_data_clear()
 for k in a.data.shape_keys.key_blocks[1:]:k.value=0
for side in ['R','L']:
 bpy.data.objects['R3 | '+side+' wrist'].animation_data_clear();ik=r.pose.bones['forearm_'+side].constraints['R3 | conversational gesture'];ik.influence=1;ik.use_stretch=False
for mod in list(a.modifiers):
 if mod.type=='NODES':a.modifiers.remove(mod)
aplicar(a);cam.data.sensor_fit='VERTICAL';add_safe_precision(a,cam,width=180,height=320,aspect=9/16)
s.render.resolution_x=360;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.fps=24;s.frame_start=1;s.frame_end=N
s.render.engine='CYCLES';s.cycles.samples=1;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2;s.render.use_persistent_data=True
s.render.use_compositing=False;s.render.use_sequencer=False;s.render.dither_intensity=0;s.sequence_editor_clear()
screen=bpy.data.objects['CRT moving picture'];nt=screen.data.materials[0].node_tree;tex=next(n for n in nt.nodes if n.type=='TEX_IMAGE');tex.image=bpy.data.images.load(str(ROOT/'assets/gameplay/monitor_montado.mp4'));tex.image_user.frame_start=1;tex.image_user.frame_offset=0;tex.image_user.frame_duration=N;tex.image_user.use_auto_refresh=True
next(n for n in nt.nodes if n.type=='EMISSION').inputs['Strength'].default_value=1.3
with wave.open(str(ROOT/'assets/voz/narracao_completa.wav'))as w:sr=w.getframerate();voice=array.array('h',w.readframes(w.getnframes()))
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
def beat(t,start,end):return math.sin(math.pi*(t-start)/(end-start))if start<t<end else 0
def talking(t):
 t=math.floor(t*8)/8;v=voice[int(t*sr):int((t+.06)*sr)];return sum((x/32768)**2 for x in v)/max(1,len(v))>.0009
def empty(name,loc=(0,0,0),parent=None):
 o=bpy.data.objects.new(name,None);s.collection.objects.link(o);o.parent=parent;o.location=loc;return o
def shaded(name,color):
 m=H.material(name,color,lit=False);nt=m.node_tree;em=next(n for n in nt.nodes if n.type=='EMISSION');rgb=em.inputs['Color'].links[0].from_socket;g=nt.nodes.new('ShaderNodeNewGeometry');dot=nt.nodes.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=(-.35,-.55,.75);nt.links.new(g.outputs['Normal'],dot.inputs[0]);add=nt.nodes.new('ShaderNodeMath');add.operation='MULTIPLY_ADD';add.inputs[1].default_value=.24;add.inputs[2].default_value=.76;nt.links.new(dot.outputs['Value'],add.inputs[0]);mul=nt.nodes.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;nt.links.new(rgb,mul.inputs[1]);nt.links.new(add.outputs[0],mul.inputs[2]);nt.links.new(mul.outputs[0],em.inputs['Color']);return m
# Garage components have baked-style faceted lighting, without noisy ray-traced shadows.
concrete=shaded('GARAGE | concrete',(.23,.25,.25));dark=shaded('GARAGE | rubber',(.018,.022,.029));yellow=shaded('GARAGE | hazard yellow',(.94,.64,.035));paint=shaded('CAR | midnight blue',(.075,.12,.19));metal=shaded('CAR | silver',(.38,.43,.48));red=H.material('CAR | tail light',(.8,.03,.025),lit=False);white=H.material('GARAGE | fluorescent',(.90,.87,.68),lit=False)
H.box('GARAGE | floor',(20,0,-.07),(13,15,.12),concrete);H.box('GARAGE | back wall',(20,4,1.55),(13,.18,3.2),concrete);H.box('GARAGE | left wall',(15,0,1.55),(.18,10,3.2),concrete)
for x in [17,20,23]:
 for y in [-4,0,3]:
  H.box('GARAGE | parking line',(x,y,.002),(.055,2.1,.006),yellow)
for x,y in [(16,-2.3),(24,-2.3),(17,2.5),(23,2.5),(20,-2.3)]:
 H.box('GARAGE | pillar',(x,y,1.5),(.55,.55,3),concrete)
 for z in range(6):
  H.box('GARAGE | hazard collar',(x,y,.12+z*.18),(.562,.562,.10),yellow if z%2 else dark)
for x in [17,20,23]:H.box('GARAGE | ceiling lamp',(x,0,3.05),(1.5,.35,.035),white)
# Texturing: a low-resolution concrete tile, kept crisp rather than blurred.
import random
rng=random.Random(7);im=bpy.data.images.new('GARAGE | 64px concrete',64,64);pixels=[]
for _ in range(4096):
 c=.23+rng.choice([-.025,0,.025]);pixels.extend((c,c*1.04,c*1.05,1))
im.pixels=pixels;im.pack();nt=concrete.node_tree;tx=nt.nodes.new('ShaderNodeTexImage');tx.image=im;tx.interpolation='Closest';tx.projection='BOX';tx.projection_blend=0;coords=nt.nodes.new('ShaderNodeTexCoord');nt.links.new(coords.outputs['Generated'],tx.inputs['Vector']);rgb=next(n for n in nt.nodes if n.type=='RGB');
for link in list(rgb.outputs[0].links):nt.links.new(tx.outputs['Color'],link.to_socket)
car=empty('CAR | motion',(20,0,0))
H.box('CAR | body',(0,0,.57),(1.56,3.05,.47),paint,car,bevel=.09)
H.box('CAR | hood',(0,-1.03,.85),(1.49,1.03,.18),paint,car,bevel=.04)
H.box('CAR | trunk',(0,1.12,.84),(1.49,.79,.18),paint,car,bevel=.04)
H.box('CAR | front bumper',(0,-1.58,.48),(1.57,.10,.16),metal,car)
H.box('CAR | grill',(0,-1.637,.67),(.73,.015,.13),dark,car)
for sign in [-1,1]:
 H.box('CAR | headlight',(sign*.56,-1.637,.69),(.30,.025,.15),white,car)
 H.box('CAR | tail light',(sign*.57,1.537,.70),(.30,.025,.13),red,car)
 for y in [-.99,1.01]:
  H.cylinder('CAR | tire',(sign*.79,y,.32),.31,.17,dark,car,vertices=12,rot=(0,math.pi/2,0))
  H.cylinder('CAR | hub',(sign*.885,y,.32),.17,.014,metal,car,vertices=8,rot=(0,math.pi/2,0))
 H.beam('CAR | A pillar',(sign*.70,-.69,.89),(sign*.63,-.44,1.73),.065,paint,car)
 H.beam('CAR | C pillar',(sign*.70,.78,.89),(sign*.63,.55,1.73),.08,paint,car)
 H.box('CAR | door trim',(sign*.76,.02,.92),(.06,1.28,.12),paint,car)
H.box('CAR | roof',(0,.07,1.75),(1.38,1.16,.085),paint,car,bevel=.02)
H.box('CAR | dashboard',(0,-.64,.93),(1.35,.24,.14),dark,car)
for x in [-.28,.35]:
 H.box('CAR | seat cushion',(x,.1,.48),(.43,.48,.15),dark,car)
 H.box('CAR | seat back',(x,.39,.84),(.43,.13,.65),dark,car,bevel=.035)
wheel=H.torus('CAR | steering wheel',(-.28,-.39,1.06),.18,.018,dark,car,rot=(math.pi/2,0,0),segments=16)
H.beam('CAR | wheel spoke',(-.46,-.39,1.06),(-.10,-.39,1.06),.023,metal,car)
# Clone the unchanged seated mesh; the car is built around the supplied proportions.
r2=r.copy();r2.data=r.data.copy();r2.name='CAR | Dery rig';s.collection.objects.link(r2);r2.animation_data_clear();r2.parent=car;r2.matrix_parent_inverse=Matrix.Identity(4);r2.location=(-.28,0,-.17);r2.rotation_euler=(0,0,0)
for p in r2.pose.bones:
 p.rotation_quaternion=base[p.name]
 for c in list(p.constraints):p.constraints.remove(c)
a2=a.copy();a2.data=a.data.copy();a2.name='CAR | Dery';s.collection.objects.link(a2);a2.animation_data_clear();a2.parent=r2;a2.matrix_parent_inverse=Matrix.Identity(4);a2.location=(0,0,0);a2.rotation_euler=(0,0,0);a2.scale=(1,1,1)
for m in list(a2.modifiers):
 if m.type=='NODES':a2.modifiers.remove(m)
 elif m.type=='ARMATURE':m.object=r2
install_faces(a2)
# The clone already has wardrobe tags, so replace its freshly installed face light explicitly.
fnt=a2.data.materials[1].node_tree;illum=neutral_light(fnt)
for node in list(fnt.nodes):
 if node.type=='VERTEX_COLOR' and node.layer_name=='PS1FaceLightFit':
  for link in list(node.outputs['Color'].links):fnt.links.new(illum,link.to_socket)
a2.data.materials[1]['DeryNeutralLight']=True
aplicar(a2);add_safe_precision(a2,cam,width=180,height=320,aspect=9/16)
wrists={}
for side,sign in [('R',-1),('L',1)]:
 target=empty('CAR | '+side+' wrist',(-.28+sign*.17,-.27,1.06),car);wrists[side]=target
 pole=empty('CAR | '+side+' elbow',(-.28+sign*.55,.12,.95),car)
 ik=r2.pose.bones['forearm_'+side].constraints.new('IK');ik.name='CAR | wheel contact';ik.target=target;ik.chain_count=2;ik.use_stretch=False
 orientation=empty('CAR | '+side+' palm orientation',parent=car);orientation.rotation_mode='QUATERNION';orientation.rotation_quaternion=Vector((0,-1,0)).to_track_quat('Y','Z')
 c=r2.pose.bones['hand_'+side].constraints.new('COPY_ROTATION');c.target=orientation;c.owner_space='WORLD';c.target_space='WORLD'
bar=empty('BOSS | health bar',(20,-2.59,2.28))
H.box('BOSS | black border',(0,0,0),(1.15,.025,.17),dark,bar);H.box('BOSS | full life',(0,-.019,0),(1.05,.015,.085),yellow,bar)
font=bpy.data.curves.new('BOSS | pillar label','FONT');font.body='PILASTRA';font.align_x='CENTER';font.size=.15;font.extrude=0
label=bpy.data.objects.new('BOSS | PILASTRA',font);s.collection.objects.link(label);label.parent=bar;label.location=(0,-.025,.19);label.rotation_euler=(math.pi/2,0,0);font.materials.append(white)
front=Vector((math.sin(.6),-math.cos(.6),0));up=Vector((0,0,1));events=[]
for m in list(s.timeline_markers):s.timeline_markers.remove(m)
for sh in info['shots']:s.timeline_markers.new(f"{sh['id']:02d} | {sh['kind']} | {sh['mood']}",frame=sh['start'])
for f in range(1,N+1):
 t=(f-1)/24;sh=next(x for x in info['shots']if x['start']<=f<=x['end']);mood=sh['mood'];u=(f-sh['start'])/max(1,sh['end']-sh['start']);talk=talking(t)
 for name,q in base.items():r.pose.bones[name].rotation_quaternion=q
 turn=.6*(1-smooth((t-2.65)/.5))if mood=='deadpan'else .25 if mood=='test'else .05
 r.pose.bones['head'].rotation_quaternion=head_front.slerp(head_monitor,turn)
 tilt=.10 if mood=='confused'else .015*math.sin(t*3.2)
 r.pose.bones['head'].rotation_quaternion@=rest['head'].inverted()@Quaternion((0,1,0),tilt)@rest['head']
 lean=(-.05*beat(t,4.9,7.4)-.07*beat(t,31.5,34.95)+.035*math.sin(t*2))if mood!='deadpan'else .035
 r.pose.bones['upper_chest'].rotation_quaternion@=rest['upper_chest'].inverted()@Quaternion((1,0,0),lean)@rest['upper_chest']
 for side,sign in [('R',-1),('L',1)]:
  outward=Vector((math.cos(.6)*sign,math.sin(.6)*sign,0))
  g=max(beat(t,5.05,6.1),beat(t,6.25,7.35),beat(t,11,12.4),beat(t,12.55,14.2),beat(t,28,29.05),beat(t,29.25,30.35),beat(t,30.45,31.45),beat(t,31.65,32.8),beat(t,33,34.85))
  if side=='L':g*=.8
  pos=shoulders[side]+front*(.19+.08*g)+outward*(.10+.04*g)+up*(-.28+.23*g)
  if mood=='small':pos=shoulders[side]+front*(.25+.025*g)-outward*.04+up*(-.14+.06*g)
  if mood=='stunt':pos=shoulders[side]+front*.23+outward*(.13+.08*g)+up*(-.17+.15*g)
  if mood=='confused'and side=='L':pos=shoulders[side]+front*.22+outward*.13+up*(-.09+.025*g)
  wrist=bpy.data.objects['R3 | '+side+' wrist'];wrist.location=pos;H.record(wrist,'location',f)
  r.pose.bones['hand_'+side].rotation_quaternion=Quaternion((0,1,0),sign*.35*g)
 for p in r.pose.bones:H.record(p,'rotation_quaternion',f)
 face=(12 if talk else 20)if mood in ['explain','test','list']else (24 if talk else 6)if mood=='deadpan'else (12 if talk else 22)if mood=='confused'else (11 if talk else 4)
 if any(x<=t<x+.125 for x in [5.6,12.8,28.6,32.4,34.3]):face=10
 a['PS1_face_id']=face;a.keyframe_insert(data_path='["PS1_face_id"]',frame=f)
 if not events or events[-1]['id']!=face:events.append(dict(frame=f,id=face))
 # Controlled approach and one small collision, not a simulation.
 if mood=='brake':cy=-.33*smooth(u/.70)
 elif t>=37.78:cy=-.08-.37*smooth((t-39.9)/.65)+.035*math.sin(max(0,t-40.55)*24)*math.exp(-max(0,t-40.55)*9)if t>=39.9 else -.08
 else:cy=0
 car.location=(20,cy,0);H.record(car,'location',f)
 for name,q in base.items():r2.pose.bones[name].rotation_quaternion=q
 r2.pose.bones['head'].rotation_quaternion=Quaternion((0.6927400231,0.0094303070,-0.6694391966,0.2682266533)) if mood=='defeat'else base['head'] @ rest['head'].inverted() @ Quaternion((0,0,1),-.08) @ rest['head']
 r2.pose.bones['upper_chest'].rotation_quaternion@=rest['upper_chest'].inverted()@Quaternion((1,0,0),.10*beat(t,40.5,40.9))@rest['upper_chest']
 for p in r2.pose.bones:H.record(p,'rotation_quaternion',f)
 cface=6 if mood=='defeat'and not talk else 24 if mood=='defeat'else 5 if t>=40.5 else 25 if mood=='brake'and u>.6 else 12 if talk else 13
 a2['PS1_face_id']=cface;a2.keyframe_insert(data_path='["PS1_face_id"]',frame=f)
 a2.hide_render=sh['kind']!='garage';a2.keyframe_insert(data_path='hide_render',frame=f)
 for obj in [bar,label]+list(bar.children):
  obj.hide_render=t<37.78;H.record(obj,'hide_render',f)
 if sh['kind']=='garage':
  if mood=='defeat':cam.location=(17.9,.03+cy,1.50);target=Vector((19.72,-.04+cy,1.32));lens=66
  elif mood=='boss':cam.location=(16.5,-4.8,2.6);target=Vector((20,-1.4,1.35));lens=24
  else:cam.location=(17.35,-3.5,2.1);target=Vector((20,-.75+cy,1.05));lens=37
 elif sh['kind']=='monitor':cam.location=(1.15,.28,1.55);target=Vector((.1095,-.7959,1.262));lens=39
 elif mood in ['deadpan','confused']:cam.location=(1.24,-.32,1.55);target=Vector((0,.10,1.415));lens=65
 else:cam.location=(2.1,-.80,1.64);target=Vector((0,.04,1.18));lens=38
 cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;H.record(cam,'location',f);H.record(cam,'rotation_euler',f);H.record(cam.data,'lens',f)
H.commit_curves()
for obj in [a,a2]:
 for fc in obj.animation_data.action.fcurves:
  for key in fc.keyframe_points:key.interpolation='CONSTANT'
(ROOT/'face_cues.json').write_text(json.dumps(events,indent=2))
s.sequence_editor_create().sequences.new_sound('VOZ | original + brief SFX',str(ROOT/'assets/voz/narracao_mix.wav'),channel=1,frame_start=1)
s.frame_set(124);s.render.filepath='//../renders/final/frame_';bpy.data.orphans_purge(do_recursive=True);bpy.ops.file.pack_all()
(ROOT/'output').mkdir(exist_ok=True);project=ROOT/'output/Dery_Driver.blend';bpy.ops.wm.save_as_mainfile(filepath=str(project),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(project),compress=True)
for t in [5.55,15.5,25.4,28.4,33.2,38.7,40.8,43.3]:
 s.frame_set(round(t*24)+1);s.render.filepath=str(ROOT/f'output/preview_{round(t*24)+1:04d}.png');bpy.ops.render.render(write_still=True)
print('DRIVER_SCENE_READY',flush=True)
