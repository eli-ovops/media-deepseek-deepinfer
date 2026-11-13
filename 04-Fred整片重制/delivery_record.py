from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parent;E=R/'evidence'
def rec(p):p=Path(p);return {'path':str(p.resolve()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
m=json.loads((R/'Manifest.json').read_text());audio=json.loads((E/'audio-preservation.json').read_text());ui=json.loads((E/'compare-browser.json').read_text())
checks={'content_id':m['content_id'],'variant':m['variant'],'status':'04_COMPLETE_PREVIEW_DELIVERED_PENDING_PMO_REVIEW','timestamp':datetime.datetime.now().astimezone().isoformat(),'owner':'04 / 01a11a6f-49ef-7653-934a-4312979fd4e7','finalVideo':rec(R/'output/deepinfer-fred-full-v1.mp4'),'manifest':rec(R/'Manifest.json'),'subtitle':rec(R/'output/deepinfer-fred-v1.srt'),'compareUrl':'http://127.0.0.1:55291/',
 'passed':{'videoSpec':'1080×1920，60/1，5654帧，94.233333s；H.264 yuv420p；AAC48k','fullDecode':rec(E/'decode-final.json'),'originalPCM':'源WAV完全相同SHA；全轨原速；没有新配音/BGM/SFX','audioNumerical':{'bestLagSamples48k':audio['bestLagSamplesWithinPlusMinus24'],'zeroLagCorrelation':audio['zeroLagCorrelation'],'snrDb':audio['snrDb'],'evidence':rec(E/'audio-preservation.json')},'sourceReuse':'9个完整准确Fred源码派生，11图形场景，3真人段；实际调用AST门通过','librarySuggestion':rec(E/'gate-suggestion-final.json'),'libraryKeyframes':rec(E/'gate-keyframes-final.json'),'planning':rec(E/'planning-final.json'),'visualSampleCoverage':m['reviewCoverage'],'browser':{'evidence':rec(E/'compare-browser.json'),'halfSpeedDriftMs':abs(ui['halfSpeedLive'][0]['time']-ui['halfSpeedLive'][1]['time'])*1000,'normalSpeedDriftMs':abs(ui['normalSpeedLive'][0]['time']-ui['normalSpeedLive'][1]['time'])*1000,'pausedSameFrame':ui['pausedFrame'][0]['time']==ui['pausedFrame'][1]['time'],'singleAudibleVideo':True,'pauseStatusFix':'源代码已改，reload后逐帧/跳转正常，UI截图evidence/compare-page-final.png'}},
 'notPassed':{'implementationGate':{'status':'FAIL','reason':'静态regex跨Sequence标签误匹配子Talk from={0}，真实首场Sequence没有from属性；保留失败，不修改门禁','evidence':rec(E/'implementation-final.json'),'analysis':rec(E/'clock-lint-analysis.json')},'representativeGate':'NOT_PASSED：没有正常速度连续视听证据，不虚填normalSpeed=true','formalGate':'NOT_PASSED：前序未全通过；技术规格/解码各自通过，不合并正式验收'},
 'unknown':['本片完整正常速度连续视听','直接听音/主观自然度','05独立质检（待PMO释放）','PMO验收','用户对新整片认可'],
 'repairs':[{'issue':'初次Remotion容器音轨晚约42.6ms','action':'原图像码流copy+原WAV独立AAC封装','result':'零偏移相关0.999985；图像包SHA不变','evidence':rec(E/'video-remux-identity.json')},{'issue':'T02g切焦旧状态硬复位','action':'沿原q曲线混合淡出/抬升/完成勾','result':'代表片段4fps及当前全片2fps/中间原尺寸检查无该硬复位'}],
 'limits':['真实仓库截图放大受原1265×712像素限制；没有重画官方UI','仅服务器→职责胶囊是几何连续交接，其他明确硬切处如43.35秒不称无缝形变','原13d请求段有已认可样片的阅读停留，未宣称全片每秒持续运动','本机本地依赖通过包链接复用；工程不是可直接跨机器运行的全打包依赖'],
 'handoff':{'artifactGenerated':True,'toolMessageSent':'PENDING','pmoReceived':'UNKNOWN','pmoAccepted':'PENDING','next':'PMO审真实原件后释放原05；问题回原04定向修复；无发布、无清理'}}
(R/'04-自检与交付.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2))
(R/'README.md').write_text('''# DeepInfer完整Fred重制 v1

当前为04完整可试看交付，待PMO及05验收。**不是全项验收通过或发布批准。**

- 完整片：`output/deepinfer-fred-full-v1.mp4`
- 当前SHA256：`'''+checks['finalVideo']['sha256']+'''`
- 1080×1920，原生60fps，5654帧，94.233333秒，约49.91MB。
- 新旧同步页：http://127.0.0.1:55291/ （仅本机；单路新版声音，半速、逐帧、章节跳转）
- 原声、原速、原字幕及源时钟不变；使用原纯真人底片。现有封面沿用，无新封面制作。

## 当前交付文件

`Manifest.json` 给出每场景准确源、预览、Top3选择、完整派生源码、实际调用、kit、段落时钟、输出SHA和检查范围。
`04-自检与交付.json` 为分层结论；`evidence/` 保存实际工具回执、原尺寸帧、全片189帧概览及音频保留计算。

最终画面使用T22a/T04e/T13d/T04b/T02g/T04f/T13a/T03d/T04d，11图形场景及3真人段。两次仓库ROI共用同图；末段复现前段GPU/CPU步骤。不是旧成片图形覆盖，也未用参考预览MP4充当新动效。

初次Remotion音轨延迟约42.6毫秒已修正：最终用原WAV直接AAC封装，图像包SHA完全一致。最终零偏移相关0.999985、SNR45.11dB，最佳偏移0采样。这些是数值证据，不是直接听音。

## 验证范围与尚未通过项

选型与关键帧库门禁实际PASS；最终规格和完整音视频解码PASS；已看全片0–94秒2fps共189帧、8张当前原尺寸帧，以及代表片段4fps图49帧和早前中间态。

implementation门实际FAIL：regex跨过Sequence标签边界，把子组件`Talk from={0}`误报为`Sequence from={0}`。准确解释见`evidence/clock-lint-analysis.json`，不修改门禁或假填PASS。
representative/formal阶段未通过；完整正常速度连续视听、直接听音、05独立质检、PMO与用户验收仍待完成。用户本任务明确要求先交完整成片与真实自检范围，因此提供可试看文件，不冒充全部验收通过。

## 重导出（同机现有依赖）

在本目录执行：

```sh
node render.cjs
python3 mux_audio.py
python3 qc_export.py --technical-only
python3 bind_compare.py
```

`render.cjs`先出`output/deepinfer-fred-picture-render.mp4`，`mux_audio.py`复制图像并装入原WAV到最终路径。改变源码后必须更新Manifest与相关证据，不能沿用旧门禁PASS。

如页面服务退出，在本目录运行`python3 serve.py`，读控制台新URL。要固定现有端口可用`CATALOG_PORT=55291 python3 serve.py`（仅端口空闲时）。服务只开放两条已绑定SHA文件，含Range、Host/Origin校验，无目录浏览。重导出/重绑后须重启本服务加载新allowlist。

本机依赖链接复用已存在Remotion4.0.451/React19.2.5，当前目录.cache独立；跨机器须按package.json安装对应依赖和Chrome。`src/`为冻结交付源码。`plan.py`、`adapt.py`、`refine.py`、`record_selection.py`、`complete_contract.py`为制作期间构建脚本，不能代替冻结源码或直接运行覆盖当前Manifest。

## 历史文件

`output/initial-remotion-audio-v1.mp4`为已否决音轨偏移的初次容器，**不交用户/不发布**；其图像与最终一致。`output/representative-v1.mp4`是内部12.25秒动作样本，不能冒充整片或最终音轨。旧版对比基准及认可26.3秒样片都保持原文件，未覆盖。
''')
print(checks['finalVideo'])
