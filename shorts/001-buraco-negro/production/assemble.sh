#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

python - <<'PY'
from pathlib import Path
from PIL import Image
expected={f'frame_{i:04d}.png' for i in range(1,1027)}
found={p.name for p in Path('renders').glob('frame_*.png')}
if expected != found:
    raise SystemExit(f'Render incompleto: faltam {len(expected-found)}; extras {len(found-expected)}')
for name in sorted(expected):
    with Image.open(Path('renders')/name) as im:
        assert im.size==(360,640), name
        im.verify()
print('1026 quadros de origem verificados.')
PY

ffmpeg -hide_banner -loglevel warning -y \
  -framerate 15 -start_number 1 -i renders/frame_%04d.png \
  -vf 'scale=1080:1920:flags=neighbor:out_color_matrix=bt709,fps=30' \
  -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -an -movflags +faststart output/Dery_Buraco_Negro_sem_voz.mp4

ffmpeg -hide_banner -loglevel warning -y \
  -i output/Dery_Buraco_Negro_sem_voz.mp4 -i assets/voz_original.mp3 \
  -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 256k -ar 48000 \
  -af apad -shortest -movflags +faststart \
  -metadata title='E se você caísse em um BURACO NEGRO?' \
  output/Dery_Buraco_Negro_com_voz.mp4

ffprobe -v error -show_entries \
  format=duration:stream=codec_name,codec_type,width,height,r_frame_rate,nb_frames,sample_rate,channels \
  -of json output/Dery_Buraco_Negro_com_voz.mp4
