"""Independent audit of archived two-state states; no source-fiber/arm replay.

Reconstructs cell rates with erfc, a star generator and its reversible symmetric
similarity, then checks all archived exact and BE states spectrally. Tests the
source implementation's one-step solve, declared boundary map and rejections.
Prints a source-pinned JSON receipt without altering any input.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
from scipy.integrate import quad
from scipy.linalg import eigh, solve
from scipy.special import erf, erfc

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/anatomical-arm-v1/review/two-state-kinetics'
PARAM = dict(f1=52., g1=4., g2=21.1, E1=2., E2=-.6, w=.3,
             beta=.5, nH=3.1, Ca50M=.83e-6)
TIMES = np.array([0., .008, .02, .04, .1, .2, .5, 1.])
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def cell_rates(edges):
    z = edges / (.3 * np.sqrt(2))
    lo, hi = z[:-1], z[1:]
    values = np.empty(len(lo))
    positive, negative = lo >= 0, hi <= 0
    crossing = ~(positive | negative)
    values[positive] = .5 * (erfc(lo[positive]) - erfc(hi[positive]))
    values[negative] = .5 * (erfc(-hi[negative]) - erfc(-lo[negative]))
    values[crossing] = .5 * (erf(hi[crossing]) - erf(lo[crossing]))
    return 52 * values


def transport_matrix(x, dx, delta):
    count = len(x)
    r = abs(delta) / dx
    T = np.diag(np.r_[np.full(count, 1-r), 1.])
    if delta > 0:
        T[np.arange(1, count), np.arange(count-1)] = r
        T[-1, count-1] = r
        edge, escaped_center = count-1, x[-1] + dx
    else:
        T[np.arange(count-1), np.arange(1, count)] = r
        T[-1, 0] = r
        edge, escaped_center = 0, x[0] - dx
    return T, edge, escaped_center


def main():
    summary = json.loads((OUT / 'summary.json').read_text())
    assert summary['result'] == 'PASS_FIXED_CAPACITY_KINETIC_TRANSPORT_BENCHMARK'
    assert summary['parameters'] == PARAM
    assert len(summary['cases']) == 144 and len(summary['grids']) == 6
    for name, digest in summary['sourceHashes'].items():
        assert sha(ROOT / name) == digest, name
    assert sha(OUT / 'matched-states.npz') == summary['matchedStatesSHA256']
    archive = np.load(OUT / 'matched-states.npz')
    assert np.array_equal(archive['matchedTimesSeconds'], TIMES)
    assert len(archive.files) == 175
    spec = importlib.util.spec_from_file_location('two_state_subject', ROOT / 'tools/two_state_kinetics.py')
    subject = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(subject)
    assert subject.PARAM == PARAM

    f = lambda x: 52 * np.exp(-x*x/(2*.3**2)) / (np.sqrt(2*np.pi)*.3)
    g = lambda x: 4*np.exp(-2*x) + 21.1*np.exp(.6*x)
    I, ie = quad(lambda x: f(x)/g(x), -8, 8, epsabs=1e-12, epsrel=1e-12)
    J, je = quad(lambda x: x*f(x)/g(x), -8, 8, epsabs=1e-12, epsrel=1e-12)
    continuous_force = (I+J) / ((1+I)*.5)
    maximum = {key: 0. for key in ['cellRateAbsoluteDifference', 'generatorColumnSum',
               'detailedBalanceAbsoluteResidual', 'generatorSimilarityDifference',
               'equilibriumStateDifference', 'exponentialStateDifference',
               'exponentialForceDifference', 'spectralBEMatchedStateDifference',
               'spectralBEMatchedForceDifference', 'archivedMatchedMassError',
               'terminalResidualL1PerSecond', 'terminalForceDifference',
               'recordedScalarDifference', 'boundaryIdentityError',
               'directImplicitSolveDifference']}
    minimum_matched, minimum_spectral, largest_eigenvalue = np.inf, np.inf, -np.inf
    grids, cases, synthetic, rejections = [], [], [], []
    by_case = {}
    for row in summary['grids']:
        name, radius, dx = row['name'], row['radius'], row['dx']
        bins = round(2*radius/dx)
        edges = np.linspace(-radius, radius, bins+1)
        x = (edges[1:]+edges[:-1])/2
        Fi, gi = cell_rates(edges), g(x)
        assert np.array_equal(x, archive[name+'-x'])
        assert np.all(Fi > 0) and np.all(gi > 0)
        maximum['cellRateAbsoluteDifference'] = max(maximum['cellRateAbsoluteDifference'],
                                                    float(np.max(abs(Fi-archive[name+'-Fi']))))
        assert np.max(abs(Fi-archive[name+'-Fi'])) < 1e-13
        assert np.max(abs(gi-archive[name+'-gi'])) < 1e-12
        eq_d = 1/(1+np.sum(Fi/gi))
        equilibrium = np.r_[eq_d*Fi/gi, eq_d]
        maximum['equilibriumStateDifference'] = max(maximum['equilibriumStateDifference'],
                          float(np.max(abs(equilibrium-archive[name+'-equilibrium-N1']))))
        flux = Fi*equilibrium[-1]-gi*equilibrium[:-1]
        maximum['detailedBalanceAbsoluteResidual'] = max(maximum['detailedBalanceAbsoluteResidual'],
                                                         float(np.max(abs(flux))))
        A = np.diag(np.r_[-gi, -np.sum(Fi)])
        A[:-1, -1], A[-1, :-1] = Fi, gi
        off_diagonal = A.copy()
        np.fill_diagonal(off_diagonal, 0.)
        assert np.all(off_diagonal >= 0)
        column_error = float(np.max(abs(np.sum(A, axis=0))))
        maximum['generatorColumnSum'] = max(maximum['generatorColumnSum'], column_error)
        assert column_error < 1e-12
        # Construct the symmetric generator directly from detailed balance.
        S = np.diag(np.r_[-gi, -np.sum(Fi)])
        S[:-1, -1] = S[-1, :-1] = np.sqrt(Fi*gi)
        root_eq = np.sqrt(equilibrium)
        similarity = A * root_eq[None, :] / root_eq[:, None]
        maximum['generatorSimilarityDifference'] = max(maximum['generatorSimilarityDifference'],
                                                        float(np.max(abs(S-similarity))))
        eigenvalues, vectors = eigh(S)
        largest_eigenvalue = max(largest_eigenvalue, float(eigenvalues[-1]))
        assert eigenvalues[-1] <= 1e-10
        assert eigenvalues[-2] < 0
        shifted = []
        for delta in [.001, -.001, .0005, -.0005]:
            T, edge, center = transport_matrix(x, dx, delta)
            assert np.all(T >= 0) and np.max(abs(np.sum(T, axis=0)-1)) < 1e-14
            shifted.append(T @ equilibrium)
        shifted = np.array(shifted)
        coordinates = vectors.T @ (shifted.T / root_eq[:, None])

        def spectral_states(factors):
            return (root_eq[:, None] * (vectors @ (factors[:, None]*coordinates))).T

        exact = np.array([spectral_states(np.exp(t*eigenvalues)) for t in TIMES])
        persisted_exact = archive[name+'-exponential-N1']
        exact_diff = float(np.max(abs(exact-persisted_exact)))
        exact_force_diff = float(np.max(abs((exact-persisted_exact)[..., :-1] @ (1+x)/.5)))
        maximum['exponentialStateDifference'] = max(maximum['exponentialStateDifference'], exact_diff)
        maximum['exponentialForceDifference'] = max(maximum['exponentialForceDifference'], exact_force_diff)
        minimum_spectral = min(minimum_spectral, float(np.min(exact)))
        assert exact_diff <= 2e-12 and exact_force_diff <= 2e-12
        exact_mass_error = float(np.max(abs(np.sum(exact, axis=2)-1)))
        assert exact_mass_error <= 2e-12 and np.min(exact) >= -2e-14
        baseline = float(equilibrium[:-1] @ (1+x)/.5)
        spatial_error = abs(baseline-continuous_force)/abs(continuous_force)
        grids.append(dict(name=name, bins=bins, spatialRelativeForceError=spatial_error,
                          independentExactMassError=exact_mass_error,
                          independentExactMinimumPopulation=float(np.min(exact)),
                          independentExactStateDifference=exact_diff,
                          largestSymmetricEigenvalue=float(eigenvalues[-1]),
                          slowestNonzeroEigenvalue=float(eigenvalues[-2])))
        for c in [case for case in summary['cases'] if case['grid'] == name]:
            N = 1/(1+(.83e-6/10**(-c['pCa']))**3.1)
            assert c['capacity'] == N and c['acceptedTimeSeconds'] == 1.
            assert c['acceptedSteps'] == round(1/c['dt'])
            j = [.001, -.001, .0005, -.0005].index(c['delta'])
            assert all(abs(round(t/c['dt'])*c['dt']-t) < 1e-13 for t in TIMES)
            # Rational powers are an independent solution of the full BE system.
            be = N*np.array([spectral_states((1-c['dt']*eigenvalues)**(-round(t/c['dt'])))
                             for t in TIMES])[:, j]
            states = archive[c['name']]
            assert states.shape == (8, bins+1)
            assert np.isfinite(states).all() and np.min(states) >= 0
            minimum_matched = min(minimum_matched, float(np.min(states)))
            state_difference = float(np.max(abs(be-states)))
            force_difference = float(np.max(abs((be-states)[:, :-1] @ (1+x)/.5)))
            maximum['spectralBEMatchedStateDifference'] = max(maximum['spectralBEMatchedStateDifference'], state_difference)
            maximum['spectralBEMatchedForceDifference'] = max(maximum['spectralBEMatchedForceDifference'], force_difference)
            assert state_difference <= 2e-12 and force_difference <= 2e-12
            mass_error = float(np.max(abs(np.sum(states, axis=1)-N)))
            maximum['archivedMatchedMassError'] = max(maximum['archivedMatchedMassError'], mass_error)
            assert mass_error <= 2e-12
            forces = states[:, :-1] @ (1+x)/.5
            reference_forces = N*exact[:, j, :-1] @ (1+x)/.5
            temporal_error = float(np.max(abs(forces-reference_forces)))
            normalized_error = temporal_error/(abs(c['delta'])*N/.5)
            terminal_flux = Fi*states[-1, -1]-gi*states[-1, :-1]
            residual = float(np.sum(abs(terminal_flux))+abs(np.sum(terminal_flux)))
            terminal_force_error = float(abs(forces[-1]-N*baseline))
            maximum['terminalResidualL1PerSecond'] = max(maximum['terminalResidualL1PerSecond'], residual)
            maximum['terminalForceDifference'] = max(maximum['terminalForceDifference'], terminal_force_error)
            assert residual <= 1e-10 and terminal_force_error <= 1e-10
            assert c['allStepMassErrorMax'] <= 2e-12 and c['allStepMinimumPopulation'] >= 0
            T, edge, center = transport_matrix(x, dx, c['delta'])
            escaped = abs(c['delta'])/dx*N*equilibrium[edge]
            lost_moment = escaped*(1+center)
            expected_fast = (N*np.sum(equilibrium[:-1])*c['delta']-lost_moment)/.5
            fast_error = abs(forces[0]-N*baseline-expected_fast)
            maximum['boundaryIdentityError'] = max(maximum['boundaryIdentityError'], float(fast_error))
            assert fast_error <= 1e-12 and escaped <= 1e-10 and abs(lost_moment/.5) <= 1e-10
            comparisons = [np.max(abs(forces-c['matchedForces'])),
                           np.max(abs(reference_forces-c['matchedReferenceForces'])),
                           abs(residual-c['terminalKineticResidualL1PerSecond']),
                           abs(terminal_force_error-c['terminalForceDifferenceFromOriginalEquilibrium']),
                           abs(temporal_error-c['maximumMatchedForceError']),
                           abs(escaped-c['boundary']['escapedMass']),
                           abs(lost_moment-c['boundary']['escapedDiscreteMoment'])]
            maximum['recordedScalarDifference'] = max(maximum['recordedScalarDifference'], float(max(comparisons)))
            assert max(comparisons) <= 2e-12
            if c['dt'] == .001:
                assert normalized_error <= .05
            cases.append(dict(name=c['name'], independentMaximumTemporalForceError=temporal_error,
                              independentNormalizedTemporalError=normalized_error,
                              independentSpectralBEStateDifference=state_difference))
            by_case[name, c['pCa'], c['delta'], c['dt']] = (temporal_error, forces)

        if name == 'R2.4-dx0.04':
            for dt in [.004, .002, .001]:
                y = shifted[0]
                direct = solve(np.eye(bins+1)-dt*A, y)
                actual = subject.backward_euler(y, 1., Fi, gi, dt)
                difference = float(np.max(abs(actual-direct)))
                maximum['directImplicitSolveDifference'] = max(maximum['directImplicitSolveDifference'], difference)
                assert difference <= 2e-12
            # A synthetic edge-heavy population exposes both boundary signs.
            edge_state = np.zeros(bins+1)
            edge_state[0], edge_state[-2], edge_state[bins//2], edge_state[-1] = .27, .31, .12, .30
            for delta in [.01, -.01]:
                T, edge, center = transport_matrix(x, dx, delta)
                actual, loss = subject.shift(edge_state, 1., x, dx, delta)
                expected = T @ edge_state
                escaped = abs(delta)/dx*edge_state[edge]
                moment = escaped*(1+center)
                increment = (np.sum(edge_state[:-1])*delta-moment)/.5
                assert np.max(abs(actual-expected)) <= 1e-14
                assert np.min(actual) >= 0 and abs(np.sum(actual)-1) <= 1e-14
                assert abs(loss['escapedMass']-escaped) <= 1e-14
                assert abs(loss['escapedDiscreteMoment']-moment) <= 1e-14
                assert abs((actual[:-1]-edge_state[:-1]) @ (1+x)/.5-increment) <= 1e-12
                synthetic.append(dict(delta=delta, escapedMass=escaped,
                                      escapedDiscreteMoment=moment, immediateForceIncrement=increment,
                                      minimumPopulation=float(np.min(actual)), massError=float(abs(np.sum(actual)-1))))
            invalid = []
            negative, nonfinite, mass_bad = equilibrium.copy(), equilibrium.copy(), equilibrium.copy()
            negative[0], nonfinite[0], mass_bad[-1] = -1e-6, np.nan, mass_bad[-1]+1e-6
            for label, bad in [('negative population', negative), ('nonfinite population', nonfinite), ('incorrect mass', mass_bad)]:
                invalid.append((label, lambda bad=bad: subject.backward_euler(bad, 1., Fi, gi, .001)))
            for invalid_capacity in [0., -1., 1.1, np.nan]:
                invalid.append((f'capacity {invalid_capacity}', lambda value=invalid_capacity: subject.validate(equilibrium, value)))
            for invalid_dt in [0., -.001, np.nan]:
                invalid.append((f'timestep {invalid_dt}', lambda value=invalid_dt: subject.backward_euler(equilibrium, 1., Fi, gi, value)))
            for invalid_delta in [0., dx, -dx, 2*dx, -2*dx, np.nan]:
                invalid.append((f'shift {invalid_delta}', lambda value=invalid_delta: subject.shift(equilibrium, 1., x, dx, value)))
            for label, action in invalid:
                try:
                    action()
                except ValueError as exc:
                    rejections.append(dict(input=label, result='REJECTED', reason=str(exc)))
                else:
                    raise AssertionError('invalid input accepted: '+label)

    temporal_ratios = []
    for row in summary['grids']:
        for pca in [4.5, 6.1]:
            for delta in [.001, -.001, .0005, -.0005]:
                errors = [by_case[row['name'], pca, delta, dt][0] for dt in [.004, .002, .001]]
                ratios = [errors[i+1]/errors[i] for i in [0, 1]]
                assert all(.3 <= ratio <= .8 for ratio, error in zip(ratios, errors) if error > 1e-12)
                temporal_ratios.extend(ratios)
    spatial_ratios = []
    for radius in [2.4, 3.0]:
        errors = [row['spatialRelativeForceError'] for row in grids if row['name'].startswith(f'R{radius:g}-')]
        ratios = [errors[i+1]/errors[i] for i in [0, 1]]
        assert all(.2 <= ratio <= .8 for ratio, error in zip(ratios, errors) if error > 1e-12)
        assert errors[-1] <= 1e-4
        spatial_ratios.extend(ratios)
    extent_difference = 0.
    for dx in [.04, .02, .01]:
        for pca in [4.5, 6.1]:
            for delta in [.001, -.001, .0005, -.0005]:
                for dt in [.004, .002, .001]:
                    a = by_case[f'R2.4-dx{dx:g}', pca, delta, dt][1]
                    b = by_case[f'R3-dx{dx:g}', pca, delta, dt][1]
                    extent_difference = max(extent_difference, float(np.max(abs(a-b))))
    assert extent_difference <= 1e-8
    # Diagnostic only: the predeclared spatial gate concerns equilibrium force.
    # Subtract each grid's own baseline to isolate transient strain-bin error.
    transient_spatial = []
    for radius in [2.4, 3.0]:
        incremental = []
        for dx in [.04, .02, .01]:
            name = f'R{radius:g}-dx{dx:g}'
            x = archive[name+'-x']
            baseline = archive[name+'-equilibrium-N1'][:-1] @ (1+x)/.5
            incremental.append(archive[name+'-exponential-N1'][..., :-1] @ (1+x)/.5-baseline)
        for pca in [4.5, 6.1]:
            N = 1/(1+(.83e-6/10**(-pca))**3.1)
            for j, delta in enumerate([.001, -.001, .0005, -.0005]):
                differences = [N*(incremental[i+1][:, j]-incremental[i][:, j]) for i in [0, 1]]
                errors = [float(np.max(abs(value))) for value in differences]
                transient_spatial.append(dict(radius=radius, pCa=pca, delta=delta,
                    coarseToHalfMatchedIncrementDifferences=differences[0].tolist(),
                    halfToFineMatchedIncrementDifferences=differences[1].tolist(),
                    maximumMatchedIncrementDifferences=errors, halvingDifferenceRatio=errors[1]/errors[0],
                    finestDifferenceNormalizedByDeltaCapacity=errors[1]/(abs(delta)*N/.5),
                    interpretation='Diagnostic exact-generator transient strain-bin refinement; no additional acceptance gate'))
    inputs = [Path(__file__), OUT/'summary.json', OUT/'matched-states.npz', OUT/'execute.log']
    inputs += [ROOT/name for name in summary['sourceHashes']]
    receipt = dict(result='PASS_INDEPENDENT_TWO_STATE_KINETIC_AUDIT',
                   sourceHashes={str(path.relative_to(ROOT)): sha(path) for path in inputs},
                   archivedCaseCount=len(cases), independentlyConstructedGridCount=len(grids),
                   independentMethod='Reversible symmetric eigensystem; exponential and rational BE powers; erfc cell integrals; direct implicit solve',
                   maxima=maximum, archivedMatchedMinimumPopulation=float(minimum_matched),
                   independentSpectralMinimumPopulation=float(minimum_spectral), largestGeneratorEigenvalue=float(largest_eigenvalue),
                   independentContinuousQuadrature=dict(I=I, xMoment=J, errors=[ie, je], baselineForceAtN1=continuous_force),
                   temporalRatiosRange=[min(temporal_ratios), max(temporal_ratios)],
                   spatialRatiosRange=[min(spatial_ratios), max(spatial_ratios)],
                   maximumMatchedExtentForceDifference=extent_difference,
                   transientSpatialDiagnostics=transient_spatial,
                   grids=grids, cases=cases, syntheticBoundaryTests=synthetic, invalidInputRejections=rejections,
                   sourceParity='Primary PDF extraction independently read; visual column alignment/source code parity not certified',
                   limits=['Archived matched states checked independently; all-step metrics additionally supported by source validation and positivity-safe formula.',
                           'Synthetic boundary loss is a declared discrete center-mass convention, not exact continuous tail force.',
                           'No source-fiber trajectory, cooperative/series model, descending branch, human coefficient or arm qualification.'])
    print(json.dumps(receipt, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
