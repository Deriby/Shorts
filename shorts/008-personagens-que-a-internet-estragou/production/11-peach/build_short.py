"""Peach: phrase-led acting, PS1 precision, a crown display and clearly labelled fan creations."""
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
 p.matrix=Matrix.LocRotScale(m.translation,delta@m.to_quaternion(),m.to_scale());bpy.context.view_layer.update();q=p.rotation_quaternion.copy();p.rotation_quaternion=base['head']if rig==r else Quaternion();bpy.context.view_layer.update();return q
head_cam=toward(r,(2.1,-.85,1.65));head_final=toward(r,(1.25,-1.25,1.56));head_side=toward(r,(1.8,-.45,1.55));head_monitor=toward(r,(.11,-.80,1.30))
shoulders={side:r.matrix_world@r.pose.bones['arm_'+side].head for side in ['R','L']};front=Vector((math.sin(.6),-math.cos(.6),0));up=Vector((0,0,1))



# Distinct phrase-led gestures: presentation, sigh, warning and reassurance.
R=[(0,(.17,.10,-.30,0)),(1.2,(.17,.10,-.30,0)),(1.5,(.22,.09,-.20,.45)),(1.9,(.22,.09,-.20,.45)),(2.25,(.17,.10,-.30,0)),(6.65,(.17,.10,-.30,0)),(7.0,(.23,.10,-.18,.65)),(7.75,(.23,.10,-.18,.65)),(8.6,(.17,.10,-.30,0)),(12.6,(.17,.10,-.30,0)),(12.95,(.16,.10,-.32,0)),(13.5,(.16,.10,-.32,0)),(14.0,(.17,.10,-.30,0))]
L=[(0,(.19,.10,-.29,0)),(6.8,(.19,.10,-.29,0)),(7.3,(.20,.11,-.25,.3)),(7.9,(.20,.11,-.25,.3)),(8.65,(.19,.10,-.29,0)),(12.6,(.19,.10,-.29,0)),(12.95,(.18,.11,-.26,.2)),(13.6,(.18,.11,-.26,.2)),(14.0,(.19,.10,-.29,0))]
orient={}
for side in ['R','L']:
 o=empty('ACTING | '+side+' palm');o.rotation_mode='QUATERNION';orient[side]=o;c=r.pose.bones['hand_'+side].constraints.new('COPY_ROTATION');c.target=o;c.owner_space='WORLD';c.target_space='WORLD'
objects=[]
def box(name,loc,size,mat,parent=None):
 o=H.box('SHOWCASE | '+name,loc,size,mat,parent);objects.append(o);return o
def graphic(name,filename):
 mat=H.material('SHOWCASE | '+name,lit=False);nt=mat.node_tree;tx=nt.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(ROOT/'assets/memes'/filename),check_existing=True);tx.interpolation='Closest';nt.links.new(tx.outputs['Color'],next(n for n in nt.nodes if n.type=='EMISSION').inputs['Color']);return mat
stone=H.material('SHOWCASE | rose stone',(.34,.22,.29),lit=False);gold=H.material('SHOWCASE | gold',(.72,.46,.10),lit=False);velvet=H.material('SHOWCASE | velvet',(.18,.035,.095),lit=False);dark=H.material('SHOWCASE | plum trim',(.09,.035,.10),lit=False);jewel=H.material('SHOWCASE | rose gem',(.8,.065,.25),lit=False)
with bpy.data.libraries.load(str(REPO/'assets/cenarios/museu/Museu_Internet.blend'))as(src,dst):
 dst.objects=[n for n in src.objects if n.startswith(('MUSEUM | floor','MUSEUM | wall','MUSEUM | column','MUSEUM | capital'))]
for o in dst.objects:s.collection.objects.link(o)
bpy.context.view_layer.update()
for o in dst.objects:
 mw=o.matrix_world.copy();o.parent=None;o.matrix_world=Matrix.Translation((20,0,0))@mw;o.animation_data_clear();o.hide_render=False;o.name=o.name.replace('MUSEUM |','SHOWCASE | shell')
 if o.name=='SHOWCASE | shell floor':o.scale.x*=2;o.scale.y*=2
 elif o.name=='SHOWCASE | shell wall':o.scale.x*=2
 for m in list(o.modifiers):
  if m.type=='NODES':o.modifiers.remove(m)
 o.data.materials[0]=gold if any(w in o.name for w in ['column','band'])else stone;objects.append(o)
