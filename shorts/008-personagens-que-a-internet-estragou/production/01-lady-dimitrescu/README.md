# Personagens que a internet estragou — Lady Dimitrescu

Primeiro bloco: entregas **9:16 em 1080×1920** e **16:9 em 1920×1080**, ambas com 24 fps e 39 segundos. Voz de 38,313 s recebida no pacote do usuário, preservada sem cortes, mudança de velocidade ou altura. A timeline segue a gravação real, cuja ordem difere do texto inicial.

## Arquivos

- `output/Lady_Dimitrescu_Personagens_que_a_internet_estragou_9x16.mp4`: master do short.
- `output/Lady_Dimitrescu_Personagens_que_a_internet_estragou_16x9.mp4`: master horizontal, com câmeras e composição de mídia próprias.
- `output/Dery_Lady_Master_16x9.blend`: projeto horizontal.
- `output/Dery_Lady_Dimitrescu.blend`: quarto, entrada do castelo, rig, atuação, expressões e voz na timeline.
- `assets/voz/voz_original.mp3`: gravação original preservada byte a byte. Os WAVs são sua decodificação e cópia com silêncio final.
- `assets/gameplay/`: trechos selecionados dos vídeos enviados e o feed sincronizado do monitor.
- `assets/memes/`: imagens enviadas, reenquadramento vertical da reação, print com banner coberto e currículo fictício da gag.
- `source_manifest.json`: nomes originais, hashes e intervalos dos vídeos usados. O ZIP original e os vídeos integrais permanecem no acervo local; não são duplicados no Git.
- `timeline.json`, `acting_cues.json`, `face_cues.json`: montagem, poses por frase e trocas discretas dos PNGs.
- `scene_validation.json` e `export_validation.json`: verificações de integridade da cena, expressão, áudio e arquivo exportado.

## Atuação e montagem

Os 17 planos alternam gameplay, monitor, memes, Dery e a vinheta do castelo. A atuação usa curvas diferentes para cada braço, com preparação, gesto, sustentação e retorno. Há um gesto de apresentação, duas mãos indicando as garras, uma palma aberta de desconfiança, mão retraída de constrangimento e apresentação final do monitor. Os braços não usam um ciclo periódico. A cabeça alterna entre tela e câmera conforme a intenção da frase, usando a referência pessoal fornecida no episódio 007; o vídeo pessoal continua fora do repositório público.

Na entrada do castelo, Dery indica a altura e depois reage defensivamente à presença sugerida pela sombra. Os pés permanecem apoiados. A cena não exige simulação, contato com a porta ou um modelo completo da Lady. O cenário foi separado como [asset reutilizável](../../../../assets/cenarios/entrada_castelo/).

O fim acompanha a fala “carreira paralela”: currículo fictício no monitor, campo de outras atividades coberto e reação de Dery. Não há a antiga piada do aluguel nem fala adicional. Não foram embutidas legendas da narração; textos de memes e placas pertencem à cena.

Parte dos vídeos enviados usa roupa ou câmera modificadas. São apoio visual e humor, sem afirmar que sejam cenas oficiais inéditas. O banner original do print de site foi completamente coberto no derivado publicado; o original não está incluído no repositório.

## Visual PS1

Render nativo 360×640 no vertical e 640×360 no horizontal, com upscale inteiro 3× por vizinho mais próximo. Precisão de vértices em grade de 128×228 no vertical e 405×228 no horizontal, preservando a proteção do rosto contra fissuras. Texturas do corpo endereçadas em 128 px, amostragem Closest, sombreamento facetado e cenário de poucos polígonos. Na exportação, quantização de 5 bits por canal e dithering Bayer fixo 4×4, sem ruído aleatório, desfoque ou transição de glitch.

O movimento dos personagens e da câmera produz o tremido da geometria; o dithering fica preso à grade de pixels. O corpo original, a camiseta preta com M amarelo e as 31 expressões desenhadas foram preservados. As coordenadas da malha são conferidas contra o modelo de origem.

## Reproduzir

Na raiz do repositório, com Blender 4.3, FFmpeg, NumPy e Pillow:

```sh
blender -b -t 2 --python-exit-code 1 --python shorts/008-personagens-que-a-internet-estragou/production/01-lady-dimitrescu/build_short.py
blender -b shorts/008-personagens-que-a-internet-estragou/production/01-lady-dimitrescu/output/Dery_Lady_Dimitrescu.blend -t 1 --python-exit-code 1 --python shorts/008-personagens-que-a-internet-estragou/production/01-lady-dimitrescu/verify_scene.py
python shorts/008-personagens-que-a-internet-estragou/production/01-lady-dimitrescu/export_short.py
python shorts/008-personagens-que-a-internet-estragou/production/01-lady-dimitrescu/verify_export.py
```

`prepare_assets.py` prepara o pacote original e o monitor; para executá-lo novamente, é necessário restaurar o ZIP local e seu inventário de inspeção. As mídias preparadas necessárias ao render já estão versionadas. O projeto Blender usa caminhos relativos para vídeo e áudio: baixar a pasta de produção completa para editar.

A versão 16:9 foi renderizada com a mesma atuação e áudio. O monitor tem aproximação própria, o castelo ganha extensão lateral e o close final usa uma câmera lateral. A gameplay mantém o quadro completo; a comparação de altura e o meme vertical usam composição horizontal, e a reação usa a imagem original lado a lado. O vídeo longo ainda exige a montagem dos demais blocos.

Para gerar o horizontal:

```sh
blender -b -t 2 --python-exit-code 1 --python shorts/008-personagens-que-a-internet-estragou/production/01-lady-dimitrescu/build_short.py -- --wide
blender -b shorts/008-personagens-que-a-internet-estragou/production/01-lady-dimitrescu/output/Dery_Lady_Master_16x9.blend -t 1 --python-exit-code 1 --python shorts/008-personagens-que-a-internet-estragou/production/01-lady-dimitrescu/verify_scene.py -- --wide
python shorts/008-personagens-que-a-internet-estragou/production/01-lady-dimitrescu/export_short.py --wide
python shorts/008-personagens-que-a-internet-estragou/production/01-lady-dimitrescu/verify_export.py --wide
```

Os quadros e relatórios do horizontal ficam separados em `renders/final_16x9`, `scene_validation_16x9.json` e `export_validation_16x9.json`.

Apenas os planos 3D passam pelo Blender, em dois processos de dois threads; inserts de imagens e gameplay são montados separadamente. Quadros intermediários, backups e ZIPs duplicados ficam fora do Git.
