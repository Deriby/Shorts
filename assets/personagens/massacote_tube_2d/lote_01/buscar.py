"""Consulta local do banco de poses; não precisa de rede."""
from pathlib import Path
import sqlite3,sys,unicodedata

def norm(text):
    return ''.join(c for c in unicodedata.normalize('NFD',text.casefold()) if not unicodedata.combining(c))

root=Path(__file__).resolve().parent
con=sqlite3.connect(f'file:{root / "catalogo.sqlite"}?mode=ro',uri=True)
terms=norm(' '.join(sys.argv[1:])).split()
for ident,title,tags,file in con.execute('SELECT id,title,tags,file FROM poses ORDER BY id'):
    if all(term in norm(title+' '+tags) for term in terms):print(f'{ident} | {title} | {root / file}')
con.close()
