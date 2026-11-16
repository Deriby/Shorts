# Prévia 01 — personagem 2D conversando

Prévia solicitada pelo usuário: 9,3 s, 279 quadros, MP4 H.264 1280×720/30 fps com áudio AAC. Projeto WFP 1920×1080/30 fps com camadas e keyframes editáveis. Sem Blender.

Há entrada curta, gestos leves de corpo/cabeça, bigode movido pela energia da voz e troca conversando → apontando → conversando, com preparação e retorno. As poses aprovadas do lote 01 ficam intactas. Duas bases limpas foram criadas com image_gen para o bigode se mover sem revelar boca. Elas também não têm boca desenhada. Planos de corpo/cabeça/bigode extraídos em PNG; o corpo tem sobreposição de pescoço para acomodar a inclinação da cabeça.

A voz de teste usa apenas 0–9,3 s de `shorts/008-personagens-que-a-internet-estragou/production/00-intro/assets/voz/narracao_completa.wav`, já existente. O trecho inicia “A internet conseguiu colocar uma personagem de videogame…” e inclui “E do jeito mais errado possível”. Não há voz nova, mudança de tom ou velocidade. O original permanece inteiro.

O MP4 é uma composição local das mesmas transformações numéricas salvas nos keyframes do WFP. A validação estrutural estrita do WFP passou (biblioteca raiz, UUIDs, extra.json, caches, recursos e 11 bindings). Quatro faixas visuais e uma faixa de áudio; 45 curvas e 4.230 pontos de keyframe. Abertura/reprodução/exportação nativa ainda não verificadas no Filmora. Aprovação estética da prévia pendente.

A referência do Drive continua registrada no fluxo 2D e sua análise anterior orientou o teste. Não houve nova reprodução da referência nem medição nova de movimentos neste pedido; esta prévia não estabelece uma reprodução exata daquele vídeo.

## Arquivos e reprodução

- `Previa_Conversando_2D.mp4`: prévia com voz.
- `Filmora/`: WFP, instruções e todas as mídias necessárias.
- `fontes/`: duas bases limpas preparadas com image_gen.
- `keyframes.json`: transformações por quadro, comuns ao WFP e ao render de prévia.
- `filmora_validacao.json` e `validacao.json`: resultados de verificação.
- `rig_camadas.json`: índice das camadas, para reutilização.

Na raiz do repositório, com ImageMagick/FFmpeg e o Python do ambiente:

```
source /workspace/.shorts-venv/bin/activate
python assets/personagens/massacote_tube_2d/previa_01/preparar_camadas.py
python assets/personagens/massacote_tube_2d/previa_01/gerar_animacao.py
python assets/personagens/massacote_tube_2d/previa_01/montar_filmora.py
python assets/personagens/massacote_tube_2d/previa_01/validar_previa.py
```

As bases limpas ficam persistidas; os scripts não fazem novas chamadas de geração nem alteram as poses aprovadas. A aplicação nativa do Filmora deve ser usada para conferir a abertura e a aparência no editor.

## Downloads pelo GitHub

- [Baixar a prévia MP4](https://github.com/Deriby/Shorts/blob/main/assets/personagens/massacote_tube_2d/previa_01/Previa_Conversando_2D.mp4?raw=true).
- [Baixar WFP e mídias em ZIP](https://github.com/Deriby/Shorts/blob/main/assets/personagens/massacote_tube_2d/previa_01/entrega/Massacote_Tube_Previa_2D_Filmora.zip?raw=true).

O usuário definiu downloads sempre pelo GitHub. O ZIP contém o WFP e todas as mídias verificadas, com arquivos relativos à pasta `midias/`.
