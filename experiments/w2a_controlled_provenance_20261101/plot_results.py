"""Standalone scientific figures from frozen results and labelled analytic curves."""
import csv
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from engine import repeat_risk,fresh_risk

ROOT=Path(__file__).resolve().parent


def main():
    costs=json.loads((ROOT/'cost_grid.json').read_text())
    confidence=json.loads((ROOT/'confidence_diagnostic.json').read_text())
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,
                         'savefig.bbox':'tight','pdf.fonttype':42})
    fig,ax=plt.subplots(2,2,figsize=(11.4,8.0),constrained_layout=True)
    n=np.arange(1,32)
    rep=[repeat_risk(int(k),.75,.8) for k in n]
    fresh=[fresh_risk(int(k),.75,.8) for k in n]
    ax[0,0].plot(n,rep,color='#2266aa',lw=2,label='One root: reread or copies')
    ax[0,0].plot(n,fresh,color='#15945f',lw=2,label='One read per independent root')
    ax[0,0].axhline(.25,color='#2266aa',ls=':',label='Same-root floor: 1-r')
    ax[0,0].axhline(.35,color='#9a5e28',ls='--',label='Persistent reading error control')
    ax[0,0].set(title='A. Equal reads; known r=.75, a=.80',xlabel='Number of reads',ylabel='Bayes error',ylim=(0,.39))
    ax[0,0].legend(fontsize=8)
    ratio=np.linspace(0,1,601)
    repeatcost=[repeat_risk(math.floor(4-c+1e-12),.75,.8) for c in ratio]
    freshcost=[fresh_risk(math.floor(4/(1+c)+1e-12),.75,.8) for c in ratio]
    ax[0,1].plot(ratio,repeatcost,label='Repeat one root',color='#2266aa',lw=2)
    ax[0,1].plot(ratio,freshcost,label='Fresh roots',color='#15945f',lw=2)
    ax[0,1].axvline(1/3,color='0.4',ls=':',label='c / read cost = 1/3')
    ax[0,1].set(title='B. Two specified policies; B=4, read cost=1',xlabel='Root activation cost / read cost',ylabel='Bayes error',ylim=(.26,.37))
    ax[0,1].legend(fontsize=8)
    center=[r for r in costs if r['r']==.75 and r['a']==.8 and r['root_cost']==1]
    budgets=[r['budget'] for r in center]
    for key,label,color in [('repeat_risk','Repeat','#2266aa'),('fresh_risk','Fresh','#15945f'),
                             ('best_static_risk','Best arbitrary static depths','#ba8134'),('DP_risk','Finite-horizon optimal adaptive','#a43573')]:
        ax[1,0].plot(budgets,[r[key] for r in center],marker='o',label=label,color=color,lw=1.8)
    ax[1,0].set(title='C. Common cost cap; known r=.75, a=.80, c=1',xlabel='Hard budget',ylabel='Bayes error',xticks=budgets)
    ax[1,0].legend(fontsize=8)
    k=[r['reads'] for r in confidence]
    ax[1,1].plot(k,[r['correct_all_positive_confidence'] for r in confidence],label='Correct same-root posterior',color='#2266aa',lw=2)
    ax[1,1].plot(k,[r['naive_all_positive_confidence'] for r in confidence],label='Wrong URL-iid posterior',color='#bd3f31',lw=2)
    ax[1,1].axhline(.95,color='0.4',ls=':',label='Claimed confidence target .95')
    ax[1,1].axhline(.75,color='#2266aa',ls=':')
    ax[1,1].set(title='D. Conditioning on all-positive observations',xlabel='Number of same-root reads',ylabel='Posterior confidence',ylim=(.6,1.015))
    ax[1,1].legend(fontsize=8)
    for fmt in ['png','pdf']:fig.savefig(ROOT/f'mechanism_summary.{fmt}',dpi=180)
    plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(10.5,3.2),constrained_layout=True)
    rs=[.6,.75,.9];aa=[.6,.8,.95]
    vmax=max(r['DP_gain_over_best_static'] for r in costs)
    for axis,c in zip(axes,[0,1,3]):
        matrix=np.array([[next(v['DP_gain_over_best_static'] for v in costs if v['r']==r and v['a']==a and v['root_cost']==c and v['budget']==12) for a in aa] for r in rs])
        im=axis.imshow(matrix,cmap='Blues',vmin=0,vmax=vmax)
        for iy in range(3):
            for ix in range(3):axis.text(ix,iy,f'{matrix[iy,ix]:.4f}',ha='center',va='center',fontsize=9)
        axis.set(xticks=range(3),xticklabels=aa,yticks=range(3),yticklabels=rs,xlabel='Reading reliability a',ylabel='Root reliability r',title=f'Root cost c={c}, budget=12')
    fig.colorbar(im,ax=axes,label='Best-static error minus optimal-adaptive error',shrink=.8)
    for fmt in ['png','pdf']:fig.savefig(ROOT/f'adaptive_gain_grid.{fmt}',dpi=180)
    plt.close(fig)
    with (ROOT/'analytic_curve_values.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['curve','x','repeat_risk','fresh_risk'])
        for k,risk,new in zip(n,rep,fresh):writer.writerow(['equal_reads_analytic_extension',int(k),risk,new])
        for c,risk,new in zip(ratio,repeatcost,freshcost):writer.writerow(['cost_flip_analytic_illustration',c,risk,new])
    print('Wrote 2 scientific figure pairs and labelled analytic-curve values; no sampled or model data.')


if __name__=='__main__':main()
