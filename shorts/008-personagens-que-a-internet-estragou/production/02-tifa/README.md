# Personagens que a internet estragou — Tifa

Segundo bloco, com a voz enviada pelo usuário no pacote “2 - Tifa.zip”. Entregas 9:16 em 1080×1920 e 16:9 em 1920×1080, 24 fps, 28,083 segundos. A gravação original tem 27,395 segundos decodificados e foi mantida inteira, sem mudança de velocidade ou altura; há apenas silêncio após o fim.

## Arquivos

- `output/Tifa_Personagens_que_a_internet_estragou_9x16.mp4`: short vertical.
- `output/Tifa_Personagens_que_a_internet_estragou_16x9.mp4`: master horizontal com enquadramentos e imagens próprios.
- `output/Dery_Tifa.blend` e `output/Dery_Tifa_Master_16x9.blend`: quarto, sala de reunião, rig, expressões e voz.
- `assets/voz/voz_original.mp3`: arquivo original preservado byte a byte; os WAVs são decodificação e cópia com silêncio final.
- `assets/gameplay/`: dois recortes selecionados, sem o áudio original dos jogos, e o feed sincronizado para os monitores.
- `assets/memes/`: meme e notícia fornecidos, retratos e interfaces fictícias criadas para a encenação.
- `source_manifest.json`: inventário, hashes, identificação das versões dos jogos e intervalos selecionados. Os arquivos integrais e o ZIP continuam no acervo privado local, sem duplicação no Git.
- `timeline.json`, `acting_cues.json`, `face_cues.json`: cortes, gestos por frase e expressões discretas.
- `scene_validation*.json` e `export_validation*.json`: verificações de cena, áudio e MP4.

## Atuação e montagem

Vinte planos seguem a gravação: monitor, Dery, interface da chamada, apresentação da Tifa, soco único, combate, suspiro, meme, notícia e sala de reunião. A cena fora do quarto é uma encenação cômica: Dery sentado, mesa, microfone decorativo e telão. Não reproduz falas ou imagens de políticos reais. A geometria foi salva como [asset reutilizável](../../../../assets/cenarios/sala_reuniao/). Os avisos “CENSURADO”, “PARTICIPANTE REMOVIDO” e os cartões “ENCAMINHADO” ilustram o ocorrido sem mostrar o vídeo adulto ou inventar métricas.

Os braços usam preparação, gesto, sustentação, retorno e pausas, com tempos distintos por lado. A cabeça acompanha a intenção da fala e alterna tela/câmera. O soco é único; a reação na reunião tem interrupção, recuo, alívio e sorriso que desaparece. Não há ciclo periódico de braços. A referência pessoal de gestos do episódio 007 continua privada. As 31 expressões PNG permanecem disponíveis com troca seca e sem morphs. Não há legendas da narração embutidas nem fala gerada adicional.

O material fornecido inclui vídeos com títulos imprecisos: os dois trechos selecionados mostram **Final Fantasy VII Rebirth**, embora o nome de um upload mencione Remake. A notícia é uma captura fornecida pelo usuário sobre a reunião italiana de janeiro de 2022; a ilustração não afirma invasão de sistemas governamentais ou sessão plenária regular.

## Aparência PS1 e continuidade

Reaproveita a base validada da Lady: render nativo 360×640 / 640×360, ampliação inteira por vizinho mais próximo, texturas Closest, endereçamento do corpo em 128 px, geometria facetada, precisão de vértices reduzida com proteção de costuras do rosto, paleta de 5 bits e dithering Bayer fixo 4×4. Sem borrão, glitch ou piscadas aleatórias de luz.

Camiseta preta com M amarelo e correções de pele/mangas preservadas. As coordenadas do modelo original permanecem iguais nos dois atores. A cadeira da reunião mantém o mesmo apoio e a pose sentada; mãos usam IK sem alongamento. As versões compartilham atuação e áudio, com câmeras próprias; o vertical usa interfaces redesenhadas para leitura e a versão horizontal conserva o quadro dos jogos.

## Reproduzir

Com Blender 4.3, FFmpeg, NumPy e Pillow, a partir da raiz do repositório:

```sh
blender -b -t 2 --python-exit-code 1 --python shorts/008-personagens-que-a-internet-estragou/production/02-tifa/build_short.py
blender -b shorts/008-personagens-que-a-internet-estragou/production/02-tifa/output/Dery_Tifa.blend -t 1 --python-exit-code 1 --python shorts/008-personagens-que-a-internet-estragou/production/02-tifa/verify_scene.py
python shorts/008-personagens-que-a-internet-estragou/production/02-tifa/export_short.py
python shorts/008-personagens-que-a-internet-estragou/production/02-tifa/verify_export.py
```

Para o horizontal, adicionar `-- --wide` aos comandos do Blender e `--wide` aos scripts Python; carregar `Dery_Tifa_Master_16x9.blend` na verificação. Os quadros intermediários e relatórios são separados por formato. A exportação usa um processo Blender de dois threads por formato; neste ambiente, a exportação final roda um formato por vez para evitar contenção. A retomada `--resume` preserva quadros prontos. O render exclui a geometria do cenário que fica fora da câmera. Inserts de mídia dispensam render 3D.

`prepare_assets.py` é a etapa de ingestão e requer o inventário privado e os originais restaurados. As mídias preparadas necessárias ao render já estão versionadas. Baixar a pasta completa para editar os projetos, pois vídeos e áudio usam caminhos relativos. Quadros intermediários, backups, pacote ZIP e referências privadas não são versionados.
