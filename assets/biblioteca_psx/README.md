# Banco PSX recebido do usuário

Recebido em 11/11/2026 para **reaproveitar modelos, props, cenários e texturas nas próximas animações**, consultando este banco antes de criar recursos do zero.

- [Pacote original no Google Drive](https://drive.google.com/file/d/1M4MgjcMoNM-OW6gAXcxCzV2zRHpW7Bsq/view?usp=sharing): `Banco 3D para vídeos.zip`.
- [Registro de recebimento, integridade, formatos e pastas](recebimento.json).
- Download: 692.858.658 bytes; conteúdo extraído: 958.331.850 bytes.
- 26 conjuntos, 3.703 arquivos. Contagens incluem versões do mesmo modelo em formatos diferentes; não representam 3.703 modelos únicos.

## Onde estão os arquivos

Neste ambiente, os originais extraídos estão em `assets/biblioteca_psx/originais/Banco 3D para vídeos/`. O ZIP intacto permanece em `/workspace/attachments/biblioteca-psx/Banco_3D_para_videos.zip`.

O cache de originais fica fora do Git; este registro e o link de origem são versionados. Ao usar outro ambiente, obter o pacote do Drive e extraí-lo em `assets/biblioteca_psx/originais/`, preservando a estrutura interna. Não presumir que os arquivos brutos acompanham um clone do repositório.

## Conjuntos disponíveis

| Uso | Pastas do pacote |
| --- | --- |
| Casas e interiores | `House`, `Quequis_House`, `Trailer_Park` |
| Comércio e alimentação | `6twelve`, `DINER`, `Gas_station`, `Tacos` |
| Rua, transporte e escritório | `URBAN`, `Bus_stop`, `Metro_PSX`, `OFFICE` |
| Carros | `PSX_Style_Cars_by_GGBot_(August2023)`, `Retro Car1.0`, `Suv`, `Taxi 01` |
| Natureza | `Retro Tree Pack v1.0`, `retro_nature_pack`, `tree_pack_1.1` |
| Objetos variados | `LowPolyAssetPack_Free`, `RetroModelPack`, `PSX Kitchen Props Pack`, `PS1BottlesAssetPackV1.1`, `PSX firearms basic kit` |
| Temáticos e caixa de jogo | `Christmas`, `halloween`, `Free_PSX_Case_Template` |

Há arquivos FBX, GLB, OBJ/MTL, DAE e 62 arquivos Blender, além de texturas PNG/JPG. Existem também pacotes Unity e arquivos Unreal; escolher os formatos de intercâmbio disponíveis para trabalhar no Blender. A extração verificou os CRCs de todos os arquivos. As importações e materiais ainda não foram testados no Blender.

## Uso nas produções

1. Escolher pelo roteiro os objetos e cenários adequados e trabalhar numa cópia; manter os originais intactos.
2. Conferir escala, UVs e caminhos de texturas ao importar. O `LowPolyAssetPack_Free` inclui instrução para religar `MasterMaterial1px` caso a textura falte.
3. Preservar os avisos e créditos próprios de cada conjunto. As permissões variam por pacote; não redistribuir o banco bruto nem atribuir uma licença única a todos os arquivos.
4. Integrar apenas os recursos utilizados à produção, conforme seus avisos. Manter a direção PS1 aprovada: texturas pequenas e nítidas com Closest, geometria angular e movimento coerente; sem borrão, glitch ou oscilação artificial da tela.

O recebimento deste banco não inicia uma nova animação nem altera o projeto Filmora atual. A proposta de automação da seção 5 do resumo anterior continua descartada.
