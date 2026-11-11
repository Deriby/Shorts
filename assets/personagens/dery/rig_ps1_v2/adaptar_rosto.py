"""Rebuild only the facial patch of the supplied rig, preserving the boundary."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
from mathutils.bvhtree import BVHTree
from collections import Counter
import sys,argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parent)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
BASE=args.output.resolve();BASE.mkdir(parents=True,exist_ok=True)
SOURCE=Path(__file__).resolve().parent/'original'/'autorig_actor.fbx'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(SOURCE),use_anim=True)
# The supplied FBX imports at centimetre-scale; scale the complete hierarchy together.
bpy.ops.object.empty_add(type='PLAIN_AXES');root=bpy.context.object;root.name='EscalaImportacao'
for obj in list(bpy.data.objects):
 if obj!=root and obj.parent is None:obj.parent=root
root.scale=(160,160,160)
bpy.context.view_layer.update()
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=650;scene.render.resolution_y=650;scene.render.resolution_percentage=100
scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.3
scene.display.shading.show_shadows=True;scene.display.shading.show_specular_highlight=False
scene.display.shading.background_type='VIEWPORT';scene.display.shading.background_color=(.16,.17,.19)
scene.view_settings.view_transform='Standard'
bpy.ops.object.camera_add();scene.camera=bpy.context.object;scene.camera.data.type='ORTHO';scene.camera.data.ortho_scale=.51;scene.camera.data.clip_start=.001

o=bpy.data.objects['default'];old=o.data;groupnames=[g.name for g in o.vertex_groups]
original_normals=[n.vector.copy() for n in old.corner_normals]
source_positions=[v.co.copy() for v in old.vertices]
source_world=[o.matrix_world@v.co for v in old.vertices]
source_bvh=BVHTree.FromPolygons(source_world,[list(p.vertices) for p in old.polygons],all_triangles=True)
def clamp(v):return max(0,min(1,v))
def smooth(v):v=clamp(v);return v*v*(3-2*v)
def interp(z,keys):
 for (za,a),(zb,b) in zip(keys,keys[1:]):
  if z<=zb:return a+(b-a)*clamp((z-za)/(zb-za))
 return keys[-1][1]
def target(x,z):
 base=interp(z,[(1.54,-.103),(1.575,-.108),(1.606,-.108),(1.626,-.106),(1.641,-.104),(1.658,-.105),(1.679,-.106),(1.700,-.107),(1.75,-.103)])
 base+=.055*(abs(x)/.09)**2
 depth=interp(z,[(1.54,0),(1.606,0),(1.626,.003),(1.641,.030),(1.658,.017),(1.679,.003),(1.700,0),(1.75,0)])
 width=interp(z,[(1.54,.023),(1.626,.023),(1.641,.023),(1.658,.016),(1.679,.014),(1.75,.014)])
 result=base-depth*max(0,1-abs(x)/width)
 if z<1.594:
  hit=source_bvh.ray_cast(Vector((x,-1,z)),Vector((0,1,0)))[0]
  if hit is not None:
   w=smooth((z-1.574)/.020);result=result*w+hit.y*(1-w)
 return result
def influence(co):
 x,y,z=co
 return smooth((z-1.574)/.020)*smooth((1.750-z)/.022)*smooth((.097-abs(x))/.022)*smooth((-.020-y)/.028)
inv0=o.matrix_world.inverted()
for v in old.vertices:
 co=o.matrix_world@v.co;w=influence(co)
 if w:
  co.y=co.y*(1-w)+target(co.x,co.z)*w;v.co=inv0@co
old.update()
world=[o.matrix_world@v.co for v in old.vertices]
# Select one closed front region on the untouched source, before deformation.
source_selection=[]
for p in old.polygons:
 def inside_source(i):
  x,y,z=source_world[i]
  width=.071 if z>1.596 else .056+(z-1.563)*.45
  return 1.563<z<1.722 and abs(x)<width and y<-.048
 if all(inside_source(i) for i in p.vertices):source_selection.append(p.index)
sel=set(source_selection)
edge_counts=Counter(e for i in sel for e in old.polygons[i].edge_keys)
adjacency={}
for (a,b),count in edge_counts.items():
 if count==1:adjacency.setdefault(a,[]).append(b);adjacency.setdefault(b,[]).append(a)
assert all(len(neighbors)==2 for neighbors in adjacency.values())
start=min(adjacency);loop=[start];previous=None;current=start
while True:
 following=next(i for i in adjacency[current] if i!=previous)
 if following==start:break
 assert following not in loop
 loop.append(following);previous,current=current,following
assert len(loop)==len(adjacency), 'Expected a single facial boundary'

outline=[Vector((world[i].x,world[i].z)) for i in loop]
area=sum(a.x*b.y-b.x*a.y for a,b in zip(outline,outline[1:]+outline[:1]))
if area<0:loop.reverse();outline.reverse()
def inside(x,z):
 odd=False
 for a,b in zip(outline,outline[1:]+outline[:1]):
  if (a.y>z)!=(b.y>z) and x<(b.x-a.x)*(z-a.y)/(b.y-a.y)+a.x:odd=not odd
 return odd
def boundary_distance(x,z):
 p=Vector((x,z));minimum=100
 for a,b in zip(outline,outline[1:]+outline[:1]):
  delta=b-a;t=max(0,min(1,(p-a).dot(delta)/delta.length_squared))
  minimum=min(minimum,(p-a-t*delta).length)
 return minimum
points=list(outline)
for z in [1.573,1.588,1.606,1.626,1.641,1.658,1.679,1.700,1.713]:
 for x in [-.061,-.046,-.028,-.014,0,.014,.028,.046,.061]:
  if inside(x,z) and boundary_distance(x,z)>.003:points.append(Vector((x,z)))
cdt=delaunay_2d_cdt(points,[],[list(range(len(loop)))],1,1e-7)
uvpoints,edges,faces,origverts,_,_=cdt
print('CDT',len(uvpoints),'vertices',len(faces),'faces')
assert all(len(f)==3 for f in faces)
# Re-use exact boundary vertices so there is no separate overlapping face sheet.
keep_polys=[p for p in old.polygons if p.index not in sel]
used=sorted({i for p in keep_polys for i in p.vertices})
old_to_new={i:n for n,i in enumerate(used)}
vertices=[old.vertices[i].co.copy() for i in used]
weights=[[(g.group,g.weight) for g in old.vertices[i].groups] for i in used]
inv=o.matrix_world.inverted()
head_group=o.vertex_groups['CC_Base_Head'].index
bvh=BVHTree.FromPolygons(world,[list(p.vertices) for p in old.polygons],all_triangles=True)
def facial_depth(x,z):return target(x,z)
cdt_to_new={}
for n,(p,orig) in enumerate(zip(uvpoints,origverts)):
 b=[i for i in orig if i<len(loop)]
 if b:cdt_to_new[n]=old_to_new[loop[b[0]]]
 else:
  x,z=p;cdt_to_new[n]=len(vertices)
  vertices.append(inv@Vector((x,facial_depth(x,z),z)));weights.append([(head_group,1.0)])
polygons=[tuple(old_to_new[i] for i in p.vertices) for p in keep_polys]
polygons.extend(tuple(cdt_to_new[i] for i in f) for f in faces)
old_uv=[[tuple(old.uv_layers.active.data[i].uv) for i in p.loop_indices] for p in keep_polys]
mesh=bpy.data.meshes.new('Dery | frente contínua PS1');mesh.from_pydata(vertices,[],polygons);mesh.update()
for m in old.materials:mesh.materials.append(m)
mat=bpy.data.materials.new('ROSTO | BASE NEUTRA — pintar no próximo chat');mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.48,.30,.22,1);bs.inputs['Roughness'].default_value=1;bs.inputs['Specular IOR Level'].default_value=0
mat.diffuse_color=(.48,.30,.22,1);mesh.materials.append(mat)
tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.name='EXPRESSAO_PNG';tex.label='PNG 256 × 256 — preencher na etapa de texturas';tex.interpolation='Closest';tex.location=(-370,200)
uvnode=mat.node_tree.nodes.new('ShaderNodeUVMap');uvnode.uv_map='DeryFaceUV';uvnode.location=(-580,200);mat.node_tree.links.new(uvnode.outputs['UV'],tex.inputs['Vector'])
mesh.uv_layers.new(name='Channel0');mesh.uv_layers.new(name='DeryFaceUV');uvold=mesh.uv_layers['Channel0'];uvface=mesh.uv_layers['DeryFaceUV']
for p in mesh.polygons:
 if p.index<len(keep_polys):
  src=keep_polys[p.index];p.material_index=src.material_index;p.use_smooth=src.use_smooth
  for li,uv in zip(p.loop_indices,old_uv[p.index]):uvold.data[li].uv=uv
 else:p.material_index=len(mesh.materials)-1;p.use_smooth=True
 for li in p.loop_indices:
  co=o.matrix_world@mesh.vertices[mesh.loops[li].vertex_index].co
  uvface.data[li].uv=((co.x+.078)/.156,(co.z-1.554)/.176)
  if p.index>=len(keep_polys):uvold.data[li].uv=uvface.data[li].uv
mesh.uv_layers.active=uvface
# Keep the original mesh datablock only in the original imported study, not in deliverable.
o.data=mesh;o.name='Dery_Massacote_Rig_PS1_v2'
o.vertex_groups.clear()
for name in groupnames:o.vertex_groups.new(name=name)
for n,groups in enumerate(weights):
 for gi,w in groups:o.vertex_groups[gi].add([n],w,'REPLACE')
# Close extremely thin triangulation slivers at the original outline.
import bmesh
bm=bmesh.new();bm.from_mesh(mesh)
loose=[e for e in bm.edges if len(e.link_faces)==1]
if loose:
 result=bmesh.ops.holes_fill(bm,edges=loose,sides=20)
 for f in result['faces']:f.material_index=1;f.smooth=True
 bmesh.ops.triangulate(bm,faces=result['faces'])
bm.to_mesh(mesh);bm.free();mesh.update()
# Project every corner again, including filled boundary slivers.
for p in mesh.polygons:
 for li in p.loop_indices:
  co=o.matrix_world@mesh.vertices[mesh.loops[li].vertex_index].co
  mesh.uv_layers['DeryFaceUV'].data[li].uv=((co.x+.078)/.156,(co.z-1.554)/.176)
mesh.uv_layers['Channel0'].active_render=True
# A simple continuous surface needs equally simple normals, without baked lids/lips.
normal_values=[]
normal_transform=o.matrix_world.to_3x3().transposed()
for p in mesh.polygons:
 for li in p.loop_indices:
  vi=mesh.loops[li].vertex_index;co=o.matrix_world@mesh.vertices[vi].co
  eps=.0005
  dx=(target(co.x+eps,co.z)-target(co.x-eps,co.z))/(2*eps)
  dz=(target(co.x,co.z+eps)-target(co.x,co.z-eps))/(2*eps)
  new_n=(normal_transform@Vector((dx,-1,dz))).normalized()
  if p.index<len(keep_polys):
   src=keep_polys[p.index];sli=src.loop_start+list(p.loop_indices).index(li)
   source_n=original_normals[sli]
   w=influence(co)
   normal_values.append((source_n*(1-w)+new_n*w).normalized())
  else:normal_values.append(new_n)
mesh.normals_split_custom_set(normal_values)
for m in bpy.data.materials:
 if m.use_nodes:
  for n in m.node_tree.nodes:
   if n.type=='TEX_IMAGE':n.interpolation='Closest'
# Restore a neutral inspection view and show the retained low-poly silhouette.
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.color_type='SINGLE';scene.display.shading.single_color=(.65,.67,.69)
scene.display.shading.show_cavity=False
focus=Vector((0,-.045,1.64));cam=scene.camera
for label,loc in [('frente',(0,-3,1.64)),('perfil',(3,0,1.64)),('tres_quartos',(2,-3,1.70))]:
 cam.location=loc;cam.rotation_euler=(focus-cam.location).to_track_quat('-Z','Y').to_euler()
 scene.render.filepath=str(BASE/('Previa_'+label+'.png'));bpy.ops.render.render(write_still=True)
# Export a precise template of the facial UV island (not an expression drawing).
lines=[]
for p in mesh.polygons:
 if p.material_index!=len(mesh.materials)-1:continue
 coords=[mesh.uv_layers['DeryFaceUV'].data[i].uv for i in p.loop_indices]
 points_s=' '.join(f'{uv.x*512:.3f},{(1-uv.y)*512:.3f}' for uv in coords)
 lines.append(f'<polygon points="{points_s}"/>')
svg='<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512"><rect width="512" height="512" fill="#ede5d8"/><g fill="none" stroke="#625b52" stroke-width="0.6">'+''.join(lines)+'</g></svg>'
(BASE/'UV_Rosto_PS1.svg').write_text(svg)
report={'original_vertices':len(old.vertices),'original_triangles':len(old.polygons),'new_vertices':len(mesh.vertices),'new_triangles':len(mesh.polygons),'original_facial_triangles':len(sel),'new_facial_triangles':sum(p.material_index==1 for p in mesh.polygons),'shared_boundary_vertices':len(loop),'retained_source_vertices':len(used),'new_facial_vertices':len(vertices)-len(used),'body_below_neck_preserved':all((vertices[n]-source_positions[i]).length<1e-7 for i,n in old_to_new.items() if (o.matrix_world@source_positions[i]).z<1.54),'face_uv':'DeryFaceUV','rig_bones':len(next(ob for ob in bpy.data.objects if ob.type=='ARMATURE').data.bones)}
from collections import Counter
edge_counts=Counter(e for p in mesh.polygons for e in p.edge_keys)
report['edge_face_counts']=dict(Counter(edge_counts.values()))
report['preserved_action_names']=[a.name for a in bpy.data.actions]
report['personalized_face_textures_created']=False
report['stage']='geometry and UV base; personalized expression textures deferred by user'
assert all(n==2 for n in edge_counts.values()), report
(BASE/'adaptacao.json').write_text(json.dumps(report,indent=2)+'\n')
print('REPORT',report)
# Convenient camera when opening the project.
cam.location=(2,-3,1.70);cam.rotation_euler=(focus-cam.location).to_track_quat('-Z','Y').to_euler()
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.region_3d.view_distance=.62;area.spaces.active.region_3d.view_location=focus
   area.spaces.active.region_3d.view_rotation=cam.rotation_euler.to_quaternion();area.spaces.active.shading.type='SOLID'
bpy.ops.file.pack_all()
bpy.context.view_layer.objects.active=o
bpy.ops.object.select_all(action='DESELECT');o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Dery_Rig_PS1_Base.blend'))
