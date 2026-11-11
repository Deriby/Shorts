"""Reusable drawn expression selector for the v8 model, with dry texture swaps."""
from pathlib import Path
import bpy
import numpy as np
import hashlib
import json
from mathutils import Vector

ROOT = Path(__file__).resolve().parent

def texture_group():
    group = bpy.data.node_groups.new('DERY | expressão PNG 4x3 | clamp por célula', 'ShaderNodeTree')
    group.interface.new_socket(name='UV', in_out='INPUT', socket_type='NodeSocketVector')
    group.interface.new_socket(name='ID', in_out='INPUT', socket_type='NodeSocketFloat')
    group.interface.new_socket(name='UV Atlas', in_out='OUTPUT', socket_type='NodeSocketVector')
    group.interface.new_socket(name='Centro do rosto', in_out='OUTPUT', socket_type='NodeSocketFloat')
    n, links = group.nodes, group.links
    inputs = n.new('NodeGroupInput'); outputs = n.new('NodeGroupOutput')
    def calc(op, a, b=0):
        node = n.new('ShaderNodeMath'); node.operation = op
        for socket, value in zip(node.inputs, (a, b)):
            if isinstance(value, (int, float)): socket.default_value = value
            else: links.new(value, socket)
        return node.outputs[0]
    idx = calc('FLOOR', calc('MINIMUM', calc('MAXIMUM', inputs.outputs['ID'], 0), 10))
    col = calc('MODULO', idx, 4)
    row = calc('SUBTRACT', 2, calc('FLOOR', calc('DIVIDE', idx, 4)))
    split = n.new('ShaderNodeSeparateXYZ'); links.new(inputs.outputs['UV'], split.inputs[0])
    vec = n.new('ShaderNodeCombineXYZ')
    for axis, offset, count in [('X', col, 4), ('Y', row, 3)]:
        value = calc('MINIMUM', calc('MAXIMUM', split.outputs[axis], .5/128), 127.5/128)
        links.new(calc('DIVIDE', calc('ADD', value, offset), count), vec.inputs[axis])
    links.new(vec.outputs[0], outputs.inputs['UV Atlas'])
    # Preserve the original skin at the outer boundary. This is a spatial
    # seam mask; the expression ID itself has no temporal blending.
    def ramp(value):
        return calc('MINIMUM', calc('MAXIMUM', value, 0), 1)
    mx = ramp(calc('DIVIDE', calc('SUBTRACT', calc('MINIMUM', split.outputs['X'], calc('SUBTRACT', 1, split.outputs['X'])), .10), .055))
    my = ramp(calc('DIVIDE', calc('SUBTRACT', calc('MINIMUM', split.outputs['Y'], calc('SUBTRACT', 1, split.outputs['Y'])), .035), .045))
    links.new(calc('MULTIPLY', mx, my), outputs.inputs['Centro do rosto'])
    return group

def install(avatar):
    assert 'DeryFaceFitV8' in avatar.data.uv_layers
    avatar['PS1_face_id'] = 0
    avatar.id_properties_ui('PS1_face_id').update(min=0, max=10, description='0 neutro; 1 sorriso; 2 risada; 3 surpresa; 4 raiva; 5 confusão; 6 deboche; 7 tristeza; 8 nojo; 9 piscada; 10 falando')
    atlas = bpy.data.images.load(str(ROOT / 'Atlas_Expressoes_4x3.png'), check_existing=True)
    atlas.name = 'Dery | 10 expressões PNG + neutro | atlas 4x3'
    group = texture_group()
    count = 0
    for index in (1, 2):
        material = avatar.data.materials[index]
        nt = material.node_tree; nodes, links = nt.nodes, nt.links
        selector = nodes.new('ShaderNodeValue'); selector.name = 'DERY | PS1_face_id'
        driver = selector.outputs[0].driver_add('default_value').driver
        variable = driver.variables.new(); variable.name = 'face'; variable.type = 'SINGLE_PROP'
        variable.targets[0].id = avatar; variable.targets[0].data_path = '["PS1_face_id"]'
        driver.expression = 'face'
        originals = [node for node in list(nodes) if node.type == 'TEX_IMAGE' and node.image and node.image.name == 'Rosto_Neutro_128']
        assert len(originals) == 5, (material.name, len(originals))
        for neutral in originals:
            coords = neutral.inputs['Vector'].links[0].from_socket
            consumers = [link.to_socket for link in neutral.outputs['Color'].links]
            mapping = nodes.new('ShaderNodeGroup'); mapping.node_tree = group
            links.new(coords, mapping.inputs['UV']); links.new(selector.outputs[0], mapping.inputs['ID'])
            tile = nodes.new('ShaderNodeTexImage'); tile.image = atlas; tile.interpolation = 'Closest'; tile.extension = 'EXTEND'
            tile['DeryTextureFamily'] = 'DeryExpressionAtlasV1'; tile.label = 'Expressão PNG | mesma célula em todas as amostras'
            links.new(mapping.outputs['UV Atlas'], tile.inputs['Vector'])
            mix = nodes.new('ShaderNodeMixRGB'); mix.label = 'Pele original preservada na borda'
            links.new(mapping.outputs['Centro do rosto'], mix.inputs[0]); links.new(neutral.outputs['Color'], mix.inputs[1]); links.new(tile.outputs['Color'], mix.inputs[2])
            for socket in consumers: links.new(mix.outputs[0], socket)
            count += 1
    assert count == 10
    return count

