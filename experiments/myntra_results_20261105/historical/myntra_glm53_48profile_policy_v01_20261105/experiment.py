"""Frozen, no-retry HTTPS collection and paired deterministic policy replay."""
from __future__ import annotations
import argparse
import concurrent.futures as cf
import datetime as dt
import getpass
import hashlib
import json
import math
import multiprocessing
import os
from pathlib import Path
import random
import re
import statistics
import threading
import time
import urllib.error
import urllib.request
from stream_transport import StreamTransport, StreamProtocolError

import engine
import environment as ref
import replay

BASE = Path(__file__).resolve().parent
CFG = json.loads((BASE/'config.json').read_text())
INPUT = BASE/'artifacts/input'
REFERENCE = BASE/'artifacts/reference'
RUN = BASE/'artifacts/run'
RESULTS = BASE/'results'
LOCK = threading.Lock()


def read(path):
    return json.loads(Path(path).read_text())


def rows(path):
    p = Path(path)
    return [json.loads(s) for s in p.read_text().splitlines() if s.strip()] if p.exists() else []


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def write(path, obj):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix+'.tmp')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n')
    tmp.replace(p)


def write_rows(path, values):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(''.join(canonical(v)+'\n' for v in values))


def append(path, obj):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('a') as handle:
        handle.write(canonical(obj)+'\n')


def frozen_requests():
    return rows(INPUT/'prompts/http_requests.jsonl')


def freeze():
    if (BASE/'FROZEN.json').exists() or rows(RUN/'ATTEMPTS.jsonl'):
        raise RuntimeError('Preserve existing freeze and attempts')
    source_prompts = rows(INPUT/'prompts/requests.jsonl')
    payloads = []
    for p in source_prompts:
        assert hashlib.sha256(p['prompt'].encode()).hexdigest() == p['prompt_sha256']
        payload = {'model': CFG['requested_model'],
                   'messages': [{'role': 'user', 'content': p['prompt']}], **CFG['api_parameters']}
        payloads.append({'job_id': p['job_id'], 'prompt_sha256': p['prompt_sha256'],
                         'body': payload, 'body_sha256': hashlib.sha256(canonical(payload).encode()).hexdigest()})
    write_rows(INPUT/'prompts/http_requests.jsonl', payloads)
    files = {str(p.relative_to(BASE)): digest(p) for p in sorted(BASE.rglob('*'))
             if p.is_file() and '__pycache__' not in p.parts
             and p.name != 'FROZEN.json' and 'results' not in p.relative_to(BASE).parts
             and 'run' not in p.relative_to(BASE).parts}
    record = {'status': 'FROZEN_PRE_INFERENCE', 'frozen_utc': now(),
              'requested_model': CFG['requested_model'], 'base_url': CFG['base_url'],
              'planned_calls': CFG['planned_calls'], 'files': files,
              'credential_in_manifest': False, 'decode_parameters': CFG['api_parameters']}
    write(BASE/'FROZEN.json', record)
    return {'status': record['status'], 'files': len(files), 'model_calls': 0}


def verify():
    manifest = read(BASE/'FROZEN.json')
    if manifest['status'] != 'FROZEN_PRE_INFERENCE':
        raise RuntimeError('Unexpected frozen contract')
    bad = [name for name,h in manifest['files'].items()
           if not (BASE/name).is_file() or digest(BASE/name) != h]
    if bad:
        raise RuntimeError('Frozen files changed: '+', '.join(bad[:5]))
    return {'status': 'FROZEN_HASHES_PASS', 'files': len(manifest['files'])}


def load_context():
    profiles = {p['profile_id']: p for p in rows(INPUT/'private/profiles.jsonl')}
    priors = rows(INPUT/'private/prior_profiles.jsonl')
    source_cfg = read(REFERENCE/'ENVIRONMENT_CONFIG.json')
    return {'profiles': profiles, 'menus': {m['menu_id']: m for m in rows(INPUT/'public/menus.jsonl')},
            'cases': rows(INPUT/'private/selected_cases.jsonl'),
            'vocab': read(INPUT/'public/vocabularies.json'),
            'thresholds': source_cfg['purchase_thresholds'],
            'priors': {i: [p for p in priors if p['pool_index']==i] for i in range(6)}}


