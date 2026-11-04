"""Standalone theory figures from the bounded numerical receipt."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parent
r=json.loads((ROOT/'results.json').read_text())
cases={x['name']:x for x in r['continuous_cases']}
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(1,2,figsize=(7.6,3.05),layout='constrained')
ax=axes[0]; x=np.arange(2); width=.33
names=['three_shared','three_split']
for offset,key,label,color in [(-width/2,'oracle_formula','Type-only oracle','#838b98'),
                              (width/2,'numerically_repaired_upper_cost','Unknown format','#2874ad')]:
    values=[cases[n][key] for n in names]
    bars=ax.bar(x+offset,values,width,color=color,label=label)
    ax.bar_label(bars,fmt='%.2f',padding=3,fontsize=8)
ax.set(xticks=x,xticklabels=['One group','Two groups'],ylabel='Leading online cost',
       ylim=(0,11),title='Three-item catalogue')
ax.legend(loc='upper left',frameon=False,fontsize=8)
ax.set_xlabel(r'$p=.8,\ q=.6,\ \alpha=0$',labelpad=12,fontsize=8)

ax=axes[1]
curve=r['phase_curve_k7']; p=np.array([x['p'] for x in curve]); y=[x['psi_over_B'] for x in curve]
cross=.734893622116569
ax.axvspan(.5,cross,color='#e1f0e2',zorder=0)
ax.axvspan(cross,1,color='#f9e7dd',zorder=0)
ax.plot(p,y,color='#2874ad',lw=2)
ax.axhline(.5,color='#555',ls='--',lw=1)
ax.axvline(cross,color='#555',ls=':',lw=1)
ax.text(.61,.585,'Zero premium',ha='center',fontsize=8)
ax.text(.865,.585,'Positive premium',ha='center',fontsize=8)
ax.set(xlim=(.5,1),ylim=(.475,.602),xlabel='Better-format reliability p',
       ylabel=r'$\psi_p(1/7)/B_p$',title='Fixed-catalogue transition')
ax.text(.98,.03,r'$0.73489<p_*<0.73490$',transform=ax.transAxes,ha='right',fontsize=8)
for suffix in ['pdf','png']:
    fig.savefig(ROOT/f'general_catalogue_boundary.{suffix}',dpi=220)
plt.close(fig)
