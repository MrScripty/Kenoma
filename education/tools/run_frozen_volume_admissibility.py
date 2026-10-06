"""One frozen coarse 1.25 diagnostic with 1.01 control; no nonlinear solve."""
import hashlib
import json
import subprocess
import time
import traceback
from pathlib import Path

import numpy as np

from frozen_pressure_spaces import ROOT, FrozenOperator, replay
from frozen_volume_kernel import maps, restrict, volume_metrics, REFERENCE_SINGULAR_TOLERANCE
from source_amplitude_p2_p1 import digest
from run_full_p2_p1 import serial

OLD = ROOT/'data/anatomical-arm-v1/review/frozen-pressure-space-comparison'
OUT = ROOT/'data/anatomical-arm-v1/review/frozen-volume-admissibility'
SOURCES = ['tools/frozen_volume_kernel.py', 'tools/volume-admissibility-replay.mjs',
           'tools/run_frozen_volume_admissibility.py', 'tests/test_frozen_volume_kernel.py',
           'research/mechanical-closure/frozen-volume-admissibility-protocol.md',
           'tools/frozen_pressure_spaces.py', 'tools/frozen-pressure-replay.mjs',
           'tools/full_p2_p1.py', 'tools/source_amplitude_p2_p1.py', 'tools/run_full_p2_p1.py',
           'web/anatomical-material.mjs', 'web/anatomical-modal.mjs', 'web/anatomical-element.mjs',
           'web/anatomical-intersections.mjs', 'tools/anatomical-compression-quadrature.mjs']


def read(path):
    return json.loads(path.read_text())


def save(name, data):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT/name).open('x') as f:
        json.dump(serial(data), f, indent=2, allow_nan=False); f.write('\n')


def volume_replay(B, x, v, depth):
    data = dict(mesh=B.m, positionsM=x, direction=v, material=B.material, activation=B.activation, depth=depth)
    process = subprocess.run(['node',str(ROOT/'tools/volume-admissibility-replay.mjs')], input=json.dumps(serial(data)),
                             text=True,capture_output=True,check=True)
    return json.loads(process.stdout)


def derivative_checks(B, x, state, v, Z=None):
    free = B.m['free']; vf = v.ravel()[free]; Hv = state['H']@vf
    projected = None if Z is None else Z.T@Hv
    checks = []
    for h in [1e-7,5e-8]:
        gradients = []; energies = []; sides = []
        for sign in [1,-1]:
            probe = x+sign*h*v; s = B.evaluate(probe); q = replay(B,probe,s)
            gradients.append(np.array(q['gradientN'])[free]); energies.append(q['energyJ'])
            error = float(np.max(abs(s['g']-q['gradientN'])))
            gates = dict(assembly=error<=2e-6, energyReplay=abs(q['energyJ']-s['energy'])<=1e-12,
                         originalGeometryBand=.98<=q['Jmin']<=q['Jmax']<=1.02,
                         strictCrossings=q['surface']['crossingPairs']==0,
                         exactHeldCaps=bool(np.array_equal(probe[B.m['cap']],x[B.m['cap']])))
            sides.append(dict(sign=sign,maximumIndependentForceDifferenceN=error,gates=gates,passed=all(gates.values()),
                              independentOriginalReplay=q,
                              scope='Straight-line derivative probe; kernel imposed at base only; no exact nonlinear-volume path or state advancement'))
        fd=(gradients[0]-gradients[1])/(2*h)
        relative=float(np.linalg.norm(fd-Hv)/np.linalg.norm(Hv))
        p_relative=None if Z is None else float(np.linalg.norm(Z.T@fd-projected)/np.linalg.norm(projected))
        energy_error=float(abs((energies[0]-energies[1])/(2*h)-state['g']@v.ravel()))
        checks.append(dict(stepM=h,fullGradientActionRelativeError=relative,
                           kernelProjectedGradientActionRelativeError=p_relative,
                           independentDirectionalRayleighNPerM=float(vf@fd),
                           directionalRayleighDifferenceNPerM=float(vf@(fd-Hv)),
                           independentEnergyGradientDifferenceN=energy_error,sides=sides,
                           passed=bool(relative<=1e-4 and (p_relative is None or p_relative<=1e-4)
                                       and energy_error<=1e-6 and all(s['passed'] for s in sides))))
    return checks


