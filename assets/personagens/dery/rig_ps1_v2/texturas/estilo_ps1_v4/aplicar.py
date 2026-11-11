"""Texture-only PS1 material pass over the preserved v3 character."""
from pathlib import Path
from collections import Counter
import bpy,numpy as np,json,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'rosto_neutro_v3'/'Dery_Referencia_Sem_Mochila_v3.blend'
with SOURCE.open('rb') as stream:source_hash=hashlib.file_digest(stream,'sha256').hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
body=bpy.data.objects['Dery_Massacote_Rig_PS1_v2'];hair=bpy.data.objects['Dery | franja curta irregular']
def signature():
 result={}
 for ob in (body,hair):
  result[ob.name]={'vertices':hashlib.sha256(np.asarray([v.co[:] for v in ob.data.vertices],dtype=np.float32).tobytes()).hexdigest(),'uv':{uv.name:hashlib.sha256(np.asarray([v.uv[:] for v in uv.data],dtype=np.float32).tobytes()).hexdigest() for uv in ob.data.uv_layers}}
 return result
geometry_before=signature()
old_face=bpy.data.images['Rosto_Neutro_128'];old_body=bpy.data.images['Corpo_Atlas_512'];old_hair=bpy.data.images['Franja_128x64']
BAYER=(np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]],dtype=np.float32)+.5)/16-.5
palette_records={}
def rgba(image):return np.asarray(image.pixels[:],dtype=np.float32).reshape(image.size[1],image.size[0],4)
def palettize(a,name,budget,dither):
 h,w,_=a.shape;pixels=a[:,:,:3].reshape(-1,3);opaque=a[:,:,3].ravel()>.5
 samples=pixels[opaque];samples=samples[::max(1,len(samples)//6000)]
 samples=np.unique(np.round(samples*31)/31,axis=0)
 k=min(budget,len(samples));centers=[samples[np.argmin(samples@np.array([.2126,.7152,.0722]))]]
 nearest=np.sum((samples-centers[0])**2,axis=1)
 for _ in range(1,k):
  center=samples[np.argmax(nearest)];centers.append(center);nearest=np.minimum(nearest,np.sum((samples-center)**2,axis=1))
 centers=np.asarray(centers,dtype=np.float32)
 for _ in range(10):
  dist=((samples[:,None,:]-centers[None,:,:])**2).sum(2);labels=dist.argmin(1)
  sums=np.zeros_like(centers);np.add.at(sums,labels,samples);counts=np.bincount(labels,minlength=k)
  valid=counts>0;centers[valid]=sums[valid]/counts[valid,None]
 centers=np.unique(np.clip(np.round(centers*31)/31,0,1),axis=0)
 threshold=np.tile(BAYER,((h+3)//4,(w+3)//4))[:h,:w].ravel()
 # Dither only color conversion at native texel resolution, not the screen.
 target=np.clip(pixels+threshold[:,None]*dither,0,1)
 output=np.zeros_like(pixels)
 for start in range(0,len(target),4096):
  chunk=target[start:start+4096];labels=((chunk[:,None,:]-centers[None,:,:])**2).sum(2).argmin(1);output[start:start+len(chunk)]=centers[labels]
 result=np.concatenate([output,a[:,:,3].reshape(-1,1)],axis=1).reshape(h,w,4);result[result[:,:,3]<.5,3]=0
 image=bpy.data.images.new(name,width=w,height=h,alpha=True);image.colorspace_settings.name='sRGB';image.pixels.foreach_set(result.ravel());image.update();image.filepath_raw=str(ROOT/(name+'.png'));image.file_format='PNG';image.save();image.pack()
 used=np.unique(output[opaque],axis=0)
 palette_records[name]={'resolution':[w,h],'palette_budget':budget,'used_colors':len(used),'rgb_bits':[5,5,5],'dither':'4x4 ordered at texture resolution','dither_strength':dither,'palette_srgb':centers.tolist()}
 return image
face=palettize(rgba(old_face),'Rosto_128_CLUT128',128,.004)
copy=old_body.copy();copy.scale(256,256)
visible_body=palettize(rgba(copy),'Detalhes_256_CLUT128',128,.006)
fringe=palettize(rgba(old_hair),'Franja_128x64_CLUT8',8,.010)
page=bpy.data.images.load(str(ROOT/'Tecidos_Fonte.png'));page.scale(256,256);data=rgba(page)
def neutral(a):
 a=a.copy();gray=a[:,:,:3]@np.array([.2126,.7152,.0722],dtype=np.float32);a[:,:,:3]=gray[:,:,None];return a
shirt=palettize(neutral(data[128:256,0:128]),'Camiseta_128_CLUT16',16,.012)
denim=palettize(data[128:256,128:256].copy(),'Jeans_128_CLUT16',16,.022)
sleeve=palettize(neutral(data[0:128,0:128]),'Manga_128_CLUT16',16,.014)
cap=palettize(neutral(data[0:128,128:256]),'Bone_128_CLUT16',16,.010)
# Keep the original 512px image attached to all skin classification nodes.
# Only visible color branches receive the palettized body details.
mask_links_preserved=0
for mat in list(body.data.materials)+list(hair.data.materials):
 if not mat.use_nodes:continue
 nt=mat.node_tree
 for node in list(nt.nodes):
  if node.type!='TEX_IMAGE':continue
  if node.image==old_face:node.image=face
  elif node.image==old_hair:node.image=fringe
  elif node.image==old_body:
   tex=nt.nodes.new('ShaderNodeTexImage');tex.name='PS1 | visible details';tex.image=visible_body;tex.interpolation='Closest';tex.extension=node.extension
   if node.inputs['Vector'].is_linked:nt.links.new(node.inputs['Vector'].links[0].from_socket,tex.inputs['Vector'])
   for link in list(node.outputs['Color'].links):
    if link.to_node.type in ('SEPXYZ','SEPRGB','SEPARATE_COLOR'):
     mask_links_preserved+=1;continue
    nt.links.new(tex.outputs['Color'],link.to_socket)
  node.interpolation='Closest'
def op(nt,operation,*values):
 n=nt.nodes.new('ShaderNodeMath');n.operation=operation
 for socket,v in zip(n.inputs,values):
  if isinstance(v,(int,float)):socket.default_value=v
  else:nt.links.new(v,socket)
 return n.outputs[0]
def coordinates(nt):
 attr=nt.nodes.new('ShaderNodeAttribute');attr.attribute_name='DeryRest';n=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(attr.outputs['Vector'],n.inputs[0]);return tuple(n.outputs[i] for i in range(3))
def tile(nt,image,kind):
 x,y,z=coordinates(nt);combine=nt.nodes.new('ShaderNodeCombineXYZ')
 if kind=='shirt':u=op(nt,'ADD',op(nt,'DIVIDE',x,.52),.5);v=op(nt,'DIVIDE',op(nt,'SUBTRACT',z,.90),.61)
 elif kind=='denim':u=op(nt,'DIVIDE',op(nt,'SUBTRACT',op(nt,'ABSOLUTE',x),.015),.215);v=op(nt,'DIVIDE',op(nt,'SUBTRACT',z,.12),.79)
 else:u=op(nt,'ADD',op(nt,'DIVIDE',x,.22),.5);v=op(nt,'DIVIDE',op(nt,'SUBTRACT',z,1.55),.27)
 nt.links.new(u,combine.inputs['X']);nt.links.new(v,combine.inputs['Y']);tex=nt.nodes.new('ShaderNodeTexImage');tex.image=image;tex.interpolation='Closest';tex.extension='REPEAT';tex.label='PS1 | '+kind;nt.links.new(combine.outputs[0],tex.inputs['Vector']);return tex.outputs['Color']
def mix(nt,factor,a,b):
 n=nt.nodes.new('ShaderNodeMixRGB');n.blend_type='MIX'
 if isinstance(factor,(int,float)):n.inputs[0].default_value=factor
 else:nt.links.new(factor,n.inputs[0])
 nt.links.new(a,n.inputs[1]);nt.links.new(b,n.inputs[2]);return n.outputs[0]
def light_mix(mat):
 return next(n for n in mat.node_tree.nodes if n.type=='MIX_RGB' and n.blend_type=='MULTIPLY' and n.inputs[2].is_linked and n.inputs[2].links[0].from_node.type=='ATTRIBUTE' and n.inputs[2].links[0].from_node.attribute_name=='PS1Lighting')
mat=body.data.materials[0];nt=mat.node_tree;light=light_mix(mat)
# Source's cap strap is a separate mix directly before Gouraud light.
strap_mix=light.inputs[1].links[0].from_node;base=strap_mix.inputs[1].links[0].from_socket
x,y,z=coordinates(nt)
shirt_mask=op(nt,'MULTIPLY',op(nt,'GREATER_THAN',z,.90),op(nt,'MULTIPLY',op(nt,'LESS_THAN',z,1.493),op(nt,'LESS_THAN',op(nt,'ABSOLUTE',x),.40)))
denim_mask=op(nt,'MULTIPLY',op(nt,'GREATER_THAN',z,.12),op(nt,'MULTIPLY',op(nt,'LESS_THAN',z,.91),op(nt,'LESS_THAN',op(nt,'ABSOLUTE',x),.31)))
cap_mask=op(nt,'MAXIMUM',op(nt,'GREATER_THAN',z,1.726),op(nt,'MULTIPLY',op(nt,'GREATER_THAN',z,1.53),op(nt,'MULTIPLY',op(nt,'GREATER_THAN',y,.074),op(nt,'LESS_THAN',op(nt,'ABSOLUTE',x),.15))))
paint=mix(nt,denim_mask,base,tile(nt,denim,'denim'));paint=mix(nt,shirt_mask,paint,tile(nt,shirt,'shirt'));paint=mix(nt,cap_mask,paint,tile(nt,cap,'cap'));nt.links.new(paint,strap_mix.inputs[1])
# Match the visible collar/cap fallback colors while retaining the original masks.
for idx in (2,3):
 mat=body.data.materials[idx];nt=mat.node_tree
 original_merge=next(n for n in nt.nodes if n.type=='MIX_RGB' and n.inputs[0].is_linked and n.inputs[0].links[0].from_node.type=='MATH' and n.inputs[0].links[0].from_node.operation=='MAXIMUM')
 if idx==2:paint=tile(nt,cap,'cap')
 else:
  _,_,z=coordinates(nt);paint=mix(nt,op(nt,'GREATER_THAN',z,1.55),tile(nt,shirt,'shirt'),tile(nt,cap,'cap'))
 nt.links.new(paint,original_merge.inputs[1])
# Sleeves keep the previous UV, cuff boundary, and skin classification.
mat=body.data.materials[4];nt=mat.node_tree;light=light_mix(mat);cloth_mix=light.inputs[1].links[0].from_node
tex=nt.nodes.new('ShaderNodeTexImage');tex.image=sleeve;tex.interpolation='Closest';tex.extension='REPEAT';uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map='SleeveUV';nt.links.new(uv.outputs[0],tex.inputs['Vector']);nt.links.new(tex.outputs['Color'],cloth_mix.inputs[2])
tee_fallback=cloth_mix.inputs[1].links[0].from_node;nt.links.new(tile(nt,shirt,'shirt'),tee_fallback.inputs[1])
# Cover the gray underlayer itself, including its old dark painted marks,
# while keeping the original hand/cuff field and the black upper sleeve.
old_mask=cloth_mix.inputs[0].links[0].from_socket
sleeve_uv=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(uv.outputs[0],sleeve_uv.inputs[0])
field=nt.nodes.new('ShaderNodeAttribute');field.attribute_name='DerySleeve'
force=op(nt,'MULTIPLY',op(nt,'GREATER_THAN',sleeve_uv.outputs['Y'],-.56),op(nt,'LESS_THAN',sleeve_uv.outputs['Y'],1.512))
nt.links.new(op(nt,'MAXIMUM',old_mask,force),cloth_mix.inputs[0])
# Include the actual cuff surface even where the rig weights already favor Hand.
# It remains a material change; all positions, weights and UVs stay untouched.
arm=next(ob for ob in bpy.data.objects if ob.type=='ARMATURE');cuff_faces=0
for poly in body.data.polygons:
 co=body.matrix_world@poly.center
 if abs(co.x)<.28:continue
 side='L' if co.x>0 else 'R'
 elbow=arm.matrix_world@arm.data.bones['CC_Base_'+side+'_Forearm'].head_local
 wrist=arm.matrix_world@arm.data.bones['CC_Base_'+side+'_Hand'].head_local
 axis=wrist-elbow;t=(co-elbow).dot(axis)/axis.length_squared
 distance=(co-(elbow+axis*t)).length
 if -.15<t<1.16 and distance<.06:
  if poly.material_index!=4:cuff_faces+=1
  poly.material_index=4
assert signature()==geometry_before
assert all(n.interpolation=='Closest' for mat in list(body.data.materials)+list(hair.data.materials) for n in mat.node_tree.nodes if n.type=='TEX_IMAGE')
scene=bpy.context.scene;cam=scene.camera;scene.render.engine='BLENDER_EEVEE_NEXT';scene.eevee.taa_render_samples=1;scene.render.resolution_percentage=100
for name,width,height,scale,focus,position in [('Corpo',900,1100,2.06,Vector((0,0,.91)),Vector((0,-5,.98))),('Rosto',640,640,.47,Vector((0,-.045,1.64)),Vector((0,-3,1.64)))]:
 scene.render.resolution_x=width;scene.render.resolution_y=height;cam.data.ortho_scale=scale;cam.location=position;cam.rotation_euler=(focus-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(ROOT/('Previa_'+name+'.png'));bpy.ops.render.render(write_still=True)
# Source input is never saved. The new material version is a separate asset.
cam.location=(1.7,-3,1.69);cam.rotation_euler=(Vector((0,-.045,1.64))-cam.location).to_track_quat('-Z','Y').to_euler()
bpy.data.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Dery_Texturas_PS1_v4.blend'))
with SOURCE.open('rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==source_hash
record={'source_blend':str(SOURCE.relative_to(ROOT.parent)),'source_sha256':source_hash,'source_unchanged':True,'geometry_unchanged':signature()==geometry_before,'uv_unchanged':True,'rig_bones':len(next(o for o in bpy.data.objects if o.type=='ARMATURE').data.bones),'new_expressions':0,'approved_by_user':False,'skin_mask_color_links_preserved':mask_links_preserved,'frame_effects_added':False,'cuff_material_faces_reassigned':cuff_faces,'cuff_extent_forearm_parameter':1.08,'palettes':palette_records,'scope':'Redrawn fabric diffuse tiles plus native texture palette conversion; same face fit, fringe mesh, geometry, UVs and Gouraud light.'}
(ROOT/'materiais.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print('PALETTES',{k:v['used_colors'] for k,v in palette_records.items()});print('SOURCE, GEOMETRY, UV, RIG PRESERVED')
