# 04 — Left 4 Dead 2

**[Entrega atual R6 — 2 ceninhas curtas, MP4s e Filmora](output/R6_Cenas_Curtas/README.md).**

Quarto jogo de “Jogos que a internet tentou cancelar”. Saints Row IV é o quinto.

- [Short 9:16](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/04-left-4-dead-2/output/Left_4_Dead_2_Cancelar_9x16.mp4).
- [Capítulo 16:9](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/04-left-4-dead-2/output/Left_4_Dead_2_Cancelar_16x9.mp4).
- [Filmora 9:16 com mídias](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/04-left-4-dead-2/output/Left_4_Dead_2_Filmora.zip).
- [Blender](output/Dery_Left_4_Dead_2.blend) e [roteiro da animação](roteiro_animacao.md).
- [Prévia vertical](output/Previa_Cenas_9x16.jpg) e [horizontal](output/Previa_Cenas_16x9.jpg).

41,2 s/30 fps, com a voz integral de 40,943 s. Dery original, cadeira e pose de apoio nas coxas aprovadas. Zero Dery em pé e zero sets extras. Gameplay no PC preservada. O PSX fica no personagem/cenário; fotos, memes e gameplay entram limpos depois da animação, inclusive no CRT. Sem legendas ou títulos novos. Os textos que já pertencem à gameplay/imagens enviadas permanecem nas fontes.

O áudio e as mídias foram enviados no [pacote Drive](https://drive.google.com/file/d/17DsD7EeOGo6wf5n3hm6wkIDQnUfuJvkB/view), preservados em `assets/`, com inventário em `recebimento.json`. O beta do primeiro jogo aparece somente no trecho sobre o primeiro Left 4 Dead; a sequência usa a gameplay de Left 4 Dead 2. `noticia.png`, um resumo enviado sem identificação suficiente de fonte jornalística, não foi usado como se fosse uma notícia oficial. Não foi fabricada uma reunião da Valve nem um documento de encerramento do grupo.

Extraia o ZIP inteiro e abra o WFP 9:16. Voz, trilha e efeitos ficam separados. O vídeo-base está silencioso; recursos em `midias/`. O projeto Filmora 16:9 completo fica para o final da série. **Filmora não foi executado neste Linux**; abertura e reprodução nativa são distintas das verificações de estrutura/recursos.

## Reprodução

1. `python preparar.py` e `python prepare_edit.py`.
2. `blender -b -t 2 --python-exit-code 1 --python build_short.py`.
3. Rode `render_frames.py -- 0 2` e `-- 1 2` em dois processos Blender.
4. Use `../shared_media/project_screen.py` com o projeto, `output/Dery_Left_4_Dead_2.blend` e o cache `/workspace/attachments/left4dead`.
5. `python ../shared_media/compose_clean.py .`, `python make_filmora.py`, `python verify_export.py`.

O cache dos fundos estáticos do CRT é reutilizado para economizar render; o vídeo do jogo continua avançando em cada quadro na composição final. Alterar a animação exige invalidar o cache antes de renderizar novamente. O Blender incorpora as texturas e usa `assets/monitor/monitor_completo.mp4` como filme externo editável. O projeto-fonte da pose aprovada permanece intacto.
