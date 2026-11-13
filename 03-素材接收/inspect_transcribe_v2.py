import pathlib,json,subprocess,hashlib,os

ROOT=pathlib.Path(__file__).resolve().parent
request=json.loads((ROOT/'补交17段精确清单.json').read_text())
compositor=pathlib.Path('/Volumes/EXTERNAL/自媒体/Fred复刻测试-20261016/7694088597179239690/source-snapshot/FredTalk-1.5-3D/camera/node_modules/@remotion/compositor-darwin-arm64')
env=dict(os.environ,DYLD_LIBRARY_PATH=str(compositor))
metadata=[]; transcriptions=[]; paths=[]
for item in request['new_paths']:
    path=pathlib.Path(item['path'])
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest==item['sha256'],str(path)
    paths.append(dict(item,sha_verified=True))
    if item['same_as_previous_source_id']:
        print('REUSED '+item['same_as_previous_source_id'],flush=True)
        continue
    sid='N'+str(len(metadata)+1).zfill(2)
    probe=subprocess.run([str(compositor/'ffprobe'),'-v','error','-show_streams','-show_format','-of','json',str(path)],env=env,capture_output=True,text=True,check=True)
    record={'id':sid,'path':str(path),'bytes':path.stat().st_size,'sha256':digest,'probe':json.loads(probe.stdout)}
    metadata.append(record)
    (ROOT/'source-metadata-v2-new.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
    print('TRANSCRIBING '+sid+' '+record['probe']['format']['duration']+' seconds',flush=True)
    run=subprocess.run(['/Volumes/EXTERNAL/Tools/Whisper/whisper.command',str(path),'--language','zh'],capture_output=True,text=True)
    (ROOT/(sid+'-whisper-command.log')).write_text(run.stdout+'\n'+run.stderr)
    result={'id':sid,'source_path':str(path),'source_sha256':digest,'exit_code':run.returncode,'receipt':json.loads(run.stdout) if run.returncode==0 else None}
    transcriptions.append(result)
    (ROOT/'transcription-index-v2-new.json').write_text(json.dumps(transcriptions,ensure_ascii=False,indent=2)+'\n')
    if run.returncode: raise SystemExit(run.returncode)
    print('DONE '+sid,flush=True)
(ROOT/'supplement-paths-verified-v2.json').write_text(json.dumps(paths,ensure_ascii=False,indent=2)+'\n')
assert len(metadata)==12 and len(paths)==17
print('ALL_TWELVE_COMPLETE; 17 supplied path SHAs verified; old five ASR reused',flush=True)
