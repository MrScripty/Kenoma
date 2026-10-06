#!/usr/bin/env python3
"""Unexecuted finite-domain continuum-strain reference with exact translations.

Main/ghost/32 boundary densities share main-only quadrature feedback. No strain
interpolator, BE operator or source implementation is imported.
"""
import argparse
from contextlib import ExitStack
import hashlib
import json
import math
from pathlib import Path
import platform
import traceback
from types import SimpleNamespace
import warnings

import numpy as np
import scipy
from scipy.integrate import DOP853, IntegrationWarning, OdeSolution, quad
from scipy.special import roots_legendre

ROOT = Path(__file__).resolve().parents[1]
TIMES = np.array([0., 0., .008, .02, .04, .1, .2, .2, .3, .5, 1.])
RADII = [2.4, 3.]
COUNTS = [200, 400, 800]
PCAS = [4.5, 6.1]
DELTAS = [.001, -.001, .0005, -.0005]
MAX_STEPS = [.001, .0005]
BETA = .5
EDGE_COUNT = 32
SOLVER = dict(method='DOP853', rtol=1e-11, atol=1e-14,
              dense_output=True, t_eval=None, first_step=None)
TIME_GATES = np.array([1e-10, 2e-10, 2e-10])
SPACE_GATE = 1e-9
JUMP_GATE = 2e-12
INITIAL_RHS_GATE = 1e-10
INITIAL_MOMENT_GATE = 1e-10
FAILED = {}
CONTEXT = {}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(a):
    a = np.ascontiguousarray(a, dtype='<f8')
    return dict(SHA256=hashlib.sha256(memoryview(a).cast('B')).hexdigest(),
                shape=list(a.shape), nbytes=a.nbytes, dtype='little-endian float64', byteOrder='C')


def summed(a):
    return math.fsum(map(float, a))


def attachment(x):
    x = np.asarray(x)
    return 52.*np.exp(-x*x/(2*.3**2))/(np.sqrt(2*np.pi)*.3)


def detachment(x):
    x = np.asarray(x)
    return 4.*np.exp(-2*x)+21.1*np.exp(.6*x)


def capacity(pca):
    return 1./(1.+(.83/10.**(6.-pca))**3.1)


def gauss(a, b, count):
    x, w = roots_legendre(count)
    return a+(x+1)*(b-a)/2, w*(b-a)/2


def adaptive(fun, a, b):
    with warnings.catch_warnings():
        warnings.simplefilter('error', IntegrationWarning)
        value, error = quad(fun, a, b, epsabs=1e-12, epsrel=1e-12)
    if not (np.isfinite(value) and np.isfinite(error)) or error > max(1e-12, abs(value)*1e-12):
        raise ValueError('fixed adaptive-quadrature accuracy check failed')
    return float(value), float(error)


def coefficient(I, N):
    c = 1.-N
    a = 1.+I*c
    q = 2*N/(a+np.sqrt(a*a+4*I*N))
    return q*(c+q)


def moments(n, x, w):
    return np.array([summed(w*n), summed(w*(1+x)*n)/BETA,
                     summed(w*.5*(1+x)**2*n)/BETA])


def candidate_context(state, N, w, label, coordinates, time):
    CONTEXT['candidate'] = dict(density=np.asarray(state).copy(), mainWeights=w.copy(), N=float(N),
        label=label, coordinates={k: np.asarray(v).copy() for k, v in coordinates.items()}, time=time)


def remember_admitted(state, N, w, label, coordinates, time):
    CONTEXT['admitted'] = dict(density=np.asarray(state).copy(), mainWeights=w.copy(), N=float(N),
        label=label, coordinates={k: np.asarray(v).copy() for k, v in coordinates.items()}, time=time)


def preserve_context(reason):
    if 'candidate' in CONTEXT:
        FAILED.update(CONTEXT['candidate'])
    if 'admitted' in CONTEXT:
        FAILED['lastAdmitted'] = CONTEXT['admitted']
    for key in ['currentRun', 'initialVerification', 'admittedLedgers', 'segmentPrefixes', 'attemptedStep']:
        if key in CONTEXT:
            FAILED[key] = CONTEXT[key]
    FAILED['reason'] = reason


