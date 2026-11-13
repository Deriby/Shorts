"""Small object gags in the existing room; only the reaction keeps Dery visible."""
from pathlib import Path
import bpy,sys,json,math,hashlib,wave
import numpy as np
from mathutils import Vector,Matrix,Quaternion
P=Path(__file__).resolve().parent;R=next(p for p in P.parents if(p/'AGENTS.md').exists());plans=json.loads((P/'plano.json').read_text());plans=[dict(ep,**g)for ep in plans for g in ep.get('gags',[{}])];sys.path[:0]=[str(R/'assets/personagens/dery'),str(R/'shorts/003-teste-quarto-gamer/production')]
import helpers as H
from psx_render import bake_faces,affine_material
SOURCE=R/'assets/personagens/dery/atuacao_sentada_teste_v1/output/Dery_Atuacao_Apoio_Real.blend';source_sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest();selected=sys.argv[sys.argv.index('--')+1:]if '--'in sys.argv else[]
def smooth(u):u=max(0,min(1,u));return u*u*(3-2*u)
def box(n,p,d,m,parent=None):return H.box('R6 | '+n,p,d,m,parent)
def sphere(n,p,d,m,parent=None):return H.sphere('R6 | '+n,p,d,m,parent,segments=12,rings=6)
def key(o,f):
 for p in ['location','rotation_euler','scale']:o.keyframe_insert(p,frame=f)
def camera_at(cam,pos,target,lens):cam.location=pos;cam.rotation_mode='XYZ';cam.rotation_euler=(Vector(target)-Vector(pos)).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens

def append_parts(path,names):
 with bpy.data.libraries.load(str(path),link=False)as(a,b):b.objects=[n for n in a.objects if names(n)]
 result=[o for o in b.objects if o]
 for o in result:
  if o.name not in bpy.context.scene.objects:bpy.context.scene.collection.objects.link(o)
  o.animation_data_clear();o.hide_render=False;o.hide_viewport=False
  for mod in list(o.modifiers):
   if mod.type=='NODES':o.modifiers.remove(mod)
 return result

def text(body,loc,size,mat,parent):
 d=bpy.data.curves.new('R6 | impressão da caixa','FONT');d.body=body;d.align_x='CENTER';d.align_y='CENTER';d.size=size;d.extrude=.0004
 o=bpy.data.objects.new('R6 | '+body,d);o['R6Text']=True;bpy.context.scene.collection.objects.link(o);o.parent=parent;o.location=loc;o.rotation_euler=(math.pi/2,0,0);d.materials.append(mat);return o

def gamecase(title,num,loc,front,paper):
 parent=H.empty('R6 | caixa '+title,loc);box(title+' caixa',(0,0,.095),(.14,.024,.19),front,parent);box(title+' lombada',(-.067,-.013,.095),(.008,.003,.185),paper,parent)
 text(title,(0,-.014,.154),.020,paper,parent)
 if num:text(num,(0,-.014,.075),.082,paper,parent)
 return parent

