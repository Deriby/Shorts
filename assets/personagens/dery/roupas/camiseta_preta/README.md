# Dery — camiseta preta com M amarelo

Roupa atual do personagem: camiseta preta, sem faixas, com o **M amarelo aprovado do Massacote Games no centro do peito**. A geometria e o caimento originais permanecem preservados; a mudança é somente no material e na projeção da estampa.

- [Modelo Blender com rig e expressões PNG](Dery_Camiseta_Preta.blend).
- [Prévia renderizada no próprio modelo](previa.png).
- [Aplicar a cor em cenas existentes](aplicar.py).
- [Reconstruir o arquivo e a prévia](preparar_modelo.py).
- [Verificação de geometria inalterada](modelo.json).

O modelo original, as proporções, as mangas, o rosto e os UVs existentes ficam preservados. O material preto substitui a aparência azul/branca somente nos polígonos da camiseta. A estampa usa [a logo original](../../../../marca/massacote-games/logo.png), projetada numa UV adicional na frente do peito. Ela acompanha a deformação da roupa pela rig, sem plano solto ou geometria adicional. O GLB e as texturas enviados pelo usuário permanecem nos caminhos originais.

Para próximos shorts que reutilizem uma cena antiga, importar `aplicar` deste diretório e chamar `aplicar(avatar)` em cada modelo do Dery. O procedimento altera os materiais e não move vértices ou shape keys. O arquivo autônomo mantém a biblioteca de 31 rostos e a precisão PS1 sem fissuras.
