# Massacote Tube — 30 poses com óculos 3D

Novo visual aprovado pelo usuário: cartoon compacto, óculos vermelho/azul opacos, boné/jaqueta roxos com vermelho, bigode e brasão M. As trinta poses foram desenhadas com image_gen, registradas pela posição das lentes e montadas com a mesma cabeça aprovada. A boca continua sempre escondida; não existe camada de olhos para animar.

Extraia o pacote completo e abra **galeria.html** para buscar poses e baixar PNGs. `Previa_30_Poses.jpg` mostra todas; `previas/Prancha_1.jpg` a `Prancha_3.jpg` mostram dez por vez.

- `poses/`: trinta PNGs completos e transparentes, prontos para edição.
- `camadas/`: trinta corpos, cabeça compartilhada, bigode em repouso/dois estados técnicos de fala e mãos em primeiro plano quando necessárias.
- `fontes/`: artes originais geradas preservadas no GitHub; não são necessárias para abrir a galeria ou usar os PNGs, por isso ficam fora do ZIP de uso.
- `catalogo.json` e `catalogo.sqlite`: arquivos, gestos, categorias, hashes e ligações das camadas.

Todas as peças usam **2048×2048**. Não recorte o espaço transparente ao importar; ele preserva o alinhamento. Ordem de baixo para cima: **corpo da pose → cabeça sem bigode → bigode → frente**, quando houver. `cabeca_com_bigode.png` é alternativa fixa: use-a sozinha sobre o corpo, sem duplicar as duas camadas faciais. Pivôs no registro de encaixe.

Para fala, mova o bigode acompanhando a voz e as pausas; cabeça, lentes e bigode devem acompanhar o mesmo enquadramento. Os estados A/B são pequenas deformações do PNG original, não desenhos adicionais. As poses completas ficam iguais no repouso. A camada de baixo foi preparada com image_gen sem boca desenhada, evitando o bigode duplicado durante a atuação.

Gestos incluem apresentação, apontar em várias direções, joinhas, braços cruzados, dúvida, pare, ressalva, desespero, vitória, risada, vergonha, trama, T-rex, robô, pedido, apresentação lateral, cobrança de hora, maromba, aplauso, boas-vindas, pistolinhas e mãos se esfregando.

O modelo e o short anteriores continuam preservados. Esta biblioteca não inclui uma nova animação ou um novo WFP; a revisão do Sonic usa essas peças em uma produção separada. Downloads pelo GitHub.
