"""Plot the independently replayed anatomical lift/release receipt."""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 17, 'legend.fontsize': 15})

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/anatomical-arm-v1/audit'
execution = BASE / 'contact-lift-release-results.json'
run = json.loads(execution.read_text())
check = json.loads((BASE / 'contact-lift-release-recheck.json').read_text())
assert check['result'] == 'PASS'
assert check['executionReceiptSHA256'] == hashlib.sha256(execution.read_bytes()).hexdigest()
rows = check['rows']
time = [0] + [r['timeS'] for r in rows]
angle = [run['held']['state']['qRad']] + [r['qRad'] for r in rows]
activation = [0] + [r['activation'] for r in rows]
effort = [0] + [r['effort'] for r in run['attempts']]
residual = [check['heldResidualN']] + [r['residualN'] for r in rows]
release = next(r['timeS'] - a['hS'] for r, a in zip(rows, run['attempts']) if a['label'] == 'release')
fig, axes = plt.subplots(2, 2, figsize=(10, 7), constrained_layout=True)
axes[0, 0].plot(time, [q * 180 / 3.141592653589793 for q in angle], marker='.')
axes[0, 0].set_ylabel('Elbow flexion (degrees)')
axes[0, 1].plot(time, activation, label='Activation', marker='.')
axes[0, 1].step(time, effort, where='pre', label='Effort', linestyle='--')
axes[0, 1].set_ylabel('Authored\nactivation / effort')
axes[0, 1].legend()
axes[1, 0].semilogy(time, residual, marker='.', label='Replayed residual')
axes[1, 0].axhline(run['parameters']['stationarityToleranceN'], linestyle='--', color='red', label='Original force gate')
axes[1, 0].set_ylabel('Maximum free gradient (N)')
axes[1, 0].legend()
axes[1, 1].plot([r['timeS'] for r in rows], [r['minimumJ'] for r in rows], marker='.')
axes[1, 1].set_ylabel('Minimum sampled body J')
for ax in axes.flat:
    ax.axvline(release, color='grey', linestyle=':')
    ax.set_xlabel('Accepted time (s)')
    ax.grid(alpha=.2)
fig.suptitle('Reduced anatomical arm: 0.5 kg load, effort 0.04, then release\nEvery recorded pose passes finite triangle and axial-path audits')
out = ROOT / 'dist/assets/anatomical-contact-trajectory.png'
out.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(out, dpi=180)
print(out)
