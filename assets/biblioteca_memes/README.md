# Banco de memes — Massacote Games

Pack recebido pelo usuário: [pasta do Drive](https://drive.google.com/drive/folders/1TyzZ9JY1sLPyZBetqwwRDADzsqpLHRX6). **303 arquivos originais, 94,65 MB**, arquivados com tamanho e MD5 de origem conferidos e SHA-256 local: 100 áudios, 103 entradas da pasta de imagens e 100 vídeos. Quatro arquivos da pasta de imagens também são vídeos; a classificação técnica está no catálogo. Há 302 conteúdos únicos por SHA; os originais duplicados também foram preservados.

- `arquivos/`: todos os originais, armazenados pelo ID do Drive via Git LFS.
- [Catálogo JSON](catalogo.json) e [banco SQLite](catalogo.sqlite3): nomes, origem, tags, duração, dimensões, miniaturas e estado de revisão.
- [Galeria local pesquisável](index.html): abra o arquivo depois de obter a pasta pelo Git LFS; vídeos/áudios têm controles e carregam somente ao reproduzir.
- `miniaturas/`: prévias dos 203 recursos visuais.

Pesquisa: `python assets/biblioteca_memes/buscar.py computador` ou `python assets/biblioteca_memes/buscar.py gato choro`. O JSON/SQLite é a fonte de busca para os próximos projetos. Reutilizar o cache, sem baixar tudo de novo. Os arquivos usados na primeira edição estão registrados no plano `009/production/14-video-completo/revisao_memes_v3/plano_preparado.json`.

Todos os arquivos tiveram formato/duração conferidos. As miniaturas visuais foram inspecionadas; os vídeos escolhidos para a produção receberam conferência de quadros em vários momentos. Isso não significa que cada segundo de todos os vídeos/áudios foi assistido ou ouvido. O campo `review_status` distingue prévia, metadados e seleção. Sons não utilizados continuam com revisão técnica/nome. Conferir o trecho integral antes de usar um arquivo novo: a miniatura não garante que o resto do vídeo tenha o mesmo conteúdo.

Manter os memes limpos, sem filtro PSX. Nos projetos, trabalhar em derivados e registrar ID, tempo de fonte, uso e nível de áudio. Não substituir gameplay documental por meme como se fosse prova de um fato. Preservar a voz e o projeto do usuário.

O pack mistura conteúdo de terceiros; o arquivo promocional “Leia, Importante!” não concede licença geral nem é instrução do usuário. Não assumir CC0/royalty-free para o pacote inteiro por causa do nome de um áudio. Não há assinatura, instalação ou visita ao site promocional necessária para reutilizar o banco local.

Reprodução da aquisição: `sincronizar.py`, `indexar.py`, `catalogar.py`. A listagem completa usa paginação da API pública do Drive; as páginas HTML de 50 arquivos eram apenas o catálogo inicial. A referência de edição não faz parte do pack e não foi adicionada como mídia para reutilização.
