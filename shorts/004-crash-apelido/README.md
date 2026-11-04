# O apelido mais quinta série do Crash

Episódio de **28 segundos** do Massacote Games, com Dery no quarto gamer PS1, voz enviada pelo usuário e gameplay no monitor. A curiosidade é o apelido interno “Sonic’s Ass Game” durante a criação do primeiro Crash Bandicoot.

## Assistir e editar

- [Teste de direção de 5 segundos — 9:16](production/output/Dery_Teste_Direcao_5s_9x16.mp4).
- [O mesmo teste em 16:9](production/output/Dery_Teste_Direcao_5s_16x9.mp4).
- [Estudo atual do encaixe do rosto — imagem](production/output/Dery_Teste_Encaixe_Olhos.png).
- [Comparação do primeiro encaixe com o teste atualizado](production/output/Dery_Encaixe_Rosto_Comparacao.png).
- [Short vertical — 1080 × 1920, 9:16](production/output/Dery_Crash_Short_9x16_R5.mp4).
- [Master horizontal — 1920 × 1080, 16:9](production/output/Dery_Crash_Master_16x9_R5.mp4).
- [Projeto Blender com rig, animação e câmeras](production/output/Dery_Crash_Master_R5.blend).
- [Biblioteca de 31 rostos aplicada no modelo](production/output/Dery_31_Rostos_No_Modelo.png).
- [31 PNGs, atlas e controlador reutilizável](../../assets/personagens/dery/expressions_ps1/v2/).
- [Doze rostos PS1 aplicados no Dery](production/output/Dery_Expressoes_PS1_Aplicadas.png).
- [Biblioteca reutilizável dos rostos](../../assets/personagens/dery/expressions_ps1/).
- [Imagem aprovada do enquadramento](production/output/Dery_Crash_Previa_16x9.png).
- [Roteiro e cortes](roteiro.md).

As duas exportações usam os mesmos quadros e a mesma narração. A edição vertical acompanha o Dery ou o monitor conforme a tomada. Não há legendas embutidas.

## Voz e montagem

Os dois WAVs originais foram preservados em [assets/voz](production/assets/voz/), com os hashes e a ordem documentados em [audio.json](production/audio.json). Somam **27,448 segundos**; a entrega mantém a velocidade e o tom originais e termina com uma pausa curta para a reação. O áudio final inclui efeitos digitais discretos, gerados localmente.

A revisão tem treze tomadas, entre closes, plano do quarto e detalhes do monitor. O Dery olha para a câmera e para o jogo, gesticula, move cabeça e tronco e troca a textura do rosto em corte seco. A fala alterna rostos com boca aberta e fechada em passos de três quadros, conforme a energia da voz, sem sincronização fonética detalhada. A gameplay permanece em reprodução contínua durante todo o episódio. Os braços alternam gestos de conversa na altura do peito, com rotação dos punhos e ênfases com as duas mãos.

## Visual e fontes

A pose sentada e a atmosfera da prévia foram mantidas. A iluminação foi preparada uma vez no cenário e armazenada num atlas do quarto e em cores dos vértices do Dery, permitindo renderizar a animação com o mesmo ambiente. O efeito de borda é um modificador nativo de Geometry Nodes: a precisão dos vértices próximos à silhueta varia com a câmera. Cabeça e corpo compartilham a junção do pescoço, evitando a abertura vista nos testes antigos.

Os quadros nativos têm 640 × 360 pixels, com amostragem de textura sem interpolação, dithering ordenado e ampliação por vizinho mais próximo. Na revisão R2, o personagem, o vídeo e a câmera usam 24 fps. A imagem não usa os filtros fortes de suavização rejeitados no teste anterior.

Na revisão R2, o monitor usa exclusivamente a gameplay do **Crash original de PS1 enviada pelo usuário**, em reprodução contínua. As fontes das versões anteriores e o novo arquivo estão documentados em [fontes.json](production/assets/gameplay/fontes.json).

## Reproduzir

Requisitos: Blender 4.3, FFmpeg e os arquivos Git LFS do repositório. O quarto e o personagem vêm do teste 003; os materiais de voz e gameplay deste episódio estão na pasta 004.

