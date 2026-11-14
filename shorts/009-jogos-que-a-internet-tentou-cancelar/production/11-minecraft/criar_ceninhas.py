"""Brief tabletop metaphors specific to these two recorded commentaries."""
sys.path.insert(0,str(R/'shorts/003-teste-quarto-gamer/production'))
import helpers as H
from psx_render import affine_material
from mathutils.bvhtree import BVHTree
H.C.s=s
original=set(o.name for o in s.objects);palette={}
def mat(name,rgb):
 m=H.material('LOTE | '+name,rgb,lit=False);palette[m.name]=(*rgb,1);return m
black=mat('preto',(.018,.022,.029));white=mat('papel',(.88,.86,.77));red=mat('TNT',(.67,.045,.025));green=mat('grama',(.13,.40,.06));brown=mat('terra',(.28,.13,.055));wood=mat('madeira',(.40,.26,.10));grey=mat('ferro',(.32,.36,.40));pink=mat('festa',(.65,.055,.49));yellow=mat('patch',(.85,.55,.025))
def box(name,loc,size,m,parent=None):return H.box('LOTE | '+name,loc,size,m,parent)
def text(body,loc,size,m,parent=None):
 data=bpy.data.curves.new('LOTE | inscrição','FONT');data.body=body;data.align_x='CENTER';data.align_y='CENTER';data.size=size;obj=bpy.data.objects.new('LOTE | '+body,data);s.collection.objects.link(obj);obj.parent=parent;obj.location=loc;obj.rotation_euler=(math.pi/2,0,0);data.materials.append(m);return obj
def key(obj,f):
 for path in ['location','rotation_euler','scale']:obj.keyframe_insert(path,frame=f)
def case(loc):
 root=H.empty('LOTE | caixa House Party',loc);box('capa',(0,0,.090),(.130,.024,.180),pink,root);box('lombada',(-.059,-.001,.09),(.012,.028,.18),black,root);text('HOUSE\nPARTY',(.003,-.013,.11),.026,white,root);return root
def visibility(objects,a,b):
 for obj in objects:
  for frame,value in [(1,True),(a,False),(b+1,True)]:obj.hide_render=value;obj.keyframe_insert('hide_render',frame=frame)
# Probe the real desk so every small vignette has visible, measured support.
desk=bpy.data.objects['Mesa principal | madeira gasta'];bpy.context.view_layer.update();evaluated=desk.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
try:
 tree=BVHTree.FromPolygons([evaluated.matrix_world@v.co for v in mesh.vertices],[list(p.vertices)for p in mesh.polygons]);hit=tree.ray_cast(Vector((-.68,.70,1.5)),Vector((0,0,-1)));assert hit[0]is not None;Z=hit[0].z+.001
finally:evaluated.to_mesh_clear()
for shot in info['shots']:
 if shot['kind']!='gag':continue
 kind=shot['mood'];a,b=shot['start'],shot['end'];before=set(s.objects);center=Vector((-.68,.70,Z))
 if kind=='tnt':
  root=H.empty('LOTE | TNT inteira',center);box('TNT miolo',(0,0,.071),(.142,.142,.142),red,root);box('faixa branca',(0,-.0715,.071),(.142,.002,.045),white,root);text('TNT',(0,-.073,.071),.032,black,root);H.cylinder('LOTE | pavio',(0,0,.155),.004,.03,black,root,vertices=6)
  pieces=[]
  for ix in[-1,1]:
   for iy in[-1,1]:
    for iz in[-1,1]:
     o=box('cubo da explosão',center+Vector((ix*.038,iy*.038,.071+iz*.038)),(.068,)*3,red if iz>0 else brown);pieces.append((o,Vector((ix*.038,iy*.038,.071+iz*.038)),Vector((ix*.16,iy*.08,.24 if iz>0 else .13))))
  for f in range(a,b+1):
   u=(f-a)/(b-a);expand=smooth((u-.29)/.13);root.scale=(max(.001,1+.10*expand-1.10*smooth((u-.41)/.04)),)*3;key(root,f);v=max(0,(u-.43)/.57)
   for o,start,delta in pieces:
    o.scale=(max(.001,smooth((u-.43)/.035)),)*3;pos=start+delta*v;pos.z=max(.034,pos.z-.16*v*v);o.location=center+pos;o.rotation_euler=(v*1.2,v*.9,v*.7);key(o,f)
 elif kind=='privado':
  house=H.empty('LOTE | servidor privado',center);box('bloco de terra',(0,0,.012),(.245,.190,.024),brown,house);box('bloco de grama',(0,0,.030),(.245,.190,.012),green,house);box('servidor casa',(0,0,.095),(.15,.13,.12),wood,house);box('telhado',(0,0,.161),(.18,.15,.022),brown,house);box('porta privada',(0,-.068,.09),(.061,.008,.10),black,house);text('PRIVADO',(0,-.074,.148),.018,white,house);box('cadeado',(0,-.078,.089),(.028,.015,.025),yellow,house);H.torus('LOTE | arco cadeado',(0,-.079,.108),.011,.003,grey,house,rot=(math.pi/2,0,0),segments=10)
  hammer=H.empty('LOTE | martelo de punição',center+Vector((-.05,0,.39)));H.beam('LOTE | cabo',(.035,0,.10),(-.035,0,.29),.014,wood,hammer);box('cabeça do martelo',(.035,0,.09),(.095,.045,.048),grey,hammer)
  for f in range(a,b+1):
   u=(f-a)/(b-a);strike=smooth((u-.13)/.38);recover=smooth((u-.65)/.30);hammer.rotation_euler.y=-.60+1.06*strike-.10*recover;hammer.location.z=Z+.39-.240*strike+.025*recover;key(hammer,f)
 elif kind=='retirada':
  box('base da lojinha',center+Vector((0,0,.007)),(.24,.19,.014),grey)
  for x in[-.113,.113]:box('parede da lojinha',center+Vector((x,.035,.125)),(.014,.18,.24),grey)
  box('teto da lojinha',center+Vector((0,.035,.247)),(.24,.18,.012),grey);text('LOJA',center+Vector((0,-.059,.254)),.028,white)
  game=case(center+Vector((0,-.025,.014)));shutter=box('persiana',center+Vector((0,-.061,.236)),(.210,.014,.218),black)
  for f in range(a,b+1):
   u=(f-a)/(b-a);slide=smooth((u-.08)/.35);closing=smooth((u-.41)/.48);game.location.y=.675+.085*slide;key(game,f);shutter.scale.z=max(.001,closing);shutter.location.z=Z+.236-.109*closing;key(shutter,f)
 elif kind in['censura','restaurar']:
  game=case(center);bar=box('tarja obrigatória',center+Vector((0,-.017,.095)),(.157,.008,.048),black)
  if kind=='restaurar':
   patch=H.empty('LOTE | adesivo PATCH',center+Vector((.21,-.025,.045)));box('adesivo',(0,0,0),(.069,.003,.035),yellow,patch);text('PATCH',(0,-.002,0),.013,black,patch)
  for f in range(a,b+1):
   u=(f-a)/(b-a)
   if kind=='censura':bar.location.z=Z+.29-.195*smooth((u-.13)/.39)
   else:
    v=smooth((u-.13)/.40);patch.location.x=-.47-.21*v;key(patch,f);drop=smooth((u-.55)/.38);bar.location=Vector((-.68+.13*drop,.683-.05*drop,Z+.095-.087*drop));bar.rotation_euler.x=-math.pi/2*drop
   key(bar,f)
 else:raise ValueError(kind)
 visibility([o for o in s.objects if o not in before],a,b)
 for f in [a,b]:
  cam.location=(-.68,-.44,1.40);cam.rotation_mode='QUATERNION';cam.rotation_quaternion=(Vector((-.68,.70,Z+.12))-cam.location).to_track_quat('-Z','Y');cam.data.lens=58
  for prop in ['location','rotation_quaternion']:cam.keyframe_insert(prop,frame=f)
  cam.data.keyframe_insert('lens',frame=f)
 renderframes.extend(range(a,b+1))
