# Esse jogo destruiu seu criador — produção

- [Short vertical](output/Esse_jogo_destruiu_seu_criador_9x16.mp4).
- [Projeto Blender](output/Dery_Mizzurna_Falls.blend).
- [Voz original preservada](assets/voz/voz_original.mp3).
- [Ordem e tempos das tomadas](timeline.json).
- [Duração e hash da gravação](audio.json).
- [Diagnóstico e correção do rosto](face_fix.json).
- [Validação das poses e recursos](scene_validation.json).
- [Validação do vídeo exportado](export_validation.json).

Entrega 9:16, 1080 × 1920, 24 fps, com 1.214 quadros e 50,58 segundos. A voz enviada tem 49,8139 segundos após decodificação; o final reserva aproximadamente 0,77 s para a reação. O MP3 original é preservado byte a byte. Não há alteração de velocidade ou tom.

## Montagem e atuação

A gravação real determina os cortes, incluindo a forma como o usuário pronunciou a reação do PS1. O alinhamento usa reconhecimento local de segmentos e pausas medidas; erros fonéticos do reconhecimento não são transformados em falas novas. O plano segue o texto corrigido, com cidade e investigação, ambição, carros, rotinas, limitações do console, limbo, saída do diretor e piada final do CLT.

O quarto, a cadeira, os materiais, a rig e as 31 expressões vêm da base revisada do episódio 004. Os gestos diferenciam explicação, tamanho do console, volante, impaciência e afastamento do crachá. As expressões PNG trocam com chaves CONSTANT. O quadril permanece estável na cadeira.

O limbo é uma vinheta ilustrativa do Dery em uma plataforma amarela sobre um fundo grafite. A queda move o personagem inteiro por uma curva controlada; os ossos não se desarticulam. No final, um detalhe do crachá permite ler CLT durante o movimento, seguido da reação relaxada do Dery.

O trailer sem legendas inglesas fornece a cidade e os moradores, tanto em cortes diretos quanto dentro do monitor. O outro anexo foi usado como referência narrativa. A reprodução no PC tem avanço de quadros e auto-refresh. As legendas da narração ficam a cargo da edição do usuário.

## Correção do rosto

A precisão PS1 anterior usava normais na intensidade do deslocamento. Vértices coincidentes em costuras podiam receber intensidades diferentes e abrir fissuras. O diagnóstico encontrou 370 grupos de vértices coincidentes na face, com separação máxima de 1,92 mm e 131 grupos acima de 0,5 mm.

A [correção compartilhada](../../../assets/personagens/dery/ps1_precision.py) usa um atributo POINT derivado da posição original. Vértices coincidentes recebem o mesmo deslocamento, e o centro do rosto fica protegido. O teste inicial encontrou separação zero; a validação do projeto repete a verificação em três poses. UVs, desenhos, espaçamento dos olhos e materiais aprovados são preservados.

## Render e reprodução

O render 3D nativo é 360 × 640, ampliado por fator inteiro de três para 1080 × 1920 com vizinho mais próximo e redução discreta de cores. Não há filtro de desfoque. São 944 quadros de Blender e 270 de cortes diretos do trailer. Dois processos de Blender com dois threads cada produzem partições distintas de quadros a 24 fps. A paleta usa uma LUT, evitando o custo de expressões por pixel no exportador.

Na raiz do repositório:

```sh
python shorts/006-mizzurna-falls/production/prepare_assets.py
blender -b -t 2 --python-exit-code 1 --python shorts/006-mizzurna-falls/production/build_short.py
python shorts/006-mizzurna-falls/production/export_short.py
```

O `.blend` contém as texturas utilizadas empacotadas. O vídeo do monitor e o áudio estão versionados e ligados por caminhos relativos. O projeto mantém marcadores por tomada; os cortes diretos de gameplay são reunidos pelo exportador. Frames intermediários e backups ficam fora do Git.
