"""Clean baked color blotches and garment/skin boundaries without changing mesh data."""
import bpy

def light(nt):
    g=nt.nodes.new('ShaderNodeNewGeometry');g.name='DERY CLEAN | surface normal'
    dot=nt.nodes.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=(.25,-.55,.80);nt.links.new(g.outputs['Normal'],dot.inputs[0])
    level=nt.nodes.new('ShaderNodeMath');level.operation='MULTIPLY_ADD';level.inputs[1].default_value=.18;level.inputs[2].default_value=.82;nt.links.new(dot.outputs['Value'],level.inputs[0])
    return level.outputs[0]

def skin_color():
    # Match the cheek background of the reviewed expression PNGs, in linear RGB.
    return tuple(((c/255+.055)/1.055)**2.4 for c in (237,147,88))+(1,)

def tinted_skin(nt,illumination):
    mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[1].default_value=skin_color();nt.links.new(illumination,mix.inputs[2]);return mix.outputs[0]

def limpar(avatar,shirt,original_image):
    mesh=avatar.data
    # Replace discontinuous colored per-corner light bakes with one coherent
    # normal-based neutral light. Keep the face atlas, masks and original UVs.
    for material in mesh.materials:
        if not material or not material.use_nodes or material.get('DeryNeutralLight'):continue
        nt=material.node_tree;targets=[]
        for node in nt.nodes:
            if node.type=='VERTEX_COLOR'and node.layer_name in ['PS1Lighting','PS1FaceLightFit']:
                targets += [link.to_socket for output in node.outputs for link in output.links]
        if targets:
            illumination=light(nt)
            for socket in targets:nt.links.new(illumination,socket)
        material['DeryNeutralLight']=True

    skin=bpy.data.materials.new('DERY | clean continuous skin');skin.use_nodes=True
    nt=skin.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');em=nt.nodes.new('ShaderNodeEmission')
    nt.links.new(tinted_skin(nt,light(nt)),em.inputs['Color']);nt.links.new(em.outputs[0],out.inputs['Surface'])
    skin_index=len(mesh.materials);mesh.materials.append(skin)
    arm_groups={g.index for g in avatar.vertex_groups if any(word in g.name.lower()for word in ['arm','hand'])}
    shirt_index=list(mesh.materials).index(shirt)
    skin_faces=0
    for polygon in mesh.polygons:
        if polygon.material_index==shirt_index:continue
        p=polygon.center
        if not(abs(p.x)>.24 and 1.03<p.z<1.48):continue
        weight=sum(sum(g.weight for g in mesh.vertices[v].groups if g.group in arm_groups)for v in polygon.vertices)/len(polygon.vertices)
        if weight>.45:polygon.material_index=skin_index;skin_faces+=1

    # Original skin can cross UV triangles along the cuff. Recover that exact
    # per-pixel border rather than painting whole mixed triangles black.
    mesh.color_attributes.get('DeryCuffZone')or mesh.color_attributes.new(name='DeryCuffZone',type='FLOAT_COLOR',domain='CORNER')
    cuff=mesh.color_attributes['DeryCuffZone']
    for loop in mesh.loops:
        p=mesh.vertices[loop.vertex_index].co
        weight=float(abs(p.x)>.22 and 1.10<p.z<1.48)
        cuff.data[loop.index].color=(weight,weight,weight,1)
    nt=shirt.node_tree;emit=next(n for n in nt.nodes if n.type=='EMISSION');old=emit.inputs['Color'].links[0].from_socket
    uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map='UVMap'
    image=nt.nodes.new('ShaderNodeTexImage');image.name='DERY CLEAN | original cuff boundary';image.image=original_image;image.interpolation='Closest';nt.links.new(uv.outputs[0],image.inputs['Vector'])
    hsv=nt.nodes.new('ShaderNodeSeparateColor');hsv.mode='HSV';nt.links.new(image.outputs['Color'],hsv.inputs[0])
    def test(op,a,b):
        n=nt.nodes.new('ShaderNodeMath');n.operation=op;nt.links.new(a,n.inputs[0]);n.inputs[1].default_value=b;return n.outputs[0]
    low=test('GREATER_THAN',hsv.outputs[0],.015);high=test('LESS_THAN',hsv.outputs[0],.17);sat=test('GREATER_THAN',hsv.outputs[1],.25)
    both=nt.nodes.new('ShaderNodeMath');both.operation='MULTIPLY';nt.links.new(low,both.inputs[0]);nt.links.new(high,both.inputs[1])
    mask=nt.nodes.new('ShaderNodeMath');mask.operation='MULTIPLY';nt.links.new(both.outputs[0],mask.inputs[0]);nt.links.new(sat,mask.inputs[1])
    zone=nt.nodes.new('ShaderNodeVertexColor');zone.layer_name='DeryCuffZone'
    local_mask=nt.nodes.new('ShaderNodeMath');local_mask.operation='MULTIPLY';nt.links.new(mask.outputs[0],local_mask.inputs[0]);nt.links.new(zone.outputs['Color'],local_mask.inputs[1])
    blend=nt.nodes.new('ShaderNodeMixRGB');nt.links.new(local_mask.outputs[0],blend.inputs[0]);nt.links.new(old,blend.inputs[1]);nt.links.new(tinted_skin(nt,light(nt)),blend.inputs[2]);nt.links.new(blend.outputs[0],emit.inputs['Color'])
    avatar['DeryCleanSkinFaces']=skin_faces;avatar['DerySurfaceClean']='neutral_skin_cuffs_v1'
    return skin_faces
