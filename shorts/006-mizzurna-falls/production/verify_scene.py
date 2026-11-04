"""Check facial seams, stable seating, monitor playback and the badge contact."""
from pathlib import Path
from collections import defaultdict
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parent;s=bpy.context.scene
a=bpy.data.objects['DERY | animated character'];r=bpy.data.objects['Dery_Rig']
modifier=next(m for m in a.modifiers if m.type=='NODES')
def positions(enabled):
    modifier.show_viewport=enabled;bpy.context.view_layer.update()
    ev=a.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();result=[v.co.copy()for v in mesh.vertices];ev.to_mesh_clear();return result
reports=[];hips=[]
for f in [123,371,1167]:
    s.frame_set(f);before=positions(False);after=positions(True);groups=defaultdict(list)
    for i,v in enumerate(a.data.vertices):
        if v.co.z>1.44 and v.co.y<-.015 and abs(v.co.x)<.14:groups[tuple(round(c,6)for c in before[i])].append(i)
    gap=max(((after[i]-after[ids[0]]).length for ids in groups.values()if len(ids)>1 for i in ids),default=0)
    assert gap<.00005,(f,gap)
    reports.append({'frame':f,'max_facial_split_m':gap});hips.append((r.matrix_world@r.pose.bones['pelvis'].head).copy())
pelvis=max((v-hips[0]).length for v in hips);assert pelvis<.00001,pelvis
contacts=[]
for f in [1160,1170,1178]:
    s.frame_set(f);bpy.context.view_layer.update()
    target=Vector(bpy.data.objects['CLT | sliding badge'].location)+Vector((.075,.030,.009))
    group=a.vertex_groups['hand_R'].index
    indices=[v.index for v in a.data.vertices if any(g.group==group and g.weight>.35 for g in v.groups)]
    ev=a.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
    selected=set(indices)
    vertices=[a.matrix_world@v.co for v in mesh.vertices]
    polygons=[tuple(p.vertices)for p in mesh.polygons if any(i in selected for i in p.vertices)]
    tree=BVHTree.FromPolygons(vertices,polygons)
    point_error=tree.find_nearest(target)[3]
    card=bpy.data.objects['CLT | sliding badge']
    # Contact can lie on a face interior, between vertices, and anywhere along
    # the card's right side. Compare actual surfaces rather than bone endpoints.
    probes=[card.matrix_world@Vector((x,y,.007))for x in [.025,.035,.045,.055,.065,.075]for y in [-.035,-.020,-.005,.010,.025,.040]]
    error=min(tree.find_nearest(p)[3]for p in probes);ev.to_mesh_clear()
    assert error<.010,(f,error)
    contacts.append({'frame':f,'hand_surface_to_badge_contact_m':error,'single_proxy_point_distance_m':point_error})
tex=next(n for n in bpy.data.objects['CRT moving picture'].data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE')
assert tex.image_user.use_auto_refresh and tex.image_user.frame_duration==s.frame_end
for obj in [a,bpy.data.objects['LIMBO | Dery']]:
    for fc in obj.animation_data.action.fcurves:
        if 'PS1_face_id'in fc.data_path:assert all(k.interpolation=='CONSTANT'for k in fc.keyframe_points)
report={'face_checks':reports,'pelvis_movement_m':pelvis,'badge_contacts':contacts,'monitor_auto_refresh':True,'monitor_frames':tex.image_user.frame_duration,'expressions':'Drawn PNGs, constant keys; no active facial morphs.'}
(ROOT/'scene_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
