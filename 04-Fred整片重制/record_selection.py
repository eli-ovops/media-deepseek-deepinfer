from pathlib import Path
import json,hashlib,sys
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'fred-runtime/skills/fred-remotion-output/scripts'))
from library_gate import acceptance_signature
from component_distribution import analyze
from common import load_references
def record(p):
 p=Path(p);return {'path':str(p.resolve()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
cat=json.loads(Path('/Volumes/EXTERNAL/自媒体/资产库/视频制作总览/catalog.json').read_text())['components']
m=json.loads((R/'Manifest.json').read_text())
selected={'repo':'T22a','stars':'T22a','code':'T04e','request':'T13d','roles':'T04b','pipeline':'T02g','open':'T04f','layers':'T13a','progress':'T03d','shared':'T04d','summary':'T02g'}
observations={
 'INT01':'整页黄色笔刷与镜头推进适合长正文。本片两处短ROI需要同卡浮起和释义层，选择T22a。',
 'INT02':'灰蒙版洞口聚焦原句，没有浮起卡片及释义擦入，短仓库标题和星数优先T22a。',
 'T22a':'原截图浮起、紫刷精确原句、相机推近、背景退焦、原像素清晰及释义擦出，适合两次阅读同一真实仓库。',
 'T04e':'真实整页先标框再把同源像素连续抬到前景，主体和标签先后落定，适合代码及文档可研究的内容。',
 'T12d':'预览是三个阶段词从胶囊分离并退场，没有真实文件区域拆出的对应关系。',
 'T05g':'预览为两个概念和不等号建立，不表达请求往返或仓库拆解。',
 'T13d':'用户与服务器双路线，去程吞入、处理、回程停靠完整。复用已获用户视觉认可的原生竖屏派生。',
 '107-03':'两个版本卡单向箭头，适合版本更替，不能替代请求回程或多步因果推导。',
 'T04b':'一件事分裂为职责胶囊，工具卡从对应胶囊后升起，贴合GPU计算与CPU提前安排。',
 'N008':'商品旁问题转成多个人员角色，需要本片没有的商品媒体；与GPU/CPU双职责不匹配。',
 'T03c':'三节点互通循环后聚焦结论，拓扑与本片双职责不同。',
 'T02g':'身份胶囊先立住，步骤从背后抽出，源码有当前卡反色抬起和前序勾；双泳道表达并行职责及接新任务。原预览仅overview，新增current调度须实际运动检查。',
 'T16a':'单条事件时间轴及事件详情卡，不能保留两种角色同时工作的关系。',
 'T13a':'带厚度的板逆序叠起、承压下沉，指定层拉开擦黑。适合框架、线上配套和模型硬件层次；不适合替代并行步骤。',
 'T04f':'钥匙尖端插锁并转动，沿分支依次解锁能力卡，适合工程成果开放带来的研究、改造和后续创新。',
 'T02h':'三份文件翻面解释，各文件是独立载体，没有前置成果与多个后续动作的依赖。',
 'T02e':'多项内容汇聚成一个产品，方向是多到一，和本段开放后的一到多相反。',
 'T17c':'目录树展开及文件行高亮，用于具体文件路径；本段是系统层次或团队关系，避免虚构目录。',
 'T03d':'后一步从前一白卡下推出，整组重居中，最终黑胶囊落定；与少摸索后投入新优化的叙述一致。',
 'T04d':'一个根对象移位后长出圆角分支，多个子对象展开再聚焦其中之一，可表达共享工程起点。',
 'L81-R005':'预览数字50从文字中抽出再分解数量，当前没有可核的团队数量，拒绝引入数字。',
}
symbols={'T22a':'PostCard','T04e':'PackOpen','T13d':'RequestTrip','T04b':'RoleSplit','T02g':'RoleRoadmap','T04f':'KeyUnlock','T13a':'StackLayers','T03d':'CauseChain','T04d':'CategoryFocus'}
changes={
 'T22a':'原截图CSS裁去顶部100px账户区；原生相机中心540/900；同图标题和Star两次ROI，读完归位；深色材料按原白蒙版退至纯白，保留清晰原像素。',
 'T04e':'整页与两块直接通过同源SVG viewBox裁取；横排改为竖向两层，描框、拎出弧线、物理投影、标签和结论保留；只按真实坐标和口播cue适配。',
 'T13d':'直接复用认可样片的竖向双路线和13.2秒服务器→胶囊交接，输入原速整轨不再用样片音频切片。',
 'T04b':'直接复用认可样片两职责竖向拆分；在5.6秒后进入推进泳道，去掉原样片长停留。',
 'T02g':'两横泳道转为两竖列；抽卡遮挡轴相应转置；保持白卡/黑面擦入/完成勾/阴影；同图按口播连续切焦，旧焦点用原q曲线退回。',
 'T04f':'钥匙上方横向插锁，能力卡竖排；连线从锁芯下沿经左干接卡边，所有钥匙、锁梁、卡色和弹性保留。',
 'T13a':'原厚板和顶面改860宽、210高，竖屏中心540/880；层内容说明尚待配套与适配，不声称部署通过。',
 'T03d':'台阶横移改56、竖间距120，整体随新项居中；保留前后遮挡及末项黑胶囊。',
 'T04d':'树形原生竖屏重排；根为工程积累，分支为团队A/团队B/更多团队，非已核团队名或数量。',
}
m['referenceCatalogRevision']=record(R/'fred-runtime/library/catalog.json')['sha256']
m['audio']={'source':record(R/'public/voice-original-speed.wav'),'policy':'original exact PCM, original speed, no new SFX or BGM'}
m['subtitles']=record(R/'output/deepinfer-fred-v1.srt')
m['designContract']={'spec':'1080x1920 native60','reuse':'complete accurate Fred source and kit','currentModel':'UNKNOWN','continuousAV':'UNKNOWN','directHearing':'UNKNOWN','approval':'full remake authorized; 04 self-check only; PMO and05 pending'}
for p in m['pages']:
 sid=p['stableId']
 if sid not in selected:continue
 label=selected[sid];item=next(x for x in cat if x['label']==label);symbol=symbols[label]
 f=R/'evidence'/f'{sid}-candidates-refined.json'
 if not f.exists():f=R/'evidence'/f'{sid}-candidates.json'
 rows=json.loads(f.read_text())['libraryCandidates']['candidates'][:3]
 p['componentPlan']['candidates']=[{'id':x['id'],'decision':'selected' if x['label']==label else 'rejected','reason':observations[x['label']]} for x in rows]
 p['componentPlan']['inspectedReferences']=[]
 for x in rows:
  it=next(y for y in cat if y['label']==x['label']);p['componentPlan']['inspectedReferences'].append({'id':x['id'],**record(it['media']['path']),'observations':observations[x['label']],'method':'time-series sheet sampling; no continuous audiovisual claim','sheet':record(R/'evidence/reference'/f"{x['label']}.jpg")})
 src=Path(item['sources'][0]['path']);out=R/'src/components'/src.name
 p['referenceChoices']=[{'id':item['id'].removeprefix('component:'),'reason':observations[label],'preserve':'完整准确源码派生；对象关系、分层与遮挡、原字体、原阴影、原缓动及主要动作保留','change':changes[label],'useScope':f"本片{p['startFrame']/60:.6f}–{(p['startFrame']+p['durationInFrames'])/60:.6f}秒",'source':{**record(src),'symbol':symbol},'implementation':{**record(out),'symbol':symbol},'callSite':{**record(R/'src/index.tsx'),'symbol':sid.capitalize()+'Scene' if sid!='stars' else 'StarsScene','callee':symbol}}]
 # Correct plural caller and exact source names are explicit.
 p['componentAcceptance']={'status':'passed','reviewer':'assistant','stage':'suggestion','checks':{'semanticFit':observations[label],'corePreserved':changes[label],'visualQuality':'已读准确源预览时间序列图并比较Top3；此处只通过选型，不代表新导出或连续声画验收。'},'evidence':[record(R/'evidence/reference'/f'{label}.jpg')]}
 p['componentAcceptance']['contextSha256']=acceptance_signature(m,p,'suggestion')
_,normalized=load_references(R/'fred-runtime');audit=analyze(m,normalized)
decisions=[]
for g in audit['groups']:
 isRepo='repo' in g['sceneIds']
 reason='同一真实仓库的两个不同ROI；标题后相机退回原卡再看Star，不重复飞入。' if isRepo else '先建立GPU/CPU并行步骤，末段以current模式回现同一图直接接新任务，不重新抽卡。'
 ev=R/'evidence/reference'/('T22a.jpg' if isRepo else 'T02g.jpg')
 decisions.append({'groupKey':g['groupKey'],'sceneIds':g['sceneIds'],'reuseKind':'continuous-object' if isRepo else 'intentional-reprise','reason':reason,'comparisons':[{'stableId':sid,'task':next(p['oneQuestion'] for p in m['pages'] if p['stableId']==sid),'visibleState':{'repo':'标题原像素与开源释义','stars':'同图Star原像素与一万多颗星','pipeline':'GPU/CPU步骤建立后焦点到新任务','summary':'同图直接回现，焦点接续'}[sid],'reusePurpose':reason} for sid in g['sceneIds']],'evidence':[record(ev)]})
m['componentDistributionReview']={'status':'passed','reviewedBy':'assistant','contextSha256':audit['contextSha256'],'decisions':decisions,'stage':'suggestion reference overview; actual output overview pending'}
(R/'Manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
(R/'evidence/Manifest-suggestion.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
