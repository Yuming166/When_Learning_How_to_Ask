"""Literal engineering streams, not generated QRelBench worlds or training rollouts."""
import hashlib
import json
import time
import sys
from collections import Counter
from types import SimpleNamespace
import numpy as np
from .bootstrap import ROOT
from .policy import run_policy
from .strategies import POLICIES
from phase2d.runner import audit_estimate
from tests.test_contract import public


class LiteralClient:
    def __init__(self, public_view, calibration):
        self.view=public_view; self.cal=calibration; self.trace=[]; self.offset=Counter(); self.cost={'task':0,'type':0,'offline':0}
    def record(self,a,args,result):
        self.trace.append({'action':a,'args':args,'result':result}); return result
    def reset(self): return self.record('reset',{},self.view)
    def get_calibration(self):
        self.cost['offline']=2*len(self.cal['high']); return self.record('get_calibration',{},self.cal)
    def query(self,j,format):
        a=2*j+'AB'.index(format); n=self.offset[a]; self.offset[a]+=1; self.cost['task']+=1
        y=int((7*a+3*n+n//3)%5<3)
        return self.record('query',{'j':j,'format':format},{'answer':y})
    def ask_type(self,g):
        a=2*self.view['d']+g; n=self.offset[a]; self.offset[a]+=1; self.cost['type']+=1
        return self.record('ask_type',{'group':g},{'format':'AB'[int((a+n)%3>0)]})
    def _call(self,method,**kwargs):
        if method!='snapshot':raise ValueError('Engineering snapshot only')
        return {'recorded':True}
    def submit(self,guess):return self.record('submit',{'predictions':guess},{'submitted':True})


def main():
    folder=ROOT/'audit/fixtures'
    extra='--append-fixed-type' in sys.argv
    if folder.exists() and not extra:raise RuntimeError('Preserve engineering preflight output')
    if extra:
        initial=json.loads((ROOT/'PREFLIGHT.json').read_text())
        (ROOT/'audit/PREFLIGHT_INITIAL_12.json').write_text(json.dumps(initial,indent=2)+'\n')
    else:folder.mkdir()
    mode='a' if extra else 'x'
    wall=time.monotonic(); start=time.process_time(); costs=Counter(); runtimes=Counter(); rows=0
    conditions=[('ID',[1,3],0),('OOD-rate',[2,2],0),('OOD-partition',[1,2],0),('OOD-calibration',[4],1)]
    with (folder/'trajectories.jsonl').open(mode) as out,(folder/'reproduction.jsonl').open(mode) as private,(folder/'failures.jsonl').open(mode) as failures:
        for index,(panel,part,alpha) in enumerate(conditions):
            d=sum(part); literal_truth=[j%2 for j in range(d)]; literal_types=[g%2 for g in range(len(part))]
            M=16*alpha; calibration={'high':([1,1,1,0]*(M//4)),'low':([1,0]*(M//2))}
            for B in [16,32,48,64]:
                job={'index':index,'cell':index,'panel':panel,'partition':part,'p':.8,'q':.6,'alpha':alpha,'R':16,'s':.8,'eta':.05,'M':M,'budget':B,'online_cap':B,'replicate':0}
                for name in (POLICIES[-2:] if extra else POLICIES):
                    client=LiteralClient(public(part),calibration); detail=run_policy(client,name,job)
                    detail['estimation_history']=[audit_estimate(e,SimpleNamespace(truth=literal_truth,types=literal_types),.8,.6) for e in detail['estimation_history']]
                    e=detail['estimation_history'][-1]; probs=np.array(e['joint_theta_distribution']); ti=sum(bit<<(d-j-1) for j,bit in enumerate(literal_truth))
                    hh=hashlib.sha256()
                    for ev in client.trace:hh.update(json.dumps(ev,sort_keys=True,separators=(',',':')).encode()+b'\n')
                    final={**job,**detail,'policy':name,'costs':client.cost,'calibration':calibration,
                        'total_acquisition':sum(client.cost.values()),'censored':not detail['complete'],
                        'forced_tasks':int(np.sum(detail['forced_counts'])),'transcript_sha256':hh.hexdigest(),
                        'exact':detail['fit']['theta']==literal_truth,'correct_facts':sum(x==y for x,y in zip(detail['fit']['theta'],literal_truth)),
                        'posterior_quality_posthoc':{'joint_nll':float(-np.log(max(probs[ti],1e-300))),'joint_brier':float(np.sum((probs-np.eye(2**d)[ti])**2))}}
                    out.write(json.dumps(final)+'\n'); private.write(json.dumps({'job':job,'policy':name,'truth':literal_truth,'types':literal_types,'trace_prefix':client.trace,'full_trace_sha256':hh.hexdigest()})+'\n')
                    costs.update(client.cost); runtimes[name]+=detail['trajectory_cpu_seconds']; rows+=1
    if extra:
        rows+=initial['paths']; costs['task']+=initial['literal_query_records']; runtimes.update(initial['policy_CPU'])
    result={'scope':'224 deterministic literal engineering paths across d3/d4; initial 12 arms preserved, only 2 fixed-type arms appended; no benchmark world or scientific entropy generated; outcomes are not efficacy results',
            'paths':rows,'worlds':0,'literal_query_records':costs['task']+costs['type'],'CPU':time.process_time()-start+(initial['CPU'] if extra else 0),'wall':time.monotonic()-wall+(initial['wall'] if extra else 0),
            'policy_CPU':dict(runtimes),'tests_log_sha256':hashlib.sha256((ROOT/'audit/CONTRACT_TESTS.txt').read_bytes()).hexdigest(),
            'fixed_type_test_sha256':hashlib.sha256((ROOT/'audit/FIXED_TYPE_TEST.txt').read_bytes()).hexdigest(),
            'fixture_files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir()}}
    (ROOT/'PREFLIGHT.json').write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps({k:v for k,v in result.items() if k!='fixture_files'}))


if __name__=='__main__':main()
