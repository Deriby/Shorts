"""Phrase-specific performance, discrete faces, PS1 precision and a fictional writing desk buried by rigid sheets."""
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
 p.matrix=Matrix.LocRotScale(m.translation,delta@m.to_quaternion(),m.to_scale());bpy.context.view_layer.update();q=p.rotation_quaternion.copy();p.rotation_quaternion=base['head'];bpy.context.view_layer.update();return q
head_cam=toward(r,(2.1,-.85,1.65));head_final=toward(r,(1.25,-1.25,1.56));head_side=toward(r,(1.8,-.45,1.55));head_monitor=toward(r,(.11,-.80,1.30))
shoulders={side:r.matrix_world@r.pose.bones['arm_'+side].head for side in ['R','L']};front=Vector((math.sin(.6),-math.cos(.6),0));up=Vector((0,0,1))


# Intentional gestures, keyed by the actual phrases rather than a loop.
R=[(0,(.17,.10,-.30,0)),(1.45,(.17,.10,-.30,0)),(1.8,(.24,.08,-.15,.7)),(2.45,(.24,.08,-.15,.7)),(3.05,(.17,.10,-.30,0)),(6.45,(.17,.10,-.30,0)),(6.85,(.20,.10,-.12,.3)),(7.5,(.20,.10,-.12,.3)),(8.5,(.17,.10,-.30,0)),(9.1,(.17,.10,-.30,0)),(9.45,(.19,.12,-.22,.6)),(10.2,(.17,.10,-.30,0)),(12.4,(.17,.10,-.30,0)),(12.7,(.16,.10,-.32,0)),(14,(.16,.10,-.32,0)),(21.8,(.17,.10,-.30,0)),(22.1,(.20,.06,-.07,.1)),(22.7,(.20,.06,-.07,.1)),(23.7,(.17,.10,-.30,0)),(38,(.17,.10,-.30,0)),(38.9,(.17,.10,-.30,0)),(39.3,(.23,.11,-.16,.8)),(39.9,(.23,.11,-.16,.8)),(40.6,(.17,.10,-.30,0))]
L=[(0,(.19,.10,-.29,0)),(7.6,(.19,.10,-.29,0)),(8.0,(.18,.11,-.23,.35)),(8.5,(.18,.11,-.23,.35)),(9.2,(.19,.10,-.29,0)),(21.8,(.19,.10,-.29,0)),(22.4,(.19,.10,-.25,.15)),(23.3,(.19,.10,-.29,0)),(38,(.19,.10,-.29,0)),(38.3,(.24,.12,-.13,.85)),(39.0,(.24,.12,-.13,.85)),(39.55,(.19,.10,-.23,.4)),(40.65,(.19,.10,-.29,0))]
orient={}
for side in ['R','L']:
 o=empty('ACTING | '+side+' palm');o.rotation_mode='QUATERNION';orient[side]=o;c=r.pose.bones['hand_'+side].constraints.new('COPY_ROTATION');c.target=o;c.owner_space='WORLD';c.target_space='WORLD'
# Adapt the previously validated seated clone; preserve the hip, feet and body geometry.
wall=H.material('DESK | slate',(.13,.18,.22),lit=False);floor=H.material('DESK | floor',(.08,.11,.14),lit=False);wood=H.material('DESK | wood',(.29,.18,.095),lit=False);metal=H.material('DESK | metal',(.10,.13,.15),lit=False);dark=H.material('DESK | chair cloth',(.026,.037,.046),lit=False);paper=H.material('DESK | paper',(.76,.74,.63),lit=False);edge=H.material('DESK | paper edge',(.33,.35,.33),lit=False)
objects=[]
def box(name,loc,size,mat,parent=None):
 o=H.box('DESK | '+name,loc,size,mat,parent);objects.append(o);return o
def graphic(name,filename):
 mat=H.material('DESK | '+name,lit=False);nt=mat.node_tree;tx=nt.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(ROOT/'assets/memes'/filename),check_existing=True);tx.interpolation='Closest';nt.links.new(tx.outputs['Color'],next(n for n in nt.nodes if n.type=='EMISSION').inputs['Color']);return mat
box('floor',(20,0,-.04),(9,8,.08),floor);box('back wall',(20,1.65,1.6),(9,.12,3.3),wall);box('skirting',(20,1.55,.16),(9,.07,.11),metal)
for x in [17.5,18.5,19.5,20.5,21.5,22.5]:box('wall seam',(x,1.57,1.65),(.023,.02,2.9),metal)
r2=r.copy();r2.data=r.data.copy();r2.name='DESK | Dery rig';s.collection.objects.link(r2);r2.animation_data_clear();mw=r.matrix_world.copy();mw.translation.x+=20;r2.parent=None;r2.matrix_world=mw
for p in r2.pose.bones:
 p.rotation_quaternion=base[p.name]
 for c in list(p.constraints):p.constraints.remove(c)
