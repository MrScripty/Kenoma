#!/usr/bin/env python3
"""Independent DOP853 audit of a declared held-N direct-CE reversal fixture.

No source operator is imported. Original coupled bin ODE, Gaussian cell rates,
equilibrium and center-mass remaps are evaluated independently. Execution must
wait for the owner's precommitted protocol and saved trajectory packet.
"""
import argparse
import hashlib
import json
import math
import platform
import traceback
from pathlib import Path

import mpmath as mp
import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.special import ndtr

ROOT = Path(__file__).resolve().parents[1]
PARAM = dict(f1=52., g1=4., g2=21.1, E1=2., E2=-.6, w=.3,
             beta=.5, nH=3.1, Ca50M=.83e-6)
SOLVER = dict(method='DOP853', rtol=1e-11, atol=1e-14,
              first_step=None, dense_output=True, t_eval=None)
MAX_STEPS = [.001, .0005]
REFERENCE_STATE_GATE = 1e-10
REFERENCE_FORCE_GATE = 2e-10
INITIAL_RHS_L1_GATE = 1e-10
INITIAL_STATE_MAX_GATE = 2e-12
GRID_NORMALIZED_GATE = 1e-12
TIMES = np.array([0., 0., .008, .02, .04, .1, .2, .2, .3, .5, 1.])
REVERSAL = .2
TERMINAL = 1.
FAILED_WITNESS = {}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mass(p):
    return math.fsum(map(float, p))


def array_identity(array):
    # Canonical row-major little-endian float64 bytes; no archive of full nodes.
    canonical = np.ascontiguousarray(array, dtype='<f8')
    return dict(SHA256=hashlib.sha256(memoryview(canonical).cast('B')).hexdigest(),
                shape=list(canonical.shape), nbytes=canonical.nbytes,
                dtype='little-endian float64', byteOrder='C')


def checked(p, N, label):
    p = np.asarray(p, dtype=float)
    if not (np.isfinite(N) and 0 < N <= 1):
        FAILED_WITNESS.update(population=p.copy(), N=float(N), label=label,
                              reason='invalid held thin-site capacity')
        raise ValueError(f'{label}: invalid held thin-site capacity')
    if p.ndim != 1 or not np.all(np.isfinite(p)):
        FAILED_WITNESS.update(population=p.copy(), N=float(N), label=label,
                              reason='nonfinite or nonvector state')
        raise ValueError(f'{label}: nonfinite or nonvector state')
    if np.any(p < 0) or mass(p) > N:
        FAILED_WITNESS.update(population=p.copy(), N=float(N), label=label,
                              reason='strict positivity/capacity gate failed')
        raise ValueError(f'{label}: strict positivity/capacity gate failed; no clipping')
    return p


def capacity(pca):
    # Convert pCa (molar logarithm) to the table's micromolar convention.
    calcium_um = 10.**(6.-pca)
    return 1./(1.+(.83/calcium_um)**3.1)


def grid(radius, dx):
    count = int(round(2*radius/dx))
    edges = np.linspace(-radius, radius, count+1)
    x = .5*(edges[1:]+edges[:-1])
    F = np.empty(count)
    for i, (left, right) in enumerate(zip(edges[:-1], edges[1:])):
        lo, hi = left/.3, right/.3
        F[i] = 52.*((ndtr(-lo)-ndtr(-hi)) if lo >= 0 else
                    (ndtr(hi)-ndtr(lo)))
    g = 4.*np.exp(-2.*x)+21.1*np.exp(.6*x)
    if np.any(F <= 0) or np.any(g <= 0):
        raise ValueError('independent grid has a nonpositive rate')
    return x, F, g


def rhs(p, N, F, g):
    # Original coupled vector equations; no reduced BE/quadratic operator.
    B = mass(p)
    return F*(1.-B)*(N-B)-g*p


def equilibrium_mp(N, F, g):
    with mp.workdps(60):
        nn = mp.mpf(float(N))
        ff = [mp.mpf(float(v)) for v in F]
        gg = [mp.mpf(float(v)) for v in g]
        I = mp.fsum(f/d for f, d in zip(ff, gg))
        c = 1-nn
        a = 1+I*c
        q = 2*nn/(a+mp.sqrt(a*a+4*I*nn))
        p = [f*q*(c+q)/d for f, d in zip(ff, gg)]
        B = mp.fsum(p)
        residual = max(abs(f*(1-B)*(nn-B)-d*z)
                       for f, d, z in zip(ff, gg, p))
        if min(p) < 0 or B > nn:
            raise ValueError('independent mp equilibrium violates capacity')
        return np.array([float(z) for z in p]), {
            'digits': 60, 'B': mp.nstr(B, 40), 'q': mp.nstr(q, 40),
            'originalRHSMaxAbsolute': mp.nstr(residual, 12)}


