from pathlib import Path
import json,subprocess,hashlib
from PIL import Image,ImageDraw
p=Path.cwd()/'deepseek-deepinfer-20261021';q=p/'05-\u72ec\u7acb\u8d28\u68c0';v=p/'04-\u5b8c\u6574\u5236\u4f5c/output/deepinfer-full-v1.mp4'
sha=hashlib.sha256(v.read_bytes()).hexdigest();assert sha=='6b5ebdf490c4a5f34f3fc4fa2391496b6dd2d8d6e35daf739284084e7d9a4872'
frames=set()
for t in [2.7,9.333333333,15.766666667,23.7,50,59,83.583333333,89]:
 c=round(t*60);frames.update(c+n for n in [-12,-1,0,1,9,21,42])
for t in [17.4,19,20.8,22.8,25.8,30,34,37.4,39.5,41.2,42,42.8,43.4,44,45,46,47,48.5,49.6,60,62,65,67,70,73,76,79,81.5,85,87,94.2]:frames.add(round(t*60))
frames=sorted(frames)
sel='+'.join('eq(n,%d)'%f for f in frames)
subprocess.run(['/Users/USER/.local/bin/ffmpeg','-v','error','-n','-i',str(v),'-vf',"select='"+sel+"'",'-fps_mode','vfr','-q:v','2',str(q/'frame-%03d.jpg')],check=True)
rows=[]
for i,f in enumerate(frames):
 path=q/('frame-%03d.jpg'%(i+1));rows.append({'frame':f,'seconds':f/60,'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
for i in range(0,len(rows),8):
 sheet=Image.new('RGB',(1080,1010),'#ddd');d=ImageDraw.Draw(sheet)
 for j,r in enumerate(rows[i:i+8]):
  x=j%4*270;y=j//4*505;im=Image.open(r['path']);im.thumbnail((270,480));sheet.paste(im,(x,y+25));d.text((x+3,y+5),'F%d %.3fs'%(r['frame'],r['seconds']),fill='black')
 sheet.save(q/('sheet-%02d.jpg'%(i//8+1)),quality=94)
(q/'sample-index.json').write_text(json.dumps({'video_sha256':sha,'samples':rows},indent=2))
print('samples',len(rows),'sheets',(len(rows)+7)//8)
