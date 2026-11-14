"""Two brief, narration-led tabletop actions. Executed by build_short in Blender."""
sys.path.insert(0,str(R/'shorts/003-teste-quarto-gamer/production'))
import helpers as H
from psx_render import affine_material
from mathutils.bvhtree import BVHTree
H.C.s=s
original=set(o.name for o in s.objects)
cam_original=host_mat.copy()
# Measure the actual desk instead of trusting nominal asset units.
desk=bpy.data.objects['Mesa principal | madeira gasta'];evaluated=desk.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
try:
 tree=BVHTree.FromPolygons([evaluated.matrix_world@v.co for v in mesh.vertices],[list(p.vertices)for p in mesh.polygons]);hit=tree.ray_cast(Vector((-.68,.70,2)),Vector((0,0,-1)));assert hit[0]is not None;desk_z=hit[0].z
finally:evaluated.to_mesh_clear()
print('DOAX3_TABLE_TOP',desk_z,flush=True)
def material(name,color):return H.material('DOAX3 | '+name,color,lit=False)
gold=material('mala amarela',(.68,.39,.05));black=material('borracha',(.025,.025,.035));white=material('bola branca',(.88,.86,.76));blue=material('bola azul',(.035,.29,.63));yellow=material('bola amarela',(.91,.66,.03));metal=material('mola',(.36,.39,.44))
def box(name,loc,size,mat,parent=None):return H.box('DOAX3 | '+name,loc,size,mat,parent)
def key(obj,f):
 for path in ['location','rotation_euler','scale']:obj.keyframe_insert(path,frame=f)
def visible(objects,start,end):
 for obj in objects:
  for frame,value in [(1,True),(start,False),(end+1,True)]:obj.hide_render=value;obj.keyframe_insert('hide_render',frame=frame)
  for fc in obj.animation_data.action.fcurves:
   if fc.data_path=='hide_render':
    for point in fc.keyframe_points:point.interpolation='CONSTANT'
def camera(pos,target,lens):
 cam.location=pos;cam.rotation_mode='QUATERNION';cam.rotation_quaternion=(Vector(target)-cam.location).to_track_quat('-Z','Y');cam.data.lens=lens
# Reuse the luggage geometry/material already made for the Pokémon insert.
source=P.parent/'07-pokemon-sword-shield/output/R6_Cenas_Curtas/Pokemon_Sword_Shield_R6_02_Cena_Curta.blend'
with bpy.data.libraries.load(str(source),link=False)as(a,b):
 selected=[n for n in a.objects if n.startswith('R6 | mala')];b.objects=selected
imported=[o for o in b.objects if o]
body_source=next(o for o in imported if o.type=='MESH')
for obj in imported:
 obj.animation_data_clear()
 for mod in list(obj.modifiers):obj.modifiers.remove(mod)
# Separate mesh copies allow body/lid to reuse the existing suitcase's shape.
start=next(sh['start']for sh in info['shots']if sh['mood']=='mala');end=next(sh['end']for sh in info['shots']if sh['mood']=='mala');new_before=set(s.objects)
body=bpy.data.objects.new('DOAX3 | mala corpo reutilizado',body_source.data.copy());s.collection.objects.link(body);body.parent=None;body.location=(-.68,.70,desk_z+.019);body.scale=(.18/.064,.14/.052,.038/.078)
# Replace the old per-corner colour by the corresponding warm yellow; no noisy PBR.
body.data.materials.clear();body.data.materials.append(gold)
lid=H.empty('DOAX3 | dobradiça',(-.68,.77,desk_z+.038));box('tampa da mala',(0,-.07,.005),(.18,.14,.010),gold,lid)
box('alça da mala',(-.68,.624,desk_z+.023),(.048,.012,.012),black)
umbrella=H.empty('DOAX3 | guarda-sol',(-.68,.70,desk_z+.040));H.cylinder('DOAX3 | haste',(0,0,.095),.003,.19,white,umbrella,vertices=8)
verts=[(0,0,.221)]+[(.095*math.cos(i*math.tau/10),.095*math.sin(i*math.tau/10),.184)for i in range(10)];faces=[(0,1+i,1+(i+1)%10)for i in range(10)];canopy=H.mesh('DOAX3 | cobertura',verts,faces,yellow,umbrella);canopy.data.materials.append(blue)
for polygon in canopy.data.polygons:polygon.material_index=polygon.index%2
for f in range(start,end+1):
 u=(f-start)/(end-start);opening=smooth((u-.08)/.32);popup=smooth((u-.33)/.29);lid.rotation_euler.x=-1.70*opening;key(lid,f);umbrella.scale=(max(.01,popup),max(.01,popup),.02+.98*popup);umbrella.rotation_euler.z=.14*popup;key(umbrella,f)
visible([o for o in s.objects if o not in new_before],start,end)
for f in [start,end]:
 camera((-.68,-.43,1.40),(-.68,.70,desk_z+.11),60)
 for path in ['location','rotation_quaternion']:cam.keyframe_insert(path,frame=f)
 cam.data.keyframe_insert('lens',frame=f)
