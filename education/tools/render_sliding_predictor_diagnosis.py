#!/usr/bin/env python3
"""Render archived unaccepted predictor defects; no trajectory or solver."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'education/data/sliding-constraint-policy-proposal-v1'


def main():
    records = json.loads((DATA/'predictor-curvature-diagnosis.json').read_text())['records']
    values = [abs(r['rejected_H']) for r in records.values()]
    fig, ax = plt.subplots(figsize=(10, 5.5), constrained_layout=True)
    fig.suptitle('Archived unaccepted predictors: all three failed the original gate', fontsize=15)
    ax.bar(['RK4 200 µs\nfirst midpoint', 'DOP853\ninitialization probe', 'Radau\ninitialization probe'],
           values, color=['#c65537', '#497db0', '#497db0'], width=.55)
    ax.set_yscale('log')
    ax.set_ylim(4e-10, 1e-6)
    ax.axhline(1e-9, color='#252525', linestyle='--', linewidth=1.5)
    ax.text(2.48, 1.08e-9, 'original gate 1e−9', ha='right', fontsize=10)
    for j, value in enumerate(values):
        ax.text(j, value*1.17, f'{value:.8g}\n{value/1e-9:.3f} × gate', ha='center', fontsize=11)
    ax.set_ylabel('Absolute native H (dimensionless; logarithmic scale)')
    ax.grid(axis='y', alpha=.2)
    ax.set_axisbelow(True)
    ax.spines[['top', 'right']].set_visible(False)
    fig.supxlabel('Zero accepted sliding steps in these cells; exact rollback.\n'
                   'Read-only diagnosis: zero new ODE steps. Revised policy remains held.', fontsize=11)
    for suffix in ['png', 'svg']:
        path = DATA/f'archived-predictor-defects.{suffix}'
        if path.exists():
            raise ValueError('Refuse to overwrite render evidence')
        fig.savefig(path, dpi=180, metadata={'Creator': 'Kenoma archived predictor diagnosis'})
    plt.close(fig)
    print('Rendered three archived unaccepted defects; no proposed-policy execution')


if __name__ == '__main__':
    main()
