"""Use two or three motivated beats per episode, within the user's 1–4 limit."""
from pathlib import Path
import json
EXTRA={
'01-gta-san-andreas':[(17.2,42,'arquivos_cafe','Uma caixa de arquivos abre e revela uma miniatura da caneca de café.','O mod desbloqueando o conteúdo'),(45.0,42,'estrelas_cafe','A caneca recebe cinco estrelas de procurado, como se o café fosse o crime.','Contraste entre a violência e o café')],
'02-bmx-xxx':[(12.1,48,'bike_x','Três X caem sobre uma bicicletinha, fazendo o quadro ceder.','A ideia dos desenvolvedores')],
'03-bully':[(38.0,35,'disco_grade','O disco de Bully vira de lado e passa entre as barras de uma grade de brinquedo.','A proibição e o acesso nas barraquinhas')],
'04-left-4-dead-2':[(37.0,45,'amor_sequencia','O coração sobre o primeiro jogo dá lugar a uma careta de irritação quando chega o segundo.','Gostaram tanto do primeiro que ficaram bravos com outro')],
'04-saints-row-iv':[(23.2,36,'sem_graca','Dery começa com uma risada e corta para uma expressão seca, sem graça.','O órgão de classificação não achou graça')],
'06-gta-v':[(14.5,45,'peticao','Uma petição de brinquedo desenrola pela mesa e continua descendo pela borda.','Dezenas de milhares de assinaturas')],
'07-pokemon-sword-shield':[(30.5,48,'viagem','Uma Pokébola segue toda confiante com uma malinha, preparando a rejeição no monitor.','Transferir os Pokémon de um jogo para outro')],
'08-night-trap':[(24.0,42,'surto','Close no Dery: susto, olhos saltados e uma negativa curta com a cabeça.','Políticos americanos surtaram')]
}
def expand(plans,R):
 for ep in plans:
  if ep.get('gags'):continue
  fields=['start','end','count','kind','action','phrase','cache'];gags=[{k:ep[k]for k in fields}];gags[0].update(id='principal',model=ep['output']+'/'+ep['slug']+'_R6_Cena_Curta.blend')
  for i,(start,count,kind,action,phrase)in enumerate(EXTRA[ep['episode']],2):
   a=round(start*30)+1;cache=Path(ep['cache'])/kind;cache.mkdir(parents=True,exist_ok=True);gag=dict(id=kind,start=a,end=a+count-1,count=count,kind=kind,action=action,phrase=phrase,cache=str(cache),model=ep['output']+'/'+ep['slug']+f'_R6_{i:02d}_Cena_Curta.blend');gags.append(gag);(cache/'frames').mkdir(exist_ok=True)
  gags.sort(key=lambda g:g['start']);assert 2<=len(gags)<=4 and all(a['end']<b['start']for a,b in zip(gags,gags[1:]));ep['gags']=gags;(R/ep['output']/'plano_ceninha.json').write_text(json.dumps(ep,ensure_ascii=False,indent=2)+'\n')
 return plans
if __name__=='__main__':
 P=Path(__file__).resolve().parent;R=next(p for p in P.parents if(p/'AGENTS.md').exists());p=P/'plano.json';d=expand(json.loads(p.read_text()),R);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print('R6_EXPANDED',[(e['episode'],len(e['gags']))for e in d])
