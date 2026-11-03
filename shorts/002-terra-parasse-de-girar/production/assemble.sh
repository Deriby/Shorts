#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
python - <<'PY'
from pathlib import Path
from PIL import Image
expected={f'frame_{i:04d}.png' for i in range(1,1331)}
found={p.name for p in Path('renders').glob('frame_*.png')}
assert expected==found, f'Render incompleto: {len(found)}/1330'
for f in sorted(expected):
 with Image.open(Path('renders')/f) as image:
  assert image.size==(432,768)
  image.verify()
print('1330 source frames verified.')
PY
ffmpeg -hide_banner -loglevel warning -y \
 -framerate 24 -start_number 1 -i renders/frame_%04d.png \
 -vf 'scale=1080:1920:flags=neighbor:out_color_matrix=bt709' \
 -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p \
 -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
 -an -movflags +faststart output/Dery_Terra_Parou_sem_audio.mp4
ffmpeg -hide_banner -loglevel warning -y \
 -i output/Dery_Terra_Parou_sem_audio.mp4 -i assets/voz_original.mp3 -i assets/efeitos_originais.wav \
 -filter_complex '[1:a][2:a]amix=inputs=2:normalize=0:duration=longest,apad[mix]' \
 -map 0:v:0 -map '[mix]' -c:v copy -c:a aac -b:a 256k -ar 48000 \
 -shortest -movflags +faststart -metadata title='E se a Terra parasse de girar AGORA?' \
 output/Dery_Terra_Parou.mp4
