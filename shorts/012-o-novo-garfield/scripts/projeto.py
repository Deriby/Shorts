"""Projeto Filmora horizontal com as mídias separadas e efeitos nativos."""
import json
from pathlib import Path
import sys
import zipfile

from garfield import P, TED, W, H, TITLE, M, F
sys.path.insert(0,str(TED/'revisao_02/scripts'))
import projeto as native
import entregar as checks

FILM=native.film
FX={
    'Glow':[(4.47,4.77),(13.63,13.93),(58.52,58.80),(118.03,118.33)],
    'Text Vibrate':[(51.02,51.22),(105.92,106.22)],
    'Grunge_Jitter':[(19.13,19.38),(54.60,54.82)],
}
LABELS={
    'voz':'Voz original', 'musica':'Trilha original', 'sfx':'Entradas',
    'saida':'Swooshes de saída','foley':'Acentos', 'meme':'Meme A62',
    0:'Fundo em movimento',1:'Molduras e ficha',2:'Clipes do trailer',3:'Mídia principal',
    4:'Comparações e trechos',5:'Massacote · corpo',6:'Massacote · cabeça',7:'Massacote · bigode',
}


def make(ted_ref,sonic_ref,temp):
    plan=json.loads((P/'timeline.json').read_text())
    FILM.P,FILM.F,FILM.M,FILM.W,FILM.H=P,F,M,W,H
    FILM.LABELS=LABELS
    FILM.OUT=temp/(TITLE+'_16x9.wfp')
    assert all(e['track'] in LABELS for e in plan['events'])
    FILM.write_project(plan)
    files=native.load(FILM.OUT)
    doc=json.loads(files[native.TL])
    native.M=M
    native.EFFECTS=FX
    native.clip_audio(doc,files,native.read_native(ted_ref),plan)
    native.add_effects(doc,native.read_native(sonic_ref))
    files[native.TL]=FILM.data(doc)
    dest=F/FILM.OUT.name
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=4) as out:
        for name,data in files.items():
            out.writestr(name,data)

    checks.M,checks.W,checks.H,checks.EFFECTS=M,W,H,FX
    gains={e['file']:e['mix_gain_db'] for e in plan['events'] if 'mix_gain_db' in e}
    report=checks.verify_wfp(dest,False,gains,plan)
    with zipfile.ZipFile(dest) as z:
        contents=json.loads(z.read(native.META))
        assert contents['project_timeline_ratio']==[16,9]
        assert contents['project_timeline_resolution']==[1920,1080]
        clips=native.clips(native.main_timeline(json.loads(z.read(native.TL))))
        zooms=[c['postTransition']['display'] for c in clips if c.get('postTransition')]
        assert set(zooms)=={'Basic Zoom In','Fast Bounce'}
    report.update(transitions=zooms,aspect_ratio='16:9',resolution=[W,H])
    (P/'validacao_filmora.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False),flush=True)


if __name__=='__main__':
    make(*map(Path,sys.argv[1:]))
