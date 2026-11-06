# Personagens que a internet estragou — plano de animação e montagem

Planejamento autorizado pelo usuário para os **12 personagens**. Esta entrega contém roteiros e organização de produção. Na etapa de planejamento, não foram criados cenários, imagens, vozes ou renders. As produções da Ankha, do Vaporeon, da 2B, da Tracer e da D.Va foram autorizadas depois e estão concluídas; quatro blocos ainda aguardam seus pacotes. Os três vídeos anteriormente aprovados continuam preservados.

## Ordem, cena principal e roteiro de cada bloco

| Ordem | Personagem | Cena fora do quarto / gag | Situação e roteiro |
| --- | --- | --- | --- |
| 01 | Lady Dimitrescu | Entrada do castelo, sombra alta e currículo com atividade censurada. | Produzido; [roteiro](roteiros/01-lady-dimitrescu/animacao.md), [produção](production/01-lady-dimitrescu/README.md). |
| 02 | Tifa | Reunião interrompida; remover o participante não impede os compartilhamentos. | Produzido; [roteiro](roteiros/02-tifa/animacao.md), [produção](production/02-tifa/README.md). |
| 03 | Chun-Li | Câmera de pedestal e balcão de fiscalização de skin. | Produzido; [roteiro](roteiros/03-chun-li/animacao.md), [produção](production/03-chun-li/README.md). |
| 04 | Ankha | Museu com duas peças: personagem e música; dupla associação e perdão final. | Produzido; [roteiro](roteiros/04-ankha/animacao.md), [produção](production/04-ankha/README.md). |
| 05 | Vaporeon | Mesa de redação soterrada por folhas e memes de contexto; segue o fechamento da voz recebida. | Produzido; [roteiro](roteiros/05-vaporeon/animacao.md), [produção](production/05-vaporeon/README.md). |
| 06 | 2B | Estação de treinamento: preparada para máquinas, sem treinamento para a internet. | Produzido; [roteiro](roteiros/06-2b/animacao.md), [produção](production/06-2b/README.md). |
| 07 | Tracer | Entrevista entre dois Derys: reconhecer a personagem não prova que jogou. | Produzido; [roteiro](roteiros/07-tracer/animacao.md), [produção](production/07-tracer/README.md). |
| 08 | D.Va | Simulador de cockpit cujos painéis saem da frente em “o robô tá atrapalhando”. | Produzido; [roteiro](roteiros/08-dva/animacao.md), [produção](production/08-dva/README.md). |
| 09 | Mercy | Pequena sala de triagem; pedido de “misericórdia” termina indeferido. | Planejado; [roteiro](roteiros/09-mercy/animacao.md). |
| 10 | Lara Croft | Terminal de códigos dentro de ruínas; o tesouro fica esquecido ao lado do PC. | Planejado; [roteiro](roteiros/10-lara-croft/animacao.md). |
| 11 | Peach | Vitrine de coroas e retratos: transformação oficial separada da invenção dos fãs. | Planejado; [roteiro](roteiros/11-peach/animacao.md). |
| 12 | Sonic | Arquivo do fandom que vira um pequeno arcade de terror com Sonic.exe. | Planejado; [roteiro](roteiros/12-sonic/animacao.md). |

Nos três blocos já produzidos, os projetos e as timelines registram a execução final e prevalecem sobre detalhes de um plano escrito antes da gravação. Não refazer esses vídeos para igualar descrições antigas.

Os roteiros novos acompanham a última versão de cada `narracao.md`. Nenhuma fala foi reescrita para acomodar uma gag. As marcações entre colchetes orientam a atuação; os cortes e sua duração só serão fixados após ouvir o áudio recebido. A narração final gravada prevalece sobre o texto de referência. Vergil e Chris Redfield continuam fora deste vídeo.

## Linguagem comum

O quarto gamer é o ponto de partida e retorno. O monitor exibe o trecho pertinente à frase; a montagem alterna tela, gameplay direta, rosto e plano de atuação. A imagem da personagem precisa ser reconhecível antes de começar a brincadeira. Os cortes mudam com a intenção da fala, o gesto, uma revelação ou um impacto real do jogo, em vez de seguir um intervalo fixo.

