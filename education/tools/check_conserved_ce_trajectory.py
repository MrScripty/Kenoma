"""Read-only closure; no kinetic/physical rerun and no changed acceptance gates."""
import hashlib
import json
import math
import subprocess
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/anatomical-arm-v1/review/conserved-ce-trajectory'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((OUT/'evidence-manifest.json').read_text())
for p,h in m['sha256'].items(): assert sha(ROOT/p)==h,p
s=json.loads((OUT/'summary.json').read_text())
a=json.loads((OUT/'independent-audit.json').read_text())
r=json.loads((OUT/'refinement-analysis.json').read_text())
d=np.load(OUT/'matched-states.npz',allow_pickle=False)
refs=np.load(OUT/'independent-reference.npz',allow_pickle=False)
assert s['result']=='PASS_CONSERVED_CE_HISTORY_GATES' and not s['failures']
assert a['result']=='PASS_INDEPENDENT_REFERENCE_AND_STRICT_POPULATION_GATES' and 'failure' not in a
assert r['result']=='ASSESS_MATCHED_TIME_AND_TRANSPORT_WORK'
assert len(s['cases'])==len(a['cases'])==len(r['temporal'])==144 and len(a['references'])==48
assert s['parameters']==dict(f1=52.,g1=4.,g2=21.1,E1=2.,E2=-.6,w=.3,beta=.5,nH=3.1,Ca50MicroM=.83)
assert np.array_equal(d['matchedTimesSeconds'],[0,0,.008,.02,.04,.1,.2,.2,.3,.5,1])
for p,h in s['sourceHashes'].items(): assert sha(ROOT/p)==h,p
assert sha(ROOT/'tools/audit_conserved_ce_trajectory.py')==a['auditSourceSHA256']
assert sha(OUT/'independent-reference.npz')==a['independentReferenceSHA256']
assert sha(OUT/'summary.json')==a['summarySHA256']
assert sha(OUT/'matched-states.npz')==a['matchedStatesSHA256']
assert a['solver']['method']=='DOP853' and a['solver']['maxStepsSeconds']==[.001,.0005]
assert a['solver']['rtol']==1e-11 and a['solver']['atol']==1e-14
for c in s['cases']:
    assert c['acceptedTimeSeconds']==1 and c['acceptedSteps']==round(1/c['dt'])
    assert c['initialKineticResidualL1PerSecond']<=1e-10 and c['terminalKineticResidualL1PerSecond']<=1e-10
    assert c['allStepNormalizedBEResidualMax']<=1e-12 and c['allStepMinimumPopulation']>=0
    N=1/(1+(.83/10**(6-c['pCa']))**3.1)
    assert c['N']==N and c['allStepMaximumB']<=N
    p=d[c['name']]; x=d[c['grid']+'_x']
    assert p.shape==(11,len(x)) and np.all(np.isfinite(p)) and np.min(p)>=0
    assert all(math.fsum(row)<=N for row in p)
    assert np.max(np.abs(p@(1+x)/.5-c['matchedForces']))<=2e-12
    for event in ['loading','reversal']:
        q=c[event]
        assert max(q['forceIdentityError'],q['energyIdentityError'],q['headAccountingError'])<=2e-12
        assert q['interpolationWork']>0
for q in a['references']:
    assert q['capacityAbsoluteDifference']<=2e-12
    assert q['resolutionStateL1Max']<=1e-10 and q['resolutionForceAbsoluteMax']<=2e-10
    for run in q['runs']:
        assert run['requestedTerminalSeconds']==1 and run['minimumMatchedPopulation']>=0
        p=refs[q['name']+f"-maxstep{run['maxStepSeconds']:g}"]
        assert p.shape[0]==11 and np.min(p)>=0 and all(math.fsum(row)<=q['N'] for row in p)
        for seg in run['segments']:
            assert seg['actualTerminalSeconds']==seg['requestedTerminalSeconds']
            assert seg['internalMinimumPopulation']>=0 and seg['internalMaximumB']<=q['N']
            shape=seg['acceptedStateArray']['shape']
            assert shape==[seg['internalAcceptedNodes'],p.shape[1]]
            assert seg['acceptedStateArray']['nbytes']==shape[0]*shape[1]*8
render=json.loads((OUT/'render-receipt.json').read_text())
assert sha(ROOT/'tools/analyze_conserved_ce_refinement.py')==render['analysisSourceSHA256']
for p,h in render['files'].items(): assert sha(OUT/p)==h
changed=subprocess.check_output(['git','diff','--name-only','7c8ec58ee8df051a387500b8555e9fac71b6569a'],cwd=ROOT,text=True).splitlines()
assert all(p.startswith(('education/research/','education/tools/','education/data/anatomical-arm-v1/review/')) for p in changed)
assert not any(p in changed for p in ['education/book/chapters/00-scope.md','education/tools/contact_trajectory_figure.py'])
print(json.dumps(dict(result='PASS_CONSERVED_CE_EVIDENCE_CLOSURE',manifestBindings=len(m['sha256']),
                     histories=144,referenceGroups=48,acceptedBESteps=sum(c['acceptedSteps'] for c in s['cases']),
                     requestedHorizonSeconds=1,continuousStrainTransientUnqualified=True,
                     interpolationWorkReported=True,seriesPhysicalAndAnatomicalQualification=False)))
