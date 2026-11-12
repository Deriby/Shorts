# Bully — animação sobre a voz enviada

**Série:** Jogos que a internet tentou cancelar. A gravação original completa, de 46,703 s, define o ritmo. A entrega tem 47,033 s com respiro final. Sem outra voz, cortes de palavras, aceleração ou alteração de tom. Os trechos abaixo resumem a ideia da fala para orientar a cena.

| Tempo | Ideia da narração | Ação e montagem |
|---|---|---|
| 0–2,90 s | Jimmy Hopkins | Gameplay do personagem andando no pátio, no CRT do quarto. Já começa em movimento. |
| 2,90–7,00 s | Um adolescente tentando sobreviver à escola | Dery apresenta o caso sentado. Gestos de apresentação e complemento com tempos diferentes entre os braços; boca em texturas PNG. |
| 7,00–12,90 s | O jogo na escola e os protestos | Gameplay dos valentões e do pátio. A ação se mantém por uma frase completa. |
| 12,90–14,00 s | Protestos | Meme enviado sobre a acusação e o que acontece no jogo, como breve pontuação. Mantém o texto original do meme. |
| 14,00–19,97 s | Jack Thompson tenta impedir a venda na Flórida | Retrato enviado do advogado, com aproximação suave. Dá tempo de identificar quem é, sem montar cortes aleatórios a cada palavra. |
| 19,97–23,80 s | Demonstração diante de um juiz | Vinheta de audiência: Dery atrás do balcão, livros do banco ao fundo e um martelo de madeira sobre a mesa. Ele apresenta e avalia a situação. A cena é uma encenação cômica, sem representar a aparência do juiz real. |
| 23,80–26,97 s | O juiz assiste e não impede a venda | Gameplay comum do pátio ocupa a tela, como conteúdo da demonstração citada. |
| 26,97–29,93 s | A piada do juiz gamer | Volta à mesma audiência. Um controle surge sobre o balcão; Dery olha para ele, faz um gesto de apresentação e reage com expressão cômica. As mãos não ficam presas ao controle. |
| 29,93–37,53 s | A proibição comercial no Brasil em 2008 | Vinheta gráfica 3D com cores da bandeira brasileira e uma caixa simbólica do jogo diante do armário OFFICE. Uma grade fecha a passagem durante a fala sobre o veto. Não simula um documento judicial nem a prisão de quem joga. |
| 37,53–39,17 s | “Porém, vamos concordar...” | Dery volta ao quarto e se dirige ao público com um gesto curto e cara de quem já sabe a resposta. |
| 39,17–40,60 s | A barraquinha | Foto enviada da promoção de DVDs. O texto é parte da foto original, não uma legenda adicionada. |
| 40,60–42,20 s | Compras na época | Segunda foto enviada, com a pilha de jogos, mantendo continuidade com a imagem anterior. |
| 42,20–45,10 s | Jogar tranquilamente | Gameplay do Jimmy em uma situação cotidiana e cômica na escola. |
| 45,10–47,03 s | Fecho da piada | Close no Dery: gesto pequeno com as duas mãos, reação breve e expressão final. Não acrescenta uma cena de prisão ou outra alegação jurídica à fala. |

## Direção

Usar o Dery original dos shorts: camiseta preta com M, rig, malha, UVs e encaixe facial preservados. Corpo a 30 fps, mãos em arcos assimétricos com preparação, sustentação e retorno. Tronco, pescoço e cabeça têm pequenas sobreposições; pernas e cadeira permanecem estáveis. Canais faciais com 46 IDs nesta gravação, usando energia/espectro da voz para orientar as bocas em poses a 15 Hz, com reações escolhidas por intenção. É atuação estilizada guiada pela voz, sem afirmar alinhamento fonético manual.

Manter a projeção PSX da revisão R2: UV afim por triângulo, snapping em grade 320×180, pesos mais suaves no centro do rosto, Closest e trocas secas gravadas diretamente no material. Na composição: RGB555, dithering fixo e ampliação Nearest. Sem borrão, glitch ou oscilação artificial da tela inteira.

O quarto e o tribunal usam mobiliário/livros já presentes no banco. O palco sem avatar da proibição tem poses a 10 Hz; os planos com Dery mantêm 30 fps. O CRT pode usar frames PNG decodificados uma vez no cache do render, preservando a mesma sequência e mantendo o filme externo no Blender editável.

**Sem legendas nem títulos/callouts sobrepostos.** O usuário faz a legendagem depois. Texto já existente nos memes/fotos e o nome na caixa física do jogo pertencem às próprias mídias/cena.

Entregar os dois MP4s, Blender e **somente o WFP 9:16 com suas mídias**. O projeto Filmora 16:9 reunirá todos os jogos apenas ao final.
