from pathlib import Path
import json,zipfile,hashlib,shutil
P=Path(__file__).resolve().parent;R=next(x for x in P.parents if(x/'AGENTS.md').exists());S=P.parent.parent;O=P/'output';F=O/'Filmora';plan=json.loads((P/'montagem.json').read_text());v=json.loads((O/'validacao.json').read_text());report=json.loads((P/'projeto.json').read_text());name='Jogos_Que_A_Internet_Tentou_Cancelar';bundle=O/'Massacote_Completo_Filmora.zip'
instructions='''JOGOS QUE A INTERNET TENTOU CANCELAR — PROJETO COMPLETO 16:9

Abra Massacote_Completo.wfp após extrair este ZIP inteiro. Mantenha midias/ ao lado.
Não abra o WFP diretamente de dentro do ZIP. Se o Filmora pedir um arquivo,
localize-o em midias/; os arquivos têm nomes únicos por capítulo.

Inclui intro, onze jogos e outro. O jogo 10 foi descartado pelo usuário;
Minecraft mantém o número 11 e House Party, o 12.

Voz, música e sons têm faixas próprias. Os cortes de cada trecho continuam
editáveis. As onze vinhetas têm fundo, imagem, título dourado e som em camadas
separadas. O título é um PNG com letras em volume, como nas vinhetas anteriores;
para mudar as palavras, substitua o PNG correspondente. Há Glow nativo apenas
nessa camada, usando o efeito da referência de edição do usuário.

As cenas já aprovadas foram reaproveitadas em 16:9 sem novo render 3D.
Atuação, conteúdo do PC, enquadramentos e zooms da versão aprovada estão
na base de cada capítulo; os cortes dessa base continuam separados. O WFP
usa transformação neutra nesses clipes, evitando duplicar o zoom ou aplicar
um recorte vertical no vídeo longo. Para alterar o 3D, use o Blender original.
Não há legendas novas nas falas nem oscilação artificial da tela.

VoZes/arquivos originais estão preservados. Ajustes leves de volume no WFP
reproduzem a mixagem já aprovada, sem cortes, aceleração ou mudança de pitch.
O MP4 de conferência usa os mesmos quadros dos capítulos e esta mixagem.
A aparência do Glow nativo pode diferir da aproximação no MP4.

Filmora não foi executado neste Linux. Recursos, duração, velocidade 1x,
continuidade, mídia em movimento e estrutura foram conferidos por código;
a abertura nativa precisa ser conferida na sua instalação, com os plugins
pagos que você já utiliza.
'''.replace('VoZes','Vozes')
(F/'LEIA_PRIMEIRO.txt').write_text(instructions)
chapters=['00:00 Intro']
for rec in plan['records']:
 if rec['type']=='card':
  seconds=int(rec['start']/30);chapters.append(f'{seconds//60:02d}:{seconds%60:02d} {rec["title"]}')
 if rec['role']=='outro':
  seconds=int(rec['start']/30);chapters.append(f'{seconds//60:02d}:{seconds%60:02d} Encerramento')
(F/'CAPITULOS.txt').write_text('\n'.join(chapters)+'\n')
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True)as z:
 for p in F.rglob('*'):
  if p.is_file()and(p.suffix.lower()!='.wfp'or p.name==report['project']):z.write(p,str(p.relative_to(F)),compress_type=zipfile.ZIP_STORED if p.suffix.lower()in['.mp4','.png','.ttf']else zipfile.ZIP_DEFLATED)
with zipfile.ZipFile(bundle)as z:
 assert z.testzip()is None;assert len([n for n in z.namelist()if n.endswith('.wfp')])==1
 for path in(F/'midias').iterdir():assert 'midias/'+path.name in z.namelist()
