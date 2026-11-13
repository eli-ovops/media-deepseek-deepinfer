from pathlib import Path
import json,sys,hashlib
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'fred-runtime/skills/fred-remotion-output/scripts'))
from scene import packet
from library_gate import acceptance_signature
from component_distribution import analyze
from common import load_references
m=json.loads((R/'Manifest.json').read_text());captions=json.loads((R/'src/captions.json').read_text())
def rec(p):
 p=Path(p);return {'path':str(p.resolve()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
script='\n'.join(c['text'] for c in captions)+'\n';(R/'source-script.txt').write_text(script)
offset=0
for i,c in enumerate(captions):c.update(startChar=offset,endChar=offset+len(c['text']),beatId=f'cue-{i+1:02}');offset+=len(c['text'])+1
m['script']={**rec(R/'source-script.txt'),'provenance':'逐字提取已核SRT，不改稿；沿原速音轨，未补造听核'}
m['timingStatus']='audio-aligned';m['timingEvidence']={'subtitle':rec(R/'output/deepinfer-fred-v1.srt'),'note':'沿已授权现存字幕时钟；不是本轮直接听音确认'}
m['parts']=[{'id':'full','startFrame':0,'endFrameExclusive':5654}]
m['clockContract']={'mode':'scene-local','sourceRule':'Sequence按全片半开帧区间定位，内部useCurrentFrame从零；原声全轨一次，真人startFrom等于全片源帧；Full全局t仅用于字幕和真人字幕颜色。'}
m['workflow']['authorization']={'mode':'direct-output','source':str(R/'04-制作任务.md')+'：现在按同一质量完成整条94.233333秒，不停在样片或重复等待批准'}
m['outputSpec']['audio']='required'
m['representativeScenes']=['repo','stars','code','request','roles','pipeline','open','layers','progress','shared','summary']
plans={
 'repo':['完整真实仓库卡从下方升起','紫刷扫仓库标题，镜头推近原像素，开源释义擦出','标题原像素与DeepInfer开源','镜头按原quintic退回完整卡','同一张卡同尺寸交给Star'],
 'stars':['延续已建立的同一仓库卡','扫Star原像素，镜头推近，一万多颗星擦出','截图14.1k与一万多颗星对应','退回完整卡','同图进入代码区域拆解；下一段描框重建'],
 'code':['真实仓库卡建立','两处真实文件区域标框并弧线拎出，标签出现','核心代码、文档与示例及同行研究改造','保留两块区域到段末','硬切请求模型，不伪称几何morph'],
 'request':['用户、服务器和双路线先建立','请求发送、吞入、处理、结果回程停靠，最后服务器收成胶囊','DeepInfer工程层和返回结果','服务器收为820×210胶囊','在同坐标同大小交接T04b'],
 'roles':['沿同位置协同处理胶囊','胶囊拆上下两职责，GPU和CPU工具卡分别升起','计算这一轮、提前安排下一轮','两职责停稳至5.6秒','硬切双列任务图，保持GPU/CPU身份语义；不是无缝形变'],
 'pipeline':['GPU和CPU双列先立角色','步骤从角色后抽出，CPU提前安排→GPU下一轮→接新任务焦点依次切换','当前反色步骤与前序完成勾','接新任务保持到真人','切回原片50秒真人'],
 'open':['钥匙和锁芯建立','钥匙插入转动；读懂、改造、创新三卡依次解锁','已开放工程成果带来的后续动作','三条能力稳态','切到三层系统结构说明边界'],
 'layers':['三层厚板依次建立','层叠、承压，模型硬件层分离聚焦变黑','线上配套仍待补齐，模型硬件还需适配','当前适配层停稳','切因果台阶，继续工程积累价值'],
 'progress':['已有工程积累白卡建立','少摸索一部分从前卡下推出，再推出黑胶囊投入新优化','积累→少摸索→新优化','黑胶囊与上两步停稳','切共享工程根对象'],
 'shared':['工程积累根对象建立','根移位生分支，团队A/B/更多团队先后展开','多团队共用一个工程起点','更多团队聚焦居中，其余后退','切回已建立双列任务图'],
 'summary':['完整复现早先任务双列，不重新抽卡','GPU下一轮焦点转接新任务，然后CPU继续安排','同样算力接更多任务的概念过程，无数字实测宣称','已有任务图停稳','89秒切回原收尾真人']}
words={
 'repo':['DeepInfer 开源'],'stars':['一万多颗星'],'code':['核心代码','文档与示例','同行接着研究和改造'],
 'request':['用户','响应用户请求','推理服务','计算资源 · 服务成本','工程层','DeepInfer','用户请求','返回结果'],
 'roles':['协同处理','计算这一轮','显卡 GPU','提前安排下一轮','处理器 CPU'],
 'pipeline':['GPU','CPU','01','02','03','本轮计算','下一轮计算','接新任务','提前安排','下一轮就绪','继续安排'],
 'open':['工程成果','读懂代码','已有实现可研究','接着改造','在已有成果上继续做','继续创新','投入新的优化'],
 'layers':['线上配套','仍待补齐','推理框架','DeepInfer','模型与硬件','还需适配','不同环境，还需完成适配'],
 'progress':['已有工程积累','少摸索一部分','投入新的优化'],'shared':['工程积累','团队 A','团队 B','更多团队']}
words['summary']=words['pipeline']
for p in m['pages']:
 sid=p['stableId'];start=p['startFrame']/60;end=(p['startFrame']+p['durationInFrames'])/60
 cues=[c for c in captions if c['end']>start and c['start']<end]
 p['sourceBeatIds']=[c['beatId'] for c in cues];p['sourceSpans']=[{k:c[k] for k in ['startChar','endChar','text']} for c in cues];p['sharedSourceReason']='字幕句跨场景边界时共享原句，实际字词只按同一全局字幕时钟显示，不重复音频。'
 p['exactScreenWords']=words.get(sid,[])+[c['text'] for c in cues]
 if sid.startswith('talk'):
  plan=['原真人全屏准确源帧进入','原速人物表情动作与原字幕同步','本段原句本人讲述','保持原帧序列至边界','依时间线硬切下一图形或到片尾；无额外变速']
  p['referenceDisposition']={'mode':'preserved-media','reason':'用户要求复用现存纯真人底片，图形无需复刻。'}
  p['sceneGuide']={'type':'custom','customReason':'现存真人直接复用；现有图形场景类型不应改造本人表达。'}
  p['componentPlan']={'query':'本人全屏原速讲述，保持原帧动作','candidates':[],'inspectedReferences':[],'decisionReason':'沿用户明确要求在'+sid+'复用现存纯真人底片，不将真实本人改成库图形。'}
  for media in p['mediaContract']:media.update(id='talking-source',role='原速真人底片',required=True)
 else:plan=plans[sid]
 p['visualPlan']=dict(zip(['enter','change','read','exit','handoff'],plan))
 p['productionRoute']={'selected':'remotion' if not sid.startswith('talk') else 'preserved-media','source':str(R/'04-制作任务.md')}
 p['dynamicContract']={'mode':'mixed','requiredChangeEvents':1,'sampleCount':9,'staticAllowanceSeconds':3.5,'reason':'动作后保留当前对象阅读；不靠无信息移动填时长。'}
 if sid in ['repo','stars','code']:
  p['mediaContract']=[{**rec(R/'public/github-original.png'),'id':'github-original','role':'2026-10-21 11:45真实仓库截图；裁去账户顶部100px','required':True}]
 guide=p['sceneGuide'];pack=packet(R/'fred-runtime',guide['type']);guide['signature']=pack['guideSignature'];guide['applications']=[]
 for rule in pack['rules']:
  if rule['id']=='F01':decision=plan[0]+'；'+plan[1];check='按本场景实际导出时序检查'+plan[2]+'；正常速度连续视听仍UNKNOWN。'
  elif rule['id']=='F02':decision='本片只要求仓库标题/Star原句，保留截图原像素及必要上下文，不使用假网页。';check='核原像素ROI、中文释义与原截图，观察推近和归位中间态。'
  else:decision='沿准确Fred kit字体、字重与影子，主体原生竖屏重排；字幕固定1710安全区。' if not sid.startswith('talk') else '真人全屏沿原画幅，白字48px阴影字幕在1710px。';check='核本场最长文字、模块边缘、第一可读态与最终态；实际原尺寸帧佐证。'
  guide['applications'].append({'ruleId':rule['id'],'decision':decision,'check':check})
 if p.get('componentAcceptance'):p['componentAcceptance']['contextSha256']=acceptance_signature(m,p,'suggestion')
_,n=load_references(R/'fred-runtime');audit=analyze(m,n);m['componentDistributionReview']['contextSha256']=audit['contextSha256']
(R/'Manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
