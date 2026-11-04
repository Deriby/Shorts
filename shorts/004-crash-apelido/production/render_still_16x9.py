"""One 16:9 framing study, with Dery and an actual Crash PS1 screenshot.

blender -b -t 4 --python shorts/004-crash-apelido/production/render_still_16x9.py
"""
from pathlib import Path
import runpy, math
import bpy
from mathutils import Vector, Quaternion

ROOT=Path(__file__).resolve().parent
BASE=ROOT.parents[1]/'003-teste-quarto-gamer'/'production'

def pivot(name, objects, location, rotation):
    p=bpy.data.objects.new(name,None)
    bpy.context.scene.collection.objects.link(p)
    p.location=location
    bpy.context.view_layer.update()
    for obj in objects:
        obj.parent=p
        obj.matrix_parent_inverse=p.matrix_world.inverted()
    p.rotation_euler.z=rotation
    return p

def prepare(scene):
    # A creator's desk composition: monitor left, Dery at the right, with
    # independently selectable vertical crops for the two subjects.
    hero=bpy.data.objects['DERY | world motion']
    hero.animation_data_clear()
    hero.rotation_euler.z=.60
    chair=[o for o in scene.objects if o.name.startswith(('chair','seat cushion','caster wheel'))]
    pivot('chair | presenter angle',chair,(0,.10,0),.60)
    rig=bpy.data.objects['Dery_Rig']
    rig.animation_data_clear()
    rest=rig.data.bones['head'].matrix_local.to_quaternion()
    rig.pose.bones['head'].rotation_quaternion=rest.inverted()@Quaternion((0,0,1),.62)@rest
    for mat in bpy.data.objects['Dery_Head'].data.materials:
        mat.node_tree.animation_data_clear()
        for node in mat.node_tree.nodes:
            if node.name.startswith('EXPRESSION | '): node.outputs[0].default_value=0

    monitor=[o for o in scene.objects if o.name.startswith(('CRT ','power LED','monitor buttons'))]
    pivot('CRT | presenter angle',monitor,(0,-.94,.9),-.65)
    tex=next(n for n in bpy.data.materials['monitor | actual moving footage'].node_tree.nodes if n.type=='TEX_IMAGE')
    tex.image=bpy.data.images.load(str(ROOT/'assets/gameplay/crash_ps1_screenshot.png'))
    tex.interpolation='Closest'
    # Front of this +Y-facing quad reads opposite its world X direction.
    for loop in bpy.data.objects['CRT moving picture'].data.uv_layers[0].data:
        loop.uv.x=1-loop.uv.x

    # Put the same channel sign on the wall visible from this camera.
    sign=[bpy.data.objects[n] for n in ['logo backing','channel sign','channel sign small']]
    p=pivot('channel sign | left wall',sign,(.30,1.88,1.95),math.pi/2)
    p.location=(-2.075,.20,1.80)
    camera=scene.camera
    camera.animation_data_clear(); camera.data.animation_data_clear()
    camera.location=(1.90,.02,1.65)
    target=Vector((0,-.15,1.22))
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.sensor_fit='VERTICAL';camera.data.sensor_height=32
    camera.data.lens=44
    camera.data.dof.use_dof=False
    bpy.context.view_layer.update()

if __name__=='__main__':
    runpy.run_path(str(BASE/'render_ps1_still.py'),init_globals={'STILL_CONFIG':{
        'project_root':ROOT,'base_blend':BASE/'output/Dery_Quarto_Gamer_Teste.blend',
        'resolution':(640,360),'vertex_grid':(320,180),'output_resolution':(1920,1080),
        'output':ROOT/'output/Dery_Crash_Previa_16x9.png','samples':48,'prepare_scene':prepare,
    }})
