# 05 — Saints Row IV — Jogos que a internet tentou cancelar

Voz completa de 40,673 s; vídeos de **41 s**, 30 fps. [Roteiro da animação](roteiro_animacao.md), [fontes](fontes.md) e [recebimento](recebimento.json).

- `output/Saints_Row_IV_Cancelar_9x16.mp4`: short 1080×1920.
- `output/Saints_Row_IV_Cancelar_16x9.mp4`: capítulo 1920×1080 para o longo futuro.
- `output/Saints_Row_IV_Filmora.zip`: um WFP 9:16 e todas as suas mídias. Extraia tudo antes de abrir.
- `output/Dery_Saints_Row_IV.blend`: animação editável, com texturas incorporadas. O filme externo do CRT está em `../assets/monitor/monitor_completo.mp4`.
- `output/Previa_Cenas_9x16.jpg`, `output/Previa_Cenas_16x9.jpg`: quadros finais.

**Sem legendas ou títulos sobrepostos novos.** O usuário legenda manualmente depois. A placa AU/fichas são objetos da cena e o texto do meme pertence à própria imagem.

## Mídias limpas e PSX na animação

Fotos, memes e gameplay são inseridos a partir das fontes originais, sem RGB555, dithering, Nearest, snapping ou UV afim. Isso também vale para a imagem dentro do CRT: camada em resolução de entrega com perspectiva normal e proporção preservada. O tratamento PSX fica nos modelos/cenários e nas cenas de animação, sem um filtro sobre a mídia.

Dery original, malha/rig/UVs/camiseta preservados. Corpo a 30 fps, bocas PNG com chaves Constant a 15 Hz e reações por intenção da fala. Mesa, estante e armário reaproveitados do banco. A inspeção com caixa/ficha RC e posterior revisão cria uma cena fora do quarto. O mapa do reboot de 2022 enviado no ZIP não foi usado como se fosse uma imagem da missão cortada de 2013.

## Projeto e validação

O WFP tem cortes, zooms, voz integral, trilha e SFX separados; a base é silenciosa. Apenas o WFP vertical é produzido agora. O projeto Filmora do longo será montado com todos os jogos ao final.

O MP4 é composto neste ambiente. **O Filmora nativo não foi executado**: estrutura, recursos, timings e integridade são verificados por código; abertura/reprodução precisam ser conferidas na instalação do usuário. Mudar a atuação exige o Blender; os inserts e a animação já estão na base.

## Reproduzir

1. `prepare_assets.py`, `prepare_edit.py`, `prepare_crt_cache.py` preparam o áudio integral e o cache temporário de render.
2. Blender: `build_short.py`, `verify_animation.py`, depois `render_frames.py -- 0 2` e `-- 1 2` em dois processos. `finish_graphic_frames.py` completa as poses sustentadas do palco sem avatar.
3. Rode o Blender com `../shared_media/project_screen.py -- <pasta-desta-produção> output/Dery_Saints_Row_IV.blend <cache>` para registrar o display. A projeção exportada acompanha o projeto em `output/projecao_monitor.json`.
4. `python ../shared_media/compose_clean.py <pasta-desta-produção>` compõe as duas versões e a base vertical. As mídias entram após o tratamento PSX da animação.
5. `make_filmora.py` cria o WFP/pacote. `verify_export.py` e `../shared_media/verify_revision.py` conferem os resultados, incluindo fidelidade da imagem às fontes limpas.

Requer Blender 4.3, ffmpeg, Pillow, NumPy e OpenCV. O caminho local do OpenCV fica em `/workspace/tools/shorts_asr`; pesos ASR, renders e caches não são versionados. `timeline.json` guarda o cache ativo. Arquivos anteriores permanecem preservados.
