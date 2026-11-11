# Rosto neutro — proposta PS1 v2

O usuário pediu uma textura baseada na sua aparência e reforçou a referência dos modelos dos primeiros Silent Hill. Rejeitou a primeira aplicação pelo acabamento moderno e pelos recortes no rosto. Esta versão é uma nova proposta, **ainda sem aprovação do usuário**. Não iniciar a biblioteca de expressões antes do seu retorno.

## Arquivos

- [Prévia de frente](Previa_Frente.png), [três quartos](Previa_Tres_Quartos.png) e [perfil](Previa_Perfil.png).
- [Rosto_Neutro_64.png](Rosto_Neutro_64.png): textura neutra nativa de 64×64 pixels.
- [Dery_Rosto_PS1_Neutro_v2.blend](Dery_Rosto_PS1_Neutro_v2.blend): modelo com a proposta aplicada e texturas incorporadas.
- `Desenho_Fonte.png`: desenho gerado, preservado antes da conversão de formato para o asset.
- `Corpo_Atlas_256.png`: cópia do atlas original preparada em baixa resolução, preservando o original de alta resolução no rig-base.
- [aplicar.py](aplicar.py), [geracao.json](geracao.json) e [aplicacao.json](aplicacao.json): preparação reproduzível e registro da proposta.

## Aplicação

A textura foi redesenhada com blocos de cor maiores e menos detalhe. A preparação no Blender usa 64×64 pixels no rosto, 256×256 no atlas do corpo, canais de cor com precisão de cinco bits e interpolação Closest. O shader multiplica a textura por iluminação Gouraud gravada em cores de vértice/canto e usa saída de emissão; não usa brilho PBR, luzes suaves ou desfoque da tela.

O UV `DeryPS1UV` combina as coordenadas do corpo com a projeção frontal do rosto. A área de pele inclui as bochechas laterais e o pescoço. O material mantém os pixels do boné e da gola a partir do UV original `Channel0`, com uma chave de cor de pele; as áreas de olhos, boca e queixo têm proteção para impedir que os desenhos antigos reapareçam. Não há mistura com a expressão antiga no centro do rosto.

A geometria e os 71 ossos permanecem iguais ao rig-base; o modelo completo continua com 48.874 triângulos. Esta etapa altera texturas, UV e materiais para avaliação visual, sem fazer uma retopologia do corpo nem simular um emulador de PS1.

As fotos pessoais não foram copiadas para o repositório. A tentativa rejeitada foi preservada localmente em `/workspace/attachments/rascunhos_superados/rosto_neutro_v1_rejeitado/` e não integra esta entrega.

## Reproduzir

```bash
blender -b --disable-autoexec -t 4 --python assets/personagens/dery/rig_ps1_v2/texturas/rosto_neutro_v2/aplicar.py
```

O comando lê o rig-base intacto, prepara as texturas nativas, reconstrói o UV/material de conferência e gera as três vistas e o Blender desta pasta. Não modifica o rig-base ou os vídeos anteriores.
