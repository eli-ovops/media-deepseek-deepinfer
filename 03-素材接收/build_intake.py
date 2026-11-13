import json, pathlib, re, hashlib, datetime

ROOT=pathlib.Path(__file__).resolve().parent
cfg=json.loads((ROOT/'review-decisions.json').read_text())
sources=json.loads((ROOT/'source-metadata.json').read_text())
transcripts=json.loads((ROOT/'transcription-index.json').read_text())
by_id={x['id']:x for x in sources}
by_trans={x['id']:x for x in transcripts}
outputs=cfg['outputs']

def write(name,data):
    (ROOT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

inventory=[]
for source in sources:
    video=next(s for s in source['probe']['streams'] if s['codec_type']=='video')
    audio=next(s for s in source['probe']['streams'] if s['codec_type']=='audio')
    t=by_trans[source['id']]
    inventory.append({
        'id':source['id'],'source_path':source['path'],'source_sha256':source['sha256'],'source_bytes':source['bytes'],
        'duration_seconds':float(source['probe']['format']['duration']),
        'video':{k:video.get(k) for k in ['codec_name','width','height','r_frame_rate','avg_frame_rate','time_base','start_time','nb_frames']},
        'audio':{k:audio.get(k) for k in ['codec_name','channels','sample_rate','start_time','duration']},
        'full_audio_transcription':t['receipt'],'source_modified':False,
        'decoded_wav_minus_container_duration_seconds':round(t['receipt']['duration_seconds']-float(source['probe']['format']['duration']),6),
        'clock_note':'All EDL times are original media seconds, not edited-timeline or speed-adjusted time. Whisper WAV end padding may extend duration; no sample-accurate speech claim.',
        **cfg['contents'][source['id']]
    })
write(outputs['inventory'],{'content_id':cfg['content_id'],'sources':inventory,'suggested_content_order':['S3','S5','S2','S1'],'unused_source':'S4'})

clock=0.0
keeps=[]
for raw in cfg['keep_ranges']:
    item=dict(raw)
    source=by_id[item['source_id']]
    item.update({'source_path':source['path'],'source_sha256':source['sha256'],'timeline_in':round(clock,6),'duration':round(item['source_out']-item['source_in'],6),'speed':1,'gain_db':0,'denoise':False,'enabled_in_proposal':True})
    clock+=item['duration']; item['timeline_out']=round(clock,6)
    assert 0<=item['source_in']<item['source_out']<=float(source['probe']['format']['duration'])
    keeps.append(item)

discards=[]
for source in sources:
    duration=float(source['probe']['format']['duration'])
    matching=[x for x in keeps if x['source_id']==source['id']]
    if not matching:
        discards.append({'source_id':source['id'],'source_path':source['path'],'range':[0,duration],'reason':'Duplicate incomplete alternate take; S2 has the longer version. Proposed exclusion only; original file retained.'})
    else:
        if matching[0]['source_in']>0:
            discards.append({'source_id':source['id'],'source_path':source['path'],'range':[0,matching[0]['source_in']],'reason':'Short pre-roll inside low-energy region, not bulk silence cleanup.'})
        if matching[-1]['source_out']<duration:
            reason={'S3':'Incomplete code sentence replaced by full S5 take','S2':'Failed/repeated closing sentence replaced by complete S1 take','S1':'Post-speech tail only','S5':'Post-speech tail only'}[source['id']]
            discards.append({'source_id':source['id'],'source_path':source['path'],'range':[matching[-1]['source_out'],duration],'reason':reason})

boundaries=[]
for left,right in zip(keeps,keeps[1:]):
    boundaries.append({'timeline_seconds':left['timeline_out'],'left':{'source_id':left['source_id'],'source_seconds':left['source_out']},'right':{'source_id':right['source_id'],'source_seconds':right['source_in']},'audio_naturalness':'NOT_LISTENED','picture_transition':'sampled only; visible pose/framing change possible','requires':'04 inspect word endings/onsets and local continuity before claiming natural cut'})

edl={'content_id':cfg['content_id'],'version':'v1','status':'PROPOSED_FOR_PMO_REVIEW_NOT_RENDER_RELEASE','clock':'original media seconds; ranges half-open [in,out)','original_speed':True,'original_timbre':True,'keep_ranges':keeps,'proposed_exclusions':discards,'disabled_short_word_cuts':cfg['disabled_cuts'],'boundaries':boundaries,'estimated_duration_seconds':round(clock,6),'original_total_seconds':round(sum(x['duration_seconds'] for x in inventory),6),'missing_script_blocks':cfg['missing_script_blocks'],'source_selection_confidence':'ASR semantic redundancy plus visual samples; no direct audio review','precision':'Nominal seconds/frame-grid proposal, not verified per-word or exact source PTS. End cuts fall within measured low-energy gaps; this is not listening evidence.','rendered':False}
write(outputs['edl'],edl)

mapped=[]
for keep in keeps:
    folder=pathlib.Path(by_trans[keep['source_id']]['receipt']['output_directory'])
    raw=json.loads((folder/'transcript.json').read_text())
    for index,cue in enumerate(raw['transcription'],1):
        a=cue['offsets']['from']/1000; b=cue['offsets']['to']/1000
        lo=max(a,keep['source_in']); hi=min(b,keep['source_out'])
        if hi<=lo: continue
        mapped.append({'source_id':keep['source_id'],'keep_id':keep['id'],'source_asr_json':str(folder/'transcript.json'),'source_cue_index':index,'original_asr_range':[a,b],'original_asr_text':cue['text'],'intersection_with_kept_source':[lo,hi],'timeline_range':[round(keep['timeline_in']+lo-keep['source_in'],6),round(keep['timeline_in']+hi-keep['source_in'],6)],'cue_clipped':a<lo or b>hi,'display_text_status':'UNVERIFIED_ASR_NOT_FINAL_SUBTITLE','note':'If cue is clipped, do not display the whole original text over the shortened cue; manually resegment retained speech. ASR timestamps are segment-level, not words.'})
write(outputs['subtitles'],{'content_id':cfg['content_id'],'edl_version':'v1','formula':'timeline_time = keep.timeline_in + source_time - keep.source_in; speed=1','entries':mapped,'term_candidates':{'DeepSeek':['Depthic'],'DeepInfer':['Depthin for'],'GitHub':['给他们'],'梁文锋':['梁文芬'],'护城河':['护城盒'],'服':['佛'],'算力':['算例'],'精力':['经历'],'一支团队':['一直团队'],'工程积累':['工程累计']},'uncertain_short_words':cfg['disabled_cuts'],'final_subtitles_ready':False,'limits':'Proper-name candidates are grounded in frozen script. They do not prove exact spoken pronunciation; unresolved variants retained for review.'})

lines=['# Full-track ASR evidence','', 'Local Whisper base transcription only; not direct listening. Original SRT/JSON/WAV/logs remain in the tool transcripts directory.','']
for source in sources:
    receipt=by_trans[source['id']]['receipt']; folder=pathlib.Path(receipt['output_directory'])
    lines.extend(['## '+source['id'],source['path'],'SHA256 '+source['sha256'],'Original evidence: '+str(folder),'','```srt',(folder/'transcript.srt').read_text().strip(),'```',''])
(ROOT/outputs['transcripts']).write_text('\n'.join(lines),encoding='utf-8')

report={'content_id':cfg['content_id'],'stage':'03','owner':cfg['owner'],'status':'PENDING_PMO_EDL_REVIEW','completed':{'five_sources_metadata_and_sha':True,'five_full_audio_tracks_transcribed':True,'read_all_original_asr_cues':True,'visual_samples_actually_viewed':32,'contact_sheets':cfg['visual_review']['viewed_contact_sheets'],'all_five_files_examined':True,'edl_and_subtitle_remapping_basis':True},'order':['S3','S5','S2','S1'],'alternate_not_selected':'S4','estimated_edited_seconds':round(clock,6),'visual_review':cfg['visual_review'],'not_verified':['Direct audio listening/prosody/exact pronunciation','Short-word stutter and exact phoneme boundaries','Continuous video and natural joins','Full v3.2 script coverage; recording cards not in local evidence','Any rendered rough cut or final subtitles'],'can_continue':'PMO can review this proposed EDL and resolve recording-card coverage. 04 can execute only after PMO release; short-word cuts remain disabled.','missing_script_blocks':cfg['missing_script_blocks'],'parameters':{'speed':1,'gain_db':0,'denoise':False,'bgm':False,'source_overwritten':False,'private_upload':False,'new_model_or_dependencies':False,'rendered_mp4':False},'read_rule_versions':['PERMISSIONS-2026-10-14-v1','ROUTING-2026-10-13-v4','HANDOFF-2026-10-10-v2','ELI-REWORK-20261019-v1'],'routing':{'target_model':'gpt-6.1-sol','target_effort':'medium','actual_model':'UNKNOWN','actual_effort':'UNKNOWN','actual_speed':'UNKNOWN','weekly_usage_from_dispatch':'83%','five_hour_usage':'UNKNOWN','subagents':False},'tools':{'whisper':'existing whisper.cpp base, one full run per source','ffmpeg':'/Users/USER/.local/bin/ffmpeg','ffprobe':'existing compositor arm64 with child-only DYLD_LIBRARY_PATH'},'tool_issue':'Initial inspect script had a mistyped Unicode path character; fixed to task-specified exact compositor path after checking LOCAL_BLOCKERS. No tool installation/config change.','audio_review_owner':'PMO must allocate direct listening before final sound acceptance; 02 has no direct audio input. Existing known omitted-audio/calibration failure not retried.','cleanup':'No deletion; source assets and all task evidence retained.','report_receipt':'PMO回报回执.json'}
write(outputs['report'],report)

local_files=[x for x in ROOT.rglob('*') if x.is_file() and x.name!=outputs['temporary']]
external_files=[]
for row in transcripts:
    folder=pathlib.Path(row['receipt']['output_directory'])
    external_files.extend(x for x in folder.iterdir() if x.is_file())
index={'created_at':datetime.datetime.now().astimezone().isoformat(),'purpose':'Task-local evidence, recovery and handoff; all retained. No cleanup authorized or performed.','local':[{'path':str(x),'bytes':x.stat().st_size,'sha256':hashlib.sha256(x.read_bytes()).hexdigest(),'purpose':'source inspection / ASR references / visual samples / proposed EDL handoff'} for x in local_files],'whisper_external':[{'path':str(x),'bytes':x.stat().st_size,'purpose':'tool-owned WAV/ASR/log/receipt from five full local audio tracks'} for x in external_files],'local_bytes':sum(x.stat().st_size for x in local_files),'external_generated_bytes':sum(x.stat().st_size for x in external_files)}
write(outputs['temporary'],index)
print(json.dumps({'source_count':len(sources),'full_transcriptions':len(transcripts),'keep_order':[x['source_id'] for x in keeps],'duration':clock,'boundaries':boundaries,'generated_bytes':index['local_bytes']+index['external_generated_bytes']},ensure_ascii=True,indent=2))
