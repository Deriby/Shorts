# Materiais PS1 — proposta v4

O usuário pediu uma melhoria geral das texturas para aproximar o personagem dos jogos de PS1. Esta proposta parte do arquivo v3, preservando a geometria, o rig, o encaixe do rosto, os UVs e a franja. A etapa continua com **um único rosto neutro**, aguardando avaliação antes da biblioteca de expressões.

## Entrega

- [Comparação de corpo inteiro](Comparativo_Corpo.png) e [comparação do rosto](Comparativo_Rosto.png): mesmas câmeras, pose e iluminação nas versões v3/v4.
- [Nova prévia de corpo](Previa_Corpo.png) e [rosto](Previa_Rosto.png).
- [Oito direções de corpo e cabeça](previa_angulos/README.md).
- [Dery_Texturas_PS1_v4.blend](Dery_Texturas_PS1_v4.blend): nova versão com materiais e imagens incorporadas. A v3 permanece intacta.
- [materiais.json](materiais.json): orçamento de cores, cores usadas, paletas, resoluções e verificação de preservação do modelo.
- [geracao.json](geracao.json): registro da pintura dos tecidos em `Tecidos_Fonte.png`.

## O que mudou

A camiseta, o jeans, o tecido das mangas e o boné receberam novas pinturas de diffuse, com sombras largas, contraste contido e poucos detalhes por texel. O jeans perde os reflexos claros pintados que pareciam plástico. A camiseta e o boné usam tons neutros de preto; as mangas mantêm o cinza e deixam de reaproveitar as marcas escuras do material antigo no antebraço.

Cada tecido tem uma imagem nativa de 128×128 com orçamento de até 16 cores. Algumas pinturas escuras usam menos cores após a conversão, registrado no JSON. O rosto mantém 128×128 com até 128 cores, os detalhes originais de mãos/tênis usam 256×256 com até 128 cores e a franja mantém 128×64 com oito cores e o mesmo alfa binário. Os canais das paletas são quantizados para cinco bits. O dithering é aplicado na conversão de cor das texturas; na pele ele é bem mais discreto que nos tecidos. Todos os samplers usam Closest.

O desenho e a posição dos traços faciais foram preservados. As máscaras originais de pele permanecem ligadas à imagem original de classificação; a nova cor visível é separada dessa classificação para evitar deslocar gola, boné ou área da face. A cobertura do tecido no punho foi corrigida por material, sem mover vértices ou alterar pesos/UVs.

As pinturas de tecido usam coordenadas da posição de repouso do personagem, portanto acompanham a malha durante a animação. O ajuste frontal do boné e as máscaras de pele são preservados. Os UVs existentes, incluindo o encaixe facial variável da v3, não foram reconstruídos.

## Limites e verificação

O arquivo continua com 71 ossos, a mesma malha principal de 48.874 triângulos e a mesma tira de franja de 32 triângulos. Esta é uma revisão dos materiais; não otimiza a malha para o orçamento de hardware do PS1. As imagens PNG/RGBA usam cores limitadas como direção de arte, sem representar um formato nativo de jogo ou um emulador.

O script confere hashes de posições e UVs antes/depois e o SHA-256 do Blender v3 no disco. Nenhuma expressão ou animação nova foi criada. A iluminação Gouraud e as configurações da captura são as mesmas da v3; não há desfoque, glitch ou tremido adicionado à tela.

## Reproduzir

```bash
blender -b --disable-autoexec -t 4 --python assets/personagens/dery/rig_ps1_v2/texturas/estilo_ps1_v4/aplicar.py
python assets/personagens/dery/rig_ps1_v2/texturas/estilo_ps1_v4/comparar.py
blender -b --disable-autoexec -t 4 --python assets/personagens/dery/rig_ps1_v2/texturas/estilo_ps1_v4/previa_angulos/renderizar.py
python assets/personagens/dery/rig_ps1_v2/texturas/estilo_ps1_v4/previa_angulos/montar_pranchas.py
```

O quadro de tecidos gerado é separado em quatro células. A conversão para os tamanhos nativos e paletas ocorre no Blender. As fotos pessoais e os arquivos de cenas anteriores não são modificados ou copiados para esta entrega.
