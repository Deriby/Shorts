# Cena curta — Dery no novo quarto

Teste autorizado para ver como o cenário fica nos shorts, separado das produções anteriores.

- [Assistir à prévia de 6 segundos, 9:16](Previa_Dery_Quarto_6s_9x16.mp4).
- [Imagem do Dery no cenário](Previa_Dery_No_Quarto.png).
- [Cena Blender editável](Dery_No_Quarto_Teste_6s.blend), com a pasta `media` ao lado para o vídeo do monitor.

Usa o **Dery original dos shorts**, camiseta preta com M e biblioteca de 31 rostos PNG. A pose sentada foi obtida das matrizes avaliadas do master anterior e convertida para a base do rig, preservando também as pernas. O assento foi medido na cadeira do banco e a cópia foi posicionada nele; os vértices originais do personagem e os arquivos-base permanecem intactos.

O teste reaproveita a abertura da voz recebida para **O verdadeiro chefe de Driver** e a gameplay enviada no mesmo episódio. Não houve geração de voz nova. A fala ocupa os primeiros 4,9167 s, com uma pequena saída de áudio e pausa para a reação final. O vídeo no monitor foi preparado a 16 fps com atualização por frame; o material é independente do M da parede.

## Ação

| Tempo | Plano |
|---|---|
| 0–1,25 s | Driver rodando no monitor CRT. |
| 1,25–3,75 s | Dery olha para a câmera e explica com gestos diferentes entre os braços. |
| 3,75–6 s | Close para a conclusão e a expressão sem reação. |

As expressões trocam com interpolação Constant, sem morph. Os gestos têm preparação, pausa e retorno, sem repetir um ciclo de braços. A câmera é um único objeto animado com cortes secos: a precisão PS1 acompanha automaticamente seus movimentos/lente, sem depender de grupos de nós órfãos por câmera.

São 96 frames reais renderizados no Blender, 270×480/16 fps, RGB555 com dithering discreto e ampliação por Nearest para 1080×1920. O MP4 sai a 24 fps, conservando a cadência original do teste. Não há legenda nem oscilação artificial da imagem inteira. Esta é uma prévia de cenário/atuação, sem aplicar os plugins proprietários da edição Filmora.

`cena.json` registra fontes, encaixe, expressões e cortes. `exportacao.json` confere duração, dimensões, frames e mudança de imagens no plano do monitor. Para reconstruir, usar `montar_cena.py`; renderizar com `renderizar_frames.py -- 0 2` e `-- 1 2` em dois processos, e então rodar `exportar_teste.py`. As mídias locais necessárias estão em `media/`.
