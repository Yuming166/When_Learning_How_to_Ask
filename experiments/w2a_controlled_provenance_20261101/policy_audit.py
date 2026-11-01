"""Freeze and evaluate the small ordered-state witness policy without reoptimization."""
from collections import defaultdict
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent


def weights(state,r,a):
    pos=neg=F(1,2)
    for s,f in state:
        x=a**s*(1-a)**f;y=(1-a)**s*a**f
        pos*=r*x+(1-r)*y;neg*=(1-r)*x+r*y
    return pos,neg


def encode(x):return {'fraction':str(x),'float':float(x)}


def evaluate(policy,r=F(3,4),a=F(4,5),c=F(1)):
    table={(tuple(map(tuple,n['ordered_root_counts'])),n['remaining']):n for n in policy['nodes']}
    occupancy=defaultdict(F);occupancy[((),8)]=F(1)
    risk=spent=reads=roots=terminal_mass=F(0)
    for (state,remaining),node in sorted(table.items(),key=lambda x:-x[0][1]):
        mass=occupancy[(state,remaining)]
        if not mass:continue
        wp,wm=weights(state,r,a);denom=wp+wm
        if node['action']=='STOP':
            wp0,wm0=weights(state,F(3,4),F(4,5))
            conditional_error=wm/denom if wp0>wm0 else wp/denom if wm0>wp0 else F(1,2)
            nr=len(state);nt=sum(sum(pair) for pair in state)
            assert nr*c+nt<=8
            risk+=mass*conditional_error;spent+=mass*(nr*c+nt)
            reads+=mass*nt;roots+=mass*nr;terminal_mass+=mass
        else:
            ix=node['root_index'];cost=node['action_cost']
            for answer in (0,1):
                nxt=list(state)
                if node['action']=='NEW_ROOT':nxt.append((answer,1-answer))
                else:
                    s,f=nxt[ix];nxt[ix]=(s+answer,f+1-answer)
                nxt=tuple(nxt);prob=sum(weights(nxt,r,a))/denom
                occupancy[(nxt,remaining-cost)]+=mass*prob
    assert terminal_mass==1
    return {'risk':encode(risk),'expected_cost':encode(spent),'expected_reads':encode(reads),
            'expected_roots':encode(roots),'terminal_probability':encode(terminal_mass)}


def main():
    source=ROOT/'INDEPENDENT_EXPECTATIONS.json';data=json.loads(source.read_text())
    witness=data['frozen_grid_witness_checked_after_parent_result']
    nodes=witness['reachable_optimal_policy']
    policy={'kind':'FROZEN_OBSERVATION_ADAPTED_POLICY','r_center':'3/4','a_center':'4/5',
            'nominal_activation_cost':1,'budget':8,'root_indexing':'creation order',
            'terminal_decoder':'center-parameter Bayes sign, fair tie; held fixed under perturbation',
            'nodes':nodes,'source_receipt_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
    (ROOT/'center_policy.json').write_text(json.dumps(policy,indent=2)+'\n')
    central=evaluate(policy);assert F(central['risk']['fraction'])==F(24899,100000)
    eps=F(1,4000);margin=F(243,25000)-16*eps
    corners=[]
    for r,a,c in itertools.product([F(3,4)-eps,F(3,4)+eps],[F(4,5)-eps,F(4,5)+eps],[F(4,5),F(1)]):
        row=evaluate(policy,r,a,c)
        assert abs(F(row['risk']['fraction'])-F(24899,100000))<=8*eps
        corners.append({'r':str(r),'a':str(a),'c':str(c),**row})
    result={'central':central,'reachable_policy_states':len(nodes),'perturbation_epsilon':str(eps),
            'analytic_region_margin_lower_bound':encode(margin),'corner_frozen_policy_checks':corners,
            'corner_checks_are_not_region_proof':True,'policy_reoptimized_on_corners':False}
    (ROOT/'POLICY_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'central':central,'states':len(nodes),'region_margin':encode(margin)},indent=2))


if __name__=='__main__':main()
