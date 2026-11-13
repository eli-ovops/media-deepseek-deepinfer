from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent;D=R/'repair1';D.mkdir(exist_ok=True)
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
protected=['index.html','Manifest.json','delivery-v1.json','edl-v1.json','captions-v1.ass','captions-v1.json','output/deepinfer-v1.srt','output/deepinfer-full-v1.mp4','covers/manifest.json']
(D/'baseline-sha.json').write_text(json.dumps({p:h(R/p) for p in protected},indent=2))
s=(R/'index.html').read_text()
old="""for(let i=0;i<5;i++){let a=clamp(spring(t-3-i*.24,{k:180,c:14}));let move=cue(t,6+i*.35,1.1);let x=lerp(80+i*190,260+i*153,move),y=lerp(610,960,move);g.globalAlpha=a;task(g,x+(1-a)*100,y-(1-a)*150,150,78,['#615dce','#8984e5','#615dce','#8984e5','#615dce'][i],'任务');}g.globalAlpha=1;
g.strokeStyle='#b8b1a6';g.lineWidth=2;g.strokeRect(250,940,780,120);for(let i=0;i<4;i++){g.fillStyle='#ddd7cb';g.fillRect(250+i*195+130,940,55,120)}"""
new="""// Q1: keep the original branch outside the visible repair interval.
const repairQueue=t>=6&&t<15.2;
const taskWidth=repairQueue?lerp(150,140,cue(t,6,.4)):150;
if(repairQueue){
  // Real gaps occupy only the 13px free spans between 140px tasks on a 153px pitch.
  // Paint the track and its gaps BEFORE arrivals so moving blocks remain whole.
  g.strokeStyle='#b8b1a6';g.lineWidth=2;g.strokeRect(250,940,780,120);
  for(let i=0;i<4;i++){g.fillStyle='#ddd7cb';g.fillRect(260+i*153+140,940,13,120)}
}
for(let i=0;i<5;i++){let a=clamp(spring(t-3-i*.24,{k:180,c:14}));let move=cue(t,6+i*.35,1.1);let x=lerp(80+i*190,260+i*153,move),y=lerp(610,960,move);g.globalAlpha=a;task(g,x+(1-a)*100,y-(1-a)*150,taskWidth,78,['#615dce','#8984e5','#615dce','#8984e5','#615dce'][i],'任务');}g.globalAlpha=1;
if(!repairQueue){g.strokeStyle='#b8b1a6';g.lineWidth=2;g.strokeRect(250,940,780,120);for(let i=0;i<4;i++){g.fillStyle='#ddd7cb';g.fillRect(250+i*195+130,940,55,120)}}"""
assert s.count(old)==1
(R/'index-repair1.html').write_text(s.replace(old,new))
(D/'patch-source.json').write_text(json.dumps(dict(baseline='index.html',modified='index-repair1.html',baseline_sha256=h(R/'index.html'),modified_sha256=h(R/'index-repair1.html'),changed_global_frames=[1782,2334],changed_global_seconds=[29.7,38.9],reason='Queue remains visible during downward paper camera until ~38.9; extend 0.6s beyond estimated 38.3 for its full exit. CPU/GPU functions and all other objects unchanged.',queue_geometry=dict(task_x=260,pitch=153,task_width=140,gap_width=13,gap_draw_order='before task blocks'),audio_changed=False,captions_changed=False),indent=2))
