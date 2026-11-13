# 06 — GTA V

Sexto capítulo de “Jogos que a internet tentou cancelar”, depois de Saints Row IV.

- [Short 9:16](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/06-gta-v/output/GTA_V_Cancelar_9x16.mp4).
- [Capítulo 16:9](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/06-gta-v/output/GTA_V_Cancelar_16x9.mp4).
- [Filmora 9:16 com mídias](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/06-gta-v/output/GTA_V_Filmora.zip).
- [Blender](output/Dery_GTA_V.blend) e [roteiro da animação](roteiro_animacao.md).
- [Prévia vertical](output/Previa_Cenas_9x16.jpg) e [horizontal](output/Previa_Cenas_16x9.jpg).

37,3 segundos, 30 fps, com a voz inteira de 37,046 s. Dery sentado, mãos apoiadas nas coxas, cadeira original e gameplay no PC. Sem Dery em pé ou cenários extras. PSX restrito à animação; fotos/trailers e o conteúdo do monitor permanecem limpos. Sem legendas novas. Textos originais das mídias, quando houverem, pertencem às fontes.

Material enviado na pasta Drive `1glsyO1duK8KXN2UGLODYK3VDKXcw-LmM`: **06 - GTA 5.zip**, ID `1729QmQttyTAlFaLpzMAvlXFRPniwZHWC`. Originais preservados em `assets/`, nomes/hashes em `recebimento.json`. As fotografias identificam as redes, sem afirmar que retratam as unidades australianas da notícia. O fecho usa uma paródia de South Park, não uma afirmação de mecânica do GTA VI real. Nenhuma data de lançamento foi acrescentada à fala.

Extraia o ZIP inteiro para abrir o WFP 9:16. Voz, trilha e efeitos permanecem separados; o vídeo-base está silencioso em `midias/`. O projeto Filmora 16:9 completo fica para o final da série. **Filmora não foi executado neste Linux**; estrutura/recursos e abertura nativa são verificações distintas.

## Reprodução

1. `python preparar.py` e `python prepare_edit.py`.
2. `blender -b -t 2 --python-exit-code 1 --python build_short.py`.
3. Rode `render_frames.py -- 0 2` e `-- 1 2` em dois processos Blender.
4. Use `../shared_media/project_screen.py` com este projeto, `output/Dery_GTA_V.blend` e o cache `/workspace/attachments/gta_v`.
5. `python ../shared_media/compose_clean.py .`, `python make_filmora.py`, `python verify_export.py`.

São renderizados somente os planos sentados e um fundo por enquadramento de PC. A imagem do jogo é inserida em todos os quadros, em perspectiva normal. O Blender incorpora as texturas e usa o filme externo `assets/monitor/monitor_completo.mp4`. O modelo/rig/UVs e a cadeira aprovados não foram alterados.