def checked(state, N, w, label, coordinates, time=None):
    state = np.asarray(state, dtype=float)
    candidate_context(state, N, w, label, coordinates, time)
    invalid = (not (np.isfinite(N) and 0 < N <= 1) or
               state.ndim != 1 or state.size < len(w) or not np.all(np.isfinite(state)) or
               np.any(state < 0))
    B = summed(w*state[:len(w)]) if not invalid else float('nan')
    if invalid or B > N:
        preserve_context('strict density/main-population gate failed')
        raise ValueError(f'{label}: strict nonnegative density/B<=N gate failed; no clipping')
    return state


def escaping_strip(R, displacement):
    return (R-displacement, R) if displacement > 0 else (-R, -R-displacement)


def snapshot_solver_exception(solver, N, w, coordinates, segment, stage, error):
    # A raised step may not expose its failed internal trial. Preserve the
    # CURRENT stored solver state explicitly, never a stale matched candidate.
    CONTEXT.pop('candidate', None)
    time = getattr(solver, 't', None)
    state = getattr(solver, 'y', None)
    snapshot = dict(time=float(time) if time is not None else None, segment=segment,
                    stage=stage, exceptionType=type(error).__name__, exceptionMessage=str(error),
                    failedInternalTrialCandidateAvailable=False,
                    acceptedNodeProposalAvailable=stage == 'dense_output',
                    currentStoredSolverStateAvailable=state is not None,
                    nfev=getattr(solver, 'nfev', None))
    if state is not None:
        snapshot['density'] = np.asarray(state).copy()
        candidate_context(state, N, w, f'{segment} {stage} exception: current stored solver state',
                          coordinates, snapshot['time'])
    CONTEXT['attemptedStep'] = snapshot
    preserve_context(f'{stage} raised: {error}')


def jump_record(before, after, h, escape):
    expected = np.array([-escape[0], before[0]*h/BETA-escape[1],
                         before[1]*h+before[0]*h*h/(2*BETA)-escape[2]])
    error = np.abs(after-before-expected)
    record = dict(displacement=h, beforeMoments=before, afterMoments=after,
                  escapedMass=float(escape[0]), escapedSignedForceMoment=float(escape[1]),
                  escapedElasticEnergy=float(escape[2]), identityAbsoluteErrors=error,
                  interpolationWork=0.)
    if escape[0] < 0 or escape[2] < 0 or np.max(error) > JUMP_GATE:
        FAILED['jump'] = record
        raise ValueError('fixed continuum jump ledger gate failed')
    return record


