"""Still-only fitting study: preserve Dery's nose, fit drawn features, clean light."""
from pathlib import Path
import bpy,numpy as np,math
ROOT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'output/Dery_Crash_Master_R4.blend'))
s=bpy.context.scene;s.frame_set(110)
a=bpy.data.objects['DERY | animated character'];m=a.data
a.animation_data.action=None
def clamp(x):return max(0,min(1,x))
def band(z,lo,hi,edge):return clamp((z-lo)/edge)*clamp((hi-z)/edge)
# The original vertex bake contains high-frequency corner discontinuities. Fit
# only its broad facial light gradient; keep the original room/head illumination.
positions=np.array([v.co[:] for v in m.vertices])
vid=np.array([l.vertex_index for l in m.loops])
colors=np.array([c.color[:] for c in m.color_attributes['PS1Lighting'].data])
total=np.zeros((len(m.vertices),3));counts=np.bincount(vid,minlength=len(m.vertices))
np.add.at(total,vid,colors[:,:3]);total/=np.maximum(1,counts[:,None])
x=positions[:,0]/.1;z=(positions[:,2]-1.55)/.09
basis=np.stack([np.ones(len(x)),x,z,x*x,x*z,z*z],axis=1)
selection=(abs(positions[:,0])<.105)&(positions[:,1]<-.025)&(positions[:,2]>1.465)&(positions[:,2]<1.645)
active=selection.copy()
for _ in range(4):
    coef=np.linalg.lstsq(basis[active],total[active],rcond=None)[0]
    residual=np.linalg.norm(total-basis@coef,axis=1)
    active=selection&(residual<np.quantile(residual[selection],.80))
fit=np.clip(basis@coef,.08,3)
light=m.color_attributes.get('PS1FaceLightFit')or m.color_attributes.new(name='PS1FaceLightFit',type='FLOAT_COLOR',domain='CORNER')
clean=m.color_attributes.get('PS1CleanUnderEyes')or m.color_attributes.new(name='PS1CleanUnderEyes',type='FLOAT_COLOR',domain='CORNER')
# Reacquire UV/color layers after custom-data allocation.
uv=m.uv_layers['DeryFacePS1'];mask=m.color_attributes['DeryFaceMask'];light=m.color_attributes['PS1FaceLightFit'];clean=m.color_attributes['PS1CleanUnderEyes']
for loop in m.loops:
    i=loop.index;v=loop.vertex_index;px,py,pz=positions[v]
    front=clamp((-py-.006)/.028)
    eye=band(pz,1.545,1.637,.014)*clamp((.103-abs(px))/.018)
    mouth=band(pz,1.465,1.531,.009)*clamp((.079-abs(px))/.019)
    # Preserve the actual 3D nose and original skin instead of wrapping the
    # drawing's flat nose and full skin patch over the entire face.
    mask.data[i].color=(max(eye,mouth)*front,)*3+(1,)
    width=.205 if pz>1.545 else .145
    # Shift each painted eye toward the nasal bridge, retaining its scale.
    # Fall off before the brows and nose instead of squeezing the whole face.
    eye_shift=.0075*math.tanh(px/.018)*band(pz,1.552,1.604,.014)
    uv.data[i].uv.x=max(.004,min(.996,(px+eye_shift)/width+.5))
    weight=front*band(pz,1.455,1.65,.018)*clamp((.12-abs(px))/.025)
    rgb=colors[i,:3]*(1-weight)+fit[v]*weight
    light.data[i].color=(*rgb,1)
    undereye=math.exp(-((abs(px)-.044)/.030)**4)*band(pz,1.545,1.573,.006)*front
    clean.data[i].color=(undereye,)*3+(1,)
nt=m.materials[1].node_tree
# Use clear skin from the same drawn texture's outer cheek for the under-eye
# shadows. This is a localized material correction, not a new drawing.
atlas=nt.nodes['PS1 | twelve drawn textures'];vector=atlas.inputs['Vector'].links[0].from_socket
sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(vector,sep.inputs[0])
def mathnode(op,a,b):
    n=nt.nodes.new('ShaderNodeMath');n.operation=op
    for i,v in enumerate([a,b]):
        if isinstance(v,(float,int)):n.inputs[i].default_value=v
        else:nt.links.new(v,n.inputs[i])
    return n.outputs[0]
column=mathnode('FLOOR',mathnode('MULTIPLY',sep.outputs['X'],4),0)
co=nt.nodes.new('ShaderNodeCombineXYZ')
nt.links.new(mathnode('DIVIDE',mathnode('ADD',column,.045),4),co.inputs['X']);nt.links.new(sep.outputs['Y'],co.inputs['Y'])
skin=nt.nodes.new('ShaderNodeTexImage');skin.name='PS1 | clear cheek skin';skin.image=atlas.image;skin.interpolation='Closest';nt.links.new(co.outputs[0],skin.inputs['Vector'])
paint=nt.nodes.new('ShaderNodeVertexColor');paint.layer_name='PS1CleanUnderEyes'
mix=nt.nodes.new('ShaderNodeMixRGB');nt.links.new(paint.outputs['Color'],mix.inputs[0]);nt.links.new(atlas.outputs['Color'],mix.inputs[1]);nt.links.new(skin.outputs['Color'],mix.inputs[2])
for link in list(atlas.outputs['Color'].links):
    if link.to_node!=mix:nt.links.new(mix.outputs[0],link.to_socket)
base=next(n for n in nt.nodes if n.type=='TEX_IMAGE'and n.name!='PS1 | twelve drawn textures')
source=base.inputs['Vector'].links[0].from_socket
snap=nt.nodes.new('ShaderNodeVectorMath');snap.operation='SNAP';snap.inputs[1].default_value=(1/512,1/512,1)
center=nt.nodes.new('ShaderNodeVectorMath');center.operation='ADD';center.inputs[1].default_value=(.5/512,.5/512,0)
nt.links.new(source,snap.inputs[0]);nt.links.new(snap.outputs[0],center.inputs[0]);nt.links.new(center.outputs[0],base.inputs['Vector'])
for node in nt.nodes:
    if node.type=='VERTEX_COLOR' and node.layer_name=='PS1Lighting':node.layer_name='PS1FaceLightFit'
print('FACIAL_LIGHT_FIT',coef.tolist(),flush=True)
for face in [0,3,5]:
    a['PS1_face_id']=face;a.update_tag();bpy.context.view_layer.update()
    s.render.filepath=str(ROOT/'output'/f'preview_fit_face_{face:02d}.png');bpy.ops.render.render(write_still=True)
# Store only a reviewable fitting project; do not replace the published edit.
a['PS1_face_id']=0;s.render.filepath=str(ROOT/'output/preview_fit_face_00.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'output/Dery_Face_Fit_Study.blend'))
bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'output/Dery_Face_Fit_Study.blend'))
print('FACE_FIT_STILLS_READY',flush=True)
