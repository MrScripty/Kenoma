"""Four affine frozen-field comparisons; no nonlinear solve, no overwrites."""
import hashlib
import json
import subprocess
import time
import traceback
from pathlib import Path

import numpy as np
from scipy.linalg import cho_solve, eigh

from frozen_pressure_spaces import ROOT, SPACES, FrozenOperator, replay
from source_amplitude_p2_p1 import ExplicitBody, ANCHOR, digest, model
from run_full_p2_p1 import serial

OUT = ROOT/'data/anatomical-arm-v1/review/frozen-pressure-space-comparison'
SOURCES = ['tools/frozen_pressure_spaces.py', 'tools/frozen-pressure-replay.mjs', 'tools/run_frozen_pressure_spaces.py',
           'tests/test_frozen_pressure_spaces.py', 'research/mechanical-closure/frozen-pressure-space-protocol.md',
           'tools/full_p2_p1.py', 'tools/source_amplitude_p2_p1.py', 'tools/run_full_p2_p1.py',
           'web/anatomical-material.mjs', 'web/anatomical-modal.mjs', 'web/anatomical-element.mjs',
           'web/anatomical-intersections.mjs', 'tools/anatomical-compression-quadrature.mjs']


def save(name, data):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT/name).open('x') as f:
        json.dump(serial(data), f, indent=2, allow_nan=False); f.write('\n')


def weak_rms(body, values):
    if body.space == 'pointwise':
        return 0.
    w = np.array(values)
    return float(np.sqrt(max(0, w@cho_solve(body.Mfactor, w)/body.volume)))


def comparisons(left, right):
    return dict(energyDifferenceJ=left['energy']-right['energy'],
                maximumForceDifferenceN=float(np.max(abs(left['g']-right['g']))),
                maximumPressureSampleDifferencePa=float(np.max(abs(left['pq']-right['pq']))),
                maximumTangentEntryDifferenceNPerM=float(np.max(abs(left['H']-right['H']))),
                tangentFrobeniusRelativeDifference=float(np.linalg.norm(left['H']-right['H'])/np.linalg.norm(right['H'])))


def base_checks(B, x, state, analytic, witness):
    checks = [dict(name='Python full force', passed=state['residual'] <= 1e-4),
              dict(name='Python weak pressure', passed=state['weakRMS'] <= 1e-6),
              dict(name='Python pointwise pressure', passed=state['pointwiseRMS'] <= 1e-6),
              dict(name='finite coordinates', passed=bool(np.isfinite(x).all())),
              dict(name='exact held caps', passed=bool(np.array_equal(x[B.m['cap']], B.heldCaps)))]
    replays = {}
    Hv = state['H']@witness.ravel()[B.m['free']]
    for depth in [1, 2]:
        q = replay(B, x, state, depth, witness)
        mass = B if depth == 2 else FrozenOperator(B.m, B.space, depth)
        q['weakPressureRMS'] = weak_rms(mass, q['weak'])
        q['directionalWeakPressureRMSPerM'] = weak_rms(mass, q['deltaWeak'])
        q['maximumGradientDifferenceN'] = float(np.max(abs(state['g']-q['gradientN'])))
        q['energyDifferenceFromPythonJ'] = q['energyJ']-state['energy']
        q['tangentActionRelativeDifference'] = float(np.linalg.norm(np.array(q['tangentActionNPerM'])[B.m['free']]-Hv)/np.linalg.norm(Hv))
        q['massLocalMaximumDifferenceM3'] = float(np.max(abs(np.array(q['massLocal']).reshape(B.Mlocal.shape)-B.Mlocal)))
        q['analyticCapForceRelativeError'] = abs(q['capForceN']-analytic['capForceN'])/abs(analytic['capForceN'])
        for name, passed in [
            ('full force', q['freeNodalResidualN'] <= 1e-4), ('assembly', q['maximumGradientDifferenceN'] <= 2e-6),
            ('energy replay', abs(q['energyDifferenceFromPythonJ']) <= 1e-12),
            ('reaction/work', abs(q['capForceN']-q['virtualForceN']) <= 1e-3),
            ('weak pressure', q['weakPressureRMS'] <= 1e-6), ('pointwise pressure', q['pointwisePressureRMS'] <= 1e-6),
            ('geometry band', .98 <= q['Jmin'] <= q['Jmax'] <= 1.02),
            ('strict boundary crossings', q['surface']['crossingPairs'] == 0),
            ('analytic reaction', q['analyticCapForceRelativeError'] <= .01)]:
            checks.append(dict(name=f'{4*8**depth} points: {name}', passed=bool(passed)))
        replays[str(4*8**depth)] = q
    return dict(gates=checks, replays=replays, originalStationarityGatesPass=all(c['passed'] for c in checks),
                pointwiseWeakScope='IDENTITY_WITH_NO_FINITE_PRESSURE_EQUATION' if B.space == 'pointwise' else 'FINITE_PRESSURE_MASS_NORM')


