# Jogos que a internet tentou cancelar — completo 16:9

**9min21,367s**, 1920×1080, 30 fps. Intro + 11 jogos + 11 vinhetas de 2s + outro. O jogo 10 permanece fora.

- [Projeto Filmora completo com mídias — ZIP, 324 MB](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/14-video-completo/output/Jogos_Que_A_Internet_Tentou_Cancelar_Filmora_COMPLETO_16x9.zip).
- [MP4 completo para conferência](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/14-video-completo/output/Jogos_Que_A_Internet_Tentou_Cancelar_COMPLETO_16x9.mp4).
- [Prévia das onze vinhetas — 22 segundos](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/14-video-completo/output/Previa_Vinhetas_16x9.mp4).
- [Visão geral da montagem](output/Previa_Montagem_Completa.jpg).
- [Capítulos](output/Filmora/CAPITULOS.txt), [plano](montagem.json) e [conferência](output/validacao.json).

As cenas aprovadas foram reaproveitadas sem renderizar o 3D novamente. O projeto usa as bases 16:9 com enquadramentos/zooms já aprovados e cortes separados; as transformações nativas são neutras, sem duplicar o zoom. Voz, música e sons têm faixas próprias. Não há legendas novas nas falas.

As vinhetas usam M amarelo, letras douradas com volume, imagem do jogo/capa e o som curto da referência do usuário. Fundo, imagem, título PNG e som ficam em camadas separadas. Glow nativo somente no título; o MP4 é uma aproximação desse efeito. Os PNGs podem ser substituídos para mudar as palavras.

Extraia o ZIP inteiro antes de abrir o WFP e mantenha `midias/` ao lado dele. Foram conferidos os 13 áudios de voz completos, todos os recursos relativos, velocidade 1×, continuidade, amostras de quadros idênticas aos masters anteriores, áudio exportado (correlação 0.999871), decodificação integral e ZIP. **Filmora não foi aberto neste ambiente**; a validação estrutural não equivale à abertura nativa.

As produções/fontes originais permanecem intactas. Ordem: GTA San Andreas, BMX XXX, Bully, Left 4 Dead 2, Saints Row IV, GTA V, Pokémon Sword and Shield, Night Trap, Dead or Alive Xtreme 3, Minecraft, House Party.

Reprodução no ambiente: `preparar.py`, `montar_projeto.py`, `exportar_previa.py`, `verificar.py`, `empacotar.py`. Cache em `/workspace/attachments/longo009/`. O som de vinheta original pode exigir `git lfs pull` para obter o WAV.
