"""Source-bound final figure: retained rejection and eligible fine comparison."""
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'data/anatomical-arm-v1/review/source-amplitude-p2-p1-v2'
OLD = ROOT/'data/anatomical-arm-v1/review/source-amplitude-p2-p1'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
summary = json.loads((OUT/'summary.json').read_text())
for name, digest in summary['sourceHashes'].items():
    assert sha(ROOT/name) == digest, name
outputs = [OUT/'source-amplitude.png', OUT/'source-amplitude.pdf', OUT/'render-receipt.json']
assert not any(p.exists() for p in outputs), 'Preserve previous render'
inputs = [OUT/'summary.json', OLD/'coarse-1.01.json', OUT/'coarse-1.25-reclassification.json', OLD/'equivalence-control.json']
records = [json.loads(p.read_text()) for p in inputs[1:3]]
fine = OUT/'fine-1.25.json'
if fine.exists():
    inputs.append(fine)
    records.append(json.loads(fine.read_text()))
fig, axes = plt.subplots(1, 3, figsize=(13, 5.1), layout='constrained')
fig.suptitle('155 kPa × activation 1: source-anchored educational block', fontsize=15, fontweight='bold')
colors = ['#bf493f', '#157a82', '#476cc0']
for record, color in zip(records, colors):
    h = record['history']
    label = record['name'] + ('; pressure rejected' if not record['stationaryAccepted'] else '')
    axes[0].plot([x['iteration'] for x in h], [x['forceResidualN'] for x in h], 'o-', color=color, label=label)
axes[0].axhline(1e-4, color='#333', ls=':', label='unchanged force gate')
axes[0].set(yscale='log', xlabel='Newton iteration', ylabel='Full free-force residual [N]', title='Force passing alone is insufficient')
axes[0].legend(fontsize=8)
accepted = [r for r in records if r['stationaryAccepted'] and r['derivativeGatesPass']]
labels = [r['name'].replace('-', '\n') for r in accepted]
axes[1].bar(range(len(accepted)), [r['replays']['256']['capForceN'] for r in accepted], color=colors[1:])
axes[1].set_xticks(range(len(accepted)), labels)
axes[1].set(ylabel='Cap reaction [N]', title='Accepted matched-static specimens')
values = [r['spectrum']['lowestEigenvaluesNPerM'][0] for r in accepted]
axes[2].bar(range(len(values)), values, color='#bf493f')
axes[2].axhline(0, color='#333', lw=.8)
axes[2].set_xticks(range(len(values)), labels)
axes[2].set(ylabel='Lowest physical eigenvalue [N/m]', title='Verified negative curvature persists')
for i, value in enumerate(values):
    axes[2].annotate(f'{value:,.2f}', (i, value), xytext=(0, -16), textcoords='offset points', ha='center', fontsize=9)
if values:
    axes[2].set_ylim(min(values)*1.25, max(1, -min(values)*.08))
fig.supxlabel('Coarse stretch 1.01: pointwise pressure RMS 3.35×10⁻⁴ > 10⁻⁶; no refinement or curvature classification.\nMatched α = 87.084 kPa preserves the original −4293.9875 N/m witness. New runs use α = 155 kPa.\nSource: skinned human VL, 15°C cohort mean. Authored static block; no force–length, arm or clinical validation.\nEuclidean nodal spectra are mesh dependent; no continuum spectrum-convergence claim.', fontsize=9)
fig.savefig(outputs[0], dpi=160)
fig.savefig(outputs[1])
plt.close(fig)
receipt = dict(rendererSHA256=sha(Path(__file__)), inputs={str(p.relative_to(ROOT)): sha(p) for p in inputs},
               outputs={str(p.relative_to(ROOT)): sha(p) for p in outputs[:2]}, scope=summary['scope'])
outputs[2].write_text(json.dumps(receipt, indent=2)+'\n')
print('RENDERED', outputs[0], outputs[1])
