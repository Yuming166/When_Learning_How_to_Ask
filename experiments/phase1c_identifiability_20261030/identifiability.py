"""Exact rational experiments; no Monte Carlo and no model calls."""
import itertools
import json
import math
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def joint(formats, p, q, good="A", prior=F(1, 2), persistent=False):
    out = {}
    for ys in itertools.product([-1, 1], repeat=len(formats)):
        value = F(0)
        for theta, weight in [(1, prior), (-1, 1-prior)]:
            prob = weight
            if persistent:
                for m in set(formats):
                    observed = [y for y, f in zip(ys, formats) if f == m]
                    if len(set(observed)) != 1:
                        prob = F(0); break
                    r = p if m == good else q
                    prob *= r if observed[0] == theta else 1-r
            else:
                for y, m in zip(ys, formats):
                    r = p if m == good else q
                    prob *= r if y == theta else 1-r
            value += prob
        out[ys] = value
    assert sum(out.values()) == 1
    return out


def tv(a, b):
    return sum(abs(a[k]-b[k]) for k in a) / 2


def agreement(r):
    return r*r+(1-r)*(1-r)


def repeat_choice_accuracy(p, q, k):
    ca, cb = agreement(p), agreement(q)
    result = F(0)
    for a, b in itertools.product(range(k+1), repeat=2):
        mass = math.comb(k, a)*ca**a*(1-ca)**(k-a)*math.comb(k, b)*cb**b*(1-cb)**(k-b)
        result += mass*(1 if a > b else F(1, 2) if a == b else 0)
    return result


def main():
    rows = []
    for p, q in [(F(3,4), F(1,2)), (F(3,4), F(3,5)), (F(9,10),F(7,10)), (F(3,5),F(51,100))]:
        one = tv(joint("AB",p,q), joint("AB",p,q,good="B"))
        repeated = tv(joint("AABB",p,q), joint("AABB",p,q,good="B"))
        frozen = tv(joint("AABB",p,q,persistent=True),joint("AABB",p,q,good="B",persistent=True))
        assert one == frozen == 0 and repeated > 0
        assert agreement(p)-agreement(q) == 2*(p-q)*(p+q-1) > 0
        rows.append({"p":str(p),"q":str(q),"one_each_tv":str(one),"two_each_iid_tv":str(repeated),
                     "two_each_iid_known_rate_bayes_accuracy":str((1+repeated)/2),"two_each_persistent_tv":str(frozen),
                     "repeat_consistency_gap":str(agreement(p)-agreement(q)),
                     "repeat_and_compare_accuracy_by_k":{str(k):{"exact":str(repeat_choice_accuracy(p,q,k)),
                                                                "float":float(repeat_choice_accuracy(p,q,k))} for k in [1,2,4,6,8,16,32]}})
    p,q=F(3,4),F(3,5)
    assert tv(joint("AB",p,q,prior=F(3,4)),joint("AB",p,q,good="B",prior=F(3,4)))>0
    # Shared theta across two items converts across-item observations into repeats.
    correlated = tv(joint("ABAB",p,q),joint("ABAB",p,q,good="B"))
    assert correlated > 0
    below = tv(joint("AABB",F(4,5),F(1,5)),joint("AABB",F(4,5),F(1,5),good="B"))
    assert below == 0
    # With two repeats each, known rates, uniform independent theta per item,
    # the per-item likelihood ratio depends only on the two agreement indicators.
    da,db=joint("AABB",p,q),joint("AABB",p,q,good="B")
    ratios={}
    for ys in da:
        key=(ys[0]==ys[1],ys[2]==ys[3])
        ratios.setdefault(key,set()).add(da[ys]/db[ys])
    assert all(len(v)==1 for v in ratios.values())
    result={"arithmetic":"fractions.Fraction exact enumeration","cases":rows,
            "nonuniform_prior_single_pair_identifiable":True,"shared_theta_across_items_single_each_tv":str(correlated),
            "below_chance_p_4_5_q_1_5_swapped_type_tv":str(below),
            "two_each_known_rates_agreement_statistic_sufficient_for_z":True,
            "scope":"Uniform independent theta prior gives a Bayes impossibility with one A/B each; fixed-sign theory itself assumes no random prior. Known-rate Bayes accuracy is a reference, not an unknown-rate policy guarantee."}
    (ROOT/'identifiability_exact.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
