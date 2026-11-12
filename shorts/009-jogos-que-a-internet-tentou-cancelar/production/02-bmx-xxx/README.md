# BMX XXX — Jogos que a internet tentou cancelar

Segundo capítulo, com a voz e as mídias do pacote enviado pelo usuário. O roteiro da animação acompanha a gravação integral; não foi criada outra voz. [Plano por trechos](roteiro_animacao.md) e [fontes](fontes.md).

## Entregas

- `output/BMX_XXX_Cancelar_9x16.mp4`: short 1080×1920, 30 fps, 43,967 s.
- `output/BMX_XXX_Cancelar_16x9.mp4`: capítulo 1920×1080 para o futuro longo.
- `output/BMX_XXX_Filmora.zip`: **somente o projeto 9:16**, suas mídias e a fonte Baloo 2. Extraia o ZIP inteiro antes de abrir.
- `output/Filmora/BMX_XXX_9x16.wfp`: projeto avulso; precisa da pasta `midias/` do pacote.
- `output/Dery_BMX_XXX.blend`: atuação 3D editável. O CRT referencia `../assets/monitor/monitor_completo.mp4`; mantenha a organização da produção. As texturas estão incorporadas.
- `output/Previa_Cenas_9x16.jpg` e `output/Previa_Cenas_16x9.jpg`: contatos de quadros finais.

O WFP 16:9 reunirá todos os jogos apenas no final. A montagem do longo e o capítulo Bully não foram iniciados.

## Continuidade e edição

Reutiliza a cena e a projeção PSX da revisão R2 aprovada do GTA, com o Dery original, camiseta preta/M e texturas PNG. Novos gestos seguem esta voz, em vez dos tempos da gravação anterior. A vinheta do balcão conecta a ideia dos três X, a recusa das lojas e as rodas escapando. A comparação de plataformas fica em um único plano com cartões verticais, identificando as versões dos EUA.

O Filmora tem cortes, zooms com keyframes, títulos nativos, Glow nos títulos, voz inteira e SFX/trilha em faixas separadas. A base de vídeo é silenciosa. O render 3D e os inserts estão nessa base; o Blender permite alterar a atuação. O MP4 final foi composto neste ambiente, aproximando o estilo de edição aprovado. **Filmora não foi executado no Linux**: integridade e timing são checados por código, mas a abertura e os plugins nativos precisam ser conferidos na instalação do usuário.

## Reprodução da produção

1. `python prepare_assets.py` e `python prepare_edit.py` normalizam as mídias, planejam os trechos e montam o áudio. Requerem ffmpeg, NumPy e Pillow.
2. `blender -b -t 2 --python build_short.py` abre uma cópia da cena GTA R2, sem alterar a origem. `verify_animation.py` confere material, grade/UV e gera imagens de controle.
3. `blender -b -t 2 --python render_frames.py -- 0 2` e `-- 1 2`, em dois processos, renderizam somente os planos 3D necessários. A cena dos cartões sem avatar tem poses a 10 Hz; os planos com Dery são renderizados a 30 fps.
4. `python finish_graphic_frames.py` completa os quadros sustentados dos cartões. `python export_short.py` e `python export_short.py --wide` exportam as duas composições; a base horizontal temporária fica no cache, sem WFP horizontal.
5. `python make_filmora.py` monta apenas o WFP vertical e seu pacote. `python verify_export.py` checa os exports, preservação PCM, mídia em movimento, recursos e duração dos clipes, velocidade explícita 1× e ZIP.

Os caminhos do cache constam em `timeline.json`; os intermediários ficam fora do Git. `construcao.json`, `validacao_animacao.json`, `filmora.json` e `validacao.json` registram o que foi efetivamente conferido. Original de voz, fontes escolhidas e hashes em `recebimento.json`. Os arquivos-base da cena anterior, rig, malha/UVs e WFP de referência são preservados.
