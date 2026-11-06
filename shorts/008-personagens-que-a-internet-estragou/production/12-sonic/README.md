# Personagens que a internet estragou — Sonic

Décimo segundo e último bloco da seleção, produzido com o pacote “12 - Sonic.zip” enviado pelo usuário. Versões **9:16 em 1080×1920 e 16:9 em 1920×1080**, 24 fps, **34,958 segundos**. A voz decodificada tem 34,269 segundos e foi preservada inteira, sem mudar velocidade, tom ou falas. O restante é silêncio final.

## Montagem e atuação

Os 20 planos acompanham a identificação de Sonic, o arquivo do fandom, fanart, fangame, animação, fanfic, pesquisa oculta, reação com três cartões “?” e arcade de terror. O encerramento mantém “pela internet a fora”, sem retomar Sonic Feio, trailer de 2019, redesign, Tico e Teco ou a antiga piada de fracasso.

Dery apresenta a personagem, enumera com braços em tempos diferentes, sustenta a hesitação, interrompe a indicação da pesquisa e para com uma face de susto em “meu cérebro explodiu”. Os três cartões saem uma única vez por composição gráfica; o boné e a malha permanecem intactos. A pesquisa é uma interface autoral com resultados inteiramente ocultos. Não há imagens fetichistas ou closes de pés.

O corte para o arcade revela Dery em pé junto de um gabinete com vermelho fixo e tela “SONIC.EXE — FEITO POR FÃS”. Ele percebe a tela, recua levemente o tronco sem mover os pés, indica “SAIR” e deixa o menu encerrar. A tela usa três imagens fixas com trocas discretas; não depende de outro filme compartilhado. O menu é ilustrativo, sem se passar pela interface do jogo original.

As 31 faces PNG mudam por corte, sem morphs. A camiseta preta com M amarelo, pele limpa, mangas e geometria do avatar foram mantidas. Os gestos têm preparação, sustentação, retorno e repouso; não há loop periódico de conversa ou contato com controles. A referência pessoal de gestos permanece privada.

O ator do arcade reaproveita a pose em pé validada da Ankha. A validação compara os pés aos do rig aprovado, vinculado e avaliado, e verifica estabilidade do quadril, alcance dos braços, costuras do rosto, precisão PS1 e estados do menu. O Dery do quarto conserva sua pose sentada original.

## Mídias e contexto

“Sonic Dash - Gameplay and Launch Trailer” fornece a corrida normal em 20–25,5 s. “Sonic Freedom - Full Gameplay” fornece um exemplo de fangame em 26,4–30 s. Os intervalos efetivamente montados estão em `timeline.json`. Freedom ilustra a categoria de criação de fãs; a montagem não afirma que esse jogo específico seja adulto ou bizarro. O insert recebe identificação de fãs.

A fanart normal, o meme do anel, a imagem de Sonic.exe e a montagem de variantes foram enviados pelo usuário. A fanart foi recortada para remover a interface social. Sonic.exe e as variantes são criações de fãs, sem atribuição à SEGA. O vídeo de Shin Sonic não é usado como demonstração de Sonic.exe. As imagens com foco em pés, o meme de violência contra órfãos e o meme de fracasso não entram na montagem.

Todos os vídeos estão mutados. A trilha final contém somente a gravação do usuário, sem voz adicional, susto sonoro, legenda da narração, gore ou efeito de glitch.

## Arquivos

- `output/Sonic_Personagens_que_a_internet_estragou_9x16.mp4` e `output/Sonic_Personagens_que_a_internet_estragou_16x9.mp4`: finais.
- `output/Dery_Sonic.blend` e `output/Dery_Sonic_Master_16x9.blend`: quarto, arcade, rig, faces, atuação e voz.
- `assets/voz/voz_original.mp3`: recebido, preservado byte a byte. Os WAVs são a decodificação e a cópia com silêncio final.
- `assets/gameplay/`: recortes e feed sincronizado. `assets/memes/`: mídias preparadas e interfaces próprias.
- `timeline.json`, `acting_cues.json`, `face_cues.json`: cortes, gestos, expressões, efeito gráfico e estados do menu.
- `source_manifest.json`: fontes, hashes, intervalos e escolhas editoriais.
- `scene_validation*.json`, `export_validation*.json`: verificações da cena, áudio e MP4.
- [Arcade de terror reutilizável](../../../../assets/cenarios/arcade_terror/): sem personagem ou mídia do pacote; tela neutra.

## Visual e reprodução

Render nativo 360×640 / 640×360, ampliação inteira 3× por vizinho mais próximo, precisão reduzida de geometria com proteção das costuras do rosto, texturas Closest, corpo endereçado em 128 px, concreto de 64 px, paleta RGB de 5 bits e Bayer fixo 4×4. Sem blur, glitch ou piscadas aleatórias. Câmeras e interfaces têm composições próprias por formato.

Na raiz do repositório, com Blender 4.3, FFmpeg, NumPy e Pillow:

```sh
blender -b -t 2 --python-exit-code 1 --python shorts/008-personagens-que-a-internet-estragou/production/12-sonic/build_short.py
blender -b shorts/008-personagens-que-a-internet-estragou/production/12-sonic/output/Dery_Sonic.blend -t 1 --python-exit-code 1 --python shorts/008-personagens-que-a-internet-estragou/production/12-sonic/verify_scene.py
python shorts/008-personagens-que-a-internet-estragou/production/12-sonic/export_short.py
python shorts/008-personagens-que-a-internet-estragou/production/12-sonic/verify_export.py
```

Para o horizontal, adicionar `-- --wide` aos comandos Blender e `--wide` aos scripts Python; carregar `Dery_Sonic_Master_16x9.blend` na verificação. `--resume` retoma quadros completos e `--encode-only` codifica os existentes. O padrão refaz os planos 3D. Renderizar um formato por vez, com dois threads; gameplay e imagens entram diretamente na montagem.

`prepare_assets.py` requer o inventário privado e os originais restaurados. As mídias preparadas necessárias ao projeto ficam versionadas. Baixar a pasta inteira para editar: áudio e filmes usam caminhos relativos. ZIP, backups, quadros intermediários e referência pessoal ficam fora do Git.
