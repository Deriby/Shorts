"""Render camera views of the existing v3, without changing or saving its model."""
from pathlib import Path
import bpy,math,json,hashlib
from mathutils import Vector
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'Dery_Referencia_Sem_Mochila_v3.blend'
with SOURCE.open('rb') as f:source_hash=hashlib.file_digest(f,'sha256').hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene=bpy.context.scene;cam=scene.camera
scene.render.engine='BLENDER_EEVEE_NEXT';scene.eevee.taa_render_samples=1
scene.render.image_settings.file_format='PNG';scene.render.resolution_percentage=100;scene.render.film_transparent=False
cam.data.type='ORTHO';cam.data.clip_start=.01;cam.data.clip_end=100
views=[('01_frente','Frente',0),('02_tres_quartos_direita','3/4 frente — direita',45),('03_lateral_direita','Lateral direita',90),('04_costas_direita','3/4 costas — direita',135),('05_costas','Costas',180),('06_costas_esquerda','3/4 costas — esquerda',225),('07_lateral_esquerda','Lateral esquerda',270),('08_tres_quartos_esquerda','3/4 frente — esquerda',315)]
records=[]
for group,width,height,scale,focus,radius,lift in [('corpo',540,680,2.06,Vector((0,0,.91)),5,.07),('rosto',512,512,.47,Vector((0,.01,1.64)),3,.035)]:
 scene.render.resolution_x=width;scene.render.resolution_y=height;cam.data.ortho_scale=scale
 folder=HERE/group;folder.mkdir(exist_ok=True)
 for slug,label,degrees in views:
  a=math.radians(degrees)
  cam.location=focus+Vector((-radius*math.sin(a),-radius*math.cos(a),lift))
  cam.rotation_euler=(focus-cam.location).to_track_quat('-Z','Y').to_euler()
  dest=folder/(slug+'.png');scene.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
  records.append({'group':group,'file':dest.relative_to(HERE).as_posix(),'label':label,'camera_azimuth_degrees':degrees,'resolution':[width,height]})
with SOURCE.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==source_hash
(HERE/'vistas.json').write_text(json.dumps({'source_blend':SOURCE.name,'source_sha256':source_hash,'source_unchanged':True,'render_engine':scene.render.engine,'new_model_or_textures_created':False,'side_labels':'Anatomical sides of Dery: model right = negative X; model left = positive X.','views':records},ensure_ascii=False,indent=2)+'\n')
print('DONE: 16 views; source model unchanged.')
