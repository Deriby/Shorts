# Camiseta com M do Massacote — v6

Aplicação da [logo original aprovada](../../../../../marca/massacote-games/logo.png) no centro do peito, sobre o material de camiseta da v5. A amostragem equivalente a 64×64 e a interpolação Closest mantêm o aspecto pixelizado da estampa. O M recebe a mesma iluminação Gouraud da roupa e acompanha a deformação do rig pelo UV da malha.

- [Prévia de corpo](Previa_Corpo.png).
- [Detalhe da camiseta](Previa_Camiseta.png).
- [Blender editável com imagens incorporadas](Dery_Camiseta_M_v6.blend).
- [Registro de aplicação](aplicacao.json).

A alteração adiciona apenas a estampa frontal, um UV próprio e sua máscara. Preserva os pixels das texturas existentes, os UVs anteriores, a geometria, os índices de material, o rosto, a franja e os 71 ossos. Os arquivos v3 e v5 permanecem intactos. Não cria expressões nem modifica episódios anteriores.

```bash
blender -b --disable-autoexec -t 4 --python assets/personagens/dery/rig_ps1_v2/texturas/camiseta_m_v6/aplicar.py
```