Cada bloco tem uma virada visual própria. A cena fora do quarto entra no trecho que a justifica e utiliza poucos objetos. Priorizar gameplay para mostrar personagens, lutas, habilidades e transformações; os cenários autorais sustentam as piadas do Dery. As referências a material adulto usam interfaces ilustrativas e miniaturas inteiramente cobertas, com a reação do apresentador como foco. Imagens normais dos jogos permanecem normais. Textos como placas, verbetes, fichas e nomes de arquivos pertencem à cena; não são legendas da narração.

O figurino continua sendo a camiseta preta com M amarelo, com pele e mangas corrigidas. Preservar o corpo original e as 31 expressões PNG. A boca e a emoção acompanham a interpretação: sorriso na risada, repouso nas pausas, troca seca entre desenhos. Os braços têm preparação, gesto, sustentação e retorno; alternar o lado que conduz e deixar intervalos de repouso. A referência pessoal de gestos continua privada.

O rig já suporta palmas, punhos, braços, cabeça e tronco. Cliques, marcas e carimbos são resolvidos pela interface e pela montagem. Cartas, livros e fichas ficam em apoios; a atuação não depende de agarrar objetos pequenos, agarrar partes da roupa ou tocar o rosto. Usar a pose sentada validada e, quando necessário, a pose em pé já usada no castelo, com pés apoiados e movimentos de tronco. Evitar criar caminhadas ou simulações para uma piada curta.

## Preservação do visual PS1

Reutilizar o visual aprovado na Lady, Tifa e Chun-Li: baixa resolução nítida, texturas pequenas com Closest, geometria facetada, paleta reduzida, dithering fixo e tremido das bordas em movimento. A precisão de vértices deve passar por `assets/personagens/dery/ps1_precision.py`, que mantém vértices coincidentes juntos e protege o rosto. Não trocar essa aparência por desfoque, glitch, aberração cromática ou luz piscando.

Verificar o rosto nas trocas de expressão e nas viradas, a estabilidade da cadeira e dos pés, e o alcance dos braços antes de renderizar o bloco completo. Os novos objetos seguem a mesma linguagem visual; não alterar a geometria do Dery para caber no cenário.

## Duas composições, uma gravação

**9:16:** concentrar o quadro em uma ação legível. Separar rosto, conteúdo de tela e objeto de gag em cortes próprios quando não couberem juntos. Acompanhar a personagem nos recortes de gameplay. Fichas, placas e pares de retratos podem precisar de uma disposição vertical própria.

**16:9:** usar a largura para situar Dery, cenário e monitor, e para os planos com dois Derys. O rosto continua importante: combinar planos de localização com aproximações, em vez de deixar o apresentador pequeno durante a piada. Manter os vídeos de jogo na proporção adequada.

As duas versões usam a mesma voz e a mesma sequência de ideias, com câmeras e composição de mídia próprias. O 9:16 não é apenas um corte automático do master horizontal.

## Montagem do vídeo longo

1. Reaproveitar os masters horizontais de Lady, Tifa, Chun-Li, Ankha, Vaporeon, 2B, Tracer e D.Va. Somados, eles têm **304,833 segundos**; os três primeiros já foram aprovados pelo usuário. Isso não determina a duração dos outros quatro blocos.
2. Começar pelo gancho já gravado da Lady. O título geral pode aparecer no monitor ou numa identificação gráfica curta; não há uma nova abertura falada autorizada nesta etapa.
3. Nas passagens de personagem, aproveitar a pausa natural da voz e um corte para o novo conteúdo no monitor. Preservar as piadas e as falas completas. Remover apenas sobra silenciosa de exportação quando isso ajudar a ligação e não cortar a sustentação de uma reação.
4. Manter Tracer, D.Va e Mercy juntas. “Como já tínhamos dito aqui” da D.Va remete à Tracer, e “fechar o combo” da Mercy encerra esse grupo. Diferenciar seus três ambientes: entrevista, cockpit e triagem.
5. Fechar o conteúdo em Sonic.exe, conforme a nova fala do usuário. A antiga história de Sonic Feio não entra. Depois da voz, um retorno visual curto à marca pode usar o material existente; o arquivo de encerramento precisa ser conferido na etapa de montagem, sem depender de um render novo agora.
6. Ajustar a duração à soma das gravações e às pausas necessárias. Este plano não promete dez minutos nem acrescenta falas para alcançar uma duração.