renderframes.extend(range(start,end+1))
# A toy volleyball on an actual visible spring: exaggeration belongs to the object.
start=next(sh['start']for sh in info['shots']if sh['mood']=='mola');end=next(sh['end']for sh in info['shots']if sh['mood']=='mola');new_before=set(s.objects)
H.cylinder('DOAX3 | base da mola',(-.68,.70,desk_z+.006),.063,.012,black,vertices=12)
spring=H.empty('DOAX3 | mola física',(-.68,.70,desk_z+.012));segments=72;tube=6;verts=[]
for i in range(segments+1):
 angle=i/segments*math.tau*5;center=Vector((.031*math.cos(angle),.031*math.sin(angle),.128*i/segments))
 for j in range(tube):
  theta=j/tube*math.tau;verts.append(tuple(center+Vector((math.cos(angle)*math.cos(theta)*.0025,math.sin(angle)*math.cos(theta)*.0025,math.sin(theta)*.0025))))
faces=[(i*tube+j,i*tube+(j+1)%tube,(i+1)*tube+(j+1)%tube,(i+1)*tube+j)for i in range(segments)for j in range(tube)]
H.mesh('DOAX3 | arame helicoidal',verts,faces,metal,spring)
ball=H.sphere('DOAX3 | bola de vôlei',(-.68,.70,desk_z+.190),(.050,)*3,white,segments=12,rings=8);ball.data.materials.append(blue);ball.data.materials.append(yellow)
for polygon in ball.data.polygons:polygon.material_index=(polygon.index%12//2)%3
for f in range(start,end+1):
 u=(f-start)/(end-start);press=smooth((u-.08)/.29);release=smooth((u-.41)/.13);extension=1-.64*press+.64*release+.16*math.sin(max(0,u-.55)*math.tau*3)*math.exp(-max(0,u-.55)*8);spring.scale.z=extension;key(spring,f)
 if u<.54:ball.location=(-.68,.70,desk_z+.012+.128*extension+.050)
 else:
  flight=(u-.54)/.46;ball.location=(-.68+.045*flight,.70,desk_z+.190+.68*flight-.12*flight*flight);ball.rotation_euler.y=flight*5.5
 key(ball,f)
visible([o for o in s.objects if o not in new_before],start,end)
for f in [start,end]:
 camera((-.68,-.43,1.40),(-.68,.70,desk_z+.13),60)
 for path in ['location','rotation_quaternion']:cam.keyframe_insert(path,frame=f)
 cam.data.keyframe_insert('lens',frame=f)
renderframes.extend(range(start,end+1));renderframes.sort()
# New meshes use a baked directional palette plus the existing screen-space snap.
projection=bpy.data.node_groups['PSX | snapped vertices + affine UVs'];direction=Vector((-.4,-.7,1)).normalized();colors={m.name:tuple(next(n for n in m.node_tree.nodes if n.type=='RGB').outputs[0].default_value)for m in [gold,black,white,blue,yellow,metal]}
for obj in s.objects:
 if obj.name in original or obj.type!='MESH':continue
 if not obj.data.uv_layers:H.uv_faces(obj)
 attr=obj.data.attributes.get('PS1SnapWeight')or obj.data.attributes.new(name='PS1SnapWeight',type='FLOAT',domain='POINT')
 for point in attr.data:point.value=.8
 modifier=obj.modifiers.new('PSX | objeto de mesa','NODES');modifier.node_group=projection
 attr=obj.data.color_attributes.get('DOAX3Color')or obj.data.color_attributes.new(name='DOAX3Color',type='FLOAT_COLOR',domain='CORNER')
 for polygon in obj.data.polygons:
  mat=obj.data.materials[polygon.material_index]
  if mat.name not in colors:continue
  normal=(obj.matrix_world.to_3x3().inverted().transposed()@polygon.normal).normalized();shade=.56+.34*max(0,normal.dot(direction))+.10*max(0,normal.z)
  for li in polygon.loop_indices:attr.data[li].color=tuple(c*shade for c in colors[mat.name][:3])+(1,)
for name in colors:
 nt=bpy.data.materials[name].node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');em=nt.nodes.new('ShaderNodeEmission');attr=nt.nodes.new('ShaderNodeVertexColor');attr.layer_name='DOAX3Color';nt.links.new(attr.outputs['Color'],em.inputs['Color']);nt.links.new(em.outputs[0],out.inputs['Surface'])
for owner in [cam,cam.data]:
 for fc in owner.animation_data.action.fcurves:
  for point in fc.keyframe_points:point.interpolation='CONSTANT'
for obj in s.objects:
 if obj.name in original or not obj.animation_data or not obj.animation_data.action:continue
 for fc in obj.animation_data.action.fcurves:
  for point in fc.keyframe_points:point.interpolation='CONSTANT'if fc.data_path=='hide_render'else'LINEAR'
s['Production | tabletop z']=desk_z;s['Production | gag count']=2
