# Base do queixo — proposta v10

O usuário apontou a ponta estranha do queixo em um close da v9. A correção concentra-se na borda inferior da mandíbula: cancela o alongamento vertical anterior, recua discretamente a ponta e arredonda a passagem para o pescoço.

- [Antes/depois em close e perfil](Comparativo_Queixo.png).
- [Rosto ajustado](Depois_Rosto.png) e [risada](Depois_Risada.png).
- [Blender com ajuste e dez expressões](Dery_Queixo_Ajustado_v10.blend).
- [Parâmetros e verificações](ajuste.json).

A borda é relaxada usando um grafo de vizinhança que agrupa vértices coincidentes, para não abrir fendas nas costuras de UV. Um limite arredondado local suaviza a quina inferior sem projetar as camadas da superfície sobre um mesmo plano. A região da boca e o restante da cabeça ficam fora do núcleo da correção.

O ajuste está na shape key `DERY | base do queixo arredondada`: **1** mostra a proposta e **0** restaura a v9. O modelo entregue mantém as shape keys anteriores nos seus valores originais. Não houve troca de materiais, PNGs, UVs, pesos ou ossos, e a v9 permanece intacta. O controle `PS1_face_id` mantém o neutro e as dez expressões com troca seca.

O script verifica a preservação dos dados anteriores e do arquivo-fonte, o seletor nos onze IDs e coordenadas finitas da malha avaliada. O close, o perfil e a risada foram renderizados para revisão. A proposta aguarda avaliação estética; não foi iniciada animação de short.

```bash
blender -b --disable-autoexec -t 4 --python assets/personagens/dery/rig_ps1_v2/queixo_v10/ajustar.py
python assets/personagens/dery/rig_ps1_v2/queixo_v10/comparar.py
```