def solve_segment(initial, N, x, w, coordinates, injection, loss, start, end, max_step):
    checked(initial, N, w, f'segment {start} initial', coordinates, start)
    count = len(x)

    def rhs(_t, n):
        B = summed(w*n[:count])
        return injection*(1.-B)*(N-B)-loss*n

    # Public low-level API: preserve normal embedded adaptive error control.
    # Gate the current accepted-node proposal and every requested sample before
    # external admission/another step; no external restart after a gate failure.
    solver = DOP853(rhs, start, initial, end, max_step=max_step,
                    rtol=SOLVER['rtol'], atol=SOLVER['atol'],
                    first_step=SOLVER['first_step'])
    segment_key = f'{start:g}-{end:g}'
    prefix = dict(times=[float(start)], states=[initial.copy()],
                  matchedTimes=[float(start)], matchedStates=[initial.copy()],
                  mainWeights=w.copy(), coordinates=coordinates)
    CONTEXT.setdefault('segmentPrefixes', {})[segment_key] = prefix
    interpolants = []
    matched = {float(start): initial.copy()}
    requested = sorted(set(float(t) for t in TIMES if start < t <= end))
    while solver.status == 'running':
        old_t = float(solver.t)
        try:
            message = solver.step()
        except Exception as error:
            snapshot_solver_exception(solver, N, w, coordinates, segment_key, 'step', error)
            raise
        new_t = float(solver.t)
        CONTEXT['attemptedStep'] = dict(time=new_t, density=solver.y.copy(),
            previousTime=old_t, nfev=int(solver.nfev), segment=segment_key)
        if solver.status == 'failed' or not np.isfinite(new_t) or not old_t < new_t <= end:
            candidate_context(solver.y, N, w, f'solver segment {segment_key} failure', coordinates, new_t)
            preserve_context(message or 'solver failure or invalid requested interval')
            raise ValueError(message or 'DOP853 failed or left the requested interval')
        checked(solver.y, N, w, f'accepted-node candidate t={new_t}', coordinates, new_t)
        try:
            dense = solver.dense_output()
        except Exception as error:
            snapshot_solver_exception(solver, N, w, coordinates, segment_key, 'dense_output', error)
            raise
        pending = {}
        for t in requested:
            if old_t < t <= new_t:
                pending[t] = checked(dense(t), N, w,
                    f'matched candidate t={t} before admission of t={new_t}', coordinates, t).copy()
        # Nothing above may mutate the externally admitted state/time or prefix.
        prefix['times'].append(new_t)
        prefix['states'].append(solver.y.copy())
        interpolants.append(dense)
        matched.update(pending)
        for t in sorted(pending):
            prefix['matchedTimes'].append(t)
            prefix['matchedStates'].append(pending[t].copy())
        remember_admitted(solver.y, N, w, f'accepted t={new_t}', coordinates, new_t)
    if solver.status != 'finished' or solver.t != end or any(t not in matched for t in requested):
        candidate_context(solver.y, N, w, f'segment {segment_key} incomplete', coordinates, float(solver.t))
        preserve_context('requested terminal time or matched samples not reached')
        raise ValueError('DOP853 did not complete the declared segment/sample schedule')
    ts = np.asarray(prefix['times'])
    ys = np.asarray(prefix['states']).T
    sol = SimpleNamespace(t=ts, y=ys, sol=OdeSolution(ts, interpolants),
                          nfev=solver.nfev, success=True, message='finished',
                          validatedSamples=matched)
    return sol, dict(startSeconds=start, requestedTerminalSeconds=end,
                     actualTerminalSeconds=float(sol.t[-1]), nfev=sol.nfev,
                     acceptedNodes=len(sol.t), maxStepSeconds=max_step,
                     minimumDensity=float(np.min(sol.y)),
                     mainBRange=[min(summed(w*n[:count]) for n in sol.y.T),
                                 max(summed(w*n[:count]) for n in sol.y.T)],
                     acceptedStateArray=identity(sol.y.T))


