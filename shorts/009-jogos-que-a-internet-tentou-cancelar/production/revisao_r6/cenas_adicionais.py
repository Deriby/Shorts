"""Executed inside montar_cenas: additional short actions led by the narration."""
def prop_copy(src,name,point,scale=1):
 o=src.copy();o.data=src.data.copy();s.collection.objects.link(o);o.name='R6 | '+name;o.animation_data_clear();o.parent=None;corners=[src.matrix_world@Vector(c)for c in src.bound_box];bottom=Vector(((min(v.x for v in corners)+max(v.x for v in corners))/2,(min(v.y for v in corners)+max(v.y for v in corners))/2,min(v.z for v in corners)));o.data.transform(Matrix.Scale(scale,4)@Matrix.Translation(-bottom)@src.matrix_world);o.matrix_world=Matrix.Translation(Vector(point))
 for m in list(o.modifiers):
  if m.type=='NODES':o.modifiers.remove(m)
 return o

def star(name,center,radius,mat,parent=None):
 points=[(math.sin(i*math.pi/5)*(radius if i%2==0 else radius*.44),0,math.cos(i*math.pi/5)*(radius if i%2==0 else radius*.44))for i in range(10)];o=H.mesh('R6 | '+name,points,[tuple(range(10))],mat,parent);o.location=center;return o

if kind=='arquivos_cafe':
 camera_at(cam,(-.68,-.40,1.40),(-.68,.70,.84),64);yellow=H.material('R6 | pasta amarela',(.65,.39,.055),lit=True);center=Vector((-.68,.70,.782));box('fundo do arquivo',center+Vector((0,0,.004)),(.18,.14,.008),yellow)
 for x in[-.087,.087]:box('lateral do arquivo',center+Vector((x,0,.043)),(.006,.14,.078),yellow)
 for y in[-.067,.067]:box('frente do arquivo',center+Vector((0,y,.043)),(.18,.006,.078),yellow)
 cup=prop_copy(bpy.data.objects['Caneca na mesa'],'café escondido',center+Vector((0,0,.008)),.55);lid=H.empty('R6 | tampa dos arquivos',center+Vector((0,.07,.084)));box('tampa',(0,-.07,0),(.18,.14,.006),yellow,lid)
 labelroot=H.empty('R6 | rótulo',center);text('HOT COFFEE',(0,-.071,.046),.016,black,labelroot)
 for f in range(1,plan['count']+1):u=(f-1)/(plan['count']-1);lid.rotation_euler.x=-1.65*smooth((u-.15)/.55);key(lid,f)
 moving=[lid]
elif kind=='estrelas_cafe':
 camera_at(cam,(-.59,-.42,1.19),(-.588,.458,.90),58);gold=H.material('R6 | procurado',(.95,.65,.025),lit=True);stars=[]
 for i in range(5):stars.append(star('estrela procurado',(-.588+(i-2)*.030,.40,.972),.015,gold))
 for f in range(1,plan['count']+1):
  u=(f-1)/(plan['count']-1)
  for i,o in enumerate(stars):v=smooth((u-i*.09-.08)/.13);o.scale=(max(.001,v),)*3;o.rotation_euler.y=.11*math.sin(u*math.pi*2+i)*v;key(o,f)
 moving=stars
elif kind=='bike_x':
 camera_at(cam,(-.69,-.64,1.32),(-.69,.70,.87),58);root=H.empty('R6 | bicicletinha',(-.69,.70,.782));frame=H.empty('R6 | quadro da bike',(0,0,0),root);wheels=[]
 for sign in[-1,1]:
  w=H.empty('R6 | roda pequena',(sign*.08,0,.04),root);H.torus('R6 | pneu da bike',(0,0,0),.035,.005,black,w,rot=(math.pi/2,0,0),segments=16);H.cylinder('R6 | aro da bike',(0,0,0),.028,.005,metal,w,vertices=12,rot=(math.pi/2,0,0));wheels.append(w)
 A=(-.08,0,.04);B=(.08,0,.04);C=(-.015,0,.045);D=(-.035,0,.105);E=(.050,0,.102)
 for i,(a,b)in enumerate([(A,C),(A,D),(C,D),(D,E),(C,E),(E,B)]):H.beam('R6 | tubo '+str(i),a,b,.006,metal,frame)
 box('selim',(-.038,0,.115),(.036,.017,.009),black,frame);H.beam('R6 | guidão vertical',E,(.06,0,.13),.006,metal,frame);H.beam('R6 | guidão',(.06,-.025,.13),(.06,.025,.13),.006,black,frame)
 crosses=[]
 for x in[-.05,0,.05]:
  o=H.empty('R6 | X físico',(x,0,.23),root);H.beam('R6 | X1',(-.015,0,-.018),(.015,0,.018),.009,red,o);H.beam('R6 | X2',(-.015,0,.018),(.015,0,-.018),.009,red,o);crosses.append(o)
 for f in range(1,plan['count']+1):
  u=(f-1)/(plan['count']-1);fall=smooth((u-.18)/.30);crush=smooth((u-.47)/.22);frame.scale.z=1-.47*crush;key(frame,f)
  for o in crosses:o.location.z=.23-(.23-.148)*fall-.055*crush;key(o,f)
 moving=[frame,*crosses]
