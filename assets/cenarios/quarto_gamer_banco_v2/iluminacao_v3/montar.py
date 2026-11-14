from pathlib import Path
import bpy,sys,json,hashlib
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;R=next(p for p in P.parents if(p/'AGENTS.md').exists());C=Path('/workspace/attachments/quarto_luz_v3');C.mkdir(exist_ok=True);SOURCE=R/'assets/personagens/dery/atuacao_sentada_teste_v1/output/Dery_Atuacao_Apoio_Real.blend';source_sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();a=bpy.data.objects['DERY | animated character'];rig=a.parent
sys.path.insert(0,str(P));from aplicar import apply
meshes={o.name:hashlib.sha256(np.array([v.co[:]for v in o.data.vertices],np.float32).tobytes()).hexdigest()for o in s.objects if o.type=='MESH'};uvs={layer.name:hashlib.sha256(np.array([x.uv[:]for x in layer.data],np.float32).tobytes()).hexdigest()for layer in a.data.uv_layers};bones={p.name:np.array(p.matrix)for p in rig.pose.bones};camera=s.camera;camera_matrix=camera.matrix_world.copy();camera_lens=camera.data.lens
s.render.engine='CYCLES';s.cycles.samples=1;s.cycles.use_denoising=False;s.render.use_persistent_data=True;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=768;s.render.resolution_y=432;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.use_sequencer=False;s.render.use_compositing=False
# Keep movie decoding out of this lighting study; the display is not in the
# front character shot. Media is composed cleanly for the detail preview below.
screen=bpy.data.objects['Tela do PC | substituir por vídeo'];screen_nodes=[n for n in screen.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE'];original_screen=[n.image for n in screen_nodes];placeholder=bpy.data.images.new('Somente previa | tela neutra',width=1,height=1);placeholder.generated_color=(.035,.045,.07,1)
for n in screen_nodes:n.image=placeholder
s.render.filepath=str(C/'antes.png');bpy.ops.render.render(write_still=True)
result=apply(s);s.frame_set(1);bpy.context.view_layer.update()
for o in s.objects:
 if o.type=='MESH'and o.name in meshes:assert meshes[o.name]==hashlib.sha256(np.array([v.co[:]for v in o.data.vertices],np.float32).tobytes()).hexdigest(),o.name
assert all(uvs[layer.name]==hashlib.sha256(np.array([x.uv[:]for x in layer.data],np.float32).tobytes()).hexdigest()for layer in a.data.uv_layers);assert all(np.allclose(bones[p.name],np.array(p.matrix),atol=1e-6)for p in rig.pose.bones);assert not bpy.data.objects.get('Fone de ouvido')
# Preserve original movie dependencies in the editable file, with packed textures.
for n,image in zip(screen_nodes,original_screen):n.image=image
for image in bpy.data.images:
 if image.source in['FILE','MOVIE']and image.filepath and not image.packed_file:image.filepath=bpy.path.abspath(image.filepath)
s['LightingV3 | source']=str(SOURCE.relative_to(R));bpy.ops.file.pack_all();bpy.ops.file.make_paths_relative();dest=P/'Dery_Quarto_Luz_v3_Sem_Fone.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
for n in screen_nodes:n.image=placeholder
s.render.filepath=str(C/'depois.png');bpy.ops.render.render(write_still=True)
# A second real camera angle confirms the desk/headphones removal.
camera.animation_data_clear();camera.data.animation_data_clear();preset=bpy.data.objects['TESTE | jogo no CRT'];camera.matrix_world=preset.matrix_world.copy();camera.data.lens=preset.data.lens;s.render.filepath=str(C/'mesa.png');bpy.ops.render.render(write_still=True)
def psx(path):
 im=Image.open(path).convert('RGB');x=np.asarray(im,np.float32);h,w=x.shape[:2];b=(np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]],np.float32)+.5)/16-.5;noise=np.tile(b,((h+3)//4,(w+3)//4))[:h,:w,None]*5;return Image.fromarray(np.uint8(np.clip(np.floor((x+noise)/8+.5),0,31)*255/31))
old=psx(C/'antes.png');new=psx(C/'depois.png');new.resize((1920,1080),Image.Resampling.NEAREST).save(P/'Previa_Luz_16x9.png');new.crop((263,0,506,432)).resize((1080,1920),Image.Resampling.NEAREST).save(P/'Previa_Luz_9x16.png');psx(C/'mesa.png').resize((1920,1080),Image.Resampling.NEAREST).save(P/'Previa_Mesa_Sem_Fone.png');sheet=Image.new('RGB',(1536,464),(22,23,28));sheet.paste(old,(0,0));sheet.paste(new,(768,0));d=ImageDraw.Draw(sheet);d.text((15,442),'ANTES',fill='white');d.text((783,442),'LUZ NOVA / SEM FONE',fill='white');sheet.save(P/'Antes_Depois.png')
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_sha;result.update(source=str(SOURCE.relative_to(R)),source_sha256=source_sha,source_unchanged=True,avatar_geometry_unchanged=True,avatar_uvs_unchanged=True,pose_and_thigh_contacts_unchanged=True,furniture_geometry_unchanged=True,removed_headphones_only=True,existing_videos_not_rerendered=True,preview_frames=3,face_texture_system_preserved=True);(P/'alteracoes.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('ROOM_LIGHTING_V3_READY',flush=True)
