"""Read-only transient spatial refinement diagnostic; no new solves/gates."""
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'data/anatomical-arm-v1/review/two-state-kinetics'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
s = json.loads((OUT/'summary.json').read_text())
assert s['result'] == 'PASS_FIXED_CAPACITY_KINETIC_TRANSPORT_BENCHMARK'
z = np.load(OUT/'matched-states.npz', allow_pickle=False)
beta = s['parameters']['beta']
rows = []
for R in [2.4, 3.]:
    responses = []
    for dx in [.04, .02, .01]:
        prefix = f'R{R:g}-dx{dx:g}'
        x = z[prefix+'-x']
        eq = z[prefix+'-equilibrium-N1']
        exact = z[prefix+'-exponential-N1']
        # Unit-capacity increments; linearity makes pCa cancel after division by N.
        response = np.einsum('tdi,i->td', exact[:, :, :-1], 1+x)/beta - np.dot(eq[:-1], 1+x)/beta
        responses.append(response)
    for j, delta in enumerate([.001, -.001, .0005, -.0005]):
        scale = abs(delta)/beta
        pair = [float(np.max(np.abs(responses[i][:, j]-responses[i+1][:, j]))/scale) for i in [0, 1]]
        rows.append(dict(radius=R, delta=delta, norm='force increment divided by abs(delta)*N/beta',
                         coarseToMiddleDifference=pair[0], middleToFineDifference=pair[1],
                         halvingDifferenceRatio=pair[1]/pair[0],
                         perTimeCoarseToMiddle=((responses[0][:,j]-responses[1][:,j])/scale).tolist(),
                         perTimeMiddleToFine=((responses[1][:,j]-responses[2][:,j])/scale).tolist()))
r = dict(result='READ_ONLY_MATCHED_TIME_SPACE_DIAGNOSTIC', rendererOrAnalysisSHA256=sha(Path(__file__)),
         sourceHashes={str(p.relative_to(ROOT)): sha(p) for p in [OUT/'summary.json', OUT/'matched-states.npz']},
         matchedTimesSeconds=s['matchedTimesSeconds'], rows=rows,
         interpretation='Pairwise differences only; no independent continuous transient reference or new accuracy gate. Equilibrium is approximately second order, but center remap can give first-order transient error. No new simulation, extrapolated truth or physiological/arm qualification.')
p = OUT/'matched-space-diagnostic.json'
if p.exists():
    raise RuntimeError('refusing to overwrite diagnostic')
p.write_text(json.dumps(r, indent=2)+'\n')
print(json.dumps(r, indent=2))
