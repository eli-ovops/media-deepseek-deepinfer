# DeepInfer完整Fred重制 v1

当前为04完整可试看交付，待PMO及05验收。**不是全项验收通过或发布批准。**

- 完整片：`output/deepinfer-fred-full-v1.mp4`
- 当前SHA256：`0c4db02c6f30f16319fe80902db1f17eae4f676731d3688e8d90d940b5c85eac`
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
