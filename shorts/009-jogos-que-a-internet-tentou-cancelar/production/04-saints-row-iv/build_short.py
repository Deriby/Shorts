"""Bully: reuse the approved room, Dery and PSX projection without rebuilding assets."""
from pathlib import Path
import bpy,sys,json,math,hashlib,wave
import numpy as np
from mathutils import Vector,Quaternion
P=Path(__file__).resolve().parent;R=next(p for p in P.parents if(p/'AGENTS.md').exists())
SOURCE=P.with_name('01-gta-san-andreas')/'output/Dery_GTA_San_Andreas.blend'
source_sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
info=json.loads((P/'timeline.json').read_text());FPS=info['fps'];N=info['frames']
sys.path[:0]=[str(R/'assets/personagens/dery'),str(R/'shorts/003-teste-quarto-gamer/production')]
from psx_render import bake_faces,affine_material
import helpers as H
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene;H.C.s=s
s.frame_set(121);bpy.context.view_layer.update()
actor=bpy.data.objects['DERY | animated character'];shop=bpy.data.objects['GTA | Dery lojista']
rig=actor.parent;store=shop.parent;cam=bpy.data.objects[s['Production | camera']]
actors=[actor,shop];rigs=[rig,store]
mesh_hashes={a.name:hashlib.sha256(np.array([v.co[:]for v in a.data.vertices],np.float32).tobytes()).hexdigest()for a in actors}
base={r.name:{p.name:p.rotation_quaternion.copy()for p in r.pose.bones}for r in rigs}
# Preserve the evaluated seated legs and all original mesh/UV data.
for obj in [*rigs,*actors,cam,cam.data]:obj.animation_data_clear()
keep=['balcão da loja','estante da loja','piso loja','parede loja','piso do banco na loja','parede do banco na loja','Dery lojista rig','Dery lojista','câmera loja','câmera arquivos','piso arquivos','parede arquivos']
for o in list(s.objects):
 if o.name.startswith('GTA | ')and o.name[6:]not in keep:bpy.data.objects.remove(o,do_unlink=True)
# Clear the previous gesture targets but retain the valid IK/palm constraints.
for r in rigs:
 for side in ['R','L']:
  for c in [*r.pose.bones['forearm_'+side].constraints,*r.pose.bones['hand_'+side].constraints]:
   if getattr(c,'target',None):c.target.animation_data_clear()
for o in s.objects:
 if o.type=='MESH'and abs(o.location.x-40)<2 and not o.name.startswith('GTA | '):o.hide_render=True # no old archive cabinet behind comparison
