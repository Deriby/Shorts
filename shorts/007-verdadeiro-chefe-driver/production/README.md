# Produção — O verdadeiro chefe de Driver

Master vertical 1080×1920, 24 fps, 43,875 segundos. Voz original enviada pelo usuário, sem mudança de velocidade, altura ou cortes. Sem legendas de narração embutidas.

## Conteúdo

- `output/O_verdadeiro_chefe_de_Driver_9x16.mp4`: entrega final H.264/AAC.
- `output/Dery_Driver.blend`: quarto, garagem, carro, rig, atuação e voz de referência na timeline.
- `assets/voz/voz_original.mp3`: arquivo original preservado. `narracao_completa.wav` é sua decodificação; `narracao_mix.wav` acrescenta três efeitos discretos.
- `assets/gameplay/driver_tutorial_enviado.mp4`: gameplay enviada. `monitor_montado.mp4` contém a seleção sincronizada usada na tela do quarto.
- `timeline.json`: cortes ajustados à gravação real. `face_cues.json`: trocas de expressões do apresentador.
- `gesture_reference.json`: observações de atuação do vídeo pessoal. O vídeo pessoal não é incluído no repositório público nem no short.
- `scene_validation.json` e `export_validation.json`: verificações de geometria, rosto, banco, volante, mídia e áudio.

## Direção

A [garagem e o carro reutilizáveis](../../../assets/cenarios/garagem_driver/) ficam também em assets.

Vinte planos alternam gameplay, detalhe do monitor, Dery no quarto e duas aparições da garagem. Gestos desenhados à mão usam a referência pessoal: mãos na altura do peito, ênfases curtas, palmas abertas, inclinação de cabeça e aproximação do tronco. A referência orienta a atuação; não houve captura automática de movimento.

A garagem é uma caricatura low poly, com carro de janelas abertas, pilares e faixas amarelas. A pilastra tem uma barra de vida que permanece cheia após a pequena batida. Essa interface pertence à piada 3D e não ao Driver original. A gravação mostra uma tentativa concluída; a montagem de reinício ilustra a fala, sem inventar uma tela de derrota na captura.

Dery mantém as coordenadas da malha original, 31 expressões desenhadas com troca seca, camiseta preta com M amarelo e limpeza de pele/mangas. A correção compartilhada `ps1_precision.py` evita fissuras em vértices coincidentes. Texturas Closest, polígonos aparentes e ampliação inteira preservam o acabamento retrô, sem desfoque nem transições de glitch.

## Reproduzir

Executar a partir da raiz do repositório, com Blender 4.3, FFmpeg e Python:

```sh
python shorts/007-verdadeiro-chefe-driver/production/prepare_assets.py
blender -b -t 2 --python-exit-code 1 --python shorts/007-verdadeiro-chefe-driver/production/build_short.py
blender -b shorts/007-verdadeiro-chefe-driver/production/output/Dery_Driver.blend -t 2 --python-exit-code 1 --python shorts/007-verdadeiro-chefe-driver/production/verify_scene.py
python shorts/007-verdadeiro-chefe-driver/production/export_short.py
python shorts/007-verdadeiro-chefe-driver/production/verify_export.py
```

O render 3D usa 360×640, Cycles CPU com uma amostra, dois processos de dois threads e upscale 3× por vizinho mais próximo. A gameplay direta passa por FFmpeg, sem renderização no Blender; o giro recebe aceleração de 1,6× para caber no trecho citado, sem alterar a voz. O LUT final reduz a paleta sem o custo de uma expressão por pixel. PNGs intermediários e backups não são versionados.

Os vídeos usados como textura continuam externos ao `.blend`; para editar, baixar a pasta de produção mantendo sua estrutura.