def make_bank(records, context):
    result = {}
    for job in rows(INPUT/'private/jobs.jsonl'):
        record = dict(records.get(job['job_id'], {'valid': False, 'attempted': False,
                                                 'error_class': 'not_attempted'}))
        expected = ref.ReferenceUser(context['profiles'][job['profile_id']]).answer(job['query_action'])
        record['exact_profile_match'] = bool(record.get('valid') and
            canonical(record['parsed']['value']) == canonical(expected))
        result[(job['profile_id'], job['query_action'])] = record
    return result


def bank_signature(bank, profile_id):
    signature = []
    for action in CFG['query_actions']:
        r = bank[(profile_id, action)]
        signature.append([action, bool(r.get('valid')),
                          r['parsed']['value'] if r.get('valid') else None,
                          bool(r.get('exact_profile_match'))])
    return canonical(signature)


def record_map(directory):
    return {p.stem: read(p) for p in sorted(Path(directory).glob('*.json'))}


def replay_case(case, context, bank):
    profile = context['profiles'][case['profile_id']]
    public = {**case, 'public_menu': context['menus'][case['menu_id']]}
    observed = {(a,1): bank[(profile['profile_id'],a)] for a in CFG['query_actions']}
    output = []
    for method in CFG['methods']:
        output.extend(replay._case_trace(ref, public, profile, context['priors'][profile['pool_index']],
                       method, 1, observed, context['vocab'][str(profile['pool_index'])], context['thresholds']))
    return output


def smoke_replay():
    verify()
    context = load_context()
    records = record_map(RUN/'records')
    jobs = [j for j in rows(INPUT/'private/jobs.jsonl') if j['profile_id']==CFG['smoke_profile_id']]
    if len(jobs)!=6 or any(j['job_id'] not in records for j in jobs):
        raise RuntimeError('Incomplete smoke inventory')
    if any(not records[j['job_id']].get('transport_ok') for j in jobs):
        return {'status': 'FAIL_TRANSPORT_OR_MODEL', 'model_calls': len(jobs)}
    bank = make_bank(records, context)
    old = make_bank(record_map(REFERENCE/'luna_records'), context)
    case = next(c for c in context['cases'] if c['profile_id']==CFG['smoke_profile_id'])
    traces = replay_case(case, context, bank)
    cached = [r for r in rows(REFERENCE/'LUNA_PAIRED_POLICY_TRACES.jsonl') if r['case_id']==case['case_id']]
    equivalent = bank_signature(bank,case['profile_id']) == bank_signature(old,case['profile_id'])
    parity = not equivalent or traces == cached
    receipt = {'status': 'PASS' if len(traces)==28 and parity else 'FAIL_REPLAY_PARITY',
               'profile_id': case['profile_id'], 'case_id': case['case_id'],
               'valid_answers': sum(bool(records[j['job_id']].get('valid')) for j in jobs),
               'trace_rows': len(traces), 'luna_bank_equivalent': equivalent,
               'luna_trace_exact_parity_when_equivalent': parity, 'model_calls': 6}
    write(BASE/'SMOKE_REPLAY_RECEIPT.json', receipt)
    return receipt


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, 'redirect_refused', headers, fp)


