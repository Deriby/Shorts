# Contorno da mandíbula pela marcação — proposta v11

O usuário enviou vistas em três quartos e perfil com linhas vermelhas indicando o contorno desejado. Essa referência pede a base da mandíbula mais reta e uma quina definida na ligação com o pescoço. Ela substitui a interpretação de arredondar a ponta usada na v10.

- [Prévia nas duas vistas](Previa_Duas_Vistas.png).
- [Antes/depois nos mesmos ângulos](Comparativo_Contorno.png).
- [Rosto completo](Depois_Rosto.png) e [risada](Depois_Risada.png).
- [Modelo Blender editável com dez expressões](Dery_Contorno_Marcado_v11.blend).
- [Parâmetros e verificações](ajuste.json).

## Ajuste

A parte inferior da mandíbula acompanha um plano levemente inclinado entre a frente do queixo e a garganta. A junção com o pescoço foi trazida para a posição da quina indicada. Os pontos de guia foram interpretados visualmente na mesma câmera ortográfica das prévias; não são uma extração calibrada dos pixels do desenho do usuário.

O UV separado `DeryJawUVV11` corrige a altura de amostragem na parte inferior do rosto, evitando esticar a pintura do cavanhaque ao mudar a malha. Os dois materiais frontais continuam usando as mesmas imagens neutras e o mesmo atlas das dez expressões; as amostras vizinhas acompanham a nova origem de coordenadas. Nenhum PNG foi redesenhado.

A shape key `DERY | mandíbula conforme marcação vermelha` controla geometria e encaixe de UV juntos: **1** mostra a proposta e **0** restaura a v10. A malha-base, as shape keys anteriores, os UVs anteriores, os pixels, os pesos, os índices de material, as roupas, o boné, a franja e os 71 ossos permanecem preservados. O arquivo v10 segue intacto. O modelo possui oito camadas UV; reutilizar uma camada de ajuste existente em revisões futuras.

Foram conferidos os onze IDs do seletor facial, a preservação do arquivo-fonte e dos dados anteriores, e a ausência de novos triângulos degenerados no ajuste. O erro de assentamento no plano de guia é inferior a 0,5 mm nos vértices selecionados; essa medida se refere ao plano interpretado, não à distância exata da linha vermelha da imagem. Há renders em close, perfil e risada para revisão estética. Não foi iniciada animação de short.

```bash
blender -b --disable-autoexec -t 4 --python assets/personagens/dery/rig_ps1_v2/contorno_marcado_v11/ajustar.py
python assets/personagens/dery/rig_ps1_v2/contorno_marcado_v11/comparar.py
```
