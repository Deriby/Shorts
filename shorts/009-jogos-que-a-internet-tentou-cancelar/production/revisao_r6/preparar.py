"""Eight short, phrase-specific inserts; preserve delivered episodes and voice."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parent;R=next(p for p in P.parents if(p/'AGENTS.md').exists());C=Path('/workspace/attachments/revisao_r6');C.mkdir(parents=True,exist_ok=True)
rows=[
('01-gta-san-andreas','GTA_San_Andreas',49.2,40,'cafe','A própria caneca de café recebe uma tarja de censura.','Café acompanhado'),
('02-bmx-xxx','BMX_XXX',41.1,51,'rodas','Duas rodas do BMX rolam para lados opostos sobre a mesa.','Mais do que duas rodas'),
('03-bully','Bully',27.9,48,'juiz','O controle de videogame desliza e empurra o martelinho para o lado.','Juiz gamer'),
('04-left-4-dead-2','Left_4_Dead_2',9.8,48,'sequencia','A caixa do primeiro jogo acaba de pousar; a do segundo já chega empurrando a primeira.','Apenas um ano depois'),
('04-saints-row-iv','Saints_Row_IV',4.6,43,'recuo','Dery e sua cadeira dão um recuo curto de susto, preservando o apoio entre corpo e cadeira.','Lugar onde o sol não bate'),
('06-gta-v','GTA_V',34.4,42,'tecla','Uma tecla personalizada de cocô afunda e retorna no teclado do quarto.','Piada do GTA VI e South Park'),
('07-pokemon-sword-shield','Pokemon_Sword_Shield',1318/30,45,'pokebola','Uma Pokébola bate no vidro do monitor com Galar e ricocheteia.','Barrado na imigração'),
('08-night-trap','Night_Trap',1.7,51,'vampiro','A caixinha-vampiro do Night Trap recua quando um alho entra deslizando na mesa.','Garotas de camisola e vampiros')]
plans=[]
for ep,slug,start,count,kind,action,phrase in rows:
 project=ROOT/ep;old4=ep in['01-gta-san-andreas','02-bmx-xxx','03-bully','04-saints-row-iv'];source=project/'output'/('R4_Sem_Dery_Em_Pe'if old4 else'');info=json.loads((source/'timeline.json'if old4 else project/'timeline.json').read_text());filmora=source/'Filmora';wfp=next(filmora.glob('*.wfp'));base=next((filmora/'midias').glob('*.mp4'));tag='_R4'if old4 else'_Cancelar';short=source/(slug+tag+'_9x16.mp4');wide=source/(slug+tag+'_16x9.mp4');mix=source/'mix_revisado.wav'if old4 else project/'assets/audio/mix_final.wav'
 out=project/'output/R6_Cenas_Curtas';out.mkdir(parents=True,exist_ok=True);cache=C/ep;cache.mkdir(exist_ok=True);a=round(start*30)+1;b=a+count-1;assert 1<a<b<info['frames'];files=dict(short=short,wide=wide,base=base,wfp=wfp,mix=mix)
 for path in files.values():assert path.is_file(),path
 plan=dict(episode=ep,slug=slug,chapter=info.get('chapter',ep),frames=info['frames'],fps=30,duration=info['frames']/30,start=a,end=b,count=count,kind=kind,action=action,phrase=phrase,source={k:str(v.relative_to(R))for k,v in files.items()},source_sha256={k:hashlib.sha256(v.read_bytes()).hexdigest()for k,v in files.items()},source_filmora=str(filmora.relative_to(R)),source_info=str((source/'timeline.json'if old4 else project/'timeline.json').relative_to(R)),output=str(out.relative_to(R)),cache=str(cache),source_base_name=base.name,standing_dery=False,new_subtitles=False)
 plans.append(plan);(out/'plano_ceninha.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
 # The local timeline lets the shared depth-mask exporter inspect just this insert.
 (cache/'timeline.json').write_text(json.dumps(dict(frames=count,fps=30,shots=[dict(kind='monitor',start=1,end=count)])))
from expandir import expand
plans=expand(plans,R)
(P/'plano.json').write_text(json.dumps(plans,ensure_ascii=False,indent=2)+'\n')
p=R/'AGENTS.md';s=p.read_text();note='- Nova direção autorizada pelo usuário: **pelo menos uma ceninha curta por short**, com ação ligada à fala, sem encher o vídeo de cortes, sem gags genéricas/complexas de execução duvidosa e com custo baixo. A revisão atual cobre os oito capítulos da série 009, preservando voz inteira, duração, planos do PC, mídias limpas e zero Dery em pé. Reutilizar os masters entregues e renderizar apenas os inserts; fontes antigas ficam intactas em cópias `output/R6_Cenas_Curtas/`. Plano e ferramentas em `009/production/revisao_r6/`. Esta autorização supera a opção anterior de nenhum set/insert extra, mas não reabre os 12 personagens da série 008 nem autoriza outro jogo/compilar o longo. Manter esta direção nas próximas produções autorizadas.\n\n';s=s.replace('# Produção de shorts\n\n','# Produção de shorts\n\n'+note,1);p.write_text(s)
p=R/'.gitattributes';s=p.read_text()
for plan in plans:s+='\n'+plan['output']+'/'+plan['slug']+'_R6_Filmora.zip filter=lfs diff=lfs merge=lfs -text'
p.write_text(s+'\n');print('R6_PLANNED',len(plans),sum(p['count']for p in plans),flush=True)
