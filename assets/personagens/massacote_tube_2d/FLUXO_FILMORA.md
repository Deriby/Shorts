# Fluxo ativo — 2D no Filmora

O usuário aprovou as dez poses do lote 01, incluindo o queixo corrigido da pose rindo, e definiu a produção com personagem 2D e animação por keyframes no Filmora. Não usar Blender neste fluxo. Os arquivos 3D antigos são histórico preservado.

## Referência no Drive

O usuário esclareceu que a movimentação deve seguir o personagem 2D do vídeo de referência já guardado no Drive. Link localizado no histórico do projeto: [vídeo sobre materiais perdidos de Carros, 16min16s](https://drive.google.com/file/d/1wVZ7iaKOuyQ5a0wD0Ij3zOy3_sG9UsO-/view). O arquivo do Drive é um ZIP contendo `referencia.mp4` (1280 × 720, 30 fps).

A análise anterior está em `shorts/009-jogos-que-a-internet-tentou-cancelar/production/14-video-completo/revisao_memes_v3/ANALISE_REFERENCIA.md` e os metadados em `revisao_memes_v3/referencia_visual.json`. Ela registra avatar, gestos, reenquadramentos e alternância com cenas/ilustrações; na abertura, apresentação de 0–2,4 s, cena ilustrativa aproximadamente de 2,4–7,8 s e retorno mais próximo ao avatar. Usar o movimento do apresentador 2D como referência para os keyframes e a atuação das poses, com o bigode cobrindo a boca.

Nesta retomada foram recuperados o link e a análise salva; não houve nova reprodução do vídeo. O cache antigo indicado pelos metadados (`/workspace/attachments/memes009/referencia.mp4`) está ausente nesta máquina. Antes de medir movimentos ou copiar timings específicos, reabrir o arquivo original do Drive. Conferir os registros e caches existentes antes de pedir reenvio ao usuário. Não tratar os intervalos de montagem da análise como velocidade de animação do personagem.

## Assets e montagem

Usar PNGs transparentes da biblioteca, com poses e expressões adequadas à intenção da fala. Manter identidade, roupa, bigode e cavanhaque aprovados. Fazer movimentos de posição, escala, rotação e opacidade por keyframes no Filmora; entradas, saídas e trocas de pose devem acompanhar as falas e reações.

A boca nunca aparece. Na fala básica, mover somente o bigode. Para controle direto por keyframes, preparar uma base fixa com a região coberta e o bigode em uma camada transparente independente, sem deixar uma cópia fixa por baixo. Não animar a imagem inteira para simular movimento isolado do bigode. Os quadros A/B/C do lote 01 e o loop de 0,6 s são referência visual. As poses conversando e apontando agora têm corpo, cabeça e bigode separados em `previa_01/Filmora/midias/`, com índice em `previa_01/rig_camadas.json`; a prévia de movimento ainda aguarda avaliação.

Priorizar gestos legíveis e transições curtas com início, sustentação e retorno, variando conforme o texto. Nas pausas, retornar o bigode ao repouso. Não aplicar oscilação repetitiva ao personagem inteiro.

## Estado atual

- Base e dez poses aprovadas pelo usuário após a revisão 1.1.
- PNGs, catálogo JSON e banco SQLite disponíveis em `lote_01/`.
- Prévia solicitada: `previa_01/Previa_Conversando_2D.mp4`, 9,3 s com trecho da voz existente; WFP editável com corpo/cabeça/bigode e keyframes. Abertura nativa ainda não testada.
- A expansão para cem poses ainda não foi produzida.
- Abertura, reprodução e exportação nativas no Filmora só podem ser declaradas após verificação no aplicativo.
