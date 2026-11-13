import json, pathlib, subprocess, re, wave, math, array

ROOT=pathlib.Path(__file__).resolve().parent
records=json.loads((ROOT/'transcription-index.json').read_text())
output=[]
for record in records:
    folder=pathlib.Path(record['receipt']['output_directory'])
    wav=folder/'audio.wav'
    run=subprocess.run(['/Users/USER/.local/bin/ffmpeg','-nostdin','-hide_banner','-i',str(wav),'-af','silencedetect=noise=-35dB:d=0.12','-f','null','-'],capture_output=True,text=True,check=True)
    (ROOT/(record['id']+'-silence.log')).write_text(run.stderr)
    silence=[]
    pending=None
    for line in run.stderr.splitlines():
        match=re.search(r'silence_start: ([0-9.]+)',line)
        if match: pending=float(match[1])
        match=re.search(r'silence_end: ([0-9.]+)',line)
        if match and pending is not None:
            silence.append([pending,float(match[1])]); pending=None
    with wave.open(str(wav)) as w:
        rate=w.getframerate(); pcm=array.array('h',w.readframes(w.getnframes()))
    rms=[]
    block=int(rate*.01)
    for i in range(0,len(pcm),block):
        chunk=pcm[i:i+block]
        value=math.sqrt(sum(x*x for x in chunk)/len(chunk))/32768
        rms.append(round(20*math.log10(max(value,1e-8)),2))
    item={'source_id':record['id'],'wav':str(wav),'rms_step_seconds':.01,'rms_dbfs':rms,'silences_minus35db_120ms':silence,'limits':'Low energy is not proof of no speech or natural sounding cut.'}
    output.append(item)
    print(record['id'],json.dumps(silence))
(ROOT/'audio-energy-analysis.json').write_text(json.dumps(output,ensure_ascii=True,indent=2)+'\n')
