from pathlib import Path
R=Path(__file__).resolve().parent
def change(file,pairs):
 p=R/file;s=p.read_text()
 for a,b in pairs:
  if a in s:s=s.replace(a,b)
 p.write_text(s)
change('src/components/T22a-PostCard.tsx',[("inset: 0, filter: push >","inset: 0, opacity: 1-push, filter: push >"),("opacity: 0.8 * push","opacity: push"),('borderRadius: S.radius,\n          overflow:', 'borderRadius: S.radius * (1-push),\n          overflow:')])
change('src/components/T04e-PackOpen.tsx',[("opacity: 0.6 * recede","opacity: 0.94 * recede")])
change('src/index.tsx',[("y:418,w:220,h:139","y:418,w:220,h:115"),("categories={['研究代码','适配环境','继续优化']}","categories={['团队 A','团队 B','更多团队']}")])
change('src/components/T02g-RoleRoadmap.tsx',[
 ('const laneDim = cur && !isCurLane ? focus : 0;', '''let laneDim = cur && !isCurLane ? focus : 0;
        if(c.focusSchedule){laneDim=0;for(const event of c.focusSchedule){laneDim=mix(laneDim,event.lane===li?0:1,q(t,event.at,event.at+0.55));}}'''),
 ('const isCur = isCurLane && cur!.step === j;','let isCur = isCurLane && cur!.step === j;'),
 ('const done = isCurLane && j < cur!.step;','let done = isCurLane && j < cur!.step;'),
 ('const lift = isCur ? focus : 0;','let lift = isCur ? focus : 0;'),
 ('const fade = done || later ? focus : 0;','let fade = done || later ? focus : 0;'),
 ('const check = done ? p(t, focusAt + 0.25, focusAt + 0.6) : 0;', '''let check = done ? p(t, focusAt + 0.25, focusAt + 0.6) : 0;
              if(c.focusSchedule){
                lift=0;fade=0;check=0;
                for(const event of c.focusSchedule){
                  const v=q(t,event.at,event.at+0.55);
                  lift=mix(lift,event.lane===li&&event.step===j?1:0,v);
                  fade=mix(fade,event.lane===li&&event.step!==j?1:0,v);
                  check=mix(check,event.lane===li&&j<event.step?1:0,p(t,event.at+0.25,event.at+0.6));
                }
                done=check>0;isCur=lift>0.001;
              }''')
])
