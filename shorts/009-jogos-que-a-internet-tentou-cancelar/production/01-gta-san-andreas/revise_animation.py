"""R2: fluid acting, independently baked faces, affine UVs and vertex snapping.

Starts from the preserved R1 Blender/timeline. Does not change any spoken audio,
shots, underlying character geometry or original expression PNGs.
"""
from pathlib import Path
import bpy,sys,json,math,hashlib,wave
import numpy as np
from mathutils import Vector,Quaternion

P=Path(__file__).resolve().parent;REPO=next(p for p in P.parents if(p/'AGENTS.md').exists())
sys.path.insert(0,str(REPO/'assets/personagens/dery'))
from psx_render import bake_faces,install_scene
SOURCE=P/'output/Dery_GTA_San_Andreas_R1.blend'
info=json.loads((P/'timeline_r1.json').read_text());old_fps=info['fps'];FPS=30;factor=FPS/old_fps
source_sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene
actor=bpy.data.objects['DERY | animated character'];shop=bpy.data.objects['GTA | Dery lojista']
rig=actor.parent;store=shop.parent;cam=bpy.data.objects[s['Production | camera']]
s.frame_set(1)
source_vertices={a.name:np.array([tuple(v.co)for v in a.data.vertices],dtype=np.float32)for a in[actor,shop]}
originals={r.name:r.animation_data.action.copy()for r in[rig,store]}
# Every action is retimed once. Texture selectors will be independently baked.
actions=set()
for datablocks in[bpy.data.objects,bpy.data.cameras,bpy.data.node_groups,bpy.data.materials]:
    for obj in datablocks:
        ad=getattr(obj,'animation_data',None)
        if ad and ad.action:actions.add(ad.action)
for action in actions:
    for fc in action.fcurves:
        for key in fc.keyframe_points:
            for point in[key.co,key.handle_left,key.handle_right]:point.x=(point.x-1)*factor+1
        fc.update()
for sh in info['shots']:
    sh['start']=round((sh['start']-1)*factor)+1;sh['end']=round(sh['end']*factor)
info.update(fps=FPS,frames=round(info['duration']*FPS),monitor_file='assets/monitor/monitor_completo_r2.mp4',
            cache='/workspace/attachments/jogos_cancelar_r2',revision=2)