def set_expression(avatar, index):
    avatar['PS1_face_id'] = max(0, min(10, int(index)))
    avatar.update_tag()
    bpy.context.view_layer.update()

def configure_preview(scene):
    focus = Vector((0, -.045, 1.655))
    scene.camera.location = (0, -3, 1.655)
    scene.camera.rotation_euler = (focus - scene.camera.location).to_track_quat('-Z', 'Y').to_euler()
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces.active.shading.type = 'MATERIAL'
                area.spaces.active.shading.use_scene_world = True
                area.spaces.active.shading.use_scene_lights = True
                area.spaces.active.region_3d.view_location = focus
                area.spaces.active.region_3d.view_distance = .65
                area.spaces.active.region_3d.view_rotation = scene.camera.rotation_euler.to_quaternion()

def build():
    source = ROOT.parent / 'texturas/encaixe_rosto_v8/Dery_Encaixe_Rosto_v8.blend'
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(source))
    body = bpy.data.objects['Dery_Massacote_Rig_PS1_v2']; mesh = body.data
    def digest(data): return hashlib.sha256(np.asarray(data, dtype=np.float32).tobytes()).hexdigest()
    def state():
        return {'basis': digest([v.co[:] for v in mesh.vertices]),
                'uvs': {uv.name: digest([p.uv[:] for p in uv.data]) for uv in mesh.uv_layers},
                'shape_keys': {key.name: (key.value, digest([v.co[:] for v in key.data])) for key in mesh.shape_keys.key_blocks},
                'weights': digest([(v.index, g.group, g.weight) for v in mesh.vertices for g in v.groups]),
                'assignments': digest([p.material_index for p in mesh.polygons])}
    before = state()
    image_hashes = {i.name: digest(i.pixels[:]) for i in bpy.data.images if i.type == 'IMAGE'}
    count = install(body)
    scene = bpy.context.scene; camera = scene.camera
    scene.render.engine = 'BLENDER_EEVEE_NEXT'; scene.eevee.taa_render_samples = 1
    scene.render.resolution_x = 448; scene.render.resolution_y = 448; scene.render.resolution_percentage = 100
    camera.data.ortho_scale = .425; camera.location = (0, -3, 1.655)
    camera.rotation_euler = (Vector((0, -.045, 1.655)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    preview = ROOT / 'previas'; preview.mkdir(exist_ok=True)
    manifest = json.loads((ROOT / 'expressoes.json').read_text())
    for entry in manifest['expressions']:
        set_expression(body, entry['id'])
        for slot in (1, 2):
            value = mesh.materials[slot].node_tree.nodes['DERY | PS1_face_id'].outputs[0].default_value
            assert abs(value - entry['id']) < .001, (entry['id'], value)
        scene.render.filepath = str(preview / f"{entry['id']:02d}_{entry['slug']}.png")
        bpy.ops.render.render(write_still=True)
    set_expression(body, 2)
    camera.location = (1.55, -3, 1.68)
    camera.rotation_euler = (Vector((0, -.045, 1.655)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = str(preview / 'Risada_Tres_Quartos.png'); bpy.ops.render.render(write_still=True)
    set_expression(body, 0)
    configure_preview(scene)
    assert state() == before
    assert all(digest(bpy.data.images[name].pixels[:]) == old for name, old in image_hashes.items())
    bpy.ops.file.pack_all(); bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'Dery_10_Expressoes_PS1.blend'))
    assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
    validation = {'source': '../texturas/encaixe_rosto_v8/' + source.name, 'source_sha256': source_hash,
                  'source_unchanged': True, 'geometry_uvs_shape_keys_weights_assignments_preserved': True,
                  'original_images_unchanged': True, 'expression_selector_checked_ids': list(range(11)),
                  'atlas_samplers': count, 'nearest_sampling': True, 'cell_edge_clamping': True,
                  'neutral_skin_boundary_preserved': True, 'expression_morphing': False,
                  'new_expressions': 10, 'rig_bones': len(next(o for o in bpy.data.objects if o.type == 'ARMATURE').data.bones),
                  'user_authorized_expression_test': True, 'approved_by_user': False}
    (ROOT / 'validacao.json').write_text(json.dumps(validation, ensure_ascii=False, indent=2) + '\n')
    print(validation)

if __name__ == '__main__':
    build()
