# Fluxo ativo — 2D no Filmora

O usuário aprovou as dez poses do lote 01, incluindo o queixo corrigido da pose rindo, e definiu a produção com personagem 2D e animação por keyframes no Filmora. Não usar Blender neste fluxo. Os arquivos 3D antigos são histórico preservado.

## Assets e montagem

Usar PNGs transparentes da biblioteca, com poses e expressões adequadas à intenção da fala. Manter identidade, roupa, bigode e cavanhaque aprovados. Fazer movimentos de posição, escala, rotação e opacidade por keyframes no Filmora; entradas, saídas e trocas de pose devem acompanhar as falas e reações.

A boca nunca aparece. Na fala básica, mover somente o bigode. Para controle direto por keyframes, preparar uma base fixa com a região coberta e o bigode em uma camada transparente independente, sem deixar uma cópia fixa por baixo. Não animar a imagem inteira para simular movimento isolado do bigode. Os quadros A/B/C do lote 01 e o loop de 0,6 s são referência visual: ainda não constituem um personagem entregue em camadas separadas.

Priorizar gestos legíveis e transições curtas com início, sustentação e retorno, variando conforme o texto. Nas pausas, retornar o bigode ao repouso. Não aplicar oscilação repetitiva ao personagem inteiro.

## Estado atual

- Base e dez poses aprovadas pelo usuário após a revisão 1.1.
- PNGs, catálogo JSON e banco SQLite disponíveis em `lote_01/`.
- Nenhum novo WFP ou vídeo é criado apenas para registrar essa decisão.
- A expansão para cem poses ainda não foi produzida.
- Abertura, reprodução e exportação nativas no Filmora só podem ser declaradas após verificação no aplicativo.
