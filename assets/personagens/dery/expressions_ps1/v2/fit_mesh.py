from pathlib import Path
import bpy,numpy as np,math

def fit_mesh(a):
    m=a.data
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
