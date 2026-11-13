from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent
files=[('之前发布',Path('/Volumes/EXTERNAL/自媒体/deepseek-deepinfer-20261021/04-完整制作/output/deepinfer-full-v1-repair1.mp4')),('Fred重制 v2',R/'output/deepinfer-fred-full-v2.mp4')]
a={};versions=[]
for label,p in files:
 h=hashlib.sha256(p.read_bytes()).hexdigest();s=p.stat();i=h[:24];a[i]={'path':str(p.resolve()),'bytes':s.st_size,'mtime_ns':s.st_mtime_ns,'sha256':h};versions.append({'label':label,'url':'/asset/'+i,'filename':p.name,'sha256':h,'bytes':s.st_size})
chapters=[('标题推近',7.2),('Star推近',13.5),('代码拆解',15.766667),('请求往返',23.7),('职责拆分',37.75),('提前安排',43.35),('工程开放',57.3),('配套与适配',66.5),('继续创新',72.7),('共享起点',78.916667),('更多任务',83.583333),('真人收尾',89)]
(R/'allowlist.json').write_text(json.dumps(a,ensure_ascii=False,indent=2));(R/'catalog.json').write_text(json.dumps({'versions':versions,'chapters':[{'label':l,'time':t} for l,t in chapters]},ensure_ascii=False,indent=2))
print(json.dumps(versions,ensure_ascii=False,indent=2))
