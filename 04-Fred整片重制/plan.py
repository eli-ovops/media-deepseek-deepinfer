from pathlib import Path
import json,hashlib,subprocess
r=Path(__file__).resolve().parent;root=Path('/Users/USER/.codex/skill-repos/FredTalk')
scenes=[('talk-open',0,162,None,'','AI的成本战'),('repo',162,560,'image-comparison','真实界面 局部 拉远 全貌','DeepInfer开源'),('stars',560,946,'image-comparison','真实截图 关键句 荧光 放大','GitHub一万多颗星'),('code',946,1422,'relationship','整体 仓库 拆开 几个部分','核心代码交给同行研究改造'),('request',1422,2265,'relationship','请求 服务器 返回 结果 去程 回程','用户涌入与服务成本'),('roles',2265,2601,'relationship','角色 分工 任务 拆分 环节 计算 安排','GPU本轮计算与CPU提前安排'),('pipeline',2601,3000,'relationship','两条 身份 泳道 步骤 当前 点亮','减少等待和接新任务'),('talk-view',3000,3438,None,'','梁文锋与持续创新'),('open',3438,3990,'relationship','钥匙 解锁 能力 开放','开放工程成果和继续创新'),('layers',3990,4362,'relationship','分层 结构 当前 层 点亮','线上配套与模型硬件适配'),('progress',4362,4735,'relationship','原因 因果 链 推进 结果','少些摸索，把精力放在新优化'),('shared',4735,5015,'relationship','主题 分支 类别 展开','一支团队积累成为多个团队起点'),('summary',5015,5340,'relationship','两条 身份 泳道 步骤 当前 点亮','同一套算力接更多任务更少等待'),('talk-end',5340,5654,None,'','AI服务更快更便宜')]
m={'content_id':'deepseek-deepinfer-20261021','variant':'fred-full-remake-v1','version':'v1','timelineFps':60,'durationInFrames':5654,'outputSpec':{'width':1080,'height':1920,'fps':60},'workflow':{'profile':'fred-video-v2','componentMatching':'v1'},'pages':[]}
for sid,a,b,typ,q,txt in scenes:
 p={'stableId':sid,'startFrame':a,'durationInFrames':b-a,'oneQuestion':txt,'sourceSpans':[{'text':txt}],'implementationMode':'adapted' if typ else 'preserved-media','referenceChoices':[]}
 if typ:p.update(sceneGuide={'type':typ},componentPlan={'query':q})
 else:p.update(mediaContract=[{'path':str(r.parent/'04-完整制作/output/talking-source-v1.mp4'),'sha256':'c0dc321bb50c73d91136b2f72d8faf4c9da30a086171d5496dd0f97725bbd318','sourceInSeconds':a/60,'sourceOutSeconds':b/60}])
 m['pages'].append(p)
(r/'Manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
for p in m['pages']:
 if p['implementationMode']=='preserved-media':continue
 out=subprocess.check_output(['python3',str(root/'skills/fred-remotion-output/scripts/scene.py'),'--project-root',str(root),'--manifest',str(r/'Manifest.json'),'--scene-id',p['stableId'],'--candidates-only'])
 (r/'evidence'/f"{p['stableId']}-candidates.json").write_bytes(out)
 d=json.loads(out);print(p['stableId'],[(x['label'],x['title']) for x in d['libraryCandidates']['candidates'][:3]])