def validate_response(payload, job, context):
    model = payload.get('model')
    if model not in CFG['accepted_reported_models']:
        return {'transport_ok': False, 'valid': False, 'error_class': 'reported_model_mismatch',
                'reported_model_strings': [model] if isinstance(model,str) else []}
    result = {'transport_ok': True, 'valid': False, 'reported_model_strings': [model],
              'usage': payload.get('usage'), 'response_id': payload.get('id')}
    try:
        choices = payload['choices']
        if len(choices)!=1:
            raise ValueError('choice_count')
        choice = choices[0]
        result['finish_reason'] = choice.get('finish_reason')
        if choice.get('finish_reason') != 'stop':
            raise ValueError('non_stop_finish')
        message = choice['message']
        if message.get('tool_calls'):
            raise ValueError('unexpected_tool_call')
        content = message.get('content')
        result['content'] = content
        parsed = replay.parse_field_answer(job['query_action'], content,
                    context['vocab'][str(job['pool_index'])], context['thresholds'])
        result.update(valid=True, parsed={'value': parsed})
    except Exception as exc:
        result.update(error_class='invalid_answer', parse_error=type(exc).__name__+': '+str(exc)[:120])
    return result


def collect(api_key):
    verify()
    if rows(RUN/'ATTEMPTS.jsonl') or list((RUN/'records').glob('*.json')):
        raise RuntimeError('Already attempted: no automatic rerun or retry')
    context = load_context()
    jobs = rows(INPUT/'private/jobs.jsonl')
    request_bank = {r['job_id']: r for r in frozen_requests()}
    state = {'start': time.monotonic(), 'attempted': 0, 'consecutive_failures': 0,
             'transport_failures': 0, 'abort_reason': None}
    transport = StreamTransport(CFG)
    endpoint = CFG['base_url'].rstrip('/')+'/chat/completions'

    def redact(text):
        return re.sub(r'sk-[A-Za-z0-9_.-]+', '[REDACTED]', str(text).replace(api_key,'[REDACTED]'))

    def one(job):
        jid = job['job_id']
        with LOCK:
            if time.monotonic()-state['start'] >= CFG['total_wall_seconds']:
                state['abort_reason'] = 'global_dispatch_deadline'
            if state['abort_reason']:
                result = {**job, 'attempted': False, 'valid': False, 'transport_ok': False,
                          'not_attempted_reason': state['abort_reason']}
                write(RUN/'records'/f'{jid}.json', result)
                return result
            state['attempted'] += 1
            number = state['attempted']
            append(RUN/'ATTEMPTS.jsonl', {'job_id':jid, 'attempt_number':number, 'started_utc':now(),
                'request_sha256':request_bank[jid]['body_sha256'], 'requested_model':CFG['requested_model']})
        started = time.monotonic()
        result = {**job, 'attempted':True, 'attempt_number':number, 'started_utc':now(),
                  'requested_model':CFG['requested_model'], 'request_sha256':request_bank[jid]['body_sha256']}
        try:
            body = canonical(request_bank[jid]['body']).encode()
            assert hashlib.sha256(body).hexdigest() == request_bank[jid]['body_sha256']
            time.sleep(CFG['minimum_request_interval_seconds'])
            response_path = RUN/'responses'/f'{jid}.sse'
            payload, meta = transport.call(endpoint, body, api_key, response_path)
            result.update(meta)
            result['response_sha256'] = digest(response_path)
            result.update(validate_response(payload, job, context))
        except StreamProtocolError as exc:
            result.update(transport_ok=False, valid=False, error_class=exc.reason,
                          error=redact(str(exc))[:500], http_status=exc.status,
                          reported_model_strings=exc.models)
        except urllib.error.HTTPError as exc:
            raw = redact(exc.read().decode('utf-8',errors='replace'))
            result.update(transport_ok=False, valid=False, error_class='http_error',
                          http_status=exc.code, provider_error=raw[:2000])
        except Exception as exc:
            result.update(transport_ok=False, valid=False, error_class=type(exc).__name__,
                          error=redact(str(exc))[:500])
        result.update(finished_utc=now(), latency_seconds=time.monotonic()-started)
        with LOCK:
            if result.get('transport_ok'):
                state['consecutive_failures'] = 0
            else:
                state['transport_failures'] += 1
                state['consecutive_failures'] += 1
                if result.get('error_class')=='reported_model_mismatch':
                    state['abort_reason']='reported_model_mismatch'
                elif result.get('http_status') in (400,401,402,403,404,422):
                    state['abort_reason']='http_contract_or_auth_'+str(result['http_status'])
                elif state['consecutive_failures']>=3:
                    state['abort_reason']='three_consecutive_transport_failures'
        write(RUN/'records'/f'{jid}.json', result)
        return result

    def phase(name, selected):
        outputs = []
        start = now()
        print(canonical({'phase':name,'planned':len(selected),'status':'STARTED'}),flush=True)
        with cf.ThreadPoolExecutor(max_workers=CFG['concurrency']) as pool:
            for fut in cf.as_completed([pool.submit(one,j) for j in selected]):
                result=fut.result()
                outputs.append(result)
                if len(outputs)%24==0 or len(outputs)==len(selected):
                    print(canonical({'phase':name,'completed':len(outputs),'planned':len(selected),
                        'valid':sum(bool(r.get('valid')) for r in outputs),
                        'transport_failures':state['transport_failures'],'abort_reason':state['abort_reason']}),flush=True)
        receipt={'phase':name,'status':'PHASE_COMPLETED' if not state['abort_reason'] else 'STOPPED',
                 'started_utc':start,'finished_utc':now(),'records':len(outputs),
                 'attempted':sum(bool(r.get('attempted')) for r in outputs),
                 'valid':sum(bool(r.get('valid')) for r in outputs), 'abort_reason':state['abort_reason']}
        write(BASE/('SMOKE_RECEIPT.json' if name=='smoke' else 'FULL_RECEIPT.json'), receipt)
        return receipt

    smoke = [j for j in jobs if j['profile_id']==CFG['smoke_profile_id']]
    phase('smoke',smoke)
    check=smoke_replay()
    print(canonical({'smoke_replay':check}),flush=True)
    if check['status']=='PASS' and not state['abort_reason']:
        phase('full',[j for j in jobs if j not in smoke])
    else:
        state['abort_reason']=state['abort_reason'] or 'smoke_replay_failed'
    # Account explicitly for every unattempted planned job.
    existing=record_map(RUN/'records')
    for job in jobs:
        if job['job_id'] not in existing:
            write(RUN/'records'/(job['job_id']+'.json'),{**job,'attempted':False,'valid':False,
                'transport_ok':False,'not_attempted_reason':state['abort_reason'] or 'not_dispatched'})
    records=record_map(RUN/'records')
    receipt={'status':'COLLECTION_COMPLETE' if state['attempted']==len(jobs) and not state['abort_reason'] else 'COLLECTION_STOPPED',
        'finished_utc':now(),'planned':len(jobs),'attempted':state['attempted'],'records':len(records),
        'valid':sum(bool(r.get('valid')) for r in records.values()),'transport_failures':state['transport_failures'],
        'abort_reason':state['abort_reason'],'retries':0,'concurrency':CFG['concurrency'],
        'wall_seconds':time.monotonic()-state['start'],
        'reported_models':sorted({m for r in records.values() for m in r.get('reported_model_strings',[])})}
    write(BASE/'RUN_RECEIPT.json',receipt)
    transport.close()
    print(canonical(receipt),flush=True)
    return receipt


