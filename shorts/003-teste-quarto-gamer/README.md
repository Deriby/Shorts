# Teste de formato — Massacote Games (5 segundos)

Prévia curta solicitada para avaliar Dery num quarto gamer com estética PS1, voz gerada e cortes do monitor para a reação do personagem. Este teste não representa um episódio completo nem define a voz definitiva do canal.

**Fala:** “Esse jogo roda liso. Quem está travando sou eu.”

| Tempo | Imagem |
| --- | --- |
| 0,00–0,92 s | Dery sentado no quarto, assistindo ao monitor. |
| 0,92–1,79 s | Corte para o vídeo rodando dentro da tela do computador. |
| 1,79–3,65 s | Corte para Dery, com gesto e movimento simples da boca acompanhando a voz. |
| 3,65–5,00 s | Dery trava como um NPC, com expressão de derrota. |

O monitor usa um trecho **ilustrativo de nossa produção anterior**, sem áudio. Ainda não foi fornecido um clipe de jogo para este teste. A proposta para os próximos vídeos continua sendo inserir o trecho do jogo correspondente ao que estiver sendo dito.

## Arquivos

- [Assistir à prévia com voz](production/output/Dery_Quarto_Gamer_5s.mp4)
- [Projeto editável no Blender](production/output/Dery_Quarto_Gamer_Teste.blend)
- [Voz provisória, com cinco segundos](production/assets/voz_teste.wav)
- [Construção da cena](production/build_scene.py)
- [Render e montagem](production/render_preview.py)

O modelo e a rig são os enviados pelo usuário. As expressões PNG vêm dos testes anteriores do Dery. O cenário contém mesa, monitor CRT, computador, teclado, cadeira, cama, prateleira e arte em pixels. Bordas com poucos pixels, texturas sem interpolação, cores quantizadas e uma grade de vértices dão o tratamento retrô. A cena é renderizada em 360 × 640 e ampliada com vizinho mais próximo para 1080 × 1920, a 24 fps. Não há legendas.

## Voz

Voz sintética brasileira genérica: Piper `pt_BR-faber-medium`, executada localmente com sherpa-onnx. Não é uma imitação ou clonagem da voz do usuário. A narração termina antes do fim, deixando uma pausa para a reação.

- [Modelo de voz oficial](https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-pt_BR-faber-medium.tar.bz2)
- [Model card e licença do conjunto de dados: CC0](production/assets/VOZ_MODELO_LICENCA.txt)

O arquivo do modelo de voz é uma dependência externa e não está duplicado no repositório. `make_voice.py` aceita os caminhos nas variáveis `DERY_TTS_PYTHON_PATH` e `DERY_TTS_MODEL_DIR`. A voz gerada está versionada para permitir renderizar a prévia sem reinstalar o sintetizador.

## Reproduzir

Requisitos: Blender 4.3 e FFmpeg no PATH. Obtenha os arquivos Git LFS ao clonar.

```bash
blender -b -t 4 --python shorts/003-teste-quarto-gamer/production/build_scene.py
python shorts/003-teste-quarto-gamer/production/render_preview.py
```

Renders individuais, backups e caches são ignorados pelo Git. A geração de boca usa apenas a energia do áudio; não é sincronização fonética detalhada.
