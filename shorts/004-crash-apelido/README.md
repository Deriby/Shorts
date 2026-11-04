# O apelido mais quinta série do Crash

Episódio de **28 segundos** do Massacote Games, com Dery no quarto gamer PS1, voz enviada pelo usuário e gameplay no monitor. A curiosidade é o apelido interno “Sonic’s Ass Game” durante a criação do primeiro Crash Bandicoot.

## Assistir e editar

- [Short vertical — 1080 × 1920, 9:16](production/output/Dery_Crash_Short_9x16_R2.mp4).
- [Master horizontal — 1920 × 1080, 16:9](production/output/Dery_Crash_Master_16x9_R2.mp4).
- [Projeto Blender com rig, animação e câmeras](production/output/Dery_Crash_Master_R2.blend).
- [Imagem aprovada do enquadramento](production/output/Dery_Crash_Previa_16x9.png).
- [Roteiro e cortes](roteiro.md).

As duas exportações usam os mesmos quadros e a mesma narração. A edição vertical acompanha o Dery ou o monitor conforme a tomada. Não há legendas embutidas.

## Voz e montagem

Os dois WAVs originais foram preservados em [assets/voz](production/assets/voz/), com os hashes e a ordem documentados em [audio.json](production/audio.json). Somam **27,448 segundos**; a entrega mantém a velocidade e o tom originais e termina com uma pausa curta para a reação. O áudio final inclui efeitos digitais discretos, gerados localmente.

A revisão tem treze tomadas, entre closes, plano do quarto e detalhes do monitor. O Dery olha para a câmera e para o jogo, gesticula, move cabeça e tronco e movimenta a boca conforme a energia da voz. A abertura de boca é estilizada, sem sincronização fonética detalhada. A gameplay permanece em reprodução contínua durante todo o episódio. A revisão remove as expressões PNG sobrepostas aos olhos e usa movimentos sutis da própria malha, gestos mais amplos e mais movimentos da cabeça e do corpo.

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