def bootstrap_plan(cases):
    ids = sorted({c['profile_id'] for c in cases})
    index = {p:i for i,p in enumerate(ids)}
    strata = {}
    for c in cases:
        strata.setdefault(c['stratum'],set()).add(c['profile_id'])
    rng=random.Random(CFG['bootstrap_seed'])
    ordered=[sorted(ps) for ps in strata.values()]
    draws=[[index[rng.choice(ps)] for ps in ordered for _ in ps]
           for _ in range(CFG['bootstrap_repetitions'])]
    return ids,draws


def paired_difference(cases,left,right,plan):
    ids,draws=plan
    diffs={p:[] for p in ids}
    for c in cases:
        diffs[c['profile_id']].append(int(left[c['case_id']])-int(right[c['case_id']]))
    totals=[sum(diffs[p]) for p in ids]
    counts=[len(diffs[p]) for p in ids]
    samples=sorted(sum(totals[i] for i in draw)/sum(counts[i] for i in draw) for draw in draws)
    def percentile(q):
        position=(len(samples)-1)*q
        lo,hi=math.floor(position),math.ceil(position)
        return samples[lo] if lo==hi else samples[lo]*(hi-position)+samples[hi]*(position-lo)
    all_diffs=[v for p in ids for v in diffs[p]]
    return {'difference':sum(all_diffs)/len(all_diffs),'cluster_bootstrap_95_ci':[percentile(.025),percentile(.975)],
            'case_wins':sum(v>0 for v in all_diffs),'case_ties':sum(v==0 for v in all_diffs),
            'case_losses':sum(v<0 for v in all_diffs),
            'profile_clusters_win':sum(v>0 for v in totals),'profile_clusters_tie':sum(v==0 for v in totals),
            'profile_clusters_loss':sum(v<0 for v in totals)}