def remap(p, N, x, dx, delta):
    """Own center-bin interpolation; escaping attached mass is detached.

    A transfer matrix is evaluated explicitly instead of calling subject shift.
    All column moment/escape effects are recorded, with no clipping or reset.
    """
    p = checked(p, N, 'independent remap input')
    if not (np.isfinite(delta) and 0 < abs(delta) < dx):
        raise ValueError('independent remap requires a sub-bin nonzero shift')
    n = len(p)
    r = abs(delta)/dx
    moved = np.zeros(n)
    escaped = 0.
    escaped_moment = 0.
    sign = 1 if delta > 0 else -1
    for i in range(n):
        moved[i] += (1-r)*p[i]
        destination = i+sign
        if 0 <= destination < n:
            moved[destination] += r*p[i]
        else:
            escaped += r*p[i]
            escaped_moment += r*p[i]*(1+x[i]+sign*dx)
    moved = checked(moved, N, 'independent remap output')
    before = float(np.dot(1+x, p)/.5)
    after = float(np.dot(1+x, moved)/.5)
    predicted = (mass(p)*delta-escaped_moment)/.5
    return moved, dict(escapedMass=escaped,
                      escapedDiscreteMoment=escaped_moment,
                      immediateForceIncrement=after-before,
                      discreteMomentPrediction=predicted,
                      momentIdentityError=abs(after-before-predicted),
                      beforeB=mass(p), afterB=mass(moved),
                      massIdentityError=abs(mass(moved)-mass(p)+escaped))


def solve_segment(initial, N, F, g, start, end, max_step):
    checked(initial, N, f'reference segment {start} initial')
    solution = solve_ivp(lambda _t, p: rhs(p, N, F, g), (start, end),
                         initial, max_step=max_step, **SOLVER)
    if not solution.success or solution.t[-1] != end:
        raise ValueError('DOP853 failed or changed requested segment terminal time')
    # Gate every accepted solver node; no clipping or skipped tail populations.
    for t, p in zip(solution.t, solution.y.T):
        checked(p, N, f'DOP853 accepted t={t}')
    return solution, dict(startSeconds=start, requestedTerminalSeconds=end,
                          actualTerminalSeconds=float(solution.t[-1]),
                          success=bool(solution.success), message=solution.message,
                          maxStepSeconds=max_step, nfev=int(solution.nfev), internalAcceptedNodes=len(solution.t),
                          internalMinimumPopulation=float(np.min(solution.y)),
                          internalMinimumB=min(mass(z) for z in solution.y.T),
                          internalMaximumB=max(mass(z) for z in solution.y.T),
                          acceptedStateArray=array_identity(solution.y.T))


def independent_reference(eq, N, F, g, x, dx, delta, max_step):
    """Continue own reference through the reversal; never reset to BE state."""
    own_load, load = remap(eq, N, x, dx, delta)
    first, r1 = solve_segment(own_load, N, F, g, 0., REVERSAL, max_step)
    own_pre = checked(first.sol(REVERSAL), N, 'reference reversal pre')
    own_post, jump = remap(own_pre, N, x, dx, -delta)
    second, r2 = solve_segment(own_post, N, F, g, REVERSAL, TERMINAL, max_step)
    states = []
    for index, t in enumerate(TIMES):
        if index == 0:
            p = eq
        elif index == 1:
            p = own_load
        elif t == REVERSAL:
            p = own_pre if index == 6 else own_post
        elif t < REVERSAL:
            p = first.sol(t)
        else:
            p = second.sol(t)
        states.append(checked(p, N, f'reference matched t={t} index={index}'))
    states = np.asarray(states)
    return states, (first, second), dict(segments=[r1, r2], loading=load, reversal=jump,
                        minimumMatchedPopulation=float(np.min(states)),
                        maximumMatchedB=max(mass(z) for z in states),
                        reversalInitialState='own DOP853 pre-reversal state independently remapped',
                        requestedTerminalSeconds=TERMINAL,
                        terminalRHSMaxAbsolute=float(np.max(np.abs(rhs(second.y[:, -1], N, F, g)))))


def ratios(errors):
    return [None if a == 0 else b/a for a, b in zip(errors[:-1], errors[1:])]


