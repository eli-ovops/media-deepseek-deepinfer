import json, pathlib, subprocess, datetime

ROOT = pathlib.Path(__file__).resolve().parent
sources = json.loads((ROOT/'source-metadata.json').read_text())
results = []
for source in sources:
    print('TRANSCRIBING '+source['id'], flush=True)
    run = subprocess.run(['/Volumes/EXTERNAL/Tools/Whisper/whisper.command', source['path'], '--language', 'zh'], capture_output=True, text=True)
    (ROOT/(source['id']+'-whisper-command.log')).write_text(run.stdout+'\n'+run.stderr)
    item = {'id': source['id'], 'source_path': source['path'], 'source_sha256': source['sha256'], 'exit_code': run.returncode, 'receipt': json.loads(run.stdout) if run.returncode==0 else None}
    results.append(item)
    (ROOT/'transcription-index.json').write_text(json.dumps(results, ensure_ascii=True, indent=2)+'\n')
    print(json.dumps(item, ensure_ascii=True), flush=True)
    if run.returncode:
        raise SystemExit(run.returncode)
print('ALL_FIVE_COMPLETE', flush=True)
