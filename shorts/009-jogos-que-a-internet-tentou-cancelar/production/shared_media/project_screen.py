"""Export the visible CRT quad and depth-aware occlusion mask; no beauty render."""
from pathlib import Path
import bpy,json,sys,math,hashlib
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
args=sys.argv[sys.argv.index('--')+1:];P=Path(args[0]).resolve();model=P/args[1];C=Path(args[2]);C.mkdir(parents=True,exist_ok=True)
info=json.loads((P/'timeline.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(model));s=bpy.context.scene
screen=bpy.data.objects['Tela do PC | substituir por vídeo'];cam=bpy.data.objects[s['Production | camera']]
# The projection pass never decodes video: colors are irrelevant to ray visibility.
placeholder=bpy.data.images.new('Projection only',width=1,height=1)
for node in screen.data.materials[0].node_tree.nodes:
 if node.type=='TEX_IMAGE':node.image=placeholder
out={};occluded=0;visible=0
for sh in info['shots']:
 if sh['kind']not in['monitor','host','close']:continue
 for frame in range(sh['start'],sh['end']+1):
  s.frame_set(frame);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();evaluated=screen.evaluated_get(deps);mesh=evaluated.to_mesh()
  try:
   corners=[evaluated.matrix_world@mesh.vertices[i].co for i in[3,2,1,0]]
   proj=[world_to_camera_view(s,cam,p)for p in corners]
   if any(v.z<=0 for v in proj):continue
   quad=[(v.x*768,(1-v.y)*432)for v in proj]
   if max(p[0]for p in quad)<0 or min(p[0]for p in quad)>768 or max(p[1]for p in quad)<0 or min(p[1]for p in quad)>432:continue
   area=abs(sum(quad[i][0]*quad[(i+1)%4][1]-quad[(i+1)%4][0]*quad[i][1]for i in range(4)))/2
   if area<4:continue
   # Coarse visibility detects hands/bezel in front of the display.
   origin=cam.matrix_world.translation
   def hits(u,v):
    p=corners[0]*(1-u)*(1-v)+corners[1]*u*(1-v)+corners[2]*u*v+corners[3]*(1-u)*v
    direction=p-origin;hit=s.ray_cast(deps,origin,direction.normalized(),distance=direction.length+.08)
    return bool(hit[0]and hit[4]and hit[4].original==screen.original)
   sample=[hits((x+.5)/8,(y+.5)/6)for y in range(6)for x in range(8)]
   mask=None
   if not all(sample):
    width,height=64,48;mask=[int(hits((x+.5)/width,(y+.5)/height))*255 for y in range(height)for x in range(width)];occluded+=1
   out[str(frame)]={'quad':quad,'mask':mask};visible+=1
  finally:evaluated.to_mesh_clear()
report=dict(model_sha256=hashlib.sha256(model.read_bytes()).hexdigest(),render_size=[768,432],screen_aspect=4/3,mask_size=[64,48],frames=out,visible_frames=visible,occluded_frames=occluded)
(C/'screen_projection.json').write_text(json.dumps(report,separators=(',',':')))
print('SCREEN_PROJECTION_READY',P.name,visible,occluded,flush=True)
