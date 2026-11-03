"""Check wrist constraint targets in rig/world space during the full post gag."""
import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'output/Dery_Terra_Parou.blend'))
s=bpy.context.scene; rig=bpy.data.objects['Dery_Rig']
report=[]
for t in [30.4,31.5,32.6,33.7,35.5,36.8,52.5,54.0]:
    s.frame_set(round(t*24)+1); bpy.context.view_layer.update()
    for side in ['L','R']:
        wrist=rig.matrix_world@rig.pose.bones['hand_'+side].head
        target=bpy.data.objects['IK | wrist '+side].matrix_world.translation
        error=(wrist-target).length
        assert error<.012, (t,side,error)
        report.append({'time':t,'hand':side,'wrist_target_error_m':error})
editor=s.sequence_editor_create()
if not any(strip.name.startswith('FX |') for strip in editor.sequences):
    editor.sequences.new_sound('FX | original quiet foley',str(ROOT/'assets/efeitos_originais.wav'),2,1)
s.frame_set(1)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'output/Dery_Terra_Parou.blend'))
(ROOT/'output/validacao_pegada.json').write_text(json.dumps({'method':'wrist-to-target distance across edited post shots','samples':report},indent=2))
print('GRIP_CHECK_PASS',len(report),'samples; max error',max(p['wrist_target_error_m'] for p in report),'meters')
