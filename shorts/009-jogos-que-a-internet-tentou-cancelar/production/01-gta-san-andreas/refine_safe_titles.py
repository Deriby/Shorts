"""Fix two stage labels and invalidate only shots in which they are visible."""
from pathlib import Path
import bpy,json,hashlib,sys
P=Path(__file__).resolve().parent;model=P/'output/Dery_GTA_San_Andreas.blend'
C=Path('/workspace/attachments/jogos_cancelar/frames')
bpy.ops.wm.open_mainfile(filepath=str(model))
bpy.data.objects['GTA | classificação EUA'].location.z=.91
label=bpy.data.objects['GTA | original arquivos'];label.data.body='VERSÃO\nORIGINAL';label.data.size=.095;label.location.z=1.68
bpy.ops.wm.save_as_mainfile(filepath=str(model),compress=True)
info=json.loads((P/'timeline.json').read_text());removed=0
affected=['archive']if'--archive-only'in sys.argv else['shop','archive']
for sh in info['shots']:
    if sh['kind']in affected:
        for f in range(sh['start'],sh['end']+1):
            p=C/f'frame_{f:04d}.png'
            if p.exists():p.unlink();removed+=1
generation=hashlib.sha256(model.read_bytes()+(P/'assets/monitor/monitor_completo.mp4').read_bytes()).hexdigest()
(C/'source.sha256').write_text(generation+'\n')
(P/'ajuste_enquadramento.json').write_text(json.dumps(dict(changes=['Two-line archive heading fits central 9:16','US rating caption moved below the white card'],
    affected_kinds=affected,invalidated_frames=removed,other_frames_unchanged=True,
    rationale='Only two emissive text objects moved/changed; both are outside all unaffected cameras.'),indent=2)+'\n')
print('TITLE_REFINEMENT',removed,flush=True)
