# Jogos que a internet tentou cancelar

Série em produção para o Massacote Games. O primeiro capítulo é **GTA San Andreas / Hot Coffee**, com a voz e as mídias enviadas pelo usuário. Os outros jogos serão definidos depois; esta entrega não é o vídeo longo completo.

## 01 — GTA San Andreas

- [Short 9:16 — download](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/01-gta-san-andreas/output/GTA_San_Andreas_Cancelar_9x16.mp4).
- [Capítulo 16:9 para o longo — download](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/01-gta-san-andreas/output/GTA_San_Andreas_Cancelar_16x9.mp4).
- [Projetos Filmora com mídias — download](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/01-gta-san-andreas/output/GTA_San_Andreas_Projetos_Filmora.zip).
- [Prévia vertical](production/01-gta-san-andreas/output/Previa_Cenas_9x16.jpg) e [prévia horizontal](production/01-gta-san-andreas/output/Previa_Cenas_16x9.jpg).
- [Roteiro de animação sobre a voz](production/01-gta-san-andreas/roteiro_animacao.md).
- [Blender editável](production/01-gta-san-andreas/output/Dery_GTA_San_Andreas.blend).
- [Produção, fontes e verificações](production/01-gta-san-andreas/).

Os dois vídeos têm **53,4 segundos**, em 1080×1920 e 1920×1080, 30 fps. A gravação inteira, de aproximadamente 53,09 segundos, foi preservada. Não foi criada outra voz, nem foram cortadas frases. O pequeno respiro final permite encaixar o capítulo seguinte.

## Edição e projetos

O pacote inclui **dois WFPs**, vertical e horizontal, as respectivas bases silenciosas, voz, trilha baixa e sons separados. Os cortes, zooms e títulos nativos ficam editáveis. Extraia tudo antes de abrir e mantenha `midias/` ao lado dos projetos. A fonte Baloo 2 com licença OFL acompanha o pacote.

A referência de estilo é a edição concluída pelo usuário na produção 20 de “Personagens que a internet estragou”: títulos amarelos com contorno, enquadramentos pela fala, sons pontuais e Glow localizado nos títulos. Não há oscilação artificial da tela. A estrutura dos projetos é verificada por código; **o Filmora não foi executado no Linux**, portanto a abertura e a aparência dos plugins nativos devem ser conferidas na instalação do usuário. Os MP4s foram compostos/exportados neste ambiente, com aproximação dos elementos de edição; não são exports do renderizador proprietário do Filmora.

## Visual e atuação

Foi reutilizado o Dery original, com camiseta preta/M e as 131 expressões PNG. As bocas mudam por troca seca de textura e respondem à energia da gravação; isso é animação estilizada, não alinhamento fonético automático. Os braços usam gestos assimétricos com pausa e retorno, e as caretas pontuam a piada. A estante, o balcão e o armário criam duas vinhetas fora do quarto, ligadas à história.

O render 3D usa 768×432/15 fps e composição central planejada para o 9:16. A edição adapta os inserts, os zooms e os textos para cada formato. A ampliação Nearest, a paleta RGB555 com dithering fixo e a precisão geométrica de câmera mantêm a aparência PS1 nítida, sem filtro borrado ou glitch. Renders intermediários e ASR ficam fora do Git.

O Blender tem as imagens incorporadas; o vídeo do CRT é uma dependência externa em `production/01-gta-san-andreas/assets/monitor/monitor_completo.mp4`. Para editar a cena, mantenha essa organização ou clone com Git LFS. O WFP utiliza os renders já compostos: alterar a atuação ou o conteúdo 3D do CRT exige retornar ao Blender.

As fontes recebidas, seus nomes e hashes estão em `recebimento.json`. A música de fundo vem do áudio do showcase enviado, em volume baixo e com redução durante a fala. Os efeitos curtos de interface/reação foram sintetizados para esta edição. Não foram publicados o ZIP bruto, a referência pessoal de gestos ou imagens do minigame adulto.
