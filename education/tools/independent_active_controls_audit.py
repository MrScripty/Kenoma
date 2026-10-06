"""Read-only independent checks of saved active-control evidence; no simulations.

Uses receipt data, constant-J directional energy algebra, a high-precision
traction-free branch reduction, and a separately constructed Maxwell operator.
Prints JSON; preserves all input receipts and imports no mechanics solver code.
"""
import hashlib
import json
from pathlib import Path
import subprocess

import mpmath as mp
import numpy as np
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/anatomical-arm-v1/review/active-stability-controls'
OLD = ROOT / 'data/anatomical-arm-v1/review/full-p2-p1'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    summary = json.loads((OUT / 'summary.json').read_text())
    for name, expected in summary['sourceHashes'].items():
        assert digest(ROOT / name) == expected, name
    paths = sorted(OUT.glob('case-*.json'))
    assert len(paths) == 8
    maxima = {k: 0. for k in ['forceResidualN', 'forceDifferenceN', 'weakRMS',
              'pointwisePressureRMS', 'reactionWorkMismatchN', 'fullDerivativeError',
              'localDerivativeError', 'axialDerivativeError', 'weakConstraint']}
    jlo, jhi, cap_max, det_change = 10., 0., 0., 0.
    worst_full = None
    pressure_dimensions = set()
    checked_inputs = [OUT / 'summary.json', OUT / 'memory-stability-symbolic.json']
    for path in paths:
        d = json.loads(path.read_text())
        prior_path = OLD / (d['name'] + '.json')
        mesh_path = OLD / (d['name'].split('-')[0] + '-mesh.json')
        checked_inputs.extend([path, prior_path, mesh_path])
        prior = json.loads(prior_path.read_text())
        mesh = json.loads(mesh_path.read_text())['mesh']
        assert digest(prior_path) == d['priorReceiptSHA256']
        assert np.array_equal(d['positionsM'], prior['terminalPositionsM'])
        assert d['stationaryAccepted'] and d['result'] == 'PASS_STATIONARY_ISOLATION'
        assert d['sourceHashes'] == summary['sourceHashes']
        for q in d['replays'].values():
            mismatch = abs(q['capForceN'] - q['virtualForceN'])
            for key, value in [('forceResidualN', q['freeNodalResidualN']),
                              ('forceDifferenceN', q['forceDifferenceN']),
                              ('weakRMS', q['weakRMS']),
                              ('pointwisePressureRMS', q['pointwisePressureRMS']),
                              ('reactionWorkMismatchN', mismatch)]:
                maxima[key] = max(maxima[key], value)
            assert q['freeNodalResidualN'] <= 1e-4
            assert q['forceDifferenceN'] <= 2e-6
            assert q['weakRMS'] <= 1e-6 and q['pointwisePressureRMS'] <= 1e-6
            assert mismatch <= 1e-3
            assert .98 <= q['Jmin'] <= q['Jmax'] <= 1.02
            assert q['surface']['crossingPairs'] == 0
            jlo, jhi = min(jlo, q['Jmin']), max(jhi, q['Jmax'])
        for category, key, label in [('spectrum', 'gradientChecks', 'fullDerivativeError'),
                                     ('local', 'derivativeChecks', 'localDerivativeError'),
                                     ('axial', 'finiteChecks', 'axialDerivativeError')]:
            for check in d[category][key]:
                assert check['passGate'] == (check['relativeError'] <= 1e-4)
                assert check['passGate']
                if check['relativeError'] > maxima[label]:
                    maxima[label] = check['relativeError']
                    if category == 'spectrum':
                        worst_full = dict(name=d['name'], activation=d['activation'], **check)
        projection = d['weakProjection']
        assert projection['constraintPass'] and projection['relativeConstraint'] <= 1e-12
        assert projection['freeCount'] - projection['rank'] == projection['nullDimension']
        maxima['weakConstraint'] = max(maxima['weakConstraint'], projection['relativeConstraint'])
        pressure_dimensions.add((projection['freeCount'], projection['rank'], projection['nullDimension']))
        for category in ['spectrum', 'weakProjection']:
            witness = np.array(d[category]['witness'])
            assert abs(np.linalg.norm(witness) - 1) < 1e-12
            cap_max = max(cap_max, float(np.max(abs(witness[mesh['cap']]))))
        F = np.array(d['local']['referenceF'])
        u, m = [np.array(d['local']['worst'][key]) for key in ['u', 'm']]
        assert abs(u @ np.linalg.inv(F).T @ m) < 1e-12
        assert abs(np.linalg.norm(u) - 1) < 1e-12 and abs(np.linalg.norm(m) - 1) < 1e-12
        for epsilon in [-.01, -.001, .001, .01]:
            det_change = max(det_change, abs(np.linalg.det(F + epsilon * np.outer(u, m)) - np.linalg.det(F)))
    assert cap_max == 0.

    # Independent energy reduction: J is constant on the admissible rank-one path.
    d = json.loads((OUT / 'case-coarse-1.25-a0.01.json').read_text())
    F = np.array(d['local']['referenceF'])
    lam, J = F[0, 0], np.linalg.det(F)
    u, m = [np.array(d['local']['worst'][key]) for key in ['u', 'm']]
    sigma = 8708387.370104775
    f = (1 - ((lam - 1) / .5)**2)**2
    fp = -4 * ((lam - 1) / .5) * (1 - ((lam - 1) / .5)**2) / .5
    kp, k = 20000 * np.exp(6 * (lam - 1)), 20000 / 6 * np.expm1(6 * (lam - 1))
    matrix = 1000 * J**(-2 / 3)
    passive = m[0]**2 * (kp * u[0]**2 + k / lam * (1 - u[0]**2))
    active = m[0]**2 * .01 * sigma * (fp * u[0]**2 + f / lam * (1 - u[0]**2))
    total = matrix + passive + active
    assert abs(total - d['local']['worst']['valuePa']) < 1e-8
    local = dict(matrixPa=float(matrix), passiveFiberPa=float(passive),
                 activeFiberPa=float(active), totalPa=float(total),
                 savedValuePa=d['local']['worst']['valuePa'])

    # Pyy=0 yields K log(lambda*s^2)=mu J^(-2/3)(lambda^2-s^2)/3.
    # Substitution into Pxx yields mu J^(-2/3)(lambda-s^2/lambda)+fiber force.
    mp.mp.dps = 50
    mu, bulk, sig = mp.mpf(1000), mp.mpf(10)**6, mp.mpf('8708387.370104775')
    area, length = mp.mpf('.0004'), mp.mpf('.14')

    def reaction(lam, activation):
        s = mp.findroot(lambda s: bulk * mp.log(lam * s * s)
                        - mu * (lam * s * s)**(-mp.mpf(2) / 3) * (lam * lam - s * s) / 3,
                        1 / mp.sqrt(lam))
        k = mp.mpf(20000) / 6 * mp.expm1(6 * (lam - 1))
        k += activation * sig * (1 - ((lam - 1) / mp.mpf('.5'))**2)**2
        return area * (mu * (lam * s * s)**(-mp.mpf(2) / 3) * (lam - s * s / lam) + k)

    axial = []
    for stretch in ['1.01', '1.25']:
        for activation in ['0.00', '0.01']:
            d = json.loads((OUT / f'case-coarse-{stretch}-a{activation}.json').read_text())
            slope = mp.diff(lambda lam: reaction(lam, mp.mpf(activation)), mp.mpf(stretch)) / length
            difference = float(slope) - d['axial']['axialDerivativeNPerM']
            assert abs(difference) < 1e-8
            axial.append(dict(stretch=stretch, activation=activation,
                              independentSlopeNPerM=mp.nstr(slope, 40),
                              savedSlopeNPerM=d['axial']['axialDerivativeNPerM'],
                              differenceNPerM=difference))

    s = sp.symbols('s')
    M, tau = sp.symbols('M tau', positive=True)
    c, km = sp.symbols('c km', nonnegative=True)
    K = sp.symbols('K', real=True)
    operator = sp.Matrix([[M*s*s + c*s + K, 1], [-tau*km*s, 1 + tau*s]])
    polynomial = sp.expand(operator.det())
    coefficients = sp.Poly(polynomial, s).all_coeffs()
    margin = sp.expand(coefficients[1]*coefficients[2] - coefficients[0]*coefficients[3])
    assert sp.simplify(margin - (M*c + M*tau*km + c*c*tau + c*tau*tau*(K + km))) == 0
    factor = sp.factor(polynomial.subs({c: 0, km: 0}))
    assert sp.simplify(factor - (1 + tau*s)*(M*s*s + K)) == 0
    symbolic = json.loads((OUT / 'memory-stability-symbolic.json').read_text())
    assert symbolic['result'] == 'PASS_PARAMETER_FREE_LINEAR_MEMORY_STABILITY_IDENTITY'
    assert symbolic['sourceSHA256'] == digest(ROOT / 'tools/active_memory_stability.py')
    checked_inputs.extend(ROOT / name for name in summary['sourceHashes'])
    checked_inputs.extend([ROOT / 'tools/active_memory_stability.py', Path(__file__)])
    receipt = dict(result='PASS_INDEPENDENT_ACTIVE_CONTROLS_INTERNAL_AUDIT',
                   sourceCommit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                   sourceHashes={str(path.relative_to(ROOT)): digest(path) for path in sorted(set(checked_inputs))},
                   auditedCaseCount=len(paths), gateMaxima=maxima, sampledJRange=[jlo, jhi],
                   worstFullDerivative=worst_full, pressureDimensions=sorted(pressure_dimensions),
                   maximumCapWitnessEntry=cap_max, maximumRankOneDeterminantChange=float(det_change),
                   constantJLocalCurvature=local, independentAxialDerivatives=axial,
                   independentMaxwell=dict(characteristicPolynomial=str(polynomial),
                                           routhHurwitzMargin=str(margin), undampedFactorization=str(factor)),
                   limits=['No controls rerun, new optimizer or source-bound receipt modification.',
                           'Saved gradient checks audited; full FE spectra not independently recomputed.',
                           'Independent local, axial and scalar symbolic calculations; no anatomical or nonlinear qualification.'])
    print(json.dumps(receipt, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
