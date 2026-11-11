# Refino da textura existente — proposta v5

Após rejeitar a troca de materiais da v4, o usuário pediu tentar novamente **apenas melhorando as texturas existentes da v3**. Esta proposta mantém os mesmos PNGs, desenhos, jeans, cores de roupa, encaixe facial e franja. Nenhuma pintura nova foi gerada e nenhum material da v4 foi reaplicado.

- [Antes/depois do corpo](Comparativo_Corpo.png) e [rosto](Comparativo_Rosto.png), com a mesma câmera e iluminação da v3.
- [Detalhe ampliado do jeans](Detalhe_Jeans.png), sem interpolação que borre os pixels.
- [Prévia de corpo](Previa_Corpo.png), [rosto](Previa_Rosto.png) e [Blender editável](Dery_v3_Refino_v5.blend).
- [Registro de preservação e parâmetros](refino.json).

## Acabamento aplicado

O material realça suavemente a diferença entre um texel e seus quatro vizinhos, com intensidade e variação máxima de cor limitadas. Isso reforça os detalhes que já existem. Rosto e franja usam intensidades menores. As imagens originais e seus pixels permanecem intactos e incorporados ao Blender.

Somente a cor visível do material principal do corpo usa uma grade de amostragem equivalente a 256×256 sobre o mesmo atlas de 512×512, tornando os texels mais aparentes. Os samplers usados na classificação da pele continuam nas coordenadas nativas; não houve troca de máscaras ou deslocamento de UVs. Rosto, franja e tecido das mangas mantêm suas resoluções nativas.

O efeito é discreto e reversível. Os nós `Refino | ...` controlam a nitidez de cada família de imagem; zero desliga esse realce. A grade de amostragem da roupa é uma etapa separada do realce. Não houve nova paleta, conversão de cores, dithering adicional, desfoque da tela ou novo desenho de dobras.

O script compara os pixels de todas as imagens, as posições dos vértices, os UVs, os índices de material e o SHA-256 do arquivo v3. O rig mantém seus 71 ossos. **A v3 continua como base selecionada; esta v5 aguarda avaliação.** Não iniciar expressões ou shorts por este pedido.

Ao implementar futuras trocas de expressão, atualizar todos os nós com o mesmo `DeryTextureFamily`, incluindo o texel central e as amostras vizinhas. Nesta etapa existe somente o rosto neutro.

## Reproduzir

```bash
blender -b --disable-autoexec -t 4 --python assets/personagens/dery/rig_ps1_v2/texturas/refino_v3_v5/refinar.py
python assets/personagens/dery/rig_ps1_v2/texturas/refino_v3_v5/comparar.py
python assets/personagens/dery/rig_ps1_v2/texturas/refino_v3_v5/detalhe_jeans.py
```
