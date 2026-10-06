#!/usr/bin/env python3
"""Independent fixed-budget mp60 vector audit; no physical trajectory or loading."""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import traceback

import mpmath as mp
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/anatomical-arm-v1/review/source-two-state-operator'
mp.mp.dps = 60
STATE_GATE = mp.mpf('2e-12')
RESIDUAL_GATE = mp.mpf('1e-12')
FD_DELTA = mp.mpf('1e-20')
FD_GATE = mp.mpf('1e-25')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scalar(x):
    # Preserve each actual binary64 input exactly in the independent arithmetic.
    return mp.mpf(float(x))


def vector(a):
    return [scalar(x) for x in a]


def norm(a):
    return max([abs(x) for x in a], default=mp.mpf(0))


def rhs(p, N, F, g):
    B = mp.fsum(p)
    return [F[i] * (1-B) * (N-B) - g[i]*p[i] for i in range(len(p))]


def jacobian(p, N, F, g, h=None):
    r = 1+N-2*mp.fsum(p)
    if h is None:
        return mp.matrix([[-g[i]*(i == j)-F[i]*r for j in range(len(p))]
                          for i in range(len(p))])
    return mp.matrix([[(1+h*g[i])*(i == j)+h*F[i]*r
                       for j in range(len(p))] for i in range(len(p))])


def reference(old, N, F, g, h=None):
    # Solve ORIGINAL vector equations, never the reduced quadratic.
    def residual(*p):
        f = rhs(p, N, F, g)
        return f if h is None else [p[i]-old[i]-h*f[i] for i in range(len(p))]

    def derivative(*p):
        return jacobian(p, N, F, g, h)

    solution = mp.findroot(residual, tuple(old), J=derivative,
                           solver='mdnewton', tol=mp.mpf('1e-45'), maxsteps=20)
    p = list(solution)
    own_residual = norm(residual(*p))
    # The numerical reference is gated independently, including the admissible branch.
    if any(x < 0 for x in p) or mp.fsum(p) > N:
        raise ValueError('reference root violates strict population bounds')
    if own_residual > mp.mpf('1e-40'):
        raise ValueError('reference full residual exceeds 1e-40')
    return p, own_residual


def fd_check(p, N, F, g, h=None):
    analytic = jacobian(p, N, F, g, h)
    errors = []
    for j in range(len(p)):
        lo, hi = list(p), list(p)
        lo[j] -= FD_DELTA
        hi[j] += FD_DELTA
        rlo, rhi = rhs(lo, N, F, g), rhs(hi, N, F, g)
        for i in range(len(p)):
            num = (rhi[i]-rlo[i])/(2*FD_DELTA)
            if h is not None:
                num = (i == j)-h*num
            errors.append(num-analytic[i, j])
    return norm(errors)


def checked_output(p, n, N):
    p = np.asarray(p)
    if p.shape != (n,) or not np.all(np.isfinite(p)):
        raise ValueError('operator returned wrong shape or nonfinite population')
    if np.any(p < 0) or math.fsum(map(float, p)) > float(N):
        raise ValueError('operator violates strict post-step population bounds')
    return p


