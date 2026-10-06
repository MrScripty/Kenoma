"""Read-only source/mapping closure and blocked-experiment scope evidence."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/anatomical-arm-v1/review/dimensional-contractile-mapping'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((OUT/'evidence-manifest.json').read_text())
for p,h in m['sha256'].items():
    assert sha(ROOT/p)==h,p
pin=json.loads((OUT/'source-repository-pin.json').read_text())
tree=json.loads((OUT/'source-tree-verification.json').read_text())
facts=json.loads((ROOT/'research/mechanical-closure/source-code-parameter-facts.json').read_text())
assert pin['commit']==tree['commit']==facts['commit']=='8c766dfb308051309193e7290ddd0bac3b726d11'
assert pin['tree']==tree['tree']==facts['tree']=='a802ec6f7299d0745dfab1d5b715a3d9b7aa6f20'
assert tree['truncated'] is False
by={f['path']:f for f in tree['files']}
assert by[facts['path']]['gitBlobSHA']==facts['git_blob_sha']
assert by[facts['path']]['bytes']==facts['bytes']==460311
for f in pin['files']:
    if f['bytes'] is not None:
        assert by[f['path']]['gitBlobSHA']==f['gitBlobSHA']
assert facts['redparms']['lce0']==0 and facts['redparms']['Fscale']==2
assert facts['redparms']['gamma']==130 and facts['additional_newparms']['h']==1.2e-8
assert facts['redparms']['K']==100 and facts['code_conventions']['fitting_PE_K']==1
assert facts['units']['physical_force_calibration'].startswith('UNRESOLVED')
assert facts['gates']['original_table_pixels']=='BLOCKED'
v=json.loads((ROOT/'data/anatomical-arm-v1/review/source-visual/visual-parameter-column-receipt.json').read_text())
assert v['visualInspectionCompleted'] is False
assert v['nextExperimentVisualPrerequisiteSatisfied'] is False
assert not v['verifiedPixelFiles'] and v['localOriginalPDFPath'] is None
bridge=json.loads((OUT/'symbolic-bridge.json').read_text())
assert bridge['result']=='PASS_SYMBOLIC_DIMENSIONAL_AND_SERIES_BRIDGE'
assert sha(ROOT/'tools/contractile_dimensional_bridge.py')==bridge['sourceSHA256']
for name in ['source-code-initialization-audit.md','dimensional-contractile-mapping.md']:
    b=(ROOT/'research/mechanical-closure'/name).read_bytes()
    assert b'\r' not in b,name
entry='116a26c12e7a477c0f5c455f0936108f4ffb1b12'
changed=subprocess.check_output(['git','diff','--name-only',entry],cwd=ROOT,text=True).splitlines()
assert all(p.startswith(('education/research/','education/tools/','education/data/anatomical-arm-v1/review/')) for p in changed),changed
assert not any(p in changed for p in ['education/book/chapters/00-scope.md','education/tools/contact_trajectory_figure.py'])
subprocess.run(['git','merge-base','--is-ancestor',entry,'HEAD'],cwd=ROOT,check=True)
print(json.dumps(dict(result='PASS_SOURCE_MAPPING_BLOCKER_EVIDENCE_CLOSURE',manifestBindings=len(m['sha256']),
                     sourceCommitAndTreePinned=True,individualFitBlobAndUnitsRecorded=True,
                     symbolicDimensionalBridgePass=True,sourceVisualPrerequisiteSatisfied=False,
                     coupledReleaseExecuted=False,oldKineticPacketAndProductionScopePreserved=True,
                     blockers=['Original parameter-column pixels unavailable','SI force/area calibration unresolved',
                               'Historical stroke/gamma and PE conventions require coherent version choice',
                               'Human overlap/fascicle/series and final-publication parity unqualified']),indent=2))
