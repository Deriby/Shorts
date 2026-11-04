"""Preserve and order the recordings, edit the monitor feed, and mix the audio."""
from pathlib import Path
import json,math,wave,array,hashlib,subprocess
ROOT=Path(__file__).resolve().parent;ASSETS=ROOT/'assets';FPS=24
def run(args):subprocess.run(args,check=True,stdout=subprocess.DEVNULL)
def pcm(path):
    with wave.open(str(path))as w:
        assert(w.getnchannels(),w.getsampwidth(),w.getframerate())==(1,2,44100)
        return array.array('h',w.readframes(w.getnframes()))
def wav(path,data):
    with wave.open(str(path),'wb')as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(44100);w.writeframes(data.tobytes())
def main():
    order=['2-fish-audio-20261104-022123.wav','1-fish-audio-20261104-022427.wav','3-fish-audio-20261104-022657.wav']
    voice=array.array('h');entries=[]
    for name in order:
        path=ASSETS/'voz'/name;data=pcm(path)
        entries.append({'file':'assets/voz/'+name,'start':len(voice)/44100,'duration':len(data)/44100,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()});voice.extend(data)
    duration=len(voice)/44100;nframes=math.ceil((duration+.875)*FPS);end=nframes/FPS
    wav(ASSETS/'voz/narracao_completa.wav',voice)
    a=entries[1]['start'];b=entries[2]['start']
    # Boundaries follow the recorded words; source times refer to the upload.
    specs=[(0,1.2,'monitor','explain',36.5,780,False),(1.2,2.95,'game','explain',37.7,780,False),
      (2.95,5.0,'actor','irony',38.2,780,False),(5,8,'actor','explain',5.3,640,False),
      (8,10.4,'monitor','explain',7.5,640,False),(10.4,a,'game','explain',5.0,640,False),
      (a,a+1.4,'game','explain',36.8,780,False),(a+1.4,a+2.15,'game','explain',24,640,False),
      (a+2.15,a+3.0,'game','explain',57,640,False),(a+3,a+4.15,'game','explain',14.0,640,False),
      (a+4.15,a+7.55,'game','explain',24.0,640,False),(a+7.55,a+8.65,'game','recoil',38.2,800,False),
      (a+8.65,a+9.17,'actor','recoil',39.0,800,False),(a+9.17,a+12.2,'game','shock',30.3,650,False),
      (a+12.2,b,'actor','trauma',32.0,650,False),(b,b+2.1,'actor','serious',64.2,640,True),
      (b+2.1,b+5.2,'monitor','serious',64.2,640,True),(b+5.2,b+8.85,'actor','awkward',1.5,640,True),
      (b+8.85,duration,'actor','smug',1.5,640,True),(duration,end,'actor','ending',1.5,640,True)]
    shots=[]
    for i,(t0,t1,kind,mood,source,focus,still)in enumerate(specs):
        first=round(t0*FPS)+1;last=round(t1*FPS)
        if i==len(specs)-1:last=nframes
        shots.append({'id':i,'start':first,'end':last,'kind':kind,'mood':mood,'source_start':source,'focus_x':focus,'still':still})
    assert shots[0]['start']==1 and shots[-1]['end']==nframes
    assert all(x['end']+1==y['start'] for x,y in zip(shots,shots[1:]))
    media=ROOT/'renders/media';media.mkdir(parents=True,exist_ok=True)
    source=ASSETS/'gameplay/san_andreas_postal2_enviado.mp4';cache=media/'source_24fps.mp4'
    if not cache.exists():run(['ffmpeg','-v','error','-y','-threads','4','-i',str(source),'-an','-vf','fps=24,scale=640:360:flags=neighbor','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',str(cache)])
    segments=[]
    for shot in shots:
        count=shot['end']-shot['start']+1;out=media/f"seg_{shot['id']:02d}.mp4"
        if shot['still']:
            image=media/f"still_{shot['id']:02d}.png"
            extract=['ffmpeg','-v','error','-y','-ss',str(shot['source_start']),'-i',str(cache)]
            if shot['source_start']>62:
                extract+=['-vf','crop=440:135:100:0,scale=640:196:flags=neighbor,pad=640:360:0:82:color=0x15131e']
            run([*extract,'-frames:v','1',str(image)])
            args=['-loop','1','-framerate','24','-i',str(image)]
        else:args=['-ss',str(shot['source_start']),'-i',str(cache)]
        run(['ffmpeg','-v','error','-y',*args,'-an','-vf','fps=24','-frames:v',str(count),'-c:v','libx264','-threads','2','-preset','ultrafast','-crf','18','-pix_fmt','yuv420p',str(out)])
        segments.append(out)
    listing=media/'concat.txt';listing.write_text(''.join("file '"+str(p)+"'\n"for p in segments))
    feed=ASSETS/'gameplay/monitor_montado.mp4'
    run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(listing),'-an','-c:v','copy','-movflags','+faststart',str(feed)])
    game=array.array('h',subprocess.check_output(['ffmpeg','-v','error','-i',str(source),'-vn','-ac','1','-ar','44100','-f','s16le','-']))
    mixed=array.array('h',voice);mixed.extend([0]*(math.ceil(end*44100)-len(mixed)))
    for shot in shots:
        if shot['still']:continue
        first=round((shot['start']-1)/FPS*44100);last=round(shot['end']/FPS*44100);src=round(shot['source_start']*44100)
        for j in range(last-first):
            if src+j<len(game):mixed[first+j]=max(-32768,min(32767,mixed[first+j]+int(game[src+j]*.055)))
    beeps=[b-.18,duration+.12,duration+.34]
    for at in beeps:
        for i in range(round(.07*44100)):
            t=i/44100;value=.055*math.sin(math.tau*(420 if t<.035 else 210)*t)*math.exp(-t*30)
            k=round(at*44100)+i
            if k<len(mixed):mixed[k]=max(-32768,min(32767,mixed[k]+int(32767*value)))
    wav(ASSETS/'voz/narracao_mix.wav',mixed)
    (ROOT/'audio.json').write_text(json.dumps({'sequence':entries,'total_voice_seconds':duration,'duration':end,'order':[2,1,3],'originals_unchanged':True,'ending':'Recorded pior/melhor mistura line; no unrecorded Grove Street or neighbor dialogue'},ensure_ascii=False,indent=2))
    (ROOT/'timeline.json').write_text(json.dumps({'fps':FPS,'frames':nframes,'duration':end,'voice_duration':duration,'part2':a,'part3':b,'shots':shots,'beeps':beeps},ensure_ascii=False,indent=2))
    print('POSTAL_ASSETS_READY',nframes,'frames',end,'seconds',flush=True)
if __name__=='__main__':main()
