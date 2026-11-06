# Intro — Personagens que a internet estragou

Abertura exclusiva do vídeo longo, produzida com a gravação enviada pelo usuário e materiais existentes. **16:9 em 1920×1080, 24 fps, 32,875 segundos**. A voz decodificada tem 32,209 segundos e foi preservada inteira, sem mudar velocidade, tom ou falas. Há cerca de 0,666 s de silêncio final. Nenhuma versão vertical foi gerada.

## Direção e continuidade

O usuário pediu menos cortes sem nexo e mais criatividade. A intro tem **três planos e dois cortes de imagem**:

1. Reunião ilustrativa em tela cheia, usando os estados já preparados para a Tifa: imagem normal, interrupção censurada e participante removido.
2. O mesmo estado aparece no CRT do quarto. Uma câmera contínua recua para revelar Dery, acompanha a apresentação dos casos e volta ao monitor quando ele seleciona a Lady.
3. A seleção termina no mesmo primeiro quadro do master da Lady, preparando a ligação com o bloco 01.

O arquivo cresce dentro da mesma tela. Quatro cartões acompanham “vilã, heroína, princesa e ouriço”; depois, o catálogo revela os 12 casos. As prévias suspeitas ficam opacas. Na frase sobre ideias que ninguém precisava ter tido, uma pasta “IDEIAS” vai uma única vez para a lixeira. O cursor abre o caso 01 no fechamento.

O título aparece uma vez como janela do arquivo, durante quatro segundos. Não há legendas da narração. Os gestos são planejados por ideia completa, com braços em tempos diferentes, pausas e retornos. As 31 faces PNG mudam por corte. A camiseta preta com M amarelo, pele limpa, mangas e geometria do modelo foram mantidas. A referência pessoal de gestos permanece privada.

## Reaproveitamento e escopo

A reunião é a encenação autoral do episódio da Tifa, com identificação “ENCENAÇÃO” preservada. O catálogo usa retratos normais dos 12 episódios; referências a conteúdo adulto usam somente cartões inteiramente opacos. Não há nova obtenção de mídia, voz adicional ou áudio retirado dos episódios.

O quadro de saída foi extraído do primeiro frame do master horizontal publicado da Lady. O vídeo da Lady e os demais 11 blocos não foram alterados. A montagem integral do longo não foi exportada nesta etapa.

## Arquivos

- `output/Intro_Personagens_que_a_internet_estragou_16x9.mp4`: final horizontal.
- `output/Dery_Intro_Personagens_16x9.blend`: quarto, Dery, câmera, faces, monitor e áudio.
- `assets/voz/voz_original.mp3`: original recebido, preservado byte a byte. Os WAVs são a decodificação e a cópia com silêncio final.
- `assets/gameplay/monitor_montado.mp4`: desenvolvimento contínuo da interface do monitor.
- `assets/memes/`: fontes reutilizadas, catálogo e quadro de entrada da Lady.
- `timeline.json`: três planos finais; `screen_cues.json`: ações dentro da interface, sem confundir cada estado com um corte de câmera.
- `acting_cues.json`, `face_cues.json`: gestos, olhares, trajetórias e expressões.
- `source_manifest.json`: procedência, hashes e escolhas editoriais.
- `scene_validation.json`, `export_validation.json`: verificações da câmera contínua, corpo, rosto, mãos, áudio e MP4.

## Visual e reprodução

Render nativo 640×360, ampliação inteira 3× por vizinho mais próximo, precisão de geometria reduzida com proteção das costuras, texturas Closest, corpo endereçado em 128 px, paleta RGB de 5 bits e Bayer fixo 4×4. O visual PS1 não usa blur, glitch ou luz piscando.

Na raiz do repositório, com Blender 4.3, FFmpeg, NumPy e Pillow:

```sh
python shorts/008-personagens-que-a-internet-estragou/production/00-intro/prepare_assets.py
blender -b -t 2 --python-exit-code 1 --python shorts/008-personagens-que-a-internet-estragou/production/00-intro/build_intro.py
blender -b shorts/008-personagens-que-a-internet-estragou/production/00-intro/output/Dery_Intro_Personagens_16x9.blend -t 1 --python-exit-code 1 --python shorts/008-personagens-que-a-internet-estragou/production/00-intro/verify_scene.py
python shorts/008-personagens-que-a-internet-estragou/production/00-intro/export_intro.py
python shorts/008-personagens-que-a-internet-estragou/production/00-intro/verify_export.py
```

`prepare_assets.py` usa os materiais dos episódios existentes e os metadados da voz em `audio.json` (ou o intake local, quando disponível); as mídias preparadas necessárias ao projeto e ao render ficam versionadas. A interface inicial e a saída são compostas diretamente; somente o plano do quarto é renderizado em Blender, com dois threads. `--resume` retoma quadros completos e `--encode-only` codifica os existentes. Baixar a pasta inteira para editar: filme e áudio usam caminhos relativos. Quadros intermediários, backups e diagnósticos ficam fora do Git.
