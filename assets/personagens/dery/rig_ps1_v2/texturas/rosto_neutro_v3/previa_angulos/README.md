# Prévia em oito direções

Renderizações do arquivo `../Dery_Referencia_Sem_Mochila_v3.blend`, solicitadas pelo usuário para conferir todos os lados da proposta atual.

- [Corpo inteiro — oito ângulos](Corpo_8_Angulos.png).
- [Cabeça — oito ângulos](Rosto_8_Angulos.png).
- Imagens individuais em `corpo/` e `rosto/`, com resolução nativa preservada nas pranchas.
- [vistas.json](vistas.json): arquivo de origem, SHA-256, câmeras e nomes das vistas.

Cada grupo contém frente, três quartos pela direita, lateral direita, três quartos das costas pela direita, costas, três quartos das costas pela esquerda, lateral esquerda e três quartos pela esquerda. Os lados indicam a anatomia do Dery, não o lado de quem observa a imagem.

A câmera gira ao redor do modelo. Pose, malha, rig, materiais, texturas e iluminação permanecem iguais aos do arquivo recebido. O Blender de origem não foi salvo nem alterado; seu hash foi conferido antes e depois. Estas vistas não representam aprovação do personagem nem iniciam expressões ou animações.

Para reproduzir:

```bash
blender -b --disable-autoexec -t 4 --python assets/personagens/dery/rig_ps1_v2/texturas/rosto_neutro_v3/previa_angulos/renderizar.py
python assets/personagens/dery/rig_ps1_v2/texturas/rosto_neutro_v3/previa_angulos/montar_pranchas.py
```
