# Referência de corpo inteiro — proposta v3

O usuário forneceu uma referência do personagem com camiseta preta, mangas cinza por baixo, jeans escuros, tênis claros e boné para trás. Pediu esse visual sem mochila e reforçou que os pixels, a geometria angular e o cabelo sobre a testa devem permanecer.

Na conferência, apontou que os desenhos lembravam sua aparência, mas ficavam pequenos no centro da cabeça. Também rejeitou a franja de pontas repetidas. Esta proposta ajusta o encaixe do mesmo desenho e substitui as pontas por uma franja texturizada. **Ainda não houve aprovação da versão corrigida. Não iniciar as outras expressões.**

## Arquivos

- [Corpo inteiro](Previa_Corpo.png) e [close do rosto](Previa_Rosto.png).
- [Prévia em oito direções](previa_angulos/): pranchas de corpo e cabeça, com imagens individuais para examinar todos os lados da versão atual.
- [Dery_Referencia_Sem_Mochila_v3.blend](Dery_Referencia_Sem_Mochila_v3.blend): candidato editável com as texturas incorporadas, 71 ossos e franja ligada ao osso da cabeça.
- `Rosto_Neutro_128.png`: um único rosto neutro, 128×128, usando o desenho de `Desenho_Fonte.png`.
- `Franja_128x64.png`: textura de cabelo com alfa binário, derivada de `Franja_Fonte.png`; não usa mais as sete pontas triangulares da primeira conferência.
- `Corpo_Atlas_512.png`: atlas original preparado para este visual; `Malha_Cinza_64.png`: tecido usado nas mangas.
- [aplicar.py](aplicar.py), [aplicacao.json](aplicacao.json) e [geracao.json](geracao.json): preparação e registros.

## Encaixe e materiais

O UV frontal foi ampliado nos dois eixos. A largura varia com a altura para ajustar sobrancelhas, olhos, nariz e boca, mantendo o nariz centralizado na geometria. A altura passa de 0,176 m para 0,190 m, ancorada em z=1,641 m. O perfil horizontal está em `face_fit_u_profile` no registro. O ajuste usa a foto frontal fornecida como referência visual; não foi realizado um processo automático de detecção de marcos ou fotogrametria.

Os desenhos faciais foram preservados durante esse ajuste. A franja usa uma tira curva de 16 quads (32 triângulos), textura Closest e recorte de alfa. A tira acompanha o rig por pesos do `CC_Base_Head`, com as mesmas transformações do corpo. A malha principal permanece intacta, com 48.874 triângulos; não se trata de uma retopologia completa do corpo.

As mangas cinza usam a malha dos braços e um material de tecido sobre a região de pele, com corte antes do punho. O tecido vem do banco PSX recebido: `6twelve/Textures/Fabric_01.jpg`. O original está no cache do banco; o projeto inclui apenas a textura utilizada, preparada em 64×64. A reprodução pode usar esse PNG se o banco não estiver disponível. A gola e o boné preservam os recortes do atlas original; o ajuste frontal do boné foi adicionado no material.

As texturas usam canais de cinco bits e Closest. A iluminação é gravada por canto de vértice e aplicada sobre a cor, sem brilho PBR, desfoque de tela ou glitch. As prévias são estáticas em fundo neutro para avaliar o personagem. O arquivo não contém mochila, cenário de rua ou animação nova. As fotos pessoais não foram copiadas para o Git.

## Reproduzir

```bash
blender -b --disable-autoexec -t 4 --python assets/personagens/dery/rig_ps1_v2/texturas/rosto_neutro_v3/aplicar.py
```

O script lê o rig-base intacto e os desenhos desta pasta, prepara os materiais e a franja, gera as duas prévias e salva uma saída separada. Os episódios anteriores e as propostas v1/v2 não são alterados. A primeira conferência desta proposta foi preservada fora do Git em `/workspace/attachments/rascunhos_superados/referencia_v3_primeiro_encaixe/`.
