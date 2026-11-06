"""Phrase-specific performance, discrete faces, PS1 precision and a fictional triage bay and a denied request for mercy."""
from pathlib import Path
import sys,json,math,wave,array,bpy
from mathutils import Vector,Quaternion,Matrix
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parent;REPO=next(p for p in ROOT.parents if(p/'AGENTS.md').exists());WIDE='--wide'in sys.argv
sys.path[:0]=[str(REPO/'shorts/003-teste-quarto-gamer/production'),str(REPO/'assets/personagens/dery'),str(REPO/'assets/personagens/dery/expressions_ps1/v2'),str(REPO/'assets/personagens/dery/roupas/camiseta_preta')]
import helpers as H
from ps1_precision import add_safe_precision
from setup_faces31 import install as install_faces
from aplicar import aplicar
from limpar import light as neutral_light
bpy.ops.wm.open_mainfile(filepath=str(REPO/'shorts/004-crash-apelido/production/output/Dery_Crash_Master_R5.blend'))
s=bpy.context.scene;H.C.s=s;r=bpy.data.objects['Dery_Rig'];a=bpy.data.objects['DERY | animated character'];cam=s.camera
for im in bpy.data.images:
 if im.source=='FILE'and im.filepath:im.filepath=bpy.path.abspath(im.filepath)
s.frame_set(1);base={p.name:p.rotation_quaternion.copy()for p in r.pose.bones};rest={p.name:p.matrix_local.to_quaternion()for p in r.data.bones}
bpy.context.view_layer.update();evaluated_rig=r.evaluated_get(bpy.context.evaluated_depsgraph_get());seated_pose={p.name:p.matrix.copy()for p in evaluated_rig.pose.bones}
r.animation_data_clear();a.animation_data_clear();cam.animation_data_clear();cam.data.animation_data_clear()
if a.data.shape_keys:
 a.data.shape_keys.animation_data_clear()
 for k in a.data.shape_keys.key_blocks[1:]:k.value=0
for side in ['R','L']:
 bpy.data.objects['R3 | '+side+' wrist'].animation_data_clear();ik=r.pose.bones['forearm_'+side].constraints['R3 | conversational gesture'];ik.influence=1;ik.use_stretch=False
for m in list(a.modifiers):
 if m.type=='NODES':a.modifiers.remove(m)
aplicar(a);info=json.loads((ROOT/'timeline.json').read_text());N=info['frames'];aspect=16/9 if WIDE else 9/16
s.render.resolution_x=640 if WIDE else 360;s.render.resolution_y=360 if WIDE else 640;s.render.resolution_percentage=100;s.render.fps=24;s.frame_start=1;s.frame_end=N
s.render.engine='CYCLES';s.cycles.samples=1;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2;s.render.use_persistent_data=True;s.render.use_compositing=False;s.render.use_sequencer=False;s.render.dither_intensity=0;s.sequence_editor_clear();cam.data.sensor_fit='VERTICAL'
def precision(obj,avatar=False):
 add_safe_precision(obj,cam,width=405 if WIDE else 128,height=228,aspect=aspect)
 if not avatar:
  for x in obj.data.attributes['PS1SnapWeight'].data:x.value=1
precision(a,True)
for p in a.data.polygons:
 if p.material_index!=1:p.use_smooth=False
# Quantize original body/nose texture addressing, leaving the reviewed face atlas intact.
for mat in a.data.materials:
 if not mat or not mat.use_nodes:continue
 for n in mat.node_tree.nodes:
  if n.type=='TEX_IMAGE':n.interpolation='Closest'
  if n.type=='VECT_MATH'and n.operation=='SNAP':n.inputs[1].default_value=(1/128,1/128,1)
  elif n.type=='VECT_MATH'and n.operation=='ADD'and abs(n.inputs[1].default_value[0]-.5/512)<1e-7:n.inputs[1].default_value=(.5/128,.5/128,0)
