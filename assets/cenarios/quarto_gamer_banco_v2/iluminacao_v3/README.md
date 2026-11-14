# Quarto — luz ciano/roxa, sem fone

Atualização solicitada pelo usuário: manter o quarto novo, recuperar a atmosfera do antigo e retirar o fone cinza da mesa.

- [Prévia 16:9](Previa_Luz_16x9.png) e [9:16](Previa_Luz_9x16.png).
- [Antes e depois, com a mesma câmera e pose](Antes_Depois.png).
- [Mesa sem o fone](Previa_Mesa_Sem_Fone.png).
- [Base editável com Dery sentado](Dery_Quarto_Luz_v3_Sem_Fone.blend).

A iluminação do cenário foi recalculada em `PS1Light`, com ciano à esquerda, violeta à direita e luz principal suave. O Dery recebe uma camada de luz por vértice sobre os materiais existentes. Texturas, UVs, malhas, pesos, 131 expressões, pose de apoio nas coxas, cadeira e curvas de animação permanecem preservados. Somente o objeto `Fone de ouvido` foi removido; caixas de som e cabo do chão continuam no lugar.

Esta é a base selecionada para as próximas produções autorizadas. A alteração visual ainda aguarda a avaliação do usuário. Não foram renderizados novamente os shorts nem o vídeo longo; a base anterior permanece intacta.

## Reutilização

Abra este Blender para preparar a próxima produção. A câmera principal é `TESTE | câmera animada`; `TESTE | jogo no CRT` fornece a vista da mesa. A atuação de oito segundos é uma referência de contato, não um ciclo para repetir sob outra fala: adaptar gestos e faces à nova voz.

Alternativamente, após carregar a base anterior e antes de adicionar novos inserts, importe `aplicar.py` e execute `apply(bpy.context.scene)`. O módulo recalcula as cores da sala e substitui as luzes de referência; não o aplique depois de acrescentar a iluminação própria de uma gag. A camada de luz do avatar é estática, calculada sobre a pose avaliada, como a iluminação PSX já usada no projeto.

Manter gameplay, memes e fotos limpos, inclusive dentro do CRT, compondo a mídia depois do passe PSX. O monitor neutro aparece somente no detalhe de avaliação; o Blender mantém o nó de mídia original para substituição na próxima produção. Não aplicar dithering ou posterização à mídia. As prévias foram renderizadas no Blender e ampliadas com Nearest; não usam blur, glitch ou tremido global.

Reprodução: `blender -b -t 2 --python-exit-code 1 --python assets/cenarios/quarto_gamer_banco_v2/iluminacao_v3/montar.py`, com a base anterior disponível pelo Git LFS. São apenas três imagens, não um novo vídeo. `alteracoes.json` registra as fontes e a preservação de geometria/UVs/pose; `validacao_reabertura.json` confere o arquivo salvo.