def trace_lookup(traces):
    result={(r['case_id'],r['method'],r['budget']):r for r in traces}
    if len(result)!=len(traces):
        raise RuntimeError('Duplicate traces')
    return result


def validate_reference_statistics():
    context=load_context()
    cases=context['cases']
    plan=bootstrap_plan(cases)
    old=read(REFERENCE/'LUNA_ANALYSIS.json')
    lookup=trace_lookup(rows(REFERENCE/'LUNA_PAIRED_POLICY_TRACES.jsonl'))
    if len(lookup)!=280*4*7:
        raise RuntimeError('Reference coverage mismatch')
    for b in CFG['budgets']:
        dv={c['case_id']:lookup[(c['case_id'],'decision_value',b)]['exact_decision_correct'] for c in cases}
        for m in CFG['methods']:
            values={c['case_id']:lookup[(c['case_id'],m,b)]['exact_decision_correct'] for c in cases}
            assert sum(values.values())==old['budget_metrics'][m][str(b)]['correct']
            if m=='decision_value':
                continue
            result=paired_difference(cases,dv,values,plan)
            expected=old['decision_value_pairwise'][str(b)][m]
            for key in ('difference','cluster_bootstrap_95_ci','case_wins','case_losses',
                        'case_ties','profile_clusters_win','profile_clusters_tie','profile_clusters_loss'):
                if result[key]!=expected[key]:
                    raise RuntimeError(f'Bootstrap/reference parity failed: {b}/{m}/{key}')
    return {'status':'REFERENCE_STATISTICS_EXACT_PARITY','cells':28,'paired_comparisons':21,
            'bootstrap_repetitions':CFG['bootstrap_repetitions']}


WORKER={}


def init_worker():
    context=load_context()
    WORKER.update(context=context,bank=make_bank(record_map(RUN/'records'),context))


def worker(case):
    return replay_case(case,WORKER['context'],WORKER['bank'])


