# Bully — Jogos que a internet tentou cancelar

Terceiro capítulo, a partir da voz, gameplay e imagens do pacote enviado pelo usuário. [Roteiro da animação](roteiro_animacao.md) e [fontes](fontes.md). A gravação original inteira, de 46,703 s, foi preservada; entrega de 47,033 s com pequeno respiro final.

## Entregas

- `output/Bully_Cancelar_9x16.mp4`: short 1080×1920/30 fps.
- `output/Bully_Cancelar_16x9.mp4`: capítulo 1920×1080/30 fps para a futura montagem.
- `output/Bully_Filmora.zip`: **um WFP 9:16 e todas as suas mídias**. Extraia o ZIP inteiro antes de abrir.
- `output/Filmora/Bully_9x16.wfp`: arquivo avulso; requer `midias/` do pacote.
- `output/Dery_Bully.blend`: animação 3D editável, com texturas incorporadas. O CRT usa `../assets/monitor/monitor_completo.mp4`; preserve a estrutura da produção ao editar a cena.
- `output/Previa_Cenas_9x16.jpg` e `output/Previa_Cenas_16x9.jpg`: contatos de quadros finais.

**Sem legendas nem títulos/callouts sobrepostos**, tanto no MP4 quanto no WFP. O usuário faz a legendagem depois. Textos que já estão nas fotos/memes e o nome na caixa física da vinheta são parte das próprias fontes/cena.

Somente o projeto Filmora vertical é montado agora. O WFP do longo reunirá todos os jogos ao final; a montagem do longo e outro capítulo não foram iniciados.

## Atuação, cenário e edição

Mantém o Dery original, camiseta/M, proporções, rig, UVs e correção das junções do rosto. Reaproveita o quarto e a projeção PSX da revisão R2 do GTA, adaptando gestos à voz atual. Os canais do rosto usam 46 IDs, com trocas secas diretamente no material; boca orientada por energia/espectro do áudio a 15 Hz e corpo a 30 fps. Não é um alinhamento fonético manual.

O balcão, a estante e os livros OFFICE criam a audiência. Martelo e controle apoiam a piada do juiz, sem ligação frágil entre a mão e o objeto. Uma bandeira esquemática e uma grade sobre o jogo representam o veto comercial brasileiro; não simulam uma decisão judicial oficial ou a prisão de jogadores. O armário também vem do banco. O uso e os avisos dos ativos estão registrados nas fontes.

PSX: UV afim por triângulo, grade de projeção 320×180, Closest, peso mais suave no centro do rosto, RGB555/dithering fixo e ampliação Nearest. Sem borrão, glitch ou oscilação artificial da tela. O palco gráfico sem avatar tem poses a 10 Hz; planos com Dery são renderizados a 30 fps.

O WFP tem cortes, zooms por cena, voz integral e trilha/SFX em faixas separadas, com velocidade 1× explícita e durações de fonte coerentes. A base é silenciosa; atuação e inserts já estão nela. Alterações de atuação são feitas no Blender. A referência é a edição final do usuário na produção 20, respeitando a preferência posterior de não incluir legendas/títulos.

**Filmora não foi executado no Linux.** Os projetos passam por verificação estrutural; abertura e reprodução nativas precisam ser conferidas na instalação do usuário. Os MP4s são composições exportadas neste ambiente, não exports do renderizador proprietário do Filmora.

## Reprodução

1. `python prepare_assets.py` e `python prepare_edit.py` selecionam/normalizam mídia, preservam o PCM completo e montam o áudio.
2. `python prepare_crt_cache.py` decodifica uma vez o filme selecionado do CRT em PNGs temporários, com hash da origem. O Blender editável mantém o filme; o render usa o cache para evitar buscas H.264 por frame. Os PNGs não vão para o Git nem para o pacote Filmora.
3. `blender -b -t 2 --python build_short.py` monta uma cópia da base GTA R2, preservando o arquivo original. `verify_animation.py` confere seletores reais, chaves Constant, grade/UV afim e imagens de controle de rosto com câmera/pose fixas.
4. Rode `blender -b -t 2 --python render_frames.py -- 0 2` e `-- 1 2` em dois processos. `python finish_graphic_frames.py` completa as poses sustentadas do palco gráfico. O renderer permite um terceiro argumento opcional de limite de frames para conferir o cache antes do lote.
5. `python export_short.py` e `python export_short.py --wide` exportam as duas versões. Somente a vertical produz a base silenciosa para o WFP; a horizontal exporta diretamente o capítulo final.
6. `python make_filmora.py` monta apenas o WFP vertical e seu pacote; `python verify_export.py` confere MP4s, PCM integral, recursos, velocidade/duração dos clipes, ausência de títulos e integridade do ZIP.

Dependências já utilizadas: Blender 4.3, ffmpeg, NumPy e Pillow. Os caminhos do cache constam em `timeline.json`. `construcao.json`, `validacao_animacao.json`, `filmora.json` e `validacao.json` documentam as verificações. Renders intermediários, ASR e ZIP original ficam fora do Git.