a2=a.copy();a2.data=a.data.copy();a2.name='DESK | Dery';s.collection.objects.link(a2);a2.animation_data_clear();a2.parent=r2;a2.matrix_parent_inverse=Matrix.Identity(4);a2.matrix_basis=Matrix.Identity(4)
for m in list(a2.modifiers):
 if m.type=='NODES':a2.modifiers.remove(m)
 elif m.type=='ARMATURE':m.object=r2
install_faces(a2);nt=a2.data.materials[1].node_tree;illum=neutral_light(nt)
for n in list(nt.nodes):
 if n.type=='VERTEX_COLOR'and n.layer_name=='PS1FaceLightFit':
  for link in list(n.outputs['Color'].links):nt.links.new(illum,link.to_socket)
a2.data.materials[1]['DeryNeutralLight']=True;precision(a2,True)
chair=empty('DESK | chair support',(20,.10,0));chair.rotation_euler.z=.6
box('chair seat',(0,0,.49),(.47,.44,.12),dark,chair);box('chair back',(0,.24,.94),(.48,.11,.76),dark,chair)
for x in [-.18,.18]:
 for y in [-.15,.17]:box('chair leg',(x,y,.23),(.04,.04,.45),metal,chair)
box('table',(20,-.82,.665),(3.8,.64,.10),wood)
for x in [18.7,21.3]:box('table leg',(x,-.82,.31),(.09,.40,.62),metal)
box('rear display bezel',(21.10,1.48,1.55),(1.72,.09,1.02),dark)
o=H.quad('DESK | display',[(20.29,1.42,1.095),(21.91,1.42,1.095),(21.91,1.42,2.005),(20.29,1.42,2.005)],screen.data.materials[0]);objects.append(o)
papers=[];labels=[graphic('sheet '+str(i),n)for i,n in enumerate(['folha_intro.png','folha_argumento.png','folha_conclusao.png'])]
for stack,(x,count)in enumerate([(19.42,28),(20.63,16)]):
 for i in range(count):
  root=empty('DESK | sheet root %s %s'%(stack,i));papers.append((root,stack,i));z=.723+i*.026
  x0=x+(.018 if i%2 else -.018);y0=-.82+(.012 if i%3 else -.014)
  box('sheet',(x0,y0,z),(.60,.43,.021),paper,root)
  box('ink edge',(x0,y0-.216,z+.004),(.52,.003,.004),edge,root)
  if i in [2,count-1]:
   o=H.quad('DESK | top sheet label',[(x0-.295,y0-.21,z+.011),(x0+.295,y0-.21,z+.011),(x0+.295,y0+.21,z+.011),(x0-.295,y0+.21,z+.011)],labels[stack%3],parent=root);objects.append(o)
for obj in objects:precision(obj)
bpy.context.view_layer.update();head_desk=toward(r2,(21.7,-3.3,1.82));head_paper=toward(r2,(19.42,-.82,1.04));head_paper=head_desk.slerp(head_paper,.55)
shoulders2={side:r2.matrix_world@r2.pose.bones['arm_'+side].head for side in ['R','L']};w2={};p2={};front2=front.copy()
for side in ['R','L']:
 w2[side]=empty('DESK | '+side+' wrist');ik=r2.pose.bones['forearm_'+side].constraints.new('IK');ik.target=w2[side];ik.chain_count=2;ik.use_stretch=False
 p2[side]=empty('DESK | '+side+' palm');p2[side].rotation_mode='QUATERNION';c=r2.pose.bones['hand_'+side].constraints.new('COPY_ROTATION');c.target=p2[side];c.owner_space='WORLD';c.target_space='WORLD'
