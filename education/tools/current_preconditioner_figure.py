"""Source-bound isolated-control comparison; no solver or acceptance changes."""
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parents[1]
base = root / 'data/anatomical-arm-v1'
review = base / 'review/fixed-coefficient-controls'
inputs = [base / ('audit/fixed-coefficient-taper-quadratic' + suffix + '.json')
          for suffix in ['', '-current-preconditioner', '-current-preconditioner-recheck']]
receipt = review / 'current-preconditioner-render-receipt.json'
if receipt.exists():
    raise RuntimeError('Preserve existing render evidence')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
old, new, replay = [json.loads(p.read_text()) for p in inputs]
assert replay['result'] == 'PASS_ENLARGED_CONTROL_REPLAY'
assert replay['executionReceiptSHA256'] == sha(inputs[1])
fig, axes = plt.subplots(1, 3, figsize=(13, 4.8))
for r, name in [(old, 'Reference: rejected at 80'), (new, 'Current + fallback: accepted at 30')]:
    t = r['attempt']['trace']
    axes[0].semilogy([v['iteration'] for v in t], [v['maxGradient'] for v in t], label=name)
axes[0].axhline(1e-4, color='black', ls='--', lw=1, label='Unchanged 1e-4 N gate')
axes[0].set(xlabel='Nonlinear iteration', ylabel='Recorded projected residual (N)', title='Same 80/80 budgets')
axes[0].legend(fontsize=8)
c = replay['comparison']
labels = ['Affine\naccepted', 'Quadratic\naccepted']
axes[1].bar(labels, [c[k]['minimumCornerJ'] for k in ['affine', 'quadratic']], color=['#347b9f', '#ba5548'])
axes[1].axhline(1, color='black', lw=1)
axes[1].set(ylabel='Minimum corner J', title='Local compression persists', ylim=(0, 1.1))
axes[2].bar(labels, [c[k]['fullNodalResidualN'] for k in ['affine', 'quadratic']], color=['#347b9f', '#ba5548'])
axes[2].set(ylabel='Maximum free nodal force (N)', title='Excluded forces remain')
fig.suptitle('Fixed coefficients, activation 0.01: reduced convergence does not qualify the tissue shape', fontsize=12)
fig.text(.5, .015, 'Matched restricted states differ by 13.703 mm; total volume ratios remain near 1.0085. Full nodal/spatial convergence unqualified.', ha='center', fontsize=9)
fig.tight_layout(rect=(0, .05, 1, .92))
outputs = [review / ('current-preconditioner-comparison.' + ext) for ext in ['png', 'pdf']]
for p in outputs:
    if p.exists():
        raise RuntimeError('Preserve existing figure')
    fig.savefig(p, dpi=180)
data = {'result': 'PASS_SOURCE_BOUND_CONTROL_RENDER', 'inputs': {str(p.relative_to(root)): sha(p) for p in inputs},
        'rendererSHA256': sha(Path(__file__)), 'outputs': {str(p.relative_to(root)): sha(p) for p in outputs}}
receipt.write_text(json.dumps(data, indent=2) + '\n')
print(json.dumps(data, indent=2))
