"""Post-confirmation question-budget comparison; original task and methods fixed.

Run with Python 3 and NumPy. No language-model calls. Results retain every
menu and budget, and reproduce the existing four-question primary result.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
from itertools import combinations, product
import json, hashlib, time
import numpy as np
import ranking_search as source
from richer_preferences import Belief

ROOT = Path(__file__).resolve().parent
OUT = ROOT / '三四五题比较'
METHODS = ['Fixed order', 'Profile information gain',
           'Decision-set information gain', 'One-step decision value']
BUDGETS = [3, 4, 5]


def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


class BudgetBelief(Belief):
    def __init__(self, p, limit=5):
        self.d = len(p)
        self.p = np.asarray(p)
        self.bits = np.array(list(product((0, 1), repeat=self.d)))
        self.base = 3 ** np.arange(self.d - 1, -1, -1)
        self.codes, self.masks, self.prob = [], [], []
        for n in range(limit + 1):
            codes, masks, probabilities = [], [], []
            for subset in combinations(range(self.d), n):
                for values in product((0, 1), repeat=n):
                    codes.append(sum((v + 1) * self.base[j] for j, v in zip(subset, values)))
                    masks.append(sum(1 << j for j in subset))
                    probabilities.append(np.prod([p[j] if v else 1 - p[j]
                                                  for j, v in zip(subset, values)]))
            self.codes.append(np.array(codes))
            self.masks.append(np.array(masks))
            self.prob.append(np.array(probabilities))
        self.children, self.unasked = [], []
        for n in range(limit):
            lookup = {code: i for i, code in enumerate(self.codes[n + 1])}
            children = np.zeros((len(self.codes[n]), self.d, 2), dtype=int)
            unknown = (self.masks[n][:, None] & (1 << np.arange(self.d))) == 0
            for i, code in enumerate(self.codes[n]):
                for j in np.flatnonzero(unknown[i]):
                    children[i, j] = [lookup[code + self.base[j]], lookup[code + 2 * self.base[j]]]
            self.children.append(children)
            self.unasked.append(unknown)


def evaluate(model, accept):
    posterior = model.marginals(accept)
    value = [a.max(axis=1) for a in posterior]
    signatures = accept @ (1 << np.arange(accept.shape[1]))
    groups = model.marginals(signatures[:, None] == np.unique(signatures))
    entropy = [-(a * np.log(np.maximum(a, 1e-300))).sum(axis=1) for a in groups]
    profile_entropy = -(model.p * np.log(model.p) + (1 - model.p) * np.log(1 - model.p))
    mass = np.prod(np.where(model.bits, model.p, 1 - model.p), axis=1)
    states = np.zeros((4, len(model.bits)), dtype=int)
    rates = {}
    for n in range(5):
        policy = np.array([
            np.full(len(model.codes[n]), n),
            model.choose(np.broadcast_to(profile_entropy, (len(model.codes[n]), model.d)), n),
            model.choose(-model.expect(entropy[n + 1], n), n),
            model.choose(model.expect(value[n + 1], n), n),
        ])
        question = policy[np.arange(4)[:, None], states]
        reply = model.bits[np.arange(len(model.bits))[None, :], question]
        states = model.children[n][states, question, reply]
        if n + 1 in BUDGETS:
            decisions = posterior[n + 1].argmax(axis=1)[states]
            correct = accept[np.arange(len(accept))[None, :], decisions]
            rates[n + 1] = (correct @ mass).tolist()
            # Conditional success and actual weighted profile outcomes agree.
            assert np.allclose(value[n + 1][states] @ mass, rates[n + 1], atol=1e-12)
    assert np.all(np.diff(np.array(list(rates.values())), axis=0) >= -1e-12)
    return rates


def direct_check(model, accept, budget, method):
    """Independent subset-conditioning recursion, without ternary-state arrays."""
    bits = model.bits
    prior = np.prod(np.where(bits, model.p, 1 - model.p), axis=1)
    sig = accept @ (1 << np.arange(accept.shape[1]))
    _, group = np.unique(sig, return_inverse=True)

    def entropy(p):
        p = p[p > 0]
        return -float(p @ np.log(p))

    def recurse(mask, used):
        total = prior[mask].sum()
        if len(used) == budget:
            return float((prior[mask] @ accept[mask]).max())
        scores = np.full(model.d, -np.inf)
        for j in range(model.d):
            if j in used:
                continue
            value = 0.0
            for y in (0, 1):
                child = mask & (bits[:, j] == y)
                child_mass = prior[child].sum()
                w = prior[child] / child_mass
                if method == 1:
                    v = -entropy(w)
                elif method == 2:
                    v = -entropy(np.bincount(group[child], weights=w))
                else:
                    v = float((w @ accept[child]).max())
                value += child_mass / total * v
            scores[j] = value
        q = len(used) if method == 0 else int(np.flatnonzero(scores >= scores.max() - 1e-12)[0])
        return sum(recurse(mask & (bits[:, q] == y), used + (q,)) for y in (0, 1))
    return recurse(np.ones(len(bits), dtype=bool), ())


def run():
    OUT.mkdir(exist_ok=True)
    plan_path = source.OUT / '排序确认设计.json'
    plan = json.loads(plan_path.read_text(encoding='utf-8'))
    primary = next(c for c in plan['cases'] if c['name'] == 'primary')
    protocol = dict(budgets=BUDGETS, methods=METHODS, case=primary,
                    source_design_sha256=hashlib.sha256(plan_path.read_bytes()).hexdigest(),
                    script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    scope='Post-confirmation budget sensitivity on the same 576 menus; no retuning, new users, or LLM calls.',
                    intervals='5000 paired menu bootstrap draws within the three original seeds; 98.333333% marginal intervals for DV minus decision-set IG at each of three budgets (Bonferroni).',
                    bootstrap_seed=20261105531)
    protocol_path = OUT / 'protocol.json'
    if protocol_path.exists():
        assert json.loads(protocol_path.read_text(encoding='utf-8')) == protocol
    else:
        write('protocol.json', protocol)
    data = {r['product_id']: r for r in source.source_rows()}
    model = BudgetBelief(primary['config']['prior'])
    original_text = (source.OUT / '排序确认结果.json').read_text(encoding='utf-8')
    pos = original_text.index('[', original_text.index('"results"')) + 1
    while original_text[pos].isspace():
        pos += 1
    original = json.JSONDecoder().raw_decode(original_text, pos)[0]
    assert original['name'] == 'primary'
    del original_text
    original_map = {(r['seed'], tuple(r['items'])): r for r in original['menus']}
    records, check_errors = [], []
    max_reproduction_error = 0.0
    start = time.monotonic()
    for i, menu in enumerate(primary['menus']):
        accept = source.signatures(*source.components([data[x] for x in menu['items']], primary['labels'], model), primary['config'])
        rates = evaluate(model, accept)
        old = original_map[(menu['seed'], tuple(menu['items']))]
        error = float(np.max(np.abs(np.array(rates[4]) - old['rates'][:4])))
        max_reproduction_error = max(max_reproduction_error, error)
        assert error < 1e-10
        if i in (0, 192, 384):
            for budget in BUDGETS:
                for method in range(4):
                    exact = direct_check(model, accept, budget, method)
                    err = abs(exact - rates[budget][method])
                    assert err < 1e-10
                    check_errors.append(err)
        records.append(dict(**menu, rates=rates))
        if (i + 1) % 96 == 0:
            print(f'{i + 1}/576 menus; {time.monotonic() - start:.1f}s', flush=True)
    a = np.array([[r['rates'][b] for b in BUDGETS] for r in records])
    gaps = 100 * (a[:, :, 3] - a[:, :, 2])
    rng = np.random.default_rng(protocol['bootstrap_seed'])
    seeds = sorted({r['seed'] for r in records})
    groups = [np.array([i for i, r in enumerate(records) if r['seed'] == seed]) for seed in seeds]
    bootstrap = []
    for _ in range(50):
        indices = np.hstack([rng.choice(g, size=(100, len(g)), replace=True) for g in groups])
        bootstrap.extend(gaps[indices].mean(axis=1))
    ci = np.percentile(bootstrap, [100 / 120, 100 - 100 / 120], axis=0).T
    result = dict(methods=METHODS, budgets=BUDGETS,
                  accuracy_percent=(100 * a.mean(axis=0)).tolist(),
                  dv_minus_set_ig_pp=gaps.mean(axis=0).tolist(),
                  simultaneous_three_budget_intervals=ci.tolist(),
                  per_seed={str(seed): (100 * a[g].mean(axis=0)).tolist() for seed, g in zip(seeds, groups)},
                  original_four_question_max_abs_error=max_reproduction_error,
                  independent_check_max_abs_error=max(check_errors),
                  protocol_sha256=hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
                  menus=records)
    write('results.json', result)
    print(json.dumps({k:v for k,v in result.items() if k != 'menus'}, indent=2), flush=True)


if __name__ == '__main__':
    run()
