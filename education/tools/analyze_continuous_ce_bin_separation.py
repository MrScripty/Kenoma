"""Separate preserved BE time error from bin-model error at matched times.

Read only previously accepted independent bin references and new continuous
receipts; no ODE/operator replay, density interpolation or new pass threshold.
"""
import hashlib
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT/'data/anatomical-arm-v1/review/conserved-ce-trajectory'
OUT = ROOT/'data/anatomical-arm-v1/review/continuous-strain-ce'


def main():
    audit = json.loads((OLD/'independent-audit.json').read_text())
    old = json.loads((OLD/'summary.json').read_text())
    subject = json.loads((OUT/'summary.json').read_text())
    assert audit['result'] == 'PASS_INDEPENDENT_REFERENCE_AND_STRICT_POPULATION_GATES'
    assert subject['result'] == 'PASS_CONTINUUM_QUADRATURE_TIME_AND_TRANSLATION_GATES'
    ref = np.load(OLD/'independent-reference.npz',allow_pickle=False)
    states = np.load(OLD/'matched-states.npz',allow_pickle=False)
    assert np.array_equal(ref['matchedTimesSeconds'],subject['matchedTimesSeconds'])
    grids = {g['name']:g for g in old['grids']}
    continuous = {(r['R'],r['pCa'],r['delta']):np.asarray(r['matchedMoments'])[:,1]
                  for r in subject['runs'] if r['count']==800 and r['maxStepSeconds']==.0005}
    rows=[]
    for q in audit['references']:
        grid=grids[q['grid']]
        x=states[q['grid']+'_x']
        p=ref[q['name']+'-maxstep0.0005']
        force=np.array([math.fsum(row*(1+x))/.5 for row in p])
        target=continuous[grid['R'],q['pCa'],q['delta']]
        denominator=abs(force[1]-force[0])
        net=(force-force[0])-(target-target[0])
        rows.append(dict(name=q['name'],R=grid['R'],dx=grid['dx'],pCa=q['pCa'],delta=q['delta'],
            signedMatchedForceResponseErrors=net.tolist(),
            maximumForceResponseError=float(np.max(np.abs(net))),
            ownInitialForceIncrement=float(denominator),
            relativeForceResponseError=float(np.max(np.abs(net))/denominator)))
    groups=[]
    for R in [2.4,3.]:
        for pca in [4.5,6.1]:
            for delta in [.001,-.001,.0005,-.0005]:
                errors=[next(q['relativeForceResponseError'] for q in rows
                             if (q['R'],q['pCa'],q['delta'],q['dx'])==(R,pca,delta,dx))
                        for dx in [.04,.02,.01]]
                groups.append(dict(R=R,pCa=pca,delta=delta,relativeForceResponseErrors=errors,
                    halvingRatios=[errors[1]/errors[0],errors[2]/errors[1]]))
    inputs=[OLD/'independent-audit.json',OLD/'independent-reference.npz',OLD/'matched-states.npz',OLD/'summary.json',OUT/'summary.json']
    result=dict(result='READ_ONLY_BIN_SPATIAL_ERROR_SEPARATION',
        analysisSourceSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        inputSHA256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        referencesCompared=len(rows),rows=rows,groups=groups,
        halvingRatioRange=[min(v for q in groups for v in q['halvingRatios']),max(v for q in groups for v in q['halvingRatios'])],
        R3RelativeResponseErrorRanges=[dict(dx=dx,range=[min(q['relativeForceResponseError'] for q in rows if q['R']==3 and q['dx']==dx),max(q['relativeForceResponseError'] for q in rows if q['R']==3 and q['dx']==dx)]) for dx in [.04,.02,.01]],
        normalization='Maximum baseline-subtracted force-response difference / bin reference own initial force increment',
        interpretation='Independent bin ODE reference removes BE time bias; combined BE+bin errors can cancel and need not decrease monotonically in every case',
        scope='Moment assessment only; no new pass threshold, common density L1 mapping, numerical replay or anatomical/physical qualification')
    with (OUT/'bin-spatial-separation.json').open('x') as handle:json.dump(result,handle,indent=2);handle.write('\n')
    print(json.dumps({k:result[k] for k in ['result','referencesCompared','halvingRatioRange','R3RelativeResponseErrorRanges']}))


if __name__=='__main__':
    main()
