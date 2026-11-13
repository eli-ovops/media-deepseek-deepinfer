from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,datetime,subprocess
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(path,data):(R/path).write_text(json.dumps(data,ensure_ascii=False,indent=2))
E=json.loads((R/'edl-v1.json').read_text());T=json.loads((R/'qc/technical-checks.json').read_text());C=json.loads((R/'covers/manifest.json').read_text())
scenes=[
 dict(id='real-open',frames=[0,162],type='preserved-media',source='N06'),
 dict(id='repository',frames=[162,946],type='adapted-sy',sources=['16-pagecam'],callsite='index.html:86 repository(t)',objects='真实仓库→原生Star焦点→一万多概括→源码符号',preserve='透视平面、读点停稳、推镜、前后层次',change='真实截图替换编辑台，保留原生数字'),
 dict(id='engine-copy',frames=[946,1422],type='adapted-sy',sources=['16-pagecam'],callsite='index.html:89 engine(t), panel() at50',objects='运行/调度/源码三层分离，副本独立去外部工位，原服务灯继续运行',preserve='Z separation *2.2，rotateX8/rotateY-19，焦点rack、panel几何及shadow',change='替换内容，移除作者按钮和身份，竖屏适配'),
 dict(id='cost-mechanism',frames=[1422,3000],type='adapted-sy',sources=['17-editorial','16-pagecam'],callsite='index.html:71 editorial(t), camAt()68, highlighter()67',objects='请求进入GPU轨，下轮CPU调度提前到本轮计算下方，其他任务接入可用时段',preserve='同页纸纹、log zoom、荧光笔、源spring任务入轨',change='删除原作者虚构调查/倍数，改为本期机制；无量化性能承诺'),
 dict(id='real-opinion',frames=[3000,3540],type='preserved-media',source='N11',note='36氪2024访谈转述短注'),
 dict(id='shared-engine',frames=[3540,5015],type='adapted-sy',sources=['16-pagecam'],callsite='index.html:91 sharing(t)',objects='核心模块保持形状，两工位继承同一起点，外围配套/适配/新优化补入',preserve='spring panel落位、层深和阴影，连续模块身份'),
 dict(id='same-compute',frames=[5015,5340],type='adapted-sy',sources=['16-pagecam'],callsite='index.html:96 closing(t)',objects='固定轨道内空隙接入任务',preserve='原clip入轨关系',change='不显示耗时或倍数'),
 dict(id='real-end',frames=[5340,5654],type='preserved-media',source='S1',note='原声保留有机会、更快更便宜')]
sources=[]
for name in ['16-pagecam','17-editorial','20-blueprint']:
 p=R/'source'/f'{name}.html';sources.append(dict(id=name,path=str(p),sha256=sha(p),selected=name!='20-blueprint',reason='软件页面空间/持续纸面适用' if name!='20-blueprint' else '已比较麦克风特定爆炸几何，与软件调度不匹配，未调用'))
base=R.parents[1]/'sy-styles-vertical-demo-20261017/04/qa'
refs=[]
for name,observation in [('t3.1.png','panel Z层次、透视、任务入轨、镜头推进'),('t14.5.png','同页巡读、长页图形、标记与字阶')]:
 p=base/name;refs.append(dict(path=str(p),sha256=sha(p),observations=observation))
