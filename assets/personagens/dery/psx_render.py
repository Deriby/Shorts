"""PSX projection: seam-safe vertex rounding and real affine UV interpolation.

UV*z and z are stored at corners after deformation. Dividing their perspective-
interpolated values in the shader produces screen-linear, affine coordinates.
No random UV noise, camera shake or blur is added.
"""
import bpy
from ps1_precision import add_safe_precision

PREFIX='PSX_Affine_'

def projection_group(reference,camera,uv_names,width=320,height=180,aspect=16/9):
    modifier=add_safe_precision(reference,camera,width=width,height=height,aspect=aspect)
    g=modifier.node_group;g.name='PSX | snapped vertices + affine UVs'
    nodes,links=g.nodes,g.links
    output=next(n for n in nodes if n.type=='GROUP_OUTPUT')
    geometry=output.inputs[0].links[0].from_socket
    own=nodes.new('GeometryNodeSelfObject')
    obj=nodes.new('GeometryNodeObjectInfo');obj.transform_space='ORIGINAL';links.new(own.outputs[0],obj.inputs['Object'])
    cam=nodes.new('GeometryNodeObjectInfo');cam.transform_space='ORIGINAL';cam.inputs['Object'].default_value=camera
    inv=nodes.new('FunctionNodeInvertMatrix');links.new(cam.outputs['Transform'],inv.inputs[0])
    position=nodes.new('GeometryNodeInputPosition')
    world=nodes.new('FunctionNodeTransformPoint');links.new(position.outputs[0],world.inputs[0]);links.new(obj.outputs['Transform'],world.inputs[1])
    local=nodes.new('FunctionNodeTransformPoint');links.new(world.outputs[0],local.inputs[0]);links.new(inv.outputs[0],local.inputs[1])
    sep=nodes.new('ShaderNodeSeparateXYZ');links.new(local.outputs[0],sep.inputs[0])
    depth=nodes.new('ShaderNodeMath');depth.operation='MULTIPLY';depth.inputs[1].default_value=-1;links.new(sep.outputs['Z'],depth.inputs[0])
    limit=nodes.new('ShaderNodeMath');limit.operation='MAXIMUM';limit.inputs[1].default_value=.005;links.new(depth.outputs[0],limit.inputs[0])
    for name in sorted(uv_names):
        uv=nodes.new('GeometryNodeInputNamedAttribute');uv.data_type='FLOAT_VECTOR';uv.inputs['Name'].default_value=name
        split=nodes.new('ShaderNodeSeparateXYZ');links.new(uv.outputs['Attribute'],split.inputs[0])
        combined=nodes.new('ShaderNodeCombineXYZ')
        for axis in ['X','Y']:
            mul=nodes.new('ShaderNodeMath');mul.operation='MULTIPLY'
            links.new(split.outputs[axis],mul.inputs[0]);links.new(limit.outputs[0],mul.inputs[1]);links.new(mul.outputs[0],combined.inputs[axis])
        links.new(limit.outputs[0],combined.inputs['Z'])
        store=nodes.new('GeometryNodeStoreNamedAttribute');store.data_type='FLOAT_VECTOR';store.domain='CORNER'
        store.inputs['Name'].default_value=PREFIX+name
        links.new(geometry,store.inputs['Geometry']);links.new(combined.outputs[0],store.inputs['Value']);geometry=store.outputs['Geometry']
    links.new(geometry,output.inputs[0]);g['method']='perspective(UV*z) / perspective(z) = affine(UV)'
    g['snap_grid']=[width,height];g['uv_names']=','.join(sorted(uv_names))
    return modifier,g

