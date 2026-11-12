# Dery — 100 novas expressões PS1

**100 novos PNGs, já instalados no Dery original.** São **131 rostos no total**, contando os 31 anteriores preservados. A malha, as proporções, o rig, os UVs e a camiseta preta com M continuam os mesmos do personagem usado nos shorts. O experimento `rig_ps1_v2` não foi usado.

- [Baixar o Blender com as 131 expressões incorporadas](https://github.com/Deriby/Shorts/raw/refs/heads/main/assets/personagens/dery/expressions_ps1/v3/Dery_131_Expressoes_PS1.blend).
- [Prévia de expressões selecionadas no modelo](Previa_Expressoes_No_Dery.png).
- Todas as novas no modelo: [fala A/E/I/O](No_Modelo_01.png), [outras bocas](No_Modelo_02.png), [reações](No_Modelo_03.png), [caricatas](No_Modelo_04.png).
- [Encaixe em frente, três quartos e perfil](Conferencia_Angulos.png).
- [PNGs individuais](png/), [atlas](atlas_131_16x9.png), [índice completo](expressions.json) e [famílias de fala](fala_familias.json).

| IDs | Quantidade | Uso |
| --- | ---: | --- |
| 0–30 | 31 | Rostos originais; mesmos índices e PNGs idênticos aos anteriores |
| 31–80 | 50 novas | Bocas para fala: cinco emoções × dez posições |
| 81–105 | 25 novas | Olhares, constrangimento, dúvida, cansaço e reações |
| 106–130 | 25 novas | Olhão, dentão, vesgo, choro, espirais e caretas exageradas |

As famílias de fala são **neutra, alegre, irritada, sarcástica e empolgada**. Cada uma tem boca fechada M/B/P, A, E, I, O, U, lábio F/V, língua L, entreaberta D/T/N e bico CH/X. São poses estilizadas para seleção pela fala gravada; esta biblioteca não faz reconhecimento de áudio nem sincronismo automático. As associações fonéticas são guias de animação.

## Usar

Abra `Dery_131_Expressoes_PS1.blend`, selecione **`DERY | animated character`** e altere a propriedade **`PS1_face_id`**, de **0 a 130**. A cena é uma prévia estática; o arquivo não contém uma nova narração ou um short.

Para animar, marque os índices necessários e use interpolação **Constant**. O rosto inteiro troca de textura no quadro indicado, sem mistura ou deformação facial. Alterne bocas pela intenção da fala e feche nos intervalos; não percorra os cinquenta índices em loop. Mantenha uma família durante cada frase e reserve as caricatas para as piadas e reações.

Exemplo na família neutra: 31 fechado → 32 A → 33 E → 56 U → 31 fechado. Os índices das outras famílias estão em `fala_familias.json`.

Para atualizar uma cena existente com o **Dery original e o encaixe v2 revisado**:

```python
import sys
sys.path.insert(0, '/caminho/Shorts/assets/personagens/dery/expressions_ps1/v3')
from setup_faces131 import install, set_face
import bpy
avatar = bpy.data.objects['DERY | animated character']
install(avatar)
set_face(avatar, 32, frame=1)
set_face(avatar, 31, frame=5)  # insere chaves Constant
```

O instalador copia o material revisado, mantém a pele/nariz e a iluminação limpa, retargeta o driver para o personagem selecionado e troca o atlas. Não refaz malha ou UVs e recusa uma base desconhecida. A limpeza antiga sob os olhos continua nos IDs originais; não apaga a parte inferior dos olhos grandes nem as lágrimas dos desenhos novos. Ao usar um novo enquadramento, configure `ps1_precision.py` com a câmera e a resolução da produção.

## Arte e verificação

Quatro folhas novas foram desenhadas com `image_gen`, usando as expressões originais como referência. `prepare_library.py` apenas recorta as células uniformes, reduz para 128×128 com **Nearest**, registra os nomes e monta o atlas 16×9 de 2048×1152. Não suaviza os rostos nem redesenha os 31 PNGs antigos. As fontes ficam em `sources/`.

As quatro páginas `No_Modelo_*` são renders reais do personagem com cada um dos cem IDs novos, em câmera fixa. A ampliação usa Nearest; a prévia não usa borrão ou oscilação da tela. A conferência de ângulos mostra uma seleção de quatro expressões. Os resultados ainda aguardam avaliação estética do usuário.

`validacao.json` registra a reabertura no Blender 4.3.2, imagens incorporadas, limites do driver, chaves Constant, integridade do modelo original, cem PNGs novos diferentes, cem renders diferentes e correspondência de cada célula do atlas. A geometria, os UVs e a pose do rig foram comparados antes e depois da instalação. O arquivo original não foi sobrescrito.

Reconstrução e prévias (os renders intermediários ficam fora do Git):

```bash
python assets/personagens/dery/expressions_ps1/v3/prepare_library.py
blender -b -t 4 --python assets/personagens/dery/expressions_ps1/v3/build_model.py
blender -b -t 4 --python assets/personagens/dery/expressions_ps1/v3/build_model.py -- all
blender -b -t 4 --python assets/personagens/dery/expressions_ps1/v3/build_model.py -- angles
python assets/personagens/dery/expressions_ps1/v3/montar_previas.py
blender -b -t 4 --python assets/personagens/dery/expressions_ps1/v3/verify_blender.py
python assets/personagens/dery/expressions_ps1/v3/verificar_biblioteca.py
```
