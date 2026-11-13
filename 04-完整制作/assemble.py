from pathlib import Path
import subprocess,json,sys
R=Path(__file__).resolve().parent;FF='/Users/USER/.local/bin/ffmpeg'
edl=json.loads((R/'edl-v1.json').read_text()); rows=edl['keep_ranges']
def run(cmd,name):
 (R/'qc'/f'{name}-command.json').write_text(json.dumps(cmd,ensure_ascii=False,indent=2))
 with open(R/'qc'/f'{name}.log','w') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True)
if '--base' in sys.argv:
 cmd=[FF,'-n','-hide_banner']
 for r in rows:cmd+=['-i',r['source_path']]
 filters=[]
 for i,r in enumerate(rows):filters.append(f'[{i}:v]trim=start={r["source_in"]}:end={r["source_out"]},setpts=PTS-STARTPTS,fps=60,tpad=stop_mode=clone:stop_duration=0.05,trim=end_frame={r["frames"]},setsar=1,format=yuv420p[v{i}]')
 filters.append(''.join(f'[v{i}]' for i in range(len(rows)))+'concat=n=6:v=1:a=0[v]')
 cmd+=['-filter_complex',';'.join(filters),'-map','[v]','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-r','60','-movflags','+faststart',str(R/'output/talking-source-v1.mp4')]
 run(cmd,'source-render')
else:
 # Fixed 60fps cuts: graph A [162,3000), graph B [3540,5340).
 graph='[0:v]split=3[r0][r1][r2];[r0]trim=end_frame=162,setpts=PTS-STARTPTS[a];[r1]trim=start_frame=3000:end_frame=3540,setpts=PTS-STARTPTS[c];[r2]trim=start_frame=5340:end_frame=5654,setpts=PTS-STARTPTS[e];[1:v]setpts=PTS-STARTPTS[b];[2:v]setpts=PTS-STARTPTS[d];[a][b][c][d][e]concat=n=5:v=1:a=0[joined];[joined]ass=captions-v1.ass:fontsdir=fonts[v]'
 cmd=[FF,'-n','-hide_banner','-i','output/talking-source-v1.mp4','-i','output/graphic-a.mp4','-i','output/graphic-b.mp4','-i','audio/voice-original-speed.wav','-filter_complex',graph,'-map','[v]','-map','3:a','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-r','60','-c:a','aac','-b:a','192k','-ar','48000','-ac','1','-movflags','+faststart','output/deepinfer-full-v1.mp4']
 import os
 os.chdir(R);run(cmd,'final-render')
print('complete')
