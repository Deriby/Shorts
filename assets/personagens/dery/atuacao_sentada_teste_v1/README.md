# Teste — atuação sentada do Dery

[Assistir ao teste de 8 segundos](https://github.com/Deriby/Shorts/raw/refs/heads/main/assets/personagens/dery/atuacao_sentada_teste_v1/output/Teste_Atuacao_Sentada_8s_9x16.mp4) · [Quadros](output/Quadros_Atuacao.jpg) · [Blender](output/Dery_Atuacao_Sentada_Teste.blend)

Estudo solicitado após o usuário rejeitar a naturalidade dos gestos e as vinhetas de apresentador em pé. **Somente este teste foi produzido. A avaliação estética ainda depende do usuário.** Os shorts entregues permanecem preservados.

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

A cadeira foi ajustada **apenas nesta cópia**: substituição das partes baixas/largas dos apoios por apoios que atendem à nova pose. A malha, UVs, pesos e estrutura dos ossos do Dery não foram alterados. A pose das pernas permanece fixa, preservando o encaixe no assento. Há conferência do contato na pele avaliada, não só da posição dos controles dos punhos.

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
