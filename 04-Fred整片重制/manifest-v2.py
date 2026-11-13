from pathlib import Path
import json,hashlib,sys,copy,shutil
R=Path(__file__).resolve().parent;E=R/'evidence/v2';sys.path.insert(0,str(R/'fred-runtime/skills/fred-remotion-output/scripts'))
from library_gate import acceptance_signature
from component_distribution import analyze
from common import load_references

def rec(p):p=Path(p);return {'path':str(p.resolve()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
m=json.loads((E.parent/'v1-freeze/Manifest.json').read_text());idx=json.loads((E/'sample-index.json').read_text());video=idx['video'];affected={'repo','stars','code'}
m['version']='v2';m['variant']='fred-full-remake-v2';m['parentVersion']={'version':'v1','video':rec(R/'output/deepinfer-fred-full-v1.mp4'),'manifest':rec(E.parent/'v1-freeze/Manifest.json'),'snapshotIndex':rec(E.parent/'v1-freeze/snapshot-index.json')}
m['revision']={'task':rec(R/'04-返修-Q1Q2.md'),'affectedScenes':sorted(affected),'issues':['Q1 affine camera ROI stays in frame','Q2 same screenshot inherited across F945→946'],'sourceScope':rec(E/'change-scope.json'),'astScope':rec(E/'source-scope.json'),'audio':'AAC packets copied unchanged from reviewed v1','retained':['all other scene source and timing','captions','talking plate','real screenshot','kit/fonts/material','covers','global gate implementation']}
shutil.copyfile(R/'output/deepinfer-fred-v1.srt',R/'output/deepinfer-fred-v2.srt');m['subtitles']=rec(R/'output/deepinfer-fred-v2.srt')
notes={'repo':'Q1屏幕仿射端点插值，保留quintic和最终构图；F432/F540及10fps中间态标题完整在画幅内。','stars':'Q1同法修Star；F810/F930及10fps中间态完整；归位结束提前0.02秒到local6.4秒，保证F945完整稳态。','code':'Q2沿前场x60/y567.778/w960/h464.443裁剪截图、满透明度继承；0–0.7秒按原q移动到拆解基位，描框和拎出cue保持；F945→946无白帧或几何突跳。'}
for p in m['pages']:
 sid=p['stableId']
 for ref in p.get('referenceChoices',[]):
  for key in ['implementation','callSite']:
   record=ref[key];record.update(rec(record['path']))
 if sid in affected:
  p['referenceChoices'][0]['change']+=' v2: '+notes[sid]
  frames=[f for f in idx['frames'] if p['startFrame']<=f['frame']<p['startFrame']+p['durationInFrames']]
  p['keyframeReview']={'status':'assistant-reviewed-Q1Q2-only','frames':frames,'sourceFiles':[rec(R/'src/index.tsx'),p['referenceChoices'][0]['implementation']],'artifact':video,'scope':'仅Q1/Q2精确帧，见sample-index；非连续视听','observations':notes[sid],'normalSpeed':'UNKNOWN','directHearing':'UNKNOWN'}
  p['componentAcceptance']={'status':'passed','reviewer':'assistant','stage':'keyframes','checks':{'semanticFit':'原内容和现成组件职责保留；只修本次两项几何/继承问题。','corePreserved':notes[sid],'visualQuality':notes[sid]+' 仅采样检查范围。'},'evidence':[f for f in frames if f['frame'] in [432,540,810,930,946,966,984]]}
  p['componentAcceptance']['contextSha256']=acceptance_signature(m,p,'keyframes')
 else:
  p['inheritedReview']={'from':'v1','independentReview':str(R/'05-独立质检/审查-v1.md'),'reason':'本次源与动作保持；按PMO要求不重开全场审查。v1旧帧不冒充新v2逐场检查。'}
  if 'componentAcceptance' in p:p['componentAcceptance']['status']='inherited-v1-not-reexecuted'
  if 'keyframeReview' in p:p['keyframeReview']['status']='historical-v1'
m['export']={**video,'videoFrames':5654,'videoSeconds':5654/60,'audioEvidence':rec(E/'audio-packet-identity.json'),'containerEvidence':rec(E/'probe.json'),'decode':rec(E/'decode.json')}
m['reviewCoverage']={'scope':'Q1/Q2 only','samplingIndex':rec(E/'sample-index.json'),'geometrySupplement':rec(E/'roi-geometry.json'),'preservedSamples':rec(E/'unchanged-sample-comparison.json'),'normalSpeedAV':'UNKNOWN','directHearing':'UNKNOWN','independent05V2':'PENDING','noRepeatedWholeFilmReview':True}
m['deliveryLimits']={'implementationGate':'原FAIL保留，05独立确认跨标签regex误报，不重跑/改门禁','continuousAV':'UNKNOWN','directHearing':'UNKNOWN','independent05V2':'PENDING','pmoAcceptance':'PENDING','userApproval':'PENDING'}
m['componentDistributionReview']['status']='inherited-v1-no-reselection'
(R/'Manifest-v2.json').write_text(json.dumps(m,ensure_ascii=False,indent=2));(R/'Manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
# Current gate is explicitly bounded; do not turn v1 unchanged-page evidence into all-v2 acceptance.
s=copy.deepcopy(m);s['gateScope']={'mode':'bounded-revision','issues':['Q1','Q2'],'fullManifest':rec(R/'Manifest-v2.json')};s['pages']=[p for p in s['pages'] if p['stableId'] in affected]
_,n=load_references(R/'fred-runtime');a=analyze(s,n)
d=next(d for d in m['componentDistributionReview']['decisions'] if 'repo' in d['sceneIds']);d['evidence']=[rec(E/'sheet-01.jpg'),rec(E/'sheet-03.jpg')]
s['componentDistributionReview']={'status':'passed','reviewedBy':'assistant','contextSha256':a['contextSha256'],'decisions':[d],'stage':'Q1/Q2 final sampled output only'}
(E/'Manifest-keyframes-scope.json').write_text(json.dumps(s,ensure_ascii=False,indent=2))
print(video)
