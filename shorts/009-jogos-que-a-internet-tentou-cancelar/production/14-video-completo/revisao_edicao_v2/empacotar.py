from pathlib import Path
import hashlib
import json
import zipfile

P = Path(__file__).resolve().parent
L = P.parent
R = next(p for p in P.parents if (p / 'AGENTS.md').exists())
F = L / 'output/Filmora'
project = F / 'Massacote_Completo_Editado.wfp'
bundle = L / 'output/Massacote_Completo_Editado_Filmora.zip'
validation = json.loads((P / 'validacao.json').read_text())
instructions = '''JOGOS QUE A INTERNET TENTOU CANCELAR — EDICAO REVISADA 16:9

Abra Massacote_Completo_Editado.wfp depois de extrair este pacote inteiro.
Se ja baixou as midias do projeto anterior, basta colocar este WFP ao lado
da pasta midias. Nao precisa baixar as midias novamente.

112 clipes recebem animacao nativa: aproximacoes, zooms de reacao com entrada
rapida, retornos e movimentos separados nas camadas das onze vinhetas.
As 60 transicoes usam Basic Zoom In, Warp Zoom 6, Fast Bounce, SwingLeft e
SwingRight da sua edicao final do primeiro video longo. Os recursos pagos
dependem da instalacao dos plugins, como no seu projeto de referencia.

Todos os 296 clipes mantem seus tempos, fontes e velocidade. Voz, musica e
sons permanecem separados e identicos ao projeto anterior. As midias sao as
mesmas. Nao ha novas legendas, glitch, tremido global ou outro render 3D.
Interfaces, textos e inserts comicos preservam seu enquadramento anterior.

O quarto com a nova iluminacao/sem fone foi aprovado para futuras producoes.
Esta revisao de edicao reutiliza os videos prontos: nao refaz o cenario antigo
que ja esta nos pixels destes capitulos.

O MP4 completo anterior nao representa os novos keyframes/transicoes.
Exporte este WFP no Filmora para obter a nova edicao. Nao foi executado
Filmora neste Linux. A estrutura, recursos, keyframes, enquadramentos e
registro nativo foram conferidos; a abertura e os plugins ainda precisam
ser verificados no aplicativo.
'''
(F / 'LEIA_EDITADO.txt').write_text(instructions)
files = [project, F / 'CAPITULOS.txt', *sorted((F / 'midias').iterdir()), *sorted((F / 'fontes').iterdir())]
assert all(p.is_file() for p in files)
hashes = {str(p.relative_to(F)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
with zipfile.ZipFile(bundle, 'w', zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as z:
    z.writestr('LEIA_PRIMEIRO.txt', instructions)
    for p in files:
        z.write(p, str(p.relative_to(F)), compress_type=zipfile.ZIP_STORED if p.suffix in ('.mp4', '.png', '.ttf', '.wfp') else zipfile.ZIP_DEFLATED)
with zipfile.ZipFile(bundle) as z:
    assert z.testzip() is None
    assert [n for n in z.namelist() if n.endswith('.wfp')] == [project.name]
    for name, digest in hashes.items():
        assert hashlib.sha256(z.read(name)).hexdigest() == digest
report = dict(bundle=str(bundle.relative_to(R)), bytes=bundle.stat().st_size,
              sha256=hashlib.sha256(bundle.read_bytes()).hexdigest(), files=len(files) + 1,
              media_files=len(list((F / 'midias').iterdir())), all_member_hashes_checked=True,
              one_current_project_only=True, native_filmora_open=False)
(P / 'pacote.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
index = L.parent.parent / 'ordem_capitulos.json'
data = json.loads(index.read_text())
data['complete_long'].update(project_bundle=str(bundle.relative_to(index.parent)),
                             current_project=str(project.relative_to(index.parent)),
                             editorial_revision='keyframes e transicoes v2',
                             previous_mp4_does_not_include_revision=True)
index.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
print('PACKAGE_READY', bundle.stat().st_size, flush=True)
