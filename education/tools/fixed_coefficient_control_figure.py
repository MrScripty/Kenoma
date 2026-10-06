"""Render completed fixed-coefficient controls without solving mechanics."""
from pathlib import Path
import hashlib
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/anatomical-arm-v1'
OUT = BASE / 'review/fixed-coefficient-controls'
NAMES = ['prism', 'taper', 'attachment', 'sheet']
COLORS = ['#156b93', '#b53d42', '#167e68', '#8056aa']
LABELS = ['Matched prism', 'Taper, fixed caps', 'Frozen attachments', 'Attachments + sheets']
inputs = {}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(name):
    path = BASE / name
    inputs[name] = digest(path)
    return json.loads(path.read_text())

cases = []
for name in NAMES:
    run = read(f'audit/fixed-coefficient-{name}.json')
    replay = read(f'audit/fixed-coefficient-{name}-recheck.json')
    assert replay['executionReceiptSHA256'] == inputs[f'audit/fixed-coefficient-{name}.json']
    assert replay['result'] in ['PASS_REDUCED_CONTROL_REPLAY', 'PASS_PRESERVED_CONTROL_REJECTION']
    assert replay['verifiedAcceptedStages'] == len(run['accepted'])
    cases.append((run, replay))

fig, axes = plt.subplots(2, 2, figsize=(12, 8.2))
summary = []
for (run, replay), color, label in zip(cases, COLORS, LABELS):
    accepted = [r for r in replay['rows'] if r['accepted'] and r['activation'] > 0]
    rejected = [r for r in replay['rows'] if not r['accepted']]
    force = lambda r, key: sum(v[key] for k, v in r['reactions'].items() if k != 'support')
    a = [r['activation'] for r in accepted]
    axes[0, 0].plot(a, [r['minimumCornerJ'] for r in accepted], 'o-', color=color, label=label)
    axes[0, 1].plot(a, [r['fields']['forceLength']['mean'] for r in accepted], 'o-', color=color)
    axes[1, 0].plot(a, [r['maximumFreeNodalComponentN'] for r in accepted], 'o-', color=color)
    axes[1, 0].plot(a, [r['independentResidualN'] for r in accepted], ':', color=color, alpha=.7)
    axes[1, 1].plot(a, [force(r, 'directDistalN') for r in accepted], 'o-', color=color)
    axes[1, 1].plot(a, [force(r, 'axialVirtualForceN') for r in accepted], '^--', color=color)
    for row in rejected:
        x = row['activation']
        for ax, y in [(axes[0, 0], row['minimumCornerJ']),
                      (axes[0, 1], row['fields']['forceLength']['mean']),
                      (axes[1, 0], row['maximumFreeNodalComponentN']),
                      (axes[1, 1], force(row, 'directDistalN')),
                      (axes[1, 1], force(row, 'axialVirtualForceN'))]:
            ax.plot(x, y, 'x', color=color, markersize=10, markeredgewidth=2)
    last = replay['rows'][-1]
    summary.append({'case': run['case'], 'executionResult': run['result'],
                    'freshReplayResult': replay['result'], 'acceptedStages': len(run['accepted']),
                    'lastAcceptedActivation': replay['lastAcceptedActivation'],
                    'terminalCandidateAccepted': last['accepted'],
                    'terminalCandidateActivation': last['activation'],
                    'terminalCandidateIndependentResidualN': last['independentResidualN'],
                    'terminalCandidateFullNodalResidualN': last['maximumFreeNodalComponentN'],
                    'terminalCandidateMinimumCornerJ': last['minimumCornerJ'],
                    'terminalCandidateGlobalVolumeRatio': last['globalVolumeRatio'],
                    'terminalCandidateMeanForceLength': last['fields']['forceLength']['mean'],
                    'terminalCandidateDirectBodyAndSheetForceN': force(last, 'directDistalN'),
                    'terminalCandidateVirtualBodyAndSheetForceN': force(last, 'axialVirtualForceN')})

for ax in axes.flat:
    ax.set_xscale('log')
    ax.set_xlabel('Activation (prescribed)')
    ax.grid(True, alpha=.18)
axes[0, 0].set(title='Local volume ratio; total volume can still increase', ylabel='Minimum corner J')
axes[0, 0].axhline(1, color='#999999', linestyle=':', linewidth=1)
axes[0, 1].set(title='Operating force–length suppression', ylabel='Reference-volume mean fL')
axes[1, 0].set(title='Full nodal force (solid) / projected force (dotted)', ylabel='Largest force component (N)')
axes[1, 0].set_yscale('log')
axes[1, 0].axhline(1e-4, color='#555555', linestyle='--', label='Unchanged 1e-4 N gate')
axes[1, 0].legend(fontsize=8)
axes[1, 1].set(title='Direct cap (solid) / whole-body virtual force (dashed)', ylabel='Body + sheet axial force (N)')
axes[1, 1].set_yscale('symlog', linthresh=1)
fig.suptitle('Fixed coefficients: reduced balance and unresolved tissue mechanics', fontsize=16)
handles, labels = axes[0, 0].get_legend_handles_labels()
fig.legend(handles, labels, loc='lower center', ncol=4, bbox_to_anchor=(.5, .045), fontsize=10)
fig.text(.5, .013, '× = rejected candidate; neither attachment case advances past activation 0.  No full-nodal or biological qualification.', ha='center', fontsize=10)
fig.tight_layout(rect=(0, .095, 1, .955))
outputs = {}
for suffix in ['png', 'pdf']:
    path = OUT / f'fixed-coefficient-controls.{suffix}'
    if path.exists():
        raise RuntimeError('Preserve existing render ' + str(path))
    fig.savefig(path, dpi=180)
    outputs[path.name] = digest(path)
plt.close(fig)
receipt = {'schema': 1, 'result': 'PASS_SOURCE_BOUND_CONTROL_RENDER', 'rendererSHA256': digest(Path(__file__)),
           'inputs': inputs, 'outputs': outputs, 'cases': summary,
           'limits': ['Accepted reduced states and rejected candidates are explicitly separated.',
                      'Full free nodal forces remain a separate failing diagnostic for the tapered control.',
                      'No constitutive assumption, coefficient, iteration budget, activation schedule or acceptance gate changes.']}
path = OUT / 'control-render-receipt.json'
if path.exists():
    raise RuntimeError('Preserve existing render receipt')
path.write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