def witness_record(B, state, x, v, T, Q, Z=None):
    vf=v.ravel()[B.m['free']]; Hv=state['H']@vf
    decomposition=B.decomposition(state,v); metrics=volume_metrics(B,state,x,v,T,Q)
    original=replay(B,x,state,direction=v)
    original_Hv=np.array(original['tangentActionNPerM'])[B.m['free']]
    base_gates=dict(force=original['freeNodalResidualN']<=1e-4,
                    assembly=float(np.max(abs(state['g']-original['gradientN'])))<=2e-6,
                    energyReplay=abs(state['energy']-original['energyJ'])<=1e-12,
                    localPressure=original['pointwisePressureRMS']<=1e-6,
                    reactionWork=abs(original['capForceN']-original['virtualForceN'])<=1e-3,
                    geometry=.98<=original['Jmin']<=original['Jmax']<=1.02,
                    strictCrossings=original['surface']['crossingPairs']==0)
    observations={str(4*8**d):volume_replay(B,x,v,d) for d in [1,2]}
    record=dict(direction=v,metrics=metrics,completePhysicalRayleigh=decomposition,
                directMatrixRayleighNPerM=float(vf@Hv),firstVariationN=float(state['g']@v.ravel()),
                independentOriginalTangentActionRelativeError=float(np.linalg.norm(original_Hv-Hv)/np.linalg.norm(Hv)),
                independentOriginalDirectionalRayleighNPerM=float(vf@original_Hv),
                baseGates=base_gates,baseGatesPass=all(base_gates.values()),baseOriginalReplay=original,
                independentVolumeAndConstituentReplays=observations,
                derivativeChecks=derivative_checks(B,x,state,v,Z))
    record['derivativeGatesPass']=all(c['passed'] for c in record['derivativeChecks'])
    if Z is not None:
        record['projectedOriginalTangentActionRelativeError']=float(np.linalg.norm(Z.T@(original_Hv-Hv))/np.linalg.norm(Z.T@Hv))
    return record


