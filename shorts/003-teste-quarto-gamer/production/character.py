"""Original Dery rig, original UV preserved, projected expression PNGs."""
from pathlib import Path
import bpy, math
from mathutils import Vector, Quaternion, Matrix
s=rig=body=head=hero=ASSETS=None
expressions={}
rest={}
clips={}
moving_bones=[]
RECORD=None
def empty(name,loc=(0,0,0),parent=None):
    o=bpy.data.objects.new(name,None)
    s.collection.objects.link(o)
    o.location=loc
    o.parent=parent
    return o

def mesh(name,verts,faces,material,uv=None,parent=None):
    me=bpy.data.meshes.new(name)
    me.from_pydata(verts,[],faces)
    me.update()
    o=bpy.data.objects.new(name,me)
    s.collection.objects.link(o)
    o.data.materials.append(material)
    o.parent=parent
    if uv:
        layer=me.uv_layers.new(name='UVMap')
        for p in me.polygons:
            for li in p.loop_indices:
                layer.data[li].uv=uv[me.loops[li].vertex_index]
    return o

def emat(name,color,strength=1):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    nt=m.node_tree
    nt.nodes.clear()
    e=nt.nodes.new('ShaderNodeEmission')
    e.inputs['Color'].default_value=(*color,1)
    e.inputs['Strength'].default_value=strength
    out=nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(e.outputs[0],out.inputs['Surface'])
    return m,e

def smooth(x):
    x=max(0,min(1,x))
    return x*x*(3-2*x)

def vlerp(a,b,u):
    return Vector(a).lerp(Vector(b),max(0,min(1,u)))

def character_material(name,face=False):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    nt=m.node_tree
    nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial')
    emission=nt.nodes.new('ShaderNodeEmission')
    uv=nt.nodes.new('ShaderNodeUVMap')
    uv.uv_map=body.data.uv_layers[0].name if not face else head.data.uv_layers[0].name
    tex=nt.nodes.new('ShaderNodeTexImage')
    tex.image=bpy.data.images.load(str(ASSETS/'Dery_Material_Diffuse.png'),check_existing=True)
    tex.interpolation='Closest'
    nt.links.new(uv.outputs[0],tex.inputs['Vector'])
    color=tex.outputs['Color']
    weights={}
    if face:
        p_uv=nt.nodes.new('ShaderNodeUVMap')
        p_uv.uv_map='FaceProjection'
        masknode=nt.nodes.new('ShaderNodeVertexColor')
        masknode.layer_name='ExpressionMask'
        for label in ['susto','panico','derrota']:
            exp=nt.nodes.new('ShaderNodeTexImage')
            exp.name='PNG | '+label
            exp.image=bpy.data.images.load(str(ASSETS/('expressao_'+label+'.png')),check_existing=True)
            exp.interpolation='Closest'
            nt.links.new(p_uv.outputs[0],exp.inputs['Vector'])
            weight=nt.nodes.new('ShaderNodeValue')
            weight.name='EXPRESSION | '+label
            weight.outputs[0].default_value=0
            mul=nt.nodes.new('ShaderNodeMath'); mul.operation='MULTIPLY'
            nt.links.new(masknode.outputs['Color'],mul.inputs[0])
            nt.links.new(weight.outputs[0],mul.inputs[1])
            alpha=nt.nodes.new('ShaderNodeMath'); alpha.operation='MULTIPLY'
            nt.links.new(mul.outputs[0],alpha.inputs[0])
            nt.links.new(exp.outputs['Alpha'],alpha.inputs[1])
            blend=nt.nodes.new('ShaderNodeMixRGB')
            nt.links.new(alpha.outputs[0],blend.inputs[0])
            nt.links.new(color,blend.inputs[1])
            nt.links.new(exp.outputs['Color'],blend.inputs[2])
            color=blend.outputs[0]
            weights[label]=weight.outputs[0]
    # Directional, normal-based game lighting without stochastic raytracing noise.
    geom=nt.nodes.new('ShaderNodeNewGeometry')
    dot=nt.nodes.new('ShaderNodeVectorMath'); dot.operation='DOT_PRODUCT'
    dot.inputs[1].default_value=(.25,-.65,.72)
    nt.links.new(geom.outputs['Normal'],dot.inputs[0])
    level=nt.nodes.new('ShaderNodeMath'); level.operation='MULTIPLY_ADD'
    level.inputs[1].default_value=.25
    level.inputs[2].default_value=.80
    nt.links.new(dot.outputs['Value'],level.inputs[0])
    shaded=nt.nodes.new('ShaderNodeMixRGB'); shaded.blend_type='MULTIPLY'; shaded.inputs[0].default_value=1
    nt.links.new(color,shaded.inputs[1])
    nt.links.new(level.outputs[0],shaded.inputs[2])
    nt.links.new(shaded.outputs[0],emission.inputs['Color'])
    nt.links.new(emission.outputs[0],out.inputs['Surface'])
    return m,weights

