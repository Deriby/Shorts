"""Seam-safe PS1 precision: coincident vertices move together; facial UVs stay stable."""
import bpy

def add_safe_precision(avatar,camera,width=216,height=384,aspect=9/16):
    # A position-derived POINT attribute gives duplicated seam vertices identical
    # weights. Normal-based weights split them and expose dark cracks.
    attr=avatar.data.attributes.get("PS1SnapWeight") or avatar.data.attributes.new(name="PS1SnapWeight",type="FLOAT",domain="POINT")
    clamp=lambda v:max(0.0,min(1.0,v))
    for vertex,item in zip(avatar.data.vertices,attr.data):
        x,y,z=vertex.co
        face=clamp((z-1.34)/.07)*clamp((1.78-z)/.10)*clamp((.155-abs(x))/.035)*clamp((-.005-y)/.04)
        item.value=1-face
    g=bpy.data.node_groups.new('PS1 | seam-safe camera precision','GeometryNodeTree')
    g.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
    g.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    n=g.nodes;link=g.links
    def input_value(socket,value):
        if isinstance(value,(int,float,tuple,list)):
            socket.default_value=value
        else:link.new(value,socket)
    def calc(operation,a,b=None,c=None):
        x=n.new('ShaderNodeMath');x.operation=operation
        for i,v in enumerate([a,b,c]):
            if v is not None:input_value(x.inputs[i],v)
        return x.outputs[0]
    def vector(operation,a,b=None):
        x=n.new('ShaderNodeVectorMath');x.operation=operation
        input_value(x.inputs[0],a)
        if b is not None:input_value(x.inputs[1],b)
        return x.outputs['Value'] if operation in ['DOT_PRODUCT','LENGTH','DISTANCE'] else x.outputs['Vector']
    def transform(value,matrix,direction=False):
        x=n.new('FunctionNodeTransformDirection' if direction else 'FunctionNodeTransformPoint')
        link.new(value,x.inputs[0]);link.new(matrix,x.inputs[1]);return x.outputs[0]
    def inverse(matrix):
        x=n.new('FunctionNodeInvertMatrix');link.new(matrix,x.inputs[0]);return x.outputs[0]

    inp=n.new('NodeGroupInput');out=n.new('NodeGroupOutput')
    own=n.new('GeometryNodeSelfObject')
    oi=n.new('GeometryNodeObjectInfo');oi.transform_space='ORIGINAL';link.new(own.outputs[0],oi.inputs['Object'])
    ci=n.new('GeometryNodeObjectInfo');ci.transform_space='ORIGINAL';ci.inputs['Object'].default_value=camera
    position=n.new('GeometryNodeInputPosition')
    world=transform(position.outputs[0],oi.outputs['Transform'])
    pc=transform(world,inverse(ci.outputs['Transform']))
    weights=n.new('GeometryNodeInputNamedAttribute');weights.data_type='FLOAT'
    weights.inputs['Name'].default_value='PS1SnapWeight'
    strength=weights.outputs['Attribute']

    sep=n.new('ShaderNodeSeparateXYZ');link.new(pc,sep.inputs[0])
    depth=calc('MULTIPLY',sep.outputs['Z'],-1)
    lens=n.new('ShaderNodeValue');lens.name='Camera focal length';lens.outputs[0].default_value=camera.data.lens
    driver=lens.outputs[0].driver_add('default_value').driver
    var=driver.variables.new();var.name='focal';var.type='SINGLE_PROP'
    var.targets[0].id_type='CAMERA';var.targets[0].id=camera.data;var.targets[0].data_path='lens'
    driver.expression='focal'
    scale=calc('DIVIDE',lens.outputs[0],camera.data.sensor_height)
    u=calc('ADD',calc('DIVIDE',calc('MULTIPLY',calc('DIVIDE',sep.outputs['X'],depth),scale),aspect),.5)
    v=calc('ADD',calc('MULTIPLY',calc('DIVIDE',sep.outputs['Y'],depth),scale),.5)
    def snap(coord,res):
        return calc('DIVIDE',calc('FLOOR',calc('ADD',calc('MULTIPLY',coord,res),.5)),res)
    us=snap(u,width);vs=snap(v,height)
    x=calc('MULTIPLY',calc('DIVIDE',calc('MULTIPLY',calc('SUBTRACT',us,.5),depth),scale),aspect)
    y=calc('DIVIDE',calc('MULTIPLY',calc('SUBTRACT',vs,.5),depth),scale)
    combine=n.new('ShaderNodeCombineXYZ')
    link.new(x,combine.inputs['X']);link.new(y,combine.inputs['Y']);link.new(sep.outputs['Z'],combine.inputs['Z'])
    new_world=transform(combine.outputs[0],ci.outputs['Transform'])
    new_local=transform(new_world,inverse(oi.outputs['Transform']))
    difference=vector('SUBTRACT',new_local,position.outputs[0])
    amount=n.new('ShaderNodeVectorMath');amount.operation='SCALE'
    link.new(difference,amount.inputs[0]);link.new(strength,amount.inputs['Scale'])
    setpos=n.new('GeometryNodeSetPosition')
    link.new(inp.outputs[0],setpos.inputs['Geometry']);link.new(amount.outputs[0],setpos.inputs['Offset'])
    link.new(setpos.outputs[0],out.inputs[0])
    modifier=avatar.modifiers.new('PS1 | seam-safe screen-space edges','NODES');modifier.node_group=g
    return modifier
