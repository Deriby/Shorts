"""Create original short SFX and export the 96-frame animation as a phone-ready MP4."""
from pathlib import Path
import array, math, random, subprocess, wave, json

HERE=Path(__file__).resolve().parent
OUT=HERE/'output'
SR=48000
sound=[0.0]*(4*SR)
rng=random.Random(884)

def tone(start,duration,f0,f1,volume):
    phase=0.0
    for i in range(round(duration*SR)):
        u=i/max(1,duration*SR)
        phase+=math.tau*(f0+(f1-f0)*u)/SR
        envelope=math.sin(math.pi*u)**2
        j=round(start*SR)+i
        if j<len(sound):
            sound[j]+=volume*envelope*(math.sin(phase)+.15*math.sin(2*phase))

def shoe(start,volume=.12):
    length=round(.055*SR)
    for i in range(length):
        u=i/length
        j=round(start*SR)+i
        sound[j]+=volume*(1-u)**3*(rng.uniform(-1,1)*.7+math.sin(i*math.tau*130/SR)*.3)

for t in [.20,.39,.58,.78]:
    shoe(t,.11)
# A small proud two-note flourish, then a creak and a slipping squeak.
tone(1.04,.09,523,523,.075)
tone(1.15,.13,784,784,.075)
tone(2.10,.25,190,135,.09)
tone(2.43,.22,920,260,.075)
shoe(2.57,.21)
shoe(2.74,.12)
tone(2.68,.28,230,70,.10)
audio=OUT/'efeitos_originais_4s.wav'
pcm=array.array('h',(round(max(-1,min(1,v))*32767)for v in sound))
with wave.open(str(audio),'wb')as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())

video=OUT/'Massacote_Outro_Dery_4s_9x16.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-framerate','24','-start_number','1',
    '-i',str(HERE/'renders/frame_%04d.png'),'-i',str(audio),
    '-vf','scale=1080:1920:flags=neighbor,setsar=1','-frames:v','96','-t','4',
    '-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',
    '-c:a','aac','-b:a','160k','-movflags','+faststart',str(video)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
v=next(x for x in probe['streams']if x['codec_type']=='video')
assert(v['width'],v['height'])==(1080,1920)
assert int(v['nb_frames'])==96
assert abs(float(probe['format']['duration'])-4)<.01
assert any(x['codec_type']=='audio'for x in probe['streams'])
print(json.dumps({'file':video.name,'duration':probe['format']['duration'],'frames':v['nb_frames'],'size_bytes':video.stat().st_size},indent=2))