for plan in plans:
 if selected and plan['episode']not in selected and plan.get('id')not in selected and plan['kind']not in selected:continue
 bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene;H.C.s=s;s.frame_set(1);bpy.context.view_layer.update();actor=bpy.data.objects['DERY | animated character'];rig=actor.parent;cam=bpy.data.objects[s['Production | camera']];cam.animation_data_clear();cam.data.animation_data_clear();s.camera=cam
 for obj in list(s.objects):
  if obj.animation_data:obj.animation_data_clear()
 if plan['kind']not in['recuo','sem_graca','surto']:
  for obj in [*rig.children_recursive,rig]:
   if obj.name in bpy.data.objects:bpy.data.objects.remove(obj,do_unlink=True)
 if s.sequence_editor:s.sequence_editor_clear()
 s.frame_start=1;s.frame_end=plan['count'];s.render.fps=30;s.render.resolution_x=768;s.render.resolution_y=432;s.render.resolution_percentage=100;s.render.use_sequencer=False;s.render.use_compositing=False
 s.render.engine='CYCLES';s.cycles.samples=1;s.cycles.use_denoising=False;s.render.use_persistent_data=True;s.render.threads_mode='FIXED';s.render.threads=2;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.compression=10
 screen=bpy.data.objects['Tela do PC | substituir por vídeo'];placeholder=bpy.data.images.new('R6 | monitor, mídia composta depois',width=1,height=1);placeholder.generated_color=(.018,.018,.022,1)
 for n in screen.data.materials[0].node_tree.nodes:
  if n.type=='TEX_IMAGE':n.image=placeholder
 black=H.material('R6 | borracha',(.015,.019,.025),lit=True);metal=H.material('R6 | metal fosco',(.55,.56,.61),lit=True);white=H.material('R6 | marfim',(.86,.81,.66),lit=True);red=H.material('R6 | vermelho',(.65,.025,.018),lit=True);blue=H.material('R6 | azul',(.055,.14,.28),lit=True);brown=H.material('R6 | plástico marrom',(.23,.075,.025),lit=True)
 light_data=bpy.data.lights.new('R6 | luz próxima','AREA');light_data.energy=55;light_data.shape='DISK';light_data.size=1.4;light=bpy.data.objects.new(light_data.name,light_data);s.collection.objects.link(light);light.location=(-.7,-.2,2.2)
 kind=plan['kind'];moving=[];original=set(o.name for o in s.objects)
 if kind=='cafe':
  target=Vector((-.588,.458,.838));camera_at(cam,(-.59,-.39,1.14),target,66)
  dark=H.material('R6 | censura',(.002,.002,.002),lit=False)
  censor=box('censura só no café',target+(cam.location-target).normalized()*.085,(.158,.072,.003),dark);censor.rotation_euler=cam.rotation_euler;censor.rotation_euler.rotate_axis('X',0);moving.append(censor)
  H.cylinder('R6 | café',(-.588,.458,.884),.034,.002,brown,vertices=16)
  for f in range(1,plan['count']+1):
   u=(f-1)/(plan['count']-1);v=smooth((u-.24)/.20);censor.scale=(max(.001,v),1,1);key(censor,f)
 elif kind=='rodas':
  camera_at(cam,(-.70,-1.16,1.32),(-.70,.25,.845),52)
  source=R/'shorts/009-jogos-que-a-internet-tentou-cancelar/production/02-bmx-xxx/output/Dery_BMX_XXX.blend';parts=append_parts(source,lambda n:n.startswith(('BMX | wheel','BMX | tire','BMX | spoke','BMX | hub')));wheels=sorted([o for o in parts if o.type=='EMPTY'],key=lambda o:o.name)
  assert len(wheels)==2
  for sign,o in zip([-1,1],wheels):
   o.scale=(.45,)*3
   for f in range(1,plan['count']+1):
    u=(f-1)/(plan['count']-1);distance=.20*smooth((u-.18)/.75);o.location=(-.70+sign*(.075+distance),.25,.782+.151*.45);o.rotation_euler=(0,-sign*distance/(.151*.45),0);key(o,f)
  moving=wheels
 elif kind=='juiz':
  camera_at(cam,(-.69,-.65,1.72),(-.69,.26,.815),56)
  source=R/'shorts/009-jogos-que-a-internet-tentou-cancelar/production/03-bully/output/Dery_Bully.blend';parts=append_parts(source,lambda n:n.startswith(('Bully | mallet','Bully | gamepad reveal','Bully | pad','Bully | dpad'))and 'base'not in n);gavel=next(o for o in parts if o.name.startswith('Bully | mallet')and o.type=='EMPTY');pad=next(o for o in parts if o.name.startswith('Bully | gamepad reveal'))
  pad.scale=(.58,)*3;gavel.scale=(.68,)*3;pad.rotation_euler=(0,0,0)
  def ground(parent):
   bpy.context.view_layer.update();z=min((o.matrix_world@Vector(c)).z for o in parent.children_recursive if o.type=='MESH'for c in o.bound_box);parent.location.z+=.782-z
  for f in range(1,plan['count']+1):
   s.frame_set(f);u=(f-1)/(plan['count']-1);p=smooth((u-.08)/.77);push=max(0,(p-.69)/.31)*.100;pad.location=(-1.020+.320*p,.235,0);gavel.location=(-.690+push,.235,0);gavel.rotation_euler=(1.26,0,math.pi/2+.08*smooth((u-.69)/.28));ground(pad);ground(gavel);key(pad,f);key(gavel,f)
  moving=[pad,gavel]
 elif kind=='sequencia':
  camera_at(cam,(-.67,-1.25,1.28),(-.67,.27,.885),50)
  first=gamecase('L4D','1',(-.75,.26,.782),black,white);second=gamecase('L4D','2',(-.52,.26,.782),red,white)
  for f in range(1,plan['count']+1):
   u=(f-1)/(plan['count']-1);first.location=(-.75-.065*smooth((u-.50)/.35),.26,.782+.035*(1-smooth(u/.24)));first.rotation_euler=(0,0,-.08*smooth((u-.50)/.35));second.location=(-.35-.23*smooth((u-.24)/.38),.26,.782+.12*(1-smooth((u-.24)/.38)));second.rotation_euler=(0,0,.05*(1-smooth((u-.58)/.25)));key(first,f);key(second,f)
  moving=[first,second]
 elif kind=='recuo':
  # Move character and its original support together; the hands retain thigh contact.
  chair=bpy.data.objects['Cadeira do Dery'];group=H.empty('R6 | recuo da cadeira original');saved=rig.matrix_world.copy();rig.parent=group;rig.matrix_world=saved;saved=chair.matrix_world.copy();chair.parent=group;chair.matrix_world=saved
  # Tight reaction keeps the existing seated staging; no additional furniture.
  head=rig.matrix_world@rig.pose.bones['head'].head;target=head+Vector((0,0,-.26));old=cam.matrix_world.copy();forward=cam.matrix_world.to_quaternion()@Vector((0,0,-1));cam.location+=forward*.34;cam.data.lens=52
  keys=[];families=json.loads((R/'assets/personagens/dery/expressions_ps1/v3/fala_familias.json').read_text())
  voice_file=R/'shorts/009-jogos-que-a-internet-tentou-cancelar/production/04-saints-row-iv/assets/voz/voz_timeline.wav'
  with wave.open(str(voice_file))as w:rate=w.getframerate();voice=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(float)/32768
  code=(P.parent/'01-gta-san-andreas/revise_animation.py').read_text();exec(code[code.index('def mouth_at(t):'):code.index('face_metrics={}')])
  for f in range(1,plan['count']+1):
   u=(f-1)/(plan['count']-1);v=smooth((u-.08)/.18)*(1-smooth((u-.60)/.37));group.location=(.14*v,-.025*v,0);key(group,f);t=(plan['start']+f-2)/30;value=106 if .22<u<.44 else families['irritada'if u>.44 else'neutra'][mouth_at(math.floor(t*15)/15)];actor['PS1_face_id']=value;actor.keyframe_insert('["PS1_face_id"]',frame=f);keys.append((f,value))
  bake_faces(actor,keys);moving=[group]
 elif kind=='tecla':
  camera_at(cam,(-1.045,-.48,1.29),(-1.045,.29,.85),66)
  button=H.empty('R6 | tecla personalizada',(-1.055,.294,.814));box('base da tecla',(0,0,.015),(.062,.060,.027),black,button)
  for i,(r,z)in enumerate([(.025,.043),(.019,.060),(.011,.074)]):sphere('cocô plástico '+str(i),(0,0,z),(r,r*.85,.013),brown,button)
  for f in range(1,plan['count']+1):
   u=(f-1)/(plan['count']-1);v=smooth((u-.22)/.12)*(1-smooth((u-.55)/.24));button.location.z=.814-.012*v;button.rotation_euler.z=.055*math.sin(u*math.pi*2)*v;key(button,f)
  moving=[button]
 elif kind=='pokebola':
  preset=bpy.data.objects['TESTE | jogo no CRT'];cam.matrix_world=preset.matrix_world.copy();cam.data.lens=preset.data.lens
  ball=H.empty('R6 | Pokébola que não atravessa o monitor');radius=.055
  # UV sphere split into solid red and white hemispheres, with a black equator.
  mesh=sphere('Pokébola', (0,0,0),(radius,)*3,white,ball);mesh.data.materials.append(red)
  for polygon in mesh.data.polygons:polygon.material_index=1 if polygon.center.z>0 else 0
  H.torus('R6 | faixa preta',(0,0,0),radius,.005,black,ball,segments=16)
  H.cylinder('R6 | botão',(0,-radius,0),.014,.009,black,ball,vertices=12,rot=(math.pi/2,0,0));H.cylinder('R6 | miolo',(0,-radius-.006,0),.008,.009,white,ball,vertices=10,rot=(math.pi/2,0,0))
  start=Vector((-1.11,-.01,.98));hit=Vector((-1.23,.54289-radius-.004,1.08));end=Vector((-.96,-.13,.85))
  for f in range(1,plan['count']+1):
   u=(f-1)/(plan['count']-1)
   if u<.46:v=u/.46;ball.location=start.lerp(hit,v)+Vector((0,0,.06*math.sin(math.pi*v)))
   else:v=(u-.46)/.54;ball.location=hit.lerp(end,v)+Vector((0,0,.08*math.sin(math.pi*v)))
   ball.rotation_euler=(u*4.5,0,-u*1.5);key(ball,f)
  moving=[ball]
 elif kind=='vampiro':
  camera_at(cam,(-.65,-1.12,1.30),(-.65,.29,.89),54)
  case=gamecase('NIGHT\nTRAP','',(-.72,.29,.782),blue,white)
  # A deliberately toy-like vampire case: two simple eyes and triangular fangs.
  for x in[-.030,.030]:sphere('olho vampiro',(x,-.020,.103),(.013,.006,.010),white,case);sphere('pupila',(x,-.026,.103),(.005,.003,.006),black,case)
  for x in[-.020,.020]:
   H.mesh('R6 | presa',[(x-.007,-.018,.077),(x+.007,-.018,.077),(x,-.018,.047)],[(0,1,2)],white,case)
  garlic=H.empty('R6 | alho',(-.48,.29,.782))
  for i in range(6):
   a=i*math.tau/6;sphere('dente de alho',(math.cos(a)*.016,math.sin(a)*.016,.025),(.020,.014,.026),white,garlic)
  H.cylinder('R6 | talinho',(0,0,.062),.006,.035,white,garlic,vertices=6)
  for f in range(1,plan['count']+1):
   u=(f-1)/(plan['count']-1);v=smooth((u-.16)/.40);fear=smooth((u-.48)/.32);garlic.location.x=-.40-.18*v;case.location.x=-.72-.08*fear;case.rotation_euler.z=-.11*fear;key(garlic,f);key(case,f)
  moving=[garlic,case]
 elif kind in['arquivos_cafe','estrelas_cafe','bike_x','disco_grade','amor_sequencia','sem_graca','peticao','viagem','surto']:
  exec((P/'cenas_adicionais.py').read_text())
 else:raise ValueError(kind)
 # Place small tabletop props on real support, away from the desk's front lip.
 def translate_root(obj,delta):
  obj.location+=Vector(delta)
  if obj.animation_data and obj.animation_data.action:
   for fc in obj.animation_data.action.fcurves:
    if fc.data_path=='location':
     for point in fc.keyframe_points:point.co.y+=delta[fc.array_index]
 roots=[o for o in s.objects if o.name not in original and o.type not in['CAMERA','LIGHT']and(o.parent is None or o.parent.name in original)]
 if kind in['rodas','juiz','sequencia','vampiro']:
  for o in roots:translate_root(o,(-.20,.20,0))
  cam.location+=Vector((-.20,.20,0))
 probes={'rodas':(-.90,.45),'juiz':(-.89,.435),'sequencia':(-.87,.46),'vampiro':(-.85,.49),'arquivos_cafe':(-.68,.70),'estrelas_cafe':(-.588,.458),'cafe':(-.588,.458),'bike_x':(-.69,.70),'disco_grade':(-.69,.68),'amor_sequencia':(-.67,.70),'peticao':(-.70,.50),'viagem':(-.65,.70)}
 if kind in probes:
  from mathutils.bvhtree import BVHTree
  bpy.context.view_layer.update();evaluated=bpy.data.objects['Mesa principal | madeira gasta'].evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
  try:tree=BVHTree.FromPolygons([evaluated.matrix_world@v.co for v in mesh.vertices],[tuple(p.vertices)for p in mesh.polygons]);hit=tree.ray_cast(Vector((*probes[kind],1.2)),Vector((0,0,-1)),1)
  finally:evaluated.to_mesh_clear()
  assert hit[0] is not None,('No real tabletop',kind,probes[kind]);baseline=.782
  if kind in['cafe','estrelas_cafe']:
   cup=bpy.data.objects['Caneca na mesa'];baseline=min((cup.matrix_world@Vector(c)).z for c in cup.bound_box)
  dz=hit[0].z+.001-baseline
  for o in roots:translate_root(o,(0,0,dz))
  cam.location.z+=dz
  if kind in['cafe','estrelas_cafe']:bpy.data.objects['Caneca na mesa'].location.z+=dz
  else:bpy.data.objects['Caneca na mesa'].hide_render=True
  s['R6 | actual tabletop']=[*probes[kind],hit[0].z];s['R6 | tabletop correction']=dz
 # Existing room, character and materials remain intact on disk. Rebind only the copy.
 for group in bpy.data.node_groups:
  for node in group.nodes:
   if node.bl_idname=='GeometryNodeObjectInfo'and 'Object'in node.inputs:
    obj=node.inputs['Object'].default_value
    if obj and obj.type=='CAMERA':node.inputs['Object'].default_value=cam
 projection=bpy.data.node_groups['PSX | snapped vertices + affine UVs']
 for obj in list(s.objects):
  if obj.name not in original and obj.type=='FONT':
   bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.ops.object.convert(target='MESH')
 for obj in s.objects:
  if obj.name not in original and obj.type=='MESH':
   if not obj.data.uv_layers:H.uv_faces(obj)
   attr=obj.data.attributes.get('PS1SnapWeight')or obj.data.attributes.new(name='PS1SnapWeight',type='FLOAT',domain='POINT')
   for value in attr.data:value.value=.12 if obj.get('R6Text')else .8
   mod=obj.modifiers.new('PSX | cena curta','NODES');mod.node_group=projection
   for mat in obj.data.materials:affine_material(mat,'UVMap',1)
 # Bake a tiny directional palette into new props, as on the library furniture.
 # One-sample beauty rendering then has no noisy new PBR surfaces.
 base_colors={}
 for mat in bpy.data.materials:
  if mat.name.startswith('R6 |')and mat.use_nodes:
   rgb=next((n for n in mat.node_tree.nodes if n.type=='RGB'),None)
   if rgb:base_colors[mat.name]=tuple(rgb.outputs[0].default_value)
 direction=Vector((-.4,-.7,1)).normalized()
 for obj in s.objects:
  if obj.type!='MESH'or not any(m and m.name in base_colors for m in obj.data.materials):continue
  attr=obj.data.color_attributes.get('R6Color')or obj.data.color_attributes.new(name='R6Color',type='FLOAT_COLOR',domain='CORNER')
  for polygon in obj.data.polygons:
   mat=obj.data.materials[polygon.material_index]
   if not mat or mat.name not in base_colors:continue
   normal=(obj.matrix_world.to_3x3().inverted().transposed()@polygon.normal).normalized();shade=.56+.34*max(0,normal.dot(direction))+.10*max(0,normal.z);color=base_colors[mat.name]
   for li in polygon.loop_indices:attr.data[li].color=tuple(c*shade for c in color[:3])+(1,)
 for name in base_colors:
  mat=bpy.data.materials[name];nt=mat.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');em=nt.nodes.new('ShaderNodeEmission');attr=nt.nodes.new('ShaderNodeVertexColor');attr.layer_name='R6Color';nt.links.new(attr.outputs['Color'],em.inputs['Color']);nt.links.new(em.outputs[0],out.inputs['Surface'])
 for action in bpy.data.actions:
  for fc in action.fcurves:
   for point in fc.keyframe_points:point.interpolation='CONSTANT'if 'face'in fc.data_path else'LINEAR'
 s.frame_set(1);bpy.context.view_layer.update();s['R6 | action']=plan['action'];s['R6 | source episode']=plan['episode'];s['R6 | standing Dery']=False
 bpy.ops.outliner.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();bpy.ops.file.make_paths_relative();out=R/plan['output'];dest=R/plan.get('model',str((out/(plan['slug']+'_R6_Cena_Curta.blend')).relative_to(R)));bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
 cache=Path(plan['cache']);(cache/'frames').mkdir(exist_ok=True)
 for f in sorted({1,round(plan['count']*.48),plan['count']}):s.frame_set(f);s.render.filepath=str(cache/'frames'/f'frame_{f:04d}.png');bpy.ops.render.render(write_still=True)
 print('R6_PREVIEW_READY',plan['episode'],flush=True)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_sha
