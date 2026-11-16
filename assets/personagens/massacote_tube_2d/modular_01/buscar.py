from pathlib import Path
import argparse,sqlite3,unicodedata

def norm(s):return ''.join(c for c in unicodedata.normalize('NFD',s.casefold())if not unicodedata.combining(c))
p=argparse.ArgumentParser();p.add_argument('termos',nargs='*');p.add_argument('--tipo',choices=['pose','olhos','bigode','frente','rig']);args=p.parse_args();root=Path(__file__).resolve().parent
con=sqlite3.connect(f'file:{root/"catalogo.sqlite"}?mode=ro',uri=True)
for ident,kind,title,file in con.execute('SELECT id,type,title,file FROM assets ORDER BY type,file'):
 if args.tipo and kind!=args.tipo:continue
 if all(norm(term)in norm(title+' '+file)for term in args.termos):print(f'{ident} | {title} | {root/file}')
con.close()