precision(bpy.data.objects['ROOM | baked lighting geometry'])
# Keep the monitor bright and continuously refreshed.
screen=bpy.data.objects['CRT moving picture'];nt=screen.data.materials[0].node_tree;tex=next(n for n in nt.nodes if n.type=='TEX_IMAGE');tex.image=bpy.data.images.load(str(ROOT/'assets/gameplay/monitor_montado.mp4'));tex.interpolation='Closest';tex.image_user.frame_start=1;tex.image_user.frame_offset=0;tex.image_user.frame_duration=N;tex.image_user.use_auto_refresh=True
next(n for n in nt.nodes if n.type=='EMISSION').inputs['Strength'].default_value=1.15
wide_monitor_lens=39
if WIDE:
 cam.location=(1.15,.28,1.55);cam.rotation_euler=(Vector((.1095,-.7959,1.262))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=39;bpy.context.view_layer.update()
 points=[world_to_camera_view(s,cam,screen.matrix_world@v.co)for v in screen.data.vertices]
 width=max(p.x for p in points)-min(p.x for p in points);height=max(p.y for p in points)-min(p.y for p in points)
 wide_monitor_lens=39*min(.88/width,.80/height)

with wave.open(str(ROOT/'assets/voz/narracao_completa.wav'))as w:sr=w.getframerate();voice=array.array('h',w.readframes(w.getnframes()))
def empty(name,loc=(0,0,0),parent=None):
 o=bpy.data.objects.new(name,None);s.collection.objects.link(o);o.parent=parent;o.location=loc;return o
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
def curve(keys,t):
 if t<=keys[0][0]:return keys[0][1]
 for (t0,v0),(t1,v1)in zip(keys,keys[1:]):
  if t<=t1:
   u=smooth((t-t0)/(t1-t0))
   if isinstance(v0,(float,int)):return v0+(v1-v0)*u
   return tuple(x+(y-x)*u for x,y in zip(v0,v1))
 return keys[-1][1]
def talk(t):
 t=math.floor(t*8)/8;v=voice[int(t*sr):int((t+.065)*sr)];return sum((x/32768)**2 for x in v)/max(1,len(v))>.0007
def toward(rig,point):
 p=rig.pose.bones['head'];bpy.context.view_layer.update();m=p.matrix.copy();wq=rig.matrix_world.to_quaternion();fwd=(wq@m.to_quaternion()@rest['head'].inverted())@Vector((0,-1,0));v=Vector(point)-(rig.matrix_world@m.translation);ang=math.atan2(v.y,v.x)-math.atan2(fwd.y,fwd.x);delta=wq.inverted()@Quaternion((0,0,1),ang)@wq
 p.matrix=Matrix.LocRotScale(m.translation,delta@m.to_quaternion(),m.to_scale());bpy.context.view_layer.update();q=p.rotation_quaternion.copy();p.rotation_quaternion=(base2 if rig.name=='TRIAGE | Dery rig'else base)['head'];bpy.context.view_layer.update();return q
head_cam=toward(r,(2.1,-.85,1.65));head_final=toward(r,(1.25,-1.25,1.56));head_side=toward(r,(1.8,-.45,1.55));head_monitor=toward(r,(.11,-.80,1.30))
shoulders={side:r.matrix_world@r.pose.bones['arm_'+side].head for side in ['R','L']};front=Vector((math.sin(.6),-math.cos(.6),0));up=Vector((0,0,1))



Rkeys=[(0,(.17,.10,-.30,0)),(1.3,(.17,.10,-.30,0)),(1.6,(.25,.09,-.13,.85)),(2.3,(.25,.09,-.13,.85)),(3.0,(.17,.10,-.30,0)),(11.2,(.17,.10,-.30,0)),(11.6,(.20,.08,-.21,.35)),(12.2,(.20,.08,-.21,.35)),(13.4,(.17,.10,-.30,0))]
Lkeys=[(0,(.19,.10,-.29,0)),(11.2,(.19,.10,-.29,0)),(11.55,(.24,.11,-.16,.75)),(12.65,(.24,.11,-.16,.75)),(13.5,(.19,.10,-.29,0))]
orient={}
for side in ['R','L']:
 o=empty('ACTING | '+side+' palm');o.rotation_mode='QUATERNION';orient[side]=o;c=r.pose.bones['hand_'+side].constraints.new('COPY_ROTATION');c.target=o;c.owner_space='WORLD';c.target_space='WORLD'
objects=[]
def box(name,loc,size,mat,parent=None):
 o=H.box('TRIAGE | '+name,loc,size,mat,parent);objects.append(o);return o
def graphic(name,filename):
 mat=H.material('TRIAGE | '+name,lit=False);nt=mat.node_tree;tx=nt.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(ROOT/'assets/memes'/filename),check_existing=True);tx.interpolation='Closest';nt.links.new(tx.outputs['Color'],next(n for n in nt.nodes if n.type=='EMISSION').inputs['Color']);return mat
