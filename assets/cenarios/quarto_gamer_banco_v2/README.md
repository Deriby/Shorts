# Quarto gamer PS1 — montagem com o banco 3D

**Teste posterior autorizado:** [cena de 6 segundos com o Dery original, voz e gameplay de Driver](teste_short/), para avaliar o uso em shorts. O cenário-base desta pasta continua intacto; a cópia animada está separada.

Novo cenário montado a pedido do usuário, reaproveitando os modelos e texturas de `assets/biblioteca_psx/`. O quarto anterior, os vídeos e o personagem Dery permanecem preservados. Esta versão está pronta para avaliação visual e reutilização; não foi aplicada automaticamente aos shorts existentes.

- [Prévia do quarto completo](Previa_Quarto_Completo.png).
- [Enquadramento vertical para shorts](Previa_Quarto_9x16.png).
- [Mesa e computador CRT](Previa_Mesa_CRT.png).
- [Blender editável com texturas incorporadas](Quarto_Gamer_Banco_PS1.blend).
- [Fontes utilizadas e posições](fontes_e_montagem.json) e [validação](validacao.json).

## Montagem

Mesa em L, computador bege com monitor de tubo, teclado/mouse, cadeira, luminária, rádio, fone, TV antiga, estante com consoles/controles/jogos/CDs, cama, tapete, janela, porta, pizza e garrafa. A marca M reaproveita a logo já aprovada do canal.

Foram utilizados modelos de **OFFICE, House, LowPolyAssetPack_Free e PSX Kitchen Props Pack**, além de arte do **Free_PSX_Case_Template**. A cama é o `bed_02` do House, extraído do FBX, orientado e escalado para o quarto. A ligação de opacidade incorreta desse FBX foi removida no material da cópia para manter o colchão opaco. Nenhum arquivo do banco original foi alterado. A arquitetura simples do set usa texturas de reboco, madeira, teto e janela do banco. Somente os recursos utilizados foram incorporados ao Blender, sem redistribuir o banco bruto.

O visual usa texturas com **Closest**, luz colorida difusa gravada nos vértices/cantos da malha, três câmeras e precisão de geometria por câmera. A deformação foi reduzida nos props e desligada nas superfícies próximas/coplanares para evitar o piso atravessar o tapete e artefatos nos decals. As prévias são renders reais do Blender em 480×270 ou 270×480, com RGB555, dithering ordenado discreto e ampliação inteira por Nearest. Não há borrão, glitch ou tremido da imagem inteira. O cenário completo conserva o detalhamento dos modelos importados; não foi limitado ao orçamento total de polígonos de um PS1 real.

## Reutilização

A coleção principal é `Massacote | quarto gamer do banco`. O arquivo não contém avatar/rig. O empty `DERY | posição de referência` marca o assento para posicionar uma cópia do personagem original numa produção futura.

O PC tem a superfície `Tela do PC | substituir por vídeo`, com UV ajustado à tela do modelo e material próprio **`DISPLAY | PC | trocar mídia`**. A troca de mídia desse material não altera o M da parede. Conectar a imagem/vídeo da nova produção ao nó de imagem, preservando o UV e Closest.

As câmeras são `01 | Quarto completo`, `02 | Enquadramento para shorts` e `03 | Computador e mesa`. Cada uma tem seu grupo `Quarto | precisão PS1 | …`: ao mudar de câmera para renderizar, atribuir o grupo correspondente aos modificadores `PS1 | bordas por câmera` da coleção e usar a proporção correspondente. A função `choose` em `montar_quarto.py` faz essa configuração durante a geração das prévias. O teto fica oculto somente na apresentação geral e visível nas duas câmeras de interior. O arquivo salvo abre na visão geral.

`montar_quarto.py` reproduz a montagem no Blender 4.3.2 com o cache do banco disponível; `exportar_previas.py` finaliza os PNGs; `verificar_quarto.py` reabre o arquivo e confere imagens incorporadas, UVs, coordenadas, proporção da cama, materiais separados, integridade dos modelos de origem e preservação do Dery atual. Nenhum vídeo foi renderizado.

## Fontes e avisos

Banco recebido do usuário: [registro da biblioteca](../../biblioteca_psx/README.md). O manifesto registra os caminhos e hashes dos modelos utilizados. As permissões e os créditos variam por conjunto; não atribuir a licença de um deles ao restante.

O aviso do **LowPolyAssetPack_Free** declara CC0 1.0 Universal e foi preservado em [creditos/LowPolyAssetPack_NOTES.txt](creditos/LowPolyAssetPack_NOTES.txt). O readme do template de caixa credita **sodaraptor / @sodaraptor_dev**, preservado em [creditos/PSX_Case_Readme.txt](creditos/PSX_Case_Readme.txt). Os demais conjuntos são identificados pelos nomes e caminhos presentes no pacote fornecido.
