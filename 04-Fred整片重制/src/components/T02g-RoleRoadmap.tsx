// T02g-RoleRoadmap：两个身份路线图
// 观众要看懂的变化：两条身份泳道 → 各自的步骤依次排开；回现时当前一步被点亮
// 动作：overview —— 每条泳道左侧的身份黑胶囊先立住，这条身份要走的步骤卡从胶囊背后依次抽出、排到右侧；
//       current —— 从终态直接开始（不重新入场），当前一步抬起变黑，同泳道已完成的退灰打勾、未到的退灰，另一条泳道整体退后。
// 与库内区分：T02a 是单排编号卡依次立起、再抬起当前项；这里是“身份 → 它的几步”两条泳道，步骤从身份里抽出，
//            点亮时同时交代完成 / 当前 / 未到三种状态。
// 规则：外观、动效、字体、音效只用 ../kit（见 DESIGN.md 第 2 节）；所有内容走 props；不改 kit。
import React from 'react';
import { S, accentOn, clamp, cueAt, mix, p, q, textWidth } from '../kit/theme';
import { Frame, Handoff, HandoffProps, Sfx, abs, textBase, useT } from '../kit/ui';

export type RoleLane = { role: string; steps: string[] };
export type RoleRoadmapProps = HandoffProps & {
  lanes: RoleLane[];                              // 1–3 条泳道，每条 1–5 步；步骤名可用 \n 指定断行
  mode: 'overview' | 'current';                   // overview：依次建立；current：从终态开始，点亮当前一步
  current: { lane: number; step: number } | null; // 当前一步（0 起）；overview 下传了也会在建立完后点亮
  focusSchedule?: {at:number;lane:number;step:number}[];
  cues?: number[];                                // overview：[i]=第 i 条泳道开始建立，[泳道数]=点亮；current：[0]=点亮
};

// 默认内容：第 114 期 S03 路线图（逐字稿 v6 制作备注：使用者 找→下载→授权→跑起来；上传者 传上去→三个文件）
export const roleRoadmapDefaults: RoleRoadmapProps = {
  lanes: [
    { role: '使用者', steps: ['找项目', '下载哪个', '授权 CLI', '跑起来'] },
    { role: '上传者', steps: ['传上去', '三个文件'] },
  ],
  mode: 'overview',
  current: null,
};

// 比 kit textWidth 稍保守：大写拉丁字母按 0.68 估（MiSans Heavy 大写偏宽）
const tw = (s: string, size: number) =>
  Array.from(s).reduce((w, ch) => w + (/[A-Z]/.test(ch) ? 0.68 : /[\u0000-ÿ]/.test(ch) ? 0.58 : 1) * size, 0);

