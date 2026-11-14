# 09 — Dead or Alive Xtreme 3

Nono capítulo de “Jogos que a internet tentou cancelar”.

- [Assistir/baixar o short 9:16](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/09-dead-or-alive-xtreme-3/output/Dead_or_Alive_Xtreme_3_Cancelar_9x16.mp4).
- [Baixar o capítulo 16:9](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/09-dead-or-alive-xtreme-3/output/Dead_or_Alive_Xtreme_3_Cancelar_16x9.mp4).
- [Baixar o projeto Filmora 9:16 com mídias](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/09-dead-or-alive-xtreme-3/output/Dead_or_Alive_Xtreme_3_Filmora.zip).
- [Blender editável](output/Dery_Dead_or_Alive_Xtreme_3.blend), [roteiro de animação](roteiro_animacao.md) e [fontes](recebimento.json).
- [Prévia vertical](output/Previa_Cenas_9x16.jpg) e [horizontal](output/Previa_Cenas_16x9.jpg).

41,233 s, 1237 quadros a 30 fps. Voz original inteira de 40,951 s, preservada nos arquivos de origem. O pequeno respiro final não corta nem estende palavras. Não há legendas/títulos novos.

Dery original sentado, mãos com apoio nas coxas e gestos por intenção; 35 IDs faciais usados por troca seca de PNG. Há três planos do jogo rodando no PC, gameplay direta e o GIF animado do próprio jogo. O PSX fica no personagem/cenário/props; gameplay e GIF, inclusive dentro do CRT, são compostos limpos depois.

Duas ceninhas ligadas à fala:

1. **17,2–18,7 s — férias:** mala miniatura abre e revela um guarda-sol sobre a mesa.
2. **27,9–30,2 s — física:** bola de vôlei comprime uma mola de brinquedo e sai voando.

A mala reutiliza a geometria já produzida para o insert do Pokémon. Cenário, móveis, modelo, UVs e cadeira aprovados ficam intactos. Os apoios dos dois props foram medidos na malha da mesa. Nenhuma cena do Dery em pé, câmera tremendo ou glitch.

A voz trata da ausência de lançamento ocidental. Não foram criadas cenas de banimento por autoridades ou manchetes apresentadas como prova. O trailer e o GIF com pessoa real foram recebidos/preservados, mas a montagem usa os minigames e o GIF do próprio jogo.

## Filmora

Extraia o ZIP inteiro antes de abrir o WFP e mantenha `midias/` ao lado. A base é silenciosa; voz, música baixa e os dois sons das ceninhas têm faixas próprias. Os 13 planos e seus zooms ficam editáveis. Cada gag é um clipe contínuo. A animação 3D/CRT está na base renderizada; alterações no 3D são feitas no Blender.

Há somente projeto 9:16. O WFP do vídeo longo será montado ao final com todos os jogos. **Filmora não foi executado neste Linux**; verificações estruturais não substituem abertura no aplicativo.

## Conferência e reprodução

[Validação](output/validacao.json): duração/quadros/decodificação dos três vídeos, PCM completo e idêntico no pacote, fontes recebidas por hash, CRT em movimento, GIF animado, movimento das duas gags, mídia limpa, recursos/velocidade 1×/continuidade do WFP e ZIP íntegro. Correlação de áudio exportado: 0.999851. A estética continua sujeita ao retorno do usuário.

`preparar.py` preserva a voz e monta o monitor; `prepare_edit.py` prepara música/sons. Execute `build_short.py` no Blender; ele chama `criar_ceninhas.py`. Renderize com `render_frames.py -- 0 2` e `-- 1 2` em dois processos. Exporte a projeção usando `../shared_media/project_screen.py` e componha por `../shared_media/compose_clean.py .`. Termine com `make_filmora.py`, `verify_export.py` e `finalizar_registros.py`. Cache recriável em `/workspace/attachments/09-proximo/`, fora do Git.
