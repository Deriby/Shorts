# Personagens que a internet estragou — Chun-Li

Terceiro bloco da série, com voz, imagens e vídeos enviados pelo usuário no pacote “3 - Chun-Li.zip”. Versões 9:16 em 1080×1920 e 16:9 em 1920×1080, 24 fps, 40 segundos. A gravação decodificada tem 39,327 segundos e foi preservada inteira, sem acelerar, mudar o tom ou acrescentar falas. Há silêncio final para sustentar a reação.

## Entregas e arquivos

- `output/ChunLi_Personagens_que_a_internet_estragou_9x16.mp4`: short vertical.
- `output/ChunLi_Personagens_que_a_internet_estragou_16x9.mp4`: master horizontal com enquadramentos próprios.
- `output/Dery_ChunLi.blend` e `output/Dery_ChunLi_Master_16x9.blend`: quarto, balcão de fiscalização, câmera de pedestal, rig, atuação, faces e voz.
- `assets/voz/voz_original.mp3`: gravação original byte a byte. Os WAVs são sua decodificação e cópia com silêncio final.
- `assets/gameplay/`: três trechos selecionados e o feed sincronizado dos monitores; sem as trilhas sonoras originais dos vídeos.
- `assets/memes/`: imagens fornecidas preparadas para a montagem, galeria censurada e gráficos autorais de fiscalização. Imagens grandes foram reduzidas antes da montagem para evitar decodificar o original em cada quadro.
- `source_manifest.json`: nomes originais, hashes, trechos, filtros e identificação dos jogos. O ZIP e os vídeos integrais ficam no acervo local, fora do Git.
- `timeline.json`, `acting_cues.json`, `face_cues.json`: montagem, gestos por frase e trocas de face dos dois atores.
- `scene_validation*.json` e `export_validation*.json`: verificações da cena, áudio e MP4 por formato.

## Montagem e atuação

Os 26 planos seguem a gravação: apresentação no monitor, golpe de Street Fighter, retrato clássico, luta, Dery convencido, suspiro e deboche, memes das pernas e do Jackie Chan, galeria ilustrativa censurada, crossover e dança em Fortnite. O fim sai do quarto: câmera de pedestal, revelação do balcão “FISCALIZAÇÃO DE SKIN”, ficha de prioridades e olhar sem reação do fiscal.

A ficha é uma gag gráfica: “VENCER A PARTIDA” fica sem marca; “CONFERIR A SKIN” ganha um check. Ela não representa uma interface real do jogo ou estatísticas de jogadores. A galeria censurada é autoral e não mostra material adulto. Os memes usados são não explícitos; o original do pacote foi preservado localmente.

Os gestos têm preparação, sustentação e repouso, com curvas diferentes entre os braços. Há apresentação, confiança, retração no suspiro, um pequeno gesto interrompido, uma única passagem curta com duas batidas de ombro e a irritação do fiscal. Sem ciclo contínuo de braços. A referência pessoal de gestos do episódio 007 continua privada. As expressões PNG mudam de uma vez; o sorriso acompanha a risada, e a boca repousa nas pausas. Não há legendas da narração embutidas nem vocalizações geradas.

A narração termina em “fiscalizar a skin” e no suspiro, conforme a versão do usuário. Não há a frase antiga sobre apagar o histórico. Os cortes foram alinhados aos segmentos da gravação recebida, não impostos a partir de uma duração prevista.

## Cenário, aparência e formatos

O balcão adapta a geometria da sala de reunião da Tifa: paredes, piso, mesa, cadeira e tela. Foram acrescentados painel frontal, placa, ficha e câmera simples de pedestal. Dery permanece sentado, com a pose e as proporções originais. Não há nova roupa, fila de figurantes, personagem Chun-Li 3D ou contato complexo de mãos com objetos.

Mantém a camiseta preta com M amarelo, correções de pele/mangas, 31 faces PNG e a precisão de vértices que protege as costuras do rosto. Render nativo 360×640 / 640×360 com upscale inteiro 3× por vizinho mais próximo, texturas Closest, corpo endereçado em 128 px, geometria facetada, quantização de 5 bits e dithering Bayer fixo 4×4. Sem blur, glitch ou luz piscando aleatoriamente.

A placa vertical usa duas linhas e posição própria para permanecer legível. Câmeras e recortes dos jogos são independentes por formato; o horizontal preserva o quadro completo. A ficha e a galeria têm composições próprias no vertical.

O material de luta é **Street Fighter 6**, contemporâneo: não foi apresentado como captura de Street Fighter II ou prova da ocupação atual da personagem. O retrato clássico acompanha a apresentação da carreira. A frase “arrisco dizer” permanece opinião, sem ranking inventado. O ano de 2021 situa a chegada a Fortnite; a montagem não inventa uma data para as primeiras obras de fãs.

## Reproduzir

Na raiz do repositório, com Blender 4.3, FFmpeg, NumPy e Pillow:

```sh
blender -b -t 2 --python-exit-code 1 --python shorts/008-personagens-que-a-internet-estragou/production/03-chun-li/build_short.py
blender -b shorts/008-personagens-que-a-internet-estragou/production/03-chun-li/output/Dery_ChunLi.blend -t 1 --python-exit-code 1 --python shorts/008-personagens-que-a-internet-estragou/production/03-chun-li/verify_scene.py
python shorts/008-personagens-que-a-internet-estragou/production/03-chun-li/export_short.py
python shorts/008-personagens-que-a-internet-estragou/production/03-chun-li/verify_export.py
```

Para o horizontal, adicionar `-- --wide` aos comandos Blender e `--wide` aos scripts Python; carregar `Dery_ChunLi_Master_16x9.blend` na verificação. Quadros e relatórios ficam separados por formato. `--resume` na exportação aproveita quadros completos existentes; o padrão renderiza novamente os planos 3D. `--encode-only` refaz apenas a codificação a partir dos quadros prontos.

Somente os planos 3D passam pelo Blender. O cenário fora da câmera fica oculto no render; cada formato usa um processo de dois threads e os formatos são renderizados em sequência para evitar a contenção observada no processamento paralelo. Quadros são salvos por renomeação de arquivo temporário para a retomada não considerar PNGs incompletos. Gameplay, fotos e gráficos entram diretamente na montagem.

`prepare_assets.py` é a ingestão e requer o inventário privado e os originais restaurados; as mídias preparadas já estão versionadas. Para editar os projetos, baixar a pasta inteira, pois áudio e vídeos usam caminhos relativos. Renders intermediários, backups, pacote ZIP e referência pessoal ficam fora do Git.