// 两行均衡断开（拉丁词不拆）
function splitTwo(s: string): string[] {
  const tokens = s.match(/[A-Za-z0-9.\-_/+#]+|\s+|./gu) ?? [s];
  const total = tw(s, 1);
  let best = 1, bestScore = Infinity, acc = 0;
  for (let i = 1; i < tokens.length; i++) {
    acc += tw(tokens[i - 1], 1);
    if (/^[，,、。：:；;！!？?]$/.test(tokens[i])) continue;
    const score = Math.abs(acc - total / 2) + (/^\s+$/.test(tokens[i - 1]) ? -0.6 : 0);
    if (score < bestScore) { bestScore = score; best = i; }
  }
  return [tokens.slice(0, best).join('').trim(), tokens.slice(best).join('').trim()].filter(Boolean);
}

// rgb 插值（白卡 → 黑卡、墨字 → 白字 / 灰字）
const hex = (h: string) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
const lerpColor = (a: string, b: string, v: number) => {
  const A = hex(a), B = hex(b);
  return `rgb(${A.map((x, i) => Math.round(mix(x, B[i], clamp(v)))).join(',')})`;
};

const AREA_W = 1760;       // 整组最大宽
const ROLE_GAP = 46;       // 身份胶囊到第一张卡
const GAP = 24;            // 卡与卡
const LANE_GAP = 64;       // 泳道之间
const PAD = 26;            // 卡内边距

export function RoleRoadmap(props: Partial<RoleRoadmapProps>) {
  const c = { ...roleRoadmapDefaults, ...props };
  const t = useT();
  const lanes = c.lanes.slice(0, 3).map((l) => ({ role: l.role, steps: l.steps.slice(0, 5) }));
  const nL = Math.max(1, lanes.length);
  const maxSteps = Math.max(1, ...lanes.map((l) => l.steps.length));

  // —— 版式：所有泳道共用身份胶囊宽度和卡宽，列与列严格对齐 ——
  const CARD_H = 236;
  const ROLE_H=174;
  const roleUnits = Math.max(1, ...lanes.map((l) => textWidth(l.role, 1)));
  const roleSize = Math.min(nL >= 3 ? 88 : 104, 330 / roleUnits);   // 身份名长时收字号，把宽度留给步骤卡
  const roleW = 390;
  const cardW = 390;
  const inner = cardW - PAD * 2;
  const allSteps = lanes.flatMap((l) => l.steps);
  // 卡内标题：一行放得下 ≥44px 就一行，否则两行；所有卡共用一个字号
  const lineFit = (s: string) => Math.min(56, inner / Math.max(1, tw(s, 1)));
  const twoLine = (s: string) => s.includes('\n') || lineFit(s) < 42;
  const linesOf = (s: string) => (s.includes('\n') ? s.split('\n').slice(0, 2) : twoLine(s) ? splitTwo(s) : [s]);
  const labelSize = Math.min(56, ...allSteps.map((s) => Math.min(...linesOf(s).map((l) => inner / Math.max(1, tw(l, 1))))),
    ...allSteps.filter(twoLine).map(() => (CARD_H - PAD * 2 - 48) / (2 * 1.16)));
  const groupW = roleW + ROLE_GAP + maxSteps * cardW + (maxSteps - 1) * GAP;
  const X0 = 105;
  const totalH = nL * CARD_H + (nL - 1) * LANE_GAP;
  const laneY = (i: number) => 370;
  const laneX=(i:number)=>X0+i*480;
  const cardX = (j: number) => X0 + roleW + ROLE_GAP + j * (cardW + GAP);

  // —— 时间 ——
  const current = c.mode === 'current';
  const active=c.focusSchedule?.filter(x=>x.at<=t).at(-1);
  const chosen=active ?? c.current;
  const cur = chosen && chosen.lane >= 0 && chosen.lane < nL && chosen.step >= 0 && chosen.step < lanes[chosen.lane].steps.length
    ? chosen : null;
  const laneAt = (i: number) => cueAt(c.cues, i, 0.1 + i * 1.7);
  const focusAt = active?.at ?? (current ? cueAt(c.cues, 0, 0.3) : cueAt(c.cues, nL, laneAt(nL - 1) + 1.2));
  const focus = cur ? q(t, focusAt, focusAt + 0.55) : 0;
  // current 模式：整张图第一帧就是终态
  const built = (v: number) => (current ? 1 : v);

  return <Frame>
    <Handoff enter={c.enter} exit={c.exit} exitAt={c.exitAt}>
      {lanes.map((lane, li) => {
        const y = laneY(li);
        const a = laneAt(li);
        const roleIn = built(p(t, a, a + 0.42));
        const isCurLane = !!cur && cur.lane === li;
        let laneDim = cur && !isCurLane ? focus : 0;
        if(c.focusSchedule){laneDim=0;for(const event of c.focusSchedule){laneDim=mix(laneDim,event.lane===li?0:1,q(t,event.at,event.at+0.55));}}
        const roleRight = y + ROLE_H;
        return <div key={li} style={{ position: 'absolute', inset: 0, opacity: mix(1, 0.3, laneDim) }}>
          {/* 步骤卡：从身份胶囊背后抽出；裁切左边界就是胶囊右沿 */}
          <div style={{ position: 'absolute', left: laneX(li)-55, top: roleRight-2, width: cardW+110, height: 1100, overflow: 'hidden' }}>
            {lane.steps.map((step, j) => {
              const sa = a + 0.24 + j * 0.32;
              const e = built(p(t, sa, sa + 0.62));
              const x = mix(-CARD_H-48, 64+j*(CARD_H+72),e);   // 起点连投影一起藏在胶囊右沿之外
              let isCur = isCurLane && cur!.step === j;
              let done = isCurLane && j < cur!.step;
              const later = isCurLane && j > cur!.step;
              let lift = isCur ? focus : 0;
              let fade = done || later ? focus : 0;
              let check = done ? p(t, focusAt + 0.25, focusAt + 0.6) : 0;
              if(c.focusSchedule){
                lift=0;fade=0;check=0;
                for(const event of c.focusSchedule){
                  const v=q(t,event.at,event.at+0.55);
                  lift=mix(lift,event.lane===li&&event.step===j?1:0,v);
                  fade=mix(fade,event.lane===li&&event.step!==j?1:0,v);
                  check=mix(check,event.lane===li&&j<event.step?1:0,p(t,event.at+0.25,event.at+0.6));
                }
                done=check>0;isCur=lift>0.001;
              }
              // 共用字号定下来后，一行放得下的就不折行（避免“加 / License”这种断头）
              const lines = !step.includes('\n') && tw(step, labelSize) <= inner ? [step] : linesOf(step);
              const ink = lerpColor(S.ink, S.faint, fade);
              if (e <= 0) return null;
              const label = (color: string) => <div style={{ position: 'absolute', left: PAD, right: PAD, bottom: PAD - 2, color }}>
                {lines.map((l, k) => <div key={k} style={{ ...textBase(labelSize, 900), lineHeight: 1.16 }}>{l}</div>)}
              </div>;
              const num = (color: string, o = 1) => <div style={{ ...textBase(34, 900), position: 'absolute', left: PAD, top: PAD - 4, color, opacity: o }}>
                {String(j + 1).padStart(2, '0')}</div>;
              return <div key={j} style={{
                position: 'absolute', left: 55, top: x - 22 * lift, width: cardW, height: CARD_H,
                transform: `scale(${1 + 0.06 * lift})`, zIndex: isCur ? 20 : 10 - j,   // 先出的压在上面：后面的卡从它底下摊开
              }}>
                {lift > 0 && <div style={{ position: 'absolute', inset: 0, borderRadius: S.radius, background: S.dark, boxShadow: S.capsuleShadow, opacity: lift }} />}
                {/* 白卡层：墨字（已完成 / 未到的退成灰） */}
                <div style={{ position: 'absolute', inset: 0, borderRadius: S.radius, background: '#fff', boxShadow: S.shadow }} />
                {num(S.faint, done ? 1 - clamp(check * 2) : 1)}
                {done && check > 0 && <svg width={46} height={46} viewBox="0 0 46 46" style={{ position: 'absolute', left: PAD - 4, top: PAD - 6 }}>
                  <path d="M8 24 L19 34 L38 12" fill="none" stroke={S.accent} strokeWidth={7} strokeLinecap="round" strokeLinejoin="round"
                    strokeDasharray={50} strokeDashoffset={50 * (1 - check)} />
                </svg>}
                {label(ink)}
                {/* 黑面层：自下而上擦满整张卡，里面是同位置的白字 + 深底紫序号（两层文字反色，motion-craft §6） */}
                {lift > 0 && <div style={{
                  position: 'absolute', inset: 0, borderRadius: S.radius, background: S.dark, overflow: 'hidden',
                  clipPath: `inset(${100 * (1 - lift)}% 0 0 0 round ${S.radius}px)`,
                }}>
                  {num(accentOn(true))}
                  {label('#fff')}
                </div>}
              </div>;
            })}
          </div>
          {/* 身份胶囊 */}
          <div style={{
            ...abs({ x: laneX(li), y, w: roleW, h: ROLE_H }), borderRadius: ROLE_H / 2, background: S.dark, boxShadow: S.capsuleShadow,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            opacity: clamp(roleIn * 1.8), transform: `scale(${mix(0.82, 1, roleIn)})`,
          }}>
            <span style={{ ...textBase(roleSize, 900, S.body), color: '#fff' }}>{lane.role}</span>
          </div>
        </div>;
      })}
    </Handoff>
    {!current && lanes.map((_, i) => <Sfx key={i} name="pop" at={laneAt(i)} />)}
    {cur && <Sfx name="woosh" at={focusAt} />}
  </Frame>;
}
