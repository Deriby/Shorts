"""One downloadable archive, with separate editable projects and received media."""
from pathlib import Path
import zipfile,json
from separar import P,OUT,sha

report=json.loads((P/'manifesto.json').read_text())
assert len(report['projects'])==12
instructions='''PROJETOS FILMORA — LADY AO SONIC

Extraia o ZIP inteiro antes de abrir um projeto. Cada pasta tem um WFP separado
em 1080x1920, 60 fps, e uma subpasta midias. Abra o WFP do personagem desejado.

Os projetos usam sua edição concluída como base: cortes, títulos, plugins,
transições, sons e mixagem continuam editáveis. As animações-base foram trocadas
pelas versões verticais originais, com os mesmos tempos e o mesmo áudio.
Os zooms/posições da animação foram adaptados por tipo de cena para o 9:16.
Cada short começa na fala; as vinhetas de passagem e a intro/encerramento do
vídeo longo ficam fora. Uma composição de conteúdo no final da Tifa permanece.

As músicas, sons e recursos que só estavam no seu PC mantêm os caminhos do
projeto original. Consulte FONTES_NO_SEU_PC.txt em cada pasta. Caso peça uma
fonte, localize a mesma mídia usada no vídeo longo. Os plugins pagos continuam
dependendo da sua instalação do Filmora. Este ZIP não é um pacote completo
de todas as fontes externas do seu computador.

A biblioteca e as composições internas originais foram preservadas para não
quebrar IDs/templates. A timeline principal de cada WFP contém apenas seu
personagem, embora o painel de mídias ainda possa listar itens do longo.

Foram conferidos integridade dos projetos, tempos, fontes recebidas, velocidade
e preservação das configurações nativas. O Filmora não foi executado neste
ambiente Linux: a abertura/reprodução nativa ainda precisa ser conferida nele.
Nenhum MP4 final com plugins do Filmora foi exportado aqui.
'''
(OUT/'LEIA_PRIMEIRO.txt').write_text(instructions)
archive=OUT/'Projetos_Filmora_Lady_ao_Sonic_9x16.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True)as z:
    z.writestr('LEIA_PRIMEIRO.txt',instructions)
    z.writestr('MANIFESTO.json',json.dumps(report,ensure_ascii=False,indent=2))
    for rec in report['projects']:
        project=OUT/rec['project'];base=project.parent
        z.write(project,str(project.relative_to(OUT)))
        z.write(base/'FONTES_NO_SEU_PC.txt',str((base/'FONTES_NO_SEU_PC.txt').relative_to(OUT)))
        for media in rec['bundled_media']:
            p=base/'midias'/media['name'];ext=p.suffix.lower()
            z.write(p,str(p.relative_to(OUT)),compress_type=zipfile.ZIP_STORED if ext in ('.mp4','.mp3','.m4a','.jpg','.png')else zipfile.ZIP_DEFLATED)
with zipfile.ZipFile(archive)as z:
    assert z.testzip() is None
    assert sum(n.endswith('.wfp')for n in z.namelist())==12
(P/'pacote.json').write_text(json.dumps({'archive':archive.name,'bytes':archive.stat().st_size,'sha256':sha(archive),'projects':12,'zip_integrity':True},indent=2)+'\n')
print('PACKAGE',archive,archive.stat().st_size,flush=True)
