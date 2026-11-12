"""BMX XXX: reuse the approved room, Dery and PSX projection without rebuilding assets."""
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
 if not owner.animation_data.action:owner.animation_data.action=bpy.data.actions.new(owner.name+' | BMX')
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

# A small marketing desk, using the already imported bank desk and shelving.
gold=H.material('BMX | yellow',(.97,.64,.07),lit=False);paper=H.material('BMX | cream',(.85,.82,.71),lit=False)
red=H.material('BMX | red',(.72,.075,.045),lit=False);dark=H.material('BMX | ink',(.024,.026,.039),lit=False)
green=H.material('BMX | green',(.16,.48,.19),lit=False);purple=H.material('BMX | purple',(.28,.12,.47),lit=False)
metal=H.material('BMX | spokes',(.55,.58,.61),lit=False)
new_meshes=[]
def box(name,loc,size,mat,parent=None):
 o=H.box('BMX | '+name,loc,size,mat,parent);new_meshes.append(o);return o
def text(name,body,loc,size,mat=paper):
 d=bpy.data.curves.new('BMX | '+name,'FONT');d.body=body;d.align_x='CENTER';d.align_y='CENTER';d.size=size;d.extrude=.001
 o=bpy.data.objects.new('BMX | '+name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(math.pi/2,0,0);d.materials.append(mat);return o
header=text('letreiro','BMX',(20,1.70,2.05),.17,gold)
xs=[]
for i in range(3):
 o=text('X '+str(i),'X',(19.84+i*.16,-.61,.97),.21,red);xs.append(o)
 # Anticipation then one cartoony pop; a decisive motion rather than screen shake.
 for t,scale in [(0,0),(12.65+i*.22,0),(12.79+i*.22,1.18),(13.03+i*.22,1.0),(19.5,1),(20.0,.0),(info['duration'],0)]:
  o.scale=(scale,scale,scale);o.keyframe_insert('scale',frame=round(t*FPS)+1)
 for t,rz in [(12.65+i*.22,-.25),(12.85+i*.22,.08),(13.03+i*.22,0)]:
  o.rotation_euler=(math.pi/2,rz,0);o.keyframe_insert('rotation_euler',frame=round(t*FPS)+1)
refusal=[]
refusal.append(box('cartaz recusa',(20,-.63,1.015),(.93,.025,.43),paper))
refusal.append(text('carimbo','VENDA RECUSADA',(20,-.652,1.14),.068,red))
refusal.append(text('walmart','WALMART',(20,-.653,1.015),.082,dark))
refusal.append(text('toys','TOYS “R” US',(20,-.653,.895),.078,dark))
for o in refusal:
 for t,v in [(0,True),(20.7,True),(20.74,False),(26.08,True),(info['duration'],True)]:
  o.hide_render=v;o.keyframe_insert('hide_render',frame=round(t*FPS)+1)

# Three vertically stacked console cards remain readable in the phone crop.
text('regiao','VERSÕES DOS EUA',(40,-.58,1.68),.066,gold)
rows=[]
for index,(name,desc,z,mat)in enumerate([('PS2','CENSURADO',1.34,purple),('XBOX','CONTEÚDO MANTIDO',1.00,green),('GAMECUBE','CONTEÚDO MANTIDO',.66,purple)]):
 parent=bpy.data.objects.new('BMX | platform '+name,None);s.collection.objects.link(parent);parent.location=(40,-.57,z)
 box('card '+name,(0,0,0),(.98,.055,.29),mat,parent)
 title=text('name '+name,name,(40,-.608,z+.055),.09,paper);title.parent=parent;title.location=(0,-.038,.055)
 desc_o=text('desc '+name,desc,(40,-.608,z-.065),.048,paper);desc_o.parent=parent;desc_o.location=(0,-.038,-.065)
 # One small emphasis per spoken platform. No flickering or arbitrary motion.
 begin=[27.2,31.6,32.9][index]
 for t,zscale in[(0,1),(begin,1),(begin+.18,1.055),(begin+.50,1),(info['duration'],1)]:
  parent.scale=(zscale,zscale,zscale);parent.keyframe_insert('scale',frame=round(t*FPS)+1)
 rows.append(parent)
# Final two wheels literally leave the pitch; never attached to the avatar hands.
wheels=[]
for side in[-1,1]:
 parent=bpy.data.objects.new('BMX | wheel '+str(side),None);s.collection.objects.link(parent)
 tire=H.torus('BMX | tire '+str(side),(0,0,0),.133,.018,dark,parent,rot=(math.pi/2,0,0),segments=20);new_meshes.append(tire)
 for j in range(8):
  angle=j*math.tau/8;o=H.beam('BMX | spoke',(0,0,0),(.122*math.cos(angle),0,.122*math.sin(angle)),.005,metal,parent);new_meshes.append(o)
 hub=H.cylinder('BMX | hub',(0,0,0),.025,.045,gold,parent,vertices=8,rot=(math.pi/2,0,0));new_meshes.append(hub)
 for t in[0,39.55,39.56,40.2,41.6,42.1,42.5,43.2,info['duration']]:
  u=smooth((t-41.65)/1.45);x=side*(.22+u*.96);z=.96-max(0,u-.52)*.40
  parent.location=(20+x,-.87,z);parent.rotation_euler=(0,-side*u*7.0,0)
  parent.keyframe_insert('location',frame=round(t*FPS)+1);parent.keyframe_insert('rotation_euler',frame=round(t*FPS)+1)
 for child in parent.children:
  for t,v in [(0,True),(39.55,True),(39.56,False),(info['duration'],False)]:
   child.hide_render=v;child.keyframe_insert('hide_render',frame=round(t*FPS)+1)
 wheels.append(parent)
# Reuse the exact approved projection graph, only on new meshes.
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
 preset=bpy.data.objects[{'monitor':'TESTE | jogo no CRT','host':'TESTE | apresentador','shop':'GTA | câmera loja','archive':'GTA | câmera arquivos'}.get(sh['kind'],'TESTE | apresentador')]
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
Rhand=beats(REST,[(3.05,(.25,.16,-.17,.72,.52),.22,.60),(4.68,(.22,.12,-.12,.87,.38),.18,.52),(6.18,(.23,.18,-.20,.62,.62),.15,.65)])
Lhand=beats(REST,[(3.65,(.21,.18,-.24,.46,.60),.25,.65),(5.46,(.21,.19,-.18,.68,.74),.20,.70)])
SR=beats(STAND,[(11.98,(.25,.16,-.16,.82,.60),.25,.65),(13.45,(.22,.15,-.14,.92,.45),.25,.65),(19.85,(.23,.17,-.13,.98,.68),.15,.55),(22.15,(.27,.18,-.21,.71,.60),.20,.65),(24.65,(.23,.17,-.14,.84,.44),.20,.7),(40.13,(.24,.19,-.20,.60,.75),.22,.65),(42.5,(.22,.18,-.17,.69,.58),.2,.65)])
SL=beats(STAND,[(12.63,(.21,.18,-.24,.48,.72),.30,.70),(20.62,(.22,.19,-.16,.72,.75),.20,.65),(23.38,(.23,.20,-.20,.68,.70),.25,.7),(40.87,(.22,.19,-.22,.64,.7),.22,.65)])
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
   # A short look down at the escaping wheels, then address the viewer again.
   if r==store and name=='head':pitch+=.16*smooth((t-41.5)/.35)*(1-smooth((t-43.0)/.5))
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
  t=(frame-1)/FPS;mood='empolgada'if t<11.5 else'sarcastica'if t<19.4 else'irritada'if t<26.08 else'neutra'if t<34.52 else'sarcastica'
  value=families[mood][mouth_at(math.floor(t*15)/15)]
  for begin,end,index in[(13.12,13.34,122),(19.52,19.72,111),(20.3,20.52,106),(25.7,25.96,105),(41.8,42.04,118),(43.3,info['duration'],107)]:
   if begin<=t<end:value=index
  for blink in[3.5,6.8,12.3,21.6,24.2,40.5]:
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
(P/'output').mkdir(exist_ok=True);s['Production | chapter']='BMX XXX';s['Production | fps']=30;s['Production | revision']=2
bpy.ops.wm.save_as_mainfile(filepath=str(P/'output/Dery_BMX_XXX.blend'),compress=True)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_sha
report=dict(source=str(SOURCE.relative_to(R)),source_sha256=source_sha,source_unchanged=True,meshes_unchanged=True,fps=FPS,frames=N,faces=faces,max_wrist_reach=metrics,psx_group=projection.name,filmora_formats=['9:16'],long_project_deferred=True)
(P/'construcao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('BMX_SCENE_READY',json.dumps(report),flush=True)
