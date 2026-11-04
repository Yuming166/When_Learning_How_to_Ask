"""Plot information coefficients, not model responses or observed accuracies."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
results=json.loads((ROOT/'numerical_results.json').read_text())
cases={x['name']:x for x in results['coefficient_cases']}
names=['majority3_shared','majority3_singletons','near_boundary_together','near_boundary_split']
labels=['3 votes\n(2,1)','3 votes\n(1,1,1)',
        '3/5 support\none group','3/5 support\nsplit groups']
ratios=[cases[n]['unknown']['numerically_repaired_upper_cost']/cases[n]['analytic_oracle']['oracle_cost'] for n in names]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,
                     'axes.spines.right':False,'axes.spines.top':False,'pdf.fonttype':42})
fig,(ax,bx)=plt.subplots(1,2,figsize=(7.4,3.0),layout='constrained')
fig.suptitle(r'$p=.8,q=.6$; theoretical information coefficients',fontsize=9)
bars=ax.bar(range(4),ratios,color=['#398589','#d27a36','#398589','#d27a36'],width=.67)
ax.axhline(1,ls='--',lw=.8,color='#333333')
ax.set(xticks=range(4),xticklabels=labels,ylim=(0,1.85),
       ylabel='Cost / type-only oracle cost',title=r'Group structure at $\alpha=0$')
ax.tick_params(axis='x',labelsize=7.6)
for bar,ratio in zip(bars,ratios):
    ax.text(bar.get_x()+bar.get_width()/2,ratio+.035,f'{ratio:.3f}',ha='center',fontsize=8)
curve=results['OR_calibration_curve']; alphas=[r['alpha'] for r in curve]
learner=[r['decision_cost'] for r in curve]; oracle=[r['oracle_cost'] for r in curve]
bx.plot(alphas,learner,'o-',color='#3b70ad',lw=1.5,ms=3,label='Unknown format')
bx.plot(alphas,oracle,'s-',color='#398589',lw=1.5,ms=3,label='Type-only oracle')
bx.fill_between(alphas,oracle,learner,color='#3b70ad',alpha=.10)
bx.set(xlabel=r'Calibration ratio per stream $\alpha$',ylabel='Online-cost coefficient',
       title='Positive OR with finite calibration',xlim=(0,8))
bx.legend(frameon=False,fontsize=8)
fig.savefig(ROOT/'decision_boundary.pdf',metadata={'CreationDate':None,'ModDate':None})
fig.savefig(ROOT/'decision_boundary.png',dpi=200)
plt.close(fig)
print('Wrote decision_boundary.pdf and decision_boundary.png; theoretical coefficient illustrations only.')
