# Mídias limpas — revisão R3

Solicitação do usuário: remover o tratamento PSX de gameplay, fotos e memes, mantendo-o no Dery e na animação. A revisão alcança os três capítulos anteriores desta série e já integra Saints Row IV.

A animação dos anteriores é reutilizada, com os tempos e fontes originais. Os inserts são reconstruídos com as mídias recebidas em resolução original, sem RGB555/dithering ou Nearest. A imagem do CRT é inserida depois, com perspectiva correta, proporção preservada e suporte a máscara de oclusão. O cenário/modelo mantém o visual PSX.

## Downloads corrigidos

| Capítulo | Short 9:16 | Capítulo MP4 16:9 | Filmora 9:16 com mídias |
|---|---|---|---|
| GTA San Andreas | [MP4](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/01-gta-san-andreas/output/R3_Midias_Limpas/GTA_San_Andreas_R3_Midias_Limpas_9x16.mp4) | [MP4](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/01-gta-san-andreas/output/R3_Midias_Limpas/GTA_San_Andreas_R3_Midias_Limpas_16x9.mp4) | [ZIP](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/01-gta-san-andreas/output/R3_Midias_Limpas/GTA_San_Andreas_Filmora_Midias_Limpas.zip) |
| BMX XXX | [MP4](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/02-bmx-xxx/output/R3_Midias_Limpas/BMX_XXX_R3_Midias_Limpas_9x16.mp4) | [MP4](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/02-bmx-xxx/output/R3_Midias_Limpas/BMX_XXX_R3_Midias_Limpas_16x9.mp4) | [ZIP](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/02-bmx-xxx/output/R3_Midias_Limpas/BMX_XXX_Filmora_Midias_Limpas.zip) |
| Bully | [MP4](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/03-bully/output/R3_Midias_Limpas/Bully_R3_Midias_Limpas_9x16.mp4) | [MP4](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/03-bully/output/R3_Midias_Limpas/Bully_R3_Midias_Limpas_16x9.mp4) | [ZIP](https://github.com/Deriby/Shorts/raw/refs/heads/main/shorts/009-jogos-que-a-internet-tentou-cancelar/production/03-bully/output/R3_Midias_Limpas/Bully_Filmora_Midias_Limpas.zip) |

**Se você já editou ou legendou um WFP, preserve esse projeto e substitua só o vídeo-base pelo arquivo de mesmo nome em `midias/` do novo pacote.** Isso mantém suas alterações locais. Os WFPs distribuídos nesta revisão conservam a edição entregue anteriormente; os títulos editáveis antigos de GTA/BMX continuam em suas faixas, sem legendas novas. Saints Row IV e Bully não têm títulos sobrepostos acrescentados.

Extraia o ZIP inteiro antes de abrir. Somente WFPs 9:16 nesta revisão; o projeto Filmora 16:9 completo fica para o final da série. Os MP4s 16:9 são capítulos de montagem. Os arquivos anteriores e Blenders originais não foram sobrescritos.

## Implementação e conferência

- `project_screen.py` roda no Blender e exporta o quadrilátero avaliado do display e eventual máscara de oclusão por profundidade, sem renderizar novamente a animação.
- `compose_clean.py` lê os inserts originais e os insere após a camada PSX. Para os anteriores, usa `--legacy` e reaproveita as bases/animações entregues. A mesma ferramenta compõe Saints Row IV a partir dos PNGs nativos.
- `package_revision.py` conserva os WFPs originais, troca a base e reúne as mídias usadas em uma cópia separada.
- `verify_revision.py` confere resolução, quadros/duração, decodificação, recursos, velocidade 1× e ZIP. Compara uma foto real do MP4-base com a fonte limpa e a imagem anterior; também verifica preservação de um plano de animação.

Os relatórios `validacao_midias.json`, `midias_limpas.json`, `filmora.json`, as comparações e os contatos ficam junto de cada revisão. Os caminhos de cache são temporários; o Blender-fonte e a projeção acompanham a produção. OpenCV foi instalado em diretório local de ferramentas, sem alterar o Python do sistema.

**Filmora não foi executado neste Linux.** A validação estrutural não comprova a abertura/reprodução nativa na instalação do usuário.
