# Retomada do Massacote Tube — TED virou DESENHO

**Estado atual:** a [revisão 3](shorts/011-ted-virou-desenho/revisao_03/README.md) tem o projeto Filmora com o Massacote 2D nos dois trechos de reação. O usuário rejeitou os closes realistas e pediu a retirada das 40 imagens do catálogo ativo. A revisão 2 está registrada no [README do Ted](shorts/011-ted-virou-desenho/README.md). Os registros abaixo descrevem a preparação da primeira produção.

Este documento transfere o estado relevante da conversa anterior para um novo chat/ambiente. O histórico bruto da conversa não acompanha automaticamente o ambiente. Os arquivos e as decisões abaixo estão no repositório `https://github.com/Deriby/Shorts`, branch `main`.

## Pedido ativo e autorização

Produzir o short **TED virou DESENHO**. O usuário disse: “Agora mete bala nesse shorts”. A produção está autorizada: continuar até entregar o vídeo e o projeto, sem pedir confirmação para começar e sem parar no recebimento das fontes.

- Pasta: `shorts/011-ted-virou-desenho/`.
- Pacote original: https://drive.google.com/file/d/1KVYN09XWw_L1hs38SwaXAXrZhK8ELkec/view
- Nome confirmado: `TED virou DESENHO.zip`.
- Tamanho confirmado: **41.237.797 bytes**.
- Saída: short **9:16**, MP4 e WFP editável com as mídias usadas, entregues pelo GitHub.
- Sem nova voz, legendas automáticas ou textos que repetem a fala. O usuário legenda depois. Preservar a gravação recebida.
- Este pedido é do **Tube, com avatar 2D**. Não trocar pelo Dery 3D/PSX do Games e não retomar o longo 009.

O pedido anterior de gerar frames cômicos em 16:9 também foi cumprido; isso não pede automaticamente uma edição horizontal de todo novo short.

## O que realmente foi feito no Ted

Até a preparação desta retomada, **nenhum MP4 ou WFP do Ted foi montado**. O ZIP foi identificado e o conector gerou uma referência completa de arquivo, mas ele não foi transferido para o filesystem do ambiente antigo. A voz e as mídias internas não foram inspecionadas. Não inventar transcrição, roteiro exato, cenas ou tempos antes de abrir as fontes.

Registros: `shorts/011-ted-virou-desenho/README.md` e `recebimento.json`. Atualizá-los conforme o trabalho real avançar.

## Rede: verificar o novo ambiente, sem herdar o bloqueio antigo

O ambiente antigo bloqueava o download normal com HTTP CONNECT 403. A política era restrita, sem hosts adicionais. O usuário **já autorizou expressamente liberar `drive.usercontent.google.com`**, depois abriu outro ambiente para aplicar a configuração. Não pedir essa autorização de novo.

O erro de **32 MiB é de um importador específico, não do Google Drive**. O pacote Sonic de 128 MB foi recebido anteriormente. O usuário rejeitou a necessidade de dividir o ZIP: manter o arquivo inteiro no link original, sem exigir divisão ou reenvio.

1. Conferir a rede efetiva do novo ambiente. O bloqueio descrito acima é uma observação do ambiente antigo, não uma regra que deva ser presumida no novo.
2. Preferir o conector do Drive para metadados e arquivos. Para referência binária usar `fetch(download_raw_file=true, include_base64=false)`, quando disponível. Não pedir base64 inline nem versionar URLs temporárias assinadas.
3. Com rede liberada, o download normal do arquivo público pode usar o endpoint oficial `https://drive.usercontent.google.com/download?id=1KVYN09XWw_L1hs38SwaXAXrZhK8ELkec&export=download`, preservando proxy/TLS e a política do ambiente. O endpoint pode devolver um formulário de confirmação; conferir o conteúdo e o ID em vez de tratar HTML como ZIP.
4. Validar tamanho, assinatura/CRC do ZIP, extração segura e metadados. Em seguida ouvir/transcrever a gravação e assistir aos trechos enviados antes de planejar a montagem.

Se ainda houver bloqueio, relatar a condição observada neste ambiente e o ajuste concreto necessário. Não entrar de novo num ciclo de tentativas do importador limitado a 32 MiB.

## Personagem atual e recortes

O personagem ativo é o **Massacote Tube compacto com óculos 3D**, não as propostas históricas anteriores. Referência inteira aprovada:

`assets/personagens/massacote_tube_2d/estudos_estilo/oculos_3d_v1/Previa_Massacote_Oculos_3D.png`

Características: boné roxo para trás, cabelo castanho, óculos com armação creme, lente opaca vermelha à esquerda da imagem e azul à direita, bigode castanho grande, cavanhaque, jaqueta roxa/vermelha e brasão M. **Boca sempre completamente coberta pelo bigode. Não animar olhos por trás das lentes opacas.**

O usuário rejeitou repetidamente os recortes antigos de cabeça/bigode/corpo e as tentativas de remendar máscaras. A arte inteira foi elogiada como “filé”, mas isso não aprovou os recortes. Depois autorizou regenerar as peças separadas.

