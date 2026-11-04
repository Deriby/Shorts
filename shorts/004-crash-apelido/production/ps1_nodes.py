"""Native, animated camera-space vertex precision. No frame handlers required."""
import bpy

def add_contour_modifier(avatar,camera,width=320,height=180,aspect=16/9):
    g=bpy.data.node_groups.new('PS1 | camera-space contour precision','GeometryNodeTree')
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
    position=n.new('GeometryNodeInputPosition');normal=n.new('GeometryNodeInputNormal')
    world=transform(position.outputs[0],oi.outputs['Transform'])
    pc=transform(world,inverse(ci.outputs['Transform']))
    wn=transform(normal.outputs[0],oi.outputs['Transform'],True)
    cn=transform(wn,inverse(ci.outputs['Transform']),True)
    cn=vector('NORMALIZE',cn)
    toward=vector('NORMALIZE',vector('MULTIPLY',pc,(-1,-1,-1)))
    facing=calc('ABSOLUTE',vector('DOT_PRODUCT',cn,toward))
    strength=calc('DIVIDE',calc('SUBTRACT',.60,facing),.30)
    clamp=n.new('ShaderNodeClamp');link.new(strength,clamp.inputs[0]);strength=clamp.outputs[0]

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
    modifier=avatar.modifiers.new('PS1 | animated screen-space edges','NODES');modifier.node_group=g
    return modifier
