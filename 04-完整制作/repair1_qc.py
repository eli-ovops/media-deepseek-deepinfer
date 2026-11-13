from pathlib import Path
import subprocess,json,hashlib,os,io
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;D=R/'repair1';FF='/Users/USER/.local/bin/ffmpeg'
P=Path('/Volumes/EXTERNAL/自媒体/Fred复刻测试-20261016/7694088597179239690/source-snapshot/FredTalk-1.5-3D/camera/node_modules/@remotion/compositor-darwin-arm64');ENV=dict(os.environ,DYLD_LIBRARY_PATH=str(P))
old=R/'output/deepinfer-full-v1.mp4';new=R/'output/deepinfer-full-v1-repair1.mp4'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def packets(f,select):
 return json.loads(subprocess.check_output([str(P/'ffprobe'),'-v','error','-select_streams',select,'-show_packets','-show_entries','packet=pts,dts,pts_time,dts_time,duration,data_hash','-show_data_hash','sha256','-of','json',str(f)],env=ENV))['packets']
v0=packets(old,'v:0');v1=packets(new,'v:0');a0=packets(old,'a:0');a1=packets(new,'a:0')
assert len(v0)==len(v1)==5654
prefix=[p['data_hash'] for p in v0[:1672]]==[p['data_hash'] for p in v1[:1672]]
suffix=[p['data_hash'] for p in v0[2422:]]==[p['data_hash'] for p in v1[2422:]]
audio=a0==a1
assert prefix and suffix and audio,(prefix,suffix,audio)
pts=sorted(int(p['pts']) for p in v1);assert pts==[i*256 for i in range(5654)],(pts[:3],pts[-3:])
baseline=json.loads((D/'baseline-sha.json').read_text());protected={p:sha(R/p)==h for p,h in baseline.items()};assert all(protected.values())
covers=json.loads((R/'covers/manifest.json').read_text());assert all(sha(Path(c['path']))==c['sha256'] for c in covers)
cmd=[FF,'-v','error','-ss','27.7','-i',str(new),'-t','12.8','-f','null','-'];decode=subprocess.run(cmd,capture_output=True,text=True);(D/'local-decode.log').write_text(decode.stderr);assert decode.returncode==0
times=[27.85,27.866667,29.683333,29.7,30,30.5,31.3,32,34,37.4,38.3,38.883333,38.9,39,40.35,40.366667,40.383333,41.7]
sheet=Image.new('RGB',(1440,5*655),'#222');samples=[]
for i,t in enumerate(times):
 data=subprocess.check_output([FF,'-v','error','-ss',str(t),'-i',str(new),'-frames:v','1','-f','image2pipe','-vcodec','png','-']);im=Image.open(io.BytesIO(data)).convert('RGB');name=f'final-{t:.6f}.png';im.save(D/name);samples.append(dict(time=t,path=str(D/name),sha256=sha(D/name)));im.thumbnail((360,640));x=i%4*360;y=i//4*655;sheet.paste(im,(x,y));ImageDraw.Draw(sheet).text((x+5,y+640),f'{t:.6f}',fill='white')
sheet.save(D/'local-contact.jpg',quality=95)
report=dict(status='OWNER_LOCAL_CHECK_COMPLETE_PENDING_PMO_05',old_sha256=sha(old),new_sha256=sha(new),new_path=str(new),new_bytes=new.stat().st_size,duration=94.233333,total_frames=5654,dimensions=[1080,1920],fps=60,patch_graphics_frames=[1782,2334],patch_graphics_seconds=[29.7,38.9],gop_wrapper_frames=[1672,2422],gop_wrapper_seconds=[1672/60,2422/60],new_graphic_frames=552,unmodified_guard_frames_reused_from_old=198,prefix_packets_exact_match=prefix,prefix_frame_count=1672,suffix_packets_exact_match=suffix,suffix_frame_count=3232,audio_packets_and_timestamps_exact_match=audio,video_pts_exact_60fps=True,protected_baseline_files=protected,covers_sha_unchanged=True,local_decode_command=cmd,local_decode_exit=decode.returncode,samples=samples,direct_listening=False,continuous_visual_review=False)
(D/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['samples','protected_baseline_files','local_decode_command']},ensure_ascii=False,indent=2))
