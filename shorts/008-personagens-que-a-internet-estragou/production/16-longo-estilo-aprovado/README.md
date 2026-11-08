# Personagens que a internet estragou — estilo aprovado

O usuário aprovou a amostra corrigida da Tracer, sem a oscilação artificial da tela, e pediu o restante do vídeo nesse padrão. Esta revisão preserva sua edição recebida até a 2B e remonta Tracer, D.Va, Mercy, Lara Croft, Peach, Sonic e o encerramento.

- [Vídeo completo 16:9](output/Personagens_que_a_internet_ESTRAGOU_Estilo_Aprovado_16x9.mp4).
- [Somente o restante: Tracer ao encerramento](output/Restante_Tracer_ao_Encerramento_Estilo_Aprovado_16x9.mp4).
- [Projeto Filmora com as mídias do restante](output/Restante_Estilo_Aprovado_Filmora.zip).
- [Capítulos para a descrição do YouTube](capitulos_youtube.txt).
- [Montagem e enquadramentos](montagem.json), [projeto](projeto_filmora.json) e [verificações](verificacao.json).

## Padrão da versão

A referência aprovada é a prévia de 15 s do commit `aee7345eacb48e6d6286b16f8962b2b131ab6656`. As vinhetas mantêm os retratos com movimento vertical de baixo para cima e os nomes dourados com extrusão. O tratamento do corpo usa o mesmo glow discreto e reenquadramento em 640×360 ampliado por vizinho mais próximo. A oscilação artificial da tela foi removida. O movimento PS1 já existente nos modelos permanece.

Os zooms acompanham falas e reações, usando a entrada rápida em cerca de 0,25 s e aproximação até 208% quando a cena comporta esse enquadramento. Os valores e pontos de foco foram definidos por cena; gameplay, quadros explicativos e elementos importantes mantêm espaço para leitura. A entrevista da Tracer reutiliza as curvas da amostra aprovada. O encerramento mantém o plano contínuo e o corte para a marca.

As gravações completas dos sete blocos entram no tom, velocidade e ganho originais. A música é reduzida no sussurro da D.Va e na pergunta final da Tracer, e sai no fechamento sério da Mercy e na passagem do Sonic ao arcade de terror. A trilha varia entre três trechos recuperados em estéreo da edição do usuário: Cooped Up, The Scuffler e Bully — Searching, conforme os nomes registrados no WFP. O alinhamento/subtração das vozes limpas e o filtro em 8 kHz reduzem os resíduos de AAC. São recuperações do MP4, não arquivos musicais originais separados.

O trecho recebido até 4:52,483 é copiado para o completo sem recodificar a imagem. O áudio é reunido numa sequência contínua e codificado em AAC para evitar atraso acumulado entre blocos. A versão anterior da montagem, os shorts, os arquivos Blender e a amostra aprovada continuam preservados. Não houve novo render Blender.

## Ajustes no Filmora

Extraia o ZIP antes de abrir `Restante_Estilo_Aprovado.wfp`. Se pedir mídia, localize o primeiro arquivo na pasta `midias`; todos têm nomes únicos. Voz, música, vídeo base, retrato e logo estão separados. O projeto contém somente o restante, para facilitar o acabamento sobre a edição já feita pelo usuário. Após exportar os ajustes, ele pode ser acrescentado ao projeto anterior em 4:52,483. O MP4 completo também já está pronto para assistir.

Os plugins pagos usados no projeto original foram preservados. Os módulos **Text Vibrate** e as transições de oscilação ficam **desativados por padrão**, acompanhando a correção aprovada; seus parâmetros continuam disponíveis para edição. O Glow e os efeitos das vinhetas permanecem. Não foi imposta limitação por licença.

**A abertura deste WFP ainda precisa ser validada no Filmora do usuário.** A checagem de integridade, mídias e tempos não substitui esse teste. O aplicativo não é executado neste ambiente Linux; os MP4s usam o tratamento por código aprovado na amostra, e não uma renderização dos plugins proprietários.

## Reprodução da produção

`montar.py` prepara as mídias, recupera as trilhas, renderiza o tratamento sobre os masters e exporta o completo e o restante. `projeto_filmora.py` monta o projeto nativo e seu pacote. Requer FFmpeg, FFprobe, NumPy, SciPy e Pillow. O helper do teste 15 foi generalizado com argumentos opcionais de duração/nome, mantendo os padrões da amostra. Intermediários ficam em `renders/`, fora do Git; o ZIP versionado é o pacote de entrega.

Vídeos base do projeto são remuxes sem áudio dos masters originais a 24 fps, sem perda de imagem. A entrega MP4 é 1920×1080 a 60 fps, com repetição dos quadros de animação e movimentos de zoom no ritmo aprovado. Os pequenos ajustes de duração ocorrem somente no silêncio final, para alinhar os quadros a 60 fps; todas as falas foram preservadas.
