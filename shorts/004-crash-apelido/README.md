# O apelido mais quinta série do Crash

Primeiro episódio de jogos do Massacote Games. Curiosidade: o apelido interno “Sonic’s Ass Game” durante a criação do primeiro Crash Bandicoot.

## Etapa atual

- [Prévia estática em 16:9](production/output/Dery_Crash_Previa_16x9.png), renderizada no cenário Blender do Dery.
- Dois áudios originais recebidos, preservados separadamente: **11,527 s + 15,921 s**, cerca de **27,448 s** no total.
- Trechos de gameplay de **Crash Bandicoot N. Sane Trilogy**, selecionados para ilustrar a câmera por trás do protagonista.
- [Roteiro de referência e plano de cortes](roteiro.md).

A prévia usa uma captura do **Crash Bandicoot original de PS1** no monitor. Os trechos em vídeo selecionados são do remake, para apoio visual; não são imagens do protótipo nem filmagens da criação do jogo.

## Enquadramento

O master é **16:9**, em 1920 × 1080, com o monitor à esquerda e o Dery à direita. Para a versão 9:16, os cortes poderão alternar o recorte para o Dery e para o monitor. A composição é uma proposta visual estática; o vídeo completo ainda não foi renderizado nesta etapa.

A foto mantém a pose sentada corrigida, a iluminação ciano/violeta e o tratamento de contorno PS1. O sinal do canal foi posicionado na parede visível à câmera. A imagem do monitor tem a orientação correta, sem espelhamento.

## Arquivos e fontes

- [Áudios originais](production/assets/voz/).
- [Fontes, versões e intervalos dos trechos de gameplay](production/assets/gameplay/fontes.json).
- [Trecho 10–14 s da fonte](production/assets/gameplay/Crash_Nsane_camera_10-14.mp4).
- [Trecho 56–59 s da fonte](production/assets/gameplay/Crash_Nsane_apoio_56-59.mp4).
- [Script da imagem em 16:9](production/render_still_16x9.py).

O vídeo fonte é uma montagem com cenas de gameplay e cenas cinematográficas publicada num repositório de fãs. Foram separados trechos de gameplay; a autoria original da montagem não é identificada pelo arquivo. A narração é dos arquivos fornecidos pelo usuário.

## Reproduzir a imagem

Requer Blender 4.3, FFmpeg e os arquivos Git LFS do repositório. Reutiliza o projeto do quarto gamer e o renderizador de contorno do teste 003.

```bash
blender -b -t 4 --python shorts/004-crash-apelido/production/render_still_16x9.py
```
