"""Post-hoc numeric audit on retained IG histories; no new environment queries."""
import json
from pathlib import Path

import numpy as np

from decision_ig import QuadratureDecisionIG

HERE=Path(__file__).resolve().parent


def choose(scores,counts,absolute):
    best=float(max(scores))
    tolerance=1e-14 if absolute else 64*np.finfo(float).eps*abs(best)
    ties=np.flatnonzero(scores>=best-tolerance)
    return int(ties[np.argmin(counts[ties])])


def main():
    source=HERE/'artifacts/pilot'
    worlds=json.loads((source/'worlds.json').read_text())
    rows=[]
    for world in worlds:
        record=json.loads((source/f"{world['id']}__decision_ig.json").read_text())
        history=record['history'];points={min(t,len(history)) for t in [24,50,100,200,len(history)-1] if t>0}
        posteriors={q:QuadratureDecisionIG(world['public'],order=q) for q in [6,10,14]}
        counts=np.zeros(2*world['public']['d'],dtype=int)
        for t,event in enumerate(history):
            if t in points:
                scores={q:p.scores() for q,p in posteriors.items()}
                rows.append({'world_id':world['id'],'prefix':t,
                             'q6_max_gain':float(max(scores[6])),
                             'q6_absolute_tie_choice':choose(scores[6],counts,True),
                             'q6_relative_tie_choice':choose(scores[6],counts,False),
                             'q10_relative_tie_choice':choose(scores[10],counts,False),
                             'q14_relative_tie_choice':choose(scores[14],counts,False),
                             'q6_q14_max_abs_difference':float(max(abs(scores[6]-scores[14]))),
                             'q10_q14_max_abs_difference':float(max(abs(scores[10]-scores[14]))),
                             'scores':{str(q):s.tolist() for q,s in scores.items()}})
            for posterior in posteriors.values():posterior.observe(event['action'],event['answer'])
            counts[event['action']]+=1
    out={'status':'POSTHOC_NUMERICAL_DIAGNOSTIC_NOT_NEW_RESPONSE_EVALUATION',
         'prefixes':rows,'prefix_count':len(rows),
         'absolute_vs_relative_q6_choice_changes':sum(x['q6_absolute_tie_choice']!=x['q6_relative_tie_choice'] for x in rows),
         'q6_q14_relative_choice_changes':sum(x['q6_relative_tie_choice']!=x['q14_relative_tie_choice'] for x in rows),
         'q10_q14_relative_choice_changes':sum(x['q10_relative_tie_choice']!=x['q14_relative_tie_choice'] for x in rows),
         'new_environment_observations':0,'primary_frozen_results_changed':False}
    (HERE/'results/quadrature_replay_audit.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='prefixes'},indent=2))


if __name__=='__main__':main()