s.frame_start=1;s.frame_end=N;s.render.fps=FPS;s.render.resolution_x=768;s.render.resolution_y=432
s.render.engine='CYCLES';s.cycles.samples=1;s.cycles.use_denoising=False;s.render.use_persistent_data=True
s.render.threads_mode='FIXED';s.render.threads=2;s.render.dither_intensity=0
screen=bpy.data.objects['Tela do PC | substituir por vídeo']
tex=next(n for n in screen.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE')
tex.image=bpy.data.images.load(str(P/info['monitor_file']),check_existing=True);tex.interpolation='Closest'
tex.image_user.frame_start=1;tex.image_user.frame_offset=0;tex.image_user.frame_duration=N;tex.image_user.use_auto_refresh=True

def write_curve(owner,path,values,component=0,constant=False):
 if not owner.animation_data:owner.animation_data_create()
 if not owner.animation_data.action:owner.animation_data.action=bpy.data.actions.new(owner.name+' | Saints Row IV')
 a=owner.animation_data.action;old=a.fcurves.find(path,index=component)
 if old:a.fcurves.remove(old)
 fc=a.fcurves.new(path,index=component);fc.keyframe_points.add(len(values));fc.keyframe_points.foreach_set('co',[x for pair in values for x in pair])
 for k in fc.keyframe_points:k.interpolation='CONSTANT'if constant else'LINEAR'
 fc.update()
def smooth(x):x=max(0,min(1,x));return x*x*x*(10+x*(-15+6*x))
def interpolate(keys,t):
 if t<=keys[0][0]:return np.array(keys[0][1],float)
 if t>=keys[-1][0]:return np.array(keys[-1][1],float)
 k=next(i for i in range(len(keys)-1)if t<keys[i+1][0]);a,x=keys[k];b,y=keys[k+1];x=np.array(x,float);y=np.array(y,float)
 if np.allclose(x,y):return x
 prev=keys[max(0,k-1)];nxt=keys[min(len(keys)-1,k+2)]
 m0=(y-np.array(prev[1]))/max(.01,b-prev[0])*.55 if k else np.zeros_like(x)
 m1=(np.array(nxt[1])-x)/max(.01,nxt[0]-a)*.55 if k+2<len(keys)else np.zeros_like(x)
 u=(t-a)/(b-a);return(2*u**3-3*u*u+1)*x+(u**3-2*u*u+u)*(b-a)*m0+(-2*u**3+3*u*u)*y+(u**3-u*u)*(b-a)*m1

# A fictional classification desk: the same bank desk, shelves and filing cabinet.
gold=H.material('SRIV | gold',(.95,.63,.08),lit=False);paper=H.material('SRIV | paper',(.82,.80,.70),lit=False)
red=H.material('SRIV | refused',(.70,.06,.04),lit=False);dark=H.material('SRIV | ink',(.025,.027,.04),lit=False)
green=H.material('SRIV | cleared',(.08,.45,.21),lit=False);purple=H.material('SRIV | alien crate',(.31,.10,.43),lit=False)
metal=H.material('SRIV | metal',(.34,.37,.42),lit=False)
new_meshes=[]
def box(name,loc,size,mat,parent=None):
 o=H.box('SRIV | '+name,loc,size,mat,parent);new_meshes.append(o);return o
def text(name,body,loc,size,mat=paper):
 d=bpy.data.curves.new('SRIV | '+name,'FONT');d.body=body;d.align_x='CENTER';d.align_y='CENTER';d.size=size;d.extrude=.001
 o=bpy.data.objects.new('SRIV | '+name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(math.pi/2,0,0);d.materials.append(mat);return o
# AU is a sign within the set, never an overlaid subtitle.
box('country sign',(20,1.64,1.98),(.39,.04,.21),dark);text('country','AU',(20,1.61,1.98),.13,gold)
crate=box('case',(20,-.50,.96),(.55,.30,.31),purple)
for x in[19.79,20.21]:box('crate strap',(x,-.50,.965),(.035,.32,.33),metal)
lid=bpy.data.objects.new('SRIV | lid hinge',None);s.collection.objects.link(lid);lid.location=(20,-.35,1.11)
box('lid',(0,-.15,0),(.57,.32,.05),metal,lid)
for sec,ang in[(0,0),(21,0),(21.35,-.8),(22.0,-.8),(23.6,0),(40.98,0)]:
 lid.rotation_euler=(ang,0,0);lid.keyframe_insert('rotation_euler',frame=round(sec*FPS)+1)
card=box('rating card',(20,-.68,1.14),(.30,.025,.29),paper)
rc=text('refused label','RC',(20,-.697,1.15),.16,red)
ma=text('revised label','MA15+',(20,-.697,1.15),.078,green)
for obj,keys in[(rc,[(0,False),(35.5,True)]),(ma,[(0,True),(35.5,False)])]:
 for sec,hidden in keys:obj.hide_render=hidden;obj.keyframe_insert('hide_render',frame=round(sec*FPS)+1)
# A little folder is removed from the shipment as the modified version is mentioned.
folder=box('optional mission folder',(20.14,-.58,1.26),(.17,.025,.20),gold)
for sec,x,sc in[(0,20.14,1),(34.6,20.14,1),(35.5,20.39,1),(35.9,20.57,.02),(40.98,20.57,.02)]:
 folder.location.x=x;folder.scale=(sc,sc,sc);folder.keyframe_insert('location',frame=round(sec*FPS)+1);folder.keyframe_insert('scale',frame=round(sec*FPS)+1)
# Archive metaphor: document marked RC, supported by the existing OFFICE cabinet.
for obj in s.objects:
 if obj.type=='MESH'and abs(obj.location.x-40)<2 and not obj.name.startswith(('GTA | ','SRIV | ')):obj.hide_render=False
box('document',(40,-.51,1.1),(.62,.045,.73),paper);text('document RC','RC',(40,-.54,1.19),.29,red)
for z in[.90,.84]:box('document lines',(40,-.54,z),(.39,.018,.022),dark)
box('archive country sign',(40,-.53,1.66),(.44,.03,.19),dark);text('archive AU','AU',(40,-.55,1.66),.11,gold)
# The screen surface itself is a clean-media surface. The character and bezel keep PSX.
for modifier in list(screen.modifiers):
 if modifier.type=='NODES':screen.modifiers.remove(modifier)
screen.data.materials[0]=screen.data.materials[0].copy();screen['Clean media surface']=True
nt=screen.data.materials[0].node_tree;image_node=next(n for n in nt.nodes if n.type=='TEX_IMAGE');uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map='UVMap';nt.links.new(uv.outputs[0],image_node.inputs['Vector']);image_node.interpolation='Linear'
projection=bpy.data.node_groups['PSX | snapped vertices + affine UVs']
for obj in new_meshes:
 if not obj.data.uv_layers:H.uv_faces(obj)
 attr=obj.data.attributes.get('PS1SnapWeight')or obj.data.attributes.new(name='PS1SnapWeight',type='FLOAT',domain='POINT')
 for value in attr.data:value.value=1
 m=obj.modifiers.new('PSX | snapped vertices and affine UV','NODES');m.node_group=projection
 for mat in obj.data.materials:affine_material(mat,'UVMap',1)

# Camera cuts are phrase-led. The original camera object is retained for GN pointers.
for marker in list(s.timeline_markers):s.timeline_markers.remove(marker)
for sh in info['shots']:
 preset=bpy.data.objects[{'monitor':'TESTE | jogo no CRT','host':'TESTE | apresentador','close':'TESTE | reação','shop':'GTA | câmera loja','archive':'GTA | câmera arquivos'}.get(sh['kind'],'TESTE | apresentador')]
 position=preset.location.copy();rotation=preset.rotation_euler.copy();lens=preset.data.lens
 if sh['kind']=='archive':position=Vector((40,-3.15,1.5));rotation=(Vector((40,-.1,1.12))-position).to_track_quat('-Z','Y').to_euler();lens=36
 forward=rotation.to_quaternion()@Vector((0,0,-1))
 for frame in range(sh['start'],sh['end']+1):
  u=(frame-sh['start'])/max(1,sh['end']-sh['start']);cam.location=position+forward*(.03*smooth(u)if sh['kind']in['host','shop']else 0)
  cam.keyframe_insert('location',frame=frame)
 for f in[sh['start'],sh['end']]:
  cam.rotation_euler=rotation;cam.data.lens=lens;cam.keyframe_insert('rotation_euler',frame=f);cam.data.keyframe_insert('lens',frame=f)
 s.timeline_markers.new(f"{sh['id']:02d} {sh['mood']}",frame=sh['start'])
for owner,path in[(cam,'rotation_euler'),(cam.data,'lens')]:
 for fc in owner.animation_data.action.fcurves:
  if fc.data_path==path:
   for k in fc.keyframe_points:k.interpolation='CONSTANT'
s.camera=cam

# Fresh gesture beats on this voice, with asymmetric arcs and held intentions.
REST=(.13,.10,-.34,.08,.08);STAND=(.13,.11,-.39,.05,.1)
def beats(rest,specs):
 result=[(0,rest)]
 for t,pose,hold,ret in specs:
  result.extend([(t-.22,rest),(t,pose),(t+hold,pose),(t+hold+ret,rest)])
 result.append((info['duration'],rest));return sorted(result)
Rhand=beats(REST,[(3.62,(.21,.16,-.20,.66,.50),.22,.70),(5.15,(.24,.18,-.16,.83,.68),.22,.65),(12.05,(.24,.17,-.17,.72,.60),.30,.70),(13.45,(.20,.15,-.22,.56,.42),.22,.64)])
Lhand=beats(REST,[(4.35,(.21,.18,-.21,.58,.65),.24,.60),(12.75,(.21,.20,-.20,.64,.70),.28,.65)])
SR=beats(STAND,[(20.48,(.25,.18,-.18,.80,.57),.25,.70),(22.1,(.23,.15,-.13,.92,.44),.30,.65),(24.4,(.26,.19,-.17,.82,.72),.34,.75),(35.03,(.24,.17,-.20,.68,.57),.27,.67),(36.7,(.25,.18,-.16,.85,.68),.26,.70)])
SL=beats(STAND,[(21.25,(.22,.19,-.22,.60,.72),.30,.65),(23.35,(.23,.20,-.18,.76,.66),.28,.70),(25.4,(.22,.19,-.19,.70,.62),.26,.70),(35.8,(.23,.20,-.20,.65,.74),.25,.70),(37.5,(.22,.18,-.20,.67,.62),.20,.58)])
metrics={}
for r,paths in[(rig,{'R':Rhand,'L':Lhand}),(store,{'R':SR,'L':SL})]:
 # No old action is evaluated when the new curves are installed.
 bpy.context.view_layer.update();basis=r.matrix_world.to_quaternion();fwd=basis@Vector((0,-1,0));lat=basis@Vector((1,0,0));up=Vector((0,0,1))
 shoulders={side:r.matrix_world@r.pose.bones['arm_'+side].head for side in['R','L']}
 for side,sign in[('R',-1),('L',1)]:
  target=next(c for c in r.pose.bones['forearm_'+side].constraints if c.type=='IK').target
  palm=next(c for c in r.pose.bones['hand_'+side].constraints if c.type=='COPY_ROTATION').target
  q0=palm.rotation_quaternion.copy();palm.rotation_mode='QUATERNION';locations=[[]for _ in range(3)];rotations=[[]for _ in range(4)]
  maxdist=0
  for frame in range(1,N+1):
   t=(frame-1)/FPS;fw,out,z,lift,roll=interpolate(paths[side],t);activity=max(0,min(1,(z+(.39 if r==store else.34))/.22))
   delta=fwd*(fw+math.sin(t*3.4+(0 if side=='R'else.9))*.005*activity)+lat*(sign*out)+up*z
   if delta.length>.410:delta*=.410/delta.length
   maxdist=max(maxdist,delta.length);p=shoulders[side]+delta+lat*(math.sin(t*1.45)*.004)+up*(math.sin(t*1.7)*.002)
   q=Quaternion(lat,-float(lift))@q0@Quaternion((0,1,0),sign*float(roll))
   for i in range(3):locations[i].append((frame,p[i]))
   for i in range(4):rotations[i].append((frame,q[i]))
  for i,ks in enumerate(locations):write_curve(target,'location',ks,i)
  for i,ks in enumerate(rotations):write_curve(palm,'rotation_quaternion',ks,i)
  metrics[r.name+' '+side]=maxdist
 for name in['waist','spine','chest','upper_chest','neck','head']:
  pb=r.pose.bones.get(name)
  if not pb:continue
  rest=pb.bone.matrix_local.to_quaternion();ks=[[]for _ in range(4)]
  for frame in range(1,N+1):
   t=(frame-1)/FPS
   pitch=(.019*math.sin((t-.08)*2.1)+.012*math.sin(t*4.2))if name=='head'else .011*math.sin(t*1.72)+.006*math.sin(t*.63+.8)if name in['chest','upper_chest']else .004*math.sin(t*1.1)
   roll=.014*math.sin((t-.14)*1.35+.6)if name=='head'else .008*math.sin(t*1.13+.6)
   # A small nod toward the controller when the gamer joke lands.
   if r==store and name=='head':pitch+=.10*smooth((t-21.1)/.35)*(1-smooth((t-22.2)/.5))
   q=base[r.name][name]@(rest.inverted()@Quaternion((1,0,0),pitch)@Quaternion((0,1,0),roll)@rest)
   for i in range(4):ks[i].append((frame,q[i]))
  for i,k in enumerate(ks):write_curve(r,f'pose.bones["{name}"].rotation_quaternion',k,i)

families=json.loads((R/'assets/personagens/dery/expressions_ps1/v3/fala_familias.json').read_text())
with wave.open(str(P/'assets/voz/voz_timeline.wav'))as w:rate=w.getframerate();voice=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(float)/32768
# Reuse the spectral classifier from the approved revision, not its old times.
source_code=(P.with_name('01-gta-san-andreas')/'revise_animation.py').read_text()
exec(source_code[source_code.index('def mouth_at(t):'):source_code.index('face_metrics={}')])
faces={}
for a in actors:
 keys=[]
 for frame in range(1,N+1):
  t=(frame-1)/FPS;mood='sarcastica'if t<20 else'irritada'if t<34.6 else'alegre'
  value=families[mood][mouth_at(math.floor(t*15)/15)]
  for begin,end,index in[(4.2,4.45,118),(5.8,6.15,107),(12.1,12.35,122),(13.8,14.2,106),(21.2,21.45,111),(25.8,26.2,105),(35.7,35.95,84),(37.8,38.3,107)]:
   if begin<=t<end:value=index
  for blink in[3.7,5.5,12.7,20.8,23.4,25.1,35.0,37.2]:
   if blink<=t<blink+.1:value=10
  keys.append((frame,value))
 write_curve(a,'["PS1_face_id"]',keys,constant=True);bake_faces(a,keys)
 faces[a.name]=dict(unique_ids=len(set(v for _,v in keys)),changes=sum(x[1]!=y[1]for x,y in zip(keys,keys[1:])),material_baked=True)
s.frame_set(121);bpy.context.view_layer.update()
for a in actors:assert hashlib.sha256(np.array([v.co[:]for v in a.data.vertices],np.float32).tobytes()).hexdigest()==mesh_hashes[a.name]
# Convert remaining old paths before changing the save directory; preserve packed textures.
for image in bpy.data.images:
 if image.filepath and image.source in['FILE','MOVIE']and not image.packed_file:image.filepath=bpy.path.abspath(image.filepath)
bpy.ops.file.pack_all();bpy.ops.file.make_paths_relative()
(P/'output').mkdir(exist_ok=True);s['Production | chapter']='Saints Row IV';s['Production | fps']=30;s['Production | revision']=2
bpy.ops.wm.save_as_mainfile(filepath=str(P/'output/Dery_Saints_Row_IV.blend'),compress=True)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_sha
report=dict(source=str(SOURCE.relative_to(R)),source_sha256=source_sha,source_unchanged=True,meshes_unchanged=True,fps=FPS,frames=N,faces=faces,max_wrist_reach=metrics,psx_group=projection.name,filmora_formats=['9:16'],long_project_deferred=True)
(P/'construcao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('SAINTS_ROW_IV_SCENE_READY',json.dumps(report),flush=True)