shot=R/'assets/github-original.png'
capture=dict(url='https://github.com/deepseek-ai/DeepInfer',path=str(shot),sha256=sha(shot),captured_file_mtime=datetime.datetime.fromtimestamp(shot.stat().st_mtime,datetime.timezone(datetime.timedelta(hours=8))).isoformat(),method='IAB原生截图，实际读取项目身份及Star',visible_stars='14.1k',public_emphasis='一万多颗星',native_count_unchanged=True,crop='视频裁掉上方账号栏，只裁窗/缩放来源像素')
save('Manifest.json',dict(content_id='deepseek-deepinfer-20261021',version='v1',status='OWNER_COMPLETE_PENDING_PMO_05',fps=60,width=1080,height=1920,total_frames=5654,duration=5654/60,edl_path=str(R/'edl-v1.json'),audio='audio/voice-original-speed.wav',caption_path=str(R/'output/deepinfer-v1.srt'),designContract=dict(original_speed=True,source_clock='单EDL统一原声/真人/字幕/图形cue',no_glass=True,style='认可sy v5的准确源码及kit适配；不转移Fred私人品牌/音轨'),scenes=scenes,source_files=sources,inspectedReferences=refs,rejectedFredCandidates=[dict(id='T14a2',reason='计时赛跑易读成实测倍数，本期无同口径计时',actually_viewed='时间序列图/T14a2-1-preview-p01.jpg'),dict(id='T09f',reason='列表ROI飞行需要实际对应列表，本期不伪造软件界面',actually_viewed='时间序列图/T09f-1-preview-p01.jpg'),dict(id='L81-C003',reason='胶囊分支更适合分类，不能充分表现CPU/GPU交叠',actually_viewed='时间序列图/L81-C003-1-preview-p01.jpg')],source_capture=capture,technical_checks=T,remaining=['direct listening','word-level subtitle proof','continuous visual review','PMO acceptance','independent05','user approval'],route=dict(rule='ROUTING-2026-10-13-v4',initial_target='gpt-6-astra/high',resume_target='gpt-6.1-sol/high',reason='Astra容量不可用，PMO明确同Owner续接',actual_model='UNKNOWN',actual_effort='UNKNOWN',actual_speed='UNKNOWN',weekly_usage_dispatch='90%',five_hour_usage='UNKNOWN',subagents=False),source_gate=dict(type='native sy HTML/Canvas, no Remotion composition',remotion_canonical_gate_pass=None,evidence='准确源码/认可参考与本期代表样本对照；未冒充连续AV PASS')))
out=Image.new('RGB',(1200,620),'#ddd')
for i,c in enumerate(C):
 im=Image.open(c['path']);assert im.size==tuple(c['dimensions']);im.thumbnail((300,560));out.paste(im,(i*300+(300-im.width)//2,0));ImageDraw.Draw(out).text((i*300+8,575),Path(c['path']).name,fill='black')
out.save(R/'covers/phone-thumbnails.jpg',quality=95)
save('covers/generation-record.json',dict(tool='built-in image_gen imagegen; no paid API',identity_reference=str(R.parents[1]/'人物形象与封面资产-20261009/外部艺术照精选-20261009/入选/01-主形象-图2-棕色西装.png'),layout_reference=str(R.parents[1]/'qianwen-go-case-20261013/flow/06/封面/简体-白底本人-3x4-v3.png'),exact_title=['DeepSeek','省钱引擎','开源了'],colors=['black','black','vivid purple'],prompt_contract='White background, huge heavy black-purple exact headline; original reference preserves recognizable Eli face/hair/thin glasses only; change to light gray overshirt/charcoal tee, standing with laptop, violet code chip as visual metaphor; independently re-layout each 3:4/9:16/16:9/4:3, no headline overlap, no extra text/cards, all characters fully visible.',rework='3:4移开人头以完整显出尾字；16:9下移电脑以让开了的底钩；原始生成文件保留',scope='内置工具生成艺术封面，未声称真实拍照或DeepInfer硬件产品',finals=C))
files=[]
for p in sorted(R.rglob('*')):
 if p.is_file() and not p.is_symlink():files.append(dict(path=str(p),bytes=p.stat().st_size,mtime=datetime.datetime.fromtimestamp(p.stat().st_mtime).isoformat(),purpose='交付/工程复现/来源/QC证据，保留'))
save('file-inventory.json',dict(scope=str(R),total_bytes=sum(x['bytes'] for x in files),files=files,cleanup='PAUSED per task; all retained',df=subprocess.check_output(['df','-k',str(R)],text=True)))
save('delivery-v1.json',dict(content_id='deepseek-deepinfer-20261021',status='PENDING_PMO_REVIEW',video=T['file'],sha256=T['sha256'],spec=dict(width=1080,height=1920,fps=60,duration=94.233333,frames=5654,audio='AAC48kHzmono'),subtitles=str(R/'output/deepinfer-v1.srt'),edl=str(R/'edl-v1.json'),project=str(R),manifest=str(R/'Manifest.json'),report=str(R/'制作自检与交付-v1.md'),covers=[x['path'] for x in C],playback=json.loads((R/'playback-url.json').read_text()),qc_sheets=[str(R/'qc/final-overview.jpg'),str(R/'qc/all-caption-crops.jpg')],not_verified=['直接听音/口误清除','逐词字幕同步','连续视觉/衔接自然度','PMO/05/用户验收'],cleanup=False,publishing_authorized=False))
print('Packaged',len(files),'files; total',sum(x['bytes'] for x in files),'bytes')
