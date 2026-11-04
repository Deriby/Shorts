# Misturaram GTA com POSTAL 2

Short do Massacote Games sobre a mistura de GTA San Andreas com POSTAL 2 apresentada no vídeo enviado pelo usuário.

Formato final exclusivamente **9:16, 1080 × 1920**. Produção sincronizada aos três WAVs enviados, com **42,17 segundos e 24 fps**.

- [Assistir ao short vertical](production/output/Misturaram_GTA_com_POSTAL_2_9x16.mp4).
- [Projeto Blender com rig, câmeras e expressões](production/output/Dery_GTA_POSTAL2.blend).
- [Ordem, duração e hashes das vozes](production/audio.json).
- [Montagem por tomada e trechos da referência](production/timeline.json).

- [Roteiro de narração — texto para gravar](roteiro_narracao.md).
- [Roteiro de animação — cenas, expressões, cortes e som](roteiro_animacao.md).
- [Vídeo de referência original enviado](production/assets/gameplay/san_andreas_postal2_enviado.mp4).
- [Observações verificadas e tempos no vídeo](production/assets/gameplay/fontes.json).

A produção usa o Dery no quarto gamer PS1, com a biblioteca já existente de 31 rostos, o encaixe revisado e trocas secas de expressão. O arco vai da curiosidade à lembrança da missão do trem e termina na mudança de confiança durante a brincadeira de “pior/melhor mistura”.

O vídeo de referência mostra primeira e terceira pessoa, a interface e armas associadas a POSTAL, carros, bicicleta, pichação e a missão com Big Smoke. A própria apresentação identifica uma demo v0.2. O roteiro descreve essas demonstrações e evita atribuir autor, engine, campanha completa ou condições atuais de download que não foram verificadas.

A voz gravada determina o sincronismo. As legendas continuam a cargo da edição do usuário e não estão embutidas.

## Voz e adaptação do roteiro

Os arquivos originais estão preservados em `production/assets/voz/`, com os mesmos hashes dos anexos. A ordem correta de narração é **2 → 1 → 3**: abertura e explicação; exemplos e trem; demo e fechamento. A concatenação sem alteração de velocidade ou tom soma **41,2503 segundos**. O restante da duração é reservado à reação final.

A gravação substitui a confissão por “A gente já sofria seguindo aquele troço no jogo normal” e fecha com a brincadeira de “pior/melhor mistura possível”. A montagem segue essa gravação. As falas de Grove Street e do vizinho presentes no roteiro inicial não foram acrescentadas, e a gag de batida de porta foi substituída por reações e sons digitais breves.

## Montagem e visual

O Dery, a cadeira, o quarto, a iluminação e os 31 rostos vêm da base já revisada do episódio 004. O rosto usa os UVs e o espaçamento de olhos ajustados, com correção de olheiras e troca seca de PNG. O gesto acompanha a frase: explicação, deboche, recuo na pá, lembrança do trem e mudança de confiança no fechamento.

Os exemplos do mod entram como cortes de gameplay com recorte vertical próprio, preservando o foco da ação. Nas falas e reações, a gameplay continua na tela do PC. A apresentação da versão e a arte de encerramento são quadros estáticos intencionais; os trechos de jogo permanecem em movimento.

A cena é composta diretamente em retrato, renderizada em 360 × 640 e ampliada para 1080 × 1920 por vizinho mais próximo, com dithering e bordas instáveis. O modificador PS1 usa o aspecto 9:16. O alcance dos braços é limitado pela rig; o Dery reage à pá vista no jogo.

Para economizar renderização, apenas as tomadas com o quarto ou o personagem passam pelo Blender. Os cortes diretos de gameplay são preparados do arquivo enviado e depois reunidos na mesma sequência vertical.

## Reproduzir

Requisitos: Blender 4.3, FFmpeg, Python e os arquivos Git LFS do repositório.

```bash
python shorts/005-gta-postal2/production/prepare_assets.py
blender -b -t 4 --python-exit-code 1 --python shorts/005-gta-postal2/production/build_short.py
python shorts/005-gta-postal2/production/export_short.py
```

O arquivo `monitor_montado.mp4` é a sequência usada no PC do projeto Blender. Os frames, segmentos e caches de conversão ficam em `production/renders/`, fora do Git. Para montar novamente a exportação a partir de frames já preparados, use `export_short.py --encode-only`.
