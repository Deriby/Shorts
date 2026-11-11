# Rosto PSX e contorno frontal marcado — v12

O usuário aprovou o contorno marcado de perfil e pediu o rosto e as expressões mais pixelizados. Durante a prévia apontou a proporção frontal e enviou outra marcação vermelha: rosto afunilando até o queixo e pescoço abrindo para os ombros. Esta versão segue essa referência frontal e mantém as coordenadas do perfil anterior, além do acabamento facial.

- [Rosto e pescoço antes/depois no frontal](Comparativo_Contorno_Frontal.png).
- [Quatro rostos com acabamento PSX](Previa_Rostos_PSX.png).
- [Comparação da amostragem 128/64](Comparativo_Pixels.png), com o pescoço corrigido nos dois lados.
- [Três quartos](Previa_Tres_Quartos.png) e [perfil](Previa_Perfil.png).
- [Blender com dez expressões](Dery_Rosto_PSX_64_v12.blend).
- [Parâmetros e verificações](validacao.json).

## Acabamento e controles

Os materiais frontais usam uma grade de amostragem equivalente a **64×64** antes de ler o PNG neutro ou a célula do atlas de expressões. As bordas dos texels permanecem nítidas com Closest. O realce local anterior foi desligado nesses dois materiais. Não há pós-processamento da tela ou regeneração da arte: os PNGs originais continuam em 128×128 e seus pixels permanecem intactos.

A propriedade personalizada `PSX_face_resolution` controla a grade: 64 é o padrão, 32 deixa os pixels maiores e 128 permite mais detalhe. `PS1_face_id` mantém o neutro no ID 0 e as dez expressões nos IDs 1–10, com troca seca. Todas as amostras frontais, inclusive as vizinhas e as entradas do atlas, usam a mesma grade; o limite de cada célula permanece protegido.

O contorno frontal está na shape key `DERY | rosto e pescoço conforme guia frontal`, entregue em **1**. Ajusta a largura da mandíbula por altura, mantém o pescoço mais estreito em cima e preserva a abertura na base para os ombros. Em **0** mostra o contorno anterior. Atua somente em X: as coordenadas Y/Z do perfil marcado permanecem iguais. O comparativo frontal usa a mesma expressão, resolução facial e câmera nos dois lados. Os perfis de largura foram interpretados visualmente da marcação, sem extração calibrada dos pixels.

A malha-base, as shape keys anteriores, os oito UVs, os pesos, os índices de material, os pixels, o rig de 71 ossos, as roupas e os arquivos anteriores foram preservados. A alteração geométrica nova está apenas na shape key de contorno frontal. Vértices coincidentes compartilham a mesma correção para preservar as costuras. O seletor foi conferido em todos os onze IDs e foram renderizadas vistas frontal, três quartos e perfil. O contorno frontal e o acabamento pixelizado aguardam avaliação do usuário. Não foi produzido um short ou vídeo novo.

```bash
blender -b --disable-autoexec -t 4 --python assets/personagens/dery/rig_ps1_v2/pixel_psx_v12/aplicar.py
python assets/personagens/dery/rig_ps1_v2/pixel_psx_v12/comparar.py
```