def run(R, count, pca, delta, max_step):
    CONTEXT.clear()
    CONTEXT['currentRun'] = dict(R=R, count=count, pCa=pca, delta=delta,
                                 maxStepSeconds=max_step)
    x, w = gauss(-R, R, count)
    f, g = attachment(x), detachment(x)
    N = capacity(pca)
    I = summed(w*f/g)
    alpha = coefficient(I, N)

    def eq(z):
        return alpha*attachment(z)/detachment(z)

    eqn = eq(x)
    checked(eqn, N, w, 'initial equilibrium candidate', {'main': x}, 0.)
    initial = moments(eqn, x, w)
    initial_rhs = summed(w*np.abs(f*(1-initial[0])*(N-initial[0])-g*eqn))
    if initial_rhs > INITIAL_RHS_GATE:
        FAILED['initialWeightedRHSL1PerSecond'] = initial_rhs
        preserve_context('initial weighted full RHS exceeds fixed gate')
        raise ValueError('initial full weighted RHS gate failed')
    I_quad, I_error = adaptive(lambda z: float(attachment(z)/detachment(z)), -R, R)
    alpha_quad = coefficient(I_quad, N)
    adaptive_moments, adaptive_errors = [], []
    for order in [0, 1, 2]:
        value, error = adaptive(lambda z: float(alpha_quad*attachment(z)/detachment(z)*
             (1. if order == 0 else ((1+z)/BETA if order == 1 else .5*(1+z)**2/BETA))), -R, R)
        adaptive_moments.append(value)
        adaptive_errors.append(error)
    if np.max(np.abs(initial-adaptive_moments)) > INITIAL_MOMENT_GATE:
        FAILED['initialAdaptiveMomentComparison'] = dict(mainMoments=initial,
            adaptiveMoments=adaptive_moments, absoluteDifferences=np.abs(initial-adaptive_moments))
        raise ValueError('adaptive initial-moment verification failed fixed spatial gate')
    CONTEXT['initialVerification'] = dict(R=R, count=count, pCa=pca, delta=delta,
        maxStepSeconds=max_step, N=N, I=I, adaptiveI=I_quad,
        adaptiveIErrorEstimate=I_error, weightedRHSL1PerSecond=initial_rhs,
        initialMoments=initial, adaptiveMoments=adaptive_moments,
        adaptiveMomentErrorEstimates=adaptive_errors,
        adaptiveMomentAbsoluteDifferences=np.abs(initial-adaptive_moments))
    remember_admitted(eqn, N, w, 'equilibrium before loading', {'main': x}, 0.)
    loaded = eq(x-delta)*((x-delta >= -R)&(x-delta <= R))
    z = x+delta
    ghost_mask = (z >= -R)&(z <= R)
    ghost = eq(x)*ghost_mask
    edge_a, edge_b = escaping_strip(R, -delta)
    edge_x, edge_w = gauss(edge_a, edge_b, EDGE_COUNT)
    edge = eq(edge_x-delta)*((edge_x-delta >= -R)&(edge_x-delta <= R))
    first_initial = np.r_[loaded, ghost, edge]
    coordinates = {'main': x, 'ghost': z, 'edge': edge_x}
    checked(first_initial, N, w, 'loading translated state', coordinates, 0.)
    escape_a, escape_b = escaping_strip(R, delta)
    loading_escape = []
    loading_errors = []
    for order in [0, 1, 2]:
        value, error = adaptive(lambda q: float(eq(q)*
            (1. if order == 0 else ((1+q+delta)/BETA if order == 1 else .5*(1+q+delta)**2/BETA))), escape_a, escape_b)
        loading_escape.append(value)
        loading_errors.append(error)
    loading = jump_record(initial, moments(loaded, x, w), delta, np.array(loading_escape))
    loading['adaptiveEscapeErrorEstimates'] = loading_errors
    CONTEXT.setdefault('admittedLedgers', {})['loading'] = loading
    remember_admitted(first_initial, N, w, 'loading after admitted ledger', coordinates, 0.)
    first, first_receipt = solve_segment(first_initial, N, x, w, coordinates,
        np.r_[f, attachment(z)*ghost_mask, attachment(edge_x)],
        np.r_[g, detachment(z), detachment(edge_x)], 0., .2, max_step)
    pre = first.validatedSamples[.2]
    remember_admitted(pre, N, w, 'reversal before', coordinates, .2)
    post = pre[count:2*count].copy()
    checked(post, N, w, 'reversal translated main', {'main': x}, .2)
    reversal_escape = moments(pre[2*count:], edge_x-delta, edge_w)
    reversal = jump_record(moments(pre[:count], x, w), moments(post, x, w), -delta, reversal_escape)
    CONTEXT['admittedLedgers']['reversal'] = reversal
    remember_admitted(post, N, w, 'reversal after admitted ledger', {'main': x}, .2)
    second, second_receipt = solve_segment(post, N, x, w, {'main': x}, f, g, .2, 1., max_step)
    matched, auxiliary = [], []
    for index, t in enumerate(TIMES):
        if index == 0:
            n = eqn
        elif index == 1:
            n = loaded
        elif index <= 6:
            state = first.validatedSamples[float(t)]
            n = state[:count]
            auxiliary.append(state[count:])
        elif index == 7:
            n = post
        else:
            n = second.validatedSamples[float(t)]
        # All entries already passed their interval gate before node admission;
        # a retrospective recheck must not change the admitted clock on failure.
        matched.append(n.copy())
    main = np.asarray(matched)
    auxiliary = np.asarray([first_initial[count:]]+auxiliary)
    record = dict(R=R, count=count, pCa=pca, delta=delta, N=N, maxStepSeconds=max_step,
                  I=I, adaptiveI=I_quad, adaptiveIErrorEstimate=I_error,
                  initialWeightedRHSL1PerSecond=initial_rhs,
                  initialAdaptiveMoments=adaptive_moments,
                  initialAdaptiveMomentErrorEstimates=adaptive_errors,
                  initialAdaptiveMomentAbsoluteDifferences=np.abs(initial-adaptive_moments),
                  matchedMoments=np.asarray([moments(n, x, w) for n in main]),
                  loading=loading, loadingEscapeAdaptiveErrorEstimates=loading_errors,
                  reversal=reversal, segments=[first_receipt, second_receipt])
    arrays = dict(x=x, weights=w, matchedDensity=main,
                  ghostCoordinates=z, edgeCoordinates=edge_x, edgeWeights=edge_w,
                  auxiliaryTimes=TIMES[[1, 2, 3, 4, 5, 6]], matchedAuxiliaryDensity=auxiliary,
                  firstAcceptedTimes=first.t, secondAcceptedTimes=second.t)
    return record, arrays


