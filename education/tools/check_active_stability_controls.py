"""Read-only closure of the bounded active mechanics packet; no solves."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/anatomical-arm-v1/review/active-stability-controls'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((OUT/'evidence-manifest.json').read_text())
for p,h in m['sha256'].items():assert sha(ROOT/p)==h,p
s=json.loads((OUT/'summary.json').read_text());assert len(s['cases'])==8
for p,h in s['sourceHashes'].items():assert sha(ROOT/p)==h,p
assert all(c['stationaryAccepted'] and c['derivativeChecksPass'] for c in s['cases'])
audit=json.loads((OUT/'independent-audit.json').read_text())
assert audit['result']=='PASS_INDEPENDENT_ACTIVE_CONTROLS_INTERNAL_AUDIT'
for p,h in audit['sourceHashes'].items():assert sha(ROOT/p)==h,p
for c in s['cases']:
 if c['name'].endswith('1.25'):
  assert (c['fullMinimumNPerM']<0)==(c['activation']==.01)
  assert (c['weakProjectedMinimumNPerM']<0)==(c['activation']==.01)
  assert (c['strictLocalMinimumPa']<0)==(c['activation']==.01)
mem=json.loads((OUT/'memory-stability-symbolic.json').read_text())
assert mem['result']=='PASS_PARAMETER_FREE_LINEAR_MEMORY_STABILITY_IDENTITY'
assert sha(ROOT/'tools/active_memory_stability.py')==mem['sourceSHA256']
failure=json.loads((OUT/'memory-stability-first-failure-receipt.json').read_text())
original=subprocess.check_output(['git','show',failure['sourceCommit']+':'+failure['sourceFile']],cwd=ROOT)
assert hashlib.sha256(original).hexdigest()==failure['sourceSHA256']
assert sha(OUT/'memory-stability-symbolic-first-failure.log')==failure['failureLogSHA256']
r=json.loads((OUT/'render-receipt.json').read_text());assert sha(ROOT/'tools/active_stability_figure.py')==r['rendererSHA256']
for p,h in {**r['inputs'],**r['outputs']}.items():assert sha(ROOT/p)==h,p
changed=subprocess.check_output(['git','diff','--name-only','97e645d3cef0d4fd6237bc4874cb085afa05d5c2'],cwd=ROOT,text=True).splitlines()
assert all(p.startswith(('education/tools/','education/research/','education/data/anatomical-arm-v1/review/')) for p in changed),changed
subprocess.run(['git','merge-base','--is-ancestor','08f5f3b7fd4b987d3f049c13fdf4338bfaa2928e','HEAD'],cwd=ROOT,check=True)
print(json.dumps(dict(result='PASS_ACTIVE_MECHANICS_BOUNDED_EVIDENCE_CLOSURE',manifestBindings=len(m['sha256']),
 eightStationaryControlsAndDerivativesPass=True,passiveIsolationPositive=True,activeDescendingWitnessesPreserved=True,
 weakPressureAndStrictLocalConstraintsDistinguished=True,independentAuditPass=True,symbolicFailureAndCorrectionPreserved=True,
 rendererSourceBound=True,productionBookLeanProtectedScopeUntouched=True,
 limitations='Instantaneous fixed-activation controls and parameter-free scalar thought experiment only; no physiological or anatomical/dynamic qualification.'),indent=2))
