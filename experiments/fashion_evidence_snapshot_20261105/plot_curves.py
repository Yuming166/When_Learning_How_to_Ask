"""Descriptive full-budget curves from released paired outcome summaries."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
D=json.loads((HERE/'results/RECOMPUTED.json').read_text())
PANELS=[('small_python','Small Python'),('development_python','Development Python'),('validation_python','Validation Python'),('test_python','Test Python'),('luna8','Luna 8: repeated answer banks'),('luna48','Luna 48: reused development profiles')]
METHODS=[('fixed_order','Fixed order'),('profile_ig','Profile-IG'),('decision_set_ig','Decision-set IG'),('decision_value','Decision Value')]
fig,axes=plt.subplots(2,3,figsize=(11,6.4),sharex=True,sharey=True,layout='constrained')
for ax,(key,title) in zip(axes.flat,PANELS):
 d=D[key]
 for method,label in METHODS:
  ax.plot(range(7),[100*d['curves'][method][str(b)]['accuracy'] for b in range(7)],marker='o',markersize=3,label=label)
 n=d['curves']['decision_value']['5']['n']
 ax.set_title(f'{title}\n{d["unique_profiles"]} profiles, {n} evaluated cases',fontsize=10)
 ax.axvline(5,color='gray',alpha=.25,linestyle=':');ax.grid(alpha=.18)
 ax.set_xticks(range(7));ax.set_ylim(0,103)
for ax in axes[-1]:ax.set_xlabel('Structured disclosures')
for ax in axes[:,0]:ax.set_ylabel('Acceptable-decision accuracy (%)')
handles,labels=axes.flat[0].get_legend_handles_labels()
fig.legend(handles,labels,loc='outside lower center',ncol=4,frameon=False)
fig.suptitle('Real product menus; synthetic preferences in every panel\nDescriptive means; repeated cases and reused profiles are not independent users',fontsize=12)
fig.savefig(HERE/'results/full_budget_curves.pdf')
fig.savefig(HERE/'results/full_budget_curves.png',dpi=170)