# Hide only the foreground mug during toy inserts; it otherwise stays as supplied.
cup=bpy.data.objects['Caneca na mesa']
for f,value in [(1,False)]+[(f,v)for sh in info['shots']if sh['kind']=='gag'for f,v in [(sh['start'],True),(sh['end']+1,False)]]:cup.hide_render=value;cup.keyframe_insert('hide_render',frame=f)
for obj in list(s.objects):
 if obj.name not in original and obj.type=='FONT':
  bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.ops.object.convert(target='MESH')
projection=bpy.data.node_groups['PSX | snapped vertices + affine UVs'];direction=Vector((-.4,-.7,1)).normalized();bpy.context.view_layer.update()
for obj in s.objects:
 if obj.name in original or obj.type!='MESH':continue
 if not obj.data.uv_layers:H.uv_faces(obj)
 attr=obj.data.attributes.get('PS1SnapWeight')or obj.data.attributes.new(name='PS1SnapWeight',type='FLOAT',domain='POINT')
 for point in attr.data:point.value=.65
 modifier=obj.modifiers.new('PSX | ceninha específica','NODES');modifier.node_group=projection
 attr=obj.data.color_attributes.get('LoteColor')or obj.data.color_attributes.new(name='LoteColor',type='FLOAT_COLOR',domain='CORNER')
 for polygon in obj.data.polygons:
  material=obj.data.materials[polygon.material_index]
  if material.name not in palette:continue
  normal=(obj.matrix_world.to_3x3().inverted().transposed()@polygon.normal).normalized();shade=.60+.30*max(0,normal.dot(direction))+.10*max(0,normal.z)
  for li in polygon.loop_indices:attr.data[li].color=tuple(c*shade for c in palette[material.name][:3])+(1,)
for name in palette:
 nt=bpy.data.materials[name].node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');em=nt.nodes.new('ShaderNodeEmission');attr=nt.nodes.new('ShaderNodeVertexColor');attr.layer_name='LoteColor';nt.links.new(attr.outputs['Color'],em.inputs['Color']);nt.links.new(em.outputs[0],out.inputs['Surface'])
for owner in [cam,cam.data,cup]:
 if owner.animation_data and owner.animation_data.action:
  for fc in owner.animation_data.action.fcurves:
   for point in fc.keyframe_points:point.interpolation='CONSTANT'
for obj in s.objects:
 if obj.name in original or not obj.animation_data or not obj.animation_data.action:continue
 for fc in obj.animation_data.action.fcurves:
  for point in fc.keyframe_points:point.interpolation='CONSTANT'if fc.data_path=='hide_render'else'LINEAR'
renderframes.sort();s['Production | tabletop z']=Z;s['Production | gag count']=sum(sh['kind']=='gag'for sh in info['shots'])
