from pathlib import Path
import json,subprocess,os,hashlib,math
from PIL import Image,ImageDraw
import numpy as np
R=Path(__file__).resolve().parent;E=R/'evidence/v2';V=R/'output/deepinfer-fred-full-v2.mp4';OLD=R/'output/deepinfer-fred-full-v1.mp4';F='/Users/USER/.local/bin/ffmpeg'
P=Path('/Volumes/EXTERNAL/自媒体/Fred复刻测试-20261016/7694088597179239690/source-snapshot/FredTalk-1.5-3D/camera/node_modules/@remotion/compositor-darwin-arm64/ffprobe');env=dict(os.environ,DYLD_LIBRARY_PATH=str(P.parent))
def rec(p):p=Path(p);return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
def run(args):return subprocess.run(args,check=True,capture_output=True)
# Audio copy rather than new AAC encoding; preserve the reviewed exact packet timeline.
cmd=[F,'-v','error','-i',str(R/'output/deepinfer-fred-picture-v2.mp4'),'-i',str(OLD),'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',str(V)];run(cmd)
(E/'mux-command.json').write_text(json.dumps({'command':cmd,'final':rec(V)},ensure_ascii=False,indent=2));print('MUX',flush=True)
p=json.loads(subprocess.check_output([str(P),'-v','error','-show_streams','-show_format','-of','json',str(V)],env=env));(E/'probe.json').write_text(json.dumps(p,indent=2));v=next(s for s in p['streams'] if s['codec_type']=='video');assert (v['width'],v['height'],v['r_frame_rate'],v['nb_frames'])==(1080,1920,'60/1','5654')
r=run([F,'-v','error','-i',str(V),'-f','null','-']);assert not r.stderr;(E/'decode.json').write_text(json.dumps({'status':'PASS','exitCode':r.returncode,'stderr':r.stderr.decode(),'video':rec(V)},ensure_ascii=False,indent=2));print('DECODE',flush=True)
au=[]
for file in [OLD,V]:
 packets=json.loads(subprocess.check_output([str(P),'-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256','-show_entries','packet=pts,dts,duration,size,data_hash','-of','json',str(file)],env=env))['packets']
 au.append({'video':rec(file),'packetCount':len(packets),'packetPayloadAndTimingSha256':hashlib.sha256(json.dumps(packets,sort_keys=True).encode()).hexdigest()})
assert au[0]['packetPayloadAndTimingSha256']==au[1]['packetPayloadAndTimingSha256'];(E/'audio-packet-identity.json').write_text(json.dumps({'status':'PASS','records':au,'method':'All AAC packet hashes,pts,dts,duration,size equal; previous PCM preservation evidence inherited. No new hearing claim.'},indent=2));print('AUDIO_IDENTITY',flush=True)
# Dense 0.1s samples at all revised camera paths; every frame at the short same-image seam.
frames=sorted(set(list(range(408,560,6))+list(range(780,942,6))+list(range(942,985))+[432,540,810,930,945,946,947,966,984]))
N=E/'actual-frames';N.mkdir(exist_ok=True);expr='+'.join(f'eq(n\\,{f})' for f in frames)
run([F,'-v','error','-i',str(V),'-vf',f'select={expr}','-fps_mode','vfr',str(N/'raw-%03d.png')]);records=[]
for i,f in enumerate(frames):
 src=N/f'raw-{i+1:03}.png';dst=N/f'f{f:04}.png';src.rename(dst);records.append({'frame':f,'seconds':f/60,**rec(dst)})
for start in range(0,len(records),16):
 sheet=Image.new('RGB',(4*270,4*506),'#202025');d=ImageDraw.Draw(sheet)
 for j,row in enumerate(records[start:start+16]):
  x=j%4*270;y=j//4*506;im=Image.open(row['path']).resize((270,480));sheet.paste(im,(x,y));d.text((x+5,y+483),f"F{row['frame']} / {row['seconds']:.4f}s",fill='white')
 sheet.save(E/f'sheet-{start//16+1:02}.jpg',quality=94)
(E/'sample-index.json').write_text(json.dumps({'video':rec(V),'method':'Exact frame-number sequential decode; camera paths step6 frames=10fps; seam F942..984 every frame=60fps','frames':records,'normalSpeedViewing':'UNKNOWN','directHearing':'UNKNOWN'},ensure_ascii=False,indent=2));print('FRAMES',len(records),flush=True)
# Unaffected scene samples, one per retained scene plus code stable endpoint. No full re-review.
keep=[0,120,1320,1550,2250,2400,2800,3100,3700,4210,4650,4900,5210,5500,5653];expr='+'.join(f'eq(n\\,{f})' for f in keep);samples=[]
for file in [OLD,V]:
 raw=run([F,'-v','error','-i',str(file),'-vf',f'select={expr}','-fps_mode','vfr','-f','rawvideo','-pix_fmt','rgb24','-']).stdout
 a=np.frombuffer(raw,dtype=np.uint8).reshape((len(keep),1920,1080,3));samples.append(a)
rows=[]
for i,f in enumerate(keep):
 d=np.abs(samples[0][i].astype('int16')-samples[1][i].astype('int16'));mse=float(np.mean(d.astype(float)**2));rows.append({'frame':f,'exactPixels':bool(not np.any(d)),'meanChannelError':float(np.mean(d)),'psnrDb':None if mse==0 else 10*math.log10(255**2/mse)})
(E/'unchanged-sample-comparison.json').write_text(json.dumps({'method':'V1/V2 exact same decoded frame indexes; same source; changed encoder history may cause compression differences','frames':rows},indent=2));print('PRESERVED_SAMPLES',flush=True)
