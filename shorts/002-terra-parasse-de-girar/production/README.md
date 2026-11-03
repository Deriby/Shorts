# E se a Terra parasse de girar AGORA?

Produção do short 002 com a gravação `testevideo2.mp3`, recebida do usuário, e o modelo Dery original. Duração do áudio decodificado: aproximadamente 55,406 segundos.

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
- `assets/dery_base_limpa.blend`: modelo importado, sem a animação de outro short.
- `assets/voz_original.mp3`: gravação original, sem alteração de velocidade.
- `assets/cidade_atlas.png`, `detalhes_atlas.png` e `ceu_dia.png`: texturas dos ambientes.
- `align_audio.py`: etapa opcional de reconhecimento local com sherpa-onnx; os tempos já preparados ficam em `timing.json`.

## Reproduzir a construção e os testes de quadro

```bash
cd /workspace/Shorts/shorts/002-terra-parasse-de-girar/production
blender -b -t 4 --python build_scene.py -- --preview
```

Para renderizar a sequência depois de validar os quadros:

```bash
blender -b -t 4 --python build_scene.py -- --render
```

O gerador substitui seu próprio projeto de saída. Salve edições manuais com outro nome antes de executá-lo. Os quadros intermediários e caches ficam fora do Git.

## Convenções

É uma ilustração de uma parada repentina da parte sólida da Terra. A órbita continua, a gravidade permanece e a velocidade citada se refere à região do Equador. Deslocamentos, ondas e danos são encenados para explicar a ideia; não são uma previsão geofísica quantitativa. A sobrevivência do personagem e suas reações são recursos cômicos não gráficos.

Não incorporar legendas, conforme preferência do usuário. A montagem final deve conservar a gravação e usar a duração real do áudio.
