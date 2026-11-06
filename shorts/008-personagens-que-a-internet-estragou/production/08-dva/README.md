# Personagens que a internet estragou — D.Va

Oitavo bloco, produzido com o pacote “8 - DVa.zip” enviado pelo usuário. Versões **9:16 em 1080×1920 e 16:9 em 1920×1080**, 24 fps, **41,833 segundos**. A voz decodificada tem 41,177 segundos e foi preservada inteira, sem mudar velocidade, tom ou falas. O restante é silêncio final.

## Montagem e atuação

Os 25 planos acompanham a identificação D.Va/Hana Song, origem como gamer e piloto, propulsão, mísseis, autodestruição, interesse na piloto, traje, censura, aparte sussurrado, cockpit, retirada dos painéis e fechamento em “mas com certeza conhece ela”. Não há legendas da narração embutidas ou voz adicional.

O quarto alterna apresentação curta, palma resignada e um aparte mais próximo da câmera. O trecho sussurrado usa um limiar de energia menor somente para as trocas de face; o áudio não foi alterado. As expressões são as 31 faces PNG com troca seca, sem morphs. Os gestos têm preparação, pausa e retorno, com tempos diferentes entre os braços.

O cockpit adapta a garagem Driver: banco com encosto e apoio de cabeça, moldura frontal dividida, dois painéis e um retrato normal da piloto ao fundo. As telas dos instrumentos são ilustrações próprias. Em **34,3–34,95 s**, moldura e painéis deslizam uma única vez para os lados. Dery continua na mesma cadeira, olha a abertura e ri. A gag remove a cabine, sem mudar a roupa ou as proporções do avatar. Depois, ele volta ao espectador com uma expressão de deboche contido.

A pose sentada foi preservada a partir das matrizes avaliadas do rig original, incluindo o resultado dos controles das pernas, antes de remover as constraints da cópia. As matrizes locais são reconstruídas com `Bone.convert_local_to_pose`. As verificações comparam os pés da cópia aos do original transladado, além de conferir estabilidade do quadril, alcance dos braços, malha e costuras faciais. A camiseta preta com M amarelo, pele limpa e geometria original foram mantidas. A referência pessoal de gestos permanece privada.

## Mídias

O vídeo de habilidades fornece a apresentação, Boosters, ejeção, explosão de Self-Destruct e combate. Os cortes da ejeção e da explosão encurtam a espera entre os dois eventos, sem acelerar a voz. A explosão vem da autodestruição, sem sugerir que toda ejeção produza uma bomba.

O vídeo antigo demonstra Fusion Cannons, sem a habilidade mais nova de Micro Missiles. A fala sobre mísseis recebe um cartão esquemático próprio; os canhões não foram rotulados como mísseis. O combate aparece depois, na fala sobre treinamento, tecnologia e arsenal.

Os retratos normais e os memes de susto e “personagem/jogador” foram enviados pelo usuário. O cartão censurado é inteiramente autoral e opaco. O retrato traseiro do simulador é uma imagem fixa, mantendo a referência da piloto consistente durante a abertura. Não foram usados os vídeos de highlight intros ou Giantess Hug, nem o meme de rosto trocado. Os áudios dos vídeos estão mutados: a trilha final preserva somente a gravação do usuário.

## Arquivos

- `output/DVa_Personagens_que_a_internet_estragou_9x16.mp4` e `output/DVa_Personagens_que_a_internet_estragou_16x9.mp4`: finais.
- `output/Dery_DVa.blend` e `output/Dery_DVa_Master_16x9.blend`: quarto, cockpit, rig, faces, atuação e voz.
- `assets/voz/voz_original.mp3`: recebido, preservado byte a byte. Os WAVs são a decodificação e a cópia com silêncio final.
- `assets/gameplay/`: recortes selecionados e feed sincronizado. `assets/memes/`: mídias preparadas, cartões e instrumentos próprios.
- `timeline.json`, `acting_cues.json`, `face_cues.json`: cortes, gestos, expressões e abertura da cabine.
- `source_manifest.json`: fontes, hashes, intervalos e escolhas editoriais.
- `scene_validation*.json`, `export_validation*.json`: verificações de malha, rosto, apoio, braços, deslocamento dos painéis, áudio e MP4.
- [Cockpit reutilizável](../../../../assets/cenarios/cockpit/): banco e moldura fechada com grupos de deslizamento, sem avatar, voz ou mídias do pacote.

## Visual e reprodução

Render nativo 360×640 / 640×360, ampliação inteira 3× por vizinho mais próximo, precisão reduzida de geometria com proteção das costuras do rosto, texturas Closest, corpo endereçado em 128 px, concreto de 64 px, paleta RGB de 5 bits e Bayer fixo 4×4. Sem blur, glitch ou piscadas aleatórias. As interfaces e a composição têm layouts próprios por formato.

Na raiz do repositório, com Blender 4.3, FFmpeg, NumPy e Pillow:

```sh
blender -b -t 2 --python-exit-code 1 --python shorts/008-personagens-que-a-internet-estragou/production/08-dva/build_short.py
blender -b shorts/008-personagens-que-a-internet-estragou/production/08-dva/output/Dery_DVa.blend -t 1 --python-exit-code 1 --python shorts/008-personagens-que-a-internet-estragou/production/08-dva/verify_scene.py
python shorts/008-personagens-que-a-internet-estragou/production/08-dva/export_short.py
python shorts/008-personagens-que-a-internet-estragou/production/08-dva/verify_export.py
```

Para o horizontal, adicionar `-- --wide` aos comandos Blender e `--wide` aos scripts Python; carregar `Dery_DVa_Master_16x9.blend` na verificação. `--resume` retoma quadros completos e `--encode-only` codifica os já existentes. O padrão refaz os planos 3D. Usar um formato por vez, com dois threads. Gameplay, imagens e gráficos entram diretamente na montagem; o feed usa quadros-chave a cada segundo.

`prepare_assets.py` requer o inventário privado e os originais restaurados. As mídias preparadas necessárias aos projetos e ao render ficam versionadas. Baixar a pasta inteira para editar: áudio e filmes usam caminhos relativos. ZIP, backups, quadros intermediários e referência pessoal permanecem fora do Git.
