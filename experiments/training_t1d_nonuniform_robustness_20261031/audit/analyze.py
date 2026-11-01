"""Frozen post-run analysis. No world generation, policy fitting, or outcome feedback."""
import functools
import hashlib
import json
import math
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from t1d import bootstrap
from t1d.strategies import POLICIES
from t1d.roster import roster
from t1d.integrity import verify, history_check
from t1b.belief import Belief

STRONG = ['KL-OriginalSolver', 'KL-AnalyticReuse', 'Fused-Info', 'Belief-Gated', 'WorstFact-MI']
NBOOT = 20000


def read(p): return json.loads(Path(p).read_text())
def lines(p):
    with Path(p).open() as f:
        for line in f:
            if line.strip(): yield json.loads(line)
def end(r): return r['estimation_history'][-1]
def key(r): return r['index'], r['budget'], r['policy']
def dump(name, obj): (ROOT/name).write_text(json.dumps(obj, indent=2, allow_nan=False)+'\n')
def stat(x):
    x = np.asarray(x, dtype=float)
    return {'n': len(x), 'sum': float(x.sum()), 'mean': float(x.mean()) if len(x) else None,
            'median': float(np.median(x)) if len(x) else None,
            'p95': float(np.quantile(x, .95)) if len(x) else None}
def confidences(p): return np.maximum(np.clip(p, 0, 1), 1-np.clip(p, 0, 1))
def entropy_bits(p):
    p = np.clip(np.asarray(p), 0, 1)
    return -(p*np.log2(np.maximum(p, 1e-300))+(1-p)*np.log2(np.maximum(1-p, 1e-300)))


