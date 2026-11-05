# Personagens que a internet estragou — 2B

Sexto bloco, produzido a partir do pacote “6 - 2B.zip” enviado pelo usuário. Versões **9:16 em 1080×1920 e 16:9 em 1920×1080**, 24 fps, **39,375 segundos**. A voz decodificada tem 38,710 segundos e foi preservada inteira, sem acelerar, mudar o tom ou acrescentar falas. O restante é silêncio final.

## Montagem e atuação

Os 21 planos acompanham a gravação: identificação no monitor, combate contra máquinas, reflexão, reação aos fãs, meme, três pastas ilustrativas, resignação, autodestruição real, incredulidade, resultado da habilidade, régua cômica e estação de treinamento. O final permanece em “lutar contra a internet”. Não há legendas da narração embutidas.

A estação reaproveita piso, parede, pilares e aparência da garagem Driver, sem o carro ou a interface de chefão. Dery fica em pé numa plataforma, apresenta o teste confiante e acompanha o terminal. Em **35,25 s**, a seleção troca de “MÁQUINAS — PREPARADO” para “INTERNET — SEM TREINAMENTO”. Ele interrompe o gesto, abre os olhos e termina sem reação. O resultado muda por interface normal, sem glitch, clarões ou piscadas.

Os gestos do quarto seguem intenções distintas: apresentação contida, cabeça mais baixa na reflexão, indicação com a outra mão, palma resignada e uma objeção curta. A atuação tem preparação, sustentação e retorno, com pausas e tempos diferentes entre os braços. Não há ciclo periódico de conversa. A referência pessoal de gestos permanece privada.

O Dery mantém a geometria original, boné, camiseta preta com M amarelo, pele limpa e correção das fissuras. Usa as 31 faces PNG com troca seca e sem morphs. O clone em pé conserva o apoio dos pés e o quadril.

## Mídias e escolhas

O combate vem do vídeo de combo fornecido. A autodestruição usa a ativação, explosão e recuperação do gameplay original, mantendo o contexto e o corpo inteiro no enquadramento. A régua aparece num insert separado: é hipérbole visual, sem medir o corpo ou sugerir que golpes comuns removam o traje.

O retrato e o meme da fã foram enviados no pacote. As pastas “FANART”, “ANIMAÇÃO” e “MODS” são ilustrações próprias, com prévias opacas e seleção em três etapas. Não há fan animation adulta original. O meme com atribuição de fala ao diretor e o vídeo das escadas não foram usados. A trilha final contém somente a gravação do usuário; os áudios dos vídeos estão mutados.

## Arquivos

- `output/2B_Personagens_que_a_internet_estragou_9x16.mp4` e `output/2B_Personagens_que_a_internet_estragou_16x9.mp4`: finais.
- `output/Dery_2B.blend` e `output/Dery_2B_Master_16x9.blend`: quarto, estação, rig, faces, atuação e voz.
- `assets/voz/voz_original.mp3`: recebido, preservado byte a byte. Os WAVs são a decodificação e a cópia com silêncio final.
- `assets/gameplay/`: recortes selecionados e feed sincronizado do monitor. `assets/memes/`: mídias preparadas e interfaces próprias.
- `timeline.json`, `acting_cues.json`, `face_cues.json`: cortes, atuação e expressões.
- `source_manifest.json`: fontes, hashes, intervalos usados e escolhas editoriais.
- `scene_validation*.json`, `export_validation*.json`: verificações de malha, costuras faciais, apoio, braços, voz e MP4.
- [Estação reutilizável](../../../../assets/cenarios/estacao_treinamento/): cenário genérico sem Dery, voz ou mídia do pacote.

## Visual e reprodução

Render nativo 360×640 / 640×360 e ampliação inteira 3× por vizinho mais próximo. Precisão reduzida de geometria com proteção de costuras, texturas Closest, corpo endereçado em 128 px, concreto de 64 px, paleta RGB de 5 bits e Bayer fixo 4×4. Sem blur, glitch ou luz piscando. As interfaces têm layout próprio em cada formato.

Na raiz do repositório, com Blender 4.3, FFmpeg, NumPy e Pillow:

```sh
blender -b -t 2 --python-exit-code 1 --python shorts/008-personagens-que-a-internet-estragou/production/06-2b/build_short.py
blender -b shorts/008-personagens-que-a-internet-estragou/production/06-2b/output/Dery_2B.blend -t 1 --python-exit-code 1 --python shorts/008-personagens-que-a-internet-estragou/production/06-2b/verify_scene.py
python shorts/008-personagens-que-a-internet-estragou/production/06-2b/export_short.py
python shorts/008-personagens-que-a-internet-estragou/production/06-2b/verify_export.py
```

No horizontal, adicionar `-- --wide` aos comandos Blender e `--wide` aos scripts Python; carregar `Dery_2B_Master_16x9.blend` na verificação. `--resume` retoma quadros completos e `--encode-only` codifica os existentes. O padrão refaz os planos 3D. Usar um formato por vez, com dois threads. Gameplay, imagens e gráficos entram diretamente na montagem.

`prepare_assets.py` requer o inventário privado e os originais restaurados. As mídias preparadas necessárias aos projetos e ao render ficam versionadas. Baixar a pasta inteira para editar: áudio e filmes usam caminhos relativos. ZIP, backups, quadros intermediários e referência pessoal permanecem fora do Git.
