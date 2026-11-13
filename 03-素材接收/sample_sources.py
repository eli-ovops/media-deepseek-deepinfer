import json, pathlib, subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT=pathlib.Path(__file__).resolve().parent
SOURCES=json.loads((ROOT/'source-metadata.json').read_text())
FRAME_DIR=ROOT/'frames'
FRAME_DIR.mkdir(exist_ok=True)
font=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',18)
records=[]
canvas=Image.new('RGB',(1280,5*600),(22,22,22))
draw=ImageDraw.Draw(canvas)
for row,source in enumerate(SOURCES):
    duration=float(source['probe']['format']['duration'])
    times=[0.4,round(duration/3,3),round(2*duration/3,3),round(duration-0.4,3)]
    for col,t in enumerate(times):
        path=FRAME_DIR/(source['id']+'-'+str(t).replace('.','p')+'.jpg')
        subprocess.run(['/Users/USER/.local/bin/ffmpeg','-nostdin','-hide_banner','-loglevel','error','-n','-ss',str(t),'-i',source['path'],'-frames:v','1','-vf','scale=320:-1',str(path)],check=True)
        im=Image.open(path).convert('RGB')
        canvas.paste(im,(col*320,row*600+30))
        draw.text((col*320+8,row*600+5),source['id']+' @ '+str(t)+'s',font=font,fill='white')
        records.append({'source':source['id'],'source_path':source['path'],'requested_seconds':t,'image':str(path),'coverage':'sample only; nominal source time, not continuous viewing'})
canvas.save(ROOT/'contact-overview.jpg',quality=90)
(ROOT/'visual-samples.json').write_text(json.dumps(records,ensure_ascii=True,indent=2)+'\n')
print('20 samples and one contact sheet generated')
