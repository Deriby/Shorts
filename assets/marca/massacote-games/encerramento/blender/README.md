# Massacote Games — encerramento com Dery

Vinheta reutilizável de 4 segundos, vertical 9:16, com fundo amarelo e marca em 3D grafite. O Dery carrega o M acima da cabeça, faz pose, troca abruptamente a expressão e perde o equilíbrio. Ele, a marca e os textos saem pela direita. O começo e o final ficam vazios.

## Arquivos

- [Vídeo 1080 × 1920, 24 fps, com efeitos sonoros](output/Massacote_Outro_Dery_4s_9x16.mp4).
- [Projeto Blender com texturas e fonte empacotadas](output/Massacote_Outro_Dery_4s.blend).
- [Efeitos sonoros originais, sem fala ou música](output/efeitos_originais_4s.wav).
- [Construção e animação](build_outro.py).
- [Exportação e geração dos efeitos](export_outro.py).

Reutiliza o modelo, rig e os rostos PNG revisados do Dery. Expressões com mudanças instantâneas, sem interpolação de rosto: nervoso, orgulhoso, piscada, susto e gritando. O arquivo `face_cues.json` registra as trocas.

O M é uma malha extrudada com silhueta angular, bevel de um segmento e sombreamento por planos. Os textos também têm extrusão geométrica. O personagem conserva a textura original com filtragem Closest, o atlas de 31 expressões e a precisão de contorno em espaço da câmera. Sombras de contato em polígonos seguem a estética do console.

## Reprodução

Na raiz do repositório, com Blender 4.3 e FFmpeg instalados:

```sh
blender -b --threads 4 --python assets/marca/massacote-games/encerramento/blender/build_outro.py -- --render-all
python assets/marca/massacote-games/encerramento/blender/export_outro.py
```

Render nativo 432 × 768 e ampliação para 1080 × 1920 com vizinho mais próximo para manter bordas definidas. O script de construção reutiliza o personagem do projeto `005-gta-postal2`; o `.blend` entregue é autônomo, com recursos usados empacotados. Sem `--render-all`, o script cria seis quadros de inspeção.
