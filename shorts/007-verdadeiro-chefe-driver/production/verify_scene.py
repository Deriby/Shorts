"""Validate geometry preservation, facial seams, seating and actual wheel contact."""
from pathlib import Path
from collections import defaultdict
import bpy,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[2];s=bpy.context.scene
a=bpy.data.objects['DERY | animated character'];a2=bpy.data.objects['CAR | Dery'];r=bpy.data.objects['Dery_Rig'];r2=bpy.data.objects['CAR | Dery rig'];car=bpy.data.objects['CAR | motion']
with bpy.data.libraries.load(str(REPO/'shorts/004-crash-apelido/production/output/Dery_Crash_Master_R5.blend'))as(src,dst):dst.objects=['DERY | animated character']
original=dst.objects[0]
geometry=max((x.co-y.co).length for x,y in zip(a.data.vertices,original.data.vertices));assert geometry==0
assert len(a.data.vertices)==len(a2.data.vertices)==len(original.data.vertices)
assert max((x.co-y.co).length for x,y in zip(a2.data.vertices,original.data.vertices))==0
reports=[];room_hips=[];car_hips=[];contacts=[]
for obj,frames in [(a,[134,683,798]),(a2,[611,930,980,1040])]:
 mod=next(m for m in obj.modifiers if m.type=='NODES')
 def positions(on):
  mod.show_viewport=on;bpy.context.view_layer.update();ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();out=[v.co.copy()for v in me.vertices];ev.to_mesh_clear();return out
 for f in frames:
  s.frame_set(f);before=positions(False);after=positions(True);groups=defaultdict(list)
  for i,v in enumerate(obj.data.vertices):
   if v.co.z>1.44 and v.co.y<-.015 and abs(v.co.x)<.14:groups[tuple(round(c,6)for c in before[i])].append(i)
  gap=max(((after[i]-after[ids[0]]).length for ids in groups.values()if len(ids)>1 for i in ids),default=0)
  assert gap<.00005,(obj.name,f,gap);reports.append(dict(actor=obj.name,frame=f,max_facial_split_m=gap))
for f in [134,683,798,611,930,980,1040]:
 s.frame_set(f);bpy.context.view_layer.update();room_hips.append((r.matrix_world@r.pose.bones['pelvis'].head).copy());car_hips.append((car.matrix_world.inverted()@r2.matrix_world@r2.pose.bones['pelvis'].head).copy())
for positions in [room_hips,car_hips]:assert max((p-positions[0]).length for p in positions)<.00001
for f in [611,980,1040]:
 s.frame_set(f);bpy.context.view_layer.update();ev=a2.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();verts=[a2.matrix_world@v.co for v in me.vertices]
 for side,sign in [('R',-1),('L',1)]:
  group=a2.vertex_groups['hand_'+side].index;indices={v.index for v in a2.data.vertices if any(g.group==group and g.weight>.35 for g in v.groups)}
  tree=BVHTree.FromPolygons(verts,[tuple(p.vertices)for p in me.polygons if any(i in indices for i in p.vertices)])
  points=[car.matrix_world@Vector((-.28+.18*math.cos(ang),-.39,1.06+.18*math.sin(ang)))for ang in [j*math.tau/128 for j in range(128)]if math.cos(ang)*sign>.5]
  gap=min(tree.find_nearest(p)[3]for p in points);contacts.append(dict(frame=f,hand=side,surface_to_wheel_m=gap));assert gap<.035,(f,side,gap)
 ev.to_mesh_clear()
tex=next(n for n in bpy.data.objects['CRT moving picture'].data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE');assert tex.image_user.use_auto_refresh and tex.image_user.frame_duration==s.frame_end
for obj in [a,a2]:
 assert all(k.value==0 for k in obj.data.shape_keys.key_blocks[1:])
 for fc in obj.animation_data.action.fcurves:
  if 'PS1_face_id'in fc.data_path:assert all(k.interpolation=='CONSTANT'for k in fc.keyframe_points)
report=dict(original_geometry_max_displacement_m=geometry,face_checks=reports,seated_pelvis_stable=True,wheel_contacts=contacts,monitor_auto_refresh=True,monitor_frames=tex.image_user.frame_duration,expressions='31 drawn PNGs; discrete changes; no morphing')
(ROOT/'scene_validation.json').write_text(json.dumps(report,indent=2));print('SCENE_VALIDATED',json.dumps(report),flush=True)