wall=H.material('TRIAGE | mint wall',(.30,.40,.37),lit=False);floor=H.material('TRIAGE | floor',(.17,.24,.24),lit=False);light=H.material('TRIAGE | pale tabletop',(.56,.62,.55),lit=False);metal=H.material('TRIAGE | teal trim',(.12,.29,.30),lit=False);dark=H.material('TRIAGE | seat cloth',(.035,.065,.074),lit=False);fabric=H.material('TRIAGE | privacy fabric',(.63,.72,.64),lit=False)
# Reuse the meeting-room shell; change its colors for a small mint/cream triage bay.
with bpy.data.libraries.load(str(REPO/'assets/cenarios/sala_reuniao/Sala_Reuniao.blend'))as(src,dst):
 dst.objects=[n for n in src.objects if n.startswith(('MEETING | floor','MEETING | back wall','MEETING | skirting','MEETING | wall seam'))]
for o in dst.objects:s.collection.objects.link(o)
bpy.context.view_layer.update()
for o in dst.objects:
 mw=o.matrix_world.copy();o.parent=None;o.matrix_world=Matrix.Translation((20,0,0))@mw;o.animation_data_clear();o.hide_render=False;o.name=o.name.replace('MEETING |','TRIAGE | shell')
 for m in list(o.modifiers):
  if m.type=='NODES':o.modifiers.remove(m)
 o.data.materials[0]=floor if 'floor'in o.name else wall if 'back wall'in o.name else metal;objects.append(o)
# Crisp, authored 32px floor tiles.
im=bpy.data.images.new('TRIAGE | 32px floor',32,32);pixels=[]
for yy in range(32):
 for xx in range(32):
  v=.18 if(xx//4+yy//4)%2 else .22;pixels.extend((v,v*1.20,v*1.16,1))
im.pixels=pixels;im.pack();nt=floor.node_tree;tx=nt.nodes.new('ShaderNodeTexImage');tx.image=im;tx.interpolation='Closest';tc=nt.nodes.new('ShaderNodeTexCoord');nt.links.new(tc.outputs['Generated'],tx.inputs['Vector']);nt.links.new(tx.outputs['Color'],next(n for n in nt.nodes if n.type=='EMISSION').inputs['Color'])
local=empty('TRIAGE | local origin',(20,.10,0));local.rotation_euler.z=.6
box('seat',(0,0,.49),(.56,.52,.12),dark,local);box('seat back',(0,.25,.99),(.59,.12,.98),dark,local)
for xx in [-.18,.18]:
 for yy in [-.15,.17]:box('seat leg',(xx,yy,.23),(.04,.04,.45),metal,local)
box('table',(0,-.69,.685),(2.3,.58,.10),light,local)
for xx in [-.89,.89]:box('table leg',(xx,-.69,.32),(.07,.45,.64),metal,local)
box('keyboard',(-.18,-.78,.75),(.46,.16,.025),metal,local)
for i in range(6):box('keyboard key',(-.36+i*.07,-.79,.767),(.048,.08,.012),light,local)
# A simple folding privacy screen identifies the new location without another character.
privacy=empty('TRIAGE | privacy screen',(-1.32,.29,0),local)
for i in [-1,0,1]:
 part=empty('TRIAGE | privacy segment '+str(i),(i*.37,0,0),privacy);part.rotation_euler.z=i*.16
 box('privacy cloth',(0,0,.96),(.35,.045,1.65),fabric,part)
 for x in [-.18,.18]:box('privacy edge',(x,0,.94),(.025,.075,1.83),metal,part)
 for z in [.15,1.79]:box('privacy rail',(0,0,z),(.39,.075,.025),metal,part)
# Normal Mercy reference and an authored blue heart stay fixed on the rear wall.
box('reference frame',(21.13,1.52,1.64),(1.37,.09,.83),metal)
o=H.quad('TRIAGE | Mercy picture',[(20.48,1.468,1.25),(21.78,1.468,1.25),(21.78,1.468,2.03),(20.48,1.468,2.03)],graphic('Mercy wings','mercy_asas.jpg'));objects.append(o)
box('heart frame',(18.95,1.52,1.70),(.51,.09,.51),metal)
o=H.quad('TRIAGE | heart picture',[(18.71,1.468,1.46),(19.19,1.468,1.46),(19.19,1.468,1.94),(18.71,1.468,1.94)],graphic('heart symbol','coracao.png'));objects.append(o)
# Three FILE textures, not a shared movie, make the fictional terminal deterministic.
box('terminal foot',(.65,-.63,.77),(.31,.24,.06),metal,local);box('terminal stem',(.65,-.62,.85),(.07,.07,.15),metal,local);box('terminal bezel',(.65,-.63,1.12),(.93,.12,.55),dark,local)
panelmat=H.material('TRIAGE | dictionary terminal',lit=False);panelnodes=panelmat.node_tree;images=[]
for name in ['censurado.png','verbete.png','indeferido.png']:
 tx=panelnodes.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(ROOT/'assets/memes'/name));tx.interpolation='Closest';images.append(tx)
