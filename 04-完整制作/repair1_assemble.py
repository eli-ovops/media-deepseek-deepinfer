from pathlib import Path
import subprocess,json,os
R=Path(__file__).resolve().parent;os.chdir(R);D=R/'repair1';FF='/Users/USER/.local/bin/ffmpeg'
P=Path('/Volumes/EXTERNAL/自媒体/Fred复刻测试-20261016/7694088597179239690/source-snapshot/FredTalk-1.5-3D/camera/node_modules/@remotion/compositor-darwin-arm64');ENV=dict(os.environ,DYLD_LIBRARY_PATH=str(P))
def run(cmd,name):
 (D/f'{name}-command.json').write_text(json.dumps(cmd,ensure_ascii=False,indent=2))
 with (D/f'{name}.log').open('w') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True)
def probe(path):return json.loads(subprocess.check_output([str(P/'ffprobe'),'-v','error','-count_packets','-show_streams','-show_format','-show_data_hash','sha256','-of','json',str(path)],env=ENV))
# Exact existing IDR boundaries F1672/F2422 surround changed F1782..2333.
run([FF,'-n','-hide_banner','-i','output/deepinfer-full-v1.mp4','-map','0:v:0','-an','-c:v','copy','-f','segment','-segment_times','27.866666666667,40.366666666667','-segment_time_delta','0.008333333','-reset_timestamps','1','repair1/reuse-%03d.mp4'],'split-existing-video')
counts=[int(probe(D/f'reuse-{i:03}.mp4')['streams'][0]['nb_read_packets']) for i in range(3)]
assert counts==[1672,750,3232],counts
graph='[0:v]split=2[x][y];[x]trim=start_frame=1672:end_frame=1782,setpts=PTS-STARTPTS[a];[1:v]setpts=PTS+29.7/TB,ass=captions-v1.ass:fontsdir=fonts,setpts=PTS-STARTPTS[b];[y]trim=start_frame=2334:end_frame=2422,setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1:a=0[v]'
run([FF,'-n','-hide_banner','-i','output/deepinfer-full-v1.mp4','-i','output/repair1-queue-silent.mp4','-filter_complex',graph,'-map','[v]','-an','-frames:v','750','-r','60','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart','repair1/repaired-gop-wrapper.mp4'],'local-wrapper')
old=probe(R/'output/deepinfer-full-v1.mp4');new=probe(D/'repaired-gop-wrapper.mp4')
assert int(new['streams'][0]['nb_read_packets'])==750
# Equal SPS/PPS permits byte-preserving packet concat without automatic AnnexB conversion.
assert old['streams'][0]['extradata_hash']==new['streams'][0]['extradata_hash'],(old['streams'][0].get('extradata_hash'),new['streams'][0].get('extradata_hash'))
(D/'concat.ffconcat').write_text("ffconcat version 1.0\nfile 'reuse-000.mp4'\nduration 27.866666666667\nfile 'repaired-gop-wrapper.mp4'\nduration 12.5\nfile 'reuse-002.mp4'\nduration 53.866666666667\n")
run([FF,'-n','-hide_banner','-f','concat','-safe','0','-auto_convert','0','-i','repair1/concat.ffconcat','-i','output/deepinfer-full-v1.mp4','-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart','output/deepinfer-full-v1-repair1.mp4'],'complete-stream-copy')
result=probe(R/'output/deepinfer-full-v1-repair1.mp4');(D/'final-probe.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
assert int(result['streams'][0]['nb_read_packets'])==5654
print('Complete repair1:',result['format']['duration'],'seconds;',counts,'reused/replaced segments')
