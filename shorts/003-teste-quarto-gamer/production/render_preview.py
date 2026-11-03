"""Render exactly 120 frames, then mux the five-second test for phone playback."""
from pathlib import Path
import subprocess
import argparse

ROOT = Path(__file__).resolve().parent

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
    subprocess.run(['ffmpeg','-hide_banner','-y','-framerate','24','-start_number','1',
                    '-i',str(frames/'frame_%04d.png'),'-i',str(ROOT/'assets/voz_teste.wav'),
                    '-vf','nlmeans=s=12:p=7:r=15,hqdn3d=2:1.5:3:2,lutrgb=r=floor(val/8)*8:g=floor(val/8)*8:b=floor(val/8)*8,scale=1080:1920:flags=neighbor',
                    '-t','5','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p',
                    '-c:a','aac','-b:a','160k','-ar','48000','-movflags','+faststart',
                    str(ROOT/'output/Dery_Quarto_Gamer_5s.mp4')], check=True)

if __name__=='__main__':
    main()