elif kind=='disco_grade':
 camera_at(cam,(-.69,-.47,1.26),(-.69,.68,.86),60);center=Vector((-.69,.68,.782));gray=H.material('R6 | grade',(.32,.35,.38),lit=True)
 for x in[-.040,.040]:box('barra da grade',center+Vector((x,0,.092)),(.012,.012,.184),gray)
 box('travessa da grade',center+Vector((0,0,.184)),(.14,.015,.015),gray);disc=H.empty('R6 | CD passa de lado',(-.69,.57,.844));verts=[]
 for z in[-.001,.001]:
  for radius in[.009,.060]:verts.extend([(radius*math.cos(i*math.tau/20),radius*math.sin(i*math.tau/20),z)for i in range(20)])
 faces=[]
 for i in range(20):j=(i+1)%20;faces.extend([(i,j,20+j,20+i),(40+i,60+i,60+j,40+j),(20+i,20+j,60+j,60+i),(i,40+i,40+j,j)])
 H.mesh('R6 | disco',verts,faces,metal,disc);t=text('BULLY',(0,.025,.002),.018,black,disc);t.rotation_euler=(0,0,0)
 for f in range(1,plan['count']+1):
  u=(f-1)/(plan['count']-1);edge=smooth((u-.06)/.22)*(1-smooth((u-.75)/.22));disc.rotation_euler=(math.pi/2,0,math.pi/2*edge);disc.location.y=.57+.22*smooth((u-.29)/.43);key(disc,f)
 moving=[disc]
elif kind=='amor_sequencia':
 camera_at(cam,(-.67,-.63,1.38),(-.67,.70,.92),56);one=gamecase('L4D','1',(-.75,.70,.782),black,white);two=gamecase('L4D','2',(-.40,.70,.782),red,white)
 heart_points=[]
 for i in range(24):
  a=i*math.tau/24;heart_points.append((16*math.sin(a)**3/16*.035,0,(13*math.cos(a)-5*math.cos(2*a)-2*math.cos(3*a)-math.cos(4*a))/17*.035))
 heart=H.mesh('R6 | coração',heart_points,[tuple(range(24))],red);heart.location=(-.75,.68,1.031);anger=H.empty('R6 | irritação',(-.75,.68,1.031))
 for sign in[-1,1]:
  H.beam('R6 | irritação traço',(sign*.005,0,.005),(sign*.023,0,.023),.007,red,anger);H.beam('R6 | irritação traço',(sign*.005,0,-.005),(sign*.023,0,-.023),.007,red,anger)
 for f in range(1,plan['count']+1):
  u=(f-1)/(plan['count']-1);two.location.x=-.40-.19*smooth((u-.18)/.43);pulse=smooth(u/.17)*(1-smooth((u-.55)/.16));heart.scale=(max(.001,pulse),)*3;anger.scale=(max(.001,smooth((u-.61)/.16)),)*3;key(two,f);key(heart,f);key(anger,f)
 moving=[two,heart,anger]
elif kind in['sem_graca','surto']:
 forward=cam.matrix_world.to_quaternion()@Vector((0,0,-1));cam.location+=forward*.64;camera_at(cam,cam.location,rig.matrix_world@rig.pose.bones['head'].center+Vector((0,0,-.13)),66)
 base_neck=rig.pose.bones['neck'].matrix_basis.to_quaternion();base_head=rig.pose.bones['head'].matrix_basis.to_quaternion();keys=[];families=json.loads((R/'assets/personagens/dery/expressions_ps1/v3/fala_familias.json').read_text())
 with wave.open(str(R/'shorts/009-jogos-que-a-internet-tentou-cancelar/production'/plan['episode']/'assets/voz/voz_timeline.wav'))as w:rate=w.getframerate();voice=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(float)/32768
 code=(P.parent/'01-gta-san-andreas/revise_animation.py').read_text();exec(code[code.index('def mouth_at(t):'):code.index('face_metrics={}')])
 for f in range(1,plan['count']+1):
  u=(f-1)/(plan['count']-1);t=(plan['start']+f-2)/30;value=families['neutra'][mouth_at(math.floor(t*15)/15)]
  if kind=='sem_graca':value=14 if u<.26 else 95 if u<.77 else value;angle=.07*math.sin(math.pi*u)
  else:value=105 if .18<u<.46 else 106 if .46<=u<.76 else value;angle=.10*math.sin(3*math.pi*u)*math.sin(math.pi*u)
  for name,q,amount in [('neck',base_neck,.25),('head',base_head,.75)]:
   pb=rig.pose.bones[name];pb.rotation_mode='QUATERNION';pb.rotation_quaternion=q@Quaternion((0,1,0),angle*amount);pb.keyframe_insert('rotation_quaternion',frame=f)
  actor['PS1_face_id']=value;actor.keyframe_insert('["PS1_face_id"]',frame=f);keys.append((f,value))
 bake_faces(actor,keys);moving=[rig]