base='https://github.com/Deriby/Shorts/raw/refs/heads/main/'+str(P.relative_to(R))+'/output/'
(P/'README.md').write_text(f'''# Jogos que a internet tentou cancelar — completo 16:9\n\n**9min21,367s**, 1920×1080, 30 fps. Intro + 11 jogos + 11 vinhetas de 2s + outro. O jogo 10 permanece fora.\n\n- [Somente WFP reparado — coloque ao lado de midias/]({base}Filmora/Massacote_Completo.wfp).\n- [Projeto Filmora completo com mídias — ZIP, {bundle.stat().st_size/1e6:.0f} MB]({base}{bundle.name}).\n- [MP4 completo para conferência]({base}{name}_COMPLETO_16x9.mp4).\n- [Prévia das onze vinhetas — 22 segundos]({base}Previa_Vinhetas_16x9.mp4).\n- [Visão geral da montagem](output/Previa_Montagem_Completa.jpg).\n- [Capítulos](output/Filmora/CAPITULOS.txt), [plano](montagem.json) e [conferência](output/validacao.json).\n\nAs cenas aprovadas foram reaproveitadas sem renderizar o 3D novamente. O projeto usa as bases 16:9 com enquadramentos/zooms já aprovados e cortes separados; as transformações nativas são neutras, sem duplicar o zoom. Voz, música e sons têm faixas próprias. Não há legendas novas nas falas.\n\nAs vinhetas usam M amarelo, letras douradas com volume, imagem do jogo/capa e o som curto da referência do usuário. Fundo, imagem, título PNG e som ficam em camadas separadas. Glow nativo somente no título; o MP4 é uma aproximação desse efeito. Os PNGs podem ser substituídos para mudar as palavras.\n\nExtraia o ZIP inteiro antes de abrir o WFP e mantenha `midias/` ao lado dele. Foram conferidos os 13 áudios de voz completos, todos os recursos relativos, velocidade 1×, continuidade, amostras de quadros idênticas aos masters anteriores, áudio exportado (correlação {v['full_audio_correlation']:.6f}), decodificação integral e ZIP. **Filmora não foi aberto neste ambiente**; a validação estrutural não equivale à abertura nativa.\n\nAs produções/fontes originais permanecem intactas. Ordem: GTA San Andreas, BMX XXX, Bully, Left 4 Dead 2, Saints Row IV, GTA V, Pokémon Sword and Shield, Night Trap, Dead or Alive Xtreme 3, Minecraft, House Party.\n\nReprodução no ambiente: `preparar.py`, `montar_projeto.py`, `exportar_previa.py`, `verificar.py`, `empacotar.py`. Cache em `/workspace/attachments/longo009/`. O som de vinheta original pode exigir `git lfs pull` para obter o WAV.\n''')
status=json.loads((S/'ordem_capitulos.json').read_text());status['complete_long']=dict(production_path=str(P.relative_to(S)),duration=plan['duration'],frames=plan['frames'],format='16:9',game_count=11,chapter_cards=11,omitted=[10],project_bundle=str(bundle.relative_to(S)),preview=str((O/(name+'_COMPLETO_16x9.mp4')).relative_to(S)),native_filmora_open=False);(S/'ordem_capitulos.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n')
p=S/'README.md';s=p.read_text();s=s if '## Vídeo completo 16:9'in s else s.replace('## Lote atual — Minecraft, House Party, intro e outro','## Vídeo completo 16:9\n\n**[Projeto Filmora completo com mídias, MP4 e vinhetas](production/14-video-completo/README.md).** Intro, onze jogos e outro, com o jogo 10 descartado.\n\n## Lote atual — Minecraft, House Party, intro e outro',1);p.write_text(s)
(O/'pacote.json').write_text(json.dumps(dict(bundle=bundle.name,bytes=bundle.stat().st_size,sha256=hashlib.sha256(bundle.read_bytes()).hexdigest(),all_media_bundled=True,zip_integrity=True,native_filmora_open=False),indent=2)+'\n');print('COMPLETE_PACKAGE_READY',bundle.stat().st_size,flush=True)
