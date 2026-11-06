# Encerramento — Personagens que a internet estragou

Despedida do vídeo longo, produzida com a versão revisada e a gravação enviada pelo usuário. **16:9 em 1920×1080, 24 fps, 21,208 segundos**. A voz decodificada tem 19,958 segundos e foi preservada inteira, sem mudar velocidade, tom ou falas. A marca aparece depois da gravação completa. Nenhuma versão vertical foi gerada.

## Direção e atuação

Um plano contínuo no quarto acompanha conclusão, comentários, apoio ao canal e despedida. O arquivo dos 12 personagens vira “MISSÃO CONCLUÍDA”; depois, pastas de sugestões aparecem na fala sobre quem faltou. A interface segue para os convites COMENTAR, INSCREVER e CURTIR, e termina com o M amarelo.

O Dery alterna braços conforme a intenção de cada frase, com preparação, sustentação e retorno. No final, sorri, faz um aceno breve e dá uma piscada. Um coração gráfico amarelo aparece uma única vez. O gesto não depende de tocar o rosto, simular dedos ausentes ou criar uma pose de beijo com deformação facial.

Depois da voz, a marca ocupa a tela. São **dois planos e um corte**. A câmera do quarto faz uma aproximação suave, sem trocas repetidas de enquadramento. Não há legenda da narração, fala adicionada ou efeitos sonoros novos.

A camiseta preta com M amarelo, pele limpa, mangas e geometria do avatar foram preservadas. As 31 faces PNG mudam por corte; as antigas shape keys permanecem zeradas. A validação confere costuras, precisão PS1, alcance dos braços, apoio e continuidade da câmera. A referência pessoal de gestos permanece privada.

## Fontes e escopo

O catálogo vem da intro e o M é a logo aprovada em `assets/marca/massacote-games/logo.png`. As demais janelas são autorais. A expressão “trocentos” é ilustrada com pastas de sugestões, sem contagem estatística. A frase sobre a internet é cômica; não foram acrescentados armas ou disparos.

A versão do usuário substitui o roteiro proposto anteriormente: não entra a piada de apagar o histórico. Os botões de apoio são convites ilustrativos, sem qualquer interação real com contas ou plataformas. A intro e os 12 blocos anteriores foram preservados. Esta etapa entrega o encerramento separado, sem exportar a montagem integral do longo.

## Arquivos

- `output/Encerramento_Personagens_que_a_internet_estragou_16x9.mp4`: final horizontal.
- `output/Dery_Encerramento_Personagens_16x9.blend`: quarto, Dery, câmera, faces, monitor e áudio.
- `assets/voz/voz_original.mp3`: original recebido, preservado byte a byte. Os WAVs são a decodificação e a cópia com silêncio para a marca.
- `assets/gameplay/monitor_montado.mp4`: desenvolvimento contínuo da interface do monitor.
- `assets/memes/`: catálogo reutilizado, logo e cartão final.
- `timeline.json`, `screen_cues.json`: dois planos e ações internas da tela.
- `acting_cues.json`, `face_cues.json`: gestos, câmera e expressões.
- `source_manifest.json`: procedência, hashes e escolhas editoriais.
- `scene_validation.json`, `export_validation.json`: verificações da cena, áudio e MP4.

## Visual e reprodução

Render nativo 640×360, ampliação inteira 3× por vizinho mais próximo, precisão de geometria reduzida com proteção das costuras, texturas Closest, corpo endereçado em 128 px, paleta RGB de 5 bits e Bayer fixo 4×4. Sem blur, glitch ou luz piscando.

Na raiz do repositório, com Blender 4.3, FFmpeg, NumPy e Pillow:

```sh
python shorts/008-personagens-que-a-internet-estragou/production/13-encerramento/prepare_assets.py
blender -b -t 2 --python-exit-code 1 --python shorts/008-personagens-que-a-internet-estragou/production/13-encerramento/build_outro.py
blender -b shorts/008-personagens-que-a-internet-estragou/production/13-encerramento/output/Dery_Encerramento_Personagens_16x9.blend -t 1 --python-exit-code 1 --python shorts/008-personagens-que-a-internet-estragou/production/13-encerramento/verify_scene.py
python shorts/008-personagens-que-a-internet-estragou/production/13-encerramento/export_outro.py
python shorts/008-personagens-que-a-internet-estragou/production/13-encerramento/verify_export.py
```

`prepare_assets.py` usa as fontes existentes e os metadados da voz em `audio.json`, ou o intake local quando disponível. O cartão final é composto diretamente; o plano do quarto é renderizado em Blender, com dois threads. `--resume` retoma quadros completos e `--encode-only` codifica os existentes. Baixar a pasta inteira para editar: áudio e filme usam caminhos relativos. Quadros intermediários, backups e diagnósticos ficam fora do Git.
