# Massacote Tube — banco modular 01

Conjunto no visual Samurai Jack com acabamento digital amador, cabelo menor, olhos alongados e brasão M vermelho. Preparado conforme o plano confirmado pelo usuário. A aparência do conjunto e da animação aguarda avaliação.

## Peças para montar

- `poses/`: 10 PNGs completos com a área do rosto limpa, sem olhos, sobrancelhas, nariz ou bigode. Cabeça, cabelo, boné, orelhas, cavanhaque, roupa e gestos permanecem.
- `olhos/`: 13 pares em PNG, com olhos e sobrancelhas juntos. Inclui o par extraído do desenho aprovado e 12 variações: normal alternativo, piscada parcial, piscada fechada, bravo, confuso, pensando, desconfiado, assustado, rindo, piscando cada olho e preocupado.
- `bigode/`: bigode extraído do desenho aprovado em repouso, levantado e comprimido; WebP com ciclo demonstrativo de 0,6 s. O PNG é uma camada independente. Nenhuma boca foi desenhada por baixo.
- `frente/`: mão/antebraço das poses pensando e facepalm para colocar à frente das expressões.
- `rig/`: cabeça limpa comum e os dez corpos separados para movimentar cabeça e corpo de forma independente.
- `montados/`: mostruário das combinações. Esses JPGs são apenas exemplos; os PNGs das peças estão nas pastas acima.
- `catalogo.json`, `catalogo.sqlite` e `registro_encaixe.json`: índice, hashes, tipos e coordenadas do conjunto para reutilização.
- `fontes/`: originais gerados para preparar os assets, preservados para reprodução; use as pastas de peças para montar.

Os nomes esquerdo/direito das piscadas consideram o lado da imagem, para facilitar a escolha visual.

Todos os PNGs de peças usam **1024×1536** com transparência e registro comum. Não recorte as margens transparentes. A posição da cabeça foi padronizada para trocar as expressões sem reposicionar os elementos.

## Montagem simples no Filmora

Use, de baixo para cima: pose com rosto limpo → olhos → bigode → camada de mão à frente quando existir. Mantenha as mesmas dimensões, posição e escala em todas essas imagens. A camada `frente` tem a posição exata da mão da pose correspondente e restaura a oclusão quando os olhos ou o bigode passam por trás dela.

Para mover a cabeça separadamente, use o corpo e a cabeça da pasta `rig` em vez da pose completa, seguindo a montagem já pronta no WFP. Os olhos e o bigode acompanham o movimento da cabeça; a mão em primeiro plano acompanha o corpo.

## Prévia com voz e projeto

`previa/Previa_Modular_Conversando.mp4` tem 9,3 s/279 quadros/1280×720/30 fps. Mostra conversa, piscadas, apontar, confusão e facepalm. A fala usa o mesmo trecho de 0–9,3 s da intro de Personagens que a internet estragou já existente no projeto, sem criar uma voz nova, mudar tom ou velocidade. O bigode acompanha a energia e as pausas da voz; não é sincronismo fonético de uma boca.

`previa/Filmora/Massacote_Tube_Modular_Previa.wfp` contém seis faixas visuais (fundo, corpo, cabeça, olhos, bigode, mão à frente) e uma faixa de voz. Todas as dez poses e todos os olhos também estão preparados na biblioteca de mídias do WFP. A timeline curta usa quatro poses e piscadas/expressões ao longo da fala. Mantenha `midias/` ao lado do WFP.

Abertura/reprodução/exportação nativas no Filmora ainda não foram verificadas neste Linux. O WFP passou nas verificações estruturais de biblioteca, caches, UUIDs, bindings e duração. O MP4 é uma composição local das mesmas transformações numéricas, sem Blender. A animação com uma nova voz precisa de duração e keyframes de fala recalculados para essa gravação.

## Galeria e conferência

Extraia o ZIP inteiro e abra `galeria.html` no navegador para consultar poses, olhos e a prévia com áudio. `Previa_10_Poses_Montadas.jpg` mostra exemplos de encaixe.

O banco SQLite tem a tabela `assets` (39 PNGs, com tipo, nome e caminho) e a tabela `rig` (dez montagens). As artes anteriores e a prévia antiga permanecem intactas.

Para reproduzir as etapas no ambiente, usando os originais persistidos e o Python com Pillow/NumPy/OpenCV/SciPy:

```
source /workspace/.shorts-venv/bin/activate
python assets/personagens/massacote_tube_2d/modular_01/preparar_assets.py
python assets/personagens/massacote_tube_2d/modular_01/preparar_previa.py
python assets/personagens/massacote_tube_2d/modular_01/previa/gerar_animacao.py
python assets/personagens/massacote_tube_2d/modular_01/previa/montar_filmora.py
python assets/personagens/massacote_tube_2d/modular_01/catalogar_validar.py
python assets/personagens/massacote_tube_2d/modular_01/empacotar.py
```

Downloads e entregas pelo GitHub. Os arquivos de geração não fazem novas chamadas ao image_gen: usam as fontes que já foram salvas.
