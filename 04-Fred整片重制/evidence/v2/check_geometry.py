from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2]
# Algebra matches T22a's screen affine map; actual exported frames are reviewed separately.
def q(t,a,b):
 u=min(1,max(0,(t-a)/(b-a)));return u*u*u*(u*(u*6-15)+10)
rows=[]
for sid,start,length,line,pushAt,returnAt,textUnits in [('repo',162,398,(28,18,180,34),4.15,5.92,12.16),('stars',560,386,(1080,18,148,34),3.75,5.7,6)]:
 k=960/1265;x=60+line[0]*k;y=800-612*k/2+line[1]*k;w=line[2]*k;h=line[3]*k;z=min(5,860/w);size=88;screenY=900-(h*z+86+size*1.16)/2+h*z/2;fx=x+w/2;fy=y+h/2+(900-screenY)/z
 for local in range(length):
  t=local/60;u=q(t,pushAt,pushAt+.7)*(1-q(t,returnAt,returnAt+.7));scale=1+(z-1)*u;tx=u*(540-z*fx);ty=u*(900-z*fy)
  box=[scale*(x-8)+tx,scale*y+ty,scale*(x+w+8)+tx,scale*(y+h)+ty]
  rows.append({'scene':sid,'frame':start+local,'push':u,'box':box,'insideSafeFrame':box[0]>=48 and box[2]<=1032 and box[1]>=48 and box[3]<=1660})
assert all(r['insideSafeFrame'] for r in rows)
report={'status':'PASS_GEOMETRY_ONLY','method':'Screen affine interpolation, exact quintic; checked padded ROI all784frames of both scenes after card established. Initial float-up occurs only before push and is outside this affine-only check.','safeRect':[48,48,1032,1660],'minLeft':min(r['box'][0] for r in rows),'maxRight':max(r['box'][2] for r in rows),'samples':rows,'source':{'path':str(R/'src/components/T22a-PostCard.tsx'),'sha256':hashlib.sha256((R/'src/components/T22a-PostCard.tsx').read_bytes()).hexdigest()}}
(R/'evidence/v2/roi-geometry.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k!='samples'})
