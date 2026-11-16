"""Search descriptions, original names and tags without network access."""
import json
from pathlib import Path
import sys
import unicodedata

def norm(s):
    return unicodedata.normalize('NFKD', s.lower()).encode('ascii', 'ignore').decode()

root = Path(__file__).resolve().parent
terms = norm(' '.join(sys.argv[1:])).split()
for item in json.loads((root / 'catalogo.json').read_text())['items']:
    text = norm(' '.join([item['name'], item.get('description', ''), item['category'], *item.get('tags', [])]))
    if all(term in text for term in terms):
        print(f"{item['tag']} | {item['description']} | {root / item['relative_file']}")