def analyze():
    verify()
    context=load_context()
    cases=context['cases']
    records=record_map(RUN/'records')
    if len(records)!=288:
        raise RuntimeError('Run collection first; all planned records required')
    bank=make_bank(records,context)
    old_bank=make_bank(record_map(REFERENCE/'luna_records'),context)
    equivalent={pid for pid in context['profiles'] if bank_signature(bank,pid)==bank_signature(old_bank,pid)}
    old_traces=rows(REFERENCE/'LUNA_PAIRED_POLICY_TRACES.jsonl')
    traces=[r for r in old_traces if r['profile_id'] in equivalent]
    changed=[c for c in cases if c['profile_id'] not in equivalent]
    cache_receipt={'eligible_profiles':len(equivalent),'reused_cases':280-len(changed),'recomputed_cases':len(changed),
                   'reused_trace_rows':len(traces),'rule':'complete effective answer bank equality; frozen identical inputs and policy'}
    print(canonical({'offline_replay':cache_receipt}),flush=True)
    if changed:
        with cf.ProcessPoolExecutor(max_workers=CFG['analysis_workers'],
                 mp_context=multiprocessing.get_context('spawn'),initializer=init_worker) as pool:
            for count,new in enumerate(pool.map(worker,changed,chunksize=1),1):
                traces.extend(new)
                if count%5==0 or count==len(changed):
                    print(canonical({'recomputed_cases':count,'planned_changed_cases':len(changed)}),flush=True)
    lookup=trace_lookup(traces)
    expected={(c['case_id'],m,b) for c in cases for m in CFG['methods'] for b in CFG['budgets']}
    if set(lookup)!=expected:
        raise RuntimeError('Incomplete trace coverage')
    traces=[lookup[(c['case_id'],m,b)] for c in cases for m in CFG['methods'] for b in CFG['budgets']]
    write_rows(RESULTS/'PAIRED_POLICY_TRACES.jsonl',traces)
    metrics={}
    for m in CFG['methods']:
        metrics[m]={}
        for b in CFG['budgets']:
            group=[lookup[(c['case_id'],m,b)] for c in cases]
            n=len(group)
            buy=[r for r in group if r['reference_decision']=='BUY']
            no_buy=[r for r in group if r['reference_decision']=='NO_BUY']
            metrics[m][str(b)]={'n':n,'correct':sum(r['exact_decision_correct'] for r in group),
                'accuracy':sum(r['exact_decision_correct'] for r in group)/n,
                'failed_paths':sum(not r['answer_path_complete'] for r in group),
                'hard_violations':sum(r['hard_constraint_violation'] for r in group),
                'false_purchases':sum(r['false_purchase_case'] for r in group),
                'mean_query_units':sum(r['elicitation_units'] for r in group)/n,
                'mean_score_regret':sum(r['score_regret'] for r in group)/n,
                'mean_normalized_score_regret':sum(r['normalized_score_regret'] for r in group)/n,
                'buy_cases':len(buy),'buy_correct':sum(r['exact_decision_correct'] for r in buy),
                'no_buy_cases':len(no_buy),'no_buy_correct':sum(r['exact_decision_correct'] for r in no_buy)}
    plan=bootstrap_plan(cases)
    pairwise={}
    model_pairwise={}
    old_lookup=trace_lookup(old_traces)
    for b in CFG['budgets']:
        pairwise[str(b)]={}
        model_pairwise[str(b)]={}
        dv={c['case_id']:lookup[(c['case_id'],'decision_value',b)]['exact_decision_correct'] for c in cases}
        for m in CFG['methods']:
            values={c['case_id']:lookup[(c['case_id'],m,b)]['exact_decision_correct'] for c in cases}
            luna={c['case_id']:old_lookup[(c['case_id'],m,b)]['exact_decision_correct'] for c in cases}
            if m!='decision_value':
                pairwise[str(b)][m]=paired_difference(cases,dv,values,plan)
            comp=paired_difference(cases,values,luna,plan)
            comp['selected_action_agreement']=sum(lookup[(c['case_id'],m,b)]['selected_action']==
                    old_lookup[(c['case_id'],m,b)]['selected_action'] for c in cases)
            comp['query_sequence_agreement']=sum(lookup[(c['case_id'],m,b)]['query_sequence']==
                    old_lookup[(c['case_id'],m,b)]['query_sequence'] for c in cases)
            model_pairwise[str(b)][m]=comp
    field_quality={}
    for action in CFG['query_actions']:
        values=[bank[(pid,action)] for pid in context['profiles']]
        field_quality[action]={'planned':len(values),'attempted':sum(bool(r.get('attempted')) for r in values),
                'valid':sum(bool(r.get('valid')) for r in values),
                'exact':sum(bool(r.get('exact_profile_match')) for r in values)}
    pool_metrics=[]
    for pool in range(6):
        selected=[c for c in cases if c['prior_pool_index']==pool]
        for b in CFG['budgets']:
            pool_metrics.append({'pool':pool,'category':selected[0]['category'],'budget':b,'n':len(selected),
               'methods':{m:sum(lookup[(c['case_id'],m,b)]['exact_decision_correct'] for c in selected)
                          for m in CFG['methods']}})
    profile_metrics=[]
    for pid in context['profiles']:
        selected=[c for c in cases if c['profile_id']==pid]
        for b in CFG['budgets']:
            profile_metrics.append({'profile_id':pid,'budget':b,'n':len(selected),
                'methods':{m:sum(lookup[(c['case_id'],m,b)]['exact_decision_correct'] for c in selected)
                           for m in CFG['methods']}})
    usage={}
    for r in records.values():
        for k,v in (r.get('usage') or {}).items():
            if type(v) is int:
                usage[k]=usage.get(k,0)+v
    latencies=[r['latency_seconds'] for r in records.values() if r.get('attempted')]
    failed=[{'job_id':r['job_id'],'error_class':r.get('error_class'),'parse_error':r.get('parse_error')}
            for r in records.values() if not r.get('valid')]
    summary={'status':'ANALYZED_COMPLETE' if read(BASE/'RUN_RECEIPT.json')['status']=='COLLECTION_COMPLETE' else 'ANALYZED_STOPPED_RUN',
        'requested_model':CFG['requested_model'],'reported_models':read(BASE/'RUN_RECEIPT.json')['reported_models'],
        'provider':'Qianwen / Alibaba Cloud Model Studio','base_url':CFG['base_url'],
        'unique_profiles':48,'unique_menus':35,'profile_menu_cases':280,'planned_calls':288,
        'attempted_calls':sum(bool(r.get('attempted')) for r in records.values()),
        'valid_answers':sum(v['valid'] for v in field_quality.values()),
        'exact_profile_field_matches':sum(v['exact'] for v in field_quality.values()),
        'field_answer_quality':field_quality,'invalid_answers':failed,'budget_metrics':metrics,
        'decision_value_pairwise':pairwise,'model_minus_luna_pairwise':model_pairwise,
        'pool_metrics':pool_metrics,'profile_metrics':profile_metrics,'cache_receipt':cache_receipt,
        'token_usage':usage,'latency_seconds_mean':statistics.mean(latencies) if latencies else None,
        'latency_seconds_median':statistics.median(latencies) if latencies else None,
        'effective_answer_bank_identical_to_luna_profiles':sorted(equivalent),
        'confidence_interval_note':'48 profile clusters, 12 pool/cohort strata, 10,000 bootstrap draws, fixed menus; descriptive development panel',
        'claim_limit':'Same reused development panel; third specified customer model/API deployment; not broad natural/human-agent transfer evidence.'}
    write(RESULTS/'ANALYSIS.json',summary)
    write_report(summary)
    artifacts={str(p.relative_to(BASE)):digest(p) for root in (RUN,RESULTS) for p in sorted(root.rglob('*'))
               if p.is_file() and p.name!='OUTPUT_MANIFEST.json'}
    write(RESULTS/'OUTPUT_MANIFEST.json',{'finished_utc':now(),'frozen_contract_sha256':digest(BASE/'FROZEN.json'),'files':artifacts})
    print(canonical({'status':summary['status'],'valid':summary['valid_answers'],
                     'exact':summary['exact_profile_field_matches'],'cache':cache_receipt}),flush=True)
    return summary


def write_report(summary):
    from reporting import enrich_and_write
    enrich_and_write(summary)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=['freeze','verify','validate-reference','run','analyze'])
    command=parser.parse_args().command
    if command=='freeze': print(canonical(freeze()))
    elif command=='verify': print(canonical(verify()))
    elif command=='validate-reference':
        result=validate_reference_statistics()
        write(BASE/'REFERENCE_PARITY_RECEIPT.json',result)
        print(canonical(result))
    elif command=='run':
        verify()
        api_key=os.environ.get('DASHSCOPE_API_KEY') or getpass.getpass('API key (memory only, hidden): ')
        if not api_key.strip(): raise ValueError('Empty credential')
        collect(api_key.strip())
        api_key=None
    elif command=='analyze': analyze()


if __name__=='__main__':
    main()
