"""Visualize proven bounds and the certified nonconvexity witness.

Curves are floating-point illustrations; the separate exact certificate supplies
all asserted inequalities. No optimizer, model calls or random worlds are used.
"""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from explore_calibration import law,kl,bern

ROOT=Path(__file__).resolve().parent
cert=json.loads((ROOT/'THRESHOLD_FAILURE_CERTIFICATE.json').read_text())
us=np.linspace(.5,.95,451)
truth=law(.8,.8,.6,5,0)
g=kl(truth,law(.8,us,us,5,0,True))
f=bern(.8,us)+bern(.6,np.minimum(.6,us))+1.61*g
fig,axes=plt.subplots(1,2,figsize=(10,3.8),constrained_layout=True)
axes[0].plot(us,f,label='Witness allocation information')
axes[0].axhline(1,color='black',ls='--',label='Required information = 1')
floor=1+float(cert['unknown_rate_known_z_oracle_upper']['minimum_uniform_information_margin_display'])
floor_display=np.floor(floor*10000)/10000
axes[0].axhline(floor,color='C2',ls=':',label=f'Certified global information > {floor_display:.4f}')
axes[0].set(xlabel='Alternative high extraction rate u',ylabel='Calibration + online KL',
            title='Oracle feasibility over the continuous domain')
axes[0].legend(fontsize=8)
axes[1].plot(us,g,label='Pure-good depth-5 truth-flip KL')
witness=np.array([.5,.6,.7])
values=kl(truth,law(.8,witness,witness,5,0,True))
axes[1].plot(witness,values,'o',color='C1',label='Certified Jensen witness points')
axes[1].plot([.5,.7],values[[0,2]],'--',color='gray',label='Endpoint chord')
axes[1].set(xlabel='Alternative high extraction rate u',ylabel='Online KL per block',
            title='The inner rate optimization can be nonconvex')
axes[1].legend(fontsize=8)
fig.suptitle('r = p = 0.8, q = 0.6; mathematical certificates, not empirical model results',fontsize=10)
fig.savefig(ROOT/'calibration_certificates.png',dpi=180)
fig.savefig(ROOT/'calibration_certificates.pdf')
plt.close(fig)
print('Wrote calibration_certificates.png and .pdf')
