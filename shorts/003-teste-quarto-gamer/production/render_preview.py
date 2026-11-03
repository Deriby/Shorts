"""Render exactly 120 frames, then mux the five-second test for phone playback."""
from pathlib import Path
import subprocess
import argparse

ROOT = Path(__file__).resolve().parent

def ps1_filter():
    # A stable native pixel grid and ordered RGB555 dithering. Strong spatial
    # denoising smears painted textures and silhouettes, so do not use it here.
    bayer='-3+4*mod(X,2)+6*mod(Y,2)-8*mod(X,2)*mod(Y,2)'
    channels=':'.join(f"{c}='clip(floor(({c}(X,Y)+({bayer}))/8)*8,0,255)'" for c in 'rgb')
    return ','.join([
        'scale=216:384:flags=area',
        'unsharp=3:3:0.4:3:3:0',
        'format=gbrp',
        'geq='+channels,
        'scale=1080:1920:flags=neighbor',
    ])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--encode-only', action='store_true')
    args = parser.parse_args()
    frames = ROOT / 'renders'
    frames.mkdir(exist_ok=True)
    if not args.encode_only:
        subprocess.run(['blender', '-b', str(ROOT/'output/Dery_Quarto_Gamer_Teste.blend'),
                        '-t','4','-o',str(frames/'frame_'),'-F','PNG','-s','1','-e','120','-a'],check=True)
    missing=[i for i in range(1,121) if not (frames/('frame_%04d.png'%i)).exists()]
    if missing:
        raise RuntimeError('Missing render frames: '+str(missing))
    scene_time=(ROOT/'output/Dery_Quarto_Gamer_Teste.blend').stat().st_mtime
    stale=[i for i in range(1,121) if (frames/('frame_%04d.png'%i)).stat().st_mtime<scene_time]
    if stale:
        raise RuntimeError('Frames belong to an earlier scene revision: '+str(stale))
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','warning','-nostats','-y','-framerate','24','-start_number','1',
                    '-i',str(frames/'frame_%04d.png'),'-i',str(ROOT/'assets/voz_teste.wav'),
                    '-vf',ps1_filter(),
                    '-t','5','-c:v','libx264','-preset','medium','-crf','16','-pix_fmt','yuv420p',
                    '-c:a','aac','-b:a','160k','-ar','48000','-movflags','+faststart',
                    str(ROOT/'output/Dery_Quarto_Gamer_5s.mp4')], check=True)

if __name__=='__main__':
    main()