def encoded(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return encoded(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return repr(value)
    if isinstance(value, dict):
        return {k: encoded(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [encoded(v) for v in value]
    return value


def main():
    FAILED_WITNESS.clear()
    parser = argparse.ArgumentParser()
    parser.add_argument('--packet', required=True, type=Path)
    parser.add_argument('--protocol', required=True, type=Path)
    parser.add_argument('--protocol-commit', required=True)
    args = parser.parse_args()
    if len(args.protocol_commit) != 40 or any(c not in '0123456789abcdef' for c in args.protocol_commit):
        raise ValueError('provide the full precommitted protocol identity')
    packet = args.packet.resolve()
    protocol = args.protocol.resolve()
    target = packet/'independent-audit.json'
    archive_target = packet/'independent-reference.npz'
    if target.exists() or archive_target.exists():
        raise FileExistsError('preserve existing independent audit receipts')
    summary_path = packet/'summary.json'
    state_path = packet/'matched-states.npz'
    summary = json.loads(summary_path.read_text())
    data = np.load(state_path, allow_pickle=False)
    if not np.array_equal(data['matchedTimesSeconds'], TIMES):
        raise ValueError('matched-time/event schema differs from fixed protocol')
    if len(summary['cases']) != 144 or len(summary['grids']) != 6:
        raise ValueError('fixed 144-case/six-grid packet incomplete')
    grid_set = {(float(g['R']), float(g['dx'])) for g in summary['grids']}
    if grid_set != {(R, dx) for R in [2.4, 3.] for dx in [.04, .02, .01]}:
        raise ValueError('grid coverage differs from fixed protocol')
    cases_set = {(c['grid'], float(c['pCa']), float(c['delta']), float(c['dt']))
                 for c in summary['cases']}
    expected_set = {(g['name'], pca, delta, dt) for g in summary['grids']
                    for pca in [4.5, 6.1] for delta in [.001, -.001, .0005, -.0005]
                    for dt in [.004, .002, .001]}
    if cases_set != expected_set or len({c['name'] for c in summary['cases']}) != 144:
        raise ValueError('case coverage/uniqueness differs from fixed protocol')
    receipt = dict(result='RUNNING',
                   scope='Independent source-median held-N conserved-population direct-CE step/reversal audit; no series or SI scale',
                   auditSourceSHA256=sha(Path(__file__)), protocolPath=str(protocol),
                   protocolSHA256=sha(protocol), protocolCommit=args.protocol_commit,
                   summarySHA256=sha(summary_path), matchedStatesSHA256=sha(state_path),
                   solver=dict(**SOLVER, maxStepsSeconds=MAX_STEPS,
                               resolutionStateL1Gate=REFERENCE_STATE_GATE,
                               resolutionForceAbsoluteGate=REFERENCE_FORCE_GATE,
                               initialOriginalRHSL1Gate=INITIAL_RHS_L1_GATE,
                               initialStateMaxAbsoluteGate=INITIAL_STATE_MAX_GATE,
                               gridNormalizedMaxAbsoluteGate=GRID_NORMALIZED_GATE),
                   gates='Strict finite/nonnegative populations and independently summed B<=N at every accepted node and matched time; no clipping',
                   environment=dict(python=platform.python_version(), numpy=np.__version__,
                                    scipy=scipy.__version__, mpmath=mp.__version__),
                   requestedTerminalSeconds=TERMINAL, matchedTimesSeconds=TIMES,
                   parameters=PARAM, grids=[], references=[], cases=[], refinements={})
    stored = {'matchedTimesSeconds': TIMES}
    cache = {}
    bygrid = {g['name']: g for g in summary['grids']}
    try:
        for name, metadata in bygrid.items():
            x, F, g = grid(float(metadata['R']), float(metadata['dx']))
            actual_x, actual_F, actual_g = [data[name+'_'+suffix] for suffix in ['x', 'F', 'g']]
            if any(a.shape != b.shape for a, b in [(x, actual_x), (F, actual_F), (g, actual_g)]):
                raise ValueError('independent/source grid shapes differ')
            if any(not np.all(np.isfinite(a)) for a in [actual_x, actual_F, actual_g]):
                raise ValueError('saved grid contains nonfinite values')
            normalized = [float(np.max(np.abs(own-actual))/max(1., np.max(np.abs(own))))
                          for own, actual in [(x, actual_x), (F, actual_F), (g, actual_g)]]
            receipt['grids'].append(dict(name=name,
                xMaxAbsoluteDifference=float(np.max(np.abs(x-actual_x))),
                attachmentMaxAbsoluteDifference=float(np.max(np.abs(F-actual_F))),
                detachmentMaxAbsoluteDifference=float(np.max(np.abs(g-actual_g))),
                normalizedMaxAbsoluteDifferences=dict(x=normalized[0], F=normalized[1], g=normalized[2]),
                normalization='max absolute difference / max(1, independent vector max absolute)',
                GaussianTruncationFraction=float(2*ndtr(-metadata['R']/.3))))
            if max(normalized) > GRID_NORMALIZED_GATE:
                raise ValueError('fixed independent grid normalized agreement gate failed')
            cache[name] = (x, F, g)
        for case in summary['cases']:
            name = case['name']
            x, F, g = cache[case['grid']]
            N = float(case['N'])
            actual = data[name]
            if actual.shape != (len(TIMES), len(x)):
                raise ValueError(f'{name}: wrong matched-state shape')
            for index, p in enumerate(actual):
                checked(p, N, f'{name} saved matched index={index}')
            key = (case['grid'], float(case['pCa']), float(case['delta']))
            if key not in cache:
                refname = f"{case['grid']}-pCa{case['pCa']:g}-delta{case['delta']:g}"
                eq, eqrecord = equilibrium_mp(N, F, g)
                checked(eq, N, 'mp60 equilibrium rounded to binary64')
                initial_difference = float(np.max(np.abs(actual[0]-eq)))
                saved_rhs_l1 = mass(np.abs(rhs(actual[0], N, F, g)))
                if initial_difference > INITIAL_STATE_MAX_GATE or saved_rhs_l1 > INITIAL_RHS_L1_GATE:
                    FAILED_WITNESS.update(population=actual[0].copy(), N=N,
                        label=f'{name} saved initial equilibrium',
                        reason='initial equilibrium agreement/original-RHS gate failed')
                    raise ValueError('saved initial equilibrium state or original-RHS gate failed')
                reference_runs = []
                refrecord = dict(name=refname, grid=case['grid'], pCa=case['pCa'], delta=case['delta'], N=N,
                                 independentlyComputedN=capacity(case['pCa']),
                                 capacityAbsoluteDifference=abs(N-capacity(case['pCa'])),
                                 mpEquilibrium=eqrecord,
                                 savedEquilibriumStateMaxAbsoluteDifference=initial_difference,
                                 savedEquilibriumStateL1Difference=float(np.sum(np.abs(actual[0]-eq))),
                                 savedEquilibriumOwnRHSL1PerSecond=saved_rhs_l1,
                                 savedEquilibriumOwnRHSMaxAbsolute=float(np.max(np.abs(rhs(actual[0], N, F, g)))),
                                 roundedMpEquilibriumOwnRHSMaxAbsolute=float(np.max(np.abs(rhs(eq, N, F, g)))),
                                 runs=[])
                for max_step in MAX_STEPS:
                    states, segments, runrecord = independent_reference(eq, N, F, g, x,
                        float(bygrid[case['grid']]['dx']), float(case['delta']), max_step)
                    reference_runs.append(states)
                    runrecord['maxStepSeconds'] = max_step
                    refrecord['runs'].append(runrecord)
                    suffix = f'{refname}-maxstep{max_step:g}'
                    stored[suffix] = states
                    for index, segment in enumerate(segments):
                        stored[f'{suffix}-segment{index}-acceptedTimes'] = segment.t
                coarse, fine = reference_runs
                state_difference = float(np.max(np.sum(np.abs(coarse-fine), axis=1)))
                force_difference = float(np.max(np.abs((coarse-fine)@(1+x)/.5)))
                refrecord.update(resolutionStateL1Max=state_difference,
                                 resolutionForceAbsoluteMax=force_difference)
                receipt['references'].append(refrecord)
                if state_difference > REFERENCE_STATE_GATE or force_difference > REFERENCE_FORCE_GATE:
                    raise ValueError('fixed two-resolution DOP853 accuracy gate failed')
                cache[key] = (fine, refname)
                print(json.dumps(dict(reference=refname, resolutionStateL1Max=state_difference,
                                      resolutionForceAbsoluteMax=force_difference)), flush=True)
            reference, refname = cache[key]
            # Gate every saved initial state, including all three BE timesteps.
            initial_difference = float(np.max(np.abs(actual[0]-reference[0])))
            saved_rhs_l1 = mass(np.abs(rhs(actual[0], N, F, g)))
            if initial_difference > INITIAL_STATE_MAX_GATE or saved_rhs_l1 > INITIAL_RHS_L1_GATE:
                FAILED_WITNESS.update(population=actual[0].copy(), N=N,
                    label=f'{name} saved initial equilibrium',
                    reason='initial equilibrium agreement/original-RHS gate failed')
                raise ValueError('saved initial equilibrium state or original-RHS gate failed')
            state_errors = np.sum(np.abs(actual-reference), axis=1)
            force_errors = np.abs((actual-reference)@(1+x)/.5)
            actual_force = actual@(1+x)/.5
            receipt['cases'].append(dict(name=name, reference=refname, grid=case['grid'],
                pCa=case['pCa'], delta=case['delta'], dt=case['dt'],
                savedInitialStateMaxAbsoluteDifference=initial_difference,
                savedInitialOwnRHSL1PerSecond=saved_rhs_l1,
                stateL1Errors=state_errors, forceAbsoluteErrors=force_errors,
                maximumMatchedStateL1Error=float(np.max(state_errors)),
                maximumMatchedForceAbsoluteError=float(np.max(force_errors)),
                reportedForceMaximumDifference=float(np.max(np.abs(actual_force-case['matchedForces']))),
                savedMinimumPopulation=float(np.min(actual)), savedMaximumB=max(mass(z) for z in actual),
                terminalOwnRHSMaxAbsolute=float(np.max(np.abs(rhs(actual[-1], N, F, g))))))
        bycase = {(c['grid'], c['pCa'], c['delta'], c['dt']): c for c in receipt['cases']}
        temporal = []
        for gridname, pca, delta in sorted({(c['grid'], c['pCa'], c['delta']) for c in receipt['cases']}):
            group = [bycase[gridname, pca, delta, dt] for dt in [.004, .002, .001]]
            state_errors = [c['maximumMatchedStateL1Error'] for c in group]
            force_errors = [c['maximumMatchedForceAbsoluteError'] for c in group]
            temporal.append(dict(grid=gridname, pCa=pca, delta=delta,
                                 maximumStateL1Errors=state_errors, stateHalvingRatios=ratios(state_errors),
                                 maximumForceAbsoluteErrors=force_errors, forceHalvingRatios=ratios(force_errors)))
        receipt['refinements']['temporal'] = temporal
        spatial = []
        for pca, delta in sorted({(c['pCa'], c['delta']) for c in receipt['cases']}):
            for R in [2.4, 3.]:
                refs = [cache[(f'R{R:g}-dx{dx:g}', pca, delta)][0] for dx in [.04, .02, .01]]
                forces = [p@(1+cache[f'R{R:g}-dx{dx:g}'][0])/.5 for p, dx in zip(refs, [.04, .02, .01])]
                diffs = [float(np.max(np.abs(a-b))) for a, b in zip(forces[:-1], forces[1:])]
                spatial.append(dict(radius=R, pCa=pca, delta=delta,
                                    matchedForceBinHalvingDifferences=diffs, differenceRatio=ratios(diffs)))
        receipt['refinements']['finiteBinSpace'] = spatial
        extent = []
        for pca, delta in sorted({(c['pCa'], c['delta']) for c in receipt['cases']}):
            for dx in [.04, .02, .01]:
                forces = []
                for R in [2.4, 3.]:
                    gn = f'R{R:g}-dx{dx:g}'
                    refs = cache[gn, pca, delta][0]
                    forces.append(refs@(1+cache[gn][0])/.5)
                extent.append(dict(dx=dx, pCa=pca, delta=delta,
                                   matchedForceExtentDifferenceMax=float(np.max(np.abs(forces[0]-forces[1])))))
        receipt['refinements']['finiteExtent'] = extent
        receipt['result'] = 'PASS_INDEPENDENT_REFERENCE_AND_STRICT_POPULATION_GATES'
        receipt['assessmentLimit'] = 'Temporal and spatial differences are assessments without invented response-error thresholds; no series-loaded experiment, continuum stability or human qualification.'
    except Exception as exc:
        receipt['result'] = 'FAIL_INDEPENDENT_REFERENCE_OR_STRICT_POPULATION_GATES'
        receipt['failure'] = dict(type=type(exc).__name__, message=str(exc), traceback=traceback.format_exc(),
                                  completedCases=len(receipt['cases']), completedReferences=len(receipt['references']))
        raise
    finally:
        if FAILED_WITNESS:
            stored['failedWitnessPopulation'] = FAILED_WITNESS['population']
            receipt['failedWitness'] = {k: v for k, v in FAILED_WITNESS.items() if k != 'population'}
            receipt['failedWitness'].update(npzKey='failedWitnessPopulation',
                                           array=array_identity(FAILED_WITNESS['population']))
        np.savez_compressed(archive_target, **stored)
        receipt['independentReferenceSHA256'] = sha(archive_target)
        target.write_text(json.dumps(encoded(receipt), indent=2, allow_nan=False)+'\n')
        print(json.dumps(dict(result=receipt['result'], cases=len(receipt['cases']),
                              references=len(receipt['references']), failure=receipt.get('failure'))), flush=True)


if __name__ == '__main__':
    main()
