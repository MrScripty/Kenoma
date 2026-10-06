"""Read-only source/state preservation and scope check; no kinetics execution."""
import hashlib
import json
import subprocess
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'data/anatomical-arm-v1/review/two-state-kinetics'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
m = json.loads((OUT/'evidence-manifest.json').read_text())
for p, h in m['sha256'].items():
    assert sha(ROOT/p) == h, p
s = json.loads((OUT/'summary.json').read_text())
assert s['result'] == 'PASS_FIXED_CAPACITY_KINETIC_TRANSPORT_BENCHMARK'
assert len(s['cases']) == 144 and len(s['grids']) == 6
assert s['parameters'] == dict(f1=52.,g1=4.,g2=21.1,E1=2.,E2=-.6,w=.3,beta=.5,nH=3.1,Ca50M=.83e-6)
for p, h in s['sourceHashes'].items():
    assert sha(ROOT/p) == h, p
    source = subprocess.check_output(['git','show',s['executionCommit']+':education/'+p], cwd=ROOT)
    assert hashlib.sha256(source).hexdigest() == h, p
assert sha(OUT/'matched-states.npz') == s['matchedStatesSHA256']
z = np.load(OUT/'matched-states.npz', allow_pickle=False)
assert np.array_equal(z['matchedTimesSeconds'], s['matchedTimesSeconds'])
for c in s['cases']:
    states = z[c['name']]
    x = z[c['grid']+'-x']
    assert states.shape == (8, len(x)+1)
    assert np.all(np.isfinite(states)) and np.min(states) >= 0
    assert np.max(np.abs(np.sum(states, axis=1)-c['capacity'])) <= 2e-12
    measured = states[:, :-1]@(1+x)/s['parameters']['beta']
    assert np.max(np.abs(measured-c['matchedForces'])) <= 1e-12
    assert c['acceptedTimeSeconds'] == 1. and c['acceptedSteps']*c['dt'] == 1.
    assert c['allStepMassErrorMax'] <= 2e-12 and c['allStepMinimumPopulation'] >= 0
    assert c['terminalKineticResidualL1PerSecond'] <= 1e-10
    assert c['terminalForceDifferenceFromOriginalEquilibrium'] <= 1e-10
    assert c['boundary']['momentIdentityError'] <= 1e-12
    if c['dt'] == .001:
        assert c['normalizedTemporalForceError'] <= .05
for g in s['grids']:
    assert g['equilibriumResidualL1PerSecond'] <= 1e-10
    assert g['exponentialMassErrorMax'] <= 2e-12 and g['exponentialMinimumPopulation'] >= -2e-14
    if g['dx'] == .01:
        assert g['equilibriumForceErrorRelative'] <= 1e-4
assert s['refinements']['maxMatchedExtentForceDifference'] <= 1e-8
r = json.loads((OUT/'render-receipt.json').read_text())
assert sha(ROOT/'tools/two_state_kinetic_figure.py') == r['rendererSHA256']
for p, h in {**r['inputs'], **r['outputs']}.items():
    assert sha(ROOT/p) == h, p
d = json.loads((OUT/'matched-space-diagnostic.json').read_text())
assert sha(ROOT/'tools/two_state_matched_space.py') == d['rendererOrAnalysisSHA256']
for p, h in d['sourceHashes'].items():
    assert sha(ROOT/p) == h, p
audit = json.loads((OUT/'independent-audit.json').read_text())
assert audit['result'].startswith('PASS'), audit['result']
for p, h in audit['sourceHashes'].items():
    assert sha(ROOT/p) == h, p
changed = subprocess.check_output(['git','diff','--name-only','8741bba2134ea51e9138061a0ebc0b6ba5e9a1b3'], cwd=ROOT, text=True).splitlines()
assert all(p.startswith(('education/tools/', 'education/research/', 'education/data/anatomical-arm-v1/review/')) for p in changed), changed
subprocess.run(['git','merge-base','--is-ancestor','08f5f3b7fd4b987d3f049c13fdf4338bfaa2928e','HEAD'], cwd=ROOT, check=True)
print(json.dumps(dict(result='PASS_BOUNDED_KINETIC_EVIDENCE_CLOSURE', manifestBindings=len(m['sha256']),
                     acceptedCases=144, matchedStateArchivePass=True, independentNumericalAuditPass=True,
                     sourceExecutionCommitPreserved=True, originalEvidenceAndProtectedScopeUntouched=True,
                     limitations='Source-derived normalized equation fixture with disclosed PDF/table/code parity limits; no published-history, physiological, descending, spatial-continuum or arm qualification.'), indent=2))
