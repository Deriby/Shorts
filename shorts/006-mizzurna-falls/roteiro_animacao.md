# Esse jogo destruiu seu criador — planejamento de animação

Planejamento preliminar para **9:16**, com Dery no quarto gamer PS1 e cortes do trailer enviado. A história sobre o criador ainda depende da referência narrativa; as cenas 1 e 8 são reservas. Somente roteiro nesta etapa.

## Estrutura

| Cena / tempo de montagem estimado | Fala ou função | Imagem, atuação e expressão | Material disponível |
| --- | --- | --- | --- |
| 1 · 0–5 s | Gancho factual sobre o criador, pendente da referência. | Close do Dery olhando para a câmera; antecipar com olhar e uma pequena inclinação do tronco. A expressão final será definida pelo fato real. Evitar encenar sofrimento ou retratar o criador antes de conhecer a história. | Quarto reutilizado. O monitor reproduz a paisagem nevada, aproximadamente 4–12 s do trailer. |
| 2 · 5–10 s | “Esse é Mizzurna Falls. Um mundo aberto no PlayStation UM. Em 1998!” | Começar no título do jogo dentro do monitor. Cortar para o Dery na surpresa de “UM”; um gesto aberto à altura do peito acompanha a data. Rostos 26 impressionado → 12 explicando. | Paisagem e título, aproximadamente 4–12 s. |
| 3 · 10–18 s | “Você tem sete dias pra investigar o desaparecimento de uma garota numa cidade pequena.” | Corte para a sequência de conversa com policiais e depois para o exterior da cidade. No quarto, o Dery marca o prazo com um gesto curto. O trailer ilustra a investigação; não tratar qualquer personagem feminina mostrada como a garota desaparecida sem identificar. | Policiais à mesa, aproximadamente 19–24 s; exterior da igreja, 36–40 s. |
| 4 · 18–27 s | “Só que os moradores seguem a própria rotina. Eles mudam de lugar, e os acontecimentos não esperam você chegar.” | Alternar comércio → conversa externa → igreja. Depois, breve plano do Dery acompanhando o monitor e retornando o olhar à câmera. Gestos à altura do peito, sem agitar os dois braços continuamente. Rostos 20 pensativo → 12 explicando. | Comércio, aproximadamente 24–27 s; interações externas, 31–36 s; interiores, 40–45 s. O trailer mostra ambientes e interações, não uma comparação de horários do mesmo NPC. |
| 5 · 27–31 s | “Perdeu a hora? Pode perder uma pista também.” | Voltar ao quarto. O Dery olha para um relógio simples ao lado do monitor, estende a mão como se fosse interromper e percebe que chegou tarde. Rosto 5 susto → 6 sem reação. O relógio é uma ilustração da explicação, não uma reprodução de interface do jogo. | Cenário reutilizado; acrescentar somente um objeto pequeno, se necessário na produção. |
| 6 · 31–36 s | “Até o NPC tem agenda. Eu esqueço até consulta.” | Close. Ele aponta para o monitor em “NPC”, aponta para si em “eu” e baixa a mão. Troca seca 13 orgulhoso → 18 constrangido → 6 sem reação. Segurar a encarada por 0,2–0,3 s. A piada vem da comparação com a rotina, sem gag aleatória. | Dery e quarto. O trailer continua em movimento no PC. |
| 7 · 36–44 s | “Tudo isso num console da época do primeiro Crash. A ideia era fazer uma cidade que continuasse vivendo enquanto você investigava.” | Plano médio com uma pequena abertura de braços para a escala da ideia. Cortes de cidade, igreja e cachoeira. Manter variedade por enquadramento e demonstração, não por novos cenários 3D. Rostos 26 impressionado → 12 explicando. | Exterior, aproximadamente 36–40 s; igreja, 40–45 s; cachoeira, 45–50 s. |
| 8 · 44–58 s | História real sobre o criador e piada final, pendentes. | Reservar uma tomada do Dery e uma imagem documental pertinente, quando a fonte chegar. Não usar o personagem preso ou o incêndio do trailer como se fossem provas sobre a vida do autor. A reação do Dery deve acompanhar a informação confirmada. | As tomadas do jogo podem continuar no monitor; imagem biográfica e fecho ainda não selecionados. |

Tempos de montagem são estimativas e serão refeitos a partir da voz. As faixas de fonte foram mapeadas por amostragem; conferir os pontos de corte precisos na montagem. Se for usada a outro de 4 segundos, incluí-la no limite de duração após fechar as falas; esta etapa não determina sua inclusão.

## Enquadramento e montagem

- Alternar plano médio do Dery, close de reação, detalhe do monitor e cortes diretos do jogo. Câmera fixa dentro das tomadas; cortes motivados pelas palavras e reações.
- O trailer é 16:9. Para conversas, priorizar os rostos no recorte; quando dois personagens não couberem, mostrar o quadro completo dentro do monitor enquadrado de frente. Evitar cortar um interlocutor sem motivo.
- A cartela MIZZURNA FALLS precisa ser mostrada completa. No trecho da cidade, preservar arquitetura e contexto, em vez de ampliar até a imagem ficar ilegível.
- Abrir os cortes já na ação. Não usar a cartela HUMAN PRESENTS como introdução longa.
- Deixar espaço para as legendas que o usuário colocará na edição. Sem legendas de narração embutidas, sem geração de voz nesta etapa.
- Gameplay em movimento e monitor com exposição legível; preservar os acertos do episódio 005.

## Correção do rosto solicitada

Os riscos/rachaduras pretos reapareceram na animação. **Corrigir antes de renderizar o próximo short.** Nesta etapa a falha foi registrada, não corrigida.

Inspecionar em close a região dos olhos, boca e queixo durante as trocas de PNG e os movimentos da cabeça. Conferir UVs, bordas do atlas e amostragem, assim como a deformação de precisão PS1: vértices duplicados em costuras podem se separar se receberem deslocamentos diferentes. A origem exata ainda precisa de diagnóstico.

O resultado deve manter as expressões desenhadas em cortes secos, o encaixe de olhos aprovado e pixels definidos. Preservar o efeito PS1 no contorno sem produzir fissuras no interior do rosto. Validar alguns quadros de close e de virada de cabeça antes do render completo.

## Economia de produção

Reutilizar personagem, rig, quarto, iluminação e biblioteca de 31 expressões. Renderizar somente as tomadas em que o quarto ou o Dery aparecem; montar os cortes diretos do trailer separadamente. Não reconstruir a cidade de Mizzurna Falls em 3D para ilustrar o jogo. Não iniciar produção antes de fechar os dois blocos sobre o criador e receber a voz.