def affine_material(material,default_uv='UVMap',strength=1):
    if not material or not material.use_nodes or material.get('PSXAffine'):return 0
    nt=material.node_tree;nodes,links=nt.nodes,nt.links
    sources=[]
    for n in list(nodes):
        if n.type=='UVMAP':sources.append((n.outputs[0],n.uv_map or default_uv))
        elif n.type=='TEX_COORD'and n.outputs['UV'].is_linked:sources.append((n.outputs['UV'],default_uv))
    for n in list(nodes):
        if n.type=='TEX_IMAGE':
            n.interpolation='Closest'
            if not n.inputs['Vector'].is_linked:
                uv=nodes.new('ShaderNodeUVMap');uv.uv_map=default_uv
                links.new(uv.outputs[0],n.inputs['Vector']);sources.append((uv.outputs[0],default_uv))
    count=0
    for source,name in sources:
        targets=[link.to_socket for link in list(source.links)]
        if not targets:continue
        attr=nodes.new('ShaderNodeAttribute');attr.attribute_name=PREFIX+name;attr.name='PSX | UV times depth | '+name
        sep=nodes.new('ShaderNodeSeparateXYZ');links.new(attr.outputs['Vector'],sep.inputs[0])
        denom=nodes.new('ShaderNodeMath');denom.operation='MAXIMUM';denom.inputs[1].default_value=.005;links.new(sep.outputs['Z'],denom.inputs[0])
        vector=nodes.new('ShaderNodeCombineXYZ')
        for axis in ['X','Y']:
            div=nodes.new('ShaderNodeMath');div.operation='DIVIDE';links.new(sep.outputs[axis],div.inputs[0]);links.new(denom.outputs[0],div.inputs[1]);links.new(div.outputs[0],vector.inputs[axis])
        mix=nodes.new('ShaderNodeMixRGB');mix.name='PSX | Affine blend | '+name;mix.inputs[0].default_value=strength
        links.new(source,mix.inputs[1]);links.new(vector.outputs[0],mix.inputs[2])
        for target in targets:links.new(mix.outputs[0],target)
        count+=1
    material['PSXAffine']=True;material['PSXAffineStrength']=strength
    return count

def install_scene(scene,camera,actors,width=320,height=180):
    meshes=[o for o in scene.objects if o.type=='MESH']
    uv_names={layer.name for obj in meshes for layer in obj.data.uv_layers}
    for obj in meshes:
        for modifier in list(obj.modifiers):
            if modifier.type=='NODES'and ('PS1'in modifier.name or 'PS1'in modifier.node_group.name):obj.modifiers.remove(modifier)
        if obj not in actors:
            attr=obj.data.attributes.get('PS1SnapWeight')or obj.data.attributes.new(name='PS1SnapWeight',type='FLOAT',domain='POINT')
            for value in attr.data:value.value=1
    reference=actors[0]
    modifier,group=projection_group(reference,camera,uv_names,width,height)
    for obj in meshes:
        if obj in actors:
            attr=obj.data.attributes.get('PS1SnapWeight')
            if obj!=reference:
                # Derive weights from identical rest positions, retaining seam safety.
                temp=add_safe_precision(obj,camera,width,height,16/9);obj.modifiers.remove(temp)
            for value in obj.data.attributes['PS1SnapWeight'].data:value.value=.18+.82*value.value
        if obj!=reference:
            m=obj.modifiers.new('PSX | snapped vertices and affine UV','NODES');m.node_group=group
    processed=set();count=0
    for obj in meshes:
        default=next((u.name for u in obj.data.uv_layers if u.active_render),None)
        default=default or(obj.data.uv_layers[0].name if obj.data.uv_layers else'UVMap')
        for material in obj.data.materials:
            if material and material.as_pointer()not in processed:
                processed.add(material.as_pointer())
                count+=affine_material(material,default,.70 if material.get('DeryExpressionVersion')==3 else 1.)
    return dict(grid=[width,height],uv_layers=sorted(uv_names),affine_links=count,
                face_snap_floor=.18,face_affine=.70,method=group['method'])

def bake_faces(avatar,keys):
    """Bake the selector into its own material action; avoid object/GN driver cycles."""
    mat=avatar.data.materials[1]
    if mat.users>1:mat=mat.copy();avatar.data.materials[1]=mat
    nt=mat.node_tree;node=nt.nodes['PS1 | face ID'];socket=node.outputs[0]
    try:socket.driver_remove('default_value')
    except (TypeError,RuntimeError):pass
    nt.animation_data_clear()
    action=bpy.data.actions.new(avatar.name+' | PS1 texture swaps')
    nt.animation_data_create().action=action
    path='nodes["PS1 | face ID"].outputs[0].default_value'
    fc=action.fcurves.new(path);fc.keyframe_points.add(len(keys))
    fc.keyframe_points.foreach_set('co',[value for key in keys for value in key])
    for key in fc.keyframe_points:key.interpolation='CONSTANT'
    fc.update();mat['PSXFaceBaked']=True
    return len(keys)
