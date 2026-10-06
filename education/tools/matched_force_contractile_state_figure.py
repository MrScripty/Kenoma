#!/usr/bin/env python3
"""Static source-bound experiment figure; production contact renderer untouched."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import fitz

import matched_force_contractile_state as experiment


def main():
    out = experiment.OUT
    d = json.loads((out/'summary.json').read_text())
    assert d['result'] == 'PASS_BOUNDED_MATCHED_FORCE_COUPLING'
    times = np.array(d['timesSeconds'])
    s = d['sensitivity']['800']
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.4))
    fig.subplots_adjust(left=.06, right=.98, top=.74, bottom=.25, wspace=.3)
    fig.suptitle('Carried contractile state adds fast response; the negative mode returns',
                 fontsize=16, x=.06, ha='left', y=.95)
    fig.text(.06, .865, 'Matched nominal-force scale: 155 kPa · initial total cap force 39.76115 N · educational strain gain 130', fontsize=11)
    fig.text(.06, .813, '24 retained continuous-density histories · independent endpoint tangent · same frozen 1.25 block', fontsize=10, color='#475569')
    ax = axes[0]
    analytic = np.array(s['activeEndpointTangentPa'])/1e6
    ax.plot(times, analytic, 'o-', color='#2563eb', label='Carried state, active tangent')
    for delta, marker in [(.001, 'x'), (.0005, '+')]:
        t = next(t for t in d['tangentChecks'] if t['count'] == 800 and t['maxStepSeconds'] == .0005 and t['delta'] == delta)
        fd = (np.array(t['finiteDifferencePa'])-d['passivePointTangentPa'])/1e6
        ax.scatter(times, fd, marker=marker, s=70, color='#0f172a', label=f'Nonlinear ±{delta:g} difference')
    ax.axhline(d['relaxedActiveTangentPa']/1e6, color='#dc2626', linestyle='--', label='Relaxed / reset: −0.465 MPa')
    ax.axhline(0, color='#94a3b8', lw=.7)
    ax.set(title='Active axial endpoint response', xlabel='Hold time (s)', ylabel='dp_active / dλ (MPa)')
    ax.legend(loc='upper right', fontsize=7.8, frameon=False)
    ax = axes[1]
    block = d['block']['responses']
    minimum = [r['lowestSampledEigenvaluesNPerM'][0] for r in block[:6]]
    ax.plot(times, minimum, 'o-', color='#7c3aed', label='Lowest sampled operator eigenvalue')
    ax.axhline(0, color='#94a3b8', lw=.7)
    ax.axhline(block[-1]['lowestSampledEigenvaluesNPerM'][0], color='#dc2626', ls='--', label='Relaxed: −9,477 N/m')
    ax.annotate('−8,369 N/m at 0.2 s', xy=(.2, minimum[-1]), xytext=(.065, -6200), fontsize=9,
                arrowprops=dict(arrowstyle='->', color='#475569'))
    ax.set(title='Frozen block response operator', xlabel='Hold time (s)', ylabel='Sampled eigenvalue (N/m)')
    ax.legend(loc='lower left', fontsize=8, frameon=False)
    ax.text(.04, .68, 'Powered endpoint response\nNot a stored-energy Hessian', transform=ax.transAxes, fontsize=9, color='#475569')
    ax = axes[2]
    run = next(r for r in d['runs'] if r['name'] == 'R3-nodes800-pCa4.5-delta0.001-maxstep0.0005')
    inp = [h['attachmentElasticInputW'] for h in run['holds']]
    loss = [h['detachmentElasticRemovalW'] for h in run['holds']]
    ax.plot(times, inp, 'o-', color='#059669', label='Attachment elastic input')
    ax.plot(times, loss, 's--', color='#d97706', label='Detachment elastic removal')
    ax.set(title='Active hold energy channels (+.001)', xlabel='Hold time (s)', ylabel='Elastic channel power (W)')
    ax.ticklabel_format(axis='y', style='plain', useOffset=False)
    ax.legend(loc='upper right', fontsize=8, frameon=False)
    for ax in axes:
        ax.grid(alpha=.17)
        ax.spines[['top', 'right']].set_visible(False)
    fig.text(.06, .14, '480 fixed gates pass · worst endpoint derivative error 7.40×10⁻⁷ (gate 10⁻⁴) · time/space density gates retained', fontsize=10)
    fig.text(.06, .087, 'Positive fixed-transverse point response does not imply a positive block operator. Active input is separate from passive storage.', fontsize=9.5)
    fig.text(.06, .037, 'Composite educational experiment · no new nonlinear trajectory · no ATP/heat closure · no anatomical or clinical validation', fontsize=9.5, color='#475569')
    paths = [out/'matched-force-contractile-state.png', out/'matched-force-contractile-state.pdf',
             out/'matched-force-contractile-state.pdf-raster.png']
    assert not any(p.exists() for p in paths)
    fig.savefig(paths[0], dpi=160)
    fig.savefig(paths[1])
    plt.close(fig)
    doc = fitz.open(paths[1])
    assert len(doc) == 1
    doc[0].get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).save(paths[2])
    receipt = dict(sourceSHA256=experiment.digest(Path(__file__)), summarySHA256=experiment.digest(out/'summary.json'),
                   files={p.name: experiment.digest(p) for p in paths}, PDFPages=len(doc),
                   PNGPixels=[2400, 864], PDFRasterPixels=[1620, 584],
                   humanVisualInspectionPending=True)
    with (out/'render-receipt.json').open('x') as f:
        json.dump(receipt, f, indent=2)
        f.write('\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
