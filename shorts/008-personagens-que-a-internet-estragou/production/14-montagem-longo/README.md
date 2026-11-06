# Personagens que a internet estragou — montagem do longo

Continuação da edição enviada pelo usuário em 6 de novembro de 2026. O pacote trouxe `longvideo.mp4` e o projeto Filmora `longvideo 1.wfp`. A edição recebida termina após a 2B, aos 4:52,483. A montagem preserva esse trecho e segue com Tracer, D.Va, Mercy, Lara Croft, Peach, Sonic e o encerramento aprovado.

- [Vídeo completo 16:9](output/Personagens_que_a_internet_ESTRAGOU_Completo_16x9.mp4).
- [Somente a continuação para importar no Filmora](output/Continuacao_Tracer_ao_Encerramento_16x9.mp4).
- [Capítulos para a descrição do YouTube](capitulos_youtube.txt).
- [Referência de estilo e limites](estilo_referencia.json).
- [Montagem e dados técnicos](montagem.json).
- [Verificação da exportação](verificacao.json).

## Continuidade com a referência

As seis apresentações novas mantêm os 4,133 segundos das vinhetas recebidas: retrato central, nome amarelo em itálico, fundo escuro e indicadores de fita. O som das vinhetas vem da própria edição. Os reenquadramentos pontuais acompanham as reações e piadas, sem acrescentar novos cortes às animações. Os memes e as situações de cada bloco já estão nos masters aprovados.

O `.wfp` contém referências a músicas e efeitos instalados no computador do usuário, sem incorporar esses arquivos. Os efeitos proprietários de título/VHS do Filmora são aproximados nas novas cartelas. As trilhas de apoio foram extraídas do componente estéreo lateral de dois trechos do MP4 recebido, que remove a voz central. Esse procedimento retém parte da instrumentação e não equivale aos stems musicais completos; a extração é recentralizada para funcionar também em reprodução mono. A gravação de cada bloco novo entra inteira, no tom e velocidade originais, com trilha discreta por baixo.

O vídeo recebido fica em `assets/Edicao_usuario_ate_2B.mp4`, e o projeto Filmora original em `assets/Referencia_Filmora_original.wfp`. Não foram alterados. Não há um novo projeto Filmora nativo: para seguir editando no projeto original, importe `Continuacao_Tracer_ao_Encerramento_16x9.mp4` e coloque-o imediatamente após o final da timeline, em 4:52,483. Essa continuação é um vídeo composto, como qualquer MP4 importado.

## Exportação e reprodução

Saída horizontal 1920×1080 a 60 fps, com repetição dos quadros originais de animação a 24 fps, sem interpolação. Os reenquadramentos do corpo usam 640×360 e ampliação por vizinho mais próximo. As vinhetas usam sua própria aparência de fita; não aplicam desfoque ao Dery.

Os pacotes H.264 do trecho editado pelo usuário são copiados para o vídeo completo sem recodificação de imagem. O áudio é reunido em uma sequência contínua e codificado uma vez em AAC para evitar acúmulo de atraso nas junções. Os masters anteriores, projetos Blender, texturas e shorts 9:16 ficam preservados.

Para refazer, execute `python montar.py` com FFmpeg, FFprobe, Pillow e NumPy. Os corpos já exportados em `renders/` são reaproveitados se válidos. Ao mudar os reenquadramentos ou a mistura, remova apenas o intermediário correspondente antes de refazer. Intermediários não são versionados. A origem do pacote é o Drive `1AyEhvIPAr8xLV-faK39wtdA9NVkE4XDJ`; hashes, tempos e verificações ficam nos JSONs desta pasta.
