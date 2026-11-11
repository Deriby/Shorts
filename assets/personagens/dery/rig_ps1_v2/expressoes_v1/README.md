# Teste de 10 expressões PS1 — novo Dery

O usuário autorizou dez expressões para avaliar no modelo atual, após o ajuste de contorno v7 e encaixe v8. Esta biblioteca é própria do novo rig/UV; não utiliza o controlador antigo de 31 rostos.

- [Prancha das dez expressões aplicadas](10_Expressoes_no_Modelo.png).
- [Risada em três quartos](previas/Risada_Tres_Quartos.png).
- [Blender com seletor e imagens incorporadas](Dery_10_Expressoes_PS1.blend).
- [PNGs individuais](png/) e [atlas de uso no material](Atlas_Expressoes_4x3.png).
- [Manifesto](expressoes.json), [origem da arte](geracao.json) e [verificações](validacao.json).

| ID | Expressão |
|---:|---|
| 0 | Neutro original |
| 1 | Sorriso |
| 2 | Risada |
| 3 | Surpresa |
| 4 | Raiva |
| 5 | Confusão |
| 6 | Deboche |
| 7 | Tristeza |
| 8 | Nojo |
| 9 | Piscada: dois olhos fechados |
| 10 | Falando: boca aberta |

## Uso no Blender

Selecionar `Dery_Massacote_Rig_PS1_v2` e alterar a propriedade personalizada inteira `PS1_face_id` de 0 a 10. O arquivo abre no neutro e com visualização de materiais. Os drivers dos dois materiais frontais usam o mesmo índice. O ID seleciona uma célula do atlas com troca seca; não há interpolação entre expressões. Ao animar essa propriedade, usar keyframes com interpolação **Constant**.

O módulo `aplicar.py` também expõe `install(avatar)` para instalar na base v8 e `set_expression(avatar, id)` para selecionar uma expressão em scripts. Executar a instalação uma única vez sobre a base v8; o Blender entregue já está instalado.

O atlas tem 4×3 células de 128×128, amostragem Closest e precisão RGB555. A célula 0 preserva o PNG neutro exato anterior; as dez seguintes contêm a nova arte. A célula restante é preenchida com o neutro. As coordenadas são limitadas dentro de cada célula, incluindo todas as amostras vizinhas do realce da v5. Uma máscara espacial mantém a pele original junto à borda facial; isso não cria transição temporal entre rostos.

O modelo, a shape key de contorno, os UVs, os pesos, os índices de material, os 71 ossos, a franja, o boné, as roupas e os pixels das imagens anteriores foram preservados. O arquivo v8 permanece intacto. As prévias foram renderizadas no próprio Blender com o seletor funcionando em todos os onze IDs, e uma vista de risada em três quartos foi conferida. A biblioteca é um teste em avaliação, sem aprovação estética presumida nem autorização para iniciar um short.

## Reproduzir

```bash
python assets/personagens/dery/rig_ps1_v2/expressoes_v1/preparar.py
blender -b --disable-autoexec -t 4 --python assets/personagens/dery/rig_ps1_v2/expressoes_v1/aplicar.py
python assets/personagens/dery/rig_ps1_v2/expressoes_v1/montar_previa.py
```

A arte foi produzida por `image_gen` a partir do mapa neutro e da prévia atual. O script de preparação apenas separa as células, converte tamanho/precisão de cor e organiza os arquivos, sem desenhar rostos por código.