im=bpy.data.images.new('SHOWCASE | 32px rose stone',32,32);pixels=[]
for yy in range(32):
 for xx in range(32):
  edge=yy%8==0 or(xx+(4 if(yy//8)%2 else 0))%8==0;v=.22 if edge else .34+((xx*5+yy*3)%4)*.008;pixels.extend((v,v*.66,v*.80,1))
im.pixels=pixels;im.pack();nt=stone.node_tree;tx=nt.nodes.new('ShaderNodeTexImage');tx.image=im;tx.interpolation='Closest';tc=nt.nodes.new('ShaderNodeTexCoord');nt.links.new(tc.outputs['Generated'],tx.inputs['Vector']);tx.projection='BOX';nt.links.new(tx.outputs['Color'],next(n for n in nt.nodes if n.type=='EMISSION').inputs['Color'])
left_x,right_x=18.95,21.05
box('crown pedestal',(left_x,.25,.46),(.75,.66,.92),velvet);box('pedestal plinth',(left_x,.25,.055),(.85,.76,.10),gold);box('velvet top',(left_x,.25,.96),(.81,.72,.08),velvet)
for x in [left_x-.35,left_x+.35]:box('pedestal trim',(x,-.09,.47),(.035,.025,.88),gold)
# A generic twelve-sided crown stays on its support; it never touches the avatar.
vertices=[]
for level in [0,1]:
 for i in range(12):
  angle=2*math.pi*i/12;rad=.265 if level==0 else .34;z=1.02 if level==0 else 1.34 if i%2==0 else 1.15;vertices.append((left_x+rad*math.cos(angle),.25+rad*math.sin(angle),z))
faces=[(i,(i+1)%12,12+(i+1)%12,12+i)for i in range(12)]
me=bpy.data.meshes.new('SHOWCASE | crown mesh');me.from_pydata(vertices,[],faces);me.materials.append(gold);crown=bpy.data.objects.new('SHOWCASE | crown',me);s.collection.objects.link(crown);objects.append(crown)
for i in range(3):
 x=left_x+(i-1)*.17;o=box('gem '+str(i),(x,-.025,1.11),(.075,.045,.09),jewel);o.rotation_euler.y=.785
box('display pedestal',(right_x,.25,.46),(.90,.66,.92),velvet);box('display plinth',(right_x,.25,.055),(1.0,.76,.10),gold)
box('display frame',(right_x,.35,1.45),(1.35,.13,.82),gold)
panel=H.material('SHOWCASE | card display',lit=False);pn=panel.node_tree;img=[]
for filename in ['bowser_card.png','bowsette_card.png','oficial_a.png']:
 n=pn.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(ROOT/'assets/memes'/filename));n.interpolation='Closest';img.append(n)
swap=pn.nodes.new('ShaderNodeMixRGB');swap.name='SHOWCASE | fan swap';pn.links.new(img[0].outputs['Color'],swap.inputs[1]);pn.links.new(img[1].outputs['Color'],swap.inputs[2])
official=pn.nodes.new('ShaderNodeMixRGB');official.name='SHOWCASE | official';pn.links.new(swap.outputs[0],official.inputs[1]);pn.links.new(img[2].outputs['Color'],official.inputs[2]);pn.links.new(official.outputs[0],next(n for n in pn.nodes if n.type=='EMISSION').inputs['Color'])
o=H.quad('SHOWCASE | display picture',[(right_x-.64,.279,1.08),(right_x+.64,.279,1.08),(right_x+.64,.279,1.82),(right_x-.64,.279,1.82)],panel);objects.append(o)
for x in [18.35,21.65]:
 box('wall light',(x,1.015,2.2),(.10,.05,.72),jewel);box('light base',(x,1.01,1.8),(.24,.08,.10),gold)
# Standing clone uses the previously validated castle pose without modifying the mesh.
r2=r.copy();r2.data=r.data.copy();r2.name='SHOWCASE | Dery rig';s.collection.objects.link(r2);r2.animation_data_clear();r2.parent=None;r2.rotation_mode='XYZ';r2.location=(20,-.25,0);r2.rotation_euler=(0,0,.2)
for p in r2.pose.bones:
 p.matrix_basis=Matrix.Identity(4)
 for c in list(p.constraints):p.constraints.remove(c)
a2=a.copy();a2.data=a.data.copy();a2.name='SHOWCASE | Dery';s.collection.objects.link(a2);a2.animation_data_clear();a2.parent=r2;a2.matrix_parent_inverse=Matrix.Identity(4);a2.matrix_basis=Matrix.Identity(4)
for m in list(a2.modifiers):
 if m.type=='NODES':a2.modifiers.remove(m)
 elif m.type=='ARMATURE':m.object=r2
install_faces(a2);nt=a2.data.materials[1].node_tree;illum=neutral_light(nt)
for n in list(nt.nodes):
 if n.type=='VERTEX_COLOR'and n.layer_name=='PS1FaceLightFit':
  for link in list(n.outputs['Color'].links):nt.links.new(illum,link.to_socket)
a2.data.materials[1]['DeryNeutralLight']=True;precision(a2,True)
for obj in objects:precision(obj)
head_showcase=toward(r2,(20.8,-4.0,2.0));head_close=toward(r2,(21.1,-2.2,1.82));head_crown=toward(r2,(left_x,.25,1.24));head_frame=toward(r2,(right_x,.25,1.5))
bpy.context.view_layer.update();shoulders2={side:r2.matrix_world@r2.pose.bones['arm_'+side].head for side in ['R','L']};w2={};p2={};front2=Vector((math.sin(.2),-math.cos(.2),0))
for side in ['R','L']:
 w2[side]=empty('SHOWCASE | '+side+' wrist');ik=r2.pose.bones['forearm_'+side].constraints.new('IK');ik.target=w2[side];ik.chain_count=2;ik.use_stretch=False
 p2[side]=empty('SHOWCASE | '+side+' palm');p2[side].rotation_mode='QUATERNION';c=r2.pose.bones['hand_'+side].constraints.new('COPY_ROTATION');c.target=p2[side];c.owner_space='WORLD';c.target_space='WORLD'
MR=[(0,(.14,.08,-.34,0)),(17.6,(.14,.08,-.34,0)),(17.95,(.20,.09,-.22,.45)),(18.65,(.20,.09,-.22,.45)),(19.2,(.14,.08,-.34,0)),(19.4,(.14,.08,-.34,0)),(19.75,(.24,.10,-.14,.8)),(20.4,(.24,.10,-.14,.8)),(21.1,(.14,.08,-.34,0)),(25.2,(.14,.08,-.34,0)),(25.6,(.25,.12,-.11,.85)),(26.45,(.25,.12,-.11,.85)),(27.4,(.14,.08,-.34,0)),(33,(.14,.08,-.34,0)),(33.35,(.20,.09,-.23,.5)),(34.1,(.20,.09,-.23,.5)),(34.85,(.14,.08,-.34,0)),(35.2,(.22,.10,-.18,.65)),(35.7,(.22,.10,-.18,.65)),(36.5,(.14,.08,-.34,0))]
ML=[(0,(.14,.08,-.34,0)),(19.2,(.14,.08,-.34,0)),(19.6,(.20,.09,-.23,.45)),(20.1,(.20,.09,-.23,.45)),(20.8,(.14,.08,-.34,0)),(25.5,(.14,.08,-.34,0)),(25.95,(.22,.11,-.17,.75)),(26.6,(.22,.11,-.17,.75)),(27.4,(.14,.08,-.34,0)),(34.9,(.14,.08,-.34,0)),(35.35,(.18,.09,-.25,.4)),(35.9,(.18,.09,-.25,.4)),(36.65,(.14,.08,-.34,0))]
for m in list(s.timeline_markers):s.timeline_markers.remove(m)
for sh in info['shots']:s.timeline_markers.new(f"{sh['id']:02d} | {sh['kind']} | {sh['mood']}",frame=sh['start'])
faces={'room':[],'showcase':[]}
for f in range(1,N+1):
 t=(f-1)/24;sh=next(x for x in info['shots']if x['start']<=f<=x['end']);mood=sh['mood'];u=(f-sh['start'])/max(1,sh['end']-sh['start']);speaking=talk(t)
 for name,q in base.items():r.pose.bones[name].rotation_quaternion=q
 gaze=curve([(0,.7),(1.2,.7),(1.5,0),(2.25,0),(6.65,.5),(7.0,0),(7.75,0),(8.6,.2),(12.6,.15),(13.0,0),(14,0)],t)
 r.pose.bones['head'].rotation_quaternion=head_cam.slerp(head_monitor,gaze)
 tilt=curve([(0,0),(1.5,-.02),(2.1,-.02),(2.25,0),(6.9,.04),(7.8,.04),(8.6,0),(12.9,.055),(13.5,.055),(14,0)],t)
 r.pose.bones['head'].rotation_quaternion@=rest['head'].inverted()@Quaternion((0,1,0),tilt)@rest['head']
 lean=curve([(0,0),(1.5,-.02),(2.0,-.02),(2.25,0),(7.0,-.025),(7.8,-.025),(8.65,0),(12.9,.045),(13.5,.045),(14,0)],t)
 r.pose.bones['upper_chest'].rotation_quaternion@=rest['upper_chest'].inverted()@Quaternion((1,0,0),lean)@rest['upper_chest']
 for side,sign,keys in [('R',-1,R),('L',1,L)]:
  fw,ou,z,roll=curve(keys,t);out=Vector((math.cos(.6)*sign,math.sin(.6)*sign,0));w=bpy.data.objects['R3 | '+side+' wrist'];w.location=shoulders[side]+front*fw+out*ou+up*z;H.record(w,'location',f)
  direction=(front*.75+up*(-.75+2.4*smooth((z+.29)/.33))).normalized();orient[side].rotation_quaternion=direction.to_track_quat('Y','Z')@Quaternion((0,1,0),sign*roll);H.record(orient[side],'rotation_quaternion',f)
 for p in r.pose.bones:H.record(p,'rotation_quaternion',f)
 face=(12 if speaking else 20)if t<2.25 else(16 if speaking else 4)
 if any(b<=t<b+.083 for b in [1.8,7.8,13.5]):face=10
 a['PS1_face_id']=face;a.keyframe_insert(data_path='["PS1_face_id"]',frame=f)
 if not faces['room']or faces['room'][-1]['id']!=face:faces['room'].append(dict(frame=f,id=face))
 for p in r2.pose.bones:p.rotation_quaternion=Quaternion()
 hq=head_close if mood in ['reaction','laugh']else head_showcase
 glance=curve([(0,0),(17.6,.45),(18.3,.45),(19.2,.65),(20.2,.65),(20.8,0),(25.2,.4),(26.2,.4),(27.4,0),(33.0,.65),(33.65,.65),(34.1,.3),(34.85,.3),(35.2,0),(37.3,0)],t)
 r2.pose.bones['head'].rotation_quaternion=hq.slerp(head_crown if 19.2<=t<25.2 else head_frame,glance)
 nod=curve([(0,0),(17.95,-.015),(18.65,-.015),(19.2,0),(19.65,-.025),(20.2,-.025),(20.8,0),(25.6,-.035),(26.4,-.035),(27.4,0),(33.0,.01),(33.45,.06),(34.1,.06),(34.85,.02),(35.3,-.025),(35.85,.01),(36.6,0)],t)
 r2.pose.bones['upper_chest'].rotation_quaternion=rest['upper_chest'].inverted()@Quaternion((1,0,0),nod)@rest['upper_chest']
 for side,sign,keys in [('R',-1,MR),('L',1,ML)]:
  fw,ou,z,roll=curve(keys,t);out=Vector((math.cos(.2)*sign,math.sin(.2)*sign,0));w2[side].location=shoulders2[side]+front2*fw+out*ou+up*z;H.record(w2[side],'location',f)
  direction=(front2*.75+up*(-.8+2.3*smooth((z+.34)/.36))).normalized();p2[side].rotation_quaternion=direction.to_track_quat('Y','Z')@Quaternion((0,1,0),sign*roll);H.record(p2[side],'rotation_quaternion',f)
 for p in r2.pose.bones:H.record(p,'rotation_quaternion',f)
 face2=(12 if speaking else 20)if t<25.2 else(3 if speaking else 26)if t<29.2 else(16 if speaking else 22)if t<34.85 else(3 if speaking else 2)
 if any(b<=t<b+.083 for b in [18.5,20.3,26.6,33.7,36.1]):face2=10
 a2['PS1_face_id']=face2;a2.keyframe_insert(data_path='["PS1_face_id"]',frame=f)
 if not faces['showcase']or faces['showcase'][-1]['id']!=face2:faces['showcase'].append(dict(frame=f,id=face2))
 swap.inputs[0].default_value=1 if(27.1<=t<33.0 or 34.85<=t<35.5)else 0;official.inputs[0].default_value=1 if 19.2<=t<25.2 else 0
 H.record(swap.inputs[0],'default_value',f);H.record(official.inputs[0],'default_value',f)
 if sh['kind']=='showcase':
  if mood=='crown':cam.location=(19.45,-1.9,1.70);target=Vector((left_x,.25,1.18));lens=38 if WIDE else 25
  elif mood in ['reaction','laugh']:cam.location=(21.1,-2.2,1.82);target=Vector((20,-.25,1.56));lens=48
  elif mood=='fans':cam.location=(21.2,-3.4,1.96);target=Vector((20.3,.05,1.30));lens=38 if WIDE else 32
  else:cam.location=(20.8,-4.0,2.0);target=Vector((20,.05,1.12));lens=32 if WIDE else 25
 elif sh['kind']=='monitor':cam.location=(1.15,.28,1.55);target=Vector((.1095,-.7959,1.262));lens=wide_monitor_lens if WIDE else 39
 else:cam.location=(2.1-.025*u,-.85+.015*u,1.65);target=Vector((0,.10,1.18));lens=42
 cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;H.record(cam,'location',f);H.record(cam,'rotation_euler',f);H.record(cam.data,'lens',f)
H.commit_curves()
for obj in [a,a2]:
 for fc in obj.animation_data.action.fcurves:
  for k in fc.keyframe_points:k.interpolation='CONSTANT'
for fc in pn.animation_data.action.fcurves:
 for key in fc.keyframe_points:key.interpolation='CONSTANT'
(ROOT/'face_cues.json').write_text(json.dumps(faces,indent=2));(ROOT/'acting_cues.json').write_text(json.dumps(dict(method='Phrase-led presentation, sideways aside, crown palm, one fan reveal and an incredulous laugh. Original standing pose reused; no repeated punch or hand contact with props.',right=R,left=L,showcase_right=MR,showcase_left=ML,display_switches=dict(official=[19.2,25.2],bowsette=[27.1,33.0,34.85,35.5]),reference='Private gesture reference from episode 007; not republished.'),indent=2))
s['DeryPS1Look']=f'{405 if WIDE else 128}x228 seam-safe geometry precision; 128px body texture addressing; 5-bit RGB and fixed ordered dither at export';s['DeryFormats']='9:16 and 16:9, independent cameras and graphic layouts.'
s.sequence_editor_create().sequences.new_sound('VOZ | supplied recording',str(ROOT/'assets/voz/narracao_mix.wav'),channel=1,frame_start=1)
s.frame_set(80);bpy.data.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();(ROOT/'output').mkdir(exist_ok=True);dest=ROOT/'output'/('Dery_Peach_Master_16x9.blend'if WIDE else'Dery_Peach.blend');bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
for t in [1.7,7.4,13.2,18.2,19.9,25.9,33.5,35.6]:
 f=round(t*24)+1;sh=next(x for x in info['shots']if x['start']<=f<=x['end']);showcase=sh['kind']=='showcase'
 for o in s.objects:
  if o.type=='MESH':o.hide_render=(not showcase)if o.name.startswith('SHOWCASE |')else showcase
 s.frame_set(f);s.render.filepath=str(ROOT/f"output/preview_{'wide_'if WIDE else ''}{f:04d}.png");bpy.ops.render.render(write_still=True)
print('PEACH_SCENE_READY',flush=True)