def encode(x):
    if isinstance(x, (mp.mpf, mp.mpc)):
        return mp.nstr(x, 35)
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, np.generic):
        return encode(x.item())
    if isinstance(x, float) and not math.isfinite(x):
        return str(x)
    if isinstance(x, dict):
        return {k: encode(v) for k, v in x.items()}
    if isinstance(x, (tuple, list)):
        return [encode(v) for v in x]
    return x


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--protocol', required=True, type=Path)
    parser.add_argument('--protocol-commit', required=True)
    args = parser.parse_args()
    if len(args.protocol_commit) != 40 or any(c not in '0123456789abcdef' for c in args.protocol_commit):
        raise ValueError('provide full precommitted protocol SHA')
    protocol = args.protocol.resolve()
    source = ROOT / 'tools/source_two_state_operator.py'
    OUT.mkdir(parents=True, exist_ok=True)
    json_path, log_path = OUT/'independent-audit.json', OUT/'independent-audit.log'
    if json_path.exists() or log_path.exists():
        raise FileExistsError('preserve existing independent audit receipt')
    spec = importlib.util.spec_from_file_location('audited_source_two_state_operator', source)
    operator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(operator)
    result = {'result': 'RUNNING', 'scope': 'Synthetic one-step operator checks only; no physical trajectory',
              'sourceSHA256': sha(source), 'auditSourceSHA256': sha(Path(__file__)),
              'protocolPath': str(protocol), 'protocolSHA256': sha(protocol),
              'protocolCommit': args.protocol_commit,
              'fixedGates': {'referenceDigits': 60, 'referenceMaxSteps': 20,
                             'referenceTolerance': '1e-45', 'referenceOwnFullResidual': '1e-40',
                             'referenceStateMaxAbsolute': '2e-12', 'normalizedFullBEResidual': '1e-12',
                             'populationBounds': 'strict p_i>=0 and fsum(p)<=N',
                             'jacobianFDPerturbation': '1e-20', 'jacobianFDAbsoluteError': '1e-25',
                             'implementedJacobianScaledError': '1e-12',
                             'referenceInitialGuess': 'old state; equilibrium checks start at zero',
                             'retries': 0},
              'cases': [], 'equilibria': [], 'invalidInputs': [], 'auxiliary': [], 'failures': []}
    log = []
    current = {}

    def run(label, destination, function):
        current.clear()
        try:
            item = function()
            item.update(label=label, passed=True)
            destination.append(item)
            log.append('PASS '+label)
        except Exception as exc:
            item = {'label': label, 'passed': False, 'exception': type(exc).__name__,
                    'message': str(exc), 'traceback': traceback.format_exc()}
            item.update(current)
            destination.append(item)
            result['failures'].append(item)
            log.append('FAIL '+label+': '+type(exc).__name__+': '+str(exc))

    grids = [('three', np.array([.7, 1.3, 4.2]), np.array([.05, 2., 100.])),
             ('seven', np.geomspace(.001, 100., 7), np.geomspace(.02, 1e4, 7))]

    def audit_step(old, N, F, g, h):
        current.update(old=old, N=N, F=F, g=g, h=h)
        m_old, mN, mF, mg, mh = vector(old), scalar(N), vector(F), vector(g), scalar(h)
        ref, own = reference(m_old, mN, mF, mg, mh)
        current.update(reference=ref, referenceOwnFullResidual=own)
        raw = operator.step(old.copy(), N, F.copy(), g.copy(), h)
        current['actual'] = np.asarray(raw)
        actual = checked_output(raw, len(F), N)
        ap = vector(actual)
        error = norm([ap[i]-ref[i] for i in range(len(F))])
        residual = norm([ap[i]-m_old[i]-mh*rhs(ap, mN, mF, mg)[i] for i in range(len(F))])
        scale = max(1, mN, mh*mp.fsum(mF), mh*max(mg)*mN)
        normalized = residual/scale
        fd = max(fd_check(ref, mN, mF, mg), fd_check(ref, mN, mF, mg, mh))
        source_jac = np.asarray(operator.jacobian(actual, N, F, g))
        exact_jac = jacobian(ap, mN, mF, mg)
        if source_jac.shape != (len(F), len(F)) or not np.all(np.isfinite(source_jac)):
            raise ValueError('implemented Jacobian has wrong shape or nonfinite entries')
        jscale = max(1, norm(list(exact_jac)))
        jerror = norm([scalar(source_jac[i, j])-exact_jac[i, j]
                       for i in range(len(F)) for j in range(len(F))])/jscale
        current.update(referenceStateMaxAbsolute=error, normalizedFullBEResidual=normalized,
                       fullBEResidual=residual, residualScale=scale, jacobianFDMaxAbsoluteError=fd,
                       implementedJacobianScaledError=jerror)
        if error > STATE_GATE or normalized > RESIDUAL_GATE or fd > FD_GATE or jerror > RESIDUAL_GATE:
            raise ValueError('state/residual/Jacobian gate failed: '+str((error, normalized, fd, jerror)))
        return {'old': old, 'N': N, 'F': F, 'g': g, 'h': h, 'actual': actual,
                'reference': ref, 'referenceOwnFullResidual': own,
                'referenceStateMaxAbsolute': error, 'normalizedFullBEResidual': normalized,
                'fullBEResidual': residual, 'residualScale': scale,
                'jacobianFDMaxAbsoluteError': fd,
                'implementedJacobianScaledError': jerror,
                'postB': math.fsum(map(float, actual)), 'minPopulation': float(actual.min())}

    def audit_equilibrium(F, g, N):
        current.update(F=F, g=g, N=N)
        mF, mg, mN = vector(F), vector(g), scalar(N)
        ref, own = reference([mp.mpf(0)]*len(F), mN, mF, mg)
        current.update(reference=ref, referenceOwnFullResidual=own)
        raw = operator.equilibrium(F.copy(), g.copy(), N)
        current['actual'] = np.asarray(raw)
        actual = checked_output(raw, len(F), N)
        ap = vector(actual)
        error = norm([ap[i]-ref[i] for i in range(len(F))])
        residual = norm(rhs(ap, mN, mF, mg))/max(1, mp.fsum(mF), max(mg)*mN)
        if error > STATE_GATE or residual > RESIDUAL_GATE:
            raise ValueError('equilibrium state/full RHS gate failed: '+str((error, residual)))
        Bactual, Bref = mp.fsum(ap), mp.fsum(ref)
        if Bref > 0 and Bactual == 0:
            raise ValueError('nonzero tiny-I equilibrium population lost to cancellation')
        return {'F': F, 'g': g, 'N': N, 'actual': actual, 'reference': ref,
                'BActual': Bactual, 'BReference': Bref, 'referenceOwnFullResidual': own,
                'referenceStateMaxAbsolute': error, 'normalizedFullRHSResidual': residual}

    for name, F, g in grids:
        for N in (1e-6, .2, 1.):
            run(f'equilibrium/{name}/N={N}', result['equilibria'],
                lambda F=F, g=g, N=N: audit_equilibrium(F, g, N))
            for fraction in (0., .3, 1.):
                old = np.zeros(len(F))
                if fraction == 1:
                    old[0] = N
                elif fraction:
                    weights = np.arange(1., len(F)+1)
                    old = N*fraction*weights/weights.sum()
                for h in (1e-12, .001, .1, 1.):
                    run(f'BE/{name}/N={N}/oldFraction={fraction}/h={h}', result['cases'],
                        lambda old=old, N=N, F=F, g=g, h=h: audit_step(old, N, F, g, h))

    for label, F, g, N in [
            ('zero-attachment', np.zeros(3), np.array([.05, 2., 100.]), .2),
            ('zero-capacity', np.array([.7, 1.3, 4.2]), np.array([.05, 2., 100.]), 0.),
            ('sparse-attachment', np.array([0., 1.3, 0.]), np.array([.05, 2., 100.]), .2),
            ('tiny-I', np.array([.7, 1.3, 4.2])*1e-25, np.array([.05, 2., 100.]), .2)]:
        run('equilibrium/'+label, result['equilibria'],
            lambda F=F, g=g, N=N: audit_equilibrium(F, g, N))
        old = np.array([N/2, 0., 0.])
        run('BE/'+label, result['auxiliary'],
            lambda old=old, N=N, F=F, g=g: audit_step(old, N, F, g, .1))

    def permutation():
        F, g = grids[1][1:]
        old = .2*np.arange(1., 8)/28
        order = np.array([6, 0, 4, 1, 5, 2, 3])
        base = checked_output(operator.step(old, .4, F, g, .1), 7, .4)
        perm = checked_output(operator.step(old[order], .4, F[order], g[order], .1), 7, .4)
        error = float(np.max(np.abs(perm-base[order])))
        if error > float(STATE_GATE):
            raise ValueError('permutation covariance failure')
        return {'maxAbsolutePermutationError': error}
    run('permutation-covariance', result['auxiliary'], permutation)

    def cancellation():
        h, g, N = 1e-18, .05, 1.
        direct = N-1/(1+h*g)
        positive = (h*g)/(1+h*g)
        exact = scalar(h)*scalar(g)/(1+scalar(h)*scalar(g))
        if direct != 0 or positive <= 0 or abs(scalar(positive)-exact)/exact > mp.mpf('1e-15'):
            raise ValueError('declared cancellation witness differs')
        return {'h': h, 'g': g, 'N': N, 'oldB': N,
                'subtractedW': direct, 'positiveAccumulationW': positive, 'mp60W': exact,
                'interpretation': 'diagnostic of W subtraction, not a physical evolution test'}
    run('saturated-small-step-W-cancellation', result['auxiliary'], cancellation)

    # Rejections test input invariants and arithmetic hazards, not the scalar solution formula.
    def rejected(call):
        try:
            call()
        except (ValueError, FloatingPointError, OverflowError) as exc:
            return {'rejectionType': type(exc).__name__, 'message': str(exc)}
        raise AssertionError('invalid input was accepted')

    F, g = grids[0][1:]
    old = np.array([.03, .04, .02])
    invalids = [
        ('negative-bin-valid-total', lambda: operator.step(np.array([-.01, .04, .02]), .2, F, g, .1)),
        ('old-B-exceeds-N', lambda: operator.step(np.array([.21, 0., 0.]), .2, F, g, .1)),
        ('capacity-reset-U-would-be-valid', lambda: operator.step(np.array([1., 0., 0.]), .2, F, np.ones(3)*100., 1.)),
        ('negative-N', lambda: operator.step(old, -.1, F, g, .1)),
        ('N-above-one', lambda: operator.step(old, 1.01, F, g, .1)),
        ('negative-F', lambda: operator.step(old, .2, np.array([-.7, 1.3, 4.2]), g, .1)),
        ('zero-g', lambda: operator.step(old, .2, F, np.array([0., 2., 100.]), .1)),
        ('negative-g', lambda: operator.step(old, .2, F, np.array([-.05, 2., 100.]), .1)),
        ('zero-h', lambda: operator.step(old, .2, F, g, 0.)),
        ('negative-h', lambda: operator.step(old, .2, F, g, -.1)),
        ('nan-population', lambda: operator.step(np.array([np.nan, 0., 0.]), .2, F, g, .1)),
        ('infinite-F', lambda: operator.step(old, .2, np.array([np.inf, 1., 1.]), g, .1)),
        ('nan-N', lambda: operator.step(old, np.nan, F, g, .1)),
        ('infinite-h', lambda: operator.step(old, .2, F, g, np.inf)),
        ('mismatched-shape', lambda: operator.step(old, .2, F[:2], g, .1)),
        ('empty-input', lambda: operator.step(np.array([]), .2, np.array([]), np.array([]), .1)),
        ('overflow-h-g', lambda: operator.step(np.array([0.]), 1., np.array([1.]), np.array([1e308]), 1e308)),
        ('overflow-h-F', lambda: operator.step(np.array([0.]), 1., np.array([1e308]), np.array([1.]), 1e308)),
        ('equilibrium-negative-F', lambda: operator.equilibrium(np.array([-1.]), np.array([1.]), .2)),
        ('equilibrium-zero-g', lambda: operator.equilibrium(np.array([1.]), np.array([0.]), .2)),
        ('equilibrium-N-above-one', lambda: operator.equilibrium(F, g, 1.01)),
        ('equilibrium-overflow-I', lambda: operator.equilibrium(np.array([1e308]), np.array([1e-308]), .2)),
    ]
    for label, call in invalids:
        run('reject/'+label, result['invalidInputs'], lambda call=call: rejected(call))

    assert len(result['cases']) == 72
    result['result'] = 'PASS_INDEPENDENT_SOURCE_TWO_STATE_OPERATOR' if not result['failures'] else 'FAIL_INDEPENDENT_SOURCE_TWO_STATE_OPERATOR'
    result['counts'] = {k: len(result[k]) for k in ('cases', 'equilibria', 'auxiliary', 'invalidInputs', 'failures')}
    result['maxima'] = {key: max((mp.mpf(str(item[key])) for item in result['cases'] if item['passed']), default=mp.mpf(0))
                        for key in ('referenceStateMaxAbsolute', 'normalizedFullBEResidual', 'referenceOwnFullResidual', 'jacobianFDMaxAbsoluteError', 'implementedJacobianScaledError')}
    json_path.write_text(json.dumps(encode(result), indent=2, allow_nan=False)+'\n')
    log.append(result['result'])
    log_path.write_text('\n'.join(log)+'\n')
    print(json.dumps(encode({'result': result['result'], 'counts': result['counts'], 'maxima': result['maxima']}), indent=2))
    return 0 if not result['failures'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
