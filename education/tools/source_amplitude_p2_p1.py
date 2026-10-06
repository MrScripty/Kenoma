"""Explicit-activation comparator of existing P2/P1 equations; research only."""
import contextlib
import hashlib
import json
import subprocess
import traceback
from pathlib import Path

import numpy as np
from scipy.linalg import cho_solve, eigh

import full_p2_p1 as model
from run_full_p2_p1 import coupling, interpolate, serial

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/anatomical-arm-v1/review/source-amplitude-p2-p1'
BASE = dict(model.PARAM)
ANCHOR = dict(BASE, sigma0=155000.)
ORIGINAL_CONSTITUTIVE = model.constitutive


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@contextlib.contextmanager
def parameters(material):
    previous = dict(model.PARAM)
    model.PARAM.clear()
    model.PARAM.update(material)
    try:
        yield
    finally:
        model.PARAM.clear()
        model.PARAM.update(previous)


class ExplicitBody(model.Body):
    """Retain original evaluate/newton; add exact explicit-activation differences."""
    def __init__(self, mesh, material, activation, depth=2):
        super().__init__(mesh, depth)
        self.material = dict(material)
        self.activation = float(activation)
        self.latest = None

    def evaluate(self, x, hessian=False):
        with parameters(self.material):
            result = super().evaluate(x, hessian)
            F = np.einsum('eni,eqna->eqia', x[self.m['tets']], self.grad)
            p = result['p'][self.pi] @ self.L.T
            desired = ORIGINAL_CONSTITUTIVE(F, p, activation=self.activation, tangent=hessian)
            original = ORIGINAL_CONSTITUTIVE(F, p, activation=model.ACTIVATION, tangent=hessian)
            change = np.einsum('eqia,eqna,eq->eni', desired[0]-original[0], self.grad, self.w).reshape(-1, 30)
            np.add.at(result['g'], self.di, change)
            result['residual'] = float(np.linalg.norm(result['g'][self.m['free']]))
            result['energy'] += float(np.sum((desired[2]-original[2])*self.w))
            if hessian:
                local = np.array([np.einsum('qna,qiajb,qmb,q->nimj', self.grad[e], desired[1][e]-original[1][e],
                                          self.grad[e], self.w[e], optimize=True).reshape(30, 30)
                                  for e in range(len(F))])
                change = self.assemble(local, self.di, self.di, x.size, x.size)
                free = self.m['free']
                result['H'] += change[free][:, free].toarray()
        self.latest = dict(positionsM=x.copy(), pressurePa=result['p'].copy(), forceResidualN=result['residual'],
                           label='LATEST_EVALUATED_TRIAL; NOT_ACCEPTED_HISTORY')
        return result

    def analytic(self, stretch):
        with parameters(self.material):
            x, reference = super().analytic(stretch)
            s = reference['transverseStretch']
            F = np.diag([stretch, s, s])[None]
            P = ORIGINAL_CONSTITUTIVE(F, np.array([reference['pressurePa']]), activation=self.activation)[0][0]
            reference['capForceN'] = float(P[0, 0]*model.LENGTHS[1]*model.LENGTHS[2])
        return x, reference


def save(name, data):
    with (OUT/name).open('x') as handle:
        json.dump(serial(data), handle, indent=2, allow_nan=False)
        handle.write('\n')


def node(body, x, pressure, depth=2):
    data = dict(mesh=body.m, positionsM=x, pressurePa=pressure, material=body.material,
                activation=body.activation, depth=depth)
    command = ['node', str(ROOT/'tools/full-p2-p1-replay.mjs')]
    process = subprocess.run(command, input=json.dumps(serial(data)), text=True, capture_output=True)
    if process.returncode:
        raise RuntimeError(f'Original Node replay failed ({process.returncode}): {process.stderr}')
    return json.loads(process.stdout)


def gate(name, value):
    return dict(name=name, passed=bool(value))


