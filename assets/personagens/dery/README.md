# Personagem Dery

Modelo e texturas originais enviados pelo usuário para uso nos shorts.

**Modelo mais recente em avaliação:** [v11 — contorno pela marcação vermelha](rig_ps1_v2/contorno_marcado_v11/). Segue a indicação posterior do usuário para uma base de mandíbula mais reta e quina definida no pescoço, com encaixe de textura corrigido e as dez expressões preservadas.

**Base atual da atualização:** [versão v3](rig_ps1_v2/texturas/rosto_neutro_v3/), retomada por preferência do usuário após rejeitar todas as texturas da v4. Usar o conjunto completo de materiais da v3, com o encaixe ampliado do rosto e a franja texturizada. A v4 fica apenas no histórico. A escolha da base não confirma aprovação integral do modelo nem autoriza iniciar expressões. Os modelos e episódios anteriores permanecem preservados.

**Refino em avaliação:** [v5 sobre as mesmas texturas da v3](rig_ps1_v2/texturas/refino_v3_v5/), solicitado em seguida para melhorar o acabamento existente. Preserva os PNGs e aplica apenas amostragem e nitidez suaves nos materiais; não troca as pinturas ou as cores da roupa.

**Última adição ao novo modelo:** [M amarelo no peito — v6](rig_ps1_v2/texturas/camiseta_m_v6/), aplicado à camiseta da v5, com logo original e estampa pixelizada. Mantém rosto, franja, jeans e demais texturas.

**Contorno facial em avaliação:** [v7](rig_ps1_v2/formato_rosto_v7/), ajuste reversível de mandíbula/queixo após o usuário apontar diferença no formato do rosto. Preserva o visual da v6 e apresenta comparação de frente e três quartos.

**Encaixe facial atualizado:** [v8](rig_ps1_v2/texturas/encaixe_rosto_v8/), solicitado após ajustar o contorno. Reposiciona suavemente o mesmo desenho neutro na cabeça v7, com UV separado, preservando os pixels originais e a geometria. Inclui comparação e Blender; aguarda avaliação.

**Novo teste autorizado de expressões:** [dez rostos PS1 aplicados à base v8](rig_ps1_v2/expressoes_v1/), com PNGs 128×128, neutro original preservado, seletor `PS1_face_id` e troca seca no Blender. Inclui prancha de prévias e biblioteca própria para o novo UV/rig. Não aplicar automaticamente a biblioteca antiga de 31 rostos a esta base.

**Roupa atual:** [camiseta preta com M amarelo do Massacote Games no peito](roupas/camiseta_preta/), mantendo o corte e a geometria originais. Aplicar a troca de material ao reutilizar cenas antigas.

O mesmo procedimento inclui a limpeza das manchas na pele, da iluminação colorida antiga e das transições entre pele e mangas, preservando o rosto desenhado e a malha original.

- `Dery.glb`: corpo, cabeça e rig de 72 ossos; inclui 23 ações.
- `Dery_Material_Diffuse.png`: textura de cor original.
- `Dery_Material_Normal.png`: mapa normal original.
- `Dery_texture_pbr_20250901.png`: textura adicional fornecida no pacote.

Cada short mantém suas animações, expressões e arquivos de trabalho na própria pasta. O GLB original permanece preservado aqui para reutilização.

- [Biblioteca compartilhada de 12 rostos PS1 e controlador Blender](expressions_ps1/): PNGs pré-desenhados, com troca instantânea de expressão, para reutilizar entre episódios.
- [Biblioteca ampliada de 31 rostos PS1](expressions_ps1/v2/), com o encaixe de olhos/boca e a correção de olheiras revisados.
- [Precisão PS1 sem fissuras no rosto](ps1_precision.py): usar `add_safe_precision` nos próximos renders. O deslocamento é independente das normais, preserva vértices coincidentes e protege o centro do rosto. Mantém os UVs e os 31 desenhos existentes. A validação do episódio 006 encontrou separação zero nas poses verificadas.
