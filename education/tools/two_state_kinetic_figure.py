"""Render bound kinetic receipts. Does not execute the kinetic experiment."""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'data/anatomical-arm-v1/review/two-state-kinetics'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
s = json.loads((OUT/'summary.json').read_text())
assert s['result'] == 'PASS_FIXED_CAPACITY_KINETIC_TRANSPORT_BENCHMARK'
c = s['cases']
fig, ax = plt.subplots(2, 2, figsize=(12, 8.4))
fig.subplots_adjust(top=.82, bottom=.13, hspace=.48, wspace=.31)
fig.suptitle('Attached population: fast response and kinetic relaxation', fontsize=17, fontweight='bold', y=.965)
fig.text(.5, .913, 'Nonhuman, fixed-capacity equation fixture • direct contractile-coordinate clamp', ha='center', fontsize=11)
fig.text(.5, .88, '144 cases • two extents • three bin widths • three timesteps • fixed 1 s horizon', ha='center', fontsize=10, color='#4b5563')
colors = ['#bf6b28', '#5b83a0', '#185b47']
group = [v for v in c if v['grid']=='R3-dx0.01' and v['pCa']==4.5 and v['delta']==.001]
for v, color in zip(group, colors):
    norm = abs(v['delta'])*v['capacity']/s['parameters']['beta']
    ax[0, 0].plot(s['matchedTimesSeconds'], (np.array(v['matchedForces'])-v['baselineForce'])/norm,
                  'o-', color=color, ms=4, label=f"BE dt={v['dt']:g} s")
v = group[-1]
ax[0, 0].plot(s['matchedTimesSeconds'], (np.array(v['matchedReferenceForces'])-v['baselineForce'])/norm,
              'k--', lw=1.4, label='Exact finite generator')
ax[0, 0].set(xlim=(0, .2), title='Matched-time relaxation after +0.001 shift', xlabel='Time (s)',
              ylabel='Force increment / (N delta / beta)')
ax[0, 0].legend(fontsize=8)
for pca, color in zip([4.5, 6.1], ['#185b47', '#5b83a0']):
    pairs = [v for v in c if v['grid']=='R3-dx0.01' and v['pCa']==pca and v['dt']==.001]
    delta = [v['delta'] for v in pairs]
    fast = [v['boundary']['immediateForceIncrement'] for v in pairs]
    relaxed = [v['matchedForces'][-1]-v['baselineForce'] for v in pairs]
    order = np.argsort(delta)
    ax[0, 1].plot(np.array(delta)[order], np.array(fast)[order], 'o-', color=color, label=f'pCa {pca:g}, immediate')
    ax[0, 1].plot(np.array(delta)[order], np.array(relaxed)[order], 'x--', color=color, label=f'pCa {pca:g}, 1 s')
ax[0, 1].set(title='Immediate and relaxed increments differ', xlabel='Dimensionless link-coordinate shift', ylabel='Normalized force increment')
ax[0, 1].ticklabel_format(axis='x', style='sci', scilimits=(0, 0))
ax[0, 1].legend(fontsize=8)
for radius, marker, color in [(2.4, 'o', '#5b83a0'), (3., 'x', '#185b47')]:
    g = [v for v in s['grids'] if v['radius']==radius]
    ax[1, 0].loglog([v['dx'] for v in g], [v['equilibriumForceErrorRelative'] for v in g], marker+'-',
                    color=color, label=f'Extent ±{radius:g}')
ax[1, 0].set(title='Spatial equilibrium error against quadrature', xlabel='Bin width', ylabel='Relative baseline-force error')
ax[1, 0].legend(fontsize=8)
ax[1, 0].text(.05, .09, 'Error ratio ≈ 0.250 per halving\nFinest relative error: 1.687e−6', transform=ax[1, 0].transAxes, fontsize=9)
ax[1, 1].loglog([v['dt'] for v in group], [v['maximumMatchedForceError'] for v in group], 'o-', color='#185b47')
ax[1, 1].set(title='Temporal error against exact finite generator', xlabel='Timestep (s)', ylabel='Max matched-time force error')
ax[1, 1].text(.05, .1, 'All-case error ratios: 0.5046–0.5095\nExtent force difference ≤ 7.38e−14', transform=ax[1, 1].transAxes, fontsize=9)
for a in ax.flat:
    a.grid(True, alpha=.2)
    a.spines[['top', 'right']].set_visible(False)
fig.text(.5, .046, 'Same-input relaxed force is unchanged by construction. No descending-branch, human, series-history or arm qualification.',
          ha='center', fontsize=10, color='#7b332d')
outputs = []
for ext in ['png', 'pdf']:
    p = OUT/f'two-state-kinetics.{ext}'
    if p.exists():
        raise RuntimeError('refusing to overwrite a render')
    fig.savefig(p, dpi=170, metadata={'Creator': 'Kenoma bounded research renderer'})
    outputs.append(p)
plt.close(fig)
receipt = dict(result='PASS_RENDER_FROM_BOUND_KINETIC_RECEIPTS', rendererSHA256=sha(Path(__file__)),
               inputs={str((OUT/'summary.json').relative_to(ROOT)): sha(OUT/'summary.json')},
               outputs={str(p.relative_to(ROOT)): sha(p) for p in outputs},
               scope='Static scientific figure, equation-only normalized kinetic fixture')
(OUT/'render-receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps(receipt, indent=2))
