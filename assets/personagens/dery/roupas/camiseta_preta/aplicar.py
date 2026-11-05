"""Black shirt with the approved yellow M print; original geometry is unchanged."""
from pathlib import Path
import bpy
from mathutils import Vector
from limpar import limpar

def aplicar(avatar):
    if avatar.get('DeryWardrobe')=='camiseta_preta_limpa_v4':return avatar.get('DeryWardrobeFaces',0)
    mesh=avatar.data
    if mesh.get('DeryWardrobe')=='camiseta_preta_limpa_v4':
        avatar['DeryWardrobe']='camiseta_preta_limpa_v4'
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

    original_uv=uv.name
    mesh.uv_layers.get('DeryLogoChest')or mesh.uv_layers.new(name='DeryLogoChest')
    mesh.color_attributes.get('DeryLogoFront')or mesh.color_attributes.new(name='DeryLogoFront',type='FLOAT_COLOR',domain='CORNER')
    print_uv=mesh.uv_layers['DeryLogoChest'];front=mesh.color_attributes['DeryLogoFront']
    for loop in mesh.loops:
        p=mesh.vertices[loop.vertex_index].co
        print_uv.data[loop.index].uv=(p.x/.18+.5,(p.z-1.25)/.18+.5)
        mask=max(0,min(1,(-p.y-.015)/.045))
        front.data[loop.index].color=(mask,mask,mask,1)
    mesh.uv_layers[original_uv].active_render=True
    mesh.uv_layers.active=mesh.uv_layers[original_uv]

    m=bpy.data.materials.new('DERY | camiseta preta com M amarelo');m.use_nodes=True
    nt=m.node_tree;nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial');emit=nt.nodes.new('ShaderNodeEmission')
    attr=nt.nodes.new('ShaderNodeVertexColor');attr.layer_name='PS1Lighting'
    gray=nt.nodes.new('ShaderNodeRGBToBW');nt.links.new(attr.outputs['Color'],gray.inputs[0])
    geom=nt.nodes.new('ShaderNodeNewGeometry');dot=nt.nodes.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=(.25,-.65,.72);nt.links.new(geom.outputs['Normal'],dot.inputs[0])
    shade=nt.nodes.new('ShaderNodeMath');shade.operation='MULTIPLY_ADD';shade.inputs[1].default_value=.25;shade.inputs[2].default_value=.82;nt.links.new(dot.outputs['Value'],shade.inputs[0])
    level=nt.nodes.new('ShaderNodeMath');level.operation='MULTIPLY';nt.links.new(gray.outputs[0],level.inputs[0]);nt.links.new(shade.outputs[0],level.inputs[1])
    mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[1].default_value=(.006,.006,.006,1);nt.links.new(level.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],emit.inputs['Color']);nt.links.new(emit.outputs[0],out.inputs['Surface'])
    logo=nt.nodes.new('ShaderNodeTexImage');logo.name='MASSACOTE | approved M print'
    logo.image=bpy.data.images.load(str(Path(__file__).resolve().parents[4]/'marca/massacote-games/logo.png'),check_existing=True)
    logo.interpolation='Closest';logo.extension='CLIP'
    coordinates=nt.nodes.new('ShaderNodeUVMap');coordinates.uv_map='DeryLogoChest';nt.links.new(coordinates.outputs[0],logo.inputs['Vector'])
    front_node=nt.nodes.new('ShaderNodeVertexColor');front_node.layer_name='DeryLogoFront'
    alpha=nt.nodes.new('ShaderNodeMath');alpha.operation='MULTIPLY';nt.links.new(logo.outputs['Alpha'],alpha.inputs[0]);nt.links.new(front_node.outputs['Color'],alpha.inputs[1])
    ink=nt.nodes.new('ShaderNodeMixRGB');ink.blend_type='MULTIPLY';ink.inputs[0].default_value=1;nt.links.new(logo.outputs['Color'],ink.inputs[1]);nt.links.new(level.outputs[0],ink.inputs[2])
    composite=nt.nodes.new('ShaderNodeMixRGB');nt.links.new(alpha.outputs[0],composite.inputs[0]);nt.links.new(mix.outputs[0],composite.inputs[1]);nt.links.new(ink.outputs[0],composite.inputs[2]);nt.links.new(composite.outputs[0],emit.inputs['Color'])
    index=len(mesh.materials);mesh.materials.append(m)
    for i in selected:mesh.polygons[i].material_index=index
    limpar(avatar,m,source)

    avatar['DeryWardrobe']='camiseta_preta_limpa_v4'
    avatar['DeryWardrobeFaces']=len(selected)
    mesh['DeryWardrobe']='camiseta_preta_limpa_v4'
    mesh['DeryWardrobeFaces']=len(selected)
    return len(selected)
