"""Reusable native Blender texture swapping, driven by Dery's face ID property."""
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parent
ZV=[(1.462,0),(1.482,.09),(1.504,.24),(1.535,.42),(1.574,.72),(1.608,.86),(1.632,1)]
def clamp(x):return max(0,min(1,x))
def face_v(z):
    for (a,va),(b,vb)in zip(ZV,ZV[1:]):
        if z<=b:return va+(vb-va)*clamp((z-a)/(b-a))
    return 1
def install(avatar):
    mesh=avatar.data
    if mesh.shape_keys:
        mesh.shape_keys.animation_data_clear()
        for key in mesh.shape_keys.key_blocks:key.value=0
    uv=mesh.uv_layers.get('DeryFacePS1')or mesh.uv_layers.new(name='DeryFacePS1')
    mask=mesh.color_attributes.get('DeryFaceMask')or mesh.color_attributes.new(name='DeryFaceMask',type='FLOAT_COLOR',domain='CORNER')
    # Mesh custom-data allocation invalidates cached RNA layer references.
    uv=mesh.uv_layers['DeryFacePS1'];mask=mesh.color_attributes['DeryFaceMask']
    for loop in mesh.loops:
        x,y,z=mesh.vertices[loop.vertex_index].co
        uv.data[loop.index].uv=(max(.004,min(.996,x/.190+.5)),max(.004,min(.996,face_v(z))))
        weight=clamp((.101-abs(x))/.017)*clamp((-y-.006)/.028)*clamp((z-1.462)/.008)*clamp((1.636-z)/.012)
        mask.data[loop.index].color=(weight,weight,weight,1)
    material=bpy.data.materials.new('DERY | PS1 drawn face atlas');material.use_nodes=True
    nt=material.node_tree;nt.nodes.clear()
    def math(op,a,b=None):
        n=nt.nodes.new('ShaderNodeMath');n.operation=op
        for i,v in enumerate([a,b]):
            if v is None:continue
            if isinstance(v,(float,int)):n.inputs[i].default_value=v
            else:nt.links.new(v,n.inputs[i])
        return n.outputs[0]
    avatar['PS1_face_id']=0
    avatar.id_properties_ui('PS1_face_id').update(min=0,max=11,description='Drawn PNG face, instant texture swap: see expressions.json')
    index=nt.nodes.new('ShaderNodeValue');index.name='PS1 | face ID'
    driver=index.outputs[0].driver_add('default_value').driver
    v=driver.variables.new();v.name='face';v.type='SINGLE_PROP';v.targets[0].id=avatar;v.targets[0].data_path='["PS1_face_id"]';driver.expression='face'
    baseuv=nt.nodes.new('ShaderNodeUVMap');baseuv.uv_map='UVMap'
    base=nt.nodes.new('ShaderNodeTexImage');base.image=bpy.data.images.load(str(ROOT.parent/'Dery_Material_Diffuse.png'),check_existing=True);base.interpolation='Closest';nt.links.new(baseuv.outputs[0],base.inputs['Vector'])
    faceuv=nt.nodes.new('ShaderNodeUVMap');faceuv.uv_map='DeryFacePS1'
    sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(faceuv.outputs[0],sep.inputs[0])
    tilex=math('MODULO',index.outputs[0],4);tiley=math('SUBTRACT',2,math('FLOOR',math('DIVIDE',index.outputs[0],4)))
    combine=nt.nodes.new('ShaderNodeCombineXYZ')
    nt.links.new(math('DIVIDE',math('ADD',sep.outputs['X'],tilex),4),combine.inputs['X'])
    nt.links.new(math('DIVIDE',math('ADD',sep.outputs['Y'],tiley),3),combine.inputs['Y'])
    image=nt.nodes.new('ShaderNodeTexImage');image.name='PS1 | twelve drawn textures';image.image=bpy.data.images.load(str(ROOT/'atlas_4x3.png'),check_existing=True);image.interpolation='Closest';image.extension='EXTEND';nt.links.new(combine.outputs[0],image.inputs['Vector'])
    attr=nt.nodes.new('ShaderNodeVertexColor');attr.layer_name='DeryFaceMask'
    mix=nt.nodes.new('ShaderNodeMixRGB');nt.links.new(attr.outputs['Color'],mix.inputs[0]);nt.links.new(base.outputs['Color'],mix.inputs[1]);nt.links.new(image.outputs['Color'],mix.inputs[2])
    light=nt.nodes.new('ShaderNodeVertexColor');light.layer_name='PS1Lighting'
    multiply=nt.nodes.new('ShaderNodeMixRGB');multiply.blend_type='MULTIPLY';multiply.inputs[0].default_value=1
    nt.links.new(mix.outputs[0],multiply.inputs[1]);nt.links.new(light.outputs['Color'],multiply.inputs[2])
    em=nt.nodes.new('ShaderNodeEmission');out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(multiply.outputs[0],em.inputs['Color']);nt.links.new(em.outputs[0],out.inputs['Surface'])
    mesh.materials[1]=material
    return material
