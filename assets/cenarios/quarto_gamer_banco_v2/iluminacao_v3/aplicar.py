"""Rebake the existing PS1 room's light; preserve textures, rig and furniture."""
import bpy,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
LIGHTS=[dict(name='principal suave',pos=(-.65,-1.1,2.15),color=(1.,.86,.72),power=1.85),dict(name='ciano fundo',pos=(-1.05,1.24,1.64),color=(.055,.72,1.),power=3.8),dict(name='violeta fundo',pos=(1.35,1.28,1.78),color=(.67,.10,1.),power=4.3),dict(name='janela azul',pos=(2.35,-.45,1.85),color=(.18,.36,.90),power=1.30),dict(name='monitor ciano',pos=(-1.22,.62,1.13),color=(.10,.67,1.),power=.60),dict(name='luminaria quente',pos=(-.40,1.04,1.13),color=(1.,.48,.16),power=1.05)]
def apply(scene):
 actor=bpy.data.objects.get('DERY | animated character');removed=[]
 for obj in list(scene.objects):
  if obj.name=='Fone de ouvido'or obj.name.startswith('Fone de ouvido |'):
   removed.append(obj.name);bpy.data.objects.remove(obj,do_unlink=True)
 assert removed or scene.get('LightingV3 | removed headphones'),'Expected the previously identified headphones'
 # These are reference lights for viewport/edits; the PSX render is vertex-lit.
 for obj in list(scene.objects):
  if obj.type=='LIGHT':bpy.data.objects.remove(obj,do_unlink=True)
 for light in LIGHTS:
  data=bpy.data.lights.new('Luz V3 | '+light['name'],'POINT');data.color=light['color'];data.energy=light['power']*70;data.shadow_soft_size=.40;obj=bpy.data.objects.new(data.name,data);scene.collection.objects.link(obj);obj.location=light['pos']
 meshes=[o for o in scene.objects if o.type=='MESH'and o!=actor];points=[];triangles=[]
 for obj in meshes:
  obj.data.calc_loop_triangles();offset=len(points);points.extend(obj.matrix_world@v.co for v in obj.data.vertices);triangles.extend(tuple(offset+i for i in t.vertices)for t in obj.data.loop_triangles)
 bvh=BVHTree.FromPolygons(points,triangles,all_triangles=True);cache={};affected=[]
 for obj in meshes:
  attr=obj.data.color_attributes.get('PS1Light')
  if not attr:continue
  affected.append(obj.name);matrix=obj.matrix_world;normal_matrix=matrix.to_3x3().inverted().transposed()
  for face in obj.data.polygons:
   n=(normal_matrix@face.normal).normalized()
   for li in face.loop_indices:
    p=matrix@obj.data.vertices[obj.data.loops[li].vertex_index].co;key=tuple(round(v,5)for v in (*p,*n))
    if key not in cache:
     color=Vector((.065,.070,.105))
     for light in LIGHTS:
      delta=Vector(light['pos'])-p;distance=delta.length;direction=delta.normalized();cosine=max(0,n.dot(direction));hit=bvh.ray_cast(p+n*.004+direction*.003,direction,max(0,distance-.025));visibility=.12 if hit[0]is not None else 1.;weight=light['power']/(1+distance*distance)*(.055+.945*cosine)*visibility;color+=Vector(light['color'])*weight
     cache[key]=tuple(max(.025,min(1.32,v))for v in color)+(1.,)
    attr.data[li].color=cache[key]
 if actor:
  # Evaluate only skinning to keep original corner/vertex indices for baking.
  flags=[(m,m.show_viewport)for m in actor.modifiers]
  for mod,_ in flags:
   if mod.type!='ARMATURE':mod.show_viewport=False
  bpy.context.view_layer.update();evaluated=actor.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh();assert len(mesh.loops)==len(actor.data.loops)
  light_attr=actor.data.color_attributes.get('RoomLightV3')or actor.data.color_attributes.new(name='RoomLightV3',type='FLOAT_COLOR',domain='CORNER');rim_attr=actor.data.color_attributes.get('RoomRimV3')or actor.data.color_attributes.new(name='RoomRimV3',type='FLOAT_COLOR',domain='CORNER');normal_matrix=actor.matrix_world.to_3x3().inverted().transposed()
  for face in mesh.polygons:
   normal=(normal_matrix@face.normal).normalized()
   for li in face.loop_indices:
    p=actor.matrix_world@mesh.vertices[mesh.loops[li].vertex_index].co
    key=max(0,normal.dot((Vector((-.65,-1.1,2.15))-p).normalized()));cyan=max(0,normal.dot((Vector((-1.22,.62,1.32))-p).normalized()));purple=max(0,normal.dot((Vector((1.15,1.35,1.8))-p).normalized()))
    col=Vector((.70,.71,.75))+Vector((1.,.92,.82))*(.39*key)+Vector((.035,.68,1.))*(.32*cyan)+Vector((.77,.10,1.))*(.29*purple)
    light_attr.data[li].color=tuple(col)+(1.,);rim_attr.data[li].color=(.008*purple,.010*cyan,.020*max(purple,cyan),1.)
  evaluated.to_mesh_clear()
  for mod,value in flags:mod.show_viewport=value
  bpy.context.view_layer.update()
  # Keep the full original shading/131-face system; add only a lighting layer.
  for slot,material in enumerate(list(actor.data.materials)):
   if not material or not material.use_nodes or material.get('RoomLightingV3'):continue
   material=material.copy();actor.data.materials[slot]=material;material['RoomLightingV3']=True;nt=material.node_tree;attr=nt.nodes.new('ShaderNodeVertexColor');attr.layer_name='RoomLightV3';attr.name='Luz V3 | cor por vertice';rim=nt.nodes.new('ShaderNodeVertexColor');rim.layer_name='RoomRimV3';rim.name='Luz V3 | recorte da camiseta'
   for emission in[n for n in list(nt.nodes)if n.type=='EMISSION']:
    incoming=emission.inputs['Color'];original=incoming.links[0].from_socket if incoming.is_linked else None;default=tuple(incoming.default_value);mul=nt.nodes.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1.;mul.name='Luz V3 | preservar textura'
    if original:nt.links.new(original,mul.inputs[1])
    else:mul.inputs[1].default_value=default
    nt.links.new(attr.outputs['Color'],mul.inputs[2]);result=mul.outputs[0]
    if slot==2:
     add=nt.nodes.new('ShaderNodeMixRGB');add.blend_type='ADD';add.inputs[0].default_value=1.;nt.links.new(result,add.inputs[1]);nt.links.new(rim.outputs['Color'],add.inputs[2]);result=add.outputs[0]
    nt.links.new(result,incoming)
 scene['LightingV3 | removed headphones']=True;scene['LightingV3 | style']='Cyan/purple background, neutral warm key, clean sharp PSX; original textures/pose retained.'
 return dict(removed=removed,room_meshes_relit=affected,lights=LIGHTS,character_lighting_layer=bool(actor),original_chair=True,new_furniture=False,media_lighting_unchanged=True)
