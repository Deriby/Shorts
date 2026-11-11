# Pescoço ajustado — proposta v9

Correção do pescoço após o usuário apontar o aspecto estranho nas prévias das expressões. Parte do Blender com os dez rostos, preservando o contorno facial, o encaixe das expressões, a franja, o boné e as roupas.

- [Antes/depois de frente, três quartos e perfil](Comparativo_Pescoco.png).
- [Frente ajustada](Depois_Frente.png), [três quartos](Depois_Tres_Quartos.png), [perfil](Depois_Perfil.png) e [risada](Depois_Risada.png).
- [Blender com pescoço ajustado e dez expressões](Dery_Pescoco_Ajustado_v9.blend).
- [Parâmetros e verificações](ajuste.json).
- [Biblioteca de PNGs preservada](../expressoes_v1/).

## Correção

O pescoço fica um pouco mais estreito e menos profundo, com transição gradual para a mandíbula e a gola. A altura e a posição da cabeça não mudam. Uma nova iluminação Gouraud gravada por canto suaviza as faixas de luz e acrescenta sombra discreta sob o queixo, mantendo o visual PS1 sem brilho PBR.

O encaixe anterior esticava uma faixa de poucos texels da pele por todo o pescoço, produzindo grandes bandas de cor. O UV separado `DeryNeckUVV9` distribui uma região maior de pele limpa do mesmo PNG neutro. A média de quatro amostras dessa pele fornece o tom base; o detalhe da textura permanece em baixo contraste. Nenhum PNG foi redesenhado ou alterado.

A shape key `DERY | pescoço e ligação da mandíbula` controla o conjunto: **1** mostra a proposta; **0** restaura o contorno, UV e iluminação anteriores. Os UVs originais, a malha-base, as shape keys anteriores, os pesos, os índices de material, os pixels, a iluminação original e os 71 ossos permanecem intactos. O arquivo anterior também foi preservado.

Os onze IDs de expressão (neutro + dez novos rostos) foram conferidos no seletor. Há uma prévia da risada e uma checagem numérica de pose da cabeça a 25°, sem coordenadas inválidas; isso não constitui validação de uma animação completa. O ajuste aguarda avaliação estética do usuário, sem iniciar um short.

```bash
blender -b --disable-autoexec -t 4 --python assets/personagens/dery/rig_ps1_v2/pescoco_v9/ajustar.py
python assets/personagens/dery/rig_ps1_v2/pescoco_v9/comparar.py
```
