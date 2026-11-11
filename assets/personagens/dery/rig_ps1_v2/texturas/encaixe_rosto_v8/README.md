# Encaixe da textura facial — proposta v8

O usuário pediu ajustar a textura do rosto depois da alteração do contorno da cabeça. A v8 usa o modelo v7 e o mesmo desenho neutro de 128×128, com ajustes locais no UV para acompanhar a mandíbula mais estreita.

- [Antes/depois de frente e três quartos](Comparativo_Rosto.png).
- [Frente ajustada](Depois_Frente.png) e [três quartos ajustado](Depois_Tres_Quartos.png).
- [Modelo Blender editável](Dery_Encaixe_Rosto_v8.blend).
- [Parâmetros e verificações](encaixe.json).

## Ajuste

As sobrancelhas sobem levemente; o espaçamento horizontal dos olhos fica essencialmente igual. A boca fica um pouco mais estreita e baixa. O cavanhaque ocupa uma região mais estreita e termina mais acima da borda inferior do queixo. São mudanças pequenas de posicionamento do mesmo desenho, com os pixels nítidos e a amostragem Closest já existentes.

O encaixe novo usa o UV `DeryFaceFitV8` nos dois materiais frontais. Para restaurar o encaixe anterior, trocar o campo UV Map desses dois nós para `DeryPS1UV`. Os cinco samplers de cada família facial, incluindo os vizinhos do realce da v5, acompanham a mesma origem de coordenadas. As máscaras do atlas original mantêm suas coordenadas anteriores.

Não houve pintura nova ou edição dos pixels dos PNGs. A geometria, a shape key de mandíbula da v7, os UVs anteriores, os pesos, os materiais atribuídos, os 71 ossos, a franja, o boné e a roupa com M permanecem preservados. O arquivo v7 continua intacto. Não foram criadas expressões nem iniciada produção de shorts; a semelhança desta proposta aguarda avaliação do usuário.

```bash
blender -b --disable-autoexec -t 4 --python assets/personagens/dery/rig_ps1_v2/texturas/encaixe_rosto_v8/ajustar.py
python assets/personagens/dery/rig_ps1_v2/texturas/encaixe_rosto_v8/comparar.py
```
