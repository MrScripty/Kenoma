"""Render actual amplitude-comparator outcomes without physiological claims."""
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'data/anatomical-arm-v1/review/source-amplitude-p2-p1'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
summary = json.loads((OUT/'summary.json').read_text())
outputs = [OUT/'source-amplitude.png', OUT/'source-amplitude.pdf', OUT/'render-receipt.json']
assert not any(p.exists() for p in outputs), 'Preserve previous render'
for name, digest in summary['sourceHashes'].items():
    assert sha(ROOT/name) == digest, name
cases = summary['cases']
fig, axes = plt.subplots(1, 3, figsize=(13, 4.8), layout='constrained')
fig.suptitle('155 kPa educational amplitude: actual static P2/P1 outcomes', fontsize=15, fontweight='bold')
colors = {1.01: '#157a82', 1.25: '#bf493f'}
inputs = [OUT/'summary.json', OUT/'equivalence-control.json']
for case in cases:
    name = case['name']
    path = OUT/(name+'.json')
    if not path.exists():
        continue
    inputs.append(path)
    record = json.loads(path.read_text())
    stretch = record['stretch']
    history = record['history']
    axes[0].plot([h['iteration'] for h in history], [h['forceResidualN'] for h in history],
                 'o-' if name.startswith('coarse') else 's--', color=colors[stretch], label=name)
axes[0].axhline(1e-4, color='#333', ls=':', label='unchanged force gate')
axes[0].set(yscale='log', xlabel='Newton iteration', ylabel='Full free-force residual [N]', title='Perturbed starts; original budgets')
axes[0].legend(fontsize=8)
for level, marker in [('coarse', 'o'), ('fine', 'x')]:
    selected = [c for c in cases if c['name'].startswith(level) and c['stationaryAccepted']]
    axes[1].plot([float(c['name'].split('-')[1]) for c in selected], [c['capForceN'] for c in selected], marker, ms=9, label=level)
axes[1].set(xlabel='Prescribed stretch; separate static cases', ylabel='Cap reaction [N]', title='Original-Node accepted reactions')
axes[1].legend(fontsize=9)
selected = [c for c in cases if c['stationaryAccepted'] and c['derivativeGatesPass']]
values = [c['minimumEigenvalueNPerM'] for c in selected]
axes[2].bar(range(len(values)), values, color=['#157a82' if v > 0 else '#bf493f' for v in values])
axes[2].axhline(0, color='#333', lw=.8)
axes[2].set_xticks(range(len(values)), [c['name'].replace('-', '\n') for c in selected])
axes[2].set(yscale='symlog', ylabel='Lowest physical eigenvalue [N/m]', title='Derivative-qualified curvature only')
fig.supxlabel('Source: skinned human VL, 15°C cohort mean. Composite authored block; no force–length reproduction or arm validation.\nMatched activation × peak stress preserves the original law and negative witness. Nodal spectra have no continuum-convergence claim.', fontsize=9)
fig.savefig(outputs[0], dpi=160)
fig.savefig(outputs[1])
plt.close(fig)
outputs[2].write_text(json.dumps(dict(rendererSHA256=sha(Path(__file__)), inputs={str(p.relative_to(ROOT)): sha(p) for p in inputs},
                                     outputs={str(p.relative_to(ROOT)): sha(p) for p in outputs[:2]}, scope=summary['scope']), indent=2)+'\n')
print('RENDERED', outputs[0], outputs[1])
