"""Fully public condition grid; entropy is created only by the sealed runner."""
import math


def roster(cfg):
    result = []; cell = 0
    for panel in cfg['panels']:
        for part in panel['partitions']:
            for p, q in panel['rates']:
                for alpha in panel['alphas']:
                    for rep in range(panel['replicates']):
                        result.append({'panel': panel['name'], 'cell': cell, 'partition': part,
                            'p': p, 'q': q, 'alpha': alpha, 'R': cfg['planning_R'], 's': cfg['type_accuracy'],
                            'eta': cfg['eta'], 'M': math.ceil(alpha*cfg['planning_R']),
                            'index': cfg['development_index_start']+100*cell+rep, 'replicate': rep,
                            'stop_mode': 'terminal_certification_only', 'channel': 'iid',
                            'protocol': 'fixed_budget', 'scenario': 't1d_nonuniform_robustness_no_training'})
                    cell += 1
    # Interleave replicate/panel/cell rather than finish one panel before the others.
    return sorted(result, key=lambda j: (j['replicate'], j['panel'], j['cell']))


def jobs(cfg):
    result = []
    for k, world in enumerate(roster(cfg)):
        budgets = cfg['budgets']; order = budgets[k % len(budgets):]+budgets[:k % len(budgets)]
        for B in order:
            result.append({**world, 'budget': B, 'online_cap': B, 'check_every': B, 'milestones': [B]})
    return result
