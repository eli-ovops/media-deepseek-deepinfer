import json,pathlib,subprocess,re
from PIL import Image,ImageDraw,ImageFont

ROOT=pathlib.Path(__file__).resolve().parent
new=json.loads((ROOT/'source-metadata-v2-new.json').read_text())
old=json.loads((ROOT/'source-metadata.json').read_text())
sources={x['id']:x for x in old+new}
frames=ROOT/'frames-v2';frames.mkdir(exist_ok=True)
points=[]
for source in new:
    duration=float(source['probe']['format']['duration'])
    points.extend((source['id'],round(t,3),'distribution') for t in [.25,duration/2,duration-.25])
points.extend((sid,t,'boundary') for sid,t in [('N06',8.8),('N06',9.3),('N06',9.8),('S3',11.8),('S3',12.2),('S3',12.5),('N11',33.8),('N11',34.25),('N11',34.5),('N12',.2),('N12',26.7),('N12',27.2)])
font=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',18)
samples=[]
for page in range(3):
    canvas=Image.new('RGB',(1080,2040),(22,22,22));draw=ImageDraw.Draw(canvas)
    for cell,(sid,t,kind) in enumerate(points[page*16:(page+1)*16]):
        target=frames/(sid+'-'+str(t).replace('.','p')+'.jpg')
        subprocess.run(['/Users/USER/.local/bin/ffmpeg','-nostdin','-hide_banner','-loglevel','error','-n','-ss',str(t),'-i',sources[sid]['path'],'-frames:v','1','-vf','scale=270:-1',str(target)],check=True)
        x=(cell%4)*270;y=(cell//4)*510
        canvas.paste(Image.open(target).convert('RGB'),(x,y+30))
        draw.text((x+5,y+5),sid+' '+str(t)+'s',font=font,fill='white')
        samples.append({'source_id':sid,'source_path':sources[sid]['path'],'requested_seconds':t,'image':str(target),'kind':kind,'sheet':'contact-v2-'+str(page+1)+'.jpg','limits':'nominal source-time sample only'})
    canvas.save(ROOT/('contact-v2-'+str(page+1)+'.jpg'),quality=90)
(ROOT/'visual-samples-v2.json').write_text(json.dumps(samples,ensure_ascii=False,indent=2)+'\n')

analysis=[]
for t in json.loads((ROOT/'transcription-index-v2-new.json').read_text()):
    wav=pathlib.Path(t['receipt']['output_directory'])/'audio.wav'
    run=subprocess.run(['/Users/USER/.local/bin/ffmpeg','-nostdin','-hide_banner','-i',str(wav),'-af','silencedetect=noise=-35dB:d=0.12','-f','null','-'],capture_output=True,text=True,check=True)
    (ROOT/(t['id']+'-silence.log')).write_text(run.stderr)
    pending=None;gaps=[]
    for line in run.stderr.splitlines():
        start=re.search(r'silence_start: ([0-9.]+)',line)
        if start:pending=float(start[1])
        end=re.search(r'silence_end: ([0-9.]+)',line)
        if end and pending is not None:gaps.append([pending,float(end[1])]);pending=None
    analysis.append({'source_id':t['id'],'wav':str(wav),'silences_minus35db_120ms':gaps,'limits':'Low energy is not direct listening or proof of absent speech.'})
    print(t['id'],gaps)
(ROOT/'audio-energy-analysis-v2-new.json').write_text(json.dumps(analysis,ensure_ascii=False,indent=2)+'\n')
print('48 samples, three sheets, twelve audio energy analyses complete')
