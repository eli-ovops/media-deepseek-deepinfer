import json, pathlib, subprocess
from PIL import Image,ImageDraw,ImageFont

ROOT=pathlib.Path(__file__).resolve().parent
sources={x['id']:x for x in json.loads((ROOT/'source-metadata.json').read_text())}
points=[('S3',16.8),('S3',17.28),('S3',17.65),('S5',.45),('S2',32.3),('S2',32.82),('S2',33.3),('S1',.6),('S4',11.9),('S4',12.97),('S5',7.85),('S1',11.25)]
canvas=Image.new('RGB',(1280,1800),(22,22,22)); draw=ImageDraw.Draw(canvas)
font=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',18)
records=[]
for index,(sid,t) in enumerate(points):
    path=ROOT/'frames'/(sid+'-boundary-'+str(t).replace('.','p')+'.jpg')
    subprocess.run(['/Users/USER/.local/bin/ffmpeg','-nostdin','-hide_banner','-loglevel','error','-n','-ss',str(t),'-i',sources[sid]['path'],'-frames:v','1','-vf','scale=320:-1',str(path)],check=True)
    x=(index%4)*320; y=(index//4)*600
    canvas.paste(Image.open(path).convert('RGB'),(x,y+30))
    draw.text((x+8,y+5),sid+' @ '+str(t)+'s',font=font,fill='white')
    records.append({'source':sid,'requested_seconds':t,'image':str(path),'limits':'sample only; source nominal time'})
canvas.save(ROOT/'contact-boundaries.jpg',quality=90)
(ROOT/'boundary-samples.json').write_text(json.dumps(records,ensure_ascii=True,indent=2)+'\n')
print('12 boundary samples and second contact sheet generated')
