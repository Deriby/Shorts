# Warm goodbye: use the existing kiss/wink and smile PNGs, without new props.
D=json.loads((P/'direcao.json').read_text())
for frame,value in list(keys):
 t=(frame-1)/30
 for begin,end,index in D['faces']:
  if begin<=t<end:
   keys[frame-1]=(frame,index);actor['PS1_face_id']=index;actor.keyframe_insert('["PS1_face_id"]',frame=frame)
bake_faces(actor,keys)