class Analysis:
    def __init__(self, directory=None, engineering=False):
        self.engineering = engineering
        self.directory = Path(directory) if directory else ROOT/'artifacts'
        self.cfg = read(ROOT/'config.json')
        self.rows = list(lines(self.directory/'trajectories.jsonl'))
        self.by = {key(r): r for r in self.rows}
        self.worlds = ({r['index']: r for r in self.rows} if engineering else {j['index']: j for j in roster(self.cfg)})
        self.ids = tuple(sorted(self.worlds))
        self.labels = {}; self.traces = {}; self.metrics = {}
        self.checks = Counter(); self.errors = []

    def check(self, condition, label):
        self.checks[label] += 1
        if not condition and len(self.errors) < 100: self.errors.append(label)

    @functools.lru_cache(maxsize=100)
    def resamples(self, ids, sensitivity=False):
        groups = defaultdict(list)
        for j, i in enumerate(ids):
            r = self.worlds[i]
            g = r['cell'] if sensitivity else r['panel']
            groups[g].append(j)
        if not ids: return np.empty((NBOOT, 0), int)
        rng = np.random.default_rng(42032 if sensitivity else 42031)
        return np.concatenate([rng.choice(v, (NBOOT, len(v)), replace=True) for _, v in sorted(groups.items())], axis=1)

    def interval(self, x, ids, sensitivity=False):
        x = np.asarray(x, dtype=float); ids = tuple(ids)
        if not ids: return {'n': 0, 'mean': None, 'ci95': None, 'ci99': None}
        bs = x[self.resamples(ids, sensitivity)].mean(1)
        return {'n': len(ids), 'mean': float(x.mean()), 'ci95': np.quantile(bs, [.025, .975]).tolist(),
                'ci99': np.quantile(bs, [.005, .995]).tolist()}

    def available(self, B, arms, ids=None):
        return [i for i in (self.ids if ids is None else ids) if all((i, B, a) in self.by for a in arms)]

    def pair(self, B, a, b, ids=None):
        ids = self.available(B, [a, b], ids)
        av = np.array([self.by[i, B, a]['exact'] for i in ids], dtype=float)
        bv = np.array([self.by[i, B, b]['exact'] for i in ids], dtype=float)
        out = {'candidate': a, 'reference': b, 'budget': B, **self.interval(av-bv, ids),
               'cell_stratified_sensitivity': self.interval(av-bv, ids, True),
               'candidate_only': int(sum(av > bv)), 'reference_only': int(sum(av < bv)),
               'both_success': int(sum((av == 1) & (bv == 1))), 'both_failed': int(sum((av == 0) & (bv == 0))),
               'identical_action_sequences': sum([h['action'] for h in end(self.by[i,B,a])['action_history']] == [h['action'] for h in end(self.by[i,B,b])['action_history']] for i in ids),
               'world_outcomes': [{'index': i, 'candidate': bool(x), 'reference': bool(y)} for i, x, y in zip(ids, av, bv)]}
        for metric in ['joint_nll', 'joint_brier', 'fact_accuracy', 'type_queries', 'cpu', 'wall', 'task_hhi', 'worst_fact_uncertainty', 'starved_facts', 'redundant_confident_queries']:
            chosen = [i for i in ids if self.metrics[i,B,a].get(metric) is not None and self.metrics[i,B,b].get(metric) is not None]
            out[metric+'_difference'] = self.interval([self.metrics[i,B,a][metric]-self.metrics[i,B,b][metric] for i in chosen], chosen)
        if ids:
            x = np.array([self.metrics[i,B,a]['cpu'] for i in ids]); y = np.array([self.metrics[i,B,b]['cpu'] for i in ids])
            bs = self.resamples(tuple(ids))
            out['reference_over_candidate_CPU'] = {'ratio': float(y.sum()/x.sum()), 'ci95': np.quantile(y[bs].sum(1)/x[bs].sum(1), [.025,.975]).tolist()}
        return out

    def validate(self):
        self.check(len(self.rows) == len(self.by), 'unique_keys')
        expected = {(i,B,a) for i in self.ids for B in self.cfg['budgets'] for a in POLICIES}
        self.check(set(self.by) <= expected, 'only_planned_keys')
        for r in self.rows:
            d = sum(r['partition']); L = 2*d; e = end(r); B = r['budget']; hist = e['action_history']; c = np.asarray(r['counts'])
            self.check(c.shape == (d,2,2) and np.all(c >= 0), 'counts_shape_nonnegative')
            self.check(c.sum() == r['costs']['task'] and sum(map(len,r['type_answers'])) == r['costs']['type'], 'observation_cost_ledger')
            self.check(r['online'] == B == r['costs']['task']+r['costs']['type'], 'budget_fully_executed')
            self.check(r['costs']['offline'] == 2*r['M'] == 2*math.ceil(r['alpha']*r['R']), 'offline_fee')
            self.check(len(r['calibration']['high']) == r['M'] == len(r['calibration']['low']), 'calibration_size')
            self.check(r['total_acquisition'] == sum(r['costs'].values()), 'total_fee')
            self.check(len(hist) == B and [h['online_before'] for h in hist] == list(range(B)), 'action_history_coverage')
            forced = [t for t in range(B) if t-L*math.isqrt(t//L)**2 < L]
            self.check([h['online_before'] for h in hist if h['forced']] == forced, 'forced_schedule')
            self.check(all(hist[t]['action'] == t-L*math.isqrt(t//L)**2 for t in forced), 'forced_physical_actions')
            self.check(r['forced_tasks'] == len(forced), 'forced_ledger')
            self.check(all(0 <= h['action'] < L+len(r['partition']) for h in hist), 'legal_actions')
            if r['policy'] in ['Fresh-IG-Lite','IG-Uniform-Direct','WorstFact-MI','IG-Uniform-FixedType','IG-Fact-FixedType']:
                times = [h['online_before'] for h in hist if not h['forced']]
            elif r['policy'] in ['KL-Fresh','IG-Uniform-Fresh','IG-Fact-Fresh']:
                times = list(range(L,B))
            else:
                times = []; t = L
                while t < B:
                    times.append(t); t += math.ceil(math.sqrt(t+1))
            self.check([u['online'] for u in e['update_history']] == times, 'target_cadence')
            for u in e['update_history']:
                w = np.asarray(u['weights'])
                self.check(len(w) == L+len(r['partition']) and np.min(w) >= -1e-12 and abs(w.sum()-1) < 1e-10, 'normalized_weights')
                if r['policy'].startswith('IG-Uniform'):
                    j = 0
                    for size in r['partition']:
                        for m in [0,1]: self.check(np.ptp(w[[2*k+m for k in range(j,j+size)]]) < 1e-12, 'uniform_target_granularity')
                        j += size
            if r['policy'].startswith('IG-Uniform'):
                j = 0
                for size in r['partition']:
                    for m in [0,1]: self.check(np.ptp(c[j:j+size,m].sum(1)) <= 1, 'uniform_physical_balance')
                    j += size
            gate = r['strict_certificate']
            self.check(gate.get('total_observations') == r['total_acquisition'], 'certificate_all_observations')
            self.check(gate.get('task_counts') == c.sum(2).tolist() and gate.get('type_counts') == [len(x) for x in r['type_answers']], 'certificate_task_type_counts')
            self.check(r['complete'] == gate['certified'] and r['censored'] == (not r['complete']), 'certification_status')
            self.check(gate.get('candidate_theta') == r['fit']['theta'], 'gate_candidate')
            self.check(r['fit']['fixed_budget_completed'], 'terminal_budget_status')
            if r['policy'].endswith('FixedType'):
                self.check([(h['online_before'],h['action']) for h in hist if h['action']>=L] == [(2*L+g,L+g) for g in range(len(r['partition'])) if 2*L+g<B], 'matched_fixed_type_schedule')
            self.check(e['quadrature_order'] == 32 and r['fit']['theta'] == e['joint_theta_MAP'], 'common_decoder')
            self.check(len(e['joint_theta_distribution']) == 2**d and abs(sum(e['joint_theta_distribution'])-1) < 1e-10, 'terminal_posterior_normalization')
            if not self.engineering: self.check(r['isolation']['landlock_abi'] > 0 and r['isolation']['no_new_privileges'], 'worker_isolation')

        scoring = self.directory/'reproduction.jsonl' if self.engineering else self.directory/'private/reproduction.jsonl'
        potentials = {}; first_forced = {}; seen = set()
        for p in lines(scoring):
            k = p['job']['index'], p['job']['budget'], p['policy']; seen.add(k)
            if k not in self.by: self.check(False, 'scoring_without_terminal'); continue
            r = self.by[k]; d = sum(r['partition']); L = 2*d; truth = p['truth']; types = p['types']; e = end(r)
            old = self.labels.setdefault(r['index'], (truth, types))
            self.check(old == (truth,types), 'same_hidden_new_world')
            self.check(r['exact'] == (r['fit']['theta'] == truth), 'recovery_score')
            self.check(r['correct_facts'] == sum(x == y for x,y in zip(r['fit']['theta'],truth)), 'fact_score')
            ti = sum(int(bit) << (d-j-1) for j,bit in enumerate(truth)); probs = np.asarray(e['joint_theta_distribution'])
            self.check(abs(-math.log(max(probs[ti],1e-300))-r['posterior_quality_posthoc']['joint_nll']) < 1e-10, 'posthoc_NLL')
            self.check(abs(np.sum((probs-np.eye(2**d)[ti])**2)-r['posterior_quality_posthoc']['joint_brier']) < 1e-10, 'posthoc_Brier')
            physical = []; offsets = Counter(); reconstructed = np.zeros((d,2,2),int); reports = [[] for _ in types]; hh = hashlib.sha256()
            for ev in p['trace_prefix']:
                hh.update(json.dumps(ev,sort_keys=True,separators=(',',':')).encode()+b'\n')
                if ev['action'] == 'query':
                    a = 2*ev['args']['j']+'AB'.index(ev['args']['format']); y = ev['result']['answer']; reconstructed[a//2,a%2,y] += 1
                elif ev['action'] == 'ask_type':
                    a = L+ev['args']['group']; y = 'AB'.index(ev['result']['format']); reports[a-L].append(y)
                else: continue
                pk = r['index'], a, offsets[a]
                if pk in potentials: self.check(potentials[pk] == y, 'shared_potential_stream')
                potentials[pk] = y; offsets[a] += 1; physical.append((a,y))
            self.check(hh.hexdigest() == r['transcript_sha256'] == p['full_trace_sha256'], 'independent_trace_hash')
            self.check(np.array_equal(reconstructed,r['counts']) and reports == r['type_answers'], 'trace_count_reconstruction')
            self.check([a for a,y in physical] == [h['action'] for h in e['action_history']], 'trace_action_reconstruction')
            prefix = physical[:2*L]
            prefix = prefix[:min(len(prefix),2*L)]
            initial = first_forced.setdefault(r['index'], physical[:min(r['budget'],2*L)])
            self.check(initial[:min(len(initial),2*L)] == physical[:min(len(initial),2*L)], 'same_initial_forced_responses')
            self.traces[k] = physical
        self.check(seen == set(self.by), 'scoring_coverage')
        for i in self.ids:
            rr = [r for (j,B,a),r in self.by.items() if j == i]
            if rr: self.check(len({json.dumps(r['calibration'],sort_keys=True) for r in rr}) == 1, 'common_calibration')
            for a in POLICIES:
                # Only the frozen belief controller explicitly depends on the deadline.
                if a == 'Belief-Gated': continue
                for b1,b2 in [(16,32),(32,48),(48,64)]:
                    if (i,b1,a) in self.traces and (i,b2,a) in self.traces:
                        self.check(self.traces[i,b1,a] == self.traces[i,b2,a][:b1], 'budget_agnostic_prefix_consistency')
        return {'passed': not self.errors, 'errors': self.errors, 'checks': dict(self.checks),
                'planned_paths': len(expected), 'finished_paths': len(self.rows), 'uncompleted_planned_paths': len(expected-set(self.by)),
                'wrong_certificates': sum(r['complete'] and not r['exact'] for r in self.rows),
                'certificates': sum(r['complete'] for r in self.rows),
                'strict_confidence_censored': sum(r['censored'] for r in self.rows),
                'certificate_statuses': dict(Counter(r['strict_certificate']['status'] for r in self.rows)),
                'infrastructure_failures': len(list(lines(self.directory/'failures.jsonl'))),
                'old_public_preservation': history_check() if not self.engineering else 'engineering_fixture'}

    def extract_metrics(self):
        # A descriptive, separately timed B32 replay. No query or policy feedback.
        cache = {}; replay_start = time.process_time(); replay_states = 0
        for r in self.rows:
            k = key(r); e = end(r); d = sum(r['partition']); L = 2*d
            counts = np.asarray(r['counts']); nt = counts.sum((1,2)); conf = confidences(e['theta_prob']); hb = entropy_bits(e['theta_prob'])
            hist = e['action_history']; free = [h for h in hist if not h['forced']]; nfree = np.zeros(d,int)
            for h in free:
                if h['action'] < L: nfree[h['action']//2] += 1
            weights = nt/max(1,nt.sum()); freeweights = nfree/max(1,nfree.sum()); worst = int(np.argmax(hb))
            starved = int(sum((conf < .8) & (nfree == 0))) if free else 0
            over = bool(nfree.sum() and max(freeweights) >= .5 and any(conf[j] < .8 for j in range(d) if j != int(np.argmax(nfree))))
            truth = self.labels[r['index']][0]
            m = {'exact': float(r['exact']), 'fact_accuracy': r['correct_facts']/d,
                 'marginal_MAP_fact_accuracy': sum((np.asarray(e['theta_prob']) > .5) == truth)/d,
                 'task_queries': r['costs']['task'], 'type_queries': r['costs']['type'], 'offline': r['costs']['offline'],
                 'online': r['online'], 'total_acquisition': r['total_acquisition'],
                 'joint_nll': r['posterior_quality_posthoc']['joint_nll'], 'joint_brier': r['posterior_quality_posthoc']['joint_brier'],
                 'p_mae': abs(e['p_error']), 'q_mae': abs(e['q_error']), 'cpu': r['trajectory_cpu_seconds'], 'wall': r['trajectory_wall_seconds'],
                 'posterior_cpu': e['component_cpu'].get('posterior',0), 'target_cpu': e['component_cpu'].get('target',0),
                 'controller_cpu': e['component_cpu'].get('controller',0), 'terminal_belief_cpu': e['terminal_belief_cpu'],
                 'certification_cpu': r['gate_cpu_seconds'], 'task_hhi': float(weights@weights),
                 'free_task_hhi': float(freeweights@freeweights) if nfree.sum() else 0.,
                 'maximum_free_task_share': float(max(freeweights)), 'worst_fact_uncertainty': float(max(hb)),
                 'mean_fact_uncertainty': float(np.mean(hb)), 'starved_facts': starved, 'overexploration_flag': int(over),
                 'redundant_confident_queries': None, 'discretionary_task_queries': int(nfree.sum())}
            groups = []; start = 0
            for g,size in enumerate(r['partition']):
                js = list(range(start,start+size)); groups.append({'size':size, 'task':int(sum(nt[js])), 'type':len(r['type_answers'][g]),
                    'exact':all(r['fit']['theta'][j] == truth[j] for j in js), 'correct_facts':sum(r['fit']['theta'][j] == truth[j] for j in js)})
                start += size
            # Replay all arms at the sole primary budget. Shared sufficient states are cached.
            redundant = 0; measured = 0
            if r['budget'] == 32:
                c = np.zeros_like(counts); reports = [[] for _ in r['partition']]; groups_index = []; start = 0
                for size in r['partition']: groups_index.append(list(range(start,start+size))); start += size
                for t,(a,y) in enumerate(self.traces[k]):
                    if not hist[t]['forced'] and a < L:
                        ck = (r['index'], tuple(c.ravel()), tuple((len(x),sum(x)) for x in reports))
                        if ck not in cache:
                            belief = Belief.from_observation(c,groups_index,r['calibration'],reports,[r['s']]*len(reports),r['eta'])
                            cache[ck] = confidences(belief.summary()['theta_prob']).tolist(); replay_states += 1
                        redundant += cache[ck][a//2] >= .95; measured += 1
                    if a < L: c[a//2,a%2,y] += 1
                    else: reports[a-L].append(y)
                m['redundant_confident_queries'] = int(redundant)
            self.metrics[k] = {**m, 'per_fact_task_queries': nt.tolist(), 'per_fact_free_task_queries': nfree.tolist(),
                               'joint_MAP_per_fact_correct': [x==y for x,y in zip(r['fit']['theta'],truth)],
                               'marginal_MAP_per_fact_correct': ((np.asarray(e['theta_prob'])>.5)==truth).tolist(),
                               'terminal_fact_confidence': conf.tolist(), 'terminal_fact_entropy_bits': hb.tolist(),
                               'worst_fact_index': worst, 'groups': groups,
                               'redundancy_replay_task_queries': measured}
        self.replay = {'unique_recomputed_states': replay_states, 'CPU_seconds': time.process_time()-replay_start,
                       'scope': 'B32 nonforced task observations only, fresh order32 observation-only posterior; diagnostic never returned to sampler; >=.95 confidence is a proxy, not proof of a wasted query'}

    def arm(self,B,a,ids=None):
        ids = self.available(B,[a],ids); rr = [self.by[i,B,a] for i in ids]
        out = {'n':len(ids), 'exact':sum(r['exact'] for r in rr), 'recovery':self.interval([float(r['exact']) for r in rr],ids)}
        if ids:
            for name,value in self.metrics[ids[0],B,a].items():
                if name == 'exact': continue
                if isinstance(value,(float,int)) or value is None:
                    out[name] = stat([self.metrics[i,B,a][name] for i in ids if self.metrics[i,B,a][name] is not None])
        return out

    def run(self, write=True):
        started = time.monotonic(); cpu = time.process_time()
        validation = self.validate(); self.extract_metrics()
        pairs = [('Fresh-IG-Lite',a) for a in POLICIES if a != 'Fresh-IG-Lite']
        pairs += [('IG-Fact-Fresh','IG-Uniform-Fresh'), ('IG-Fact-Block','IG-Uniform-Block'),
                  ('IG-Fact-Fresh','IG-Fact-Block'), ('IG-Uniform-Fresh','IG-Uniform-Block'),
                  ('KL-Fresh','KL-AnalyticReuse'), ('KL-AnalyticReuse','KL-OriginalSolver'),
                  ('IG-Fact-Block','Fused-Info'), ('IG-Uniform-Direct','IG-Uniform-Fresh')]
        pairs += [('IG-Fact-FixedType','IG-Uniform-FixedType')]
        paired = {B:{a+' minus '+b:self.pair(B,a,b) for a,b in pairs} for B in self.cfg['budgets']}
        summaries = {B:{a:self.arm(B,a) for a in POLICIES} for B in self.cfg['budgets']}
        strata = {}
        dimensions = {
            'panel':lambda j:j['panel'], 'partition':lambda j:tuple(j['partition']),
            'rate':lambda j:(j['p'],j['q']), 'gap':lambda j:round(j['p']-j['q'],5), 'alpha':lambda j:j['alpha']}
        for label,f in dimensions.items():
            strata[label] = {}
            for value in sorted(set(f(j) for j in self.worlds.values()),key=str):
                ids = [i for i in self.ids if f(self.worlds[i]) == value]
                strata[label][str(value)] = {B:{'arms':{a:self.arm(B,a,ids) for a in POLICIES},
                    'Lite_minus_uniform':self.pair(B,'Fresh-IG-Lite','IG-Uniform-Direct',ids),
                    'Lite_minus_controller':self.pair(B,'Fresh-IG-Lite','Belief-Gated',ids)} for B in self.cfg['budgets']}
        factor = {}
        for B in self.cfg['budgets']:
            arms = ['IG-Uniform-Block','IG-Fact-Block','IG-Uniform-Fresh','IG-Fact-Fresh']; ids=self.available(B,arms)
            ub,nb,uf,nf = [np.array([self.by[i,B,a]['exact'] for i in ids],float) for a in arms]
            factor[B] = {n:self.interval(x,ids) for n,x in {'nonuniform_block':nb-ub,'nonuniform_fresh':nf-uf,
                'nonuniform_main':.5*(nb-ub+nf-uf),'refresh_uniform':uf-ub,'refresh_fact':nf-nb,
                'refresh_main':.5*(uf-ub+nf-nb),'interaction':(nf-nb)-(uf-ub)}.items()}
        full = validation['passed'] and validation['uncompleted_planned_paths']==0 and validation['infrastructure_failures']==0
        main = paired[32]['Fresh-IG-Lite minus IG-Uniform-Direct']
        pooled_ood = [i for i in self.ids if self.worlds[i]['panel'] != 'ID']
        id_ids = [i for i in self.ids if self.worlds[i]['panel'] == 'ID']
        def nonnegative(z):return z['n'] > 0 and z['mean'] >= 0
        reproducible = (full and main['mean'] >= .03 and main['ci95'][0] > 0
                        and paired[32]['IG-Fact-Fresh minus IG-Uniform-Fresh']['mean'] >= 0
                        and all(nonnegative(self.pair(32,'Fresh-IG-Lite','IG-Uniform-Direct',ids)) for ids in [id_ids,pooled_ood])
                        and all(nonnegative(paired[B]['Fresh-IG-Lite minus IG-Uniform-Direct']) for B in [48,64]))
        A = 'GO' if reproducible else ('NO-GO' if full and main['mean'] <= 0 else 'REVISE')
        beats_all = full and all(paired[32]['Fresh-IG-Lite minus '+a]['ci99'][0] > 0 for a in STRONG)
        practical = full and all(paired[32]['Fresh-IG-Lite minus '+a]['mean'] >= 0 and paired[32]['Fresh-IG-Lite minus '+a]['ci99'][0] >= -.03 for a in STRONG)
        C = full and all(nonnegative(paired[B]['Fresh-IG-Lite minus IG-Uniform-Direct']) for B in [16,48,64]) and all(
            nonnegative(strata['panel'][panel][32]['Lite_minus_uniform']) for panel in [p['name'] for p in self.cfg['panels']])
        # Robustness also reports every partition harm; no threshold/arm search.
        harm = {part:z[32]['Lite_minus_uniform'] for part,z in strata['partition'].items() if z[32]['Lite_minus_uniform']['n'] and z[32]['Lite_minus_uniform']['mean'] < -.10}
        if harm:C=False
        decision = {'A_nonuniform_reproducibility':A,
                    'A_fixed_type_isolated_task_granularity':'GO' if full and paired[32]['IG-Fact-FixedType minus IG-Uniform-FixedType']['ci95'][0]>0 else 'NOT_ESTABLISHED',
                    'B_strict_recovery_superiority_over_all_strong_baselines':'GO' if beats_all else 'NOT_ESTABLISHED',
                    'B_practical_baseline_engineering_gate':'GO' if practical else 'REVISE',
                    'C_cross_budget_and_heldout_directional_robustness':'GO' if C else 'REVISE',
                    'C_partition_harms_over_10pp':harm,
                    'D_independent_algorithmic_novelty_beyond_standard_greedy_IG':'NO-GO_UNESTABLISHED_BY_DESIGN',
                    'E_start_RL':'NO-GO_ADDED_VALUE_UNESTABLISHED',
                    'overall':'REVISE_EMPIRICAL_BASELINE_POSITIONING' if A!='NO-GO' else 'NO-GO_PRIMARY_METHOD_CLAIM',
                    'stop_after_this_development':True, 'confirmation_execute_authorized':False}
        result = {'scope':'bounded development, not independent confirmation', 'worlds_planned':len(self.ids),
            'summaries':summaries,'factorial':factor,'decisions':decision,'strong_reference_family':STRONG,
            'all_paths_complete_valid':full,'main_nonuniform_pair':main,
            'ID_nonuniform_pair':self.pair(32,'Fresh-IG-Lite','IG-Uniform-Direct',id_ids),
            'OOD_nonuniform_pair':self.pair(32,'Fresh-IG-Lite','IG-Uniform-Direct',pooled_ood),
            'fixed_type_nonuniform_pair':paired[32]['IG-Fact-FixedType minus IG-Uniform-FixedType'],
            'diagnostic_replay':self.replay,'analysis_CPU':time.process_time()-cpu,'analysis_wall':time.monotonic()-started}
        self.stratified = strata
        ex = (read(ROOT/'artifacts/execution.json') if not self.engineering else {'status':'engineering','seconds':0,'evaluator_cpu_seconds':0,'costs_including_partial':{},'frozen_files_preserved':False})
        startup = {}
        for rr in self.rows: startup.setdefault(rr['policy'],rr.get('isolation',{}).get('worker_startup_cpu',0))
        self.runtime = {'scientific_execution':ex,'worker_CPU_total':sum(rr['trajectory_cpu_seconds'] for rr in self.rows),
            'worker_warmup_CPU':startup,'analysis_CPU':result['analysis_CPU'],'analysis_wall':result['analysis_wall'],
            'scope':'per-arm full worker trajectory includes task/type handling, estimator, planner and terminal gate; parent aggregate CPU and pre-timer imports cannot be attributed to arms; offline replay excluded from policy cost'}
        if write:
            dump('VALIDATION.json',validation);dump('RESULTS.json',result);dump('PAIRED_OUTCOMES.json',paired)
            dump('STRATIFIED_RESULTS.json',strata)
            dump('MECHANISM_DIAGNOSTICS.json',{'rows':[{'index':i,'budget':B,'policy':a,**m} for (i,B,a),m in self.metrics.items()], 'replay':self.replay})
            dump('RUNTIME.json',self.runtime)
        return result,validation,paired


if __name__ == '__main__':
    before=verify(); result,validation,_=Analysis().run(); assert verify()==before
    print(json.dumps({'decisions':result['decisions'],'validation':validation['passed'],
                      'B32_exact':{a:z['exact'] for a,z in result['summaries'][32].items()}}))
    if not validation['passed']:raise SystemExit(1)