def stationarity(body, x, state, initial, analytic):
    replays, gates = {}, [gate('Python full force', state['residual'] <= 1e-4),
                         gate('finite coordinates', np.isfinite(x).all()),
                         gate('exact held caps', np.array_equal(x[body.m['cap']], initial[body.m['cap']]))]
    for depth in [1, 2]:
        q = node(body, x, state['p'], depth)
        mass = body if depth == 2 else model.Body(body.m, depth)
        weak = np.array(q['weak'])
        q['weakPressureRMS'] = float(np.sqrt(max(0, weak @ cho_solve(mass.Mfactor, weak)/mass.volume)))
        q['maximumGradientDifferenceN'] = float(np.max(abs(state['g']-q['gradientN'])))
        q['analyticCapForceRelativeError'] = abs(q['capForceN']-analytic['capForceN'])/max(abs(analytic['capForceN']), 1e-300)
        replays[str(4*8**depth)] = q
        for name, passed in [
            ('full force', q['freeNodalResidualN'] <= 1e-4), ('assembly', q['maximumGradientDifferenceN'] <= 2e-6),
            ('reaction/work', abs(q['capForceN']-q['virtualForceN']) <= 1e-3),
            ('weak pressure', q['weakPressureRMS'] <= 1e-6), ('pointwise pressure', q['pointwisePressureRMS'] <= 1e-6),
            ('geometry band', .98 <= q['Jmin'] <= q['Jmax'] <= 1.02),
            ('strict boundary crossings', q['surface']['crossingPairs'] == 0),
            ('analytic reaction', q['analyticCapForceRelativeError'] <= .01)]:
            gates.append(gate(f'{4*8**depth} points: {name}', passed))
    return replays, gates


def spectrum(body, x, state):
    free = body.m['free']
    eigen, vectors = eigh(state['H'], subset_by_index=[0, 2])
    vector = vectors[:, 0]
    witness = np.zeros(x.size)
    witness[free] = vector
    witness = witness.reshape(x.shape)
    Hv = state['H'] @ vector
    checks = []
    for h in [1e-7, 5e-8]:
        gradients, sides = [], []
        for sign in [1, -1]:
            probe = x+sign*h*witness
            r = body.evaluate(probe)
            q = node(body, probe, r['p'])
            weak = np.array(q['weak'])
            weak_rms = float(np.sqrt(max(0, weak @ cho_solve(body.Mfactor, weak)/body.volume)))
            error = float(np.max(abs(r['g']-q['gradientN'])))
            side = dict(sign=sign, maximumAssemblyDifferenceN=error, weakPressureRMS=weak_rms,
                        pointwisePressureRMS=q['pointwisePressureRMS'], Jmin=q['Jmin'], Jmax=q['Jmax'],
                        strictCrossings=q['surface']['crossingPairs'])
            side['passed'] = bool(error <= 2e-6 and weak_rms <= 1e-6 and q['pointwisePressureRMS'] <= 1e-6
                                  and .98 <= q['Jmin'] <= q['Jmax'] <= 1.02 and side['strictCrossings'] == 0)
            sides.append(side)
            gradients.append(np.array(q['gradientN'])[free])
        relative = float(np.linalg.norm((gradients[0]-gradients[1])/(2*h)-Hv)/np.linalg.norm(Hv))
        checks.append(dict(stepM=h, independentGradientRelativeError=relative,
                           passed=bool(relative <= 1e-4 and all(s['passed'] for s in sides)), sides=sides))
    passed = all(c['passed'] for c in checks)
    return dict(lowestEigenvaluesNPerM=eigen, witnessDirection=witness, firstVariationN=float(state['g'] @ witness.ravel()),
                gradientChecks=checks, derivativeGatesPass=passed,
                classification=('NEGATIVE_STATIONARY_DIRECTION' if eigen[0] < 0 else 'POSITIVE_SAMPLED_FULL_SPECTRUM')
                               if passed else 'UNQUALIFIED_DERIVATIVE_FAILURE',
                convention='Euclidean nodal normalization; no continuum spectral-convergence claim')


