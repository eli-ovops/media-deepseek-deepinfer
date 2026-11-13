from pathlib import Path
import subprocess,json,os,hashlib,io,struct,wave
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;Q=R/'qc';F=R/'output/deepinfer-full-v1.mp4';FF='/Users/USER/.local/bin/ffmpeg'
P=Path('/Volumes/EXTERNAL/自媒体/Fred复刻测试-20261016/7694088597179239690/source-snapshot/FredTalk-1.5-3D/camera/node_modules/@remotion/compositor-darwin-arm64');env=dict(os.environ,DYLD_LIBRARY_PATH=str(P))
meta=json.loads(subprocess.check_output([str(P/'ffprobe'),'-v','error','-show_streams','-show_format','-count_frames','-of','json',str(F)],env=env));(Q/'final-probe.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
check=subprocess.run([FF,'-v','error','-i',str(F),'-f','null','-'],capture_output=True,text=True);(Q/'full-decode.log').write_text(check.stderr);assert check.returncode==0
v=next(s for s in meta['streams'] if s['codec_type']=='video');a=next(s for s in meta['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'],v['pix_fmt'],v['r_frame_rate'],int(v['nb_read_frames']))==(1080,1920,'yuv420p','60/1',5654)
assert a['sample_rate']=='48000'
boxes=[]
with F.open('rb') as fp:
 while True:
  b=fp.read(8)
  if len(b)<8:break
  n,kind=struct.unpack('>I4s',b);start=fp.tell()-8
  if n==1:n=struct.unpack('>Q',fp.read(8))[0]
  if not n:break
  boxes.append([kind.decode(),start,n]);fp.seek(start+n)
assert next(x[1] for x in boxes if x[0]=='moov')<next(x[1] for x in boxes if x[0]=='mdat')
pcm=np.frombuffer(subprocess.check_output([FF,'-v','error','-i',str(F),'-vn','-ar','48000','-ac','1','-f','f32le','-']),dtype='<f4')
with wave.open(str(R/'audio/voice-original-speed.wav'),'rb') as w:original=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768
n=min(len(pcm),len(original));corr=float(np.corrcoef(pcm[:n],original[:n])[0,1]);assert corr>.995
edl=json.loads((R/'edl-v1.json').read_text());assert abs(sum(x['duration'] for x in edl['keep_ranges'])-5654/60)<1e-6
for i,k in enumerate(edl['keep_ranges']):assert k['timeline_out']-k['timeline_in']==k['duration'] or abs(k['timeline_out']-k['timeline_in']-k['duration'])<1e-6
for b,k in zip(edl['boundaries'],edl['keep_ranges'][1:]):assert b['timeline_seconds']==k['timeline_in']
cues=json.loads((R/'captions-v1.json').read_text())['cues'];last=0
for c in cues:assert last<=c['start']<c['end']<=5654/60;last=c['end']
def frame(t,name):
 b=subprocess.check_output([FF,'-v','error','-ss',f'{t:.8f}','-i',str(F),'-frames:v','1','-f','image2pipe','-vcodec','png','-']);im=Image.open(io.BytesIO(b)).convert('RGB');im.save(Q/name);return im
times=[0,2.683333,2.7,7,9.333333,13.7,15.75,15.766667,18.8,23.683333,23.7,28,35,41.7,44,49.983333,50,55,58.983333,59,70,83.583333,88.983333,89,89.25,93.9]
sheet=Image.new('RGB',(1440,4*450),'#222');samples=[]
for i,t in enumerate(times):
 im=frame(t,f'final-{i:02}.png');samples.append({'time':t,'path':str((Q/f'final-{i:02}.png').resolve())});thumb=im.copy();thumb.thumbnail((205,365));x=i%7*205;y=i//7*450;sheet.paste(thumb,(x,y));ImageDraw.Draw(sheet).text((x+5,y+370),f'{t:.6f}s',fill='white')
sheet.save(Q/'final-overview.jpg',quality=95)
# All 49 burned cue midpoints are sampled; these are caption crops, not continuous video review.
cs=Image.new('RGB',(1080,((len(cues)+1)//2)*115),'#222')
for i,c in enumerate(cues):
 im=frame((c['start']+c['end'])/2,f'caption-{i+1:02}.png');strip=im.crop((0,1530,1080,1740));strip.thumbnail((540,105));x=i%2*540;y=i//2*115;cs.paste(strip,(x,y));ImageDraw.Draw(cs).text((x+6,y+101),f'{i+1:02} {c["start"]:.2f}-{c["end"]:.2f}',fill='white')
cs.save(Q/'all-caption-crops.jpg',quality=95)
measure={'file':str(F),'sha256':hashlib.sha256(F.read_bytes()).hexdigest(),'bytes':F.stat().st_size,'duration':float(meta['format']['duration']),'video_frames':int(v['nb_read_frames']),'video_codec':v['codec_name'],'dimensions':[v['width'],v['height']],'fps':v['r_frame_rate'],'pixel_format':v['pix_fmt'],'audio_codec':a['codec_name'],'audio_rate':a['sample_rate'],'full_decode_exit':check.returncode,'faststart':True,'mp4_boxes':boxes,'audio_source_output_zero_lag_correlation':corr,'decoded_audio_samples':len(pcm),'voice_wav_samples':len(original),'decoded_sample_peak':float(np.max(abs(pcm))),'edl_internal_consistent':True,'caption_cues':len(cues),'caption_timeline_monotonic':True,'direct_listening':False,'continuous_visual_review':False,'actual_samples':samples}
(Q/'technical-checks.json').write_text(json.dumps(measure,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in measure.items() if k not in ['actual_samples','mp4_boxes']},ensure_ascii=False,indent=2))
