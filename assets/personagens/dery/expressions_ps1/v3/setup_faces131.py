"""Extend the ORIGINAL Dery's reviewed material; never change mesh or UVs."""
from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parent

def install(avatar):
    mesh=avatar.data
    required=['DeryFaceMask','PS1FaceLightFit','PS1CleanUnderEyes']
    if 'DeryFacePS1' not in mesh.uv_layers or any(n not in mesh.color_attributes for n in required):
        raise ValueError('Use the original Dery with the reviewed v2 face fitting. No mesh fitting is performed here.')
    source=mesh.materials[1]
    if source.get('PSXFaceBaked'):
        # Production scenes can bake the selector directly on the material.
        # Do not silently add an object driver on top of that animation.
        if source.users>1:
            copied=source.copy();mesh.materials[1]=copied
            if copied.node_tree.animation_data and copied.node_tree.animation_data.action:
                copied.node_tree.animation_data.action=copied.node_tree.animation_data.action.copy()
            return copied
        return source
    if source.get('DeryExpressionVersion')==3:
        node=source.node_tree.nodes.get('PS1 | face ID')
        curve=node.outputs[0].driver_add('default_value')
        if any(t.id==avatar for v in curve.driver.variables for t in v.targets):
            return source
        # A duplicate character must control its own face, not its source's ID.
        copied=source.copy();mesh.materials[1]=copied
        curve=copied.node_tree.nodes['PS1 | face ID'].outputs[0].driver_add('default_value')
        driver=curve.driver
        for variable in list(driver.variables):driver.variables.remove(variable)
        variable=driver.variables.new();variable.name='face';variable.type='SINGLE_PROP'
        variable.targets[0].id=avatar;variable.targets[0].data_path='["PS1_face_id"]'
        driver.expression='face'
        copied.node_tree.update_tag()
        avatar.update_tag()
        bpy.context.scene.frame_set(bpy.context.scene.frame_current)
        return copied
    m=source.copy();m.name='DERY | 131 PNG expressions | 100 new'
    nt=m.node_tree
    atlas_node=nt.nodes.get('PS1 | 31 drawn PNGs')
    cheek_node=nt.nodes.get('PS1 | clear cheek skin')
    index=nt.nodes.get('PS1 | face ID')
    if not all((atlas_node,cheek_node,index)):
        bpy.data.materials.remove(m)
        raise ValueError('Expected original v2 face nodes; refusing to replace an unknown shader.')
    atlas=bpy.data.images.load(str(ROOT/'atlas_131_16x9.png'),check_existing=True)
    for n in (atlas_node,cheek_node):
        n.image=atlas;n.interpolation='Closest';n.extension='EXTEND'
    atlas_node.name='PS1 | 131 drawn PNGs'
    # Copying a material retains drivers pointing to the old object. Retarget
    # explicitly so the helper also works on original-avatar copies.
    driver=index.outputs[0].driver_add('default_value').driver
    for v in list(driver.variables): driver.variables.remove(v)
    v=driver.variables.new();v.name='face';v.type='SINGLE_PROP'
    v.targets[0].id=avatar;v.targets[0].data_path='["PS1_face_id"]';driver.expression='face'
    def math(op,a,b=0):
        n=nt.nodes.new('ShaderNodeMath');n.operation=op;n.label='131-face atlas'
        for i,value in enumerate([a,b]):
            if isinstance(value,(int,float)):n.inputs[i].default_value=value
            else:nt.links.new(value,n.inputs[i])
        return n.outputs[0]
    ix=math('MINIMUM',math('MAXIMUM',math('FLOOR',math('ADD',index.outputs[0],.5)),0),130)
    col=math('MODULO',ix,16)
    row=math('SUBTRACT',8,math('FLOOR',math('DIVIDE',ix,16)))
    uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map='DeryFacePS1'
    sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(uv.outputs[0],sep.inputs[0])
    vector=nt.nodes.new('ShaderNodeCombineXYZ')
    for axis,count,offset in [('X',16,col),('Y',9,row)]:
        # Clamp within each tile to avoid reading a neighbouring expression.
        local=math('MINIMUM',math('MAXIMUM',sep.outputs[axis],.004),.996)
        nt.links.new(math('DIVIDE',math('ADD',local,offset),count),vector.inputs[axis])
    nt.links.new(vector.outputs[0],atlas_node.inputs['Vector'])
    cheek=nt.nodes.new('ShaderNodeCombineXYZ')
    nt.links.new(math('DIVIDE',math('ADD',col,.045),16),cheek.inputs['X'])
    nt.links.new(vector.inputs['Y'].links[0].from_socket,cheek.inputs['Y'])
    nt.links.new(cheek.outputs[0],cheek_node.inputs['Vector'])
    # Retain the exact old eye clean-up for IDs 0–29. New art is drawn clean;
    # applying this strip to huge comic eyes or tears would erase their lower half.
    old_cleanup=next(n for n in nt.nodes if n.type=='MATH' and n.operation=='LESS_THAN'
                     and abs(n.inputs[1].default_value-29.5)<.001)
    nt.links.new(ix,old_cleanup.inputs[0])
    avatar['PS1_face_id']=int(avatar.get('PS1_face_id',0))
    avatar.id_properties_ui('PS1_face_id').update(min=0,max=130,
        description='0–30 original; 31–80 speaking; 81–105 reactions; 106–130 comic. Use Constant keyframes.')
    avatar['DeryExpressionLibrary']='expressions_ps1/v3/expressions.json'
    avatar['DeryExpressionCount']=131
    m['DeryExpressionVersion']=3
    mesh.materials[1]=m
    return m

def set_face(avatar, face_id, frame=None):
    if not 0 <= int(face_id) <= 130: raise ValueError('Face ID must be 0–130')
    avatar['PS1_face_id']=int(face_id)
    material=avatar.data.materials[1]
    baked=bool(material and material.get('PSXFaceBaked'))
    if baked:
        socket=material.node_tree.nodes['PS1 | face ID'].outputs[0]
        socket.default_value=int(face_id)
        if frame is not None:
            socket.keyframe_insert('default_value',frame=frame)
            for curve in material.node_tree.animation_data.action.fcurves:
                for key in curve.keyframe_points:key.interpolation='CONSTANT'
    avatar.update_tag()
    if frame is not None:
        avatar.keyframe_insert(data_path='["PS1_face_id"]',frame=frame)
        if avatar.animation_data and avatar.animation_data.action:
            for curve in avatar.animation_data.action.fcurves:
                if curve.data_path=='["PS1_face_id"]':
                    for key in curve.keyframe_points:key.interpolation='CONSTANT'
    bpy.context.view_layer.update()
