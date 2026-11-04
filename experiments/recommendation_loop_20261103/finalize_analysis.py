"""Post-hoc synthesis; preserve primary and repair results without new samples."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
ORDER = ('round_robin', 'joint_dr_rc', 'decision_ig_relative_repair',
         'profile_kl', 'decision_kl')
LABELS = ('Round-Robin', 'Joint D-RRC', 'Decision IG\n(repaired)',
          'Profile KL', 'Decision KL')


def load_records():
    config = json.loads((HERE / 'config.json').read_text())
    worlds = json.loads((HERE / 'artifacts/pilot/worlds.json').read_text())
    records = {}
    for world in worlds:
        for arm in config['arms']:
            records[world['id'], arm] = json.loads(
                (HERE / 'artifacts/pilot' / f"{world['id']}__{arm}.json").read_text())
        records[world['id'], ORDER[2]] = json.loads(
            (HERE / 'artifacts/ig_repair' / f"{world['id']}.json").read_text())
    return config, worlds, records


def main():
    config, worlds, records = load_records()
    cost = lambda r: r['queries'] if r['status'] == 'CERTIFIED' else config['max_queries']
    metrics = {}
    for arm in (*ORDER, 'decision_ig'):
        rows = [records[w['id'], arm] for w in worlds]
        metrics[arm] = {
            'attempted': len(rows),
            'certified': sum(r['status'] == 'CERTIFIED' for r in rows),
            'capped': sum(r['status'] == 'CAPPED_UNCERTIFIED' for r in rows),
            'failed': sum(r['status'].startswith('FAILED') for r in rows),
            'wrong_certified': sum(r.get('certified_correct') is False for r in rows),
            'postprocessing_failures': sum(r.get('postprocessing_failure') is not None for r in rows),
            'mean_restricted_queries': float(np.mean([cost(r) for r in rows])),
            'mean_policy_cpu_seconds': float(np.mean([r['policy_cpu_seconds'] for r in rows])),
            'mean_gate_cpu_seconds': float(np.mean([r['gate_cpu_seconds'] for r in rows])),
            'mean_total_cpu_seconds': float(np.mean([r['cpu_seconds'] for r in rows])),
        }
    comparisons = {}
    for arm in ORDER[:-1]:
        deltas = [cost(records[w['id'], arm]) - cost(records[w['id'], 'decision_kl']) for w in worlds]
        baseline = metrics[arm]['mean_restricted_queries']
        comparisons[arm] = {
            'method_lower_cost': sum(d > 0 for d in deltas),
            'ties': sum(d == 0 for d in deltas),
            'method_higher_cost': sum(d < 0 for d in deltas),
            'baseline_minus_method_by_world': deltas,
            'mean_queries_saved_by_method': float(np.mean(deltas)),
            'descriptive_percent_saved_by_method': 100 * float(np.mean(deltas)) / baseline,
        }
    strata = {}
    for catalogue in config['catalogues']:
        subset = [w for w in worlds if w['catalogue_name'] == catalogue['name']]
        strata[catalogue['name']] = {
            arm: float(np.mean([cost(records[w['id'], arm]) for w in subset])) for arm in ORDER
        }
    target = HERE / 'results'
    result = {
        'stage': 'DEVELOPMENT_WITH_SEPARATE_POSTHOC_BASELINE_REPAIR_NOT_CONFIRMATION',
        'technical_loop': 'GO_IN_CONTROLLED_CHANNEL',
        'KL_superiority_over_strongest_baseline': 'NOT_ESTABLISHED',
        'metrics': metrics, 'comparisons': comparisons, 'catalogue_strata': strata,
        'world_order': [w['id'] for w in worlds],
        'primary_trajectories': 40, 'repair_trajectories': 8,
        'primary_observations': sum(r['queries'] for (w, arm), r in records.items() if arm != ORDER[2]),
        'repair_observations': sum(r['queries'] for (w, arm), r in records.items() if arm == ORDER[2]),
        'profile_clusters': len({w['profile_cluster'] for w in worlds}),
        'anchor_worlds': sum(w['profile_kind'] == 'anchor_all_positive' for w in worlds),
        'uncertainty': 'Descriptive only; no significance test, population CI or equivalence claim.',
        'timing_scope': 'Host-specific CPU logs, including initialization; no isolated benchmarking.',
        'input_sha256': {
            name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
            for name in ['FREEZE.json', 'REPAIR_FREEZE.json', 'results/analysis.json',
                         'results/ig_repair.json']
        },
    }
    (target / 'final_comparison.json').write_text(json.dumps(result, indent=2) + '\n')
    lines = [
        '# Final development comparison, including baseline repair', '',
        'Primary: 40 trajectories on eight worlds. Repair: eight additional trajectories on the SAME worlds.',
        'Four constructed profile clusters; half the worlds are theory anchors. No confirmation sample.', '',
        '| Arm | Certified | Capped / failed / wrong certified | Mean queries | Policy CPU seconds | Total CPU seconds |',
        '|---|---:|---:|---:|---:|---:|',
    ]
    for arm in ORDER:
        m = metrics[arm]
        lines.append(f"| {arm} | {m['certified']}/{m['attempted']} | {m['capped']} / {m['failed']} / {m['wrong_certified']} | "
                     f"{m['mean_restricted_queries']:.3f} | {m['mean_policy_cpu_seconds']:.4f} | {m['mean_total_cpu_seconds']:.4f} |")
    lines += ['', 'All paths certified, so restricted query cost equals observed stopping time in this table.',
              'The original IG mean was 397.875; its absolute tie threshold was numerically unsuitable.',
              'Only its tie rule was repaired; the original records and all Decision KL results remain unchanged.', '',
              '| World | RR | Joint D-RRC | IG original | IG repaired | Profile KL | Decision KL |',
              '|---|---:|---:|---:|---:|---:|---:|']
    for w in worlds:
        arms = ('round_robin', 'joint_dr_rc', 'decision_ig', ORDER[2], 'profile_kl', 'decision_kl')
        lines.append('| ' + w['id'] + ' | ' + ' | '.join(str(records[w['id'], a]['queries']) for a in arms) + ' |')
    lines += ['', 'Decision KL vs repaired IG: 2 lower-cost / 0 tied / 6 higher-cost worlds;',
              'mean cost 243 vs 237.5, i.e. Decision KL uses 2.32% more queries descriptively.',
              'Both catalogue strata also have a higher Decision KL mean than repaired IG.',
              'No universal ranking, real-user validity, asymptotic efficiency or empirical risk guarantee is established.']
    (target / 'FINAL_COMPARISON.md').write_text('\n'.join(lines) + '\n')

    plt.rcParams.update({'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.5), layout='constrained')
    colors = ['#a5a5a5', '#a5a5a5', '#cf8a32', '#a5a5a5', '#2874ad']
    queries = [metrics[a]['mean_restricted_queries'] for a in ORDER]
    bars = axes[0].bar(LABELS, queries, color=colors)
    axes[0].bar_label(bars, labels=[f'{v:.1f}' for v in queries], padding=3, fontsize=8)
    axes[0].set(ylabel='Mean queries to certificate', ylim=(0, 620),
                title='Eight development worlds; all 8/8 certified')
    times = [metrics[a]['mean_total_cpu_seconds'] for a in ORDER]
    bars = axes[1].bar(LABELS, times, color=colors)
    axes[1].bar_label(bars, labels=[f'{v:.2f}' for v in times], padding=3, fontsize=8)
    axes[1].set(ylabel='Mean total CPU seconds', ylim=(0, 1.95),
                title='Includes allocation, inference and stopping')
    for ax in axes:
        ax.tick_params(axis='x', labelrotation=23)
    fig.supxlabel('Controlled iid model; post-hoc IG repair on reused worlds; no independent confirmation', fontsize=8)
    for suffix in ('png', 'pdf'):
        fig.savefig(target / f'cost_comparison_repaired.{suffix}', dpi=220)
    plt.close(fig)
    print(json.dumps({'technical_loop': result['technical_loop'],
                      'KL_superiority': result['KL_superiority_over_strongest_baseline'],
                      'query_means': {a: metrics[a]['mean_restricted_queries'] for a in ORDER}}, indent=2))


if __name__ == '__main__':
    main()
