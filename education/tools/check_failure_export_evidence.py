"""Read-only preservation checks of the fixed intentional rejection tests."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/anatomical-arm-v1/review/conserved-ce-failure-export'
m=json.loads((OUT/'hash-manifest.json').read_text())
for row in m['files']:
    p=ROOT/row['path']
    assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],row['path']
s=json.loads((OUT/'test-summary.json').read_text())
assert s['result']=='PASS_INTENTIONAL_FAILURE_EXPORT_TESTS' and not s['unexpectedFailures']
assert len(s['tests'])==2 and all(t['passed'] for t in s['tests'])
assert s['noRetries'] and s['noFullPacketRerun']
for t,steps,clock,prefix in zip(s['tests'],[249,50],[.996,.2],[10,7]):
    assert t['acceptedSteps']==steps and t['lastAdmittedTimeSeconds']==clock and t['matchedPrefixCount']==prefix
assert s['tests'][0]['counts']==dict(operatorCalls=250,injections=1)
assert s['tests'][1]['counts']==dict(operatorCalls=50,injections=2)
print(json.dumps(dict(result='PASS_FAILURE_EXPORT_EVIDENCE_CLOSURE',manifestBindings=len(m['files']),
                     intentionalDiagnosticRejections=2,physicalModelFailures=0,noRetriesOrGateChanges=True)))
