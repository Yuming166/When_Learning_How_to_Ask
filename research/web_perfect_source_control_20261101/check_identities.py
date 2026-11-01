"""Deterministic rational checks of the analytic perfect-source control.

These finite checks are implementation/algebra diagnostics, not a substitute for
the universal proof in PERFECT_SOURCE_THEOREM.md. No optimization or simulation.
"""
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
import importlib.util
from itertools import product
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
HELPER = ROOT.parent/'web_unknown_calibration_20261031/certify_threshold_failure.py'
spec = importlib.util.spec_from_file_location('sealed_count_law', HELPER)
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)


@lru_cache(maxsize=None)
def observed(eA, eB, a, b, theta):
    return tuple(old.law(F(1), eA, eB, a, b, negative=theta == -1))


def mean(e, theta):
    return e if theta == 1 else 1-e


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def run():
    true_rates = [(F(3,4), F(1,2)), (F(19,20), F(3,5)),
                  (F(39,40), F(3,5)), (F(3,5), F(599,1000))]
    alternative_rates = [(F(1,2), F(1,2)), (F(39,40), F(39,40)),
                         (F(19,20), F(3,5)), (F(3,4), F(1,2)),
                         (F(3,5), F(599,1000))]
    law_checks = outcome_checks = 0
    for (p,q), (u,v), th, th2, z, z2 in product(
            true_rates, alternative_rates, [-1,1], [-1,1], [0,1], [0,1]):
        eA,eB = (p,q) if z == 0 else (q,p)
        fA,fB = (u,v) if z2 == 0 else (v,u)
        sA,sB,tA,tB = mean(eA,th),mean(eB,th),mean(fA,th2),mean(fB,th2)
        for L in range(1,7):
            for a in range(L+1):
                b=L-a
                P,Q=observed(eA,eB,a,b,th),observed(fA,fB,a,b,th2)
                assert sum(P)==sum(Q)==1 and min(P)>0 and min(Q)>0
                E_A=E_B=F(0)
                for idx,(i,j) in enumerate(product(range(a+1),range(b+1))):
                    # Pointwise likelihood factorization, using the prior full
                    # source-mixture implementation independently of the proof.
                    expected=(sA/tA)**i*((1-sA)/(1-tA))**(a-i)
                    expected*=(sB/tB)**j*((1-sB)/(1-tB))**(b-j)
                    assert P[idx]/Q[idx] == expected
                    E_A+=P[idx]*i
                    E_B+=P[idx]*j
                    outcome_checks+=1
                # These are exactly the coefficients of the four log terms;
                # hence the KL identity needs no floating-point logarithms.
                assert E_A==a*sA and a-E_A==a*(1-sA)
                assert E_B==b*sB and b-E_B==b*(1-sB)
                law_checks+=1

    repacking_checks=cost_checks=0
    for N in [1,2,3,6]:
        all_actions=[(j,a,L-a) for j in range(3)
                     for L in range(1,N+1) for a in range(L+1)]
        for kind in ['all_depths','only_cap','sparse']:
            x={}
            for j,a,b in all_actions:
                if kind=='only_cap' and a+b!=N:continue
                if kind=='sparse' and (a,b)!=(1,0):continue
                x[j,a,b]=F((j+1)*(a+2*b+1),a+b+2)
            totals={(j,m):F(0) for j in range(3) for m in [0,1]}
            for (j,a,b),w in x.items():
                totals[j,0]+=a*w
                totals[j,1]+=b*w
            packed={(j,N,0):totals[j,0]/N for j in range(3)}
            packed.update({(j,0,N):totals[j,1]/N for j in range(3)})
            for j in range(3):
                assert sum(a*w for (jj,a,b),w in packed.items() if jj==j)==totals[j,0]
                assert sum(b*w for (jj,a,b),w in packed.items() if jj==j)==totals[j,1]
            repacking_checks+=1
            for c,ell in product([F(0),F(1,2),F(1),F(3)],[F(1,3),F(1),F(2)]):
                before=sum((c+ell*(a+b))*w for (j,a,b),w in x.items())
                after=sum((c+ell*(a+b))*w for (j,a,b),w in packed.items())
                slack=c*sum((1-F(a+b,N))*w for (j,a,b),w in x.items())
                assert before-after==slack>=0
                assert after==(ell+c/N)*sum(totals.values())
                short_mass=sum(w for (j,a,b),w in x.items() if a+b<N)
                assert (before>after)==(c>0 and short_mass>0)
                cost_checks+=1

    # Reuse the already sealed imperfect-source certificate, without rerunning
    # or altering its producer. This is provenance verification, not new data.
    depth_path=ROOT.parent/'web_oracle_structure_20261031/DEPTH_MIXING_CERTIFICATE.json'
    depth=json.loads(depth_path.read_text())
    assert depth['status']=='PASS_EXACT_RATIONAL_CONTINUOUS_DOMAIN_CERTIFICATE'
    assert depth['known_rate_comparison']['unique_best_action']==[1,0]
    assert F(depth['witness']['cost'])==34
    assert F(depth['single_depth']['universal_lower_bound'])==F(413,10)>34
    assert depth['parameters']['r']=='3/5' and depth['parameters']['L_max']==6
    result=dict(status='PASS_EXACT_RATIONAL_ALGEBRA_CHECKS', date='2026-11-01',
        law_cases=law_checks, count_outcomes=outcome_checks,
        repacking_allocations=repacking_checks, cost_identities=cost_checks,
        true_rate_fixtures=[[str(a),str(b)] for a,b in true_rates],
        alternative_rate_fixtures=[[str(a),str(b)] for a,b in alternative_rates],
        labels_checked='all 16 true/alternative truth and format combinations',
        depth_caps_checked=[1,2,3,6],
        checks=['observed-count likelihood ratio factorization',
                'exact expected log-term coefficients for additive KL',
                'per-fact per-format read totals after repacking',
                'exact cost identity and strictness, including c=0 and N=1'],
        mechanism=dict(perfect_sources_unknown_rates='depth 6 by analytic theorem',
            imperfect_sources_known_rates='unique depth 1 by sealed certificate',
            imperfect_sources_unknown_rates='every optimum mixes depths by sealed certificate'),
        source_sha256=sha(Path(__file__)),
        dependencies={str(HELPER.relative_to(REPO)):sha(HELPER),
                      str(depth_path.relative_to(REPO)):sha(depth_path)},
        limits=['Finite algebra diagnostics do not replace the general analytic proof.',
                'No finite-delta batching equivalence is tested or claimed.',
                'No new stochastic worlds, model calls, or optimizations.'])
    (ROOT/'IDENTITY_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','law_cases','count_outcomes',
                                          'repacking_allocations','cost_identities']},indent=2))


if __name__=='__main__':
    run()