dictionary=panelnodes.nodes.new('ShaderNodeMixRGB');dictionary.name='TRIAGE | dictionary';panelnodes.links.new(images[0].outputs['Color'],dictionary.inputs[1]);panelnodes.links.new(images[1].outputs['Color'],dictionary.inputs[2])
verdict=panelnodes.nodes.new('ShaderNodeMixRGB');verdict.name='TRIAGE | verdict';panelnodes.links.new(dictionary.outputs[0],verdict.inputs[1]);panelnodes.links.new(images[2].outputs['Color'],verdict.inputs[2]);panelnodes.links.new(verdict.outputs[0],next(n for n in panelnodes.nodes if n.type=='EMISSION').inputs['Color'])
o=H.quad('TRIAGE | terminal picture',[(.205,-.699,.87),(1.095,-.699,.87),(1.095,-.699,1.37),(.205,-.699,1.37)],panelmat,parent=local);objects.append(o)
r2=r.copy();r2.data=r.data.copy();r2.name='TRIAGE | Dery rig';s.collection.objects.link(r2);r2.animation_data_clear();mw=r.matrix_world.copy();mw.translation.x+=20;r2.parent=None;r2.matrix_world=mw
for p in r2.pose.bones:
 p.rotation_quaternion=base[p.name]
 for c in list(p.constraints):p.constraints.remove(c)
for p in r2.pose.bones:
 kw={}if p.parent is None else dict(parent_matrix=seated_pose[p.parent.name],parent_matrix_local=p.parent.bone.matrix_local)
 p.matrix_basis=p.bone.convert_local_to_pose(seated_pose[p.name],p.bone.matrix_local,invert=True,**kw)
bpy.context.view_layer.update();basis2={p.name:p.matrix_basis.copy()for p in r2.pose.bones};base2={p.name:p.rotation_quaternion.copy()for p in r2.pose.bones}
a2=a.copy();a2.data=a.data.copy();a2.name='TRIAGE | Dery';s.collection.objects.link(a2);a2.animation_data_clear();a2.parent=r2;a2.matrix_parent_inverse=Matrix.Identity(4);a2.matrix_basis=Matrix.Identity(4)
for m in list(a2.modifiers):
 if m.type=='NODES':a2.modifiers.remove(m)
 elif m.type=='ARMATURE':m.object=r2
install_faces(a2);nt=a2.data.materials[1].node_tree;illum=neutral_light(nt)
for n in list(nt.nodes):
 if n.type=='VERTEX_COLOR'and n.layer_name=='PS1FaceLightFit':
  for link in list(n.outputs['Color'].links):nt.links.new(illum,link.to_socket)
a2.data.materials[1]['DeryNeutralLight']=True;precision(a2,True)


for o in objects:precision(o)
head_triage=toward(r2,(22,-1.9,1.72));head_close=toward(r2,(21.4,-1.6,1.62));terminal_point=local.matrix_world@Vector((.65,-.65,1.12));head_terminal=toward(r2,terminal_point)
bpy.context.view_layer.update();shoulders2={side:r2.matrix_world@r2.pose.bones['arm_'+side].head for side in ['R','L']};w2={};p2={}
for side in ['R','L']:
 w2[side]=empty('TRIAGE | '+side+' wrist');ik=r2.pose.bones['forearm_'+side].constraints.new('IK');ik.target=w2[side];ik.chain_count=2;ik.use_stretch=False
 p2[side]=empty('TRIAGE | '+side+' palm');p2[side].rotation_mode='QUATERNION';c=r2.pose.bones['hand_'+side].constraints.new('COPY_ROTATION');c.target=p2[side];c.owner_space='WORLD';c.target_space='WORLD'
