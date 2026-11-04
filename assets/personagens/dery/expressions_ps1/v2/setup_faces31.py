"""Native reusable 31-face material, with the reviewed Dery mesh fitting."""
from pathlib import Path
import sys,bpy
ROOT=Path(__file__).resolve().parent
def install(avatar):
    if not all(n in avatar.data.color_attributes for n in ['DeryFaceMask','PS1FaceLightFit','PS1CleanUnderEyes']):
        sys.path.insert(0,str(ROOT.parent));from setup_faces import install as original
        original(avatar)
        sys.path.insert(0,str(ROOT));from fit_mesh import fit_mesh
        fit_mesh(avatar)
    m=bpy.data.materials.new('DERY | 31 drawn PS1 expressions');m.use_nodes=True
    nt=m.node_tree;nt.nodes.clear()
    def math(op,a,b=0):
        n=nt.nodes.new('ShaderNodeMath');n.operation=op
        for i,v in enumerate([a,b]):
            if isinstance(v,(int,float)):n.inputs[i].default_value=v
            else:nt.links.new(v,n.inputs[i])
        return n.outputs[0]
    def uv(name):
        n=nt.nodes.new('ShaderNodeUVMap');n.uv_map=name;return n.outputs[0]
    def image(path,vector,name):
        n=nt.nodes.new('ShaderNodeTexImage');n.name=name;n.image=bpy.data.images.load(str(path),check_existing=True);n.interpolation='Closest';n.extension='EXTEND';nt.links.new(vector,n.inputs['Vector']);return n
    def attr(name):
        n=nt.nodes.new('ShaderNodeVertexColor');n.layer_name=name;return n.outputs['Color']
    def mix(f,a,b,multiply=False):
        n=nt.nodes.new('ShaderNodeMixRGB');n.blend_type='MULTIPLY'if multiply else'MIX'
        if isinstance(f,(int,float)):n.inputs[0].default_value=f
        else:nt.links.new(f,n.inputs[0])
        nt.links.new(a,n.inputs[1]);nt.links.new(b,n.inputs[2]);return n.outputs[0]
    avatar['PS1_face_id']=0;avatar.id_properties_ui('PS1_face_id').update(min=0,max=30,description='31 drawn PNG expressions; see v2/expressions.json')
    index=nt.nodes.new('ShaderNodeValue');index.name='PS1 | face ID'
    d=index.outputs[0].driver_add('default_value').driver;v=d.variables.new();v.name='face';v.type='SINGLE_PROP';v.targets[0].id=avatar;v.targets[0].data_path='["PS1_face_id"]';d.expression='face'
    ix=index.outputs[0];col=math('MODULO',ix,8);row=math('SUBTRACT',3,math('FLOOR',math('DIVIDE',ix,8)))
    sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(uv('DeryFacePS1'),sep.inputs[0])
    vector=nt.nodes.new('ShaderNodeCombineXYZ')
    nt.links.new(math('DIVIDE',math('ADD',sep.outputs['X'],col),8),vector.inputs['X'])
    nt.links.new(math('DIVIDE',math('ADD',sep.outputs['Y'],row),4),vector.inputs['Y'])
    atlas=image(ROOT/'atlas_31_8x4.png',vector.outputs[0],'PS1 | 31 drawn PNGs')
    cleanvec=nt.nodes.new('ShaderNodeCombineXYZ');nt.links.new(math('DIVIDE',math('ADD',col,.045),8),cleanvec.inputs['X']);nt.links.new(vector.inputs['Y'].links[0].from_socket,cleanvec.inputs['Y'])
    skin=image(ROOT/'atlas_31_8x4.png',cleanvec.outputs[0],'PS1 | clear cheek skin')
    cleanmask=math('MULTIPLY',attr('PS1CleanUnderEyes'),math('LESS_THAN',ix,29.5))
    painted=mix(cleanmask,atlas.outputs['Color'],skin.outputs['Color'])
    snap=nt.nodes.new('ShaderNodeVectorMath');snap.operation='SNAP';snap.inputs[1].default_value=(1/512,1/512,1);nt.links.new(uv('UVMap'),snap.inputs[0])
    center=nt.nodes.new('ShaderNodeVectorMath');center.operation='ADD';center.inputs[1].default_value=(.5/512,.5/512,0);nt.links.new(snap.outputs[0],center.inputs[0])
    base=image(ROOT.parents[1]/'Dery_Material_Diffuse.png',center.outputs[0],'DERY | original skin and nose')
    color=mix(attr('DeryFaceMask'),base.outputs['Color'],painted)
    color=mix(1,color,attr('PS1FaceLightFit'),True)
    em=nt.nodes.new('ShaderNodeEmission');out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(color,em.inputs['Color']);nt.links.new(em.outputs[0],out.inputs['Surface'])
    avatar.data.materials[1]=m
    return m
