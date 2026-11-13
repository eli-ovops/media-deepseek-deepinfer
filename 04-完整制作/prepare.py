from pathlib import Path
import json,hashlib,subprocess,os,math,datetime,wave
import numpy as np
R=Path(__file__).resolve().parent
FF='/Users/USER/.local/bin/ffmpeg'
P=Path('/Volumes/EXTERNAL/自媒体/Fred复刻测试-20261016/7694088597179239690/source-snapshot/FredTalk-1.5-3D/camera/node_modules/@remotion/compositor-darwin-arm64')
ENV=dict(os.environ,DYLD_LIBRARY_PATH=str(P))
for d in ['assets','audio','qc','output','source','fonts','covers']: (R/d).mkdir(exist_ok=True)
edl=json.loads((R.parent/'03-素材接收/剪辑EDL-v2.json').read_text())
rows=edl['keep_ranges']; timeline=0; receipts=[]; audio=[]
for row in rows:
    f=Path(row['source_path']); sha=hashlib.sha256(f.read_bytes()).hexdigest()
    assert sha==row['source_sha256'], f
    meta=json.loads(subprocess.check_output([str(P/'ffprobe'),'-v','error','-show_streams','-show_format','-of','json',str(f)],env=ENV))
    pcm=np.frombuffer(subprocess.check_output([FF,'-v','error','-i',str(f),'-vn','-ar','48000','-ac','1','-f','f32le','-']),dtype='<f4')
    if row['source_id']=='S5':
        row['source_out']=float(meta['format']['duration'])
        row['tail_change']='7.95 widened to source end; retain all available decoded tail, pad to 60fps boundary'
    n=math.ceil((row['source_out']-row['source_in'])*60-0.0001)
    s=round(row['source_in']*48000); e=min(len(pcm),round(row['source_out']*48000))
    part=pcm[s:e]; target=n*800
    assert len(part)<=target+2
    part=np.pad(part,(0,max(0,target-len(part))))[:target]; audio.append(part)
    row.update(timeline_in=timeline/60,timeline_out=(timeline+n)/60,frames=n,start_frame=timeline,pad_audio_samples=target-(e-s),speed=1,gain_db=0)
    timeline+=n
    windows=[]
    for t in [row['source_in'],row['source_out']]:
        for delta in [-.2,-.1,0,.1]:
            a=max(0,round((t+delta)*48000)); b=min(len(pcm),a+4800); q=pcm[a:b]
            if len(q): windows.append({'from':a/48000,'to':b/48000,'rms_dbfs':float(20*np.log10(max(1e-9,np.sqrt(np.mean(q*q))))),'peak_dbfs':float(20*np.log10(max(1e-9,np.max(abs(q)))))})
    receipts.append({'source_id':row['source_id'],'sha256':sha,'metadata':meta,'boundary_energy':windows,'direct_listening':False})
merged=np.concatenate(audio)
with wave.open(str(R/'audio/voice-original-speed.wav'),'wb') as w:
    w.setnchannels(1);w.setsampwidth(2);w.setframerate(48000);w.writeframes((np.clip(merged,-1,1)*32767).astype('<i2').tobytes())
edl.update(version='04-v1',keep_ranges=rows,total_frames=timeline,estimated_duration_seconds=timeline/60,source_clock='Original source trims; 60fps frame timeline; S5 tail padded <=1 frame',direct_listening=False)
for row in rows:
    row['duration']=row['frames']/60
    row['content_duration']=row['source_out']-row['source_in']
    if row['source_id']=='S5': row['reason']='完整代码补说保留至原片8.368333；原输入7.95尾刀取消；补15ms对齐60fps'
edl['boundaries']=[dict(timeline_seconds=b['timeline_in'],outgoing_source=a['source_id'],outgoing_seconds=a['source_out'],incoming_source=b['source_id'],incoming_seconds=b['source_in'],heard=False,continuous_visual_review=False) for a,b in zip(rows,rows[1:])]
edl['excluded_ranges_or_takes']=[x for x in edl['excluded_ranges_or_takes'] if not(x['source_id']=='S5' and x.get('source_range',[0])[0]==7.95)]
for c in edl['coverage']:
    if c['id']=='C3':c['source_range']=[.45,rows[2]['source_out']]
edl['v1_reuse']={'historical_input_reference':str(R.parent/'03-素材接收/剪辑EDL-v2.json'),'note':'输入历史原件保留；本EDL中只有当前keep及衔接时钟'}
edl.update(status='CURRENT_04_EXPORT_TIMELINE_PENDING_PMO',not_a_render_release=False,production_authority='04-完整制作/制作任务.md + stage04 RELEASED',edl_consistency_checks={'duration_sum':sum(x['duration'] for x in rows),'last_out':rows[-1]['timeline_out'],'frames':timeline})
(R/'edl-v1.json').write_text(json.dumps(edl,ensure_ascii=False,indent=2))
(R/'qc/input-checks.json').write_text(json.dumps(receipts,ensure_ascii=False,indent=2))
print('timeline',timeline,'frames',timeline/60,'seconds')
print([(r['source_id'],r['timeline_in'],r['timeline_out'],r['source_out']) for r in rows])
print('audio peak',float(np.max(abs(merged))))
