# Personagens que a internet estragou — Ankha

Quarto bloco, produzido a partir da voz e das mídias enviadas pelo usuário no pacote “4 - Ankha.zip”. Entregas 9:16 em 1080×1920 e 16:9 em 1920×1080, 24 fps e 44,042 segundos. A voz decodificada tem 43,350 segundos e foi preservada inteira, sem acelerar, mudar o tom ou acrescentar falas. Há apenas silêncio após o fim da gravação.

## Arquivos

- `output/Ankha_Personagens_que_a_internet_estragou_9x16.mp4`: short vertical.
- `output/Ankha_Personagens_que_a_internet_estragou_16x9.mp4`: master horizontal com câmeras e composição próprias.
- `output/Dery_Ankha.blend` e `output/Dery_Ankha_Master_16x9.blend`: quarto, museu, rig, atuação, faces PNG, voz e objetos da gag.
- `assets/voz/voz_original.mp3`: arquivo recebido, preservado byte a byte. Os WAVs são decodificação e cópia com silêncio final.
- `assets/gameplay/`: recortes selecionados e feed sincronizado do monitor.
- `assets/memes/`: imagens preparadas do usuário, retrato da exposição, etiqueta de cassete, janelas ilustrativas, dupla de peças e selo de perdão.
- `timeline.json`, `acting_cues.json`, `face_cues.json`: os 22 planos, gestos por frase e trocas de rosto de ambos os atores.
- `source_manifest.json`: inventário, hashes, origem e intervalos dos trechos usados. O ZIP e os originais integrais continuam fora do repositório.
- `scene_validation*.json` e `export_validation*.json`: verificações de geometria, rosto, apoio, IK, áudio e MP4.

## Atuação e montagem

A montagem segue a gravação real: apresentação da Ankha no monitor, reação ao animador, identificação do visual egípcio e da ilha, entrada no museu, explicação de 2021, cassete “Camel by Camel — Sandy Marton”, dupla associação, memes, pesquisa, aviso de Dery e perdão final.

O museu adapta o piso, a parede e as colunas da entrada do castelo. Tem dois pedestais: um retrato normal da Ankha e um cassete autoral. As peças dão um salto curto e alternado na expressão “double kill”; a mesma ideia ganha um cartão gráfico com composição própria por formato. No final, Dery abre uma palma e aparece “PERDOADO”, acompanhando a fala “Nós te perdoamos”. O cenário também foi preparado como [asset genérico reutilizável](../../../../assets/cenarios/museu/), com superfícies neutras.

Dery mantém a camiseta preta com M amarelo e o modelo original. No quarto, usa apresentação contida, suspiro e um único gesto de aviso; no museu, fica em pé com os pés estáveis, alterna as indicações dos dois itens e termina acolhendo o espectador. Os braços usam preparação, sustentação e retorno com tempos diferentes, sem ciclo periódico. As 31 expressões PNG permanecem disponíveis, com trocas secas e sorrisos nas risadas. A referência pessoal de gestos permanece privada.

As janelas de galeria e pesquisa são montagens autorais com prévias opacas. Não há animação adulta original, material gráfico ou personagem criança ilustrando o aviso. Os memes selecionados são não explícitos. Não há legendas da narração embutidas, fala extra ou os finais antigos sobre histórico e TikTok.

O vídeo “Ankha Sings I Love You” usa uma apresentação musical editada por fãs sobre imagem de Animal Crossing. O trecho de “Camel by Camel” é um cover/remake enviado pelo usuário, não uma gravação original de Sandy Marton. Ambos são apoio visual: a trilha final preserva apenas a voz fornecida, com os áudios dos vídeos de referência mutados. A identificação da música também fica no cassete e no texto de cena.

## Visual e formatos

Reutiliza o visual aprovado: render nativo 360×640 / 640×360, ampliação inteira 3× por vizinho mais próximo, precisão reduzida nas bordas com proteção de costuras do rosto, texturas Closest, corpo endereçado em 128 px, geometria facetada, quantização de 5 bits e Bayer fixo 4×4. A pedra do museu usa um padrão próprio de 32 px. Sem blur, glitch ou luz piscando.

As imagens muito grandes foram reduzidas antes da preparação do monitor. O museu tem distâncias de câmera e separação de pedestais próprias por formato; o cassete recebe um close que mantém título e artista legíveis. A dupla de peças e as janelas têm layout vertical e horizontal próprios. Os gráficos “DOUBLE KILL” e “PERDOADO” são compostos antes da quantização da imagem final.

## Reproduzir

Na raiz do repositório, com Blender 4.3, FFmpeg, NumPy e Pillow:

```sh
blender -b -t 2 --python-exit-code 1 --python shorts/008-personagens-que-a-internet-estragou/production/04-ankha/build_short.py
blender -b shorts/008-personagens-que-a-internet-estragou/production/04-ankha/output/Dery_Ankha.blend -t 1 --python-exit-code 1 --python shorts/008-personagens-que-a-internet-estragou/production/04-ankha/verify_scene.py
python shorts/008-personagens-que-a-internet-estragou/production/04-ankha/export_short.py
python shorts/008-personagens-que-a-internet-estragou/production/04-ankha/verify_export.py
```

Para o horizontal, adicionar `-- --wide` aos comandos Blender e `--wide` aos scripts Python; carregar `Dery_Ankha_Master_16x9.blend` na verificação. Quadros e relatórios são separados por formato. `--resume` aproveita quadros completos; `--encode-only` refaz apenas a codificação a partir deles. O padrão renderiza novamente os planos 3D.

Somente ator, monitor e museu passam pelo Blender. O cenário fora da câmera fica oculto, e os formatos usam um processo de dois threads por vez. Os PNGs são salvos por renomeação de arquivo temporário para permitir retomada. Imagens, gameplay e gráficos entram diretamente na montagem.

`prepare_assets.py` é a ingestão e requer os originais e o inventário privado restaurados. As mídias preparadas necessárias ao render já estão versionadas. Baixar a pasta inteira para editar os projetos, pois áudio e filmes usam caminhos relativos. Quadros intermediários, backups, ZIP e referência privada ficam fora do Git.
