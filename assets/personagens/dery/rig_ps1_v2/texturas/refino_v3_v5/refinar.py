"""Gentle, reversible native-texel detail pass. Reuses every original v3 image."""
from pathlib import Path
import bpy,numpy as np,hashlib,json
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'rosto_neutro_v3'/'Dery_Referencia_Sem_Mochila_v3.blend'
with SOURCE.open('rb') as f:source_hash=hashlib.file_digest(f,'sha256').hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
body=bpy.data.objects['Dery_Massacote_Rig_PS1_v2'];hair=bpy.data.objects['Dery | franja curta irregular']
def state():
 result={}
 for ob in (body,hair):
  m=ob.data;result[ob.name]={'positions':hashlib.sha256(np.asarray([v.co[:] for v in m.vertices],dtype=np.float32).tobytes()).hexdigest(),'uv':{uv.name:hashlib.sha256(np.asarray([v.uv[:] for v in uv.data],dtype=np.float32).tobytes()).hexdigest() for uv in m.uv_layers},'material_assignments':hashlib.sha256(np.asarray([p.material_index for p in m.polygons],dtype=np.int32).tobytes()).hexdigest()}
 return result
before=state()
def image_hash(i):return hashlib.sha256(np.asarray(i.pixels[:],dtype=np.float32).tobytes()).hexdigest()
images_before={i.name:image_hash(i) for i in bpy.data.images if i.type=='IMAGE'}
settings={};mask_links_preserved=0;source_count=0
for mat in list(body.data.materials)+list(hair.data.materials):
 if not mat.use_nodes:continue
 nt=mat.node_tree
 for center in list(nt.nodes):
  if center.type!='TEX_IMAGE' or not center.image:continue
  # Raw classification and alpha continue to use the exact v3 samples.
  visible=[link for link in center.outputs['Color'].links if link.to_node.type not in ('SEPXYZ','SEPRGB','SEPARATE_COLOR')]
  mask_links_preserved+=sum(link.to_node.type in ('SEPXYZ','SEPRGB','SEPARATE_COLOR') for link in center.outputs['Color'].links)
  if not visible:continue
  image=center.image;w,h=image.size
  is_face='Rosto' in image.name;is_hair='Franja' in image.name
  strength=.10 if is_face else (.08 if is_hair else .24)
  limit=.006 if is_face else (.004 if is_hair else .010)
  family=image.name
  center['DeryTextureFamily']=family
  nodes=nt.nodes;links=nt.links
  if center.inputs['Vector'].is_linked:coords=center.inputs['Vector'].links[0].from_socket
  else:coords=nodes.new('ShaderNodeTexCoord').outputs['UV']
  # Only the visible body material gets a coarser texel grid. Raw skin-mask
  # samplers in the face/sleeve materials retain their exact original UV sample.
  source_size=[w,h];sampling_size=[w,h]
  if image.name=='Corpo_Atlas_512' and mat==body.data.materials[0]:
   separate=nodes.new('ShaderNodeSeparateXYZ');links.new(coords,separate.inputs[0])
   combine=nodes.new('ShaderNodeCombineXYZ')
   for axis in ('X','Y'):
    multiply=nodes.new('ShaderNodeMath');multiply.operation='MULTIPLY';multiply.inputs[1].default_value=256;links.new(separate.outputs[axis],multiply.inputs[0])
    floor=nodes.new('ShaderNodeMath');floor.operation='FLOOR';links.new(multiply.outputs[0],floor.inputs[0])
    add=nodes.new('ShaderNodeMath');add.operation='ADD';add.inputs[1].default_value=.5;links.new(floor.outputs[0],add.inputs[0])
    divide=nodes.new('ShaderNodeMath');divide.operation='DIVIDE';divide.inputs[1].default_value=256;links.new(add.outputs[0],divide.inputs[0]);links.new(divide.outputs[0],combine.inputs[axis])
   coords=combine.outputs[0];links.new(coords,center.inputs['Vector']);w=h=256;sampling_size=[256,256]
  total=None
  for dx,dy in ((1/w,0),(-1/w,0),(0,1/h),(0,-1/h)):
   offset=nodes.new('ShaderNodeVectorMath');offset.operation='ADD';links.new(coords,offset.inputs[0]);offset.inputs[1].default_value=(dx,dy,0)
   sample=nodes.new('ShaderNodeTexImage');sample.image=image;sample.interpolation='Closest';sample.extension=center.extension;sample.projection=center.projection;sample['DeryTextureFamily']=family;sample.label='Amostra vizinha | mesmo PNG'
   links.new(offset.outputs['Vector'],sample.inputs['Vector'])
   if total is None:total=sample.outputs['Color']
   else:
    add=nodes.new('ShaderNodeVectorMath');add.operation='ADD';links.new(total,add.inputs[0]);links.new(sample.outputs['Color'],add.inputs[1]);total=add.outputs[0]
  mean=nodes.new('ShaderNodeVectorMath');mean.operation='SCALE';links.new(total,mean.inputs[0]);mean.inputs['Scale'].default_value=.25
  detail=nodes.new('ShaderNodeVectorMath');detail.operation='SUBTRACT';links.new(center.outputs['Color'],detail.inputs[0]);links.new(mean.outputs[0],detail.inputs[1])
  control=nodes.new('ShaderNodeValue');control.name='Refino | '+family;control.label='Nitidez suave | 0 desliga';control.outputs[0].default_value=strength
  boost=nodes.new('ShaderNodeVectorMath');boost.operation='SCALE';links.new(detail.outputs[0],boost.inputs[0]);links.new(control.outputs[0],boost.inputs['Scale'])
  low=nodes.new('ShaderNodeVectorMath');low.operation='MAXIMUM';links.new(boost.outputs[0],low.inputs[0]);low.inputs[1].default_value=(-limit,-limit,-limit)
  high=nodes.new('ShaderNodeVectorMath');high.operation='MINIMUM';links.new(low.outputs[0],high.inputs[0]);high.inputs[1].default_value=(limit,limit,limit)
  result=nodes.new('ShaderNodeVectorMath');result.operation='ADD';links.new(center.outputs['Color'],result.inputs[0]);links.new(high.outputs[0],result.inputs[1])
  clip_low=nodes.new('ShaderNodeVectorMath');clip_low.operation='MAXIMUM';links.new(result.outputs[0],clip_low.inputs[0]);clip_low.inputs[1].default_value=(0,0,0)
  clip_high=nodes.new('ShaderNodeVectorMath');clip_high.operation='MINIMUM';links.new(clip_low.outputs[0],clip_high.inputs[0]);clip_high.inputs[1].default_value=(1,1,1)
  for link in visible:links.new(clip_high.outputs[0],link.to_socket)
  settings[mat.name+' / '+family]={'source_resolution':source_size,'sampling_grid':sampling_size,'strength':strength,'maximum_linear_channel_change':limit,'artwork_replaced':False,'original_png_unchanged':True,'interpolation':'Closest'}
  source_count+=1