elif kind=='peticao':
 camera_at(cam,(-.70,-.48,1.13),(-.70,.38,.73),57);paper=H.material('R6 | papel',(.86,.82,.71),lit=True);rows=20
 def paper_coordinates(length):
  vertices=[]
  for i in range(rows):
   d=length*i/(rows-1)
   if d<=.31:y=.58-d;z=.786
   elif d<.31+math.pi*.02/2:a=(d-.31)/.02;y=.27-.02*math.sin(a);z=.786-.02*(1-math.cos(a))
   else:y=.25;z=.766-(d-.31-math.pi*.02/2)
   for x in[-.047,.047]:vertices.append((-.70+x,y,z))
  return vertices
 verts=paper_coordinates(.018);faces=[(2*i,2*i+1,2*i+3,2*i+2)for i in range(rows-1)];strip=H.mesh('R6 | petição desenrolando',verts,faces,paper);strip.shape_key_add(name='Base')
 labelroot=H.empty('R6 | petição ilustrativa');label=text('PETICAO',(-.70,.556,.788),.011,black,labelroot);label.rotation_euler=(0,0,0);lines=[]
 for i in range(9):lines.append(box('assinatura abstrata',(-.70+(-.004 if i%2 else .004),.535-i*.024,.789),(.043+(i%3)*.006,.002,.001),black))
 for f in range(1,plan['count']+1):
  u=(f-1)/(plan['count']-1);v=smooth((u-.08)/.85);shape=strip.shape_key_add(name='Papel '+str(f))
  for point,co in zip(shape.data,paper_coordinates(.018+.622*v)):point.co=co
  for tick,value in[(max(0,f-1),0),(f,1),(f+1,0)]:shape.value=value;shape.keyframe_insert('value',frame=tick)
  label.scale.x=max(.001,smooth((v-.03)/.04));key(label,f)
  for i,o in enumerate(lines):o.scale.x=max(.001,smooth((v-i*.044-.05)/.06));key(o,f)
 moving=[strip]
elif kind=='viagem':
 camera_at(cam,(-.65,-.62,1.48),(-.65,.70,.87),62);root=H.empty('R6 | Pokémon de mala',(-.43,.70,.837));ballroot=H.empty('R6 | bola viajante',(0,0,0),root);ball=sphere('Pokébola de viagem',(0,0,0),(.055,)*3,white,ballroot);ball.data.materials.append(red)
 for p in ball.data.polygons:p.material_index=1 if p.center.z>0 else 0
 H.torus('R6 | faixa da Pokébola',(0,0,0),.055,.004,black,ballroot,segments=16);H.cylinder('R6 | botão da bola',(0,-.055,0),.011,.008,white,ballroot,vertices=10,rot=(math.pi/2,0,0));gold=H.material('R6 | mala amarela',(.72,.43,.07),lit=True);bag=H.empty('R6 | mala',(.115,0,-.004),root);box('mala',(0,0,0),(.064,.052,.078),gold,bag);H.beam('R6 | alça 1',(-.020,0,.041),(-.020,0,.062),.005,black,bag);H.beam('R6 | alça 2',(.020,0,.041),(.020,0,.062),.005,black,bag);H.beam('R6 | alça topo',(-.020,0,.062),(.020,0,.062),.005,black,bag)
 for y in[-.022,.022]:H.torus('R6 | rodinha da mala',(0,y,-.039),.009,.003,black,bag,rot=(math.pi/2,0,0),segments=12)
 H.beam('R6 | puxador',(.045,0,.014),(.095,0,.050),.004,black,root)
 for f in range(1,plan['count']+1):
  u=(f-1)/(plan['count']-1);distance=.34*smooth((u-.05)/.9);root.location.x=-.43-distance;ballroot.rotation_euler.y=distance/.055;key(root,f);key(ballroot,f)
 moving=[root,ballroot]
else:raise ValueError(kind)
