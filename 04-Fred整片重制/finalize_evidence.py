from pathlib import Path
import json,hashlib,sys
R=Path(__file__).resolve().parent;E=R/'evidence';sys.path.insert(0,str(R/'fred-runtime/skills/fred-remotion-output/scripts'))
from library_gate import acceptance_signature
from component_distribution import analyze
from common import load_references

def rec(p):p=Path(p);return {'path':str(p.resolve()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
m=json.loads((R/'Manifest.json').read_text());v=rec(R/'output/deepinfer-fred-full-v1.mp4')
idx=json.loads((E/'final-frame-index.json').read_text());idx['extractedFromInitialContainer']=idx['video'];idx['video']=v;idx['remuxIdentity']=rec(E/'video-remux-identity.json');idx['note']='48原尺寸帧和189概览帧提取自初次容器；最终仅替换音轨，图像压缩包SHA一致，故像素证据仍适用。';(E/'final-frame-index.json').write_text(json.dumps(idx,ensure_ascii=False,indent=2))
observed={
 'repo':'7.5–8.5秒标题原像素与开源释义清楚；账户区域已裁，8秒原尺寸文字与字幕分离。原截图放大有源分辨率限制。',
 'stars':'13.5秒推进、14–15秒原Star14.1k和一万多颗星停稳；14秒原尺寸无剩余灰蒙版框线，旧释义随归位退去。',
 'code':'17秒真实区域框选后拎出，20–21秒第二块穿过第一块标签时属于原组件前后层路径；22秒两块、标签、顶部结论与底字幕均可见不裁字。',
 'request':'24–35秒双路线、请求吞入、返回胶囊停靠均见；36.8–37.75秒服务器收成胶囊，37.75秒原尺寸交接保留坐标和完整白字。',
 'roles':'39秒拆分中间空胶囊为原组件显隐；39.5–42秒两职责与工具卡依次建立；43秒后不再延长原样片停留。',
 'pipeline':'43.5–45秒双列抽卡、45.5–47.5秒CPU与GPU反色焦点转换；49秒接新任务；47.033秒原尺寸仅当前步骤清晰，其余按原组件淡化。',
 'open':'57.5秒锁芯建立，59.5–64秒钥匙转动和三能力依次解锁；64.5秒原尺寸支线留短间隙接卡，文字和字幕不重叠。',
 'layers':'66.5–68秒厚板叠起，69.5–70秒底层擦黑；70.166秒原尺寸顶面厚度、影子和模型硬件适配完整。',
 'progress':'73秒积累、74.5秒少摸索、76.5秒黑结果依次推出；77–78.5秒阅读，台阶偏移保留，无字溢出。',
 'shared':'79–82秒根与团队分支先后展开；82.5秒更多团队移到中央；82.833秒原尺寸字与胶囊边距正常，未杜撰团队数。',
 'summary':'84秒直接复现已建立双列；85.5秒GPU接新任务；87.5秒CPU继续安排，焦点变化保留前序勾；89秒切真人。'}
for p in m['pages']:
 sid=p['stableId'];a=p['startFrame'];b=a+p['durationInFrames']
 if not p.get('referenceChoices'):continue
 sheets=sorted(set(int((f/60*2)//24)+1 for f in range(a,b,30)))
 sheetrec=[rec(E/f'full-sheet-{i:02}.jpg') for i in sheets]
 native=[x for x in idx['frames'] if a<=x['frame']<b]
 p['keyframeReview']={'status':'assistant-reviewed-sampled-output','frames':sheetrec+native,'sourceFiles':[rec(R/'src/index.tsx')]+[ref['implementation'] for ref in p['referenceChoices']],'artifact':v,'scope':'全片2fps概览189帧均实际查看；8张当前原尺寸精查；代表片段4fps图49帧已看。非连续正常速度观看。','observations':observed[sid],'normalSpeed':'UNKNOWN','directHearing':'UNKNOWN'}
 p['componentAcceptance']={'status':'passed','reviewer':'assistant','stage':'keyframes','checks':{'semanticFit':p['referenceChoices'][0]['reason'],'corePreserved':p['referenceChoices'][0]['change'],'visualQuality':observed[sid]+' 仅采样范围通过；连续声画不包含。'},'evidence':sheetrec}
 p['componentAcceptance']['contextSha256']=acceptance_signature(m,p,'keyframes')
m['export']={**v,'bytes':(R/'output/deepinfer-fred-full-v1.mp4').stat().st_size,'videoFrames':5654,'videoSeconds':5654/60,'audioSeconds':94.233333,'remux':'图像copy，原WAV直接AAC320k封装，修正初次容器42.6ms延迟','audioEvidence':rec(E/'audio-preservation.json'),'videoIdentity':rec(E/'video-remux-identity.json')}
_,n=load_references(R/'fred-runtime');audit=analyze(m,n);m['componentDistributionReview']['contextSha256']=audit['contextSha256'];m['componentDistributionReview']['stage']='actual full output overview sampled; no continuous audiovisual claim'
for d in m['componentDistributionReview']['decisions']:d['evidence']=[rec(E/f'full-sheet-{i:02}.jpg') for i in ([1,2] if 'repo' in d['sceneIds'] else [4,5,8])]
m['reviewCoverage']={'overview':'0–94.0秒，步长0.5秒，189帧；最后0.233秒另有末帧','nativeInspected':[480,840,1320,2265,2822,3870,4210,4970],'representative':'37.75–49.983秒导出样片4fps图49帧；另有先前原尺寸中间帧','notPerformed':['全片正常速度连续视听','直接听音','05独立质检','用户终审'],'gateLimit':'implementation静态regex误报仍FAIL；representative/formal未通过，不作为已批准发布版。'}
(R/'Manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
