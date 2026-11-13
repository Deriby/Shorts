# 08 — Night Trap

Oitavo capítulo de “Jogos que a internet tentou cancelar”, com a gravação inteira enviada pelo usuário.

- [Short 9:16](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/08-night-trap/output/Night_Trap_Cancelar_9x16.mp4).
- [Capítulo 16:9](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/08-night-trap/output/Night_Trap_Cancelar_16x9.mp4).
- [Filmora 9:16 com mídias](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/08-night-trap/output/Night_Trap_Filmora.zip).
- [Blender](output/Dery_Night_Trap.blend), [roteiro](roteiro_animacao.md) e [fontes](recebimento.json).
- [Prévia vertical](output/Previa_Cenas_9x16.jpg) e [horizontal](output/Previa_Cenas_16x9.jpg).

43,3 s, 1299 quadros/30 fps, voz integral de 43,038 s. Dery original sentado, mãos com apoio nas coxas, dois planos com jogo no PC e nenhuma cena em pé ou set extra. Os gestos e reações seguem esta gravação, sem ciclo contínuo de braços. PNGs de fala e caretas trocam diretamente; o PSX fica na animação. Mídias e conteúdo do CRT permanecem limpos. Sem legendas novas.

Os inserts preservam o quadro 4:3 e a interface do jogo nos dois formatos. A arte/capa enviada ilustra o título; não são criadas imagens de audiências políticas ou de lojas recolhendo produtos. A reedição com classificação Mature não é apresentada como embalagem histórica de 1992.

Pacote recebido pelo Drive `1SdzwnXLG0rNUFBG1syNUvcFNGZIa79sT`. Voz WAV original, dois vídeos e cinco imagens estão em `assets/`, com nomes/hashes e seleção em `recebimento.json`.

Extraia o ZIP inteiro antes de abrir o WFP. Mantenha `midias/` ao lado do projeto. A base de vídeo é silenciosa; voz, trilha e efeitos têm faixas separadas. Há somente WFP 9:16; o projeto 16:9 do longo fica para o final. **Filmora não foi executado no Linux**: checagens de estrutura/recursos são distintas da abertura nativa.

## Reprodução

`preparar.py` decodifica/preserva a voz e organiza o filme editável do monitor; `prepare_edit.py` faz a mixagem. Execute `build_short.py` no Blender, seguido de `render_frames.py -- 0 2` e `-- 1 2` em dois processos. `../shared_media/project_screen.py` exporta o CRT; `../shared_media/compose_clean.py .` compõe os formatos. Execute `ajustar_inserts_16x9.py` para preservar a interface 4:3 também no horizontal. Termine com `make_filmora.py` e `verify_export.py`.

Cache ignorado em `/workspace/attachments/night_trap/`. O Blender incorpora texturas; seu vídeo editável externo está em `assets/monitor/monitor_completo.mp4`. A fonte aprovada de atuação permanece intacta.

## Conferência

MP4s/base com 1299 quadros a 30 fps e decodificação completa; voz PCM inteira e idêntica no pacote. Correlação do áudio exportado: 0.999843. Movimento do CRT confirmado; capa limpa com 39.13 dB de PSNR e gameplay com quadro inteiro com 42.64 dB. WFP com 14 clipes, zero títulos, arquivos presentes, velocidade 1× e sem lacunas; ZIP íntegro. Filmora nativo não foi executado. Ver [validacao.json](output/validacao.json).