MR=[(0,(.17,.10,-.30,0)),(18.3,(.17,.10,-.30,0)),(18.7,(.23,.08,-.17,.75)),(19.6,(.23,.08,-.17,.75)),(20.3,(.18,.10,-.24,.3)),(21.6,(.17,.10,-.30,0)),(26.9,(.17,.10,-.30,0)),(27.25,(.22,.09,-.13,.75)),(28.1,(.22,.09,-.13,.75)),(29.0,(.17,.10,-.30,0)),(47.5,(.17,.10,-.30,0))]
ML=[(0,(.19,.10,-.29,0)),(20.2,(.19,.10,-.29,0)),(20.55,(.20,.11,-.21,.45)),(21.3,(.20,.11,-.21,.45)),(21.8,(.19,.10,-.29,0)),(29.1,(.19,.10,-.29,0)),(29.45,(.20,.13,-.16,.65)),(30.1,(.20,.13,-.16,.65)),(30.9,(.19,.10,-.29,0)),(47.5,(.19,.10,-.29,0))]
for m in list(s.timeline_markers):s.timeline_markers.remove(m)
for sh in info['shots']:s.timeline_markers.new(f"{sh['id']:02d} | {sh['kind']} | {sh['mood']}",frame=sh['start'])
faces={'room':[],'desk':[]}
for f in range(1,N+1):
 t=(f-1)/24;sh=next(x for x in info['shots']if x['start']<=f<=x['end']);mood=sh['mood'];u=(f-sh['start'])/max(1,sh['end']-sh['start']);speaking=talk(t)
 for name,q in base.items():r.pose.bones[name].rotation_quaternion=q
 gaze=curve([(0,.85),(1.4,.85),(1.9,0),(3.1,0),(6.45,.3),(6.9,0),(8.5,0),(9.1,.35),(9.7,0),(12.4,0),(13.8,0),(21.8,0),(23.8,0),(38,.3),(38.5,0),(40.7,0)],t)
 r.pose.bones['head'].rotation_quaternion=head_cam.slerp(head_monitor,gaze)
 tilt=curve([(0,0),(1.8,-.025),(2.4,-.025),(3.05,0),(6.5,.07),(8.4,.07),(9.5,-.02),(10.35,0),(12.4,.035),(13.8,.035),(14.2,0),(21.8,0),(22.1,.055),(23.25,.055),(24,0),(38,.02),(38.45,.075),(39.4,.075),(40.6,0)],t)
 r.pose.bones['head'].rotation_quaternion@=rest['head'].inverted()@Quaternion((0,1,0),tilt)@rest['head']
 lean=curve([(0,0),(1.8,-.025),(2.5,-.025),(3.1,0),(6.8,.025),(8.2,.025),(9.5,0),(12.6,.045),(13.8,.045),(14.2,0),(21.8,0),(22.1,.08),(22.8,.08),(24,0),(38,0),(38.5,-.025),(39.4,-.025),(40.65,0)],t)
 r.pose.bones['upper_chest'].rotation_quaternion@=rest['upper_chest'].inverted()@Quaternion((1,0,0),lean)@rest['upper_chest']
 for side,sign,keys in [('R',-1,R),('L',1,L)]:
  fw,ou,z,roll=curve(keys,t);outward=Vector((math.cos(.6)*sign,math.sin(.6)*sign,0));w=bpy.data.objects['R3 | '+side+' wrist'];w.location=shoulders[side]+front*fw+outward*ou+up*z;H.record(w,'location',f)
  direction=(front*.75+up*(-.75+2.4*smooth((z+.29)/.33))).normalized();orient[side].rotation_quaternion=direction.to_track_quat('Y','Z')@Quaternion((0,1,0),sign*roll);H.record(orient[side],'rotation_quaternion',f)
 for p in r.pose.bones:H.record(p,'rotation_quaternion',f)
 face=(12 if speaking else 20)if t<6.45 else(16 if speaking else 18)if t<10.35 else(24 if speaking else 6)if t<21.8 else 5 if t<22.05 else(24 if speaking else 22)if t<38 else(1 if speaking else 22)
 if any(b<=t<b+.083 for b in [2.6,8.7,13.6,23.6,39.8]):face=10
 a['PS1_face_id']=face;a.keyframe_insert(data_path='["PS1_face_id"]',frame=f)
 if not faces['room']or faces['room'][-1]['id']!=face:faces['room'].append(dict(frame=f,id=face))
 for name,q in base.items():r2.pose.bones[name].rotation_quaternion=q
 glance=curve([(0,0),(18.3,.35),(18.9,.8),(19.8,.8),(20.6,0),(21.8,0),(26.9,.25),(27.5,.8),(28.3,.8),(29.1,0),(30.8,0),(46,0),(47.5,0)],t)
 r2.pose.bones['head'].rotation_quaternion=head_desk.slerp(head_paper,glance)
 nod=curve([(0,0),(18.3,.02),(18.8,-.025),(19.6,-.025),(20.5,.035),(21.8,0),(26.9,0),(27.4,-.03),(28.4,-.03),(29.2,.07),(30.6,.07),(31.5,.02),(46,.02)],t)
 r2.pose.bones['upper_chest'].rotation_quaternion@=rest['upper_chest'].inverted()@Quaternion((1,0,0),nod)@rest['upper_chest']
 for side,sign,keys in [('R',-1,MR),('L',1,ML)]:
  fw,ou,z,roll=curve(keys,t);outward=Vector((math.cos(.6)*sign,math.sin(.6)*sign,0));w2[side].location=shoulders2[side]+front2*fw+outward*ou+up*z;H.record(w2[side],'location',f)
  direction=(front2*.75+up*(-.75+2.4*smooth((z+.29)/.33))).normalized();p2[side].rotation_quaternion=direction.to_track_quat('Y','Z')@Quaternion((0,1,0),sign*roll);H.record(p2[side],'rotation_quaternion',f)
 for p in r2.pose.bones:H.record(p,'rotation_quaternion',f)
 face2=(24 if speaking else 22)if t<26.9 else(3 if speaking else 2)if t<29.1 else 5 if t<29.35 else(24 if speaking else 6)if t<46 else 6
 if any(b<=t<b+.083 for b in [20.9,28.8,30.9]):face2=10
 a2['PS1_face_id']=face2;a2.keyframe_insert(data_path='["PS1_face_id"]',frame=f)
 if not faces['desk']or faces['desk'][-1]['id']!=face2:faces['desk'].append(dict(frame=f,id=face2))
 for root,stack,i in papers:
  active=i<3 or t>=27.0+(i-3)*(.12 if stack==0 else .20)
  root.scale=(1,1,1)if active else(.0001,.0001,.0001);H.record(root,'scale',f)
 if sh['kind']=='desk':
  if mood in ['buried','final']:cam.location=(21.5,-2.35,1.69);target=Vector((19.98,-.12,1.30));lens=52 if WIDE else 48
  else:cam.location=(21.85,-3.6+.025*u,1.93);target=Vector((20.1,-.15,1.10));lens=36 if WIDE else 31
 elif sh['kind']=='monitor':cam.location=(1.15,.28,1.55);target=Vector((.1095,-.7959,1.262));lens=wide_monitor_lens if WIDE else 39
 elif mood in ['skeptic','deadpan']:cam.location=(1.8,-.45,1.55);target=Vector((0,.10,1.39));lens=60
 else:cam.location=(2.1-.025*u,-.85+.015*u,1.65);target=Vector((0,.10,1.18));lens=42
 cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;H.record(cam,'location',f);H.record(cam,'rotation_euler',f);H.record(cam.data,'lens',f)
