# Produção de shorts

- O usuário pediu que os trabalhos sejam salvos continuamente neste repositório GitHub, com uma pasta diferente para cada short.
- Use `shorts/NNN-assunto/`, mantendo o título exato informado pelo usuário no README do vídeo e no índice da raiz.
- Para novos shorts, use somente 9:16. Planeje 16:9 e adaptação para vídeo longo apenas quando o usuário avisar que deseja esse aproveitamento.
- Quando o pedido for somente de roteiros, entregue narração e planejamento de cenas; deixe a geração de voz e a renderização para a etapa solicitada pelo usuário.
- Preservar a correção dos riscos/rachaduras do rosto: usar `assets/personagens/dery/ps1_precision.py` nos próximos renders, evitando deslocamentos diferentes em vértices coincidentes. Conferir em close as trocas de expressão e a virada de cabeça, mantendo PNGs com troca seca e o visual PS1. A correção e a validação inicial estão no episódio 006.
- Mantenha modelos e outros ativos reutilizáveis em `assets/`; preserve os arquivos originais do usuário.
- Roteiro, gravação de voz e animação seguem a ordem combinada com o usuário. Ajuste os cortes à gravação real.
- Versione roteiros, scripts, voz, texturas, expressões, projeto Blender e vídeos finais. Não versione renders intermediários, backups ou ZIPs duplicados.
- Use Git LFS conforme `.gitattributes` para arquivos binários grandes.
- Faça commits das etapas concluídas e envie ao GitHub dentro da autorização do usuário. Verifique a branch remota antes de integrar mudanças; não use force push para contornar divergências.
- Informe claramente quando há commit local mas o envio remoto está bloqueado. Não declare publicação sem confirmar o push.
