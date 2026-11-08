# Teste de estilo — Tracer, 15 segundos

O usuário rejeitou a semelhança da primeira montagem e autorizou uma amostra curta para chegar mais perto da edição dele. Esta produção é isolada; o longo de 9min04, o WFP recebido e todos os masters anteriores ficam preservados.

- [Prévia MP4 16:9 de 15 segundos](output/Teste_Tracer_Estilo_15s_16x9.mp4).
- [Pacote para abrir no Filmora, com projeto e mídias](output/Teste_Tracer_Filmora_15s.zip).
- [Projeto WFP separado](output/Teste_Tracer_15s.wfp), que usa as mídias do ZIP.
- [Configurações nativas copiadas](efeitos_nativos_copiados.json).
- [Produção](producao.json) e [verificação](verificacao.json).

## Para testar no Filmora

Extraia o ZIP antes de abrir `Teste_Tracer_15s.wfp`. Se o Filmora pedir mídia ausente, localize o primeiro arquivo na pasta `midias` extraída. Todos os arquivos necessários estão ali. O projeto parte da versão **Filmora 14.9.3**, usada no WFP original. Os plugins da edição original precisam estar disponíveis na instalação do usuário.

**A abertura no Filmora ainda não foi validada:** o aplicativo não está disponível neste ambiente Linux. O WFP passou por checagens de integridade, referências e tempos, que não substituem o teste no aplicativo. A finalidade desta cópia é justamente testar a preservação dos efeitos nativos antes de produzir o restante. O projeto original não é sobrescrito.

## O que mudou em relação à tentativa anterior

Os zooms da edição recebida atingem 187% em cerca de 0,25 segundo e depois chegam a 208%; a primeira montagem usava reenquadramentos muito mais discretos. A amostra agora usa essa dinâmica nas reações do convidado, enquadrando cada personagem conforme a câmera. O final expõe a pergunta “mas conhece ela pelo jogo, né?” com redução da trilha.

A vinheta usa um título com extrusão dourada e retrato com movimento vertical de baixo para cima, como o template da 2B. O WFP reaproveita os dois compostos originais da vinheta, a transição e as cadeias de plugins. As duas camadas globais de **Text Vibrate** (força 5 / velocidade 50 e força 10 / velocidade 80) e o **Glow 40** mantêm as configurações originais. Os arquivos PNG/JPG são novos para a Tracer; os títulos são imagens, sem necessidade de instalar uma fonte.

O **MP4 aproxima os plugins** com composição por código. Ele serve para assistir ao ritmo e à proposta visual imediatamente. A renderização dos plugins nativos ficará por conta do teste do WFP no Filmora; não afirmar que os dois renders são idênticos.

O usuário rejeitou a oscilação artificial da tela na primeira prévia. A versão atual do MP4 remove esse deslocamento; o movimento PS1 já existente nos modelos permanece. O usuário confirmou que tem o Filmora pago e autorizou manter os plugins pagos no WFP, que continua com os efeitos nativos originais. A licença não foi uma limitação usada para escolher os efeitos desta produção.

## Voz e música

A vinheta tem 248 quadros a 60 fps (4,133 s). Em seguida entram os 10,867 s finais da entrevista, entre 13,917 e 24,783 s do master da Tracer. O trecho começa em “Tinha gente…” e contém a piada completa. A voz mantém tom, velocidade e ganho originais.

A trilha foi recuperada em estéreo do trecho 79,5–91,5 s da edição recebida: a narração limpa da Tifa foi alinhada e subtraída com ganho estimado de 0,9969. O processamento aplica passa-baixas em 8 kHz para reduzir diferenças de AAC. A checagem local de reconhecimento de fala identificou apenas música. Isso preserva mais instrumentação que a extração lateral da tentativa anterior, mas não equivale a ter o arquivo musical original separado.

`recuperar_trilha.py` prepara a música a partir das fontes já salvas; `produzir_teste.py` cria a amostra e o WFP. Requer FFmpeg, NumPy, SciPy e Pillow. Os intermediários ficam em `renders/`, fora do Git. O ZIP versionado é o pacote de entrega com as mídias do projeto, e não o arquivo bruto baixado do Drive.
