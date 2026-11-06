# Personagens que a internet estragou — Mercy

Nono bloco, produzido com o pacote “9 - Mercy.zip” enviado pelo usuário. Versões **9:16 em 1080×1920 e 16:9 em 1920×1080**, 24 fps, **29 segundos**. A gravação decodificada tem 28,325 segundos e foi preservada inteira, sem mudar velocidade, tom ou falas. O restante é silêncio final.

## Montagem e atuação

Os 17 planos alternam identificação, quarto gamer, memes recebidos, asas tecnológicas, cura, ressurreição e baia de triagem. O biombo atravessa o quadro e revela a sala em verde e creme. No terminal, uma prévia autoral inteiramente censurada dá lugar ao verbete “MERCY — MISERICÓRDIA”. O selo “INDEFERIDO” entra no início do fechamento. Dery retira a mão da apresentação e termina sério, conforme a gravação. Não há falas adicionais nem legendas da narração.

Os gestos acompanham as frases: entusiasmo inicial, explicação, apresentação interrompida, constrangimento, palma para o verbete e retorno ao repouso. Os braços têm tempos diferentes, preparação, sustentação e retorno. As 31 faces PNG mudam por corte, sem morphs. A referência pessoal de gestos permanece privada.

A cópia sentada preserva a pose avaliada completa do rig original, incluindo o resultado dos controles das pernas, antes da remoção de constraints. As matrizes locais são reconstruídas com `Bone.convert_local_to_pose`. As verificações comparam os pés da cópia aos do original transladado e conferem estabilidade do quadril, alcance dos braços, malha e costuras do rosto. A camiseta preta com M amarelo, a pele limpa e a geometria original foram mantidas.

A triagem adapta a sala de reunião e acrescenta mesa, teclado, terminal, cadeira, biombo e coração autoral. A ficha é uma metáfora sobre o pedido de misericórdia, sem prontuário de paciente ou documento da Blizzard. As três telas são texturas fixas com trocas discretas; não dependem de um segundo filme do monitor.

## Mídias

O vídeo “Mercy Ability Overview” fornece a identificação com asas em 7,2–10,5 s, a cura amarela do Caduceus Staff em 17–23 s e a ressurreição de aliados caídos em 68–72,5 s. A montagem usa intervalos desses recortes, registrados em `timeline.json`. A demonstração é do Overwatch original; não foi usada a amplificação azul de dano para ilustrar cura.

Os dois vídeos recebidos mostram a mesma demonstração em resoluções diferentes; a versão 1080p foi selecionada. Os retratos normais e os memes de sorriso e suporte foram enviados pelo usuário. A fanart de casal não foi usada. Biombo, coração, censura opaca, verbete e selo são gráficos próprios. Os áudios dos vídeos estão mutados: a trilha final contém somente a gravação do usuário.

## Arquivos

- `output/Mercy_Personagens_que_a_internet_estragou_9x16.mp4` e `output/Mercy_Personagens_que_a_internet_estragou_16x9.mp4`: finais.
- `output/Dery_Mercy.blend` e `output/Dery_Mercy_Master_16x9.blend`: quarto, triagem, rig, faces, atuação e voz.
- `assets/voz/voz_original.mp3`: recebido, preservado byte a byte. Os WAVs são a decodificação e a cópia com silêncio final.
- `assets/gameplay/`: recortes selecionados e feed sincronizado. `assets/memes/`: mídias preparadas e gráficos próprios.
- `timeline.json`, `acting_cues.json`, `face_cues.json`: cortes, gestos, expressões e estados do terminal.
- `source_manifest.json`: fontes, hashes, intervalos e escolhas editoriais.
- `scene_validation*.json`, `export_validation*.json`: verificações da cena, voz e MP4.
- [Baia de triagem reutilizável](../../../../assets/cenarios/baia_triagem/): sem personagem, voz ou mídia do pacote; displays neutros.

## Visual e reprodução

Render nativo 360×640 / 640×360, ampliação inteira 3× por vizinho mais próximo, precisão reduzida de geometria com proteção das costuras do rosto, texturas Closest, corpo endereçado em 128 px, piso de 32 px, paleta RGB de 5 bits e Bayer fixo 4×4. Sem blur, glitch ou piscadas aleatórias. As interfaces e as câmeras têm composições próprias por formato.

Na raiz do repositório, com Blender 4.3, FFmpeg, NumPy e Pillow:

```sh
blender -b -t 2 --python-exit-code 1 --python shorts/008-personagens-que-a-internet-estragou/production/09-mercy/build_short.py
blender -b shorts/008-personagens-que-a-internet-estragou/production/09-mercy/output/Dery_Mercy.blend -t 1 --python-exit-code 1 --python shorts/008-personagens-que-a-internet-estragou/production/09-mercy/verify_scene.py
python shorts/008-personagens-que-a-internet-estragou/production/09-mercy/export_short.py
python shorts/008-personagens-que-a-internet-estragou/production/09-mercy/verify_export.py
```

Para o horizontal, adicionar `-- --wide` aos comandos Blender e `--wide` aos scripts Python; carregar `Dery_Mercy_Master_16x9.blend` na verificação. `--resume` retoma quadros completos e `--encode-only` codifica os existentes. O padrão refaz os planos 3D. Usar um formato por vez, com dois threads; gameplay, imagens e gráficos entram diretamente na montagem.

`prepare_assets.py` requer o inventário privado e os originais restaurados. As mídias preparadas necessárias ao projeto e ao render ficam versionadas. Baixar a pasta inteira para editar: áudio e filmes usam caminhos relativos. ZIP, backups, quadros intermediários e referência pessoal permanecem fora do Git.
