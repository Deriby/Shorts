# Personagens que a internet estragou — Tracer

Sétimo bloco, produzido com o pacote “7 - Tracer.zip” enviado pelo usuário. Versões **9:16 em 1080×1920 e 16:9 em 1920×1080**, 24 fps, **25,083 segundos**. A gravação decodificada tem 24,414 segundos e foi preservada inteira, sem mudar velocidade, tom ou falas; o restante é silêncio final.

## Montagem e atuação

Os 16 planos acompanham a apresentação, Blink, Recall, modelo em programas 3D, prévia censurada, memes e entrevista. No quarto, Dery apresenta com uma mão, explica com a outra e deixa o gesto cair no suspiro. Não há ciclo periódico de conversa ou legendas da narração embutidas.

A entrevista usa duas cópias do modelo original, com o mesmo boné e camiseta preta com M amarelo, em cadeiras voltadas uma para a outra. O anfitrião apresenta o retrato e conduz a pergunta. O convidado acena, sustenta a expressão orgulhosa e perde o sorriso no complemento “mas conhece ela pelo jogo, né?”. Ele desvia os olhos e permanece sem resposta até o fim. **O convidado fica silencioso, sem faces de fala ou resposta gerada.** A voz recebida é a única faixa de voz.

As câmeras permanecem do mesmo lado do eixo entre os dois atores: plano inicial com ambos, pergunta do anfitrião e reação do convidado. Os closes preservam as direções dos olhares. O apoio do quadril e dos pés foi verificado em ambos os atores; as três cópias do Dery preservam a geometria original, as 31 faces PNG e a correção das fissuras. A referência pessoal de gestos continua privada.

## Fontes visuais

A identificação e as habilidades vêm de “Tracer Ability Overview | Overwatch”, enviado no pacote. Blink usa o trecho 24,2–26,6 s do original; Recall usa 31,2–34,28 s. O retorno de posição é visível. O HUD original mostra a vida no máximo nesse exemplo; não foram inventados valores ou uma recuperação de vida que o trecho não demonstre. A fala sobre a habilidade é mantida como gravada.

O viewport é uma ilustração própria com grade, cubo e retrato normal da Tracer, seguida de um cartão opaco. Não representa um arquivo real dos fãs e não inclui animação adulta. Os dois memes enviados são inseridos na montagem. “Don't mess with Tracer!” não foi selecionado. Todos os vídeos de referência estão mutados; a trilha preserva apenas a voz do usuário.

## Arquivos

- `output/Tracer_Personagens_que_a_internet_estragou_9x16.mp4` e `output/Tracer_Personagens_que_a_internet_estragou_16x9.mp4`: finais.
- `output/Dery_Tracer.blend` e `output/Dery_Tracer_Master_16x9.blend`: quarto, set, três rigs, atuação, faces e voz.
- `assets/voz/voz_original.mp3`: recebido, preservado byte a byte. Os WAVs são a decodificação e a cópia com silêncio final.
- `assets/gameplay/`: recortes e feed sincronizado. `assets/memes/`: memes preparados, retrato e interfaces próprias.
- `timeline.json`, `acting_cues.json`, `face_cues.json`: cortes, gestos por frase e expressões dos três atores.
- `source_manifest.json`: origem, hashes, intervalos e escolhas de mídia.
- `scene_validation*.json`, `export_validation*.json`: verificações de malha, rosto, apoio, braços, convidado silencioso, voz e MP4.
- [Set reutilizável](../../../../assets/cenarios/set_entrevista/): sala e duas cadeiras com superfície neutra, sem atores, voz ou mídias do pacote.

## Visual e reprodução

Render nativo 360×640 / 640×360, ampliação inteira 3× por vizinho mais próximo, precisão reduzida de geometria com proteção das costuras do rosto, texturas Closest, corpo endereçado em 128 px, paleta RGB de 5 bits e Bayer fixo 4×4. Sem blur, glitch ou luz piscando. As interfaces têm layouts próprios por formato.

Na raiz do repositório, com Blender 4.3, FFmpeg, NumPy e Pillow:

```sh
blender -b -t 2 --python-exit-code 1 --python shorts/008-personagens-que-a-internet-estragou/production/07-tracer/build_short.py
blender -b shorts/008-personagens-que-a-internet-estragou/production/07-tracer/output/Dery_Tracer.blend -t 1 --python-exit-code 1 --python shorts/008-personagens-que-a-internet-estragou/production/07-tracer/verify_scene.py
python shorts/008-personagens-que-a-internet-estragou/production/07-tracer/export_short.py
python shorts/008-personagens-que-a-internet-estragou/production/07-tracer/verify_export.py
```

Para o horizontal, adicionar `-- --wide` aos comandos Blender e `--wide` aos scripts Python; carregar `Dery_Tracer_Master_16x9.blend` na verificação. `--resume` aproveita quadros completos; `--encode-only` codifica os existentes. O padrão refaz os planos 3D. Usar um formato por vez, com dois threads. Imagens e gameplay entram diretamente na montagem; o ator fora do campo fica oculto nos closes. O feed usa quadros-chave a cada segundo.

`prepare_assets.py` requer o inventário privado e os originais restaurados. As mídias preparadas necessárias aos projetos e ao render ficam versionadas. Baixar a pasta inteira para editar: áudio e filmes usam caminhos relativos. ZIP, backups, quadros intermediários e referência pessoal ficam fora do Git.