def delta(name,axis,angle):
    q=Quaternion(axis,angle)
    rig.pose.bones[name].rotation_quaternion=rest[name].inverted()@q@rest[name]

def transform_key(o,f):
    for path in ['location','rotation_euler','scale']:
        if RECORD: RECORD(o,path,f)
        else: o.keyframe_insert(data_path=path,frame=f)

def setup(assets):
    global s,rig,body,head,hero,ASSETS,expressions,rest,bm,hm
    ASSETS=Path(assets)
    s=bpy.context.scene
    rig=bpy.data.objects['Dery_Rig']
    body=bpy.data.objects['Dery_Body']
    head=bpy.data.objects['Dery_Head']
    rig.animation_data_clear()
    for b in rig.pose.bones:
        b.matrix_basis=Matrix.Identity(4)
        b.rotation_mode='QUATERNION'
    hero=empty('DERY | world motion')
    rig.parent=hero
    rig.location=(0,0,0)
    rig.rotation_euler=(0,0,0)
    for o in [body,head]:
        o.parent=rig
        o.matrix_parent_inverse=Matrix.Identity(4)

    # Preserve original UV map and actual supplied geometry; add a second facial UV.
    head.data.color_attributes.new(name='ExpressionMask',type='FLOAT_COLOR',domain='CORNER')
    head.data.uv_layers.new(name='FaceProjection')
    # Adding mesh attributes can invalidate previously cached RNA layer references.
    projection=head.data.uv_layers['FaceProjection']
    mask=head.data.color_attributes['ExpressionMask']
    for poly in head.data.polygons:
        for li in poly.loop_indices:
            v=head.data.vertices[head.data.loops[li].vertex_index]
            x,y,z=v.co
            projection.data[li].uv=((x+.23)/.46,(z-1.37)/.46)
            # Restrict projected reaction PNGs to the eyes. The jaw, beard and
            # chin always use the supplied atlas, avoiding projection seams.
            w=smooth((.110-abs(x))/.028)*smooth((z-1.548)/.018)*smooth((1.647-z)/.025)*smooth((.018-y)/.045)
            mask.data[li].color=(w,w,w,1)


    def character_material(name,face=False):
        m=bpy.data.materials.new(name)
        m.use_nodes=True
        nt=m.node_tree
        nt.nodes.clear()
        out=nt.nodes.new('ShaderNodeOutputMaterial')
        emission=nt.nodes.new('ShaderNodeEmission')
        uv=nt.nodes.new('ShaderNodeUVMap')
        uv.uv_map=body.data.uv_layers[0].name if not face else head.data.uv_layers[0].name
        tex=nt.nodes.new('ShaderNodeTexImage')
        tex.image=bpy.data.images.load(str(ASSETS/'Dery_Material_Diffuse.png'),check_existing=True)
        tex.interpolation='Closest'
        nt.links.new(uv.outputs[0],tex.inputs['Vector'])
        color=tex.outputs['Color']
        weights={}
        if face:
            p_uv=nt.nodes.new('ShaderNodeUVMap')
            p_uv.uv_map='FaceProjection'
            masknode=nt.nodes.new('ShaderNodeVertexColor')
            masknode.layer_name='ExpressionMask'
            for label in ['susto','panico','derrota']:
                exp=nt.nodes.new('ShaderNodeTexImage')
                exp.name='PNG | '+label
                exp.image=bpy.data.images.load(str(ASSETS/('expressao_'+label+'.png')),check_existing=True)
                exp.interpolation='Closest'
                nt.links.new(p_uv.outputs[0],exp.inputs['Vector'])
                weight=nt.nodes.new('ShaderNodeValue')
                weight.name='EXPRESSION | '+label
                weight.outputs[0].default_value=0
                mul=nt.nodes.new('ShaderNodeMath'); mul.operation='MULTIPLY'
                nt.links.new(masknode.outputs['Color'],mul.inputs[0])
                nt.links.new(weight.outputs[0],mul.inputs[1])
                alpha=nt.nodes.new('ShaderNodeMath'); alpha.operation='MULTIPLY'
                nt.links.new(mul.outputs[0],alpha.inputs[0])
                nt.links.new(exp.outputs['Alpha'],alpha.inputs[1])
                blend=nt.nodes.new('ShaderNodeMixRGB')
                nt.links.new(alpha.outputs[0],blend.inputs[0])
                nt.links.new(color,blend.inputs[1])
                nt.links.new(exp.outputs['Color'],blend.inputs[2])
                color=blend.outputs[0]
                weights[label]=weight.outputs[0]
        # Directional, normal-based game lighting without stochastic raytracing noise.
        geom=nt.nodes.new('ShaderNodeNewGeometry')
        dot=nt.nodes.new('ShaderNodeVectorMath'); dot.operation='DOT_PRODUCT'
        dot.inputs[1].default_value=(.25,-.65,.72)
        nt.links.new(geom.outputs['Normal'],dot.inputs[0])
        level=nt.nodes.new('ShaderNodeMath'); level.operation='MULTIPLY_ADD'
        level.inputs[1].default_value=.25
        level.inputs[2].default_value=.80
        nt.links.new(dot.outputs['Value'],level.inputs[0])
        shaded=nt.nodes.new('ShaderNodeMixRGB'); shaded.blend_type='MULTIPLY'; shaded.inputs[0].default_value=1
        nt.links.new(color,shaded.inputs[1])
        nt.links.new(level.outputs[0],shaded.inputs[2])
        nt.links.new(shaded.outputs[0],emission.inputs['Color'])
        nt.links.new(emission.outputs[0],out.inputs['Surface'])
        return m,weights


    bm,_=character_material('DERY | original texture + game lighting')
    hm,expressions=character_material('DERY | UV expression PNGs',True)
    body.data.materials.clear(); body.data.materials.append(bm)
    head.data.materials.clear(); head.data.materials.append(hm)

    rest={b.name:b.matrix_local.to_quaternion() for b in rig.data.bones}
    return hero

