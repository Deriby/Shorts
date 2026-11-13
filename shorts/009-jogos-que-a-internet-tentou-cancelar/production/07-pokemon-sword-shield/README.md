# 07 — Pokémon Sword and Shield

**[Entrega atual R6 — 2 ceninhas curtas, MP4s e Filmora](output/R6_Cenas_Curtas/README.md).**

Sétimo capítulo de “Jogos que a internet tentou cancelar”.

- [Short 9:16](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/07-pokemon-sword-shield/output/Pokemon_Sword_Shield_Cancelar_9x16.mp4).
- [Capítulo 16:9](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/07-pokemon-sword-shield/output/Pokemon_Sword_Shield_Cancelar_16x9.mp4).
- [Filmora 9:16 com mídias](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/07-pokemon-sword-shield/output/Pokemon_Sword_Shield_Filmora.zip).
- [Blender](output/Dery_Pokemon_Sword_Shield.blend), [roteiro](roteiro_animacao.md) e [recebimento](recebimento.json).
- [Prévia vertical](output/Previa_Cenas_9x16.jpg) e [horizontal](output/Previa_Cenas_16x9.jpg).

46,333 s, 30 fps, com a voz inteira de 46,069 s. Dery sentado na cadeira original, mãos apoiadas nas coxas, gameplay no PC e nenhuma cena de Dery em pé ou set extra. O PSX fica no personagem/cenário; fotos, memes e o vídeo do monitor ficam limpos. Sem legendas novas. O GIF do Pikachu continua animado no fecho.

Os inserts do trailer com Pokémon nas laterais ou texto original usam o quadro inteiro no 9:16, sem cortar personagens/letras por um recorte central.

Pacote enviado: **07 - POKEMON SWORD AND SHIELD.zip**, ID `1On6aUlecONE7_w1V7-Te0T14SD9Zdu4g`, na pasta Drive habitual. Voz e fontes originais preservadas em `assets/`; nomes, hashes e a derivação do GIF estão em `recebimento.json`. A imagem de resumo da polêmica não foi apresentada como comunicado oficial ou tweet histórico. As imagens de Pokémon são ilustrativas, sem atribuir a um Pokémon visível uma exclusão que a fonte não comprova.

Extraia o ZIP inteiro e abra o WFP 9:16. Voz, trilha e efeitos ficam separados; o vídeo-base é silencioso e as mídias usadas estão em `midias/`. O projeto Filmora 16:9 completo fica para o final. **Filmora não foi executado no Linux**; validação de estrutura/recursos não equivale a abertura nativa.

## Reprodução

`preparar.py` organiza voz e filme editável do PC; `prepare_edit.py` faz a mixagem. Rode `build_short.py` no Blender, depois `render_frames.py -- 0 2` e `-- 1 2` em dois processos. `../shared_media/project_screen.py` exporta a projeção do CRT, e `../shared_media/compose_clean.py .` compõe as duas proporções. Termine com `make_filmora.py` e `verify_export.py`.

Cache fora do Git em `/workspace/attachments/pokemon_swsh/`. Os fundos do monitor podem ser reutilizados porque sua câmera é fixa, mas a mídia avança em todos os quadros. O Blender incorpora texturas; o filme externo editável está em `assets/monitor/monitor_completo.mp4`. O projeto-fonte da pose aprovada permanece intacto.

## Conferência

Dois MP4s e a base silenciosa: 1390 quadros, 30 fps, duração completa e decodificação conferidos. Voz PCM preservada e idêntica no pacote; áudio exportado com correlação de 0,9999. Movimento no CRT e no GIF confirmados. Meme limpo com 45,31 dB e insert de gameplay com quadro inteiro com 46,05 dB de PSNR. WFP com 17 clipes, zero títulos, mídias presentes, velocidade 1×, sem lacunas e ZIP íntegro. O aplicativo Filmora não foi executado. Métricas em [validacao.json](output/validacao.json).
