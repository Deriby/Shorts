# Minecraft — Jogos que a internet tentou cancelar

Pacote 11. Voz enviada completa, 43.681 s; saída de 43.933 s/1318 quadros a 30 fps.

- [Short 9:16](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/11-minecraft/output/Minecraft_Cancelar_9x16.mp4).
- [MP4 16:9](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/11-minecraft/output/Minecraft_Cancelar_16x9.mp4).
- [Filmora 9:16 com mídias](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/11-minecraft/output/Minecraft_Filmora.zip).
- [Blender](output/Dery_Minecraft.blend), [roteiro](roteiro_animacao.md), [fontes](recebimento.json) e [validação](output/validacao.json).
- [Prévia 16:9](output/Previa_Cenas_16x9.jpg) e [9:16](output/Previa_Cenas_9x16.jpg).

Dois inserts: TNT de brinquedo explode em cubos na revolta; mini servidor privado recebe uma martelada de banimento na fala das punições. A casa e o martelo são metáforas, não UI real. Os memes de Roblox e NO são os enviados. A imagem polemic.png é resumo, não notícia oficial; não será apresentada como prova.

Dery original na cadeira original, com apoios reais nas coxas e gestos adaptados à intenção da fala. 38 IDs de PNG facial usados, com troca seca; sem mudar malha, rig, UVs ou roupas. 2 ceninhas novas curtas.

PSX só na animação/personagem/cenário. Gameplay/fotos/memes, inclusive no CRT, ficam limpos. A narração é integral, sem frases cortadas, voz gerada, alteração de velocidade/pitch ou legendas/títulos novos. Os nomes nas miniaturas são inscrições nos objetos das gags.

## Projeto

Extraia o ZIP inteiro e mantenha `midias/` ao lado do WFP. Base silenciosa, voz, música baixa e efeitos em faixas próprias. Cortes e zooms editáveis; cada ceninha corresponde a uma ação contínua. Para mudar o 3D, edite o Blender e gere nova base. Somente WFP 9:16; o capítulo 16:9 está em MP4. Este pacote não compila o vídeo longo.

Foram conferidos duração/quadros/decodificação, voz inteira e idêntica ao PCM da produção no pacote, hashes das fontes, movimento, fidelidade das mídias limpas, recursos/continuidade/velocidade 1× do WFP e integridade do ZIP. Correlação de áudio exportado: 0.999880. **Filmora não foi executado neste Linux**; a conferência estrutural não comprova abertura no aplicativo nem aprovação estética do usuário.

## Reprodução

`preparar.py` organiza o monitor e preserva a voz; `prepare_edit.py` separa música/sons. Execute `build_short.py` no Blender; `criar_ceninhas.py` contém os inserts específicos ou a despedida facial. Renderize por `render_frames.py`. Exporte o CRT por `../shared_media/project_screen.py`. Componha com `../shared_media/compose_clean.py .`. Termine com `make_filmora.py` e `verify_export.py`. O cache em /workspace/attachments/proximos_11_12/11-minecraft não é versionado.
