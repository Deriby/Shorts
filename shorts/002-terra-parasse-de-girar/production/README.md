# E se a Terra parasse de girar AGORA?

Produção do short 002 com a gravação `testevideo2.mp3`, recebida do usuário, e o modelo Dery original. Duração do áudio decodificado: aproximadamente 55,406 segundos.

Montagem final: 55,417 segundos, 1330 quadros, 1080 × 1920 a 24 fps. Arquivo completo decodificado sem erros; a comparação entre o áudio exportado e a soma da gravação com os efeitos confirmou alinhamento sem deslocamento e ganho preservado, dentro das diferenças de compressão AAC.

## Entregas

- `output/Dery_Terra_Parou.mp4`: voz e efeitos discretos, sem legendas.
- `output/Dery_Terra_Parou_sem_audio.mp4`: imagem sem áudio para edição.
- `output/Dery_Terra_Parou.blend`: projeto editável com texturas e dois sons empacotados.
- `output/validacao_video.json`: resultado da checagem de formato, decodificação e áudio.
- `output/validacao_pegada.json`: checagem dos punhos durante as cenas do poste.

Os ZIPs de download e os quadros intermediários são gerados localmente e ficam fora do Git para evitar duplicar os arquivos versionados.

## Direção desta versão

A pedido do usuário, esta produção tem ambientes e situações diferentes, em vez de concentrar a montagem no personagem num fundo único:

- Rua de uma cidade costeira, com lojas, calçadas, asfalto, postes, fiação, bancos e palmeiras.
- Carro 3D visto por fora e por dentro, com painel, volante e banco do motorista.
- Litoral com casas, areia, mar e uma onda em malha 3D que avança.
- Globo terrestre geométrico com continentes estilizados e indicação do Equador.
- Terra em órbita do Sol mantendo sua orientação, para explicar os dias e noites longos.
- Piada física com o personagem agarrado a um poste cuja base cede.

São 21 planos editoriais. `timing.json` contém os cortes alinhados por reconhecimento local de fala e pausas da gravação. A voz não foi enviada a um serviço de transcrição externo. O reconhecimento automático teve erros de palavras; o texto aprovado e a gravação original permanecem como referência, sem transformar o texto reconhecido em legenda.

## Personagem e materiais

O modelo e rig fornecidos pelo usuário são preservados. As expressões PNG são reutilizadas do short 001 por meio do UV e máscara faciais. As ações existentes do rig servem como base; a encenação específica usa poses, alvos de mão e objetos animados.

Os cenários usam geometria 3D e atlas de texturas gerados para a estética PS1. As texturas de fachadas são materiais aplicados aos prédios; não são imagens da cena inteira sendo movidas para simular animação.

## Ferramentas e arquivos

- Blender 4.3, CPU; sem addons necessários para montar a cena.
- `build_scene.py`: cenários, movimentos, câmeras, iluminação e gravação do projeto.
- `character.py`: rig, materiais, expressões e uso das ações do modelo.
- `assets/Dery.glb`: modelo original com as 23 ações; é a entrada usada pelo gerador.
- `assets/dery_base_limpa.blend`: referência neutra preservada do modelo.
- `assets/voz_original.mp3`: gravação original, sem alteração de velocidade.
- `assets/cidade_atlas.png`, `detalhes_atlas.png` e `ceu_dia.png`: texturas dos ambientes.
- `align_audio.py`: etapa opcional de reconhecimento local com sherpa-onnx; os tempos já preparados ficam em `timing.json`.
- `make_effects.py`: efeitos sonoros originais e discretos, com redução durante a fala; não altera o ganho da voz.
- `validate_grip.py`: checagem de distância entre os punhos e os alvos nas cenas do poste.
- `assemble.sh`: exportação vertical, voz original e efeitos.

O projeto contém as ações originais para edição. O gerador usa criação de curvas em lote e um cache local recriável de poses para evitar milhares de atualizações desnecessárias do Blender.

## Pegada do poste

Os dois braços usam alvos de punho e de cotovelo, com orientação explícita das mãos para as laterais do poste. Isso corrige o cotovelo esquerdo virado para dentro e o posicionamento anterior dos punhos no centro do objeto. O poste carregado e os alvos acompanham o mesmo movimento do personagem.

A verificação em oito momentos das cenas, com duas mãos por momento, passou com erro máximo de aproximadamente 0,62 mm entre punho e alvo. Essa é uma checagem do rig; os quadros também foram conferidos para composição e leitura do rosto. A malha original não tem articulação individual de dedos, então a pegada é estilizada com a mão existente.

## Formato e som

Render de origem 432 × 768 a 24 quadros por segundo, com saída 1080 × 1920. A voz mantém velocidade e ganho. Os efeitos são gerados localmente e mixados em nível baixo, sem música e sem legendas incorporadas. A duração de exportação é explícita para não perder os últimos samples na fronteira de um pacote AAC.

## Reproduzir a construção e os testes de quadro

```bash
cd /workspace/Shorts/shorts/002-terra-parasse-de-girar/production
blender -b -t 4 --python build_scene.py -- --preview
```

Para renderizar a sequência depois de validar os quadros:

```bash
python make_effects.py
blender -b -t 4 --python build_scene.py -- --render
bash assemble.sh
python verify_video.py
```

O gerador substitui seu próprio projeto de saída. Salve edições manuais com outro nome antes de executá-lo. Os quadros intermediários e caches ficam fora do Git.

## Convenções

É uma ilustração de uma parada repentina da parte sólida da Terra. A órbita continua, a gravidade permanece e a velocidade citada se refere à região do Equador. Deslocamentos, ondas e danos são encenados para explicar a ideia; não são uma previsão geofísica quantitativa. O Sol, a Terra e a órbita são desenhos tridimensionais fora de escala. A sobrevivência do personagem e suas reações são recursos cômicos não gráficos.

Não incorporar legendas, conforme preferência do usuário. A montagem final deve conservar a gravação e usar a duração real do áudio.
