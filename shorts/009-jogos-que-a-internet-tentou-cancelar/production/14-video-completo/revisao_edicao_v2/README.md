# Edição revisada — zooms, keyframes e transições

O usuário sentiu falta do movimento de edição do primeiro longo e pediu uma montagem mais dinâmica. Esta revisão altera somente a edição nativa do último projeto completo, preservando 9min21,367s, os 296 clipes, os 97 recursos e todas as trilhas de áudio.

- [WFP atual, 1,3 MB](../output/Filmora/Massacote_Completo_Editado.wfp): salve ao lado da pasta `midias` anterior.
- [Pacote completo com as mesmas mídias](../output/Massacote_Completo_Editado_Filmora.zip).
- [Comparação de enquadramentos](Previa_Enquadramentos.jpg), apenas a transformação básica.
- [Plano dos movimentos](edicao.json) e [validação](validacao.json).

Há 112 clipes com animação nativa: aproximações progressivas, zooms curtos nas reações, abertura rápida com assentamento e afastamentos. As curvas ficam editáveis em escala e posição, no tempo da mídia-fonte. O movimento segue as intenções registradas nos roteiros, com amplitude maior nos planos abertos do Dery e menor nos closes. As onze vinhetas mantêm imagem e título em camadas com entrada/assentamento/saída; a faixa da imagem foi corrigida de áudio para vídeo para que o PNG apareça no render nativo.

As 60 transições vêm dos registros reais do WFP final do usuário: **Basic Zoom In, Warp Zoom 6, Fast Bounce, SwingLeft e SwingRight**. Aplicadas em mudanças de ideia e passagem das vinhetas, sem novos cortes. As gags mantêm entrada/saída secas; gameplay, interfaces, textos e fotos preservam o enquadramento anterior. Não foram acrescentados filtros de mídia, legendas ou tremido global. Sons, músicas, vozes e ganhos são idênticos.

Fonte de estilo: `008/production/20-edicao-final-usuario/Massacote_EDICAO_FINAL_USUARIO.wfp`. Fonte de montagem: `output/Filmora/Massacote_Completo.wfp`. Ambos permanecem intactos. O quarto com luz nova e sem fone foi aprovado para produções futuras; esta edição usa os vídeos prontos, sem novo render 3D.

**O MP4 anterior não contém esta revisão.** A entrega atual é o WFP editável; exporte-o no Filmora. O aplicativo proprietário não está disponível neste Linux. Foram conferidos estrutura/registro nativo, referências, tempos, velocidade 1×, ausência de bordas vazias, escala uniforme e enquadramentos de 13 amostras. A prancha não simula os plugins ou transições e não comprova a abertura no aplicativo.

Reprodução: `revisar.py`, `verificar.py`, `conferir_quadros.py`, `empacotar.py`. Não executar o empacotador antigo como se fosse esta versão. O pacote contém somente o novo WFP e as mídias/fontes necessárias; para quem já baixou o anterior, o WFP avulso basta.
