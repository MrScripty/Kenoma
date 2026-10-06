"""Source-derived nonhuman fixed-capacity kinetic fixture, not an arm law.

Bin masses with exact Gaussian cell rates, midpoint detachment, positive
backward Euler and explicit center-mass boundary detachment. No optimization.
"""
import hashlib
import json
import platform
import subprocess
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import quad
from scipy.linalg import expm
from scipy.special import ndtr

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/anatomical-arm-v1/review/two-state-kinetics'
PARAM = dict(f1=52., g1=4., g2=21.1, E1=2., E2=-.6, w=.3,
             beta=.5, nH=3.1, Ca50M=.83e-6)
TIMES = np.array([0., .008, .02, .04, .1, .2, .5, 1.])
DELTAS = [.001, -.001, .0005, -.0005]
PCA = [4.5, 6.1]
DTS = [.004, .002, .001]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def attachment(x):
    return PARAM['f1'] * np.exp(-np.asarray(x)**2 / (2*PARAM['w']**2)) / (np.sqrt(2*np.pi)*PARAM['w'])


def detachment(x):
    return PARAM['g1']*np.exp(-PARAM['E1']*np.asarray(x)) + PARAM['g2']*np.exp(-PARAM['E2']*np.asarray(x))


def capacity(pca):
    return 1 / (1 + (PARAM['Ca50M'] / 10**(-pca))**PARAM['nH'])


def grid(radius, dx):
    count = int(round(2*radius/dx))
    edges = np.linspace(-radius, radius, count+1)
    assert abs(edges[1]-edges[0]-dx) < 1e-14
    x = (edges[:-1]+edges[1:])/2
    lo, hi = edges[:-1]/PARAM['w'], edges[1:]/PARAM['w']
    # Survival CDF on the positive half avoids cancellation of tiny tail rates.
    cells = np.where(lo >= 0, ndtr(-lo)-ndtr(-hi), ndtr(hi)-ndtr(lo))
    rates = PARAM['f1']*cells
    assert np.all(rates > 0)
    return x, rates, detachment(x)


def validate(y, N):
    if not (np.isfinite(N) and 0 < N <= 1):
        raise ValueError('invalid fixed capacity')
    if not np.all(np.isfinite(y)) or np.any(y < 0):
        raise ValueError('nonfinite or negative population; no clipping')
    if abs(float(np.sum(y))-N) > 2e-12:
        raise ValueError('population mass gate failed')


def equilibrium(Fi, gi, N):
    d = N/(1+np.sum(Fi/gi))
    y = np.r_[d*Fi/gi, d]
    validate(y, N)
    return y


def rhs(y, Fi, gi):
    v = Fi*y[-1]-gi*y[:-1]
    return np.r_[v, -np.sum(v)]


def force(y, x):
    return float(np.dot(1+x, y[:-1])/PARAM['beta'])


def shift(y, N, x, dx, delta):
    validate(y, N)
    if not np.isfinite(delta) or not 0 < abs(delta) < dx:
        raise ValueError('shift must be finite, nonzero and smaller than one bin')
    r = abs(delta)/dx
    out = np.r_[(1-r)*y[:-1], y[-1]]
    if delta > 0:
        out[1:-1] += r*y[:-2]
        lost = r*y[-2]
        escaped_center = x[-1]+dx
    else:
        out[:-2] += r*y[1:-1]
        lost = r*y[0]
        escaped_center = x[0]-dx
    out[-1] += lost
    lost_moment = lost*(1+escaped_center)
    validate(out, N)
    prediction = (np.sum(y[:-1])*delta-lost_moment)/PARAM['beta']
    err = abs(force(out, x)-force(y, x)-prediction)
    return out, dict(escapedMass=float(lost), escapedDiscreteMoment=float(lost_moment),
                     escapedNormalizedMoment=float(lost_moment/PARAM['beta']),
                     escapedDestinationCenter=float(escaped_center),
                     immediateForceIncrement=force(out, x)-force(y, x),
                     discreteMomentPrediction=float(prediction), momentIdentityError=float(err))


def backward_euler(y, N, Fi, gi, dt):
    validate(y, N)
    if not np.isfinite(dt) or dt <= 0:
        raise ValueError('invalid positive timestep')
    a = 1/(1+dt*gi)
    d = (y[-1]+np.dot(1-a, y[:-1]))/(1+dt*np.dot(a, Fi))
    candidate = np.r_[a*(y[:-1]+dt*Fi*d), d]
    validate(candidate, N)
    return candidate


def generator(Fi, gi):
    A = np.zeros((len(Fi)+1, len(Fi)+1))
    A[:-1, :-1] = -np.diag(gi)
    A[:-1, -1] = Fi
    A[-1, :-1] = gi
    A[-1, -1] = -np.sum(Fi)
    return A


