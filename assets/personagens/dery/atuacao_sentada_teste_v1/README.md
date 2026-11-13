# Teste — atuação sentada do Dery

**Revisão atual: apoio real nas coxas.** [Ver o teste de 8 s](https://github.com/Deriby/Shorts/raw/refs/heads/main/assets/personagens/dery/atuacao_sentada_teste_v1/output/Teste_Apoio_Real_8s_9x16.mp4) · [Quadros](output/Quadros_Apoio_Real.jpg) · [Blender](output/Dery_Atuacao_Apoio_Real.blend)

A pose de descanso foi refeita: cada mão repousa sobre a respectiva coxa, a direita sobe para o gesto e retorna à superfície. A cadeira e os demais objetos permanecem originais. Só os braços/antebraços/mãos recebem novas curvas. O ritmo do gesto, a voz, as expressões, o corpo/cabeça, a câmera e o PSX permanecem os mesmos. Não há apoio novo nem descanso suspenso. A avaliação estética da correção continua com o usuário.

`corrigir_apoio_real.py` encontra as superfícies reais das calças pela malha avaliada e confere a pele das mãos em descanso, incluindo o retorno e a antecipação. `validacao_apoio_real.json` registra os intervalos de contato antes do snapping de tela e a preservação das curvas dos demais ossos. A pose não é calculada pela altura isolada do punho. O ápice do gesto é preservado; as transições são refeitas para conectar a nova posição de repouso.

Reprodução: `blender -b -t 2 --python corrigir_apoio_real.py`, depois `render_apoio_real.py -- 0 2` / `-- 1 2`, e `python export_apoio_real.py`. Cache em `/workspace/attachments/atuacao_sentada_v3/`.

## Histórico das correções

**Versão anterior rejeitada: cadeira original com braços ainda flutuando.** [Assistir ao teste corrigido de 8 s](https://github.com/Deriby/Shorts/raw/refs/heads/main/assets/personagens/dery/atuacao_sentada_teste_v1/output/Teste_Cadeira_Original_8s_9x16.mp4) · [Quadros](output/Quadros_Cadeira_Original.jpg) · [Blender](output/Dery_Atuacao_Cadeira_Original.blend)

O usuário gostou do estilo de movimento, mas rejeitou os apoios altos e depois esta revisão, que mantinha os braços parados no ar. A interpretação de que todas as poses estavam aprovadas foi incorreta. Esta revisão remove os seis objetos acrescentados e restaura a malha e os UVs originais da cadeira. Todos os keyframes do personagem, rosto e câmera permanecem exatamente iguais. A voz, duração e tratamento PSX são os mesmos. As mãos mantêm a posição de conversa sobre o colo; não foram reposicionadas para criar novos contatos. A revisão foi rejeitada porque não corrigia a pose de descanso.

`validacao_cadeira_original.json` registra a assinatura das curvas antes/depois e a conferência da cadeira. Scripts: `restaurar_cadeira.py`, `render_cadeira_original.py` (dois workers, `-- 0 2`/`-- 1 2`) e `export_cadeira_original.py`. Cache separado em `/workspace/attachments/atuacao_sentada_v2/`.

## Estudo anterior (apoios rejeitados)

[Assistir ao teste de 8 segundos](https://github.com/Deriby/Shorts/raw/refs/heads/main/assets/personagens/dery/atuacao_sentada_teste_v1/output/Teste_Atuacao_Sentada_8s_9x16.mp4) · [Quadros](output/Quadros_Atuacao.jpg) · [Blender](output/Dery_Atuacao_Sentada_Teste.blend)

Estudo solicitado após o usuário rejeitar a naturalidade dos gestos e as vinhetas de apresentador em pé. **Somente este teste foi produzido. O estilo de movimento agradou; as poses de apoio e a alteração da cadeira foram rejeitadas e substituídas pela revisão atual.** Os shorts entregues permanecem preservados.

## Proposta

Um único plano, câmera fixa e Dery sentado. A mão esquerda permanece apoiada. A direita prepara um gesto, acompanha a ideia da frase, sustenta, retorna e descansa. Uma pequena inclinação do tronco acompanha essa ação; depois entram olhar e expressão. Não há senoides, balanço contínuo, gestos espelhados ou ciclo de braços. Os tempos desta frase não devem virar um loop para outros episódios.

| Trecho | Atuação |
|---|---|
| 0–1,18 s | Pose de descanso; preparação curta da mão direita. |
| 1,18–2,95 s | Um gesto de explicação com trajetória curva e rotação coordenada de antebraço/mão. |
| 2,95–3,35 s | Sustentação e pequeno assentamento. |
| 3,35–4,62 s | Retorno e contato com o apoio. |
| 4,62–8 s | Mãos descansam; olhar e PNGs marcam a piada e a pausa. |

O áudio é o gancho original de Saints Row IV: **0–6,40 s**, encerrando no intervalo antes da frase seguinte. Os **1,60 s finais** são reservados à reação. A amostra PCM foi copiada integralmente, sem alterar velocidade/tom; não foi criada outra voz. Sem música, SFX ou legendas novas.

## Mudança de método

As poses foram construídas com pontos de apoio no mundo e solução geométrica de dois ossos. O braço não recebe um alvo que deriva continuamente com o ombro. A mão esquerda mantém sua posição quando o tronco acompanha o gesto; a direita retorna ao mesmo ponto. A orientação da mão usa a geometria da pele, em vez de assumir que a cauda arbitrária do osso indica a direção dos dedos. O modelo original não tem controles individuais de dedos; este teste não acrescenta articulações de dedos.

**Alteração rejeitada pelo usuário e removida na revisão atual.** Na primeira versão, a cadeira foi ajustada apenas nesta cópia: substituição das partes baixas/largas dos apoios por apoios que atendem à nova pose. A malha, UVs, pesos e estrutura dos ossos do Dery não foram alterados. A pose das pernas permanece fixa, preservando o encaixe no assento. Há conferência do contato na pele avaliada, não só da posição dos controles dos punhos.

A referência disponível são as observações já registradas em `shorts/007-verdadeiro-chefe-driver/production/gesture_reference.json`, extraídas anteriormente do vídeo pessoal fornecido pelo usuário. O arquivo privado antigo não estava acessível nesta sessão; **não houve nova análise daquele vídeo nem captura automática de movimento**. As poses e os tempos deste estudo foram dirigidos manualmente. O vídeo privado não é publicado.

## Visual e arquivos

Dery original com camiseta preta/M e PNGs de expressão em troca seca. Chaves do material são gravadas diretamente e conferidas; 17 IDs usados no teste, com formas de boca temporizadas para o gancho. PSX preservado na animação: UV afim, precisão de vértices, Closest, RGB555/dithering fixo e ampliação Nearest. Sem oscilação global da câmera ou motion blur. Não há mídia inserida neste plano.

- MP4 1080×1920, 30 fps, 240 quadros/8 s.
- Blender editável em `output/`, acompanhado do áudio em `assets/`.
- `atuacao.json`: trajetória, poses e fonte preservada.
- `validacao_pose.json`: seletores de rosto, estabilidade das pernas, mão apoiada e contato da pele.
- `validacao_export.json`: vídeo decodificado, dimensões/quadros e preservação da amostra de voz.

## Reprodução

1. Blender 4.3: `blender -b -t 2 --python-exit-code 1 --python build_test.py`.
2. `blender -b -t 2 --python-exit-code 1 --python verify_test.py`.
3. Rode `render_test.py -- 0 2` e `render_test.py -- 1 2` em dois processos.
4. `python export_test.py`.

O cache fica em `/workspace/attachments/atuacao_sentada/frames`, fora do Git. A cena-fonte do Saints Row IV é somente lida; seu hash é conferido antes/depois. Requer Blender, ffmpeg, NumPy e Pillow já usados na produção. Não há projeto Filmora novo para este estudo de atuação.
