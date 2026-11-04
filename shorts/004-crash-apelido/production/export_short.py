"""Encode the 16:9 master and the shot-aware vertical edit from the same frames."""
from pathlib import Path
import argparse,json,subprocess

ROOT=Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--encode-only',action='store_true')
    parser.add_argument('--revision',choices=['r1','r2'],default='r1')
    parser.add_argument('--preset',default='medium')
    args=parser.parse_args()
    rev=args.revision=='r2';suffix='_R2'if rev else ''
    frames=ROOT/('renders/r2'if rev else 'renders/final');frames.mkdir(parents=True,exist_ok=True)
    project=ROOT/('output/Dery_Crash_Master'+suffix+'.blend')
    if not args.encode_only:
        subprocess.run(['blender','-b',str(project),'-t','4','-o',str(frames/'frame_'),
                        '-F','PNG','-s','1','-e','672','-a'],check=True)
    missing=[i for i in range(1,673)if not(frames/('frame_%04d.png'%i)).exists()]
    stale=[i for i in range(1,673)if i not in missing and(frames/('frame_%04d.png'%i)).stat().st_mtime<project.stat().st_mtime]
    if missing or stale:raise RuntimeError(f'Missing frames: {missing}; stale frames: {stale}')
    crops=json.loads((ROOT/('vertical_crops_r2.json'if rev else 'vertical_crops.json')).read_text())
    expr=str(crops[-1]['x_start'])
    for shot in reversed(crops):
        a=shot['start']-1;b=shot['end']-1;x0=shot['x_start'];x1=shot['x_end']
        linear=f'{x0}+({x1-x0})*(n-{a})/{max(1,b-a)}'
        expr=f'if(between(n,{a},{b}),{linear},{expr})'
    bayer='-3+4*mod(X,2)+6*mod(Y,2)-8*mod(X,2)*mod(Y,2)'
    channels=':'.join(f"{c}='clip(floor(({c}(X,Y)+({bayer}))/8)*8,0,255)'"for c in 'rgb')
    treatment='format=gbrp,geq='+channels+',scale=1920:1080:flags=neighbor'
    # Every vertical shot follows the planned face/monitor focus. No softened
    # enlargement: both deliveries retain the native pixels and ordered dither.
    filters=f"[0:v]{treatment},split=2[master][v];[v]crop=608:1080:x='{expr}':y=0,scale=1080:1920:flags=neighbor[short]"
    common=['-t','28','-c:v','libx264','-threads','2','-preset',args.preset,'-crf','17','-pix_fmt','yuv420p',
            '-c:a','aac','-b:a','160k','-ar','44100','-movflags','+faststart']
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','warning','-nostats','-y',
        '-framerate','24','-start_number','1','-i',str(frames/'frame_%04d.png'),
        '-i',str(ROOT/'assets/voz/narracao_mix_28s.wav'),'-filter_complex',filters,
        '-map','[master]','-map','1:a',*common,str(ROOT/('output/Dery_Crash_Master_16x9'+suffix+'.mp4')),
        '-map','[short]','-map','1:a',*common,str(ROOT/('output/Dery_Crash_Short_9x16'+suffix+'.mp4'))],check=True)

if __name__=='__main__':main()