A versão mais recente, regenerada, está em:

`shorts/010-sonic-memories-beyond/production/recortes_regenerados_01/`

- PNGs de uso: `output/Filmora/midias_regeneradas/` (15 peças 1080×1920: cabeça, bigode, nove corpos e quatro frentes transparentes).
- Fontes geradas: `fontes/`.
- Conferência de encaixe: `analise/Galeria_9_Poses_Regeneradas.jpg` e `analise/Previa_Pecas_Regeneradas.mp4`.
- Projeto derivado: `output/Filmora/Massacote_Tube_Sonic_Pecas_Regeneradas.wfp`.

Esta entrega mais recente tem conferência técnica/visual registrada, mas **não recebeu aprovação estética individual explícita do usuário nem teste nativo do Filmora**. Inspecionar o encaixe e o movimento antes de reutilizar. Não afirmar que todos os recortes foram aprovados.

Não reutilizar como “corrigidos” o pacote rejeitado `correcao_recortes_01`, os protótipos de remendo ou as camadas defeituosas do banco `oculos_3d_30_poses`. O JSON histórico de direção ainda aponta para esse banco; para a questão dos recortes, considerar o estado mais recente registrado aqui e no início do `AGENTS.md`.

## Referência de edição prioritária

O usuário reeditou o Sonic para demonstrar seu estilo. A referência principal é o WFP recebido intacto:

`shorts/010-sonic-memories-beyond/production/edicao_usuario_01/recebido/Massacote_Tube_Sonic_EDITADO_USUARIO.wfp`

SHA-256: `bf145baeebb2087f05023716b7d9f5b351a4fcbda949715a1f000061e427d9c3`.

Ler também o README e o inventário de `edicao_usuario_01/`. A edição dele usa fundo nativo animado, painéis com recortes/bordas/sombras, transições Basic Zoom In/Fast Bounce e efeitos Glow/Text Vibrate/Grunge_Jitter. Não tratar esses efeitos escolhidos pelo usuário como proibidos nem inventar tremido global por código para fingir plugins. Adaptar composição, ritmo, gestos e sons à voz do Ted; não copiar os tempos do Sonic.

Referência adicional em vídeo do próprio Tube:

`shorts/010-sonic-memories-beyond/production/revisao_v2_refTube/referencia/Massacote_Tube_Carros_Referencia.mp4`

As montagens anteriores geradas do Sonic não equivalem à referência final aprovada do estilo. Preservar todos os arquivos antigos e não reeditar o Sonic por esse novo pedido.

Ferramentas locais de composição e criação de WFP existem nos scripts de `010/production/revisao_v3_cenas/`; são implementação reaproveitável, não a direção estética definitiva. A abertura/exportação nativa do Filmora não foi executada no Linux anterior. Conferir as capacidades do novo ambiente e comunicar a validação que realmente for possível.

## Bancos que precisam ser consultados na edição

### Memes recebidos do Drive

`assets/biblioteca_memes/`: **303 arquivos originais**, catálogo JSON, SQLite, galeria e `buscar.py`. O usuário reforçou para não esquecer esse banco no próximo vídeo. Vale para o Tube e para o Games, apesar do título histórico “Games” no README.

Pesquisar pelos contextos da fala, assistir/ouvir integralmente o trecho escolhido e registrar ID, corte e nível de áudio. Preservar o meme limpo e não usá-lo como prova documental de um fato. Não baixar o banco todo outra vez se os arquivos versionados/LFS já estiverem presentes.

### Catálogo de closes realistas retirado

Os 40 frames do acervo de reações deixaram o catálogo do Tube na revisão 3 do Ted. A direção atual usa o avatar 2D original do Tube nas reações.

## Retomada prática e entrega

- Ler este documento e o início do `AGENTS.md` antes de escolher assets. Os registros mais antigos são históricos e contêm instruções superadas.
- Usar `main` atualizado. Se houver trabalho já feito no novo ambiente, inspecionar e preservar antes de atualizar; não resetar ou forçar o push.
- Obter os binários necessários via Git LFS; um arquivo de poucos bytes com `version https://git-lfs.github.com/spec/v1` é só um ponteiro. Baixar seletivamente os assets usados, sem puxar todos os episódios/ZIPs históricos.
- Trabalhar no Ted em `shorts/011-ted-virou-desenho/`, mantendo voz/fontes, decisões de montagem, scripts e arquivos de entrega rastreáveis.
- Ouvir/assistir, planejar por fala, montar, conferir recortes/gestos/legibilidade/áudio em movimento e entregar MP4 + WFP/mídias. Validação de hash/JSON não substitui qualidade visual ou teste do aplicativo.
- Salvar etapas concluídas no GitHub e confirmar o push. Downloads finais pelo GitHub. Não afirmar que o Ted terminou antes de existir uma entrega verificada.

O objetivo da migração é continuar o trabalho existente, sem pedir que o usuário explique o estilo, envie os bancos ou aprove a produção outra vez.