def cache_clips():
    global clips,moving_bones
    import gzip,json
    cache=ASSETS/'poses_cache.json.gz'
    names=['idle','walk','run','startled','carry','talk','idle_tired','crouch_idle']
    all_names=[b.name for b in rig.pose.bones]
    rdata=rig.animation_data_create()
    if cache.exists():
        with gzip.open(cache,'rt') as source: clips=json.load(source)
    for name in names:
        if name in clips: continue
        action=bpy.data.actions.get(name+'_Dery_Rig')
        if action is None: continue
        rdata.action=action
        frames=[]
        end=min(192,round(action.frame_range[1]))
        for f in range(end+1):
            s.frame_set(f)
            frames.append({b.name:(b.location.copy(),b.rotation_quaternion.copy(),b.scale.copy()) for b in rig.pose.bones})
        clips[name]=frames
        print('CACHED',name,len(frames),flush=True)
    if not cache.exists():
        serial={n:[{bone:[list(v) for v in values] for bone,values in frame.items()}for frame in frames]for n,frames in clips.items()}
        with gzip.open(cache,'wt') as output: json.dump(serial,output,separators=(',',':'))
    rdata.action=None
    for b in rig.pose.bones:
        b.matrix_basis=Matrix.Identity(4)
    main=['root','pelvis','waist','spine','chest','upper_chest','neck','neck_upper','head','arm_L','forearm_L','hand_L','arm_R','forearm_R','hand_R','thigh_L','shin_L','foot_L','thigh_R','shin_R','foot_R']
    moving=set(main)
    if clips:
        for n in all_names:
            values=[tuple(v for part in frame[n] for v in part) for frames in clips.values() for frame in frames]
            if any(max(row[i] for row in values)-min(row[i] for row in values)>1e-5 for i in range(10)):
                moving.add(n)
    moving_bones=sorted(moving)
    rdata.action=bpy.data.actions.new('DERY | Short 002 performance')
    print('CACHED_CLIPS',[(n,len(v))for n,v in clips.items()],'KEY_BONES',len(moving_bones),flush=True)

def pose(clip,t,speed=1):
    frames=clips.get(clip) or clips.get('idle')
    if frames:
        data=frames[int(t*24*speed)%len(frames)]
        for b in rig.pose.bones:
            loc,q,scale=data[b.name]
            b.location=loc
            b.rotation_quaternion=q
            b.scale=scale
    else:
        for b in rig.pose.bones: b.matrix_basis=Matrix.Identity(4)
        for side,suffix in [(1,'L'),(-1,'R')]:
            delta('arm_'+suffix,(0,1,0),side*1.25)
    rig.pose.bones['root'].location=(0,0,0)

def key(f):
    for n in moving_bones:
        b=rig.pose.bones[n]
        for path in ['location','rotation_quaternion','scale']:
            if RECORD: RECORD(b,path,f)
            else: b.keyframe_insert(data_path=path,frame=f,group=n)

def expression(name,f,weight=1):
    for label,node in expressions.items():
        node.default_value=weight if label==name else 0
        if RECORD: RECORD(node,'default_value',f)
        else: node.keyframe_insert(data_path='default_value',frame=f)
