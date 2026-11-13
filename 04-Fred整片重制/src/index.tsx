import React from 'react';
import {AbsoluteFill, Audio, Composition, OffthreadVideo, Sequence, registerRoot, staticFile, useCurrentFrame} from 'remotion';
import {PostCard} from './components/T22a-PostCard';
import {PackOpen} from './components/T04e-PackOpen';
import {RequestTrip} from './components/T13d-RequestTrip';
import {RoleSplit} from './components/T04b-RoleSplit';
import {RoleRoadmap} from './components/T02g-RoleRoadmap';
import {KeyUnlock} from './components/T04f-KeyUnlock';
import {StackLayers} from './components/T13a-StackLayers';
import {CauseChain} from './components/T03d-CauseChain';
import {CategoryFocus} from './components/T04d-CategoryFocus';
import {Fonts} from './kit/ui';
import captions from './captions.json';

export function RepoScene(){return <PostCard image="github-original.png" imageWidth={1265} imageHeight={612} line={{x:28,y:18,w:180,h:34}} translation="DeepInfer 开源" highlight="开源" cues={[2.05,4.15]} returnAt={5.92}/>;}
export function StarsScene(){return <PostCard established image="github-original.png" imageWidth={1265} imageHeight={612} line={{x:1080,y:18,w:148,h:34}} translation="一万多颗星" highlight="一万多" cues={[2.35,3.75]} returnAt={5.7}/>;}
export function CodeScene(){return <PackOpen establishedCard={{x:60,y:800-(612*960/1265)/2,w:960,h:612*960/1265}} cardImage="github-original.png" cardCrop={{x:0,y:100,w:1265,h:612}} parts={[
 {image:'github-original.png',box:{x:24,y:294,w:220,h:123},label:'核心代码'},
 {image:'github-original.png',box:{x:24,y:418,w:220,h:115},label:'文档与示例'},
]} result="同行接着研究和改造" highlight="研究和改造" cues={[1.2,3.85,5.25]}/>;}
export function RequestScene(){return <RequestTrip you={{name:'用户',logo:'users.svg'}} server={{kicker:'响应用户请求',name:'推理服务',sub:'计算资源 · 服务成本'}} addressLabel="工程层" address="DeepInfer" request="用户请求" result="返回结果" highlight="结果" timeLabel="" cues={[3.75,6.49,8.45]}/>;}
export function RolesScene(){return <RoleSplit task="协同处理" roles={[{step:'计算这一轮',tool:'显卡 GPU',logo:'gpu.svg'},{step:'提前安排下一轮',tool:'处理器 CPU',logo:'cpu.svg'}]} highlight="" cues={[0.95,1.8,3.4]}/>;}
const lanes=[{role:'GPU',steps:['本轮计算','下一轮计算','接新任务']},{role:'CPU',steps:['提前安排','下一轮就绪','继续安排']}];
export function PipelineScene(){return <RoleRoadmap lanes={lanes} mode="overview" current={null} cues={[0,0.4]} focusSchedule={[{at:2.0,lane:1,step:1},{at:3.65,lane:0,step:1},{at:5.05,lane:0,step:2}]}/>;}
export function OpenScene(){return <KeyUnlock keyName="工程成果" abilities={[{label:'读懂代码',sub:'已有实现可研究'},{label:'接着改造',sub:'在已有成果上继续做'},{label:'继续创新',sub:'投入新的优化'}]} cues={[1.7,2.0,3.9,6.25]}/>;}
export function LayersScene(){return <StackLayers layers={[{name:'线上配套',item:'仍待补齐'},{name:'推理框架',item:'DeepInfer'},{name:'模型与硬件',item:'还需适配'}]} focus={2} note="不同环境，还需完成适配" highlight="适配" cues={[0,0.55,1.1,3.0]}/>;}
export function ProgressScene(){return <CauseChain steps={['已有工程积累','少摸索一部分','投入新的优化']} highlight="新的优化" cues={[0.05,1.4,3.55]}/>;}
export function SharedScene(){return <CategoryFocus topic="工程积累" categories={['团队 A','团队 B','更多团队']} focus={2} cues={[1.0,1.6,2.2,3.15]}/>;}
export function SummaryScene(){return <RoleRoadmap lanes={lanes} mode="current" current={null} focusSchedule={[{at:0,lane:0,step:1},{at:1.5,lane:0,step:2},{at:3.45,lane:1,step:2}]}/>;}
function Talk({from}:{from:number}){return <OffthreadVideo src={staticFile('talking-source-v1.mp4')} startFrom={from} muted style={{width:'100%',height:'100%',objectFit:'cover'}}/>;}
export function Full(){
 const frame=useCurrentFrame(),t=frame/60,caption=captions.find(c=>t>=c.start&&t<c.end);
 const talking=frame<162||(frame>=3000&&frame<3438)||frame>=5340;
 return <AbsoluteFill style={{background:'#fff'}}>
  <Fonts/>
  <Sequence durationInFrames={162}><Talk from={0}/></Sequence>
  <Sequence from={162} durationInFrames={398}><RepoScene/></Sequence>
  <Sequence from={560} durationInFrames={386}><StarsScene/></Sequence>
  <Sequence from={946} durationInFrames={476}><CodeScene/></Sequence>
  <Sequence from={1422} durationInFrames={843}><RequestScene/></Sequence>
  <Sequence from={2265} durationInFrames={336}><RolesScene/></Sequence>
  <Sequence from={2601} durationInFrames={399}><PipelineScene/></Sequence>
  <Sequence from={3000} durationInFrames={438}><Talk from={3000}/></Sequence>
  <Sequence from={3438} durationInFrames={552}><OpenScene/></Sequence>
  <Sequence from={3990} durationInFrames={372}><LayersScene/></Sequence>
  <Sequence from={4362} durationInFrames={373}><ProgressScene/></Sequence>
  <Sequence from={4735} durationInFrames={280}><SharedScene/></Sequence>
  <Sequence from={5015} durationInFrames={325}><SummaryScene/></Sequence>
  <Sequence from={5340} durationInFrames={314}><Talk from={5340}/></Sequence>
  <Audio src={staticFile('voice-original-speed.wav')}/>
  {caption&&<div style={{position:'absolute',left:65,right:65,top:1710,textAlign:'center',fontFamily:'Fred MiSans',fontWeight:600,fontSize:48,lineHeight:1.4,color:talking?'#fff':'#19191c',textShadow:talking?'0 2px 7px #000,0 1px 3px #000':undefined}}>{caption.text}</div>}
 </AbsoluteFill>;
}
registerRoot(()=> <Composition id="Full" component={Full} width={1080} height={1920} fps={60} durationInFrames={5654}/>);