TR=[(0,(.17,.10,-.30,0)),(16.65,(.17,.10,-.30,0)),(16.95,(.23,.10,-.17,.7)),(17.5,(.23,.10,-.17,.7)),(18.25,(.16,.10,-.31,0)),(21.5,(.16,.10,-.31,0)),(21.95,(.25,.09,-.14,.8)),(23.0,(.25,.09,-.14,.8)),(25.15,(.25,.09,-.14,.8)),(25.8,(.17,.10,-.30,0)),(29.1,(.17,.10,-.30,0))]
TL=[(0,(.19,.10,-.29,0)),(17.5,(.19,.10,-.29,0)),(17.85,(.18,.11,-.27,.2)),(18.6,(.18,.11,-.27,.2)),(19.1,(.19,.10,-.29,0)),(22.2,(.19,.10,-.29,0)),(22.55,(.19,.12,-.24,.3)),(23.1,(.19,.12,-.24,.3)),(23.8,(.19,.10,-.29,0)),(29.1,(.19,.10,-.29,0))]
for marker in list(s.timeline_markers):s.timeline_markers.remove(marker)
for sh in info['shots']:s.timeline_markers.new(f"{sh['id']:02d} | {sh['kind']} | {sh['mood']}",frame=sh['start'])
faces={'room':[],'triage':[]}
for f in range(1,N+1):
 t=(f-1)/24;sh=next(x for x in info['shots']if x['start']<=f<=x['end']);mood=sh['mood'];u=(f-sh['start'])/max(1,sh['end']-sh['start']);speaking=talk(t)
 for name,q in base.items():r.pose.bones[name].rotation_quaternion=q
 gaze=curve([(0,.8),(1.3,.8),(1.65,0),(3,0),(11.2,.4),(11.55,0),(12.8,0),(13.5,0)],t);tilt=curve([(0,0),(1.65,-.025),(2.3,-.025),(3,0),(11.6,.02),(12.5,.02),(13.5,0)],t)
 r.pose.bones['head'].rotation_quaternion=head_cam.slerp(head_monitor,gaze)@(rest['head'].inverted()@Quaternion((0,1,0),tilt)@rest['head'])
 lean=curve([(0,0),(1.6,-.025),(2.3,-.025),(3,0),(11.55,-.02),(12.7,-.02),(13.5,0)],t)
 r.pose.bones['upper_chest'].rotation_quaternion@=rest['upper_chest'].inverted()@Quaternion((1,0,0),lean)@rest['upper_chest']
 for side,sign,keys in [('R',-1,Rkeys),('L',1,Lkeys)]:
  fw,ou,z,roll=curve(keys,t);out=Vector((math.cos(.6)*sign,math.sin(.6)*sign,0));w=bpy.data.objects['R3 | '+side+' wrist'];w.location=shoulders[side]+front*fw+out*ou+up*z;H.record(w,'location',f)
  direction=(front*.75+up*(-.75+2.4*smooth((z+.29)/.33))).normalized();orient[side].rotation_quaternion=direction.to_track_quat('Y','Z')@Quaternion((0,1,0),sign*roll);H.record(orient[side],'rotation_quaternion',f)
 for p in r.pose.bones:H.record(p,'rotation_quaternion',f)
 face=(3 if speaking else 2)if t<5.12 else(12 if speaking else 20)
 if any(b<=t<b+.083 for b in [2.5,12.8]):face=10
 a['PS1_face_id']=face;a.keyframe_insert(data_path='["PS1_face_id"]',frame=f)
 if not faces['room']or faces['room'][-1]['id']!=face:faces['room'].append(dict(frame=f,id=face))
 for name,basis in basis2.items():r2.pose.bones[name].matrix_basis=basis
 glance=curve([(0,0),(16.65,.6),(17.25,.6),(17.9,0),(20.2,.15),(20.8,0),(21.5,0),(21.9,.65),(23.2,.65),(25.4,.5),(26.1,.5),(26.7,0),(29.1,0)],t)
 r2.pose.bones['head'].rotation_quaternion=(head_close if mood in ['awkward','final']else head_triage).slerp(head_terminal,glance)
 lean2=curve([(0,0),(16.65,0),(17.0,-.025),(17.55,-.025),(18.15,.045),(20.7,.045),(21.5,.045),(22.0,-.02),(23.1,-.02),(25.4,0),(26.1,.015),(29.1,.015)],t)
 r2.pose.bones['upper_chest'].rotation_quaternion@=rest['upper_chest'].inverted()@Quaternion((1,0,0),lean2)@rest['upper_chest']
 for side,sign,keys in [('R',-1,TR),('L',1,TL)]:
  fw,ou,z,roll=curve(keys,t);out=Vector((math.cos(.6)*sign,math.sin(.6)*sign,0));w2[side].location=shoulders2[side]+front*fw+out*ou+up*z;H.record(w2[side],'location',f)
  direction=(front*.75+up*(-.75+2.4*smooth((z+.29)/.33))).normalized();p2[side].rotation_quaternion=direction.to_track_quat('Y','Z')@Quaternion((0,1,0),sign*roll);H.record(p2[side],'rotation_quaternion',f)
 for p in r2.pose.bones:H.record(p,'rotation_quaternion',f)
 face2=(16 if speaking else 18)if t<23.25 else(24 if speaking else 20)if t<25.4 else(24 if speaking else 23)
 if any(b<=t<b+.083 for b in [18.2,22.9,27.1]):face2=10
 a2['PS1_face_id']=face2;a2.keyframe_insert(data_path='["PS1_face_id"]',frame=f)
 if not faces['triage']or faces['triage'][-1]['id']!=face2:faces['triage'].append(dict(frame=f,id=face2))
 dictionary.inputs[0].default_value=0 if t<23.25 else 1;verdict.inputs[0].default_value=0 if t<25.4 else 1;H.record(dictionary.inputs[0],'default_value',f);H.record(verdict.inputs[0],'default_value',f)
 if sh['kind']=='triage':
  if mood in ['awkward','final']:cam.location=(21.4,-1.6,1.62);target=Vector((20,.1,1.32));lens=56
  else:cam.location=(22.0,-2.65,1.90);target=local.matrix_world@Vector((.12,-.20,1.0));lens=37 if WIDE else 28
 elif sh['kind']=='monitor':cam.location=(1.15,.28,1.55);target=Vector((.1095,-.7959,1.262));lens=wide_monitor_lens if WIDE else 39
 else:cam.location=(2.1-.025*u,-.85+.015*u,1.65);target=Vector((0,.10,1.18));lens=42
 cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;H.record(cam,'location',f);H.record(cam,'rotation_euler',f);H.record(cam.data,'lens',f)
