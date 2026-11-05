# Personagens que a internet estragou — Vaporeon

Quinto bloco, produzido com o pacote “5 - Vaporeon.zip” enviado pelo usuário. Versões **9:16 em 1080×1920 e 16:9 em 1920×1080**, 24 fps, **47,417 segundos**. A gravação decodificada tem 46,755 segundos e foi preservada inteira, sem mudar velocidade, tom ou falas; o restante é silêncio final.

## Gravação e montagem

A voz recebida substitui partes do rascunho escrito: começa apresentando Vaporeon, antecipa a piada da pedra e termina com o pedido de contexto e os memes correspondentes. Não usa o antigo encerramento da comparação das pedras nem acrescenta a fala de fechar o navegador. Os 21 planos e os intervalos de mídia estão em `timeline.json`.

O conteúdo alterna Dery no quarto, cartão ilustrativo da Pedra da Água, documentos fictícios, gameplay de Pokémon UNITE, reações, mesa de redação, publicação com comentários e os memes de contexto enviados pelo usuário. O anime fornecido também integra o feed do monitor. Os áudios dos vídeos estão mutados; a trilha preserva somente a voz fornecida.

A mesa de redação adapta a base da sala da Tifa. Duas pilhas de folhas rígidas crescem por etapas na frase sobre a redação, sem simulação física. A mão aponta antes da entrada das folhas; depois, Dery recua o gesto, abre a outra palma e termina sem reação. A sequência usa olhares para a pilha e para a câmera, pausas e tempos diferentes entre os braços. Não há ciclo periódico de conversa.

O modelo, a camiseta preta com M amarelo e a correção das fissuras foram preservados. As faces são as 31 expressões PNG com troca seca. A referência pessoal de gestos permanece privada.

Os documentos e comentários são ilustrações próprias com conteúdo opaco. Não reproduzem o texto sexual da copypasta, nem seus supostos argumentos como explicação científica. Não há encenação de ato sexual ou consumo de drogas. O cartão da Pedra da Água é uma ilustração estilizada, não uma gravação da evolução.

## Entregas e arquivos

- `output/Vaporeon_Personagens_que_a_internet_estragou_9x16.mp4`: short vertical.
- `output/Vaporeon_Personagens_que_a_internet_estragou_16x9.mp4`: master horizontal, com câmera e composição próprias.
- `output/Dery_Vaporeon.blend` e `output/Dery_Vaporeon_Master_16x9.blend`: cenas, rig, gestos, faces e voz.
- `assets/voz/voz_original.mp3`: recebido, preservado byte a byte. Os WAVs guardam a decodificação e a cópia com silêncio final.
- `assets/gameplay/`: recortes normalizados e feed sincronizado. `assets/memes/`: memes preparados e interfaces próprias.
- `acting_cues.json`, `face_cues.json`, `source_manifest.json`: atuação, trocas de rosto, fontes, hashes e intervalos selecionados.
- `scene_validation*.json`, `export_validation*.json`: verificações de malha, rosto, apoio, braços, áudio e arquivos finais.
- [Mesa reutilizável](../../../../assets/cenarios/mesa_redacao/): cenário genérico sem personagem, voz ou mídias do pacote.

## Visual e reprodução

Render nativo 360×640 / 640×360; ampliação inteira 3× por vizinho mais próximo. Precisão reduzida nas bordas com proteção das costuras do rosto, texturas Closest, corpo endereçado em 128 px, geometria facetada, quantização RGB de 5 bits e Bayer fixo 4×4. Sem blur, glitch ou luz piscando. Interfaces verticais têm layout próprio, mantendo os textos de cena legíveis. Não há legendas da narração embutidas.

Na raiz do repositório, com Blender 4.3, FFmpeg, NumPy e Pillow:

```sh
blender -b -t 2 --python-exit-code 1 --python shorts/008-personagens-que-a-internet-estragou/production/05-vaporeon/build_short.py
blender -b shorts/008-personagens-que-a-internet-estragou/production/05-vaporeon/output/Dery_Vaporeon.blend -t 1 --python-exit-code 1 --python shorts/008-personagens-que-a-internet-estragou/production/05-vaporeon/verify_scene.py
python shorts/008-personagens-que-a-internet-estragou/production/05-vaporeon/export_short.py
python shorts/008-personagens-que-a-internet-estragou/production/05-vaporeon/verify_export.py
```

Para o horizontal, adicionar `-- --wide` aos comandos Blender e `--wide` aos scripts Python; carregar `Dery_Vaporeon_Master_16x9.blend` na verificação. `--resume` retoma quadros completos e `--encode-only` codifica os já existentes. O padrão renderiza novamente os planos 3D. Usar um formato por vez com dois threads; gameplay, imagens e gráficos entram diretamente na montagem.

`prepare_assets.py` requer o inventário privado e os originais restaurados. As mídias preparadas necessárias aos projetos e ao render já ficam versionadas. Baixar a pasta inteira, pois áudio e filmes usam caminhos relativos. ZIP, renders intermediários, backups e referência pessoal permanecem fora do Git.
