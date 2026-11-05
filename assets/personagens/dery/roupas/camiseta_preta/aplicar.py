"""Replace the original sports jersey with a plain black T-shirt, without altering geometry."""
import bpy
from mathutils import Vector

def aplicar(avatar):
    if avatar.get('DeryWardrobe')=='camiseta_preta_textura_v2':return avatar.get('DeryWardrobeFaces',0)
    mesh=avatar.data
    if mesh.get('DeryWardrobe')=='camiseta_preta_textura_v2':
        avatar['DeryWardrobe']='camiseta_preta_textura_v2'
        return mesh.get('DeryWardrobeFaces',0)
    source=next(n.image for m in mesh.materials if m and m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE'and n.image and 'Diffuse'in n.image.name)
    width,height=source.size;pixels=list(source.pixels[:]);uv=mesh.uv_layers.get('UVMap')or mesh.uv_layers[0]
    def color(p):
        x=max(0,min(width-1,round(p.x*(width-1))));y=max(0,min(height-1,round(p.y*(height-1))));i=4*(y*width+x)
        return pixels[i:i+3]
    selected=[]
    for poly in mesh.polygons:
        center=poly.center
        if not(.845<center.z<1.455 and abs(center.x)<.405):continue
        uvs=[uv.data[i].uv.copy()for i in poly.loop_indices]
        samples=[sum(uvs,Vector((0,0)))/len(uvs),*uvs]
        samples += [(p+uvs[(i+1)%len(uvs)])/2 for i,p in enumerate(uvs)]
        blue=white=skin=0
        for p in samples:
            r,g,b=color(p)
            blue+=b>max(r*1.35,g*1.12)and b>.045
            white+=min(r,g,b)>.53 and max(r,g,b)-min(r,g,b)<.18
            skin+=r>b*1.15 and r>g*1.03 and r>.15
        if (blue>=1 and skin<len(samples)*.6)or white>=len(samples)*.4:
            selected.append(poly.index)
    assert len(selected)>500, len(selected)

    m=bpy.data.materials.new('DERY | camiseta preta lisa');m.use_nodes=True
    nt=m.node_tree;nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial');emit=nt.nodes.new('ShaderNodeEmission')
    attr=nt.nodes.new('ShaderNodeVertexColor');attr.layer_name='PS1Lighting'
    gray=nt.nodes.new('ShaderNodeRGBToBW');nt.links.new(attr.outputs['Color'],gray.inputs[0])
    geom=nt.nodes.new('ShaderNodeNewGeometry');dot=nt.nodes.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=(.25,-.65,.72);nt.links.new(geom.outputs['Normal'],dot.inputs[0])
    shade=nt.nodes.new('ShaderNodeMath');shade.operation='MULTIPLY_ADD';shade.inputs[1].default_value=.25;shade.inputs[2].default_value=.82;nt.links.new(dot.outputs['Value'],shade.inputs[0])
    level=nt.nodes.new('ShaderNodeMath');level.operation='MULTIPLY';nt.links.new(gray.outputs[0],level.inputs[0]);nt.links.new(shade.outputs[0],level.inputs[1])
    mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[1].default_value=(.006,.006,.006,1);nt.links.new(level.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],emit.inputs['Color']);nt.links.new(emit.outputs[0],out.inputs['Surface'])
    index=len(mesh.materials);mesh.materials.append(m)
    for i in selected:mesh.polygons[i].material_index=index

    avatar['DeryWardrobe']='camiseta_preta_textura_v2'
    avatar['DeryWardrobeFaces']=len(selected)
    mesh['DeryWardrobe']='camiseta_preta_textura_v2'
    mesh['DeryWardrobeFaces']=len(selected)
    return len(selected)
