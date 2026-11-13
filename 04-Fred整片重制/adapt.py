from pathlib import Path
import json,shutil,re,difflib
R=Path(__file__).resolve().parent
C=json.loads(Path('/Volumes/EXTERNAL/自媒体/资产库/视频制作总览/catalog.json').read_text())['components']
def adapt(label, replacements):
    item=next(x for x in C if x['label']==label)
    source=Path(item['sources'][0]['path']);old=source.read_text();new=old
    for a,b in replacements:
        assert a in new,(label,a)
        new=new.replace(a,b)
    out=R/'src/components'/source.name;out.write_text(new)
    (R/'evidence'/f'{label}-adaptation.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=str(source),tofile=str(out))))

# Full existing T22a, with native portrait camera and CSS cropping of the account header.
adapt('T22a',[
 ('  cues?: number[];', '  established?: boolean; returnAt?: number;\n  cues?: number[];'),
 ('const MAX_CARD = { w: 1280, h: 760 };','const MAX_CARD = { w: 960, h: 1050 };'),
 ('x: 960 - cw / 2, y: 540 - ch / 2 + 10','x: 540 - cw / 2, y: 800 - ch / 2'),
 ('const enter = p(t, 0, 0.7);','const enter = c.established ? 1 : p(t, 0, 0.7);\n  const retreat = c.returnAt === undefined ? 0 : quintic(t,c.returnAt,c.returnAt+0.7);'),
 ('const brush = p(t, brushAt, brushAt + 0.6);','const brush = p(t, brushAt, brushAt + 0.6) * (1-retreat);'),
 ('const push = quintic(t, pushAt, pushAt + 0.7);','const push = quintic(t, pushAt, pushAt + 0.7) * (1-retreat);'),
 ('const trans = p(t, transAt, transAt + 0.55);','const trans = p(t, transAt, transAt + 0.55) * (1-retreat);'),
 ('Math.min(2.1, 1500 / ln.w)','Math.min(5.0, 860 / ln.w)'),
 ('const maxW = 1560;','const maxW = 900;'),
 ('Math.min(68,','Math.min(88,'),
 ('const GAP = 52;','const GAP = 86;'),
 ('540 - groupH / 2','900 - groupH / 2'),
 ('(540 - LINE_SCREEN_Y)','(900 - LINE_SCREEN_Y)'),
 ('const camera = cameraTransform(fx, fy, zoom, push);','const camera = `translate(540px,900px) scale(${mix(1,zoom,push)}) translate(${-mix(540,fx,push)}px,${-mix(900,fy,push)}px)`;'),
 ('left: 0, top: 0, width: cw, height: ch, display:', 'left: 0, top: -100*k, width: cw, height: ch+100*k, display:'),
])

# Full pixel-lift component: portrait vertical slots, retaining ROI source-to-destination interpolation.
adapt('T04e',[
 ('const TOP = 140, BOTTOM = 880;','const TOP = 260, BOTTOM = 1560;'),
 ('1500 / cc.w','960 / cc.w'),
 ('x: 960 - CW / 2','x: 540 - CW / 2'),
 ('1400 / Math.max(1, dUnits(c.result))','780 / Math.max(1, dUnits(c.result))'),
 ('const s = Math.min(1.0,','const s = Math.min(2.35,'),
 ('(1760 - (n - 1) * GAP - n * 2 * PAD) / parts.reduce((a, pt) => a + pt.box.w, 0)','740 / Math.max(...parts.map(pt=>pt.box.w))'),
 ('const groupH = rH + G1 + maxH + G2 + lH;','const groupH = rH + G1 + hs.reduce((a,b)=>a+b,0) + n*(G2+lH)+(n-1)*64;'),
 ('x: 960 - rW / 2','x: 540 - rW / 2'),
 ('const slots: Box[] = parts.map((_, i) => ({ x: 960 - rowW / 2 + ws.slice(0, i).reduce((a, b) => a + b, 0) + i * GAP, y: midY - hs[i] / 2, w: ws[i], h: hs[i] }));','const slots: Box[] = parts.map((_,i)=>({x:540-ws[i]/2,y:gTop+rH+G1+hs.slice(0,i).reduce((a,b)=>a+b,0)+i*(G2+lH+64),w:ws[i],h:hs[i]}));'),
 ('const fill = (src: string) => <Img src={staticFile(src)} style={{ position: \'absolute\', left: 0, top: 0, width: \'100%\', height: \'100%\', display: \'block\' }} />;',
  'const fill = (src:string, crop:Box=cc) => <svg width="100%" height="100%" viewBox={`${crop.x} ${crop.y} ${crop.w} ${crop.h}`} preserveAspectRatio="none"><image href={staticFile(src)} width={1265} height={712}/></svg>;'),
 ('{fill(pt.image)}','{fill(pt.image,pt.box)}'),
 ('`960px ${card.y + card.h / 2}px`','`540px ${card.y + card.h / 2}px`'),
 ('y: pillY + (1 - e) * 14','y: slots[i].y+slots[i].h+G2 + (1 - e) * 14'),
 ('x: 960 - (rW * res) / 2','x: 540 - (rW * res) / 2'),
])

adapt('T04f',[
 ('const CORE = { x: 760, y: 540, r: 98 };','const CORE = { x: 790, y: 420, r: 98 };'),
 ('const CARD_X = 1010, CARD_W = 800, GAP = 34;','const CARD_X = 235, CARD_W = 740, GAP = 74;'),
 ('const y0 = (1080 - (n * CH + (n - 1) * GAP)) / 2;','const y0 = 800;'),
 ('width={1920} height={1080}','width={1080} height={1920}'),
 ('M ${CORE.x + CORE.r - 4} ${CORE.y} H ${CORE.x + CORE.r + 70} V ${cy(i)} H ${CARD_X - 6}', 'M ${CORE.x} ${CORE.y + CORE.r - 4} V 660 H 140 V ${cy(i)} H ${CARD_X - 6}'),
])

adapt('T13a',[
 ('const W = 1120;','const W = 860;'),('const CX = 960;','const CX = 540;'),('const CY = 498;','const CY = 880;'),('const PAD = 60;','const PAD = 42;'),
 ('n <= 3 ? 136','n <= 3 ? 210'),('n <= 3 ? 48','n <= 3 ? 60'),('n <= 3 ? 30','n <= 3 ? 74'),
 ('width={1920} height={1080}','width={1080} height={1920}'),('${1920 - x0 - W * sw}','${1080 - x0 - W * sw}'),
])
adapt('T03d',[
 ('const STEP_X = 150;','const STEP_X = 56;'),('const ROW_GAP = 40;','const ROW_GAP = 120;'),
 ('n > 4 ? 118 : 140','n > 4 ? 160 : 210'),('n > 4 ? 160 : 196','n > 4 ? 190 : 220'),
 ('1760 - i * STEP_X','920 - i * STEP_X'),('960 - e.wid / 2, ty = 540 - e.hei / 2','540 - e.wid / 2, ty = 880 - e.hei / 2'),
])
adapt('T04d',[
 ('860 / (1.2','1200 / (1.2'),('1500 / (textWidth','900 / (textWidth'),
 ('960 - treeW / 2, ty = 540 - treeH / 2 + 10','540 - treeW / 2, ty = 880 - treeH / 2'),
 ('x: 960 - root.w * 0.6, y: 540 - root.h * 0.6','x: 540 - root.w * 0.6, y: 880 - root.h * 0.6'),
 ('Math.min(150, 1400 /','Math.min(132, 820 /'),
 ('x: 960 - fp.w / 2, y: 540 - fp.h / 2','x: 540 - fp.w / 2, y: 880 - fp.h / 2'),
 ('width={1920} height={1080}','width={1080} height={1920}'),
])

# Keep T02g complete card layers, reverse-color wipe, completion checks and behind-role extraction;
# transpose lanes into two columns. A cue schedule advances focus without rebuilding cards.
adapt('T02g',[
 ('  cues?: number[];', '  focusSchedule?: {at:number;lane:number;step:number}[];\n  cues?: number[];'),
 ('const CARD_H = nL >= 3 ? 190 : 236;','const CARD_H = 236;\n  const ROLE_H=174;'),
 ('const roleW = roleUnits * roleSize + roleSize * 1.3;','const roleW = 390;'),
 ('const cardW = Math.min(400, (AREA_W - roleW - ROLE_GAP - GAP * (maxSteps - 1)) / maxSteps);','const cardW = 390;'),
 ('const X0 = 960 - groupW / 2;','const X0 = 105;'),
 ('const laneY = (i: number) => 540 - totalH / 2 + 12 + i * (CARD_H + LANE_GAP);','const laneY = (i: number) => 370;\n  const laneX=(i:number)=>X0+i*480;'),
 ('const cur = c.current &&', 'const active=c.focusSchedule?.filter(x=>x.at<=t).at(-1);\n  const chosen=active ?? c.current;\n  const cur = chosen &&'),
 ('c.current.lane','chosen.lane'),('c.current.step','chosen.step'),('? c.current : null','? chosen : null'),
 ('const focusAt = current ? cueAt(c.cues, 0, 0.3) : cueAt(c.cues, nL, laneAt(nL - 1) + 1.2);','const focusAt = active?.at ?? (current ? cueAt(c.cues, 0, 0.3) : cueAt(c.cues, nL, laneAt(nL - 1) + 1.2));'),
 ('const roleRight = X0 + roleW;','const roleRight = y + ROLE_H;'),
 ("left: roleRight - 2, top: y - 80, width: 1920 - roleRight, height: CARD_H + 180", "left: laneX(li)-55, top: roleRight-2, width: cardW+110, height: 1100"),
 ('const sa = a + 0.24 + j * 0.085;','const sa = a + 0.24 + j * 0.32;'),
 ('const x = mix(roleRight - cardW - 48, cardX(j), e) - (roleRight - 2);','const x = mix(-CARD_H-48, 64+j*(CARD_H+72),e);'),
 ('left: x, top: 80 - 22 * lift','left: 55, top: x - 22 * lift'),
 ('...abs({ x: X0, y, w: roleW, h: CARD_H }), borderRadius: CARD_H / 2','...abs({ x: laneX(li), y, w: roleW, h: ROLE_H }), borderRadius: ROLE_H / 2'),
 ('...textBase(roleSize, 400, S.display)','...textBase(roleSize, 900, S.body)'),
])

# No action SFX added: this remake preserves the exact original full voice track only.
p=R/'src/kit/ui.tsx';s=p.read_text();s=s.replace('volume = 0.12','volume = 0');p.write_text(s)
old=Path('/Volumes/EXTERNAL/自媒体/deepseek-deepinfer-20261021/04-完整制作')
for src,name in [(old/'assets/github-original.png','github-original.png'),(old/'audio/voice-original-speed.wav','voice-original-speed.wav'),(old/'output/talking-source-v1.mp4','talking-source-v1.mp4')]:
    shutil.copy2(src,R/'public'/name)
shutil.copy2(old/'output/deepinfer-v1.srt',R/'output/deepinfer-fred-v1.srt')
caps=[]
for b in (old/'output/deepinfer-v1.srt').read_text().strip().split('\n\n'):
    lines=b.splitlines()
    if len(lines)<3:continue
    def secs(t):
        h,m,s=t.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(s)
    a,z=lines[1].split(' --> ');caps.append({'start':secs(a),'end':secs(z),'text':''.join(lines[2:])})
(R/'src/captions.json').write_text(json.dumps(caps,ensure_ascii=False))
(R/'package.json').write_text(json.dumps({'name':'deepinfer-fred-remake','private':True,'version':'1.0.0','dependencies':{'remotion':'4.0.451','@remotion/cli':'4.0.451','react':'19.2.5','react-dom':'19.2.5'}},indent=2))
