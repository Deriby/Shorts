# Contorno do rosto — proposta v7

O usuário identificou que o formato do rosto, além da textura, não corresponde à sua aparência. Esta proposta parte da v6, preserva a camiseta com M e testa somente o contorno inferior da cabeça: mandíbula mais estreita abaixo das bochechas e base do queixo menos reta.

- [Antes/depois de frente e três quartos](Comparativo_Rosto.png), com câmera e iluminação iguais.
- [Frente ajustada](Depois_Frente.png) e [três quartos ajustado](Depois_Tres_Quartos.png).
- [Blender editável](Dery_Contorno_Rosto_v7.blend).
- [Parâmetros e verificações](ajuste.json).

O ajuste usa interpretação visual das fotos já fornecidas na conversa. Não é um escaneamento calibrado nem uma correspondência automática de pontos faciais; a semelhança ainda precisa ser avaliada pelo usuário.

## Preservação e controle

A alteração está na shape key `DERY | contorno de mandíbula e queixo`: valor **1** mostra a proposta; **0** restaura o contorno anterior. O deslocamento máximo é de aproximadamente 9,6 mm. A malha base, os UVs, os pixels de todas as imagens, os materiais, os pesos e os 71 ossos permanecem iguais à v6. Nariz, olhos, sobrancelhas e desenho da boca não foram redesenhados. Boné e franja permanecem intactos; não há expressões novas.

Os arquivos anteriores continuam preservados. Esta é uma proposta em avaliação, sem aprovação integral do modelo ou autorização para produzir shorts.

```bash
blender -b --disable-autoexec -t 4 --python assets/personagens/dery/rig_ps1_v2/formato_rosto_v7/ajustar.py
python assets/personagens/dery/rig_ps1_v2/formato_rosto_v7/comparar.py
```
