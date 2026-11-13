import pathlib,json,hashlib,datetime

ROOT=pathlib.Path(__file__).resolve().parent
cfg=json.loads((ROOT/'review-decisions-v2.json').read_text())
old=json.loads((ROOT/'source-metadata.json').read_text())
new=json.loads((ROOT/'source-metadata-v2-new.json').read_text())
sources=old+new
by_id={x['id']:x for x in sources}
by_hash={x['sha256']:x['id'] for x in sources}
assert len(sources)==len(by_hash)==17
old_trans=json.loads((ROOT/'transcription-index.json').read_text())
new_trans=json.loads((ROOT/'transcription-index-v2-new.json').read_text())
trans={x['id']:x for x in old_trans+new_trans}
assert len(trans)==17
supplied=json.loads((ROOT/'supplement-paths-verified-v2.json').read_text())

def write(name,data):
    (ROOT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

paths=[{'path':x['path'],'sha256':x['sha256'],'source_id':x['id'],'submitted_batch':'original-five','sha_evidence':'frozen v1 source metadata'} for x in old]
paths += [{'path':x['path'],'sha256':x['sha256'],'source_id':by_hash[x['sha256']],'submitted_batch':'supplement-seventeen','sha_verified_this_run':x['sha_verified']} for x in supplied]
assert len(paths)==22 and len({x['path'] for x in paths})==22
unique=[]
for source in sources:
    video=next(x for x in source['probe']['streams'] if x['codec_type']=='video')
    audio=next(x for x in source['probe']['streams'] if x['codec_type']=='audio')
    aliases=[x['path'] for x in paths if x['source_id']==source['id']]
    unique.append({'source_id':source['id'],'canonical_path':source['path'],'all_supplied_paths':aliases,'sha256':source['sha256'],'bytes':source['bytes'],'duration_seconds':float(source['probe']['format']['duration']),'video':{k:video.get(k) for k in ['codec_name','width','height','r_frame_rate','avg_frame_rate','time_base','start_time','nb_frames']},'audio':{k:audio.get(k) for k in ['codec_name','channels','sample_rate','duration','start_time']},'content':cfg['source_content'][source['id']],'ASR':trans[source['id']]['receipt'],'reused_v1_evidence':source['id'].startswith('S'),'original_modified':False})
write('全量素材清单-v2.json',{'content_id':cfg['content_id'],'version':'v2','submitted_path_count':22,'independent_recording_count':17,'newly_transcribed_recordings':12,'duplicate_paths_reusing_old_sha':5,'paths':paths,'unique_recordings':unique,'all_requested_inputs_accounted_for':True})

keeps=[];clock=0
for raw in cfg['keep_ranges']:
    k=dict(raw);source=by_id[k['source_id']]
    assert 0<=k['source_in']<k['source_out']<=float(source['probe']['format']['duration'])
    k.update(source_path=source['path'],source_sha256=source['sha256'],duration=round(k['source_out']-k['source_in'],6),timeline_in=round(clock,6),speed=1,gain_db=0)
    clock+=k['duration'];k['timeline_out']=round(clock,6)
    k['boundary_status']='Proposed phrase/low-energy gap boundary; no direct audition or exact phoneme/PTS verification'
    keeps.append(k)
excluded=[]
for source in sources:
    duration=float(source['probe']['format']['duration']);matches=[x for x in keeps if x['source_id']==source['id']]
    if not matches:
        excluded.append({'source_id':source['id'],'source_path':source['path'],'source_range':[0,duration],'kind':'alternate_take_not_selected','reason':cfg['source_content'][source['id']],'file_deleted':False})
    else:
        if matches[0]['source_in']>0: excluded.append({'source_id':source['id'],'source_range':[0,matches[0]['source_in']],'kind':'pre_roll_or_superseded_phrase','file_deleted':False})
        if matches[-1]['source_out']<duration: excluded.append({'source_id':source['id'],'source_range':[matches[-1]['source_out'],duration],'kind':'tail_or_superseded_failed_phrase','file_deleted':False})
boundaries=[{'timeline_seconds':a['timeline_out'],'outgoing_source':a['source_id'],'outgoing_seconds':a['source_out'],'incoming_source':b['source_id'],'incoming_seconds':b['source_in'],'heard':False,'continuous_visual_review':False} for a,b in zip(keeps,keeps[1:])]
edl={'content_id':cfg['content_id'],'version':'v2','status':'FULL_CONTENT_INPUT_READY_FOR_PMO_RELEASE','not_a_render_release':True,'replaces':'v1 67.1-second partial-content proposal only; all v1 evidence preserved','source_clock':'original media seconds; half-open [in,out); speed=1','keep_ranges':keeps,'excluded_ranges_or_takes':excluded,'disabled_short_word_cuts':cfg['retained_uncertainties'],'boundaries':boundaries,'estimated_duration_seconds':round(clock,6),'duration_policy':'Actual original-speed delivery takes priority over the 60-90s writing target. Do not speed up or force-trim natural pauses to fit.','coverage':cfg['coverage'],'information_complete_against_v3_2':True,'additional_recording_required_for_information':False,'listening_acceptance':False,'parameters':{'original_speed':True,'original_timbre':True,'denoise':False,'bgm_added_at_intake':False,'source_overwritten':False},'v1_reuse':{'unchanged':['S5 source 0.45-7.95','S1 source 0.6-11.25'],'replaced':['S3 opener with N06','S2 main block with N11'],'shortened':['S3 only star segment retained'],'added':['N12 full cost/CPU mechanism block']},'production_handoff':'PMO may release unique 04 for full authorized workflow. No new per-line user approval requested. Audio naturalness and unresolved short words remain explicit 04/05 review items.'}
write('剪辑EDL-v2.json',edl)

mapped=[]
for keep in keeps:
    folder=pathlib.Path(trans[keep['source_id']]['receipt']['output_directory'])
    raw=json.loads((folder/'transcript.json').read_text())
    for i,cue in enumerate(raw['transcription'],1):
        a=cue['offsets']['from']/1000;b=cue['offsets']['to']/1000
        lo=max(a,keep['source_in']);hi=min(b,keep['source_out'])
        if hi<=lo:continue
        item={'source_id':keep['source_id'],'keep_id':keep['id'],'source_asr_json':str(folder/'transcript.json'),'source_cue_index':i,'original_asr_range':[a,b],'original_asr_text':cue['text'],'intersection_with_kept_source':[lo,hi],'timeline_range':[round(keep['timeline_in']+lo-keep['source_in'],6),round(keep['timeline_in']+hi-keep['source_in'],6)],'cue_clipped':a<lo or b>hi,'display_text_status':'ASR_EVIDENCE_NOT_FINAL_SUBTITLE'}
        if keep['source_id']=='N06' and b>keep['source_out']:item['retained_text_candidate']='DeepInfer开源了';item['note']='ASR cue also contains a following 今天 outside keep. Do not carry whole raw cue into shortened range; exact text/time still need local audition.'
        if keep['source_id']=='N11' and b>keep['source_out']:item['retained_text_candidate']='成了多个团队能用的起点';item['note']='Retained phrase ends before following failed closing attempt; do not display removed trailing words.'
        mapped.append(item)
write('字幕重映射依据-v2.json',{'content_id':cfg['content_id'],'edl_version':'v2','formula':'timeline = keep.timeline_in + source - keep.source_in; original speed','entries':mapped,'retained_uncertainties':cfg['retained_uncertainties'],'term_candidates':{'DeepSeek':['Depthic','dpsick','DeepSec'],'DeepInfer':['Depthinfer','Depthin for'],'GitHub':['给他们'],'梁文锋':['两万分','梁文芬'],'护城河':['护城和','护城盒'],'服':['扶','佛'],'算力':['算例'],'任务':['人物'],'精力':['经历'],'一支团队':['一直团队']},'final_subtitles_ready':False,'policy':'Preserve actual synonymous speech; names corrected from frozen sources do not authorize audio deletion. Split clipped cues manually and avoid claiming word-accurate ASR times.'})

lines=['# Supplement twelve full-track ASR records','', 'Read in full. Local Whisper base output is fallible, not direct listening. Old five full records remain in 全音轨转录汇总.md.','']
for source in new:
    folder=pathlib.Path(trans[source['id']]['receipt']['output_directory'])
    lines.extend(['## '+source['id'],source['path'],'SHA256 '+source['sha256'],'Original evidence '+str(folder),'','```srt',(folder/'transcript.srt').read_text().strip(),'```',''])
(ROOT/'新增12条全音轨转录汇总-v2.md').write_text('\n'.join(lines),encoding='utf-8')

report={'content_id':cfg['content_id'],'stage':'03','version':'v2','owner':'01a11a70-35e6-7db1-86ac-80a7ce40a9cb','status':'PENDING_PMO_RELEASE_WITH_COMPLETE_INFORMATION_INPUT','input_counts':{'paths':22,'independent_recordings':17,'reused_old_recordings':5,'new_complete_ASR':12,'all_SHA_accounted_for':True},'full_script_information_coverage':'COMPLETE_BY_READ_ASR_AND_SAMPLED_VIDEO','missing_information_blocks':[],'additional_recording_required_for_information':False,'coverage':cfg['coverage'],'recommended_order':[x['source_id'] for x in keeps],'estimated_original_speed_seconds':round(clock,6),'visual_review':cfg['visual_review'],'remaining_limits':['No direct native audio input; short words/pronunciation/natural joins not heard','No continuous audiovisual review','ASR is segment-level and can misrecognize terms; subtitle finalization pending','No rendering or production performed by intake Owner'],'recommendation':'Release unique 04 for complete authorized production from EDL-v2 and current source assets, not old partial 67.1s input. Resolve local audio QA during 04/05; do not ask user to approve each sentence.','rules':['PERMISSIONS-2026-10-14-v1','ROUTING-2026-10-13-v4','HANDOFF-2026-10-10-v2','ELI-REWORK-20261019-v1'],'routing':{'target_model':'gpt-6.1-sol','target_effort':'medium','actual_model':'UNKNOWN','actual_effort':'UNKNOWN','actual_speed':'UNKNOWN','weekly_usage_from_dispatch':'86%','five_hour_usage':'UNKNOWN','subagents':False},'parameters':{'speed':1,'gain_db':0,'source_modified':False,'new_models':False,'new_dependencies':False,'private_upload':False,'paid_calls':False,'rendered_mp4':False,'cleanup':False},'report_receipt':'PMO回报回执-v2.json'}
write('接收报告-v2.json',report)
print(json.dumps({'paths':22,'unique':17,'new_ASR':12,'duration':round(clock,6),'keep_order':[x['source_id'] for x in keeps],'boundary_times':[x['timeline_seconds'] for x in boundaries],'coverage_blocks':len(cfg['coverage']),'subtitle_segments':len(mapped),'new_source_duration':sum(float(x['probe']['format']['duration']) for x in new)},ensure_ascii=True,indent=2))
