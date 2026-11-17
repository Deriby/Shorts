# Massacote Tube — 30 poses novas e 10 novos olhares

Lote 02, adicional às dez poses e treze olhares aprovados do lote 01. Mantém o personagem Samurai Jack com acabamento digital amador, cabelo curto, M vermelho e boca escondida pelo bigode. As novas artes aguardam avaliação do usuário.

Extraia o ZIP inteiro e abra **galeria.html** no navegador para experimentar combinações e escolher PNGs. As pranchas `Previa_Poses_1.jpg`, `Previa_Poses_2.jpg` e `Previa_Poses_3.jpg` mostram as poses montadas; `Previa_10_Olhares.jpg` mostra os olhares novos.

## Peças

- `poses/`: 30 bases sem olhos, sobrancelhas, nariz, boca ou bigode; IDs 11–40.
- `olhos/`: dez novos pares de olhos/sobrancelhas, IDs 13–22.
- `olhos_base/`: os treze pares anteriores, copiados sem alteração para o pacote funcionar sozinho.
- `bigode/`: os mesmos três estados aprovados, sem redesenho.
- `rig/`: cabeça limpa comum e trinta corpos separados para keyframes.
- `frente/`: mão que passa na frente do rosto, quando necessária.
- `montados/`: PNGs transparentes prontos para usar sem animar o rosto e JPGs de consulta.
- `catalogo.json` e `catalogo.sqlite`: banco consultável com caminhos, títulos, categorias, hashes, aprovação e mapa das camadas.
- `fontes/`: artes originais produzidas com image_gen. Para editar, prefira os PNGs tratados nas pastas acima.

## Montagem no Filmora

Todas as peças têm **1024 × 1536**. Importe sem recortar e aplique a mesma posição, escala e rotação ao conjunto. Mantenha a proporção; o espaço transparente é necessário para o encaixe.

Ordem de baixo para cima: **pose limpa → olhos → bigode → mão à frente**. Para cabeça e corpo se moverem separadamente: **corpo → cabeça → olhos → bigode → mão à frente**. O mapa `rig` no catálogo informa os arquivos de cada pose. A pose 25 pede a mão de primeiro plano acima do bigode para o gesto de silêncio funcionar.

Pivô da cabeça: `(466, 738)`; pivô do bigode: `(468, 515)` no canvas original. A cabeça e o desenho do bigode são os mesmos do lote aprovado. Troque os olhares sem deslocar a camada; os estados de piscada continuam em `olhos_base/`.

Na fala, anime somente pequenas mudanças de posição/escala do bigode ou alterne seus estados conforme a voz e as pausas. Nunca revele uma boca. Use keyframes leves para inclinação e transições de pose. Esta entrega é uma biblioteca de PNGs; não inclui uma nova animação ou projeto WFP.

## Banco acumulado

O repositório também contém `../banco_catalogo.json` e `../banco_catalogo.sqlite`, reunindo **40 poses, 23 olhares e três estados de bigode**, sem duplicar os itens compartilhados. O lote aprovado continua intacto, com a aprovação vinculada aos arquivos originais.

Downloads oficiais: [pasta do lote no GitHub](https://github.com/Deriby/Shorts/tree/main/assets/personagens/massacote_tube_2d/modular_02).