Nos shorts, o primeiro plano já identifica a personagem ou o assunto. As referências ao vídeo maior permanecem conforme a voz do usuário, com apoio visual suficiente para o espectador entender. Não adicionar despedidas, chamadas de inscrição ou falas extras aos doze textos.

## Reaproveitamento e preparação de produção

| Base existente | Uso planejado | Elementos adicionais por bloco |
| --- | --- | --- |
| Quarto e atuação em `production/03-chun-li/` e `production/02-tifa/` | Continuidade do apresentador, câmeras, faces, roupa e monitor. | Conteúdo de tela e gestos específicos de cada gravação. |
| `assets/cenarios/entrada_castelo/` | Museu da Ankha, ruínas da Lara e vitrine real da Peach. | Pedestais, cassete, placa, coroa genérica e suportes para retratos. |
| `assets/cenarios/sala_reuniao/` | Redação do Vaporeon, entrevista da Tracer e triagem da Mercy. | Folhas, dois lugares de entrevista, biombo e gráficos próprios. |
| `assets/cenarios/garagem_driver/` | Treinamento da 2B, cockpit da D.Va e arcade do Sonic. | Terminal de treino, dois painéis de cabine e frente de fliperama. |

Usar apenas a parte visível de cada cenário. As fichas, janelas, selos e retratos são candidatos a composição 2D sobre superfícies simples. Não construir modelos novos de todos os personagens, um MEKA completo, uma cidade, uma batalha ou figurantes para estes planos.

Quando chegar o link de cada pacote: inventariar e inspecionar arquivos, medir a voz, selecionar trechos, fechar os cortes por frase, preparar o vídeo contínuo do monitor e conferir um pequeno conjunto de poses nos dois formatos. Guardar origem, intervalos e hashes dos materiais usados. O pacote original fica fora do Git; voz, recortes usados, scripts, projetos e finais entram na pasta do bloco.

O [museu genérico](../../assets/cenarios/museu/) também está disponível após a produção da Ankha, com moldura e suportes sem imagens do episódio. A [mesa de redação](../../assets/cenarios/mesa_redacao/) também foi extraída após a produção do Vaporeon, sem personagem ou mídias do pacote. A [estação de treinamento](../../assets/cenarios/estacao_treinamento/) também está disponível após a 2B, com terminal neutro. O [set de entrevista](../../assets/cenarios/set_entrevista/) também foi extraído após a Tracer, sem atores e com a superfície de referência neutra. O [cockpit](../../assets/cenarios/cockpit/) está disponível após a D.Va, com banco e grupos de painéis móveis, sem avatar ou mídia do pacote.

Na renderização, aplicar o processamento já usado na Chun-Li: ocultar o cenário fora da câmera, renderizar apenas planos 3D, compor os demais diretamente e permitir retomada de quadros completos. Neste ambiente, a configuração estável observada foi um formato por vez com dois threads; reavaliar somente se a execução justificar. Não prometer um tempo fixo antes de medir a gravação e o material.

## Conferência antes de entregar cada produção futura

- Voz completa, na velocidade e altura originais, e cortes sincronizados à gravação real.
- Expressões corretas nos sorrisos, falas e pausas; rosto sem fissuras; roupa e proporções preservadas; mãos e apoio coerentes.
- Conteúdo do monitor claro, no trecho correto e em movimento quando for vídeo.
- Gag e identificação legíveis em 9:16 e 16:9, sem perder a personagem ou o resultado de uma ação no recorte.
- Arquivos finais reproduzindo integralmente, fontes registradas e envio ao GitHub confirmado.
