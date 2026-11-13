from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parent;E=R/'evidence/v2'
def rec(p):p=Path(p);return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
m=json.loads((R/'Manifest-v2.json').read_text());samples=json.loads((E/'sample-index.json').read_text());comparison=json.loads((E/'unchanged-sample-comparison.json').read_text());probe=json.loads((E/'probe.json').read_text());v=next(s for s in probe['streams'] if s['codec_type']=='video')
report={'content_id':m['content_id'],'version':'fred-full-remake-v2','owner':'04','status':'Q1_Q2_REPAIRED_COMPLETE_FILE_READY_FOR_PMO','time':datetime.datetime.now().astimezone().isoformat(),'video':rec(R/'output/deepinfer-fred-full-v2.mp4'),'manifest':rec(R/'Manifest-v2.json'),'subtitle':rec(R/'output/deepinfer-fred-v2.srt'),'comparisonUrl':'http://127.0.0.1:55291/','videoSpec':{k:v.get(k) for k in ['codec_name','width','height','r_frame_rate','nb_frames','duration','pix_fmt','color_range']},'changes':{'Q1':'T22a镜头改为对最终屏幕仿射矩阵插值，保留quintic、zoom终点、材质、紫刷及翻译。标题/Star推近、停稳、归位的ROI完整留在安全画幅。','Q2':'T04e继承前场真实截图的裁剪和屏幕矩形、满可见度；0–0.7秒q曲线连续移动到原拆解基位，之后沿原描框与拎出cue。Star返回提早0.02秒结束以确保F945已经归位。'},'preserved':{'baselineV1':rec(R/'output/deepinfer-fred-full-v1.mp4'),'originalPublishedSha256':'b2dffec033eec5fb85192c98f45d8feaf54709125b6200fa21e056d8b67d230a','sourceScope':rec(E/'source-scope.json'),'audioAllPackets':rec(E/'audio-packet-identity.json'),'unaffectedDecodedFrames':comparison},'verified':{'actualExportFrames':len(samples['frames']),'ranges':'Q1 F408–558和F780–936，每6帧一次；Q2 F942–984逐帧，含故障和边界原尺寸精查。准确去重帧见sample-index。','geometry':rec(E/'roi-geometry.json'),'actualFrames':rec(E/'sample-index.json'),'decode':rec(E/'decode.json'),'keyframeGate':rec(E/'gate-keyframes-Q1Q2.json')},'notClaimed':{'normalSpeedContinuousAV':'UNKNOWN','directHearing':'UNKNOWN','independent05V2':'PENDING','pmoAcceptance':'PENDING','userApproval':'PENDING','allFilmReinspection':'NOT_REPEATED','implementationGate':'v1 FAIL retained, 05 independently confirmed regex false positive; not modified or rerun just to clear it'},'handoff':{'artifactCreated':True,'toolMessageSent':'PENDING','pmoReceived':'UNKNOWN','pmoAccepted':'PENDING'}}
(R/'04-返修自检-v2.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
(R/'README.md').write_text('''# DeepInfer Fred整片重制 · 当前v2

当前完整片：`output/deepinfer-fred-full-v2.mp4`  
SHA256：`'''+report['video']['sha256']+'''`  
1080×1920，60fps，5654帧，94.233333秒。仅修Q1/Q2，待PMO及05补验，不是发布批准。

[打开本机新旧同步对比](http://127.0.0.1:55291/)。页面绑定当前v2与已发布基准，提供标题/Star推近、截图交接等章节，半速、逐帧、单路声音保持。

## 两项修复

- Q1：T22a直接插值最终屏幕缩放/位移。标题和Star的推近/归位中途不再出画，原缓动、真实像素、紫刷、翻译及材质保留。
- Q2：F946直接继承F945的同一截图几何、裁剪和满可见度，再连续移到原拆解位置；取消白帧及重复淡入。其后描框、拎出、标签和结论时序保留。

其余组件、真人、字幕、5654帧时间线和现有封面不变。最终音轨直接复制被审v1的AAC包；全包内容和时间戳逐项相同，因此沿用已核原声保留证据，不重新做听核或重编码。

## 验证入口

`Manifest-v2.json`（与当前`Manifest.json`相同）是本版来源和调用链。`04-返修自检-v2.json`给出本次范围与结论。`evidence/v2/`保存实际导出中间帧、帧索引、几何补证、容器解码、保留范围、音轨包身份及本次限定三场景keyframes门禁。未重看全片，未把旧帧当新片全项验收。

连续正常速度视听与直接听音仍UNKNOWN；05针对v2补验、PMO验收及用户终审待完成。原静态implementation FAIL连同05跨标签regex误报判定保留；没有改全局门禁或为消误报改无关代码。

## 保留与重导出

v1完整MP4及其evidence/05原件保留，必要旧源码/Manifest快照见`evidence/v1-freeze/`。旧`README.md`在该快照中；`04-自检与交付.json`是历史v1结果，不作为当前交付结论。已发布基准及原26.3秒认可样片未修改。

当前重渲入口为`node render-v2.cjs`，输出无声picture-v2，然后按`evidence/v2/mux-command.json`从v1复制原AAC装入新完整文件。`qc-v2.py`包含本次一次性封装与必要检查，已有v2时不会静默覆盖；返修后应另命名输出并更新所有绑定证据。不要运行旧plan/adapt脚本覆盖冻结实现。

对比页断开时，在本目录运行`CATALOG_PORT=55291 python3 serve.py`（仅确认端口空闲时），或`python3 serve.py`获得新本机端口。文件绑定来自`python3 bind_compare-v2.py`；重新绑定后重启本任务服务，不能关闭其他服务。
''')
print(report['video'])
