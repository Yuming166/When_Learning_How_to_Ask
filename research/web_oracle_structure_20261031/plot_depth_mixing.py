"""Scientific illustration; only the labelled certificate bounds are proofs."""
from pathlib import Path
import importlib.util
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('discovery',ROOT/'discover_structure.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
certificate=json.loads((ROOT/'DEPTH_MIXING_CERTIFICATE.json').read_text())
u=np.linspace(.5,.975,1501)
r,p,q=.6,.95,.6
cal=m.bern(p,u)+m.bern(q,np.minimum(q,u))
one=m.kl(m.law(r,p,q,1,0),m.law(r,u,u,1,0,True))
two=m.kl(m.law(r,p,q,2,0),m.law(r,u,u,2,0,True))
fig,ax=plt.subplots(1,2,figsize=(10.8,4.1),layout='constrained')
ax[0].plot(u,cal+14*one+2*two,label='14 depth-1 + 2 depth-2 blocks',color='#175f8a',lw=2)
ax[0].plot(u,cal+17*one,label='All depth 1, same cost 34',color='#b9691b',ls='--')
ax[0].plot(u,cal+(34/3)*two,label='All depth 2, same cost 34',color='#74747d',ls=':')
ax[0].axhline(1,color='black',lw=1)
ax[0].set(xlabel='Alternative good extraction accuracy u',ylabel='Calibration + online KL',ylim=(0,2.7),
          title='Continuous alternatives (curves illustrative)')
ax[0].legend(loc='upper left',fontsize=8)
lo=float(certificate['full_oracle_lower']['coefficient_lower_bound_display'])
ax[1].barh([1,0],[34,41.3],color=['#175f8a','#b9691b'],height=.48)
ax[1].plot([lo,34],[1,1],color='white',lw=5,solid_capstyle='butt')
ax[1].text(34.5,1,'Oracle upper bound: 34',va='center',fontsize=9)
ax[1].text(41.8,0,'Fixed-depth lower bound: 41.3',va='center',fontsize=9)
ax[1].set(yticks=[1,0],yticklabels=['Depths may mix','Any one fixed depth'],xlim=(0,70),ylim=(-.75,1.55),
          xlabel='Leading online-cost coefficient',title='Certified separation (all 27 actions retained)')
ax[1].text(2,-.59,'Cost reduction ≥ 73/413 (≈17.68%)\nrelative to every fixed-depth design',fontsize=9)
for a in ax:a.spines[['top','right']].set_visible(False)
fig.savefig(ROOT/'depth_mixing.png',dpi=180)
fig.savefig(ROOT/'depth_mixing.pdf')

if __name__=='__main__':print('Wrote depth_mixing.png and depth_mixing.pdf')
