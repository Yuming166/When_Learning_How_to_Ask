"""Predeclared descriptive analysis with complete denominators and replay checks."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from certification import CertifiedDecisionGate
from policies import ARMS, forced_action
from run_loop import stable_seed

HERE=Path(__file__).resolve().parent


def verify_raw(records,worlds,config):
    receipts=[]
    for r in records:
        if r['status'].startswith('FAILED_INFRASTRUCTURE'):
            receipts.append({'world_id':r['world_id'],'arm':r['arm'],'status':'UNAVAILABLE_INFRASTRUCTURE_FAILURE'})
            continue
        world=worlds[r['world_id']];public=world['public'];private=world['private']
        d=public['d']; counts=np.zeros((d,2,2),dtype=np.int64)
        sequences=[np.random.default_rng(stable_seed(private['response_seed'],str(a))).random(config['max_queries']) for a in range(2*d)]
        consumed=np.zeros(2*d,dtype=int)
        for step,event in enumerate(r['history']):
            action,answer=event['action'],event['answer'];j,fmt=divmod(action,2)
            expected_forced=forced_action(step,d)
            assert event['forced']==(expected_forced is not None)
            if expected_forced is not None:assert action==expected_forced
            accuracy=float(__import__('fractions').Fraction(private['p'] if fmt==private['types'][public['groups'][j]] else private['q']))
            correct=sequences[action][consumed[action]]<accuracy;consumed[action]+=1
            assert answer==int((private['theta'][j]>0)==correct)
            counts[j,fmt,answer]+=1
            if event['gate_status']=='CERTIFIED':assert step==len(r['history'])-1
        assert counts.tolist()==r['counts'] and int(counts.sum())==r['queries']
        if r['status']=='CERTIFIED':
            gate=CertifiedDecisionGate(public,R=config['R']).check(counts)
            assert gate['certified'] and gate['item']==r['certified_output']
            assert r['certified_correct']==(gate['item']==private['winner'])
            assert gate['gap_lower']==r['certificate']['gap_lower']
            assert gate['threshold_upper']==r['certificate']['threshold_upper']
        else:
            assert r['certified_output'] is None and r['certificate'] is None
        receipts.append({'world_id':r['world_id'],'arm':r['arm'],'status':'RAW_REPLAY_PASS',
                         'queries':r['queries'],'terminal_certificate_rechecked':r['status']=='CERTIFIED'})
    return receipts


def main():
    source=HERE/'artifacts/pilot'; config=json.loads((source/'effective_config.json').read_text())
    summaries=json.loads((source/'summary.json').read_text())
    worlds={w['id']:w for w in json.loads((source/'worlds.json').read_text())}
    expected={(w,a) for w in worlds for a in config['arms']}
    assert {(r['world_id'],r['arm']) for r in summaries}==expected
    records=[json.loads((source/f"{w}__{a}.json").read_text()) for w,a in sorted(expected)]
    replay=verify_raw(records,worlds,config)
    cap=config['max_queries']
    score=lambda r:r['queries'] if r['status']=='CERTIFIED' else cap
    metrics={}
    for arm in config['arms']:
        rows=[r for r in records if r['arm']==arm]
        metrics[arm]={'attempted':len(rows),'certified':sum(r['status']=='CERTIFIED' for r in rows),
                      'wrong_certified':sum(r.get('certified_correct') is False for r in rows),
                      'capped':sum(r['status']=='CAPPED_UNCERTIFIED' for r in rows),
                      'failed':sum(r['status'].startswith('FAILED') for r in rows),
                      'mean_capped_cost_failure_as_cap':float(np.mean([score(r) for r in rows])),
                      'median_capped_cost_failure_as_cap':float(np.median([score(r) for r in rows])),
                      'mean_observed_policy_seconds':float(np.mean([r['policy_seconds'] for r in rows if r.get('policy_seconds') is not None])),
                      'observed_wall_seconds':sum(r['wall_seconds'] for r in rows if r.get('wall_seconds') is not None),
                      'observed_cpu_seconds':sum(r['cpu_seconds'] for r in rows if r.get('cpu_seconds') is not None),
                      'exact_gate_calls':sum(r['gate_calls'] for r in rows if r.get('gate_calls') is not None),
                      'uniform_unidentified_fallback_updates':sum(u['status']=='UNIDENTIFIED_RATES_UNIFORM_TARGET' for r in rows for u in (r.get('updates') or [])),
                      'postprocessing_failures':sum(r.get('postprocessing_failure') is not None for r in rows)}
    by_key={(r['world_id'],r['arm']):r for r in records}
    pairs={}
    for arm in config['arms']:
        if arm=='decision_kl':continue
        per=[]
        for world in worlds:
            a,b=by_key[world,'decision_kl'],by_key[world,arm]
            per.append({'world_id':world,'profile_cluster':a['profile_cluster'],
                        'decision_kl_status':a['status'],'baseline_status':b['status'],
                        'decision_kl_cost':score(a),'baseline_cost':score(b),
                        'baseline_minus_method':score(b)-score(a),
                        'both_certified':a['status']==b['status']=='CERTIFIED'})
        pairs[arm]={'worlds':per,'method_cost_lower':sum(x['baseline_minus_method']>0 for x in per),
                    'equal_cost':sum(x['baseline_minus_method']==0 for x in per),
                    'method_cost_higher':sum(x['baseline_minus_method']<0 for x in per),
                    'both_certified_pairs':sum(x['both_certified'] for x in per),
                    'mean_baseline_minus_method_restricted':float(np.mean([x['baseline_minus_method'] for x in per]))}
    result={'stage':'DEVELOPMENT_NOT_CONFIRMATION','attempted':len(records),'worlds':len(worlds),
            'profile_clusters':len({w['profile_cluster'] for w in worlds.values()}),
            'anchor_worlds':sum(w['profile_kind']=='anchor_all_positive' for w in worlds.values()),
            'metrics':metrics,'paired_costs':pairs,'raw_replay':replay,
            'cost_definition':'certified tau; cap for noncertified or failed trajectory; failures separately reported',
            'uncertainty':'descriptive only; no significance inference from four constructed profile clusters',
            'risk':'analytic exp(-R) model guarantee, not estimated from zero observed errors'}
    target=HERE/'results';target.mkdir(exist_ok=True)
    (target/'analysis.json').write_text(json.dumps(result,indent=2)+'\n')
    rows=['# Bounded recommendation-loop development results','',
          f"{len(records)} trajectories; {len(worlds)} paired worlds; {result['profile_clusters']} profile clusters. Four worlds are theory anchors.",
          '', '| Arm | Certified | Capped | Failed | Wrong certified | Mean capped cost | Mean policy seconds |',
          '|---|---:|---:|---:|---:|---:|---:|']
    for arm,m in metrics.items():
        rows.append(f"| {arm} | {m['certified']}/{m['attempted']} | {m['capped']} | {m['failed']} | {m['wrong_certified']} | {m['mean_capped_cost_failure_as_cap']:.2f} | {m['mean_observed_policy_seconds']:.3f} |")
    rows += ['', 'Noncertified and failed trajectories receive the cap in this restricted-cost column; this is not their completed stopping time.',
             '', '| World | RR | Joint D-RRC | Decision IG | Profile KL | Decision KL |',
             '|---|---:|---:|---:|---:|---:|']
    for world in worlds:
        cells=[]
        for arm in config['arms']:
            r=by_key[world,arm];suffix='' if r['status']=='CERTIFIED' else (' C' if r['status']=='CAPPED_UNCERTIFIED' else ' F')
            cells.append(str(r['queries'])+suffix)
        rows.append('| '+world+' | '+' | '.join(cells)+' |')
    rows+=['', 'C=capped without certificate; F=failed. No trajectory was replaced.',
           '', 'All arms share the same screened/checkpoint interval gate, action set, iid channel and paired action-indexed streams.',
           'The gate may certify later than the ideal earliest GLR crossing. Fixed-tolerance allocation and quadrature are not certified asymptotic-optimality implementations.',
           'These results do not establish real-user reliability, universal superiority or a final method choice.']
    (target/'RESULTS.md').write_text('\n'.join(rows)+'\n')
    plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(8.2,3.2),layout='constrained')
    labels=['RR','Joint D-RRC','Decision IG','Profile KL','Decision KL']
    values=[metrics[a]['mean_capped_cost_failure_as_cap'] for a in config['arms']]
    bars=axes[0].bar(labels,values,color=['#999']*4+['#2874ad'])
    axes[0].bar_label(bars,labels=[f"{metrics[a]['certified']}/8 cert." for a in config['arms']],padding=3,fontsize=7)
    axes[0].set(ylabel='Mean capped cost (queries)',title='Controlled development: 8 worlds')
    times=[metrics[a]['mean_observed_policy_seconds'] for a in config['arms']]
    axes[1].bar(labels,times,color=['#999']*4+['#2874ad'])
    axes[1].set(yscale='log',ylabel='Mean policy seconds (log)',title='Computation, including planning')
    for ax in axes:ax.tick_params(axis='x',labelrotation=25)
    for ext in ('png','pdf'):fig.savefig(target/f'cost_comparison.{ext}',dpi=220)
    plt.close(fig)
    print(json.dumps({'attempted':len(records),'raw_replay':'PASS','metrics':metrics,'pairs':{a:{k:v for k,v in p.items() if k!='worlds'} for a,p in pairs.items()}},indent=2))


if __name__=='__main__':main()