H.commit_curves()
for obj in [a,a2]:
 for fc in obj.animation_data.action.fcurves:
  for k in fc.keyframe_points:k.interpolation='CONSTANT'
for root,_,_ in papers:
 for fc in root.animation_data.action.fcurves:
  for k in fc.keyframe_points:k.interpolation='CONSTANT'
(ROOT/'face_cues.json').write_text(json.dumps(faces,indent=2));(ROOT/'acting_cues.json').write_text(json.dumps(dict(method='Phrase gestures, asymmetric hands, preparation/holds/returns, paper glance and deadpan ending. No periodic conversation loop.',right=R,left=L,desk_right=MR,desk_left=ML,reference='Personal reference from episode 007 remains private.'),indent=2))
s['DeryPS1Look']=f'{405 if WIDE else 128}x228 seam-safe precision, Closest textures, 5-bit RGB and fixed ordered dither at export';s['DeryFormats']='9:16 and 16:9 with independent cameras and card layouts'
s.sequence_editor_create().sequences.new_sound('VOZ | supplied recording',str(ROOT/'assets/voz/narracao_mix.wav'),channel=1,frame_start=1)
s.frame_set(80);bpy.data.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();(ROOT/'output').mkdir(exist_ok=True);dest=ROOT/'output'/('Dery_Vaporeon_Master_16x9.blend'if WIDE else'Dery_Vaporeon.blend');bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
for t in [7.8,19.5,28.8,30.0,39.4,46.6]:
 f=round(t*24)+1;desk=next(x for x in info['shots']if x['start']<=f<=x['end'])['kind']=='desk'
 for o in s.objects:
  if o.type=='MESH':o.hide_render=(not desk)if o.name.startswith('DESK |')else desk
 s.frame_set(f);s.render.filepath=str(ROOT/f"output/preview_{'wide_'if WIDE else ''}{f:04d}.png");bpy.ops.render.render(write_still=True)
print('VAPOREON_SCENE_READY',flush=True)
