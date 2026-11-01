"""Illustrate analytic certified bounds; this plotting grid proves nothing."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent


def lower(alpha, c):
    out = 50*(c+1)*(1-alpha*(5151/10000))
    for L in range(2, 7):
        out = np.minimum(out, (206/5)*(c+L)/(L+1))
    return out


def run():
    cert = json.loads((ROOT/'REGION_CERTIFICATE.json').read_text())
    assert cert['status'].startswith('PASS_EXACT')
    a, c = np.linspace(.95, 1.2, 201), np.linspace(.5, 1.5, 201)
    A, C = np.meshgrid(a, c)
    U = 16*C+18
    B = lower(A, C)
    saving = 100*(1-U/B)
    assert saving.min() >= 100*(5/103)-1e-10
    plt.rcParams.update({'font.size':10, 'axes.spines.top':False, 'axes.spines.right':False,
                         'pdf.fonttype':42, 'ps.fonttype':42})
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2), layout='constrained')
    im = ax[0].pcolormesh(A, C, saving, shading='auto', cmap='viridis', rasterized=True)
    fig.colorbar(im, ax=ax[0], label='Guaranteed online cost reduction (%)')
    ax[0].set(xlabel=r'Calibration coefficient $\alpha$', ylabel=r'Access cost $c/\ell$',
              title='Certified inner region', xlim=(.95, 1.2), ylim=(.5, 1.5))
    ax[0].text(.962, 1.43, r'Uniform guarantee: $5/103$ ($\approx4.85\%$)',
               color='white', fontsize=10)
    uc, bc = 16*c+18, lower(1.2, c)
    ax[1].plot(c, bc, label='Every fixed depth: lower bound', color='#8c4d0c', lw=2)
    ax[1].plot(c, uc, label='Mixed-depth witness: upper bound', color='#176b97', lw=2)
    ax[1].fill_between(c, uc, bc, color='#83baa6', alpha=.25)
    ax[1].set(xlabel=r'Access cost $c/\ell$', ylabel=r'Online cost coefficient / $\ell$',
              title=r'Bounds at $\alpha=1.20$', xlim=(.5, 1.5))
    ax[1].legend(loc='upper left', fontsize=8.5)
    ax[1].text(.92, 28, r'Gap $\geq 15/7$ throughout the rectangle', fontsize=9)
    fig.suptitle(r'Valid for $|r-0.6|, |p-0.95|, |q-0.6|\leq 1/40000$', fontsize=12)
    fig.savefig(ROOT/'depth_region.png', dpi=180, metadata={'Software':'QRelBench theory certificate'})
    fig.savefig(ROOT/'depth_region.pdf', metadata={'CreationDate':None, 'ModDate':None})
    plt.close(fig)
    print(json.dumps({'status':'PASS_PLOT_FROM_CERTIFIED_BOUNDS',
                      'minimum_displayed_saving_percent':float(saving.min()),
                      'not_exact_optimal_costs':True}, indent=2))


if __name__ == '__main__':
    run()
