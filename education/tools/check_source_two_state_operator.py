"""Read-only closure of the conserved-head operator evidence; no rerun."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'data/anatomical-arm-v1/review/source-two-state-operator'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
m = json.loads((OUT/'evidence-manifest.json').read_text())
for p, h in m['sha256'].items():
    assert sha(ROOT/p) == h, p
r = json.loads((OUT/'independent-audit.json').read_text())
assert r['result'] == 'PASS_INDEPENDENT_SOURCE_TWO_STATE_OPERATOR'
assert r['counts'] == dict(cases=72, equilibria=10, auxiliary=6, invalidInputs=22, failures=0)
assert not r['failures']
for category in ['cases', 'equilibria', 'auxiliary', 'invalidInputs']:
    assert len(r[category]) == r['counts'][category]
    assert all(row['passed'] for row in r[category])
assert r['fixedGates']['retries'] == 0 and r['fixedGates']['referenceMaxSteps'] == 20
assert r['fixedGates']['populationBounds'] == 'strict p_i>=0 and fsum(p)<=N'
assert sha(ROOT/'tools/source_two_state_operator.py') == r['sourceSHA256']
assert sha(ROOT/'tools/audit_source_two_state_operator.py') == r['auditSourceSHA256']
assert sha(ROOT/'research/mechanical-closure/source-two-state-operator-protocol.md') == r['protocolSHA256']
print(json.dumps(dict(result='PASS_CONSERVED_OPERATOR_EVIDENCE_CLOSURE',
                      manifestBindings=len(m['sha256']), counts=r['counts'],
                      noPhysicalTrajectoryOrSICalibration=True)))
