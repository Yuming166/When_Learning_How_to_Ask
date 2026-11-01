import unittest,time
import numpy as np
from t1b import bootstrap
from t1b.belief import Belief,index,stable_argmax
from t1b.controller import Residual,candidate_indices,forced_index
from phase2e.estimator import posterior,information_scores
from phase2e.exact import exact_posterior
from phase2a.coefficients import warmup_lp

PUBLIC={'d':4,'groups':[{'targets':[0]},{'targets':[1,2,3]}],'rate_domain':{'eta':.05,'levels_unknown':True},'type_accuracy':[.8,.8]}
CAL={'high':[],'low':[]}
def fixture():
    obj=Residual(PUBLIC,CAL,16,'Lookahead-2',32)
    for n,y in enumerate([1,0,1,1,0,0,1,0,1,1,0,1,0,1,1,0]):
        a=obj.next(set(range(4)));obj.observe(a,{'answer':y})
    return obj

class Contract(unittest.TestCase):
 @classmethod
 def setUpClass(cls):warmup_lp()
 def test_prior_predictive_symmetry(self):
    b=Belief.from_observation(np.zeros((4,2,2),int),[[0],[1,2,3]],CAL,[[],[]],[.8,.8],.05)
    np.testing.assert_allclose(b.first().sum(axis=0),.5,atol=1e-14)
    self.assertAlmostEqual(b.theta_mass.sum(),1)
 def test_predictive_condition_matches_recompute(self):
    o=fixture();b=o.root_belief()
    for a in [0,5,8,9]:
      for y in [0,1]:
        c=o.counts.copy();types=[t[:] for t in o.types]
        if a<8:c[a//2,a%2,y]+=1
        else:types[a-8].append(y)
        direct=Belief.from_observation(c,o.groups,CAL,types,o.type_accuracy,o.eta)
        prob,child=b.condition(a,y)
        np.testing.assert_allclose(child.w,direct.w,atol=5e-16,rtol=1e-12)
 def test_two_observation_moments(self):
    b=fixture().root_belief();f=b.first();M=b.second();mass=b.theta_mass
    for a,c in [(0,8),(8,8),(3,4)]:
      for y in [0,1]:
        p,child=b.condition(a,y)
        for z in [0,1]:
          q,leaf=child.condition(c,z)
          if y and z:joint=M[:,a,c]
          elif y:joint=f[:,a]-M[:,a,c]
          elif z:joint=f[:,c]-M[:,a,c]
          else:joint=mass-f[:,a]-f[:,c]+M[:,a,c]
          np.testing.assert_allclose(joint,p*q*leaf.theta_mass,atol=2e-15)
 def test_info_matches_frozen(self):
    o=fixture();fit=posterior(o.counts,o.groups,CAL,o.types,o.type_accuracy,o.eta)
    b=Belief(fit,o.groups,o.type_accuracy,o.eta)
    np.testing.assert_allclose(b.ig(),np.exp(information_scores(fit,o.groups,o.type_accuracy)),atol=3e-14)
 def test_joint_map_vs_exact_small(self):
    counts=np.zeros((2,2,2),int);counts[0,0,1]=2;counts[1,1,0]=1
    groups=[[0],[1]];types=[[0],[1,1]];cal={'high':[1,0],'low':[1,0]};acc=[.8,.8]
    b=Belief.from_observation(counts,groups,cal,types,acc,.05)
    exact=exact_posterior(counts.tolist(),groups,cal,types,acc)
    marginal={theta:sum(p for (th,z),p in exact['joint'].items() if th==theta) for theta in set(k[0] for k in exact['joint'])}
    np.testing.assert_allclose(b.theta_mass,[float(marginal[tuple(th)]) for th in b.k['theta']],atol=2e-12)
 def test_two_step_dp_bruteforce(self):
    o=fixture();base=o.next(set(range(4)));self.assertTrue(o.decisions)
    d=o.decisions[-1];self.assertGreaterEqual(d['nonmyopic_model_gain'],-1e-12)
    # Separately enumerate nested normalized posterior branches; compare Q2.
    b=o.root_belief();choices=d['candidate_actions'];expected=[]
    for a in choices:
      v=0.;actual=o._actual_counts().copy();actual[a]+=1
      for y in [0,1]:
        p,child=b.condition(a,y);kl=o.forecast_kl(child,o.t+1,actual,o.cumulative)
        f=forced_index(o.t+1,o.L);cc=[f] if f is not None else candidate_indices(child,kl,o.d)
        best=0.
        for c in cc:
          zval=0.
          for z in [0,1]:
            q,leaf=child.condition(c,z);zval+=q*max(leaf.theta_mass)
          best=max(best,zval)
        v+=p*best
      expected.append(v)
    np.testing.assert_allclose(d['q2'],expected,atol=2e-13)
 def test_one_step_final_budget(self):
    o=fixture();o.budget=17;o.next(set(range(4)))
    self.assertNotIn('q2',o.decisions[-1]);self.assertEqual(o.decisions[-1]['remaining_budget'],1)
 def test_original_forcing_and_ledger(self):
    o=fixture();self.assertEqual(o.forced.sum(),16)
    a=o.next(set(range(4)));self.assertEqual(tuple(a),o._pending)
    o.observe(a,{'format':'A'} if a[0]=='type' else {'answer':1})
    self.assertEqual(o.counts.sum()+sum(map(len,o.types)),17)
 def test_no_truth_inputs(self):
    with self.assertRaises(TypeError):Belief.from_observation(np.zeros((4,2,2)),[[0],[1,2,3]],CAL,[[],[]],[.8,.8],.05,true_p=.85)
if __name__=='__main__':unittest.main()
