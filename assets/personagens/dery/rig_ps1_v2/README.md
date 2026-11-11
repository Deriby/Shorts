# Dery / Massacote — novo rig, base do rosto PS1

Base recebida em `Dery Rig.zip`, em 11/11/2026. A etapa inicial simplificou a anatomia do rosto seguindo o exemplo de Silent Hill fornecido pelo usuário: nariz e contorno em geometria simples, com olhos e boca desenhados nas texturas.

**Base atual retomada: [versão v3](texturas/rosto_neutro_v3/).** O usuário rejeitou todas as texturas da v4 e preferiu o conjunto anterior completo. Usar o [Blender v3](texturas/rosto_neutro_v3/Dery_Referencia_Sem_Mochila_v3.blend), que permaneceu intacto, com o encaixe do rosto e a franja texturizada. O [registro da versão atual](versao_atual.json) identifica arquivo, hash e escopo da escolha. A [v4](texturas/estilo_ps1_v4/) permanece apenas no histórico; não reaplicar suas pinturas ou paletas. A biblioteca de expressões continua dependente do retorno do usuário.

**Nova proposta de acabamento:** [refino v5](texturas/refino_v3_v5/), solicitado para melhorar as texturas existentes, preservando a pintura e o jeans da v3. Os PNGs permanecem intactos; o ajuste ocorre na amostragem e no realce local dos materiais. A v3 continua como base selecionada até o retorno do usuário.

**Adição solicitada em seguida:** [camiseta com M amarelo, v6](texturas/camiseta_m_v6/), sobre o acabamento v5. Aplica a logo original no centro do peito e mantém o restante do visual. O Blender e as prévias estão na pasta; as versões anteriores permanecem preservadas.

**Proposta de contorno facial:** [v7](formato_rosto_v7/), após o usuário apontar que o formato do rosto também difere do seu. Testa mandíbula mais estreita e base do queixo menos reta por uma shape key reversível, mantendo as texturas da v6. O comparativo frontal e em três quartos acompanha o Blender; a semelhança aguarda avaliação.

## Arquivos

- [Dery_Rig_PS1_Base.blend](Dery_Rig_PS1_Base.blend): nova base editável, com imagens originais incorporadas e o rig preservado.
- [Frente](Previa_frente.png), [perfil](Previa_perfil.png) e [três quartos](Previa_tres_quartos.png): inspeção da geometria em material cinza, sem textura de expressão. Não representam a aparência final do personagem.
- [UV_Rosto_PS1.svg](UV_Rosto_PS1.svg): guia do UV frontal para a etapa de pintura; não é uma expressão.
- [adaptar_rosto.py](adaptar_rosto.py): reconstrução da base a partir do FBX fornecido.
- [adaptacao.json](adaptacao.json) e [validacao.json](validacao.json): alterações e verificações realizadas.
- [recebimento.json](recebimento.json): origem e hashes dos arquivos preservados em `original/`.

## Alterações

A região frontal que continha 1.368 triângulos foi substituída por uma superfície de 242 triângulos. As cavidades e relevos de olhos e boca foram removidos dessa área; o nariz conserva um volume pequeno e angular. A transição para testa e bochechas foi ajustada, mantendo a malha soldada e o contorno inferior do queixo. A escala do conjunto foi normalizada para aproximadamente 1,82 m por um pai comum, sem alterar a proporção entre malha e esqueleto.

O corpo abaixo do pescoço mantém suas posições originais. O rig mantém os 71 ossos e a ação `Armature|Default` do FBX. O modelo completo ainda tem 48.874 triângulos; esta etapa simplifica o rosto, sem fazer uma otimização completa do corpo para o orçamento de polígonos de um PS1.

O UV `DeryFaceUV` projeta a região frontal numa ilha contínua, incluindo o nariz. O material `ROSTO | BASE NEUTRA` tem um nó `EXPRESSAO_PNG` reservado, com interpolação **Closest** e UV explícito. O nó ainda não possui imagem nem ligação à cor; a cor neutra mantém a base utilizável até a pintura. No próximo chat, atribuir o PNG de expressão e ligar sua cor ao material, preservando a troca seca entre desenhos.

O UV de renderização do corpo continua sendo `Channel0`. As texturas originais do corpo não foram redesenhadas. As prévias usam material cinza para mostrar o volume sem a aparência antiga escondê-lo.

## Verificação

Todas as faces são triângulos; todas as arestas pertencem a duas faces, sem bordas abertas. Os pesos estão normalizados, o UV frontal está dentro da imagem e as texturas originais estão incorporadas ao Blender. Foram inspecionadas viradas de cabeça de −30°, 0° e +30°, sem coordenadas inválidas ou triângulos faciais degenerados. Essas verificações não substituem a revisão da atuação e dos novos desenhos na próxima produção.

Não aplicar automaticamente o controlador antigo de 31 rostos: ele usa outro encaixe, UV e rig. Esta base mantém o original recebido e os episódios anteriores separados; os roteiros de produção antigos não foram migrados.

## Reproduzir

Com Blender 4.3.2:

```bash
blender -b --disable-autoexec -t 4 --python assets/personagens/dery/rig_ps1_v2/adaptar_rosto.py -- --output /tmp/dery_rosto_ps1
```

O comando importa `original/autorig_actor.fbx`, preserva suas ações, prepara geometria e UV, gera três imagens e salva uma nova base no diretório de saída. Não utiliza os cenários ou vídeos de outros episódios.
