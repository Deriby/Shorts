# E se você caísse em um BURACO NEGRO?

Animação do modelo e rig fornecidos pelo usuário, montada para a gravação `voz_original.mp3`. Duração de entrega: aproximadamente 68,4 segundos. Vídeo vertical 1080 × 1920, 30 fps, sem legendas ou textos incorporados. Movimento de origem calculado a 15 fps e duplicado para 30 fps, com render interno 360 × 640 ampliado sem suavização para a estética retrô.

## Arquivos

- `output/Dery_Buraco_Negro_com_voz.mp4`: vídeo com a voz enviada pelo usuário, sem alteração de velocidade, sem música e sem efeitos sonoros adicionados.
- `output/Dery_Buraco_Negro_sem_voz.mp4`: o mesmo vídeo sem áudio, para edição.
- `output/Dery_Buraco_Negro.blend`: cena com rig, movimentos, câmeras, deformação e trocas de expressão animados. Texturas e áudio estão empacotados no arquivo.
- `assets/expressao_susto.png`, `expressao_panico.png` e `expressao_derrota.png`: expressões geradas a partir de uma vista frontal do modelo real.
- `assets/dery_rosto_frente.png`: referência neutra, renderizada do modelo do usuário.
- `timing.json`: marcações editoriais usadas nos planos.
- `build_animation.py` e `assemble.sh`: geração reproduzível da cena e do MP4.

## Personagem e cenário

O personagem usa a geometria original de corpo e cabeça, pesos e rig de 72 ossos. O modelo original fornecido pelo usuário foi preservado. O material do rosto usa o UV original mais um UV frontal de projeção e uma máscara para limitar as trocas de PNG à região facial. Boné, roupa, cabelo e orelhas mantêm a textura original. Os PNGs são projetados na malha da cabeça; não são sprites soltos na frente do personagem.

A deformação de espaguetificação é uma lattice depois da deformação do rig, controlada por shape key. Ela estica o corpo para longe da cabeça e mantém o rosto reconhecível. É uma metáfora cômica não gráfica, não uma simulação de dano humano.

O espaço combina partículas tridimensionais para paralaxe e uma pintura de ambiente gerada com IA, aplicada a uma superfície de cenário. O buraco negro do fundo é um elemento artístico de ambiente; não é uma simulação relativística. O personagem, rig, deformação e câmeras são animados no Blender. A iluminação usa normais 3D e materiais de aparência pré-iluminada para imitar jogos antigos.

## Voz e sincronização

A gravação original foi mantida em velocidade e volume. O MP4 converte o MP3 para AAC por compatibilidade. Há somente a voz, sem trilha ou efeitos adicionais. O arquivo original também está incluído nos arquivos de produção.

Os cortes foram marcados com o texto aprovado e as pausas medidas na gravação. Não foi usada transcrição automática palavra por palavra. Isso é narração em off com reações do personagem, não captura facial ou sincronização labial contínua.

O MP3 tem 68,424 s no contêiner; o conteúdo decodificado tem aproximadamente 68,378 s. O vídeo tem 68,4 s para encerrar num quadro inteiro; a diferença é apenas silêncio no final, sem acelerar, cortar ou esticar a fala.

## Abrir no Blender

Use Blender 4.3 ou posterior. Abra o `.blend` e use a câmera ativa. Os marcadores da timeline identificam os 14 planos. O som está no editor de vídeo para referência na reprodução. O render de imagem tem o sequenciador desligado para não substituir as imagens 3D pela faixa de áudio.

## Reproduzir os renders

Requer Blender 4.3, FFmpeg com libx264 e Python com Pillow. Não requer plugins ou GPU.

```bash
cd /workspace/Shorts/shorts/001-buraco-negro/production
blender -b -t 4 --python build_animation.py -- --preview
blender -b -t 4 --python build_animation.py -- --render
bash assemble.sh
```

Também é possível renderizar intervalos do `.blend` já pronto:

```bash
blender -b output/Dery_Buraco_Negro.blend -t 2 -o renders/frame_ -F PNG -s 1 -e 1026 -a
```

Salvar manualmente uma cópia do projeto antes de executar o gerador: `build_animation.py` reconstrói e substitui o `.blend` de saída. A geração requer o arquivo-base `assets/dery_base_limpa.blend`; ele já contém o modelo importado com suas texturas.

## Convenções de explicação

O roteiro trata de uma queda idealizada num supermassivo sem gás quente perigoso. O horizonte não é uma parede; sua linha aparece brevemente como indicação gráfica. Depois da travessia, câmera e ambiente são ilustrações explicativas, não imagens enviadas de dentro para um observador externo. O centro permanece desconhecido, sem portais apresentados como fatos.