N=info['frames'];s.render.fps=FPS;s.frame_start=1;s.frame_end=N
s.render.engine='CYCLES';s.cycles.samples=1;s.cycles.use_denoising=False;s.render.use_persistent_data=True
s.render.threads_mode='FIXED';s.render.threads=2;s.render.dither_intensity=0
screen=bpy.data.objects['Tela do PC | substituir por vídeo']
tex=next(n for n in screen.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE')
tex.image=bpy.data.images.load(str(P/info['monitor_file']),check_existing=True)
tex.image_user.frame_start=1;tex.image_user.frame_offset=0;tex.image_user.frame_duration=N;tex.image_user.use_auto_refresh=True

def quaternion_at(action,name,oldframe,fallback):
    curves=[action.fcurves.find(f'pose.bones["{name}"].rotation_quaternion',index=i)for i in range(4)]
    return Quaternion([c.evaluate(oldframe)if c else fallback[i]for i,c in enumerate(curves)]).normalized()
def write_curve(owner,path,values,component=0,constant=False):
    if not owner.animation_data:owner.animation_data_create()
    if not owner.animation_data.action:owner.animation_data.action=bpy.data.actions.new(owner.name+' | R2')
    action=owner.animation_data.action
    old=action.fcurves.find(path,index=component)
    if old:action.fcurves.remove(old)
    fc=action.fcurves.new(path,index=component);fc.keyframe_points.add(len(values))
    fc.keyframe_points.foreach_set('co',[x for pair in values for x in pair])
    for key in fc.keyframe_points:key.interpolation='CONSTANT'if constant else'LINEAR'
    fc.update()
def smooth(x):x=max(0,min(1,x));return x*x*x*(10+x*(-15+6*x))
def interpolate(keys,t):
    if t<=keys[0][0]:return np.array(keys[0][1],float)
    if t>=keys[-1][0]:return np.array(keys[-1][1],float)
    k=next(i for i in range(len(keys)-1)if t<keys[i+1][0])
    a,x=keys[k];b,y=keys[k+1];x=np.array(x,float);y=np.array(y,float)
    if np.allclose(x,y):return x
    prev=keys[max(0,k-1)];nxt=keys[min(len(keys)-1,k+2)]
    m0=(y-np.array(prev[1]))/max(.01,b-prev[0])*.55 if k else np.zeros_like(x)
    m1=(np.array(nxt[1])-x)/max(.01,nxt[0]-a)*.55 if k+2<len(keys)else np.zeros_like(x)
    u=(t-a)/(b-a)
    return (2*u**3-3*u*u+1)*x+(u**3-2*u*u+u)*(b-a)*m0+(-2*u**3+3*u*u)*y+(u**3-u*u)*(b-a)*m1

# Each target is forward, outward, vertical offset from shoulder; palm lift/roll.
REST=(.13,.10,-.34,.08,.08)
R=[(0,REST),(2.15,REST),(2.50,(.11,.08,-.35,-.03,.02)),(2.91,(.25,.14,-.18,.68,.55)),
   (3.22,(.26,.15,-.17,.72,.48)),(3.85,(.15,.12,-.30,.18,.16)),
   (4.24,(.15,.11,-.29,.17,.14)),(4.66,(.22,.08,-.10,.92,.65)),(4.95,(.23,.09,-.10,.87,.56)),(5.75,REST),
   (6.45,REST),(6.95,(.24,.13,-.17,.72,.25)),(7.25,(.25,.14,-.18,.68,.30)),(8.30,REST),
   (9.5,REST),(10.75,(.30,.19,-.10,.91,.28)),(11.15,(.29,.20,-.09,.86,.34)),(12.7,(.23,.15,-.21,.55,.18)),(13.8,REST),
   (18.9,REST),(19.45,(.21,.15,-.12,.95,.52)),(19.92,(.20,.16,-.13,.87,.55)),(21.40,REST),
   (43.1,REST),(43.75,(.24,.19,-.16,.76,.85)),(44.13,(.25,.20,-.17,.72,.80)),
   (45.25,(.20,.11,-.21,.57,.28)),(46.0,(.23,.15,-.17,.80,.45)),(47.5,REST),
   (48.3,REST),(48.9,(.23,.12,-.20,.50,.68)),(49.3,(.24,.13,-.20,.55,.75)),
   (50.2,(.16,.12,-.28,.22,.15)),(51.0,(.20,.15,-.18,.71,.38)),(51.4,(.20,.15,-.18,.68,.32)),(52.2,REST),(53.4,REST)]
L=[(0,REST),(3.7,REST),(4.23,(.18,.14,-.25,.25,.45)),(4.55,(.18,.14,-.25,.27,.40)),(5.4,REST),
   (6.8,REST),(7.43,(.20,.19,-.18,.60,.80)),(7.85,(.21,.18,-.19,.56,.73)),(8.8,REST),
   (10.6,REST),(11.4,(.21,.14,-.23,.45,.42)),(11.8,(.22,.14,-.23,.45,.40)),(12.7,REST),
   (19.5,REST),(20.15,(.20,.17,-.16,.72,.58)),(20.55,(.21,.17,-.16,.65,.58)),(21.6,REST),
   (43.5,REST),(44.25,(.20,.20,-.19,.58,.75)),(44.65,(.21,.20,-.18,.63,.71)),(45.6,(.16,.13,-.28,.26,.25)),
   (46.4,(.19,.15,-.24,.48,.45)),(47.7,REST),(49.0,REST),(49.6,(.20,.16,-.23,.43,.65)),
   (50.0,(.21,.16,-.23,.46,.60)),(51.1,REST),(53.4,REST)]
STAND=(.13,.11,-.39,.05,.10)
SR=[(0,STAND),(21.9,STAND),(22.45,(.25,.17,-.18,.84,.64)),(22.85,(.27,.18,-.17,.90,.67)),(23.7,STAND),
    (25.1,STAND),(25.7,(.23,.13,-.16,.91,.40)),(26.1,(.24,.14,-.17,.87,.44)),(26.8,STAND),
    (27.7,STAND),(28.35,(.24,.21,-.21,.75,.80)),(28.7,(.25,.22,-.22,.70,.85)),(29.9,STAND),
    (30.7,STAND),(31.5,(.27,.13,-.18,.76,.55)),(31.95,(.28,.14,-.19,.73,.52)),(33,STAND),(53.4,STAND)]
SL=[(0,STAND),(23.2,STAND),(23.8,(.19,.17,-.22,.65,.80)),(24.25,(.20,.18,-.23,.63,.73)),(25.25,STAND),
    (27.1,STAND),(27.8,(.22,.20,-.20,.80,.75)),(28.15,(.23,.20,-.21,.73,.67)),(29.25,STAND),
    (31.3,STAND),(32.05,(.21,.16,-.23,.60,.70)),(32.45,(.22,.15,-.24,.57,.64)),(33.6,STAND),(53.4,STAND)]

metrics={}
for r,targets in[(rig,{'R':R,'L':L}),(store,{'R':SR,'L':SL})]:
    s.frame_set(1);bpy.context.view_layer.update()
    basis=r.matrix_world.to_quaternion();fwd=basis@Vector((0,-1,0));lateral=basis@Vector((1,0,0));up=Vector((0,0,1))
    shoulders={side:r.matrix_world@r.pose.bones['arm_'+side].head for side in['R','L']}
    for side,sign in [('R',-1),('L',1)]:
        forearm=r.pose.bones['forearm_'+side]
        ik=next((c for c in forearm.constraints if c.type=='IK'),None)
        if not ik:
            target=bpy.data.objects.new('R2 | shop wrist '+side,None);s.collection.objects.link(target)
            ik=forearm.constraints.new('IK');ik.target=target;ik.chain_count=2;ik.use_stretch=False
        else:target=ik.target
        hand=r.pose.bones['hand_'+side]
        rotation=next((c for c in hand.constraints if c.type=='COPY_ROTATION'),None)
        if not rotation:
            palm=bpy.data.objects.new('R2 | shop palm '+side,None);s.collection.objects.link(palm)
            palm.rotation_mode='QUATERNION';palm.rotation_quaternion=(r.matrix_world@hand.matrix).to_quaternion()
            rotation=hand.constraints.new('COPY_ROTATION');rotation.target=palm;rotation.owner_space='WORLD';rotation.target_space='WORLD'
        else:palm=rotation.target
        q0=palm.rotation_quaternion.copy();palm.rotation_mode='QUATERNION'
        location_keys=[[]for _ in range(3)];rotation_keys=[[]for _ in range(4)];max_distance=0
        for frame in range(1,N+1):
            t=(frame-1)/FPS;fw,out,z,lift,roll=interpolate(targets[side],t)
            # Wrist paths have a small curved follow-through, not a straight
            # robotic piston; the envelope vanishes at the neutral resting pose.
            activity=max(0,min(1,(z-(-.39 if r==store else-.34))/.22))
            follow=math.sin(t*3.4+(0 if side=='R'else.9))*.005*activity
            delta=fwd*(fw+follow)+lateral*(sign*out)+up*z
            reach=delta.length
            if reach>.410:delta*=.410/reach
            max_distance=max(max_distance,delta.length)
            drift=lateral*(math.sin(t*1.45)*.004)+up*(math.sin(t*1.7)*.002)
            p=shoulders[side]+delta+drift
            q=Quaternion(lateral,-float(lift))@q0@Quaternion((0,1,0),sign*float(roll))
            for i in range(3):location_keys[i].append((frame,p[i]))
            for i in range(4):rotation_keys[i].append((frame,q[i]))
        for i,k in enumerate(location_keys):write_curve(target,'location',k,i)
        for i,k in enumerate(rotation_keys):write_curve(palm,'rotation_quaternion',k,i)
        metrics[r.name+' '+side]=dict(max_wrist_distance=max_distance,arm_length=forearm.length+r.pose.bones['arm_'+side].length)
    original=originals[r.name]
    for name in['waist','spine','chest','upper_chest','neck','head']:
        pb=r.pose.bones.get(name)
        if not pb:continue
        rest=pb.bone.matrix_local.to_quaternion();fallback=pb.rotation_quaternion.copy();keys=[[]for _ in range(4)]
        for frame in range(1,N+1):
            t=(frame-1)/FPS;oldframe=t*old_fps+1
            q=quaternion_at(original,name,oldframe,fallback)
            if name in['chest','upper_chest']:
                pitch=.011*math.sin(t*1.72)+.007*math.sin(t*.63+.8)
                roll=.008*math.sin(t*1.13+.6)
            elif name=='head':
                # Tiny delayed nod/tilt overlaps the larger gaze already in R1.
                pitch=.020*math.sin((t-.09)*2.25)*(.55+.45*math.sin(t*.4)**2)
                roll=.014*math.sin((t-.14)*1.35+.6)
            elif name=='neck':pitch=.005*math.sin(t*1.7-.12);roll=.004*math.sin(t*1.13)
            else:pitch=.004*math.sin(t*.9);roll=.006*math.sin(t*1.12+.15)
            q=q@(rest.inverted()@Quaternion((1,0,0),pitch)@Quaternion((0,1,0),roll)@rest)
            for i in range(4):keys[i].append((frame,q[i]))
        for i,k in enumerate(keys):write_curve(r,f'pose.bones["{name}"].rotation_quaternion',k,i)

# Bake expression selectors into the actual material. Merely checking that the
# actor property changes was insufficient: R1's seated material stayed at 31.
families=json.loads((REPO/'assets/personagens/dery/expressions_ps1/v3/fala_familias.json').read_text())
with wave.open(str(P/'assets/voz/voz_timeline.wav'))as w:
    rate=w.getframerate();voice=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(float)/32768
def mouth_at(t):
    x=voice[int(t*rate):int((t+.04)*rate)]
    if not len(x)or np.sqrt(np.mean(x*x))<.020:return'fechada_mbp'
    power=np.abs(np.fft.rfft(x*np.hanning(len(x)),n=2048))**2
    freq=np.fft.rfftfreq(2048,1/rate);total=power.sum()+1e-12
    high=power[freq>3500].sum()/total
    if high>.28:return'labio_fv'if high>.45 else'bico_ch'
    low=(freq>180)&(freq<950);upper=(freq>950)&(freq<2700)
    f1=float(np.sum(freq[low]*power[low])/(power[low].sum()+1e-12))
    f2=float(np.sum(freq[upper]*power[upper])/(power[upper].sum()+1e-12))
    if f1>520:return'aberta_a'
    if f2>1750:return'estreita_i'if f1<380 else'larga_e'
    if f2<1330:return'pequena_u'if f1<380 else'redonda_o'
    return['larga_e','entreaberta_dtn','lingua_l'][int(t*7.3)%3]
face_metrics={}
for a,is_shop in[(actor,False),(shop,True)]:
    keys=[]
    for frame in range(1,N+1):
        t=(frame-1)/FPS
        mood=('neutra'if t<24 else'irritada'if t<30.65 else'alegre')if is_shop else('sarcastica'if 6.55<=t<9.2 or t>=48.35 else'irritada'if 18.95<=t<21.85 else'empolgada'if t<6.55 else'neutra')
        # Discrete mouth holds at 15 Hz; the body moves at 30 Hz.
        held_t=math.floor(t*15)/15;value=families[mood][mouth_at(held_t)]
        reactions=[(27.7,28.1,106),(29.6,30.15,115),(34.1,34.55,96)]if is_shop else[(6.6,6.82,84),(8.85,9.17,107),(19.08,19.30,111),(21.45,21.80,105),(43.45,43.65,118),(47.9,48.25,107),(51.8,52.35,122)]
        for begin,end,index in reactions:
            if begin<=t<end:value=index
        for blink in([22.9,26.4,32.7]if is_shop else[3.55,11.8,20.85,44.65,50.75]):
            if blink<=t<blink+.10:value=10
        keys.append((frame,value))
    write_curve(a,'["PS1_face_id"]',keys,constant=True)
    bake_faces(a,keys)
    face_metrics[a.name]=dict(unique_ids=len({v for _,v in keys}),changes=sum(a[1]!=b[1]for a,b in zip(keys,keys[1:])),material_baked=True)

# Slow physical pushes generate genuine changes in projected vertices/UVs.
# They replace no shot and add no arbitrary oscillation of the frame.
for owner in[cam,cam.data]:
    if owner.animation_data and owner.animation_data.action:
        for fc in owner.animation_data.action.fcurves:
            for key in fc.keyframe_points:key.interpolation='CONSTANT'
positions=[[]for _ in range(3)]
for sh in info['shots']:
    s.frame_set(sh['start']);start=cam.location.copy();forward=cam.rotation_euler.to_quaternion()@Vector((0,0,-1))
    distance=.035 if sh['kind']in['host','close','shop']else .018 if sh['kind']=='archive'else 0
    for frame in range(sh['start'],sh['end']+1):
        u=(frame-sh['start'])/max(1,sh['end']-sh['start']);p=start+forward*(distance*smooth(u))
        for i in range(3):positions[i].append((frame,p[i]))
for i,k in enumerate(positions):write_curve(cam,'location',k,i,constant=False)
projection=install_scene(s,cam,[actor,shop],width=320,height=180)
s.frame_set(121);bpy.context.view_layer.update()
for a in[actor,shop]:
    assert np.array_equal(np.array([tuple(v.co)for v in a.data.vertices],dtype=np.float32),source_vertices[a.name])
for image in bpy.data.images:
    if image.source=='FILE'and not image.packed_file and image.filepath:image.filepath=bpy.path.abspath(image.filepath)
bpy.ops.file.pack_all();bpy.ops.file.make_paths_relative()
s['Production | revision']=2;s['Production | acting']='30fps fluid wrist arcs and overlap; independent constant PNG material keys.'
s['Production | PSX']=json.dumps(projection)
dest=P/'output/Dery_GTA_San_Andreas.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_sha
(P/'timeline.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n')
edit=json.loads((P/'edicao.json').read_text());edit['animation_fps']=FPS
(P/'edicao.json').write_text(json.dumps(edit,ensure_ascii=False,indent=2)+'\n')
report=dict(revision=2,fps=FPS,frames=N,duration=info['duration'],source_model=SOURCE.name,source_sha256=source_sha,
    source_meshes_unchanged=True,voice_changed=False,expression_fix='Material values baked with Constant keys; no object-dependent driver.',
    faces=face_metrics,wrists=metrics,projection=projection,camera_motion='slow physical pushes, no shake')
(P/'revisao_r2.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('R2_SCENE_READY',json.dumps(report,ensure_ascii=False),flush=True)