def derivative_checks(B, x, state, v):
    free = B.m['free']; Hv = state['H']@v.ravel()[free]
    output = []
    for h in [1e-7, 5e-8]:
        gradients = []; energies = []; sides = []
        for sign in [1, -1]:
            probe = x+sign*h*v; s = B.evaluate(probe)
            q = replay(B, probe, s)
            gradients.append(np.array(q['gradientN'])[free]); energies.append(q['energyJ'])
            error = float(np.max(abs(s['g']-q['gradientN'])))
            weak = weak_rms(B, q['weak'])
            side_gates = dict(assembly=error <= 2e-6, weakPressure=weak <= 1e-6,
                              finitePositiveGeometry=bool(np.isfinite(probe).all() and q['Jmin'] > 1e-6),
                              originalGeometryBand=.98 <= q['Jmin'] <= q['Jmax'] <= 1.02,
                              exactHeldCaps=bool(np.array_equal(probe[B.m['cap']], B.heldCaps)),
                              strictBoundaryCrossings=q['surface']['crossingPairs'] == 0,
                              energyReplay=abs(q['energyJ']-s['energy']) <= 1e-12)
            sides.append(dict(sign=sign, maximumIndependentForceDifferenceN=error, weakPressureRMS=weak,
                              pointwisePressureScope='DIAGNOSTIC_NONSTATIONARY_PROBE; BASE_GATE_UNCHANGED',
                              probePressurePa=None if B.space == 'pointwise' else s['p'],
                              independentReplay=q, gates=side_gates, passed=all(side_gates.values())))
        fd = (gradients[0]-gradients[1])/(2*h)
        relative = float(np.linalg.norm(fd-Hv)/np.linalg.norm(Hv))
        energy_gradient_error = float(abs((energies[0]-energies[1])/(2*h)-state['g']@v.ravel()))
        output.append(dict(stepM=h, independentGradientRelativeError=relative,
                           independentEnergyGradientDifferenceN=energy_gradient_error, sides=sides,
                           passed=bool(relative <= 1e-4 and energy_gradient_error <= 1e-6 and all(s['passed'] for s in sides))))
    return output


