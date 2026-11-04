# Rostos PS1 do Dery

Biblioteca reutilizável com **12 rostos desenhados**, em PNG de **128 × 128**, e um atlas de **512 × 384**. Os rostos foram desenhados com base no Dery original; cada expressão é uma imagem completa diferente.

- [Ver as doze texturas](Dery_Expressoes_PS1.png).
- [Ver aplicadas no modelo e no cenário](../../../../shorts/004-crash-apelido/production/output/Dery_Expressoes_PS1_Aplicadas.png).
- [Atlas para o material](atlas_4x3.png).
- [Índices das expressões](expressions.json).

| ID | Expressão | PNG |
| --- | --- | --- |
| 0 | Neutro | [neutro.png](neutro.png) |
| 1 | Falando | [falando.png](falando.png) |
| 2 | Sorriso | [sorriso.png](sorriso.png) |
| 3 | Risada | [risada.png](risada.png) |
| 4 | Deboche | [deboche.png](deboche.png) |
| 5 | Susto | [susto.png](susto.png) |
| 6 | Sem reação | [sem_reacao.png](sem_reacao.png) |
| 7 | Bravo | [bravo.png](bravo.png) |
| 8 | Triste | [triste.png](triste.png) |
| 9 | Sem graça | [sem_graca.png](sem_graca.png) |
| 10 | Piscando | [piscando.png](piscando.png) |
| 11 | Deboche falando | [deboche_falando.png](deboche_falando.png) |

## Usar no Blender

O projeto R4 do episódio 004 já tem o sistema instalado. Selecione `DERY | animated character` e altere a propriedade personalizada `PS1_face_id` de 0 a 11. Essa propriedade escolhe uma célula do atlas no material `DERY | PS1 drawn face atlas`. Para animar, insira chaves nessa propriedade e configure a interpolação como **Constant**. A expressão troca inteira no quadro marcado, sem mistura ou deformação da malha.

Para instalar em outro episódio que use a mesma malha unida do Dery, importe `setup_faces.py` no Python do Blender e execute `install(avatar)`. O instalador cria o UV `DeryFacePS1`, a máscara frontal e o controlador de expressão; a iluminação usa o atributo `PS1Lighting` preparado pela cena. A calibração dos olhos, nariz e boca foi feita para a escala original do personagem. O GLB e as texturas originais permanecem intactos na pasta superior.

`atlas_source.png` preserva o desenho de origem. `prepare_atlas.py` extrai as doze células e gera o atlas e a folha de apresentação, sem recriar a arte. Não é necessário gerar imagens novamente para usar as expressões nos próximos vídeos.
