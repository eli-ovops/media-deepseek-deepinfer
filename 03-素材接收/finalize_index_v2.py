import pathlib,json,hashlib,datetime
ROOT=pathlib.Path(__file__).resolve().parent
baseline=json.loads((ROOT/'临时文件索引.json').read_text())
old_paths={x['path'] for x in baseline['local']}|{str(ROOT/'临时文件索引.json')}
target=ROOT/'临时文件索引-v2.json'
local=[x for x in ROOT.rglob('*') if x.is_file() and str(x) not in old_paths and x!=target]
external=[]
for x in json.loads((ROOT/'transcription-index-v2-new.json').read_text()):
    external.extend(y for y in pathlib.Path(x['receipt']['output_directory']).iterdir() if y.is_file())
frozen={'剪辑EDL-v1.json':'86737bf8ee8c908fc55b1b5c6272e5cb4521fb4c769e33f0fc5d8c63945002bb','五段素材清单.json':'ab626b2ef9caed65e28f2fbf4adee734dddc9f42f152b37112186de418714650','字幕重映射依据-v1.json':'db132bf84b94ca1583271f0124447c1dc5210107dcd80c5bad17afec1d49a017'}
assert all(hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h for n,h in frozen.items())
d={'content_id':'deepseek-deepinfer-20261021','version':'v2','created_at':datetime.datetime.now().astimezone().isoformat(),'reused_v1_index':str(ROOT/'临时文件索引.json'),'v1_core_files_unchanged':True,'purpose':'Retain task evidence, local ASR, images, editable handoff. No cleanup performed. PMO task input files are inputs, not disposable outputs.','new_local':[{'path':str(x),'bytes':x.stat().st_size,'sha256':hashlib.sha256(x.read_bytes()).hexdigest(),'purpose':'v2 intake evidence / processing / handoff or PMO task input; retain'} for x in local],'new_whisper_external':[{'path':str(x),'bytes':x.stat().st_size,'purpose':'12 new full local audio-track ASR outputs; retain'} for x in external],'new_local_bytes':sum(x.stat().st_size for x in local),'new_whisper_bytes':sum(x.stat().st_size for x in external),'cleanup':'none'}
target.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'new_local_count':len(local),'new_whisper_files':len(external),'new_generated_and_input_evidence_bytes':d['new_local_bytes']+d['new_whisper_bytes'],'v1_core_files_unchanged':True}))
