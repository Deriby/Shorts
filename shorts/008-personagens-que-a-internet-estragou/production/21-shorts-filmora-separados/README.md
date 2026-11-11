# Lady ao Sonic — 12 projetos Filmora separados

O usuário pediu expressamente os projetos editados dos 12 personagens, separados. Esta etapa usa a edição completa da [produção 20](../20-edicao-final-usuario/) como base, preservada sem alteração.

**[Pacote dos 12 WFPs e mídias recebidas](output/Projetos_Filmora_Lady_ao_Sonic_9x16.zip)** — aproximadamente 441 MB. Extraia o ZIP inteiro; cada pasta contém seu WFP e a subpasta `midias` correspondente.

| Personagem | Duração | Projeto individual |
|---|---:|---|
| Lady Dimitrescu | 38,37 s | [01](output/01_Lady_Dimitrescu/01_Lady_Dimitrescu_Editado_9x16.wfp) |
| Tifa | 28,08 s | [02](output/02_Tifa/02_Tifa_Editado_9x16.wfp) |
| Chun-Li | 38,90 s | [03](output/03_Chun_Li/03_Chun_Li_Editado_9x16.wfp) |
| Ankha | 43,52 s | [04](output/04_Ankha/04_Ankha_Editado_9x16.wfp) |
| Vaporeon | 46,98 s | [05](output/05_Vaporeon/05_Vaporeon_Editado_9x16.wfp) |
| 2B | 39,98 s | [06](output/06_2B/06_2B_Editado_9x16.wfp) |
| Tracer | 25,08 s | [07](output/07_Tracer/07_Tracer_Editado_9x16.wfp) |
| D.Va | 41,83 s | [08](output/08_DVa/08_DVa_Editado_9x16.wfp) |
| Mercy | 29,00 s | [09](output/09_Mercy/09_Mercy_Editado_9x16.wfp) |
| Lara Croft | 37,33 s | [10](output/10_Lara_Croft/10_Lara_Croft_Editado_9x16.wfp) |
| Peach | 37,25 s | [11](output/11_Peach/11_Peach_Editado_9x16.wfp) |
| Sonic | 34,95 s | [12](output/12_Sonic/12_Sonic_Editado_9x16.wfp) |

Os projetos reúnem **265 clipes nativos nas timelines principais**, preservando cortes, efeitos, transições internas, títulos/composições, sons e mixagem do usuário. Cada short começa na fala; vinhetas entre personagens e a intro/encerramento do longo ficam fora. A composição de conteúdo no fim da Tifa permanece.

São 1080×1920/60 fps, usando as animações **9:16 originais**, já produzidas com câmeras/layouts próprios. Não houve render de Blender nem recorte global do longo. Os pacotes AAC dos masters 16:9 e 9:16 são idênticos nos 12 casos. As fontes conservam os 24 fps reais, contagens de frames e durações coerentes no WFP.

Os zooms/deslocamentos da animação foram moderados conforme o tipo de cena de cada clipe, preservando os tempos dos keyframes e os demais efeitos nativos. As amostras de enquadramento dos 12 personagens verificam apenas transformação básica sobre a fonte vertical, não reproduzem plugins do Filmora. A composição de conteúdo da Tifa e seu cache também foram adaptados. As composições, caches e a biblioteca original são mantidos para preservar referências; o painel de mídias pode exibir itens do longo que não aparecem no short.

## Mídias e validação

O ZIP contém 22 mídias recebidas, incluindo os 12 masters verticais. Fontes que só estavam no PC do usuário, como músicas e recursos de plugins pagos, mantêm os caminhos originais e estão listadas em `FONTES_NO_SEU_PC.txt` de cada pasta. Se solicitar localização, indicar a mesma fonte usada no longo. O pacote não incorpora todas as fontes externas do computador.

Foram conferidos integridade dos 12 WFPs/ZIP, limites dos clipes, tempos dos keyframes, metadados inclusive no cache da Tifa, hashes das mídias e preservação de todas as cadeias de efeitos fora da transformação básica. Curvas de velocidade e configurações das transições internas são as originais. O WFP de origem mantém seu hash.

**O Filmora não foi executado neste ambiente Linux. A abertura/reprodução nativa destes novos projetos ainda precisa ser conferida no aplicativo.** Não houve exportação de MP4 final com seus plugins aqui.

## Registro e reprodução

[Manifesto](manifesto.json), [verificação](verificacao.json), [amostras de enquadramento](enquadramentos_conferidos.json) e [integridade do pacote](pacote.json).

```bash
python shorts/008-personagens-que-a-internet-estragou/production/21-shorts-filmora-separados/separar.py
python shorts/008-personagens-que-a-internet-estragou/production/21-shorts-filmora-separados/verificar.py
python shorts/008-personagens-que-a-internet-estragou/production/21-shorts-filmora-separados/empacotar.py
```
