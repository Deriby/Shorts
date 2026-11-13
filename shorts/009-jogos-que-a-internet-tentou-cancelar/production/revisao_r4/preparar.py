"""Cut list: remove every standing presenter and every long extra set."""
from pathlib import Path
import json
P=Path(__file__).resolve().parent;ROOT=P.parent
names={'01-gta-san-andreas':'GTA_San_Andreas','02-bmx-xxx':'BMX_XXX','03-bully':'Bully','04-saints-row-iv':'Saints_Row_IV'}
plans={
'01-gta-san-andreas':[
(425,498,'photo','encontro_bar.png',0,'mod_desativado'),(499,568,'seated','',0,'desbloqueio'),
(657,759,'photo','cj_classificacao.png',0,'classificacao_AO'),(760,846,'game','gameplay_speedrun.mp4',44,'retirada'),(847,930,'seated','',0,'consequencia'),(931,1036,'game','gameplay_speedrun.mp4',112,'edicao_revisada'),
(1037,1144,'photo','encontro_rua.png',0,'arquivos_da_versao_original'),(1145,1210,'game','gameplay_speedrun.mp4',118,'carro_sem_tela_preta')],
'02-bmx-xxx':[
(345,438,'game','bmx_gameplay.mp4',26,'ideia'),(584,675,'photo','caixa.jpg',0,'caixa_retail'),(676,782,'seated','',0,'recusa_das_lojas'),
(783,912,'game','bmx_gameplay.mp4',62,'versoes'),(913,1036,'photo','capa.jpg',0,'outras_plataformas'),(1188,1244,'game','bmx_gameplay.mp4',80,'duas_rodas'),(1245,1319,'seated','',0,'punch')],
'03-bully':[
(600,714,'game','bully_gameplay.mp4',218-115/30,'demonstracao_ao_juiz'),(810,898,'seated','',0,'juiz_gamer'),
(899,1005,'game','bully_gameplay.mp4',500,'proibicao_no_brasil'),(1006,1126,'photo','meme.png',0,'contraste')],
'04-saints-row-iv':[
(601,720,'seated','',0,'classificacao'),(721,801,'game','weapon.mp4',14,'contexto_da_recusa'),(802,891,'photo','weapon_menu.png',0,'arma_questionada'),(892,942,'game','free_roam.mp4',558.3,'jogo_ilustrativo'),
(1039,1152,'game','free_roam.mp4',563.2,'versao_modificada')]
}
for ep,patches in plans.items():
 project=ROOT/ep;original=json.loads((project/'timeline.json').read_text());out=project/'output/R4_Sem_Dery_Em_Pe';out.mkdir(parents=True,exist_ok=True)
 shots=[]
 for sh in original['shots']:
  pieces=[p for p in patches if sh['start']<=p[0]and p[1]<=sh['end']]
  if sh['kind'] in ['shop','archive']or pieces:
   assert pieces and pieces[0][0]==sh['start']and pieces[-1][1]==sh['end'],(ep,sh)
   for start,end,kind,source,ss,label in pieces:
    shots.append(dict(start=start,end=end,kind=kind,source=source,source_start=ss,label=label,patch=True,original_shot=sh['id']))
  else:shots.append(dict(sh,patch=False,original_shot=sh['id'],label=sh['mood']))
 for i,sh in enumerate(shots):sh['id']=i
 assert shots[0]['start']==1 and shots[-1]['end']==original['frames']
 assert all(a['end']+1==b['start']for a,b in zip(shots,shots[1:]));assert not any(s['kind']in['shop','archive']for s in shots)
 original.update(slug=names[ep],episode=ep,revision=4,standing_dery=False,extra_sets=False,shots=shots)
 (out/'timeline.json').write_text(json.dumps(original,ensure_ascii=False,indent=2)+'\n')
 print(ep,'patch_frames',sum(s['end']-s['start']+1 for s in shots if s['patch']),'seated_frames',sum(s['end']-s['start']+1 for s in shots if s['kind']=='seated'))