def main():
    if (OUT/'summary.json').exists() or list(OUT.glob('*-request.json')):
        raise RuntimeError('Preserve previous diagnostic')
    start=time.time();source={n:digest(ROOT/n) for n in SOURCES}
    commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    previous={str(p.relative_to(ROOT)):digest(p) for label in ['source-amplitude-p2-p1','source-amplitude-p2-p1-v2','pressure-residual-diagnosis','frozen-pressure-space-comparison']
              for p in (ROOT/'data/anatomical-arm-v1/review'/label).rglob('*') if p.is_file()}
    archived=read(OLD/'coarse-mesh.json')['mesh']
    m={k:np.array(v) if isinstance(v,list) else v for k,v in archived.items()}
    save('coarse-mesh.json',dict(mesh=m,originalMeshSHA256=digest(OLD/'coarse-mesh.json')))
    summaries=[]
    for stretch in [1.25,1.01]:
        name=f'coarse-{stretch:.2f}';old=read(OLD/(name+'-assembled.json'));req=read(OLD/(name+'-request.json'))
        qualified=read(OLD/(name+'-pointwise.json'))
        assert qualified['baseChecks']['originalStationarityGatesPass'] and qualified['derivativeGatesPass']
        x=np.array(old['positionsM']);material=req['material'];activation=req['activation']
        save(name+'-request.json',dict(sourceCommit=commit,sourceHashes=source,previousPacketHashes=previous,
             archivedPointwiseReceiptSHA256=digest(OLD/(name+'-pointwise.json')),
             material=material,activation=activation,positionsM=x,stretch=stretch,
             relativeSingularCutoff=REFERENCE_SINGULAR_TOLERANCE,fullBlockNonlinearSolves=0,
             scope='Coarse qualified affine field only; first-order volume kernel, unchanged physical finite-K law; fine1.25 excluded'))
        print('START',name,flush=True)
        B=FrozenOperator(m,'pointwise',material=material,activation=activation);state=B.evaluate(x,True)
        broken=FrozenOperator(m,'brokenP1',material=material,activation=activation);bstate=broken.evaluate(x)
        T,Q,D=maps(B,state,broken,bstate);kernel=restrict(state['H'],T,Q)
        v=np.zeros(x.size);v[m['free']]=kernel['lowestFreeDirection'];v=v.reshape(x.shape)
        unconstrained=np.array(old['operators']['pointwise']['lowestWitness'])
        save(name+'-kernel-assembled.json',dict(positionsM=x,kernel=kernel,momentMapRMSNormalized=T,
             brokenMomentMapD=D,directPointwiseMapShape=Q.shape,directPointwiseVolumeGram=Q.T@Q,
             constrainedDirection=v,archivedFiniteKDirection=unconstrained,
             finiteKPhysicalHessianSHA256=hashlib.sha256(state['H'].tobytes()).hexdigest(),
             baseForceResidualN=state['residual'],baseEnergyJ=state['energy'],baseJmin=state['Jmin'],baseJmax=state['Jmax'],
             disposition='FROZEN_LINEARIZED_ADMISSIBILITY_DIAGNOSTIC_ONLY'))
        constrained=witness_record(B,state,x,v,T,Q,kernel['basis'])
        constrained['classification']=('CONSTRAINED_NEGATIVE_DIRECTION' if kernel['fullRestrictedEigenvaluesNPerM'][0]<0
            else 'POSITIVE_SAMPLED_RESTRICTED_SPECTRUM') if constrained['baseGatesPass'] and constrained['derivativeGatesPass'] else 'UNQUALIFIED_DIRECTION_CHECK_FAILURE'
        save(name+'-constrained.json',constrained)
        finite=witness_record(B,state,x,unconstrained,T,Q)
        finite.update(archivedLowestEigenvalueNPerM=old['operators']['pointwise']['fullPhysicalEigenvaluesNPerM'][0],
                      scope='Preserved finite-K unconstrained witness; explicitly not pointwise volume-admissible when delta logJ is nonzero')
        save(name+'-finite-K-unconstrained.json',finite)
        summaries.append(dict(name=name,rank=kernel['rank'],momentRows=kernel['rowCount'],rowRedundancy=kernel['redundantRowCount'],
             freeDisplacementCount=kernel['freeDisplacementCount'],kernelDimension=kernel['displacementKernelDimension'],
             lowestRestrictedEigenvalueNPerM=kernel['fullRestrictedEigenvaluesNPerM'][0],
             negativeRestrictedEigenvalueCount=int((kernel['fullRestrictedEigenvaluesNPerM']<0).sum()),
             constrainedClassification=constrained['classification'],constrainedVolumeRMSPerM=constrained['metrics']['directionalLogJRMSPerM'],
             finiteKUnconstrainedRayleighNPerM=finite['directMatrixRayleighNPerM'],
             finiteKUnconstrainedVolumeRMSPerM=finite['metrics']['directionalLogJRMSPerM'],
             constrainedDerivativeGatesPass=constrained['derivativeGatesPass'],unconstrainedDerivativeGatesPass=finite['derivativeGatesPass']))
        print('RESULT',name,json.dumps(serial(summaries[-1])),flush=True)
    assert all(digest(ROOT/n)==h for n,h in previous.items())
    save('summary.json',dict(result='COMPLETED_SINGLE_COARSE_VOLUME_ADMISSIBILITY_DIAGNOSTIC',sourceCommit=commit,sourceHashes=source,
         cases=summaries,previousPacketHashesUnchanged=True,previousPacketFileCount=len(previous),elapsedSeconds=time.time()-start,
         fullBlockNonlinearSolves=0,stabilizationParameters=0,coefficientChanges=0,physicalHistoryAdvanced=False,
         fine125Excluded=True,pressureNullModesRepaired=False,
         limits=['Kernel is first-order volume preservation at the finite-K affine base, not an exact nonlinear incompressible trajectory.',
                'Positive restriction cannot erase unconstrained finite-K negative curvature or justify raising K.',
                'Row redundancy handled only for displacement-kernel representation; pressure null modes remain unchanged.',
                'No fine1.25 qualification, anatomy, locking or nonlinear convergence inference.']))
    print('COMPLETE',time.time()-start,flush=True)


if __name__=='__main__':
    try:
        main()
    except Exception:
        if not (OUT/'unexpected-failure.json').exists():
            save('unexpected-failure.json',dict(result='EXCEPTION_NO_ADVANCEMENT',traceback=traceback.format_exc()))
        raise