def encoded(value):
    if isinstance(value, np.ndarray):
        return encoded(value.tolist())
    if isinstance(value, np.generic):
        return encoded(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return repr(value)
    if isinstance(value, dict):
        return {k: encoded(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [encoded(v) for v in value]
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--protocol', type=Path, required=True)
    parser.add_argument('--protocol-commit', required=True)
    parser.add_argument('--compare-packet', type=Path)
    args = parser.parse_args()
    if len(args.protocol_commit) != 40 or any(c not in '0123456789abcdef' for c in args.protocol_commit):
        raise ValueError('provide full precommitted protocol identity')
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=True)
    receipt_path, archive_path = output/'summary.json', output/'matched-densities.npz'
    if receipt_path.exists() or archive_path.exists():
        raise FileExistsError('preserve an existing continuum reference packet')
    FAILED.clear()
    CONTEXT.clear()
    receipt = dict(result='RUNNING', scope='Source-informed finite-domain continuous-strain direct-CE reference; no PE/SE or SI calibration',
                   protocolCommit=args.protocol_commit, protocolPath=str(args.protocol.resolve()),
                   protocolSHA256=sha(args.protocol), sourceSHA256=sha(Path(__file__)),
                   environment=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
                   solver=SOLVER, driver='public SciPy DOP853 step API; matched interval samples gated before external admission',
                   solverControl='Normal embedded adaptive trial/error control retained; no external restart/retry after population, ledger or accuracy-gate failure',
                   maxStepsSeconds=MAX_STEPS, radii=RADII, nodeCounts=COUNTS,
                   parameters=dict(f1=52., g1=4., g2=21.1, E1=2., E2=-.6,
                                   w=.3, beta=.5, nH=3.1, Ca50Micromolar=.83),
                   edgeNodeCount=EDGE_COUNT, momentOrder=['B', 'F', 'E'],
                   gates=dict(timePair=TIME_GATES, quadraturePair=SPACE_GATE,
                              weightedInitialRHSL1PerSecond=INITIAL_RHS_GATE,
                              initialAdaptiveMomentAbsolute=INITIAL_MOMENT_GATE, jumpIdentity=JUMP_GATE,
                              population='strict finite/nonnegative density and main-only B<=N; no clipping'),
                   matchedTimesSeconds=TIMES, runs=[], timeRefinement=[], quadratureRefinement=[])
    stored = {'matchedTimesSeconds': TIMES}
    records = {}
    # Reserve both artifacts with literal exclusive modes before any kernel.
    # Preflight alone cannot protect against another writer between checks.
    output_handles = ExitStack()
    try:
        archive_handle = output_handles.enter_context(archive_path.open('xb'))
        receipt_handle = output_handles.enter_context(receipt_path.open('x'))
    except BaseException:
        output_handles.close()
        raise
    try:
        for R in RADII:
            for count in COUNTS:
                for pca in PCAS:
                    for delta in DELTAS:
                        pair = []
                        for step in MAX_STEPS:
                            name = f'R{R:g}-nodes{count}-pCa{pca:g}-delta{delta:g}-maxstep{step:g}'
                            record, arrays = run(R, count, pca, delta, step)
                            record['name'] = name
                            receipt['runs'].append(record)
                            records[R, count, pca, delta, step] = record
                            for key, value in arrays.items():
                                stored[name+'_'+key] = value
                            pair.append(record['matchedMoments'])
                            print(json.dumps(dict(run=name, weightedInitialRHSL1=record['initialWeightedRHSL1PerSecond'])), flush=True)
                        errors = np.max(np.abs(pair[0]-pair[1]), axis=0)
                        receipt['timeRefinement'].append(dict(R=R, count=count, pCa=pca, delta=delta, momentAbsoluteErrors=errors))
                        if np.any(errors > TIME_GATES):
                            FAILED['resolutionComparison'] = dict(kind='time', R=R, count=count,
                                pCa=pca, delta=delta, momentAbsoluteErrors=errors,
                                savedRuns=[records[R, count, pca, delta, step]['name'] for step in MAX_STEPS])
                            raise ValueError('fixed time-resolution moment gates failed')
        for R in RADII:
            for pca in PCAS:
                for delta in DELTAS:
                    moments_by_count = [records[R, count, pca, delta, MAX_STEPS[-1]]['matchedMoments'] for count in COUNTS]
                    errors = [np.max(np.abs(b-a), axis=0) for a, b in zip(moments_by_count[:-1], moments_by_count[1:])]
                    receipt['quadratureRefinement'].append(dict(R=R, pCa=pca, delta=delta, countPairMomentAbsoluteErrors=errors))
                    if np.max(errors) > SPACE_GATE:
                        FAILED['resolutionComparison'] = dict(kind='quadrature', R=R,
                            pCa=pca, delta=delta, countPairMomentAbsoluteErrors=errors,
                            savedRuns=[records[R, count, pca, delta, MAX_STEPS[-1]]['name'] for count in COUNTS])
                        raise ValueError('fixed quadrature-resolution moment gate failed')
        receipt['extentDiagnostics'] = [dict(pCa=pca, delta=delta,
            momentAbsoluteDifferences=np.max(np.abs(records[2.4, 800, pca, delta, .0005]['matchedMoments']-
                                                    records[3., 800, pca, delta, .0005]['matchedMoments']), axis=0))
            for pca in PCAS for delta in DELTAS]
        if args.compare_packet:
            packet = args.compare_packet.resolve()
            subject = json.loads((packet/'summary.json').read_text())
            z = np.load(packet/'matched-states.npz', allow_pickle=False)
            if not np.array_equal(z['matchedTimesSeconds'], TIMES):
                raise ValueError('comparison packet matched event/time schema differs')
            grid_R = {g['name']: float(g['R']) for g in subject['grids']}
            receipt['comparisonSourceHashes'] = {name: sha(packet/name) for name in ['summary.json', 'matched-states.npz']}
            comparisons = []
            for case in subject['cases']:
                reference = records[grid_R[case['grid']], 800, case['pCa'], case['delta'], .0005]['matchedMoments']
                p, x = z[case['name']], z[case['grid']+'_x']
                actual = np.array([[summed(n), summed(n*(1+x))/BETA, summed(.5*(1+x)**2*n)/BETA] for n in p])
                raw = np.max(np.abs(actual-reference), axis=0)
                net = np.max(np.abs((actual-actual[0])-(reference-reference[0])), axis=0)
                comparisons.append(dict(name=case['name'], grid=case['grid'], pCa=case['pCa'], delta=case['delta'], dt=case['dt'],
                    momentAbsoluteErrors=raw, baselineSubtractedMomentAbsoluteErrors=net,
                    forceErrorOverInitialForceIncrement=float(raw[1]/abs(actual[1, 1]-actual[0, 1])),
                    baselineSubtractedForceErrorOverInitialForceIncrement=float(net[1]/abs(actual[1, 1]-actual[0, 1]))))
            receipt['finiteBinComparisons'] = comparisons
            receipt['comparisonLimit'] = 'Moment comparisons only; bin masses and quadrature densities have no declared common nodal L1 map. No new response-error gate.'
        receipt['result'] = 'PASS_CONTINUUM_QUADRATURE_TIME_AND_TRANSLATION_GATES'
    except BaseException as exc:
        preserve_context(str(exc))
        receipt['result'] = 'FAIL_CONTINUUM_REFERENCE_GATES'
        receipt['failure'] = dict(type=type(exc).__name__, message=str(exc), traceback=traceback.format_exc(), completedRuns=len(receipt['runs']))
        raise
    finally:
        if FAILED:
            if 'density' in FAILED:
                stored['failedWitnessDensity'] = FAILED['density']
                stored['failedWitnessMainWeights'] = FAILED['mainWeights']
                for key, value in FAILED['coordinates'].items():
                    stored['failedWitnessCoordinate_'+key] = value
            receipt['failedWitness'] = {key: value for key, value in FAILED.items() if key not in ['density', 'mainWeights', 'coordinates', 'lastAdmitted', 'segmentPrefixes', 'attemptedStep']}
            if 'density' in FAILED:
                receipt['failedWitness']['array'] = identity(FAILED['density'])
                receipt['failedWitness']['npzKeys'] = ['failedWitnessDensity', 'failedWitnessMainWeights']
            if 'lastAdmitted' in FAILED:
                admitted = FAILED['lastAdmitted']
                stored['lastAdmittedDensity'] = admitted['density']
                stored['lastAdmittedMainWeights'] = admitted['mainWeights']
                for key, value in admitted['coordinates'].items():
                    stored['lastAdmittedCoordinate_'+key] = value
                receipt['failedWitness']['lastAdmitted'] = {key: value for key, value in admitted.items() if key not in ['density', 'mainWeights', 'coordinates']}
                receipt['failedWitness']['lastAdmitted']['array'] = identity(admitted['density'])
            if 'attemptedStep' in FAILED:
                attempted = FAILED['attemptedStep']
                receipt['failedWitness']['attemptedStep'] = {key: value for key, value in attempted.items() if key != 'density'}
                if 'density' in attempted:
                    stored['failedAttemptedStepDensity'] = attempted['density']
                    receipt['failedWitness']['attemptedStep']['array'] = identity(attempted['density'])
            if 'segmentPrefixes' in FAILED:
                prefixes = {}
                for key, prefix in FAILED['segmentPrefixes'].items():
                    name = 'failedAdmittedPrefix-'+key
                    states = np.asarray(prefix['states'])
                    stored[name+'-times'] = np.asarray(prefix['times'])
                    stored[name+'-densities'] = states
                    stored[name+'-matchedTimes'] = np.asarray(prefix['matchedTimes'])
                    stored[name+'-matchedDensities'] = np.asarray(prefix['matchedStates'])
                    stored[name+'-mainWeights'] = prefix['mainWeights']
                    for coordinate, value in prefix['coordinates'].items():
                        stored[name+'-coordinate-'+coordinate] = value
                    prefixes[key] = dict(npzPrefix=name, acceptedNodes=len(prefix['times']),
                        acceptedTerminalSeconds=prefix['times'][-1], matchedSamples=len(prefix['matchedTimes']),
                        stateArray=identity(states))
                receipt['failedWitness']['admittedPrefixes'] = prefixes
        try:
            np.savez_compressed(archive_handle, **stored)
            archive_handle.flush()
            receipt['matchedDensitiesSHA256'] = sha(archive_path)
            receipt_handle.write(json.dumps(encoded(receipt), indent=2, allow_nan=False)+'\n')
            receipt_handle.flush()
            print(json.dumps(dict(result=receipt['result'], completedRuns=len(receipt['runs']), failure=receipt.get('failure'))), flush=True)
        finally:
            output_handles.close()


if __name__ == '__main__':
    main()
