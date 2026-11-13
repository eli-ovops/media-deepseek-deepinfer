from pathlib import Path
import subprocess,json,os,hashlib,math,sys
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;V=R/'output/deepinfer-fred-full-v1.mp4';E=R/'evidence';F='/Users/USER/.local/bin/ffmpeg'
probe=Path('/Volumes/EXTERNAL/自媒体/Fred复刻测试-20261016/7694088597179239690/source-snapshot/FredTalk-1.5-3D/camera/node_modules/@remotion/compositor-darwin-arm64/ffprobe')
env=dict(os.environ,DYLD_LIBRARY_PATH=str(probe.parent))
def rec(p):return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
def run(cmd):return subprocess.run(cmd,check=True,capture_output=True)
p=json.loads(subprocess.check_output([str(probe),'-v','error','-show_streams','-show_format','-of','json',str(V)],env=env));(E/'probe-final.json').write_text(json.dumps(p,indent=2));print('PROBE',flush=True)
r=subprocess.run([F,'-v','error','-i',str(V),'-f','null','-'],capture_output=True,text=True);(E/'decode-final.log').write_text(r.stderr);assert r.returncode==0 and not r.stderr
(E/'decode-final.json').write_text(json.dumps({'status':'PASS','exitCode':r.returncode,'stderr':r.stderr,'file':rec(V)},indent=2));print('DECODE',flush=True)
# Audio evidence is numerical preservation only, never direct hearing.
audio=[]
for name,file in [('original',R/'public/voice-original-speed.wav'),('export',V)]:
 data=run([F,'-v','error','-i',str(file),'-map','0:a:0','-ac','1','-ar','48000','-f','f32le','-']).stdout;audio.append(np.frombuffer(data,dtype='<f4').astype('float64'))
a,b=audio;n=min(len(a),len(b));a=a[:n];b=b[:n];err=b-a
shifts=range(-24,25);cor=[]
for k in shifts:
 aa=a[max(0,k):n+min(0,k)];bb=b[max(0,-k):n-min(max(0,k),n)];cor.append(float(np.dot(aa,bb)/np.sqrt(np.dot(aa,aa)*np.dot(bb,bb))))
(E/'audio-preservation.json').write_text(json.dumps({'source':rec(R/'public/voice-original-speed.wav'),'video':rec(V),'sampleRate':48000,'comparedSamples':n,'bestLagSamplesWithinPlusMinus24':list(shifts)[int(np.argmax(cor))],'zeroLagCorrelation':float(np.corrcoef(a,b)[0,1]),'snrDb':float(10*np.log10(np.mean(a*a)/np.mean(err*err))),'rmsError':float(np.sqrt(np.mean(err*err))),'peakExport':float(np.max(np.abs(b))),'policy':'exact input PCM, unchanged clock; AAC encoding differences expected; no BGM/SFX. Numerical test does not prove direct hearing or audiovisual sync.','directHearing':'UNKNOWN'},indent=2));print('AUDIO',flush=True)
if '--technical-only' in sys.argv:sys.exit(0)
D=E/'final-samples';D.mkdir(exist_ok=True)
run([F,'-v','error','-i',str(V),'-vf','select=not(mod(n\\,30)),setpts=N/(2*TB),scale=270:480','-fps_mode','vfr','-q:v','2',str(D/'sample-%03d.jpg')]);files=sorted(D.glob('sample-*.jpg'))
for base in range(0,len(files),24):
 sheet=Image.new('RGB',(6*270,4*506),'#202025');d=ImageDraw.Draw(sheet)
 for j,file in enumerate(files[base:base+24]):
  x=j%6*270;y=j//6*506;sheet.paste(Image.open(file),(x,y));d.text((x+8,y+483),f'{(base+j)/2:.1f}s',fill='white')
 sheet.save(E/f'full-sheet-{base//24+1:02}.jpg',quality=92)
print('SHEETS',len(files),flush=True)
# Native output frames; exact index extraction in one full sequential decode.
frames=[0,161,162,480,559,560,840,945,946,1090,1320,1421,1422,2258,2264,2265,2300,2400,2600,2601,2700,2822,2830,2840,2940,2999,3000,3437,3438,3550,3700,3870,3989,3990,4210,4361,4362,4650,4734,4735,4900,4970,5014,5015,5210,5339,5340,5653]
N=E/'final-native';N.mkdir(exist_ok=True)
expr='+'.join(f'eq(n\\,{f})' for f in frames)
run([F,'-v','error','-i',str(V),'-vf',f'select={expr}','-fps_mode','vfr',str(N/'extract-%03d.png')])
records=[]
for i,f in enumerate(frames):
 file=N/f'extract-{i+1:03d}.png';dest=N/f'f{f:04}.png';file.rename(dest);records.append({'frame':f,'seconds':f/60,**rec(dest)})
(E/'final-frame-index.json').write_text(json.dumps({'video':rec(V),'method':'actual MP4 sequential decode, exact frame indexes','frames':records,'overviewCount':len(files),'overviewFps':2,'continuousViewing':'NOT_PERFORMED'},indent=2));print('NATIVE',len(records),flush=True)
