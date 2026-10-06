#!/usr/bin/env python3
"""Read-only packet audit and independently scattered initial/response assembly."""
import json
from pathlib import Path

import numpy as np
from scipy.linalg import eigh

import full_p2_p1 as model
import matched_force_contractile_state as experiment
from source_amplitude_p2_p1 import ANCHOR, parameters


def main():
    out = experiment.OUT
    d = json.loads((out/'summary.json').read_text())
    assert d['result'] == 'PASS_BOUNDED_MATCHED_FORCE_COUPLING'
    assert len(d['runs']) == 24 and len(d['tangentChecks']) == 12
    assert len(d['checks']) == 480 and all(c['passed'] for c in d['checks'])
    assert not d['physicalHistoryAdvanced'] and not d['newODEIntegration'] and not d['newNonlinearSolve']
    for path, sha in d['sourceHashes'].items():
        assert experiment.digest(experiment.ROOT/path) == sha, path
    base = json.loads((experiment.REVIEW/'source-amplitude-p2-p1-v2/coarse-1.25-reclassification.json').read_text())
    mesh = json.loads((experiment.REVIEW/'source-amplitude-p2-p1/coarse-mesh.json').read_text())['mesh']
    mesh = {k: np.asarray(v) for k, v in mesh.items()}
    x = np.asarray(base['terminalPositionsM'])
    p = np.asarray(base['terminalPressurePa'])
    checks = []
    phi0 = d['sensitivity']['800']['phi0']
    for depth in [1, 2]:
        body = model.Body(mesh, depth)
        F = np.einsum('eni,eqna->eqia', x[mesh['tets']], body.grad)
        pq = p[body.pi]@body.L.T
        lam = np.linalg.norm(F[..., :, 0], axis=-1)
        n = F[..., :, 0]/lam[..., None]
        with parameters(ANCHOR):
            passive_P = model.constitutive(F, pq, activation=0.)[0]
        # Actual declared coupling, independently assembled without ExplicitBody's
        # algebraic active correction or a hardcoded zero-gradient-change assertion.
        density_phi = np.full(lam.shape, phi0)
        new_P = passive_P.copy()
        new_P[..., :, 0] += experiment.active_stress(lam, density_phi, phi0)[..., None]*n
        new_gradient = np.zeros(x.shape)
        for e, nodes in enumerate(mesh['tets']):
            for q in range(len(body.L)):
                new_gradient[nodes] += (body.grad[e, q]@new_P[e, q].T)*body.w[e, q]
        original = np.asarray(base['replays'][str(len(body.L))]['gradientN'])
        error = float(np.max(abs(new_gradient.ravel()-original)))
        residual = float(np.linalg.norm(new_gradient.ravel()[mesh['free']]))
        assert error <= 2e-6 and residual <= 1e-4
        J = np.linalg.det(F)
        assert .98 <= J.min() <= J.max() <= 1.02
        checks.append(dict(pointsPerTet=len(body.L), independentNewGradientVersusOriginalNodeMaximumN=error,
                           initialMatchedForceResidualN=residual, Jrange=[float(J.min()), float(J.max())]))
    # Independent GLOBAL row scattering / Gram product, unlike the local sparse
    # assembly in the experiment. Compare all seven endpoint operators.
    body = experiment.ExplicitBody(mesh, ANCHOR, 1.)
    state = body.evaluate(x, True)
    F = np.einsum('eni,eqna->eqia', x[mesh['tets']], body.grad)
    lam = np.linalg.norm(F[..., :, 0], axis=-1)
    direction = F[..., :, 0]/lam[..., None]
    rows = []
    for e, nodes in enumerate(mesh['tets']):
        for q in range(len(body.L)):
            row = np.zeros(x.shape)
            row[nodes] = body.grad[e, q, :, 0, None]*direction[e, q]
            rows.append(row.ravel()[mesh['free']])
    G = np.array(rows)
    v = np.asarray(base['spectrum']['witnessDirection']).ravel()[mesh['free']]
    records = []
    for i, response in enumerate(d['block']['responses']):
        sensitivity = d['sensitivity']['800']['sphi'][i] if i < 6 else 0.
        factor = (body.w*experiment.SIGMA*experiment.envelope(lam)*experiment.GAMMA*sensitivity/phi0).ravel()
        K = G.T@(factor[:, None]*G)
        operator = state['H']+K
        values = eigh(operator, subset_by_index=[0, 2], eigvals_only=True)
        eigen_error = float(np.max(abs(values-response['lowestSampledEigenvaluesNPerM'])))
        witness_error = abs(float(v@operator@v)-response['oldWitnessResponseNPerM'])
        assert eigen_error <= 1e-8 and witness_error <= 1e-8
        records.append(dict(timeSeconds=response['timeSeconds'], eigenvalueMaximumDifferenceNPerM=eigen_error,
                            witnessDifferenceNPerM=witness_error))
    refinement = []
    for count in [200, 400, 800]:
        for step in [.001, .0005]:
            cases = [t for t in d['tangentChecks'] if t['count'] == count and t['maxStepSeconds'] == step]
            coarse = next(t for t in cases if t['delta'] == .001)
            fine = next(t for t in cases if t['delta'] == .0005)
            refinement.append(dict(count=count, maxStepSeconds=step,
                coarseMaximumRelativeError=max(coarse['relativeErrors']),
                halfDisplacementMaximumRelativeError=max(fine['relativeErrors']),
                matchedTimeMaximumTangentDifferencePa=float(np.max(abs(np.array(coarse['finiteDifferencePa'])-fine['finiteDifferencePa'])))))
    report = dict(result='PASS_INDEPENDENT_MATCHED_FIELD_AND_OPERATOR_AUDIT', checksPassed=480,
                  immutableBindingsChecked=len(d['sourceHashes']), initialFieldChecks=checks,
                  independentlyScatteredOperatorChecks=records, displacementRefinement=refinement,
                  sourceSHA256=experiment.digest(Path(__file__)), summarySHA256=experiment.digest(out/'summary.json'))
    with (out/'independent-audit.json').open('x') as f:
        json.dump(report, f, indent=2)
        f.write('\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
