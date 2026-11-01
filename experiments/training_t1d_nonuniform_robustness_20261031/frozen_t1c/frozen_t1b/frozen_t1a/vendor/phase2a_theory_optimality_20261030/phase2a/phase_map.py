"""Theoretical coefficient calculations only; no trajectory observations."""
import json
from pathlib import Path
import numpy as np
from .coefficients import solve_allocation,oracle_coefficient,gamma,critical_alpha

ROOT=Path(__file__).resolve().parents[1]
PARTITIONS=[[1,15],[2,14],[4,12],[8,8],[16]]
ALPHAS=[0,1,2,3,5,10]


def main():
    out=ROOT/'artifacts/theory';out.mkdir(parents=True,exist_ok=True);rows=[]
    for alpha in ALPHAS:
        oracle=oracle_coefficient(16,.85,.6,alpha)
        for part in PARTITIONS:
            gam=gamma(16,min(part),.85,.6,alpha)
            for types in [False,True]:
                result=solve_allocation(part,.85,.6,alpha,.8 if types else None)
                row={**result,'oracle_K':oracle['K'],'Gamma_min':gam,
                     'predicted_zero_premium':gam>=1-1e-10,'numerical_premium':result['K']-oracle['K'],
                     'action_class':'task_and_type_s.8' if types else 'task_only'}
                rows.append(row)
    crossing=critical_alpha(16,8,.85,.6)
    report={'d':16,'p':.85,'q':.6,'alphas':ALPHAS,'critical_alpha_k8':crossing,'rows':rows,
        'scope':'Theoretical joint continuous-rate coefficient program, numerically checked; no empirical asymptotic observation.'}
    (out/'phase_map.json').write_text(json.dumps(report,indent=2)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(12,4.5))
    grid=np.linspace(0,10,101)
    for k in [1,2,4,8,16]:axes[0].plot(grid,[gamma(16,k,.85,.6,float(a)) for a in grid],label=f'k_min={k}')
    axes[0].axhline(1,color='black',linestyle=':');axes[0].axvline(crossing,color='gray',linestyle='--')
    axes[0].set_xlabel('Offline observations per stream / log(1/delta)');axes[0].set_ylabel('Gamma');axes[0].legend(fontsize=8)
    axes[0].set_title('Analytic phase indicator; d=16, p=.85, q=.60')
    for part in PARTITIONS:
        subset=[r for r in rows if r['partition']==part and r['action_class']=='task_and_type_s.8']
        axes[1].plot(ALPHAS,[r['numerical_premium'] for r in subset],'o-',label=str(part))
    axes[1].set_xlabel('alpha');axes[1].set_ylabel('K - K_oracle (online coefficient)');axes[1].legend(fontsize=8)
    axes[1].set_title('Joint program with finite-s type actions')
    fig.tight_layout();fig.savefig(out/'phase_map.png',dpi=180);fig.savefig(out/'phase_map.pdf');plt.close(fig)
    lines=['# Theoretical coefficient phase map','',f'critical alpha for [8,8]: {crossing:.10f}.', '',
        '|Partition|alpha|Gamma|K (task only)|K (tasks + types s=.8)|K_oracle|','|---|---:|---:|---:|---:|---:|']
    for part in PARTITIONS:
        for alpha in ALPHAS:
            rr=[r for r in rows if r['partition']==part and r['alpha']==alpha]
            a=next(r for r in rr if r['action_class']=='task_only');b=next(r for r in rr if r['action_class']!='task_only')
            lines.append(f"|{part}|{alpha}|{a['Gamma_min']:.8f}|{a['K']:.8f}|{b['K']:.8f}|{a['oracle_K']:.8f}|")
    lines+=['','These are numerical coefficient calculations. Gamma shortcuts were not used in the K solver. The zero boundary is a leading ONLINE-cost statement; total acquisition separately adds 2M. No finite-budget discontinuity or asymptotic empirical convergence is asserted. Independent small-instance optimizer and alternative enumeration evidence is in audit/COEFFICIENT_REVIEW.md.']
    (ROOT/'THEORY_PHASE_MAP.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'critical_alpha':crossing,'solves':len(rows),'maximum_relative_gap':max(r['relative_gap'] for r in rows)}))


if __name__=='__main__':main()
