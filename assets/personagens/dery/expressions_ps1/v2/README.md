# Dery — biblioteca de 31 rostos PS1

**31 expressões desenhadas em PNG**, com amostragem `Closest` e troca instantânea por índice. As doze expressões anteriores foram preservadas; há dezenove desenhos novos. A biblioteca não depende de geração de imagem para os próximos episódios.

- [Folha com os 31 desenhos](Dery_31_Expressoes.png).
- [Índices e nomes das expressões](expressions.json).
- [Atlas 8 × 4, 1024 × 512 pixels](atlas_31_8x4.png).

Cada rosto tem 128 × 128 pixels. A última célula do atlas serve de preenchimento e não é contada como expressão. As fontes desenhadas e os recortes registrados ficam em `sources/` e `prepare_library.py`; as células foram alinhadas pelos olhos, nariz, bigode e boca.

## Expressões

0 neutro; 1 falando; 2 sorriso; 3 risada; 4 deboche; 5 susto; 6 sem reação; 7 bravo; 8 triste; 9 sem graça; 10 piscando; 11 deboche falando; 12 explicando; 13 orgulhoso; 14 gargalhada; 15 olhando à esquerda; 16 sarcasmo falando; 17 piscadinha; 18 constrangido; 19 ofendido; 20 pensativo; 21 gritando; 22 confuso; 23 sério; 24 sério falando; 25 nervoso; 26 impressionado; 27 contente; 28 língua de fora; 29 nojo; 30 chorando.

## Usar no Blender

O projeto R5 do short 004 já contém o modelo com a biblioteca instalada. Selecione `DERY | animated character` e altere a propriedade personalizada **`PS1_face_id` de 0 a 30**. Insira chaves com interpolação **Constant** para trocar o desenho inteiro no quadro marcado.

`setup_faces31.install(avatar)` instala o material. Se a mesma malha unida do Dery ainda não tiver o encaixe revisado, o instalador prepara os UVs e aplica `fit_mesh.py`. É necessário o atributo de iluminação `PS1Lighting` preparado pela cena, como nos projetos 003/004. O sistema mantém o nariz original, o espaçamento de olhos ajustado no teste, as áreas de olhos e boca separadas e a correção localizada de olheiras. A expressão de choro preserva as lágrimas.

As antigas deformações faciais ficam desativadas. Os desenhos mudam no material; o movimento de braços, cabeça e corpo continua no rig.

Para reconstruir apenas os PNGs e o atlas a partir dos desenhos já salvos:

```bash
python assets/personagens/dery/expressions_ps1/v2/prepare_library.py
```
