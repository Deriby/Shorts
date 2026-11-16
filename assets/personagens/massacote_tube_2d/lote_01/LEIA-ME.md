# Massacote Tube — 10 poses, lote 01

Primeiro teste para avaliação. Não é o lote final de cem.

## Conteúdo

- `poses/`: dez PNGs RGBA transparentes em 1024 × 1536: neutro, conversando, debochado, apontando, confuso, bravo, pensando, rindo, assustado e facepalm.
- `Previa_10_Poses.jpg`: prancha de consulta.
- `galeria.html`: galeria local com busca e reprodução da fala; abra após extrair o ZIP.
- `catalogo.json` e `catalogo.sqlite`: IDs estáveis, nomes, tags, caminhos relativos, hashes e estado de aprovação. SQLite contém dez registros na tabela `poses`.
- `fala/`: três PNGs registrados A/B/C, WebP animado transparente em resolução integral e GIF de prévia com 512 × 768.

## Conversando sem mostrar a boca

O frame A é idêntico à pose `02_conversando.png`. As edições B/C do bigode foram geradas com image_gen. A montagem dos quadros usa uma máscara fixa limitada à região do bigode: todos os pixels fora dela são idênticos ao A. Há uma pequena margem de pele junto ao contorno da máscara; nenhuma boca foi desenhada.

O ciclo de 0,6 s segue A (120 ms), B (80 ms), A (100 ms), C (80 ms), B (80 ms), A (140 ms). Repita durante a fala e volte ao A nas pausas. É um teste de movimento, sem áudio e sem sincronismo com uma gravação específica. Use os PNGs para montagem em editores; o WebP oferece a prévia animada com transparência. O GIF é apenas uma prévia menor com paleta limitada.

## Consulta e verificação

`python buscar.py confuso` busca títulos/tags no SQLite. `python catalogar.py` revalida os PNGs, os limites da alteração da fala e o WebP, e atualiza JSON/SQLite/galeria. Requer Pillow e NumPy (já disponíveis no ambiente).

As dez poses foram inspecionadas, estão inteiras no quadro e têm boca coberta. A aprovação estética depende do usuário. Os arquivos originais retornados pelo gerador foram mantidos em `/workspace/generated_images`; as dez poses principais são cópias sem transformação. O anexo aprovado do usuário continua sendo a referência de identidade.
