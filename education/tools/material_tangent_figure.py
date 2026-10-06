"""Finite local tangent evidence, with explicit acceptance limits."""
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

root = Path(__file__).resolve().parents[1]
base = root / 'data/anatomical-arm-v1'
review = base / 'review/fixed-coefficient-controls'
receipt = review / 'acoustic-render-receipt.json'
if receipt.exists():
    raise RuntimeError('Preserve render evidence')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
inputs = [base / ('audit/' + stem + suffix + '.json') for stem in ['fixed-coefficient-acoustic-audit', 'fixed-coefficient-loaded-acoustic'] for suffix in ['', '-recheck']]
control, cr, load, lr = [json.loads(p.read_text()) for p in inputs]
for r, p in [(cr, inputs[0]), (lr, inputs[2])]:
    assert r['result'] == 'PASS_INDEPENDENT_FROZEN_ACOUSTIC_REPLAY'
    assert r['executionReceiptSHA256'] == sha(p)
fig, ax = plt.subplots(2, 2, figsize=(12.8, 8))
labels = ['Prism\na=1', 'Affine taper\na=1', 'Original fit\na=1', 'Quadratic\nrejected .01', 'Quadratic\naccepted .01']
rows = control['rows']
values = [r['worst']['minimumEigenvaluePa']/1e6 for r in rows]
ax[0,0].bar(labels, values, color=['#337a99' if v>0 else '#ba5548' for v in values])
ax[0,0].set_yscale('symlog', linthresh=.001)
ax[0,0].axhline(0, color='black', lw=1)
ax[0,0].set(ylabel='Minimum tested eigenvalue (MPa; signed log)', title='Frozen calibration / controls')
ax[0,1].bar(labels, [100*r['referenceVolumeFractionWithNegativeWitness'] for r in rows], color='#ba5548')
ax[0,1].set(ylabel='Reference volume with negative witness (%)', title='Finite 13-direction scan')
ids = ['FJ1486', 'FJ1512', 'FJ1478']
names = ['Brachialis', 'Short biceps', 'Long biceps']
colors = ['#337a99', '#ba5548', '#788847']
indices = load['selection']['selectedIndices']
for i, (id_, name, color) in enumerate(zip(ids, names, colors)):
    rs = [next(r for r in load['rows'] if r['elementId']==id_ and r['snapshotIndex']==idx) for idx in indices]
    x = np.arange(len(indices))+(i-1)*.25
    ax[1,0].bar(x, [r['worst']['minimumEigenvaluePa']/1e6 for r in rs], .24, label=name, color=color)
    ax[1,1].bar(x, [100*r['referenceVolumeFractionWithNegativeWitness'] for r in rs], .24, color=color)
ax[1,0].set_yscale('symlog', linthresh=.001)
ax[1,0].axhline(0, color='black', lw=1)
ax[1,0].set(ylabel='Minimum tested eigenvalue (MPa; signed log)', title='Saved accepted 0.5 kg states')
ax[1,0].legend(fontsize=9)
ax[1,1].set(ylabel='Reference volume with negative witness (%)', title='No trajectory rerun')
for a in ax[1]:
    a.set_xticks(range(len(indices)), ['0.085 s\nWorst corner', '0.13 s\nPeak activation', '0.43 s\nFinal release'])
fig.suptitle('Unchanged material: verified negative rank-one curvature dominated by the active descending limb', fontsize=12)
fig.text(.5, .015, 'Local body-material probes; finite directions/times cannot prove strong ellipticity or global stability. Reduced acceptance does not qualify the envelope.', ha='center', fontsize=9)
fig.tight_layout(rect=(0,.05,1,.94))
outputs = [review / ('material-tangent-comparison.'+ext) for ext in ['png','pdf']]
for p in outputs:
    if p.exists():
        raise RuntimeError('Preserve existing figure')
    fig.savefig(p, dpi=180)
result = {'result':'PASS_SOURCE_BOUND_MATERIAL_TANGENT_RENDER', 'inputs':{str(p.relative_to(root)):sha(p) for p in inputs}, 'rendererSHA256':sha(Path(__file__)), 'outputs':{str(p.relative_to(root)):sha(p) for p in outputs}}
receipt.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