def main():
    if list(OUT.glob('*-request.json')) or (OUT/'summary.json').exists():
        raise RuntimeError('Preserve previous execution')
    start = time.time(); hashes = {name:digest(ROOT/name) for name in SOURCES}
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    prior = {str(p.relative_to(ROOT)):digest(p) for label in ['source-amplitude-p2-p1', 'source-amplitude-p2-p1-v2', 'pressure-residual-diagnosis']
             for p in (ROOT/'data/anatomical-arm-v1/review'/label).rglob('*') if p.is_file()}
    summaries = []
    for level, mesh_path in [('coarse', ROOT/'data/anatomical-arm-v1/review/source-amplitude-p2-p1/coarse-mesh.json'),
                             ('fine', ROOT/'data/anatomical-arm-v1/review/source-amplitude-p2-p1-v2/fine-mesh.json')]:
        m = json.loads(mesh_path.read_text())['mesh']
        m = {k:np.array(v) if isinstance(v, list) else v for k,v in m.items()}
        save(level+'-mesh.json', dict(mesh=m, originalMeshSHA256=digest(mesh_path), sourceCommit=commit))
        for stretch in [1.01, 1.25]:
            name = f'{level}-{stretch:.2f}'
            x, analytic = ExplicitBody(m, ANCHOR, 1.).analytic(stretch)
            save(name+'-request.json', dict(sourceCommit=commit, sourceHashes=hashes, previousPacketHashes=prior,
                 material=ANCHOR, activation=1., stretch=stretch, positionsM=x, analytic=analytic,
                 pressureSpaces=SPACES, baseQuadraturePoints=256, independentReplayPoints=[32,256],
                 nonlinearSolves=0, stabilizationParameters=0, physicalHistoryAdvanced=False))
            print('START', name, flush=True)
            bodies = {space:FrozenOperator(m, space) for space in SPACES}
            states = {}; eigs = {}; witnesses = {}; assembled = {}
            for space, B in bodies.items():
                B.heldCaps = x[m['cap']].copy(); r = B.evaluate(x, True); states[space] = r
                eigen, vectors = eigh(r['H']); eigs[space] = eigen
                v = np.zeros(x.size); v[m['free']] = vectors[:,0]; v = v.reshape(x.shape); witnesses[space] = v
                assembled[space] = dict(energyJ=r['energy'], fullGradientN=r['g'], pressurePa=r['p'],
                    forceResidualN=r['residual'], weakPressureRMS=r['weakRMS'], pointwisePressureRMS=r['pointwiseRMS'],
                    Jmin=r['Jmin'], Jmax=r['Jmax'], meanVolumeChange=r['meanVolumeChange'], localVolumeRMS=r['localVolumeRMS'],
                    fullPhysicalEigenvaluesNPerM=eigen, lowestWitness=v,
                    tangentShape=r['H'].shape, tangentArraySHA256=hashlib.sha256(r['H'].tobytes()).hexdigest())
            save(name+'-assembled.json', dict(positionsM=x, operators=assembled, disposition='FROZEN_FIELDS_ONLY_NO_ACCEPTED_HISTORY'))
            print('ASSEMBLED', name, flush=True)
            records = {}
            for space, B in bodies.items():
                r = states[space]; v = witnesses[space]; eigen = eigs[space]
                record = dict(pressureCoupling=B.coupling(r), lowestModeDecomposition=B.decomposition(r,v),
                              baseChecks=base_checks(B,x,r,analytic,v), derivativeChecks=derivative_checks(B,x,r,v))
                record['derivativeGatesPass'] = all(c['passed'] for c in record['derivativeChecks'])
                record['lowestEigenvalueNPerM'] = float(eigen[0]); record['negativeEigenvalueCount'] = int((eigen < 0).sum())
                record['rayleighEigenDifferenceNPerM'] = record['lowestModeDecomposition']['totalNPerM']-float(eigen[0])
                record['classification'] = ('NEGATIVE_FROZEN_STATIONARY_DIRECTION' if eigen[0] < 0 else 'POSITIVE_FROZEN_FULL_SPECTRUM') \
                    if record['baseChecks']['originalStationarityGatesPass'] and record['derivativeGatesPass'] else 'UNQUALIFIED_OPERATOR_CHECK_FAILURE'
                record['crossOperatorRayleigh'] = {s:bodies[s].decomposition(states[s],v) for s in SPACES}
                save(name+'-'+space+'.json', record); records[space] = record
                print('CHECKED', name, space, record['classification'], 'rank', record['pressureCoupling']['rank'],
                      '/', record['pressureCoupling']['pressureCount'], 'lambda', float(eigen[0]), flush=True)
            compare = {a+'-'+b:comparisons(states[a],states[b]) for a,b in [('brokenP1','pointwise'),('continuousP1','pointwise'),('continuousP1','brokenP1')]}
            save(name+'-comparison.json', dict(comparisons=compare, sourceHashes=hashes,
                 interpretation='Affine base identity only; independent original pointwise energy/force/tangent action and two-step derivatives retained'))
            summaries.append(dict(name=name, comparisons=compare, operators={s:dict(
                 energyJ=states[s]['energy'], forceResidualN=states[s]['residual'], pointwisePressureRMS=states[s]['pointwiseRMS'],
                 lowestEigenvalueNPerM=records[s]['lowestEigenvalueNPerM'], negativeEigenvalueCount=records[s]['negativeEigenvalueCount'],
                 pressureCount=records[s]['pressureCoupling']['pressureCount'], rank=records[s]['pressureCoupling']['rank'],
                 nullity=records[s]['pressureCoupling']['nullity'], betaIncludingNulls=records[s]['pressureCoupling']['betaIncludingNulls'],
                 smallestPositiveBeta=records[s]['pressureCoupling']['smallestPositiveBeta'],
                 originalStationarityGatesPass=records[s]['baseChecks']['originalStationarityGatesPass'],
                 derivativeGatesPass=records[s]['derivativeGatesPass'], classification=records[s]['classification']) for s in SPACES}))
    assert all(digest(ROOT/name)==value for name,value in prior.items())
    save('summary.json', dict(result='COMPLETED_FROZEN_OPERATOR_COMPARISON', sourceCommit=commit, sourceHashes=hashes,
         cases=summaries, elapsedSeconds=time.time()-start, priorPacketHashesUnchanged=True, priorPacketFileCount=len(prior),
         nonlinearSolves=0, stabilizationParameters=0, physicalHistoryAdvanced=False,
         limitations=['Affine operator identity does not establish nonaffine equivalence, incompressible inf-sup stability, locking freedom, nonlinear convergence or anatomy.',
                     'Negative curvature and pressure nulls are retained; no pressure null mode or gauge removed.',
                     'Euclidean nodal spectra are mesh dependent; geometry and boundary checks retain original sampled/triangulated limitations.']))
    print('COMPLETE', 'elapsed', time.time()-start, flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        if not (OUT/'unexpected-failure.json').exists():
            save('unexpected-failure.json', dict(result='EXCEPTION_NO_ADVANCEMENT', traceback=traceback.format_exc()))
        raise