```bash
python shorts/004-crash-apelido/production/prepare_assets.py
blender -b -t 4 --python shorts/004-crash-apelido/production/build_short.py
blender -b shorts/004-crash-apelido/production/output/Dery_Crash_Master_R2.blend -t 1 --python shorts/004-crash-apelido/production/plan_crops.py
python shorts/004-crash-apelido/production/export_short.py
```

`prepare_assets.py` reutiliza a sequência de gameplay versionada. A regeneração dessa sequência a partir da montagem original requer o arquivo fonte descrito em `fontes.json`. `build_short.py` prepara a iluminação e o projeto editável; `export_short.py` renderiza os quadros e monta as duas proporções. Para remontar arquivos já renderizados, use `export_short.py --encode-only`.

Renders intermediários e backups do Blender ficam fora do Git.

## Revisão R2

Gameplay original enviada pelo usuário, preservada em `production/assets/gameplay/crash_ps1_enviado.mp4`. Trecho contínuo de 6 a 34 segundos, convertido a 24 fps para o monitor, sem congelamento. Brilho da tela aumentado. A revisão usa a base já iluminada, com 13 tomadas, movimentos dos dois braços, cabeça e tronco, sobrancelhas e sorriso discretos na malha. Os olhos usam a textura original, sem sobreposição das expressões PNG.

Para reproduzir a revisão, execute `revise_r2.py` no Blender e depois `export_short.py --revision r2 --preset veryfast`. A versão anterior continua no histórico do repositório.

## Revisão R3 — expressões e gestos

Revisão sobre o projeto R2, mantendo a voz, a gameplay enviada, o brilho do monitor, o cenário, as câmeras e os treze cortes. O sorriso agora movimenta a malha do rosto, os olhos e as bochechas, e ganha dentes no material. Há também uma sobrancelha levantada e uma reação de surpresa na piada. As expressões ficam concentradas nas tomadas do Dery.

Os braços usam IK de duas articulações, com alvos dos punhos e controle dos cotovelos. As mãos sobem para aparecer nos enquadramentos e alternam ênfases conforme as frases. A orientação dos cotovelos é calculada com os ossos em repouso para evitar torção dos braços.

```bash
blender -b -t 4 --python shorts/004-crash-apelido/production/revise_r3.py
python shorts/004-crash-apelido/production/export_short.py --revision r3 --preset veryfast
```

Para reconstruir a partir do projeto R2, `revise_r3.py` reaproveita os 150 quadros aprovados das tomadas focadas no monitor, caso os renders R2 estejam disponíveis localmente. A lista está em [reuse_r3.json](production/reuse_r3.json). Com esse cache, a exportação renderiza os outros 522 quadros e gera as duas proporções; sem o cache, renderiza os 672 quadros. Os renders intermediários não são versionados.

## Revisão R4 — troca de texturas PS1

O rosto agora usa imagens pré-desenhadas que trocam instantaneamente. Todas as deformações faciais anteriores ficam desativadas. A biblioteca compartilhada tem doze PNGs de 128 × 128, incluindo fala, sorriso, risada, deboche, susto e piscada. Um atlas com amostragem `Closest` e a propriedade `PS1_face_id` tornam o sistema reutilizável em outros episódios. As chaves usam interpolação `CONSTANT`.

Os gestos, as câmeras, os treze cortes, o cenário, a voz e a gameplay da revisão R3 foram mantidos. [face_cues_r4.json](production/face_cues_r4.json) registra os quadros em que o rosto muda.

```bash
blender -b -t 4 --python shorts/004-crash-apelido/production/revise_r4.py
python shorts/004-crash-apelido/production/export_short.py --revision r4 --preset veryfast
```

Os PNGs e o atlas já estão prontos na pasta compartilhada; os comandos não fazem novas gerações de imagem. Todos os 672 quadros são renderizados para aplicar o mesmo material facial também nas tomadas em que o Dery aparece na borda do enquadramento.

## Estudo de encaixe — somente imagens

