# Personagens que a internet estragou — Princesa Peach

Décimo primeiro bloco, produzido com o pacote “11 - Peach.zip” enviado pelo usuário. Versões **9:16 em 1080×1920 e 16:9 em 1920×1080**, 24 fps, **37,25 segundos**. A voz decodificada tem 36,563 segundos e foi preservada inteira, sem mudar velocidade, tom ou falas. O restante é silêncio final.

## Montagem e atuação

Os 23 planos alternam identificação, cartões de seleção de tênis e kart, luta em Showtime, Bowser, memes, galeria opaca, vitrine de coroa, diagrama Toadette → Peachette e Bowsette. O diagrama identifica a divulgação de 2018, sem atribuir essa data ao lançamento de New Super Mario Bros. U Deluxe.

Na vitrine, Dery apresenta a coroa sobre um pedestal e acompanha a troca da moldura. A transformação do jogo fica separada da hipótese dos fãs. No final, a imagem alterna Bowser/Bowsette em momentos definidos, enquanto a incredulidade do Dery vira risada em “é o Bowser pô”. Não há transformação do corpo ou roupa do apresentador, contato das mãos com a coroa ou peça sobre o boné.

Os braços usam preparação, sustentação e retorno, com tempos diferentes e pausas entre intenções. As 31 faces PNG mudam por corte, sem morphs. A camiseta preta com M amarelo, pele limpa, mangas e geometria foram mantidas. A referência pessoal de gestos permanece privada.

O ator em pé reaproveita a pose validada da Ankha. A validação compara os pés aos do rig aprovado, além da estabilidade, quadril, alcance dos braços e costuras faciais. O rig de referência é vinculado e avaliado antes da comparação; as matrizes de um objeto recém-carregado e ainda não avaliado não representam sua pose mundial. O ator do quarto mantém sua pose sentada original.

## Mídias e contexto

“Princess Peach: Showtime! — Peach in the Spotlight” fornece Kung Fu Peach enfrentando inimigos do palco em 80,5–84 s. Bowser recebe um retrato separado; ele não é identificado como inimigo desse trecho de Showtime. Como o pacote não contém tênis ou kart, essas falas recebem cartões gráficos próprios de seleção de jogo.

O pacote também não contém a transformação oficial da Super Coroa. O esquema autoral nomeia corretamente Toadette e Peachette, com estados de destaque próprios. Bowsette é identificada como criação de fãs, distinta das duas personagens oficiais.

O vídeo “Super Smash Bros. Ultimate - Bowsette Reveal Trailer” é feito por fã. O recorte 54,3–58,2 s mostra a personagem vestida e é identificado com “CRIAÇÃO DE FÃS” durante todo o insert. O recorte vertical acompanha o deslocamento horizontal da personagem para manter o rosto no quadro. Nenhum anúncio oficial de Bowsette é sugerido. Os intervalos usados na montagem estão em `timeline.json`.

Os retratos e memes foram enviados pelo usuário. O retrato da Bowsette recorta rosto, coroa e chifres; as referências a versões adultas usam cartões autorais inteiramente opacos. O vídeo musical, a animação de Rosalina e o retrato de Peach em estilo de IA não foram usados. Todos os áudios de vídeo estão mutados. A trilha final contém somente a gravação do usuário, sem voz adicional ou legendas da narração.

## Arquivos

- `output/Peach_Personagens_que_a_internet_estragou_9x16.mp4` e `output/Peach_Personagens_que_a_internet_estragou_16x9.mp4`: finais.
- `output/Dery_Peach.blend` e `output/Dery_Peach_Master_16x9.blend`: quarto, vitrine, rig, faces, atuação e voz.
- `assets/voz/voz_original.mp3`: recebido, preservado byte a byte. Os WAVs são a decodificação e a cópia com silêncio final.
- `assets/gameplay/`: recortes e feed sincronizado. `assets/memes/`: imagens preparadas e gráficos próprios.
- `timeline.json`, `acting_cues.json`, `face_cues.json`: cortes, gestos, expressões e trocas da moldura.
- `source_manifest.json`: fontes, hashes, intervalos e escolhas editoriais.
- `scene_validation*.json`, `export_validation*.json`: verificações da cena, áudio e MP4.
- [Vitrine de coroas reutilizável](../../../../assets/cenarios/vitrine_coroas/): sem avatar ou mídias do pacote; display neutro.

## Visual e reprodução

Render nativo 360×640 / 640×360, ampliação inteira 3× por vizinho mais próximo, precisão reduzida de geometria com proteção das costuras, texturas Closest, corpo endereçado em 128 px, pedra de 32 px, paleta RGB de 5 bits e Bayer fixo 4×4. Sem blur, glitch ou piscadas aleatórias. Câmeras e cartões têm layouts próprios por formato.

Na raiz do repositório, com Blender 4.3, FFmpeg, NumPy e Pillow:

```sh
blender -b -t 2 --python-exit-code 1 --python shorts/008-personagens-que-a-internet-estragou/production/11-peach/build_short.py
blender -b shorts/008-personagens-que-a-internet-estragou/production/11-peach/output/Dery_Peach.blend -t 1 --python-exit-code 1 --python shorts/008-personagens-que-a-internet-estragou/production/11-peach/verify_scene.py
python shorts/008-personagens-que-a-internet-estragou/production/11-peach/export_short.py
python shorts/008-personagens-que-a-internet-estragou/production/11-peach/verify_export.py
```

Para o horizontal, adicionar `-- --wide` aos comandos Blender e `--wide` aos scripts Python; carregar `Dery_Peach_Master_16x9.blend` na verificação. `--resume` retoma quadros completos e `--encode-only` codifica os existentes. O padrão refaz os planos 3D. Usar um formato por vez com dois threads; gameplay e imagens entram diretamente na montagem.

`prepare_assets.py` requer o inventário privado e os originais restaurados. As mídias preparadas necessárias ao projeto ficam versionadas. Baixar a pasta inteira para editar: áudio e filmes usam caminhos relativos. ZIP, backups, quadros intermediários e referência pessoal ficam fora do Git.