def case(level, mesh, stretch, hashes, commit):
    name = f'{level}-{stretch:.2f}'
    body = ExplicitBody(mesh, ANCHOR, 1.)
    initial, _, analytic = body.initial(stretch)
    save(name+'-request.json', dict(sourceCommit=commit, sourceHashes=hashes, name=name,
                                  material=ANCHOR, activation=1., initialPositionsM=initial, analytic=analytic,
                                  maxIterations=80, backtracking=24, physicalHistoryAdvanced=False))
    print('START', name, 'activation', body.activation, 'sigma0', ANCHOR['sigma0'], flush=True)
    try:
        x, state, history, reason = body.newton(initial)
        replays, gates = stationarity(body, x, state, initial, analytic)
        accepted = all(g['passed'] for g in gates)
        curve = spectrum(body, x, state) if accepted else None
        derivative = bool(curve is not None and curve['derivativeGatesPass'])
        passive = None
        if accepted:
            control = ExplicitBody(mesh, ANCHOR, 0.)
            pr = control.evaluate(x, True)
            _, pa = control.analytic(stretch)
            pq, pg = stationarity(control, x, pr, initial, pa)
            ok = all(g['passed'] for g in pg)
            ps = spectrum(control, x, pr) if ok else None
            passive = dict(activation=0., samePositions=True, forceResidualN=pr['residual'], stationarityGates=pg,
                           stationaryAccepted=ok, replays=pq, spectrum=ps)
        record = dict(sourceCommit=commit, sourceHashes=hashes, name=name, material=ANCHOR, activation=1.,
                      stretch=stretch, initialPositionsM=initial, terminalPositionsM=x, terminalPressurePa=state['p'],
                      history=history, reason=reason, analytic=analytic, stationarityGates=gates, stationaryAccepted=accepted,
                      derivativeGatesPass=derivative, fineEligible=bool(accepted and derivative), replays=replays, spectrum=curve,
                      terminal=dict(forceResidualN=state['residual'], fullGradientN=state['g'], energyJ=state['energy'],
                                    weakPressureRMS=state['weakRMS'], pointwisePressureRMS=state['pointwiseRMS'],
                                    Jmin=state['Jmin'], Jmax=state['Jmax']),
                      coupling=coupling(body, state) if accepted else None, passiveControl=passive,
                      result='PASS_STATIONARY_DERIVATIVE_GATES' if accepted and derivative else 'REJECTED_GATES_NO_ADVANCEMENT',
                      physicalHistoryAdvanced=False)
        save(name+'.json', record)
        print('RESULT', name, record['result'], 'residual', state['residual'], 'curvature', None if curve is None else curve['classification'],
              'minimum', None if curve is None else curve['lowestEigenvaluesNPerM'][0], flush=True)
        return record
    except Exception:
        record = dict(sourceCommit=commit, sourceHashes=hashes, name=name, result='EXCEPTION_NO_ADVANCEMENT',
                      initialPositionsM=initial, latestEvaluatedTrial=body.latest, traceback=traceback.format_exc(),
                      stationaryAccepted=False, derivativeGatesPass=False, fineEligible=False, physicalHistoryAdvanced=False)
        save(name+'-failure.json', record)
        print('FAILURE', name, record['traceback'], flush=True)
        return record