Estudo após o retorno sobre a aplicação dos desenhos no modelo. Os PNGs aprovados ficam preservados. O estudo mantém o nariz original, encaixa olhos e boca separadamente, suaviza as descontinuidades da iluminação facial e corrige a sombra abaixo dos olhos no material. O espaçamento dos olhos usa o meio-termo entre os dois testes de distância: deslocamento de 7,5 mm por lado no espaço original da malha, com transição suave antes das sobrancelhas.

O projeto [Dery_Face_Fit_Study.blend](production/output/Dery_Face_Fit_Study.blend) contém o teste estático com o controlador de rostos. O estudo é gerado por `blender -b -t 4 --python shorts/004-crash-apelido/production/test_face_fit.py`. As exportações R4 da etapa anterior mostram o encaixe anterior; a revisão R5 abaixo incorpora este ajuste à animação.

## Revisão R5 — 31 rostos e encaixe revisado

A biblioteca tem 31 expressões desenhadas: doze preservadas e dezenove novas. Cada rosto é um PNG de 128 × 128, reunido num atlas 8 × 4. A propriedade `PS1_face_id` escolhe de 0 a 30, com chaves `CONSTANT` para a troca seca de textura. O atlas não mistura expressões, e não há deformação facial animada.

Esta revisão incorpora o encaixe do estudo: nariz original, áreas de olhos e boca separadas, espaçamento intermediário dos olhos e correção localizada das olheiras. As descontinuidades mais fortes da iluminação facial foram removidas. A voz, a gameplay, as câmeras e os gestos de corpo/braços continuam os mesmos da revisão anterior.

As expressões do episódio foram escolhidas pela narração: explicação séria, deboche na piada, susto, pausa sem reação e risada final. A fala alterna os desenhos de boca aberta/fechada em passos de três quadros. A lista das trocas está em [face_cues_r5.json](production/face_cues_r5.json). Todos os 31 rostos foram renderizados no mesmo enquadramento para conferir o encaixe; o episódio usa uma seleção deles.

```bash
blender -b -t 4 --python shorts/004-crash-apelido/production/revise_r5.py
python shorts/004-crash-apelido/production/export_short.py --revision r5 --preset veryfast
```

O projeto R5 inclui a biblioteca instalada e usa os desenhos já versionados, sem novas gerações de imagem. `render_face_gallery.py` gera a conferência dos rostos aplicada na malha. A edição final mantém 28 segundos e 24 fps, em 16:9 e 9:16, sem legendas embutidas.

## Teste de direção — 5 segundos

Teste curto sobre a frase já gravada “Respeita o Crash. Essa bundinha tem história”, reaproveitando cenário, modelo, gameplay e biblioteca de rostos. A montagem abre no monitor, mostra Dery virando para falar com a câmera, aproxima durante a piada e termina com uma encarada séria, um som digital discreto e uma piscada. Os braços relaxam ao final para deixar a atenção no rosto.

| Tempo | Ação |
| --- | --- |
| 0,00–0,83 s | Aproximação do monitor, com som do jogo baixo. |
| 0,83–2,04 s | Plano médio, virada para a câmera: “Respeita o Crash”. |
| 2,04–3,83 s | Close com deboche: “Essa bundinha tem história”. |
| 3,83–5,00 s | Close mais próximo, reação séria, pausa, som curto e piscada. |

O WAV do teste usa o trecho original de 24,30 a 27,30 segundos, começando em 0,80 s, com velocidade e tom preservados. A gameplay enviada toca no monitor; seu áudio aparece apenas na abertura. O som digital foi gerado localmente. A edição mantém os pixels e as bordas PS1, e não tem legendas embutidas.

- [Projeto Blender do teste](production/output/Dery_Teste_Direcao_5s.blend).
- [Tempos, enquadramentos e trocas de rosto](production/direction_test_timeline.json).

```bash
blender -b -t 4 --python-exit-code 1 --python shorts/004-crash-apelido/production/build_direction_test.py
python shorts/004-crash-apelido/production/export_direction_test.py
```

O teste renderiza somente 120 quadros. Os comandos reaproveitam os ativos locais e não geram novos desenhos nem uma nova voz.