H.commit_curves()
for obj in [a,a2]:
 for fc in obj.animation_data.action.fcurves:
  for k in fc.keyframe_points:k.interpolation='CONSTANT'
for fc in panelnodes.animation_data.action.fcurves:
 for k in fc.keyframe_points:k.interpolation='CONSTANT'
(ROOT/'face_cues.json').write_text(json.dumps(faces,indent=2));(ROOT/'acting_cues.json').write_text(json.dumps(dict(method='Phrase-specific gestures, an interrupted presentation, dictionary palm and restrained serious ending. Complete evaluated seated pose retained; no periodic loop or added speech.',room_right=Rkeys,room_left=Lkeys,triage_right=TR,triage_left=TL,terminal_switch_seconds=[23.25,25.4],reference='Private gesture reference from episode 007; not republished.'),indent=2))
s['DeryPS1Look']=f'{405 if WIDE else 128}x228 seam-safe geometry precision; Closest textures; 5-bit RGB and ordered dither at export';s['DeryFormats']='9:16 and 16:9 with separate cameras and graphic layouts'
s.sequence_editor_create().sequences.new_sound('VOZ | supplied recording',str(ROOT/'assets/voz/narracao_mix.wav'),channel=1,frame_start=1)
s.frame_set(45);bpy.data.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();(ROOT/'output').mkdir(exist_ok=True);dest=ROOT/'output'/('Dery_Mercy_Master_16x9.blend'if WIDE else'Dery_Mercy.blend');bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
for t in [2.0,12.1,17.2,20.8,22.5,26.8,28.5]:
 f=round(t*24)+1;triage=next(x for x in info['shots']if x['start']<=f<=x['end'])['kind']=='triage'
 for o in s.objects:
  if o.type=='MESH':o.hide_render=(not triage)if o.name.startswith('TRIAGE |')else triage
 s.frame_set(f);s.render.filepath=str(ROOT/f"output/preview_{'wide_'if WIDE else ''}{f:04d}.png");bpy.ops.render.render(write_still=True)
print('MERCY_SCENE_READY',flush=True)
