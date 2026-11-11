"""Reusable PS1 bedroom assembled from the user's actual 3D library."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib,random,sys
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
import numpy as np

P=Path(__file__).resolve().parent;ROOT=P.parents[2]
BANK=ROOT/'assets/biblioteca_psx/originais/Banco 3D para vídeos'
OFFICE=BANK/'OFFICE/OFFICE';HOUSE=BANK/'House/House';KITCHEN=BANK/'PSX Kitchen Props Pack/PSX Kitchen Props Pack'
LP=BANK/'LowPolyAssetPack_Free/LowPolyAssetPack_Free'
WORK=Path('/workspace/attachments/quarto_gamer_v2');WORK.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;room=bpy.data.collections.new('Massacote | quarto gamer do banco');scene.collection.children.link(room)
sources=[];placements=[];random.seed(18)

def move_collection(obj):
    for c in list(obj.users_collection):c.objects.unlink(obj)
    room.objects.link(obj)
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def track(source,objects):
    sources.append({'file':str(source.relative_to(BANK)),'sha256':digest(source),'objects':[o.name for o in objects]})
    for o in objects:o['Fonte banco 3D']=str(source.relative_to(BANK))

def isolate(objects):
    meshes=[o for o in objects if o.type=='MESH']
    for o in meshes:
        matrix=o.matrix_world.copy();o.parent=None;o.matrix_world=matrix;move_collection(o)
    for o in objects:
        if o.type!='MESH':bpy.data.objects.remove(o,do_unlink=True)
    return meshes
def normalize(objects,name,location,axis=0,size=1.,rotation=0):
    points=[o.matrix_world@Vector(c)for o in objects for c in o.bound_box]
    lo=Vector(tuple(min(v[i]for v in points)for i in range(3)));hi=Vector(tuple(max(v[i]for v in points)for i in range(3)))
    center=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z));scale=size/max(1e-6,hi[axis]-lo[axis])
    transform=Matrix.Translation(Vector(location))@Matrix.Rotation(rotation,4,'Z')@Matrix.Scale(scale,4)@Matrix.Translation(-center)
    for i,o in enumerate(objects):
        world=o.matrix_world.copy();o.data=o.data.copy();o.data.transform(transform@world);o.matrix_world=Matrix.Identity(4)
        o.name=name if len(objects)==1 else name+f' | {i+1}'
        for f in o.data.polygons:f.use_smooth=False
        o.data.update()
    placements.append({'name':name,'location':location,'reference_size':size,'rotation_degrees':math.degrees(rotation)})
    return objects

def glb(source,name,loc,axis=0,size=1.,rotation=0):
    before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(source))
    objects=isolate(list(set(bpy.data.objects)-before));track(source,objects)
    return normalize(objects,name,loc,axis,size,rotation)
def office(rel,name,loc,axis=0,size=1.,rotation=0):return glb(OFFICE/rel,name,loc,axis,size,rotation)

def append_lp(rel,objname,name,loc,axis=0,size=1.,rotation=0):
    source=LP/'FBX and Blend Files'/rel
    with bpy.data.libraries.load(str(source),link=False)as(src,dst):dst.objects=[objname]
    objects=[]
    for o in dst.objects:
        if o is not None:scene.collection.objects.link(o);objects.append(o)
    objects=isolate(objects);track(source,objects)
    palette=LP/'TextureMap/MasterMaterial1px.png'
    for o in objects:
        for mat in o.data.materials:
            if not mat or not mat.use_nodes:continue
            for n in mat.node_tree.nodes:
                if n.type=='TEX_IMAGE' and (not n.image or not n.image.has_data):n.image=bpy.data.images.load(str(palette),check_existing=True)
    return normalize(objects,name,loc,axis,size,rotation)

# Recover the real bed from House, not a newly modelled substitute.
before=set(bpy.data.objects);house_source=HOUSE/'Models/House.fbx'
bpy.ops.import_scene.fbx(filepath=str(house_source))
imported=list(set(bpy.data.objects)-before);bed=next(o for o in imported if o.name=='bed_02')
matrix=bed.matrix_world.copy();bed.parent=None;bed.matrix_world=matrix;move_collection(bed)
for o in imported:
    if o!=bed:bpy.data.objects.remove(o,do_unlink=True)
track(house_source,[bed]);normalize([bed],'Cama | House bed_02',(1.83,-.62,.03),1,1.32,math.pi/2)
# Relink FBX image paths by the actual accompanying texture basenames.
textures={p.name.lower():p for p in (HOUSE/'Textures').iterdir()if p.is_file()}
for mat in bed.data.materials:
    if not mat or not mat.use_nodes:continue
    for n in mat.node_tree.nodes:
        if n.type=='TEX_IMAGE' and n.image:
            key=Path(n.image.filepath.replace('\\','/')).name.lower()
            if key in textures and not n.image.has_data:n.image.filepath=str(textures[key]);n.image.reload()
    # House's FBX connects a different bed image as opacity. The closed bed
    # geometry is opaque; do not cut away the mattress using that color map.
    bs=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if bs:
        for link in list(bs.inputs['Alpha'].links):mat.node_tree.links.remove(link)
        bs.inputs['Alpha'].default_value=1

desk=office('desks/desk1_weathered.glb','Mesa principal | madeira gasta',(-1.12,.74,0),2,.77)
office('desks/desk2.glb','Mesa lateral | retorno em L',(-2.08,-.69,0),2,.77,math.pi/2)
chair=office('chairs/office_chair_fancy.glb','Cadeira do Dery',(.36,.52,0),2,1.10)
monitor=office('computers/computer_monitor.glb','Monitor CRT | computador',(-1.25,.78,.772),2,.53)
office('computers/computer_keyboard.glb','Teclado',(-1.25,.30,.782),0,.50)
office('computers/computer_mouse.glb','Mouse',(-.86,.32,.782),0,.064)
office('computers/computer_tower.glb','Gabinete bege',(-2.03,-.08,.772),2,.48)
office('extras/circular_desklamp.glb','Luminária da mesa',(-.40,1.04,.772),2,.42,math.radians(-25))
office('extras/mug.glb','Caneca na mesa',(-.58,.47,.782),2,.108,math.radians(-12))
bookcase=office('book_things/book_case.glb','Estante de jogos',(.81,1.97,0),2,1.92)
office('book_things/book_case_small.glb','Móvel da TV',(1.98,1.26,0),2,.67)
tv=office('computers/TV.glb','TV de tubo',(1.98,1.22,.671),2,.63)
office('extras/wall_clock.glb','Relógio de parede',(-1.98,2.075,2.16),0,.32)
office('book_things/books.glb','Livros e revistas',(.46,1.94,1.50),0,.40)
office('book_things/books_alt2.glb','Manuais de jogos',(.60,1.94,.18),0,.38)

games='Technology Props/Games Consoles/Free_Mesh_GamesConsoles_Mutliple.blend'
audio='Technology Props/Audio Equipment/Free_Mesh_Audio_Equipment.blend'
misc='Technology Props/Misc Tech Props/Free_Mesh_MiscTechProps.blend'
append_lp(games,'Mesh_GameConsole_01','Console retrô | estante',(.62,1.94,1.08),0,.43)
append_lp(games,'Mesh_GameConsole_03','Segundo console',(.58,1.94,.58),0,.38)
append_lp(games,'Mesh_GameConsoleController_01','Controle na cama',(1.72,-1.05,.47),0,.20,math.radians(-25))
append_lp(games,'Mesh_GameConsoleController_02','Controle da estante',(1.12,1.94,.58),0,.18,math.radians(12))
append_lp(audio,'Mesh_Radio_01','Rádio portátil',(-2.10,-.65,.78),0,.39,math.radians(-5))
append_lp(audio,'Mesh_Headphones_01','Fone de ouvido',(-.33,.30,.79),0,.23,math.radians(-15))
append_lp(audio,'Mesh_Speakers_01','Caixa de som esquerda',(-1.69,.78,.78),2,.25)
append_lp(audio,'Mesh_Speakers_01','Caixa de som direita',(-.78,.80,.78),2,.25)
append_lp(audio,'Mesh_CDStack_01','Pilha de CDs',(1.17,1.94,1.08),0,.20)
append_lp(misc,'Mesh_Cable_01','Cabo no chão',(-1.35,.10,.012),0,.75,math.radians(21))
append_lp(misc,'Mesh_AlarmClock_01','Despertador',(.95,1.80,1.93),0,.22)
for i in range(5):
    append_lp(games,'Mesh_GameConsoleGame_01',f'Caixa de jogo {i+1}',(.93+i*.105,1.94,1.50),0,.093,math.radians(random.uniform(-3,3)))
glb(KITCHEN/'glb/pizza_box_semi_close_with_pizza.glb','Pizza esquecida',(-2.05,-1.01,.78),0,.37,math.radians(12))
glb(KITCHEN/'glb/soda_bottle.glb','Garrafa na mesa',(-1.95,-.82,.81),2,.22)

def new_material(name,image=None,color=(1,1,1,1),emissive=False):
    mat=bpy.data.materials.new(name);mat.use_nodes=True;n=mat.node_tree.nodes;l=mat.node_tree.links;n.clear()
    output=n.new('ShaderNodeOutputMaterial');bs=n.new('ShaderNodeEmission'if emissive else'ShaderNodeBsdfPrincipled')
    if not emissive:bs.inputs['Roughness'].default_value=1;bs.inputs['Specular IOR Level'].default_value=0
    socket=bs.inputs['Color'if emissive else'Base Color'];socket.default_value=color
    if image:
        tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(image),check_existing=True);tex.interpolation='Closest'
        if color!=(1,1,1,1):
            mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=color;l.new(tex.outputs['Color'],mix.inputs[1]);l.new(mix.outputs[0],socket)
        else:l.new(tex.outputs['Color'],socket)
    l.new(bs.outputs[0],output.inputs['Surface']);mat['RoomEmissive']=emissive
    return mat

wood=new_material('Banco House | tábuas',HOUSE/'Textures/WoodPlanks.jpg',(.61,.50,.37,1))
plaster=new_material('Banco House | reboco azul',HOUSE/'Textures/PlasterWhite.jpg',(.17,.25,.43,1))
sidepaint=new_material('Banco House | reboco lateral',HOUSE/'Textures/PlasterWhite.jpg',(.48,.47,.49,1))
trim=new_material('Banco House | rodapés',HOUSE/'Textures/Wood_02.jpg',(.28,.20,.13,1))
rugmat=new_material('Banco Office | tapete',OFFICE/'textures/carpet.jpg',(.39,.27,.48,1))
black=new_material('Placa | carvão',None,(.019,.022,.03,1))
gold=new_material('Massacote | amarelo',None,(.83,.46,.035,1))

def mesh_obj(name,verts,faces,material):
    m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update();o=bpy.data.objects.new(name,m);room.objects.link(o);m.materials.append(material)
    return o
def grid(name,origin,uvec,vvec,nu,nv,material,tiles=(1,1)):
    origin=Vector(origin);uvec=Vector(uvec);vvec=Vector(vvec)
    verts=[origin+uvec*(i/nu)+vvec*(j/nv)for j in range(nv+1)for i in range(nu+1)]
    faces=[]
    for j in range(nv):
        for i in range(nu):
            k=j*(nu+1)+i;faces.extend([(k,k+1,k+nu+2),(k,k+nu+2,k+nu+1)])
    o=mesh_obj(name,verts,faces,material);uv=o.data.uv_layers.new(name='UVMap')
    for p in o.data.polygons:
        for li in p.loop_indices:
            idx=o.data.loops[li].vertex_index;uv.data[li].uv=((idx%(nu+1))/nu*tiles[0],(idx//(nu+1))/nv*tiles[1])
    return o
def cube(name,loc,scale,material):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);move_collection(o);o.data.materials.append(material)
    return o

grid('Piso de tábuas',(-2.6,-2.25,0),(5.2,0,0),(0,4.5,0),26,24,wood,(4,4))
grid('Parede do fundo',(-2.6,2.22,0),(5.2,0,0),(0,0,2.75),26,14,plaster,(3.2,1.7))
grid('Parede esquerda',(-2.59,-2.25,0),(0,4.47,0),(0,0,2.75),24,14,sidepaint,(2.8,1.7))
grid('Parede direita',(2.59,2.22,0),(0,-4.47,0),(0,0,2.75),24,14,sidepaint,(2.8,1.7))
ceiling_mat=new_material('Banco House | teto',HOUSE/'Textures/Ceiling.jpg',(.48,.50,.57,1))
ceiling=grid('Teto | interiores',(-2.6,-2.25,2.75),(0,4.5,0),(5.2,0,0),20,24,ceiling_mat,(3,3))
ceiling['Uso']='Visível nas câmeras de interior; oculto na visão geral de apresentação.'
cube('Rodapé fundo',(0,2.19,.055),(5.2,.05,.11),trim)
cube('Rodapé esquerdo',(-2.56,0,.055),(.05,4.45,.11),trim)
cube('Rodapé direito',(2.56,0,.055),(.05,4.45,.11),trim)
grid('Tapete gasto',(-1.30,-1.40,.022),(2.5,0,0),(0,1.7,0),12,9,rugmat,(3,2))

# Wall decals use library textures; branding reuses the approved existing M.
door_mat=new_material('Banco House | porta',HOUSE/'Textures/Door_02.png')
grid('Porta de madeira',(-2.575,-1.55,.06),(0,.88,0),(0,0,2.10),1,1,door_mat)
window_mat=new_material('Banco House | janela',HOUSE/'Textures/Windows.jpg',(.60,.72,.92,1))
grid('Janela', (2.575,.10,1.25),(0,-1.05,0),(0,0,1.12),1,1,window_mat)
for yy in (-.99,.14):cube('Moldura da janela',(2.55,yy,1.81),(.055,.05,1.22),trim)
for zz in (1.22,2.41):cube('Moldura da janela',(2.55,-.425,zz),(.055,1.17,.05),trim)

logo_source=ROOT/'assets/marca/massacote-games/logo.png'
logo=new_material('Marca aprovada | M',logo_source,emissive=True)
cube('Placa da marca',(-.38,2.17,2.03),(.68,.055,.68),black)
grid('M na parede',(-.695,2.135,1.715),(.63,0,0),(0,0,.63),1,1,logo)
for x in (-.735,-.025):cube('Detalhe amarelo da placa',(x,2.125,2.03),(.025,.02,.66),gold)
case_art=BANK/'Free_PSX_Case_Template/Example Art/ntsc_case_front.png'
artmat=new_material('Banco | arte de caixa PSX',case_art)
grid('Pôster de jogo',(-2.57,.15,1.35),(0,.60,0),(0,0,.68),1,1,artmat)

# UV-based screen fitting uses the actual atlas to find its 3D front plane.
def uv_point(obj,target):
    mesh=obj.data;mesh.calc_loop_triangles();uv=mesh.uv_layers.active
    for tri in mesh.loop_triangles:
        co=[Vector(uv.data[li].uv)for li in tri.loops];a,b,c=co
        denom=(b.y-c.y)*(a.x-c.x)+(c.x-b.x)*(a.y-c.y)
        if abs(denom)<1e-10:continue
        u=((b.y-c.y)*(target[0]-c.x)+(c.x-b.x)*(target[1]-c.y))/denom
        v=((c.y-a.y)*(target[0]-c.x)+(a.x-c.x)*(target[1]-c.y))/denom;w=1-u-v
        if min(u,v,w)>=-1e-5:
            pts=[obj.matrix_world@mesh.vertices[i].co for i in tri.vertices]
            return pts[0]*u+pts[1]*v+pts[2]*w,(pts[1]-pts[0]).cross(pts[2]-pts[0]).normalized()
    return None
o=monitor[0];uv_center=uv_point(o,(.25,.89))
if uv_center:
    point,norm=uv_center
    if abs(norm.z)<.4:
        angle=-math.pi/2-math.atan2(norm.y,norm.x);loc=Vector((-1.25,.78,.772))
        rot=Matrix.Translation(loc)@Matrix.Rotation(angle,4,'Z')@Matrix.Translation(-loc)
        o.data.transform(rot)
    corners=[uv_point(o,uv)for uv in[(.063,.810),(.438,.810),(.438,.963),(.063,.963)]]
    if all(corners):
        display=logo.copy();display.name='DISPLAY | PC | trocar mídia'
        screen=mesh_obj('Tela do PC | substituir por vídeo',[p+n*.0018 for p,n in corners],[(0,1,2,3)],display)
        uvl=screen.data.uv_layers.new(name='UVMap')
        for li,co in zip(screen.data.polygons[0].loop_indices,[(0,0),(1,0),(1,1),(0,1)]):uvl.data[li].uv=co
        screen['Uso']='Substituir o nó de imagem por gameplay mantendo este UV.'

tv_center=uv_point(tv[0],(.40,.30))
if tv_center:
    bb=[tv[0].matrix_world@Vector(c)for c in tv[0].bound_box]
    middle=Vector(tuple((min(p[i]for p in bb)+max(p[i]for p in bb))/2 for i in range(3)))
    front=tv_center[0]-middle
    angle=-math.pi/2-math.atan2(front.y,front.x);loc=Vector((1.98,1.22,.671))
    tv[0].data.transform(Matrix.Translation(loc)@Matrix.Rotation(angle,4,'Z')@Matrix.Translation(-loc))

def rest_on(obj,supports,initial_z):
    verts=[];tris=[]
    for support in supports:
        support.data.calc_loop_triangles();offset=len(verts);verts.extend(support.matrix_world@v.co for v in support.data.vertices)
        tris.extend(tuple(offset+i for i in t.vertices)for t in support.data.loop_triangles)
    tree=BVHTree.FromPolygons(verts,tris,all_triangles=True)
    points=[obj.matrix_world@Vector(c)for c in obj.bound_box];x=(min(p.x for p in points)+max(p.x for p in points))/2;y=(min(p.y for p in points)+max(p.y for p in points))/2
    hit=tree.ray_cast(Vector((x,y,initial_z+.10)),Vector((0,0,-1)),1.5)
    if hit[0]is not None:
        dz=hit[0].z-min(p.z for p in points)+.002;obj.data.transform(Matrix.Translation((0,0,dz)))
        obj['Altura apoiada']=round(hit[0].z,5)
for obj in list(room.objects):
    if obj.type!='MESH':continue
    if obj.name.startswith(('Console retrô','Segundo console','Controle da estante','Pilha de CDs','Livros e revistas','Manuais de jogos','Caixa de jogo')):
        rest_on(obj,bookcase,min((obj.matrix_world@Vector(c)).z for c in obj.bound_box))
    elif obj.name=='Controle na cama':rest_on(obj,[bed],.85)

# Bake colored diffuse lighting into mesh corners, as a PS1 Gouraud scene.
lights=[((-1.1,-.1,2.55),(1.0,.70,.40),3.2),((1.8,1.25,2.35),(.53,.25,1.0),3.4),((2.35,-.5,1.85),(.24,.46,.86),1.7),((-1.22,.63,1.13),(.31,.74,1.0),.50),((-.4,1.04,1.11),(1.0,.56,.20),.65)]
for i,(pos,col,power)in enumerate(lights):
    data=bpy.data.lights.new(f'Luz {i+1} | referência para personagens','POINT');data.energy=power*70;data.color=col;data.shadow_soft_size=.35
    light=bpy.data.objects.new(data.name,data);room.objects.link(light);light.location=pos

meshes=[o for o in room.objects if o.type=='MESH']
positions=[];triangles=[]
for o in meshes:
    o.data.calc_loop_triangles();offset=len(positions);positions.extend(o.matrix_world@v.co for v in o.data.vertices)
    triangles.extend(tuple(offset+i for i in t.vertices)for t in o.data.loop_triangles)
bvh=BVHTree.FromPolygons(positions,triangles,all_triangles=True)
for o in meshes:
    attr=o.data.color_attributes.get('PS1Light')or o.data.color_attributes.new(name='PS1Light',type='FLOAT_COLOR',domain='CORNER')
    for face in o.data.polygons:
        normal=(o.matrix_world.to_3x3()@face.normal).normalized()
        for li in face.loop_indices:
            p=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co
            color=np.array([.22,.23,.29])
            for pos,col,power in lights:
                vec=Vector(pos)-p;distance=vec.length;direction=vec.normalized();cosine=max(0,normal.dot(direction))
                hit=bvh.ray_cast(p+normal*.004+direction*.003,direction,max(0,distance-.025))
                visibility=.18 if hit[0]is not None else 1.0
                color+=np.array(col)*power/(1+distance*distance)*(.08+.92*cosine)*visibility
            attr.data[li].color=(*np.clip(color,.08,1.3),1)

converted=set()
for o in meshes:
    for mat in o.data.materials:
        if not mat or mat in converted:continue
        converted.add(mat)
        if mat.get('RoomEmissive'):continue
        mat.use_nodes=True;n=mat.node_tree.nodes;l=mat.node_tree.links
        bs=next((x for x in n if x.type=='BSDF_PRINCIPLED'),None)
        if not bs:continue
        base=bs.inputs['Base Color'];color=base.links[0].from_socket if base.is_linked else tuple(base.default_value)
        alpha=bs.inputs['Alpha'];a=alpha.links[0].from_socket if alpha.is_linked else alpha.default_value
        light=n.new('ShaderNodeAttribute');light.attribute_name='PS1Light'
        mul=n.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1
        if isinstance(color,tuple):mul.inputs[1].default_value=color
        else:l.new(color,mul.inputs[1])
        l.new(light.outputs['Color'],mul.inputs[2]);em=n.new('ShaderNodeEmission');l.new(mul.outputs[0],em.inputs[0])
        output=next(x for x in n if x.type=='OUTPUT_MATERIAL')
        if not isinstance(a,(float,int))or a<.999:
            trans=n.new('ShaderNodeBsdfTransparent');cut=n.new('ShaderNodeMath');cut.operation='GREATER_THAN';cut.inputs[1].default_value=.5
            if isinstance(a,(float,int)):cut.inputs[0].default_value=a
            else:l.new(a,cut.inputs[0])
            mix=n.new('ShaderNodeMixShader');l.new(cut.outputs[0],mix.inputs[0]);l.new(trans.outputs[0],mix.inputs[1]);l.new(em.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],output.inputs['Surface'])
        else:l.new(em.outputs[0],output.inputs['Surface'])
        for x in n:
            if x.type=='TEX_IMAGE':x.interpolation='Closest'

anchor=bpy.data.objects.new('DERY | posição de referência',None);room.objects.link(anchor);anchor.location=(.36,.52,.46);anchor.empty_display_type='ARROWS';anchor.empty_display_size=.25
anchor['Uso']='Referência do assento; ajustar a pose avaliada do rig original ao reutilizar. Nenhum avatar foi modificado.'

def camera(name,loc,target,lens):
    data=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,data);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();data.lens=lens;data.sensor_fit='VERTICAL';data.sensor_height=24
    return o
hero=camera('01 | Quarto completo',(1.90,-4.70,2.80),(-.05,.12,1.00),32)
vertical=camera('02 | Enquadramento para shorts',(2.20,-3.7,1.76),(-.15,.86,1.31),30)
detail=camera('03 | Computador e mesa',(-.05,-2.8,1.76),(-1.12,.65,1.02),34)
scene.render.engine='BLENDER_EEVEE_NEXT';scene.eevee.taa_render_samples=1;scene.render.film_transparent=False
scene.render.image_settings.file_format='PNG';scene.world=bpy.data.worlds.new('Ambiente');scene.world.color=(.018,.019,.026)
scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
scene.render.fps=24;scene.frame_start=1;scene.frame_end=1

# Fit the real furniture, including the full bed, in the overview.
from bpy_extras.object_utils import world_to_camera_view
scene.render.resolution_x=480;scene.render.resolution_y=270
important=desk+bookcase+[bed]+chair+[bpy.data.objects['Placa da marca']]
for iteration in range(12):
    bpy.context.view_layer.update()
    projected=[world_to_camera_view(scene,hero,o.matrix_world@Vector(c))for o in important for c in o.bound_box]
    if min(p.x for p in projected)>.04 and max(p.x for p in projected)<.96 and min(p.y for p in projected)>.04 and max(p.y for p in projected)<.96:break
    hero.data.lens*=.94

sys.path.insert(0,str(ROOT/'assets/personagens/dery'))
from ps1_precision import add_safe_precision
viewgroups={}
for cam,w,h in [(hero,480,270),(vertical,270,480),(detail,480,270)]:
    mod=add_safe_precision(meshes[0],cam,width=w//2,height=h//2,aspect=w/h);g=mod.node_group;g.name='Quarto | precisão PS1 | '+cam.name;viewgroups[cam.name]=g;meshes[0].modifiers.remove(mod)
for o in meshes:
    attr=o.data.attributes.get('PS1SnapWeight')or o.data.attributes.new(name='PS1SnapWeight',type='FLOAT',domain='POINT')
    solid_prop='Fonte banco 3D'in o and not o.name.startswith(('Monitor CRT','Teclado','Mouse','Caneca'))
    for item in attr.data:item.value=.35 if solid_prop else 0
    mod=o.modifiers.new('PS1 | bordas por câmera','NODES');mod.node_group=viewgroups[hero.name]

def choose(cam,w,h):
    scene.camera=cam;scene.render.resolution_x=w;scene.render.resolution_y=h;scene.render.resolution_percentage=100
    ceiling.hide_render=(cam==hero)
    for o in meshes:o.modifiers['PS1 | bordas por câmera'].node_group=viewgroups[cam.name]

for cam,w,h,name in [(hero,480,270,'Quarto_Completo'),(vertical,270,480,'Quarto_9x16'),(detail,480,270,'Mesa_CRT')]:
    choose(cam,w,h);scene.render.filepath=str(WORK/(name+'_base.png'));bpy.ops.render.render(write_still=True)

choose(hero,480,270)
scene['PS1 | visual']='Closest, luz Gouraud por vértice, bordas com precisão de câmera, RGB555/dither no script de saída.'
scene['PS1 | trocar câmera']='Usar os grupos Quarto | precisão PS1 da câmera correspondente nos modificadores da coleção.'
scene['PS1 | conteúdo']='Cenário novo separado; não altera o modelo atual do Dery nem os vídeos anteriores.'
bpy.data.orphans_purge(do_recursive=True)
bpy.ops.file.pack_all()
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.shading.type='MATERIAL';area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Quarto_Gamer_Banco_PS1.blend'),compress=True)
record={'bank_source':'assets/biblioteca_psx/recebimento.json','sources':sources,'placements':placements,'mesh_objects':len(meshes),'triangles':sum(len(o.data.loop_triangles)for o in meshes),'packed_images':[(im.name,list(im.size),bool(im.packed_file))for im in bpy.data.images if im.type=='IMAGE'],'lighting':'colored diffuse baked into PS1Light corners, ambient + visibility rays','render_base_resolutions':[[480,270],[270,480]],'geometry_precision':'shared seam-safe screen-space group per camera','new_video_renders':0,'character_modified':False,'approved_by_user':False}
(P/'fontes_e_montagem.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('ROOM_SAVED',record['mesh_objects'],record['triangles'],len(record['packed_images']),flush=True)
