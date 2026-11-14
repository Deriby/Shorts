# Intro — Jogos que a internet tentou cancelar

Abertura. Voz enviada completa, 27.962 s; saída de 28.233 s/847 quadros a 30 fps.

- [MP4 16:9](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/00-intro/output/Intro_Cancelar_16x9.mp4).
- [Filmora 16:9 com mídias](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/00-intro/output/Intro_Cancelar_Filmora.zip).
- [Blender](output/Dery_Intro_Cancelar.blend), [roteiro](roteiro_animacao.md), [fontes](recebimento.json) e [validação](output/validacao.json).
- [Prévia 16:9](output/Previa_Cenas_16x9.jpg).

Abertura exclusivamente 16:9. Alternância motivada pela voz: café GTA, jogo BMX no CRT, rodas BMX, promessa do vídeo, arma Saints Row IV no CRT, convite final. As duas gags vêm dos masters R6 entregues; não refazer os oito shorts. Nenhuma cartela de texto ou nova legenda.

Dery original na cadeira original, com apoios reais nas coxas e gestos adaptados à intenção da fala. 42 IDs de PNG facial usados, com troca seca; sem mudar malha, rig, UVs ou roupas. 0 ceninhas novas curtas. Duas gags reaproveitadas dos masters R6, com suas fontes e quadros registrados em `reuso_gags.json`.

PSX só na animação/personagem/cenário. Gameplay/fotos/memes, inclusive no CRT, ficam limpos. A narração é integral, sem frases cortadas, voz gerada, alteração de velocidade/pitch ou legendas/títulos novos. Os nomes nas miniaturas são inscrições nos objetos das gags.

## Projeto

Extraia o ZIP inteiro e mantenha `midias/` ao lado do WFP. Base silenciosa, voz, música baixa e efeitos em faixas próprias. Cortes e zooms editáveis; cada ceninha corresponde a uma ação contínua. Para mudar o 3D, edite o Blender e gere nova base. Somente 16:9, sem versão vertical. Este pacote não compila o vídeo longo.

Foram conferidos duração/quadros/decodificação, voz inteira e idêntica ao PCM da produção no pacote, hashes das fontes, movimento, fidelidade das mídias limpas, recursos/continuidade/velocidade 1× do WFP e integridade do ZIP. Correlação de áudio exportado: 0.999786. **Filmora não foi executado neste Linux**; a conferência estrutural não comprova abertura no aplicativo nem aprovação estética do usuário.

## Reprodução

`preparar.py` organiza o monitor e preserva a voz; `prepare_edit.py` separa música/sons. Execute `build_short.py` no Blender; `criar_ceninhas.py` contém os inserts específicos ou a despedida facial. Renderize por `render_frames.py`. Exporte o CRT por `../shared_media/project_screen.py`. Componha com `compor_16x9.py`. Termine com `make_filmora.py` e `verify_export.py`. O cache em /workspace/attachments/proximos_11_12/00-intro não é versionado.