def integrate(y0, N, x, Fi, gi, dt):
    y = y0.copy()
    sampled = [y.copy()]
    steps_at = {int(round(t/dt)): k for k, t in enumerate(TIMES[1:], 1)}
    assert all(abs(round(t/dt)*dt-t) < 1e-13 for t in TIMES)
    mass_max = abs(float(np.sum(y))-N)
    minimum = float(np.min(y))
    accepted_time = 0.
    for step in range(1, int(round(1/dt))+1):
        candidate = backward_euler(y, N, Fi, gi, dt)
        # Only a validated candidate becomes the state and accepted time.
        y = candidate
        accepted_time = step*dt
        mass_max = max(mass_max, abs(float(np.sum(y))-N))
        minimum = min(minimum, float(np.min(y)))
        if step in steps_at:
            sampled.append(y.copy())
    assert accepted_time == 1. and len(sampled) == len(TIMES)
    states = np.array(sampled)
    return states, dict(acceptedSteps=int(round(1/dt)), acceptedTimeSeconds=accepted_time,
                        allStepMassErrorMax=mass_max, allStepMinimumPopulation=minimum,
                        terminalKineticResidualL1PerSecond=float(np.sum(np.abs(rhs(y, Fi, gi)))),
                        matchedForces=[force(z, x) for z in states])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if (OUT/'summary.json').exists() or (OUT/'matched-states.npz').exists():
        raise RuntimeError('refusing to overwrite an existing experiment receipt')
    refs = ['tools/two_state_kinetics.py', 'research/mechanical-closure/two-state-benchmark-protocol.md',
            'research/mechanical-closure/source-rendering-evidence.md',
            'research/mechanical-closure/two-state-source-convention-audit.md']
    record = dict(result='RUNNING', scope='Nonhuman equation-only direct-CE fixed-capacity kinetic fixture',
                  executionCommit=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
                  sourceHashes={p: sha(ROOT/p) for p in refs}, parameters=PARAM,
                  source='https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1014748',
                  environment=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
                  matchedTimesSeconds=TIMES.tolist(), grids=[], cases=[], refinements={})
    stored = {'matchedTimesSeconds': TIMES}
    try:
        I, ie = quad(lambda x: float(attachment(x)/detachment(x)), -8, 8, epsabs=1e-12, epsrel=1e-12)
        moment, me = quad(lambda x: float(x*attachment(x)/detachment(x)), -8, 8, epsabs=1e-12, epsrel=1e-12)
        base_unit = (I+moment)/((1+I)*PARAM['beta'])
        record['continuousQuadrature'] = dict(I=I, xMomentIntegral=moment, IErrorEstimate=ie,
                                               momentErrorEstimate=me, baselineForceAtN1=base_unit,
                                               attachedAtN1=I/(1+I))
        assert max(ie, me) < 1e-10
        for R in [2.4, 3.0]:
            for dx in [.04, .02, .01]:
                name = f'R{R:g}-dx{dx:g}'
                x, Fi, gi = grid(R, dx)
                eq = equilibrium(Fi, gi, 1.)
                A = generator(Fi, gi)
                assert np.max(np.abs(np.sum(A, axis=0))) < 1e-12
                qres = float(np.sum(np.abs(rhs(eq, Fi, gi))))
                assert qres <= 1e-10
                shifted, losses = zip(*(shift(eq, 1., x, dx, d) for d in DELTAS))
                shifted = np.array(shifted)
                exact = np.array([shifted if t == 0 else (expm(t*A)@shifted.T).T for t in TIMES])
                ref_mass = float(np.max(np.abs(np.sum(exact, axis=2)-1)))
                ref_min = float(np.min(exact))
                assert ref_mass <= 2e-12 and ref_min >= -2e-14
                stored[name+'-x'] = x
                stored[name+'-Fi'] = Fi
                stored[name+'-gi'] = gi
                stored[name+'-equilibrium-N1'] = eq
                stored[name+'-exponential-N1'] = exact
                base = force(eq, x)
                grecord = dict(name=name, radius=R, dx=dx, bins=len(x),
                               equilibriumForceAtN1=base, equilibriumAttachedAtN1=float(np.sum(eq[:-1])),
                               equilibriumResidualL1PerSecond=qres,
                               equilibriumForceErrorRelative=abs(base-base_unit)/abs(base_unit),
                               gaussianAttachmentTruncationFraction=float(2*ndtr(-R/PARAM['w'])),
                               exponentialMassErrorMax=ref_mass, exponentialMinimumPopulation=ref_min)
                record['grids'].append(grecord)
                print(json.dumps(dict(grid=name, baselineForceN1=base, referenceMassError=ref_mass)), flush=True)
                for pca in PCA:
                    N = capacity(pca)
                    for j, delta in enumerate(DELTAS):
                        for dt in DTS:
                            cname = name+f'-pCa{pca:g}-shift{delta:g}-dt{dt:g}'
                            states, c = integrate(N*shifted[j], N, x, Fi, gi, dt)
                            stored[cname] = states
                            reference_force = np.array([force(z, x) for z in N*exact[:, j]])
                            error = float(np.max(np.abs(np.array(c['matchedForces'])-reference_force)))
                            terminal_diff = abs(c['matchedForces'][-1]-N*base)
                            # Loss/identity scales linearly with fixed accessible population N.
                            loss = {k: float(v*N) if k != 'escapedDestinationCenter' else v for k,v in losses[j].items()}
                            c.update(name=cname, grid=name, pCa=pca, capacity=N, delta=delta, dt=dt,
                                     baselineForce=N*base, boundary=loss, matchedReferenceForces=reference_force.tolist(),
                                     maximumMatchedForceError=error,
                                     normalizedTemporalForceError=error/(abs(delta)*N/PARAM['beta']),
                                     terminalForceDifferenceFromOriginalEquilibrium=terminal_diff,
                                     terminalStateL1DifferenceFromOriginalEquilibrium=float(np.sum(np.abs(states[-1]-N*eq))))
                            record['cases'].append(c)
                            assert c['allStepMassErrorMax'] <= 2e-12 and c['allStepMinimumPopulation'] >= 0
                            assert c['terminalKineticResidualL1PerSecond'] <= 1e-10
                            assert terminal_diff <= 1e-10
                            assert loss['momentIdentityError'] <= 1e-12
                            assert loss['escapedMass'] <= 1e-10 and abs(loss['escapedNormalizedMoment']) <= 1e-10
                            if dt == .001:
                                assert c['normalizedTemporalForceError'] <= .05
        ratios = []
        for R in [2.4, 3.0]:
            for pca in PCA:
                group = [g for g in record['grids'] if g['radius'] == R]
                errs = [g['equilibriumForceErrorRelative'] for g in group]
                sr = [errs[i+1]/errs[i] for i in [0, 1]]
                assert all(.2 <= q <= .8 for q,e in zip(sr, errs) if e > 1e-12)
                assert errs[-1] <= 1e-4
                record['refinements'][f'R{R:g}-pCa{pca:g}-spatial'] = dict(relativeEquilibriumForceErrors=errs, ratios=sr)
        by = {(c['grid'], c['pCa'], c['delta'], c['dt']): c for c in record['cases']}
        for g in record['grids']:
            for pca in PCA:
                for delta in DELTAS:
                    errs = [by[g['name'], pca, delta, dt]['maximumMatchedForceError'] for dt in DTS]
                    tr = [errs[i+1]/errs[i] for i in [0, 1]]
                    assert all(.3 <= q <= .8 for q,e in zip(tr, errs) if e > 1e-12)
                    ratios.extend(tr)
        ext_err = 0.
        for dx in [.04, .02, .01]:
            for pca in PCA:
                for delta in DELTAS:
                    for dt in DTS:
                        a = by[f'R2.4-dx{dx:g}', pca, delta, dt]['matchedForces']
                        b = by[f'R3-dx{dx:g}', pca, delta, dt]['matchedForces']
                        ext_err = max(ext_err, float(np.max(np.abs(np.array(a)-b))))
        assert ext_err <= 1e-8
        record['refinements']['temporalRatiosRange'] = [min(ratios), max(ratios)]
        record['refinements']['maxMatchedExtentForceDifference'] = ext_err
        record['result'] = 'PASS_FIXED_CAPACITY_KINETIC_TRANSPORT_BENCHMARK'
    except Exception as exc:
        record['result'] = 'FAIL_FIXED_CAPACITY_KINETIC_TRANSPORT_BENCHMARK'
        record['failure'] = dict(type=type(exc).__name__, message=str(exc), completedCases=len(record['cases']))
        raise
    finally:
        np.savez_compressed(OUT/'matched-states.npz', **stored)
        record['matchedStatesSHA256'] = sha(OUT/'matched-states.npz')
        (OUT/'summary.json').write_text(json.dumps(record, indent=2)+'\n')
        print(json.dumps(dict(result=record['result'], cases=len(record['cases']), grids=len(record['grids']),
                              refinements=record['refinements'], failure=record.get('failure')), indent=2), flush=True)


if __name__ == '__main__':
    main()