assert state()==before
assert {i.name:image_hash(i) for i in bpy.data.images if i.type=='IMAGE'}==images_before
scene=bpy.context.scene;cam=scene.camera;scene.render.engine='BLENDER_EEVEE_NEXT';scene.eevee.taa_render_samples=1;scene.render.resolution_percentage=100
for name,w,h,scale,focus,position in [('Corpo',900,1100,2.06,Vector((0,0,.91)),Vector((0,-5,.98))),('Rosto',640,640,.47,Vector((0,-.045,1.64)),Vector((0,-3,1.64)))]:
 scene.render.resolution_x=w;scene.render.resolution_y=h;cam.data.ortho_scale=scale;cam.location=position;cam.rotation_euler=(focus-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(ROOT/('Previa_'+name+'.png'));bpy.ops.render.render(write_still=True)
cam.location=(1.7,-3,1.69);cam.rotation_euler=(Vector((0,-.045,1.64))-cam.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Dery_v3_Refino_v5.blend'))
with SOURCE.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==source_hash
record={'source_blend':'../rosto_neutro_v3/'+SOURCE.name,'source_sha256':source_hash,'source_unchanged':True,'all_original_image_pixels_unchanged':True,'image_pixel_hashes':images_before,'geometry_uv_material_assignments_unchanged':True,'rig_bones':len(next(ob for ob in bpy.data.objects if ob.type=='ARMATURE').data.bones),'masks_and_alpha_preserved':True,'mask_color_links_preserved':mask_links_preserved,'sampling_passes':source_count,'settings':settings,'new_texture_art_generated':False,'v4_assets_used':False,'new_expressions':0,'approved_by_user':False,'scope':'Gentle reversible native-texel detail enhancement of existing v3 samples, without repainting, recoloring, re-palettizing or changing layouts. The original 512px body image uses an effective 256px visible sampling grid; raw skin masks retain native sampling.'}
(ROOT/'refino.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print(record)
