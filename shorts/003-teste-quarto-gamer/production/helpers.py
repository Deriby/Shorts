import bpy,math
from mathutils import Vector
import character as C
ASSETS=None
lights=[]
records={}

def empty(name,loc=(0,0,0),parent=None): return C.empty(name,loc,parent)

def material(name,color=(1,1,1),atlas=None,tile=None,emission=1,lit=True,alpha=1):
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial'); em=nt.nodes.new('ShaderNodeEmission')
    em.inputs['Strength'].default_value=emission
    if atlas:
        tex=nt.nodes.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(str(ASSETS/atlas),check_existing=True); tex.interpolation='Closest'
        colorout=tex.outputs['Color']
    else:
        rgb=nt.nodes.new('ShaderNodeRGB'); rgb.outputs[0].default_value=(*color,1); colorout=rgb.outputs[0]
    nt.links.new(colorout,em.inputs['Color'])
    surface=em.outputs[0]
    if lit:
        shader=nt.nodes.new('ShaderNodeBsdfPrincipled')
        shader.inputs['Roughness'].default_value=.83
        shader.inputs['Specular IOR Level'].default_value=.20
        nt.links.new(colorout,shader.inputs['Base Color'])
        surface=shader.outputs[0]
    if alpha<1:
        tr=nt.nodes.new('ShaderNodeBsdfTransparent'); mix=nt.nodes.new('ShaderNodeMixShader'); mix.inputs[0].default_value=alpha
        nt.links.new(tr.outputs[0],mix.inputs[1]); nt.links.new(surface,mix.inputs[2]); nt.links.new(mix.outputs[0],out.inputs[0])
    else: nt.links.new(surface,out.inputs[0])
    m['tile']=tile or [0,0,1,1]
    return m

def uv_faces(o,tile=None):
    tile=tile or o.data.materials[0].get('tile',[0,0,1,1]); u0,v0,u1,v1=tile
    layer=o.data.uv_layers.get('UVMap') or o.data.uv_layers.new(name='UVMap')
    for p in o.data.polygons:
        for k,li in enumerate(p.loop_indices):
            layer.data[li].uv=[(u0,v0),(u1,v0),(u1,v1),(u0,v1)][k%4]

def box(name,loc,size,mat,parent=None,bevel=0):
    x,y,z=[v/2 for v in size]
    v=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    o=mesh(name,v,faces,mat,parent); o.location=loc; uv_faces(o)
    if bevel:
        b=o.modifiers.new('one-cut game bevel','BEVEL'); b.width=bevel; b.segments=1
    return o

def mesh(name,v,f,mat,parent=None,uv=None): return C.mesh(name,v,f,mat,uv,parent)

def quad(name,verts,mat,parent=None):
    u0,v0,u1,v1=mat.get('tile',[0,0,1,1])
    return mesh(name,verts,[(0,1,2,3)],mat,parent,[(u0,v0),(u1,v0),(u1,v1),(u0,v1)])

def cylinder(name,loc,radius,depth,mat,parent=None,vertices=10,rot=(0,0,0)):
    n=vertices
    v=[(radius*math.cos(i*math.tau/n),radius*math.sin(i*math.tau/n),z)for z in [-depth/2,depth/2]for i in range(n)]
    faces=[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)]+[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]
    o=mesh(name,v,faces,mat,parent); o.location=loc; o.rotation_euler=rot; return o

def beam(name,a,b,width,mat,parent=None,depth=None):
    a,b=Vector(a),Vector(b); o=box(name,(a+b)/2,(width,depth or width,(b-a).length),mat,parent)
    o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler(); return o

def torus(name,loc,major,minor,mat,parent=None,rot=(0,0,0),segments=24):
    bpy.ops.mesh.primitive_torus_add(major_segments=segments,minor_segments=6,major_radius=major,minor_radius=minor)
    o=bpy.context.object; o.name=name; o.parent=parent; o.location=loc; o.rotation_euler=rot; o.data.materials.append(mat); return o

def sphere(name,loc,scale,mat,parent=None,segments=24,rings=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,radius=1)
    o=bpy.context.object; o.name=name; o.parent=parent; o.location=loc; o.scale=scale; o.data.materials.append(mat); return o

def blob(parent,loc,scale):
    v=[(math.cos(i*math.tau/18)*scale[0]+loc[0],math.sin(i*math.tau/18)*scale[1]+loc[1],loc[2])for i in range(18)]
    return mesh('baked-style ground shadow',v,[tuple(range(18))],shadow,parent)

def record(obj,prop,frame):
    owner=obj.id_data
    path=obj.path_from_id(prop)
    value=getattr(obj,prop)
    try: values=tuple(float(x) for x in value)
    except TypeError: values=(float(value),)
    entry=records.setdefault((owner,path),[])
    if entry and entry[-1][0]==frame: entry[-1]=(frame,values)
    else: entry.append((frame,values))

def commit_curves():
    actions={}
    total=0
    for (owner,path),entries in records.items():
        if owner not in actions:
            action=bpy.data.actions.new('003 | '+owner.name)
            owner.animation_data_create().action=action; actions[owner]=action
        for i in range(len(entries[0][1])):
            selected=[]; prev=None
            for frame,values in entries:
                value=values[i]
                if prev is None or abs(value-prev)>1e-7:
                    selected.extend([frame,value]); prev=value
            fc=actions[owner].fcurves.new(path,index=i)
            fc.keyframe_points.add(len(selected)//2)
            fc.keyframe_points.foreach_set('co',selected)
            for point in fc.keyframe_points: point.interpolation='CONSTANT'
            fc.update(); total+=len(selected)//2
    print('BULK_KEYS',total,'actions',len(actions),flush=True)
