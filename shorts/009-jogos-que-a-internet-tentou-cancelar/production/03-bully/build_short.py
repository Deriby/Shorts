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
 if not owner.animation_data.action:owner.animation_data.action=bpy.data.actions.new(owner.name+' | Bully')
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

# A game hearing: bank furniture and books, a mallet and a controller reveal.
gold=H.material('Bully | brass',(.85,.57,.10),lit=False);paper=H.material('Bully | paper',(.8,.78,.68),lit=False)
red=H.material('Bully | red',(.67,.065,.035),lit=False);dark=H.material('Bully | ink',(.024,.027,.038),lit=False)
green=H.material('Bully | flag green',(.035,.38,.12),lit=False);yellow=H.material('Bully | flag yellow',(.94,.68,.025),lit=False)
blue=H.material('Bully | flag blue',(.045,.10,.42),lit=False);wood=H.material('Bully | wood',(.30,.12,.047),lit=False)
metal=H.material('Bully | steel',(.42,.45,.48),lit=False);controller_mat=H.material('Bully | controller',(.32,.34,.36),lit=False)
new_meshes=[]
def box(name,loc,size,mat,parent=None):
 o=H.box('Bully | '+name,loc,size,mat,parent);new_meshes.append(o);return o
def text(name,body,loc,size,mat=paper):
 d=bpy.data.curves.new('Bully | '+name,'FONT');d.body=body;d.align_x='CENTER';d.align_y='CENTER';d.size=size;d.extrude=.001
 o=bpy.data.objects.new('Bully | '+name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(math.pi/2,0,0);d.materials.append(mat);return o
def bank_copy(source,name,target):
 corners=[source.matrix_world@Vector(c)for c in source.bound_box];bottom=Vector(((min(v.x for v in corners)+max(v.x for v in corners))/2,(min(v.y for v in corners)+max(v.y for v in corners))/2,min(v.z for v in corners)))
 o=source.copy();o.data=source.data.copy();o.name='Bully | '+name;s.collection.objects.link(o);o.animation_data_clear();o.parent=None
 o.matrix_world=source.matrix_world.copy();o.location+=Vector(target)-bottom
 for m in list(o.modifiers):
  if m.type=='NODES':o.modifiers.remove(m)
 new_meshes.append(o);return o
books=next(o for o in s.objects if o.type=='MESH'and o.name.startswith('Livros e revistas'))
loz=min((books.matrix_world@Vector(c)).z for c in books.bound_box)
for i,x in enumerate([19.49,20.44]):bank_copy(books,'court books '+str(i),(x,1.18,loz))
# Props stay on the desk; there is no fragile hand attachment or new avatar mesh.
baseplate=H.cylinder('Bully | mallet base',(19.72,-.59,.82),.095,.035,wood,vertices=12);new_meshes.append(baseplate)
mallet=bpy.data.objects.new('Bully | mallet',None);s.collection.objects.link(mallet);mallet.location=(19.72,-.59,.86)
handle=H.cylinder('Bully | mallet handle',(0,0,.08),.012,.16,wood,mallet,vertices=8);new_meshes.append(handle)
head=H.cylinder('Bully | mallet head',(0,0,.17),.037,.14,wood,mallet,vertices=10,rot=(0,math.pi/2,0));new_meshes.append(head)
for time,angle in[(0,.95),(21.7,.95),(22.0,.5),(22.18,1.05),(22.5,.95),(info['duration'],.95)]:
 mallet.rotation_euler=(angle,0,0);mallet.keyframe_insert('rotation_euler',frame=round(time*FPS)+1)
pad=bpy.data.objects.new('Bully | gamepad reveal',None);s.collection.objects.link(pad);pad.location=(20,-.65,.85)
box('pad center',(0,0,0),(.27,.10,.045),controller_mat,pad)
for sign in[-1,1]:
 o=box('pad grip '+str(sign),(sign*.132,.028,-.012),(.085,.13,.055),controller_mat,pad);o.rotation_euler.z=sign*.27
box('dpad h',(-.086,-.008,.030),(.056,.018,.012),dark,pad);box('dpad v',(-.086,-.008,.030),(.018,.056,.012),dark,pad)
for x,y,mat in[(.085,-.026,green),(.112,0,red),(.059,0,blue),(.085,.026,gold)]:
 o=H.cylinder('Bully | pad button',(x,y,.030),.009,.013,mat,pad,vertices=8);new_meshes.append(o)
for time,scale in[(0,1),(26.95,.04),(27.1,1.18),(27.36,1),(info['duration'],1)]:
 pad.scale=(scale,scale,scale);pad.keyframe_insert('scale',frame=round(time*FPS)+1)
for child in pad.children:
 for time,hidden in [(0,True),(26.96,False),(info['duration'],False)]:
  child.hide_render=hidden;child.keyframe_insert('hide_render',frame=round(time*FPS)+1)
# Brazil vignette: an existing OFFICE cabinet, a symbolic game box and a closing gate.
for o in s.objects:
 if o.type=='MESH'and abs(o.location.x-40)<2 and not o.name.startswith(('GTA | ','Bully | ')):o.hide_render=False
box('flag',(40,-.61,1.57),(.80,.026,.40),green)
flagdiamond=H.quad('Bully | flag diamond',[(39.65,-.629,1.57),(40,-.629,1.745),(40.35,-.629,1.57),(40,-.629,1.395)],yellow);new_meshes.append(flagdiamond)
flagblue=H.cylinder('Bully | blue globe',(40,-.638,1.57),.098,.014,blue,vertices=16,rot=(math.pi/2,0,0));new_meshes.append(flagblue)
box('game box',(40,-.53,1.035),(.34,.065,.47),dark);box('game cover',(40,-.57,1.035),(.29,.013,.40),paper)
text('case title','BULLY',(40,-.581,1.13),.061,dark)
# This label is on a physical prop; no captions/titles are overlaid on the video.
for i in range(2):box('case stripe '+str(i),(40,-.582,.99-i*.058),(.21,.009,.022),red)
gate=bpy.data.objects.new('Bully | sales gate',None);s.collection.objects.link(gate)
for i in range(7):box('gate bar '+str(i),(-.39+i*.13,0,0),(.016,.032,.66),metal,gate)
for z in[-.33,.33]:box('gate brace',(0,0,z),(.88,.036,.030),metal,gate)
for time,x in[(0,-.99),(32.5,-.99),(33.35,0),(info['duration'],0)]:
 gate.location=(40+x,-.72,1.03);gate.keyframe_insert('location',frame=round(time*FPS)+1)
# Reuse the approved projection group, never reinstall it on the existing avatar.
projection=bpy.data.node_groups['PSX | snapped vertices + affine UVs']
for obj in new_meshes:
 if not obj.data.uv_layers:H.uv_faces(obj)
 attr=obj.data.attributes.get('PS1SnapWeight')or obj.data.attributes.new(name='PS1SnapWeight',type='FLOAT',domain='POINT')
 for d in attr.data:d.value=1
 modifier=obj.modifiers.new('PSX | snapped vertices and affine UV','NODES');modifier.node_group=projection
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
Rhand=beats(REST,[(3.24,(.23,.15,-.20,.62,.44),.30,.65),(5.28,(.25,.18,-.15,.84,.62),.28,.72),(37.9,(.22,.16,-.18,.72,.48),.23,.65),(45.44,(.20,.17,-.23,.54,.62),.30,.68)])
Lhand=beats(REST,[(4.05,(.20,.18,-.23,.48,.60),.28,.68),(6.15,(.21,.19,-.18,.65,.70),.20,.60),(38.20,(.20,.20,-.20,.60,.66),.22,.55),(45.68,(.19,.18,-.22,.52,.65),.25,.58)])
SR=beats(STAND,[(20.35,(.24,.17,-.17,.78,.55),.30,.65),(22.1,(.25,.15,-.13,.87,.44),.33,.75),(27.2,(.23,.18,-.20,.66,.56),.28,.60),(28.55,(.24,.18,-.17,.76,.70),.24,.62)])
SL=beats(STAND,[(21.03,(.22,.18,-.23,.55,.65),.32,.70),(22.95,(.21,.17,-.20,.65,.56),.20,.60),(27.67,(.22,.20,-.20,.64,.72),.32,.70)])
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
   if r==store and name=='head':pitch+=.11*smooth((t-27.0)/.35)*(1-smooth((t-28.1)/.5))
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
  t=(frame-1)/FPS;mood='neutra'if t<7 else'irritada'if t<19.96 else'neutra'if t<26.96 else'empolgada'if t<29.94 else'irritada'if t<37.54 else'sarcastica'
  value=families[mood][mouth_at(math.floor(t*15)/15)]
  for begin,end,index in[(6.55,6.76,84),(20.15,20.35,96),(27.1,27.3,122),(28.3,28.55,107),(38.65,38.9,105),(45.3,45.55,118),(46.7,info['duration'],107)]:
   if begin<=t<end:value=index
  for blink in[3.6,6.2,21.1,22.9,28.75,38.3,45.9]:
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
(P/'output').mkdir(exist_ok=True);s['Production | chapter']='Bully';s['Production | fps']=30;s['Production | revision']=2
bpy.ops.wm.save_as_mainfile(filepath=str(P/'output/Dery_Bully.blend'),compress=True)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_sha
report=dict(source=str(SOURCE.relative_to(R)),source_sha256=source_sha,source_unchanged=True,meshes_unchanged=True,fps=FPS,frames=N,faces=faces,max_wrist_reach=metrics,psx_group=projection.name,filmora_formats=['9:16'],long_project_deferred=True)
(P/'construcao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('BULLY_SCENE_READY',json.dumps(report),flush=True)
