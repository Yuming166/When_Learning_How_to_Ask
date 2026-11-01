"""Final source/analysis/render engineering check; never creates benchmark entropy."""
import importlib.util
import json
import sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from t1d.policy import run_policy
from t1d.preflight import LiteralClient
from t1d.roster import roster,jobs
from t1d.strategies import POLICIES
from tests.test_contract import public


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def main():
    fixture=ROOT/'audit/fixtures'; checked=0
    for line in (fixture/'trajectories.jsonl').read_text().splitlines():
        old=json.loads(line)
        if old['policy']!='WorstFact-MI':continue
        client=LiteralClient(public(old['partition']),old['calibration'])
        detail=run_policy(client,'WorstFact-MI',old)
        assert detail['fit']['theta']==old['fit']['theta']
        assert np.array_equal(detail['counts'],old['counts']) and detail['type_answers']==old['type_answers']
        assert [h['action'] for h in detail['estimation_history'][-1]['action_history']]==[h['action'] for h in old['estimation_history'][-1]['action_history']]
        checked+=1
    analysis=module('t1d_frozen_analysis',ROOT/'audit/analyze.py');a=analysis.Analysis(fixture,engineering=True)
    result,valid,paired=a.run(write=False)
    assert valid['passed'],valid['errors']
    for arm in POLICIES:assert isinstance(result['summaries'][32][arm]['exact'],int)
    convert=lambda v:json.loads(json.dumps(v,allow_nan=False))
    renderer=module('t1d_frozen_render',ROOT/'audit/render.py')
    docs=renderer.render(*map(convert,[result,valid,paired,a.stratified,a.runtime]),write_files=False)
    assert all(len(docs[name])>100 for name in ['FINAL_DECISION.md','COMPUTATIONAL_COST.md','CROSS_BUDGET_EVALUATION.md'])
    cfg=json.loads((ROOT/'config.json').read_text());worlds=roster(cfg);plan=jobs(cfg)
    panels={p['name']:sum(w['panel']==p['name'] for w in worlds) for p in cfg['panels']}
    assert len(worlds)==len({w['index'] for w in worlds})==96 and set(panels.values())=={24}
    maximum=sum(j['budget'] for j in plan)*len(POLICIES);assert maximum==215040<=cfg['limits']['online_actions']
    pref=json.loads((ROOT/'PREFLIGHT.json').read_text())
    projected=pref['CPU']/4*96*1.75
    gates={'passed':valid['passed'] and projected<=2200,'literal_fixture_paths':valid['finished_paths'],
           'literal_observation_checks':sum(valid['checks'].values()),'final_worst_MI_fixture_rechecks':checked,
           'source_and_renderer_smoke_passed':True,'distinct_contract_tests':9,
           'engineering_compile_corrections_before_execution':2,'scientific_worlds_consumed':0,
           'planned_worlds':len(worlds),'panels':panels,'policies':len(POLICIES),'planned_paths':len(plan)*len(POLICIES),
           'planned_online':maximum,'projected_scientific_CPU_with_1p75_margin':projected,
           'hard_wall_seconds':cfg['limits']['wall_seconds'],'sources_must_be_sealed_before_entropy':True}
    (ROOT/'PREFLIGHT_GATES.json').write_text(json.dumps(gates,indent=2)+'\n')
    (ROOT/'audit/ANALYSIS_PREFLIGHT.json').write_text(json.dumps({'scope':'literal engineering, not efficacy','passed':valid['passed'],'checks':valid['checks'],'errors':valid['errors'],'fixture_paths':valid['finished_paths'],'rendered_in_memory':list(docs),'scientific_worlds':0},indent=2)+'\n')
    print(json.dumps(gates))


if __name__=='__main__':main()
