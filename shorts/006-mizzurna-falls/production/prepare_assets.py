"""Synchronize the supplied recording and prepare the clean trailer monitor feed."""
from pathlib import Path
import subprocess,json,math,wave,array,hashlib
ROOT=Path(__file__).resolve().parent
FPS=24
def run(args):subprocess.run(args,check=True,stdout=subprocess.DEVNULL)
def write_wav(path,values):
    with wave.open(str(path),'wb')as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(44100);w.writeframes(values.tobytes())
def main():
    original=ROOT/'assets/voz/voz_original.mp3'
    voicefile=ROOT/'assets/voz/narracao_completa.wav'
    with wave.open(str(voicefile))as w:
        sr=w.getframerate();voice=array.array('h',w.readframes(w.getnframes()))
    assert sr==44100
    duration=len(voice)/sr;frames=math.ceil((duration+.75)*FPS);end=frames/FPS
    # Phrase boundaries from local ASR and pauses measured in the actual upload.
    specs=[
        (0,2.08,'game','city',36.5,640),
        (2.08,4.262,'game','city',31.5,640),
        (4.262,7.121,'actor','serious',31.5,640),
        (7.121,10.841,'monitor','title',11.0,640),
        (10.841,14.527,'monitor','investigate',21.7,640),
        (14.527,17.892,'actor','bichim',24.0,640),
        (17.892,19.354,'actor','scale',36.2,640),
        (19.354,23.063,'game','city',36.2,650),
        (23.063,24.4,'actor','drive',36.0,640),
        (24.4,27.674,'game','residents',31.6,640),
        (27.674,29.15,'actor','explain',24.1,640),
        (29.15,31.521,'actor','recoil',39.0,640),
        (31.521,33.0,'actor','slow',24.0,640),
        (33.0,35.1,'actor','waiting',40.0,640),
        (35.1,37.3,'limbo','shock',45.0,640),
        (37.3,39.1,'actor','serious',24.0,640),
        (39.1,41.8,'actor','director',36.0,640),
        (41.8,44.24,'monitor','director',38.0,640),
        (44.24,46.746,'actor','setup',36.0,640),
        (46.746,end,'actor','clt',36.0,640),
    ]
    shots=[]
    for i,(t0,t1,kind,mood,source,focus)in enumerate(specs):
        shots.append({'id':i,'start':round(t0*FPS)+1,'end':round(t1*FPS),'kind':kind,'mood':mood,'source_start':source,'focus_x':focus})
    shots[-1]['end']=frames
    assert all(a['end']+1==b['start']for a,b in zip(shots,shots[1:]))
    media=ROOT/'renders/media';media.mkdir(parents=True,exist_ok=True)
    source=ROOT/'assets/gameplay/mizzurna_falls_trailer_enviado.mp4'
    cache=media/'trailer_24fps.mp4'
    run(['ffmpeg','-v','error','-y','-threads','2','-i',str(source),'-an','-vf','fps=24,scale=640:360:flags=neighbor','-c:v','libx264','-threads','2','-preset','ultrafast','-crf','18','-pix_fmt','yuv420p',str(cache)])
    clips=[]
    for shot in shots:
        out=media/f"monitor_{shot['id']:02d}.mp4";count=shot['end']-shot['start']+1
        run(['ffmpeg','-v','error','-y','-ss',str(shot['source_start']),'-i',str(cache),'-an','-frames:v',str(count),'-c:v','libx264','-threads','2','-preset','ultrafast','-crf','18','-pix_fmt','yuv420p',str(out)])
        clips.append(out)
    listing=media/'concat.txt';listing.write_text(''.join("file '"+str(p)+"'\n"for p in clips))
    run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(listing),'-an','-c:v','copy','-movflags','+faststart',str(ROOT/'assets/gameplay/monitor_montado.mp4')])
    mixed=array.array('h',voice);mixed.extend([0]*(math.ceil(end*sr)-len(mixed)))
    def tone(at,dur,f0,f1,level):
        phase=0
        for j in range(round(dur*sr)):
            u=j/(dur*sr);phase+=math.tau*(f0+(f1-f0)*u)/sr
            k=round(at*sr)+j
            if k<len(mixed):mixed[k]=max(-32768,min(32767,mixed[k]+round(32767*level*math.sin(phase)*math.sin(math.pi*u)**2)))
    for at in [33.25,33.52]:tone(at,.045,160,90,.055)
    tone(36.18,.52,430,85,.065)
    tone(49.90,.075,740,740,.045)
    write_wav(ROOT/'assets/voz/narracao_mix.wav',mixed)
    audio={'original':'assets/voz/voz_original.mp3','original_filename':'VOZ - O jogo que DESTRUIU seu Criador.mp3','sha256':hashlib.sha256(original.read_bytes()).hexdigest(),'voice_duration_seconds':duration,'duration_seconds':end,'fps':FPS,'frames':frames,'speed_changed':False,'pitch_changed':False,'trimmed':False,'method':'Original MP3 preserved byte-for-byte; decoded PCM without timing changes. Small original synthesized SFX added only in the separate mix.','alignment':'Local Whisper tiny segment estimates, cross-checked with measured pauses; phonetic ASR errors are not inserted into narration.'}
    (ROOT/'audio.json').write_text(json.dumps(audio,ensure_ascii=False,indent=2))
    (ROOT/'timeline.json').write_text(json.dumps({'fps':FPS,'frames':frames,'duration':end,'voice_duration':duration,'shots':shots,'fall_start':36.15,'badge_push':[48.0,49.1]},indent=2))
    print('ASSETS_READY',frames,end,flush=True)
if __name__=='__main__':main()
