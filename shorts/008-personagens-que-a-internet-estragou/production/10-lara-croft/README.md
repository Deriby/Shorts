# Personagens que a internet estragou — Lara Croft

Décimo bloco, produzido com o pacote “10 - Lara Croft.zip” enviado pelo usuário. Versões **9:16 em 1080×1920 e 16:9 em 1920×1080**, 24 fps, **37,333 segundos**. A voz decodificada tem 36,658 segundos e foi preservada inteira, sem mudar velocidade, tom ou falas. O restante é silêncio final.

## Montagem e atuação

Os 20 planos acompanham a Lara clássica, os anos 90, exploração, templo, dinossauro, trocadilho dos polígonos, boato do código, mod de PC e terminal nas ruínas. A janela fictícia “CÓDIGO SECRETO?” é interrompida por “BOATO”. A pasta “Nude Raider” aparece identificada como mod de fãs para PC, com a prévia inteiramente opaca. Não há demonstração do mod no PS1.

A virada revela Dery sentado numa ruína com um computador e um baú aberto de moedas ao lado. Ele olha o tesouro, volta ao terminal e apresenta uma palma de incredulidade. O rosto irritado fecha “meia dúzia de polígonos”. O baú permanece estático; não há contato de mãos, abertura simulada ou nova roupa. A gag mantém a versão revisada pelo usuário, sem acrescentar fala ou recuperar os finais antigos sobre dinossauro ou Paint.

Os gestos acompanham cada intenção, com preparação, sustentação, retorno e tempos diferentes entre os braços. As 31 faces PNG mudam por corte, sem morphs. A camiseta preta com M amarelo, pele limpa, mangas e geometria do Dery foram preservadas. A referência pessoal de gestos permanece privada.

A cópia sentada conserva a pose avaliada completa do rig original, incluindo o resultado dos controles das pernas, antes da remoção de constraints. As matrizes locais são reconstruídas com `Bone.convert_local_to_pose`. A validação compara os pés aos do original transladado e confere estabilidade do quadril, alcance dos braços, costuras do rosto e precisão PS1.

## Mídias e contexto

O trailer “Tomb Raider - Kingdom” é um nível feito por fã e fornece a caminhada em cenário de pedra em 14–19 s. “Insane Details in 1998 PS1 Game!” fornece um trecho de movimentação clássica, com Lara escalando um portão gradeado em 109,5–115 s. Os intervalos efetivamente montados estão em `timeline.json`. São imagens ilustrativas de jogo com Lara vestida, sem atribuir esses níveis ao primeiro Tomb Raider.

Os clipes recebidos não estabelecem um encontro com dinossauro. Essa fala recebe uma placa autoral de T-Rex, sem rotular outro animal como dinossauro. Os memes de rosto, Lara clássica e Lara/Gretchen foram enviados pelo usuário. A cinemática do chuveiro, o meme com foco no torso e o retrato moderno não foram usados. As janelas do código, a refutação e a pasta censurada são gráficos próprios.

Os vídeos de origem estão mutados; a trilha final contém somente a gravação do usuário. Não há voz adicional nem legendas da narração.

## Arquivos

- `output/Lara_Personagens_que_a_internet_estragou_9x16.mp4` e `output/Lara_Personagens_que_a_internet_estragou_16x9.mp4`: finais.
- `output/Dery_Lara.blend` e `output/Dery_Lara_Master_16x9.blend`: quarto, ruína, rig, faces, atuação e voz.
- `assets/voz/voz_original.mp3`: recebido, preservado byte a byte. Os WAVs são a decodificação e a cópia com silêncio final.
- `assets/gameplay/`: recortes selecionados e feed sincronizado. `assets/memes/`: imagens preparadas e gráficos próprios.
- `timeline.json`, `acting_cues.json`, `face_cues.json`: cortes, gestos e expressões.
- `source_manifest.json`: fontes, hashes, intervalos e escolhas editoriais.
- `scene_validation*.json`, `export_validation*.json`: verificações de cena, áudio e MP4.
- [Terminal nas ruínas reutilizável](../../../../assets/cenarios/terminal_ruinas/): sem personagem, voz ou mídia do pacote; display neutro.

## Visual e reprodução

Render nativo 360×640 / 640×360, ampliação inteira 3× por vizinho mais próximo, precisão reduzida de geometria com proteção das costuras do rosto, texturas Closest, corpo endereçado em 128 px, pedra de 32 px, paleta RGB de 5 bits e Bayer fixo 4×4. Sem blur, glitch ou piscadas aleatórias. Câmeras e interfaces têm composições próprias por formato.

Na raiz do repositório, com Blender 4.3, FFmpeg, NumPy e Pillow:

```sh
blender -b -t 2 --python-exit-code 1 --python shorts/008-personagens-que-a-internet-estragou/production/10-lara-croft/build_short.py
blender -b shorts/008-personagens-que-a-internet-estragou/production/10-lara-croft/output/Dery_Lara.blend -t 1 --python-exit-code 1 --python shorts/008-personagens-que-a-internet-estragou/production/10-lara-croft/verify_scene.py
python shorts/008-personagens-que-a-internet-estragou/production/10-lara-croft/export_short.py
python shorts/008-personagens-que-a-internet-estragou/production/10-lara-croft/verify_export.py
```

Para o horizontal, adicionar `-- --wide` aos comandos Blender e `--wide` aos scripts Python; carregar `Dery_Lara_Master_16x9.blend` na verificação. `--resume` retoma quadros completos e `--encode-only` codifica os existentes. O padrão refaz os planos 3D. Renderizar um formato por vez, com dois threads; gameplay e imagens entram diretamente na montagem.

`prepare_assets.py` requer inventário privado e originais restaurados. As mídias preparadas necessárias ao projeto e ao render ficam versionadas. Baixar a pasta inteira para editar: áudio e filmes usam caminhos relativos. ZIP, backups, quadros intermediários e referência pessoal ficam fora do Git.