def equivalence(hashes, commit):
    old_path = ROOT/'data/anatomical-arm-v1/review/full-p2-p1/coarse-1.25.json'
    old = json.loads(old_path.read_text())
    mesh = json.loads((old_path.parent/'coarse-mesh.json').read_text())['mesh']
    mesh = {k: np.array(v) if isinstance(v, list) else v for k, v in mesh.items()}
    x = np.array(old['terminalPositionsM'])
    alpha = BASE['sigma0']*.01
    a = alpha/ANCHOR['sigma0']
    original = ExplicitBody(mesh, BASE, .01)
    matched = ExplicitBody(mesh, ANCHOR, a)
    r, s = original.evaluate(x, True), matched.evaluate(x, True)
    F = np.einsum('eni,eqna->eqia', x[mesh['tets']], original.grad)
    p = r['p'][original.pi] @ original.L.T
    with parameters(BASE):
        pc = ORIGINAL_CONSTITUTIVE(F, p, activation=.01, tangent=True)
    with parameters(ANCHOR):
        qc = ORIGINAL_CONSTITUTIVE(F, p, activation=a, tangent=True)
    errors = {name: float(np.linalg.norm(left-right)/max(1., np.linalg.norm(left)))
              for name, left, right in [('stress', pc[0], qc[0]), ('tangent', pc[1], qc[1]), ('nonvolumeEnergy', pc[2], qc[2]),
                                       ('gradient', r['g'], s['g']), ('condensedHessian', r['H'], s['H'])]}
    _, original_analytic = original.analytic(1.25)
    _, matched_analytic = matched.analytic(1.25)
    original_replays, original_gates = stationarity(original, x, r, x, original_analytic)
    matched_replays, matched_gates = stationarity(matched, x, s, x, matched_analytic)
    original_node, matched_node = original_replays['256'], matched_replays['256']
    witness = np.array(old['spectrum']['witnessDirection']).ravel()[mesh['free']]
    values = [float(witness @ z['H'] @ witness) for z in [r, s]]
    checks = [gate('direct and assembled equivalence', max(errors.values()) <= 1e-12),
              gate('admissible matched activation', 0 <= a <= 1), gate('negative old witness retained', max(values) < 0),
              gate('original and matched force gate', max(r['residual'], s['residual'], original_node['freeNodalResidualN'], matched_node['freeNodalResidualN']) <= 1e-4),
              gate('independent original assembly', max(abs(r['g']-original_node['gradientN'])) <= 2e-6),
              gate('independent matched assembly', max(abs(s['g']-matched_node['gradientN'])) <= 2e-6),
              gate('original stationary replay gates', all(g['passed'] for g in original_gates)),
              gate('matched stationary replay gates', all(g['passed'] for g in matched_gates))]
    output = dict(sourceCommit=commit, sourceHashes=hashes, preservedReceiptSHA256=digest(old_path), alphaPa=alpha,
                  originalSigma0Pa=BASE['sigma0'], originalActivation=.01, matchedSigma0Pa=ANCHOR['sigma0'], matchedActivation=a,
                  relativeErrors=errors, originalWitnessRayleighNPerM=values, gates=checks,
                  result='PASS_EQUIVALENCE_NEGATIVE_WITNESS_RETAINED' if all(c['passed'] for c in checks) else 'FAIL_EQUIVALENCE_CONTROL',
                  originalReplay=original_replays, matchedReplay=matched_replays, originalStationarityGates=original_gates,
                  matchedStationarityGates=matched_gates, originalForceResidualN=r['residual'], matchedForceResidualN=s['residual'],
                  physicalHistoryAdvanced=False, interpretation='Peak relabeling at matched alpha changes no law; full-activation run is a separate amplitude experiment')
    save('equivalence-control.json', output)
    print('EQUIVALENCE', output['result'], 'matched activation', a, 'Rayleigh', values, flush=True)
    return output


