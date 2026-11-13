from pathlib import Path
import bpy, json, hashlib
P=Path(__file__).resolve().parent
R=next(p for p in P.parents if (p/'AGENTS.md').exists())
C=Path('/workspace/attachments/atuacao_sentada_v2');C.mkdir(parents=True,exist_ok=True)
old=P/'output/Dery_Atuacao_Sentada_Teste.blend'
source=R/'shorts/009-jogos-que-a-internet-tentou-cancelar/production/04-saints-row-iv/output/Dery_Saints_Row_IV.blend'
old_sha=hashlib.sha256(old.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(old))
s=bpy.context.scene
chair=bpy.data.objects['Cadeira do Dery']
def anim_signature():
 rows=[]
 for obj in s.objects:
  if obj.animation_data and obj.animation_data.action:
   rows.append((obj.name,[(fc.data_path,fc.array_index,[(tuple(k.co),k.interpolation)for k in fc.keyframe_points])for fc in obj.animation_data.action.fcurves]))
 for mat in bpy.data.materials:
  if mat.node_tree and mat.node_tree.animation_data and mat.node_tree.animation_data.action:
   rows.append((mat.name,[(fc.data_path,fc.array_index,[(tuple(k.co),k.interpolation)for k in fc.keyframe_points])for fc in mat.node_tree.animation_data.action.fcurves]))
 return hashlib.sha256(json.dumps(sorted(rows)).encode()).hexdigest()
def mesh_signature(mesh):
 return hashlib.sha256(json.dumps(dict(vertices=[tuple(v.co)for v in mesh.vertices],polygons=[tuple(f.vertices)for f in mesh.polygons],uvs={u.name:[tuple(v.uv)for v in u.data]for u in mesh.uv_layers})).encode()).hexdigest()
anim_before=anim_signature()
chair_world=[list(row)for row in chair.matrix_world]
with bpy.data.libraries.load(str(source),link=False) as (fr,to):
 to.objects=['Cadeira do Dery']
original=to.objects[0]
mesh_sha=mesh_signature(original.data)
chair.data=original.data
assert [list(row)for row in chair.matrix_world]==chair_world
bpy.data.objects.remove(original,do_unlink=True)
removed=[]
for obj in list(s.objects):
 if obj.name.startswith(('Test | fitted armrest','Test | armrest post')):
  removed.append(obj.name);bpy.data.objects.remove(obj,do_unlink=True)
assert len(removed)==6,removed
assert anim_signature()==anim_before
s['Test | chair revision']='Original chair restored; all avatar, facial and camera keyframes preserved exactly.'
for image in bpy.data.images:
 if image.source=='FILE'and image.filepath and not image.packed_file:image.filepath=bpy.path.abspath(image.filepath)
bpy.ops.file.pack_all();bpy.ops.file.make_paths_relative()
dest=P/'output/Dery_Atuacao_Cadeira_Original.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
assert hashlib.sha256(old.read_bytes()).hexdigest()==old_sha
assert mesh_signature(chair.data)==mesh_sha
report=dict(original_test_unchanged=True,approved_animation_preserved_exactly=True,animation_signature=anim_before,chair_mesh_uvs_match_original=True,chair_transform_unchanged=True,chair_mesh_sha256=mesh_sha,removed_objects=removed,avatar_mesh_changed=False,hand_pose_changed=False,duration=8,frames=240,fps=30)
(P/'validacao_cadeira_original.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('CHAIR_RESTORED',json.dumps(report),flush=True)
s.render.engine='CYCLES';s.cycles.samples=1;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
for frame in [1,91]:
 s.frame_set(frame);s.render.filepath=str(C/f'pose_{frame:03d}.png');bpy.ops.render.render(write_still=True)