def main():
    if (OUT/'summary.json').exists() or list(OUT.glob('*-request.json')):
        raise RuntimeError('Preserve earlier execution; output already exists')
    source = ['tools/source_amplitude_p2_p1.py', 'tools/full_p2_p1.py', 'tools/run_full_p2_p1.py',
              'tools/full-p2-p1-replay.mjs', 'web/anatomical-material.mjs', 'web/anatomical-modal.mjs',
              'web/anatomical-element.mjs', 'web/anatomical-intersections.mjs', 'tools/anatomical-compression-quadrature.mjs',
              'research/mechanical-closure/source-amplitude-p2-p1-protocol.md',
              'data/anatomical-arm-v1/review/source-amplitude-p2-p1/primary-source-binding.json']
    hashes = {name: digest(ROOT/name) for name in source}
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    control = equivalence(hashes, commit)
    records, meshes, skips = {}, {}, []
    for level, counts in [('coarse', (4, 1, 1)), ('fine', (8, 2, 2))]:
        eligible = [s for s in [1.01, 1.25] if level == 'coarse' or records[f'coarse-{s:.2f}']['fineEligible']]
        for stretch in [1.01, 1.25]:
            if stretch not in eligible:
                skips.append(dict(name=f'fine-{stretch:.2f}', reason='Coarse stationarity/derivative gates failed'))
        if not eligible:
            continue
        meshes[level] = model.mesh(counts)
        save(level+'-mesh.json', dict(sourceHashes=hashes, sourceCommit=commit, mesh=meshes[level]))
        for stretch in eligible:
            records[f'{level}-{stretch:.2f}'] = case(level, meshes[level], stretch, hashes, commit)
    refinement = []
    for stretch in [1.01, 1.25]:
        coarse = records[f'coarse-{stretch:.2f}']
        fine = records.get(f'fine-{stretch:.2f}')
        if fine is None or not fine['fineEligible']:
            refinement.append(dict(stretch=stretch, result='UNQUALIFIED_NO_ACCEPTED_FINE_PAIR'))
            continue
        positions = interpolate(meshes['coarse'], np.array(coarse['terminalPositionsM']), meshes['fine']['X'])
        difference = float(np.linalg.norm(positions-np.array(fine['terminalPositionsM']), axis=1).max())
        reaction = abs(coarse['replays']['256']['capForceN']-fine['replays']['256']['capForceN'])/abs(fine['replays']['256']['capForceN'])
        j = max(abs(coarse['terminal'][key]-fine['terminal'][key]) for key in ['Jmin', 'Jmax'])
        ratio = fine['coupling']['beta']/coarse['coupling']['beta']
        refinement.append(dict(stretch=stretch, maximumInterpolatedPositionDifferenceM=difference, relativeCapForceDifference=reaction,
                               JExtremaDifference=j, infSupBetaRatio=ratio, infSupTrendConcern=ratio < .5,
                               matchedStaticRefinementPass=bool(difference <= .0005 and reaction <= .01 and j <= .005)))
    summaries = [dict(name=name, result=r['result'], stationaryAccepted=r['stationaryAccepted'], derivativeGatesPass=r['derivativeGatesPass'],
                      forceResidualN=r.get('terminal', {}).get('forceResidualN'), capForceN=r.get('replays', {}).get('256', {}).get('capForceN'),
                      Jmin=r.get('terminal', {}).get('Jmin'), Jmax=r.get('terminal', {}).get('Jmax'),
                      curvatureClassification=None if r.get('spectrum') is None else r['spectrum']['classification'],
                      minimumEigenvalueNPerM=None if r.get('spectrum') is None else float(r['spectrum']['lowestEigenvaluesNPerM'][0]),
                      passiveStationary=None if r.get('passiveControl') is None else r['passiveControl']['stationaryAccepted'],
                      passiveMinimumNPerM=None if r.get('passiveControl') is None or r['passiveControl']['spectrum'] is None else float(r['passiveControl']['spectrum']['lowestEigenvaluesNPerM'][0]))
                 for name, r in records.items()]
    save('summary.json', dict(sourceCommit=commit, sourceHashes=hashes, cases=summaries, refinement=refinement, skipped=skips,
                             equivalenceResult=control['result'], physicalHistoryAdvanced=False,
                             scope='COMPOSITE_EDUCATIONAL_STATIC_AMPLITUDE_ONLY; NO_SPECIMEN_ARM_OR_CLINICAL_VALIDATION'))
    print('COMPLETE', json.dumps(serial(summaries)), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        if OUT.is_dir() and not (OUT/'unexpected-run-failure.json').exists():
            save('unexpected-run-failure.json', dict(result='EXCEPTION_NO_ADVANCEMENT', traceback=traceback.format_exc(), physicalHistoryAdvanced=False))
        raise
