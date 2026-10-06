"""Read-only operators, one frozen reproduction, optional original-budget fine diagnostic.

All outputs are additive; rejected states never become accepted evidence here.
"""
import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path

import numpy as np
from scipy.linalg import cho_solve, eigh, solve

import source_amplitude_p2_p1 as amplitude
from run_full_p2_p1 import serial, interpolate

ROOT = amplitude.ROOT
OUT = ROOT/'data/anatomical-arm-v1/review/pressure-residual-diagnosis'
OLD = ROOT/'data/anatomical-arm-v1/review/source-amplitude-p2-p1'
FINE = ROOT/'data/anatomical-arm-v1/review/source-amplitude-p2-p1-v2'


def read(path):
    return json.loads(path.read_text())


def mesh(path):
    return {k: np.array(v) if isinstance(v, list) else v for k, v in read(path)['mesh'].items()}


def metrics(body, x, pressure=None):
    r = body.evaluate(x)
    p = r['p'] if pressure is None else pressure
    F = np.einsum('eni,eqna->eqia', x[body.m['tets']], body.grad)
    J = np.linalg.det(F)
    log = np.log(J)
    pq = p[body.pi]@body.L.T
    mismatch = log-pq/body.material['bulk']
    w, V = body.w, body.volume
    mean = lambda a: float(np.sum(w*a)/V)
    rms = lambda a: float(np.sqrt(mean(a*a)))
    weak_local = np.einsum('qi,eq,eq->ei', body.L, mismatch, w)
    weak = np.zeros(body.m['nv']); np.add.at(weak, body.pi, weak_local)
    return dict(forceResidualN=r['residual'], weakPressureRMS=float(np.sqrt(max(0, weak@cho_solve(body.Mfactor, weak)/V))),
                pointwisePressureRMS=rms(mismatch), referenceVolumeM3=V,
                deformedVolumeM3=float(np.sum(w*J)), meanVolumeChange=mean(J-1),
                localVolumeChangeRMS=rms(J-1), meanLogJ=mean(log), logJRMS=rms(log),
                representedLogJRMS=rms(pq/body.material['bulk']),
                projectionOrthogonality=mean(mismatch*pq/body.material['bulk']),
                meanCompatibilityResidual=mean(mismatch), maxAbsCompatibilityResidual=float(abs(mismatch).max()),
                equivalentPressureMismatchRMSPa=body.material['bulk']*rms(mismatch),
                pressureMinPa=float(p.min()), pressureMaxPa=float(p.max()),
                Jmin=r['Jmin'], Jmax=r['Jmax'], quadraturePoints=len(body.L))


def checks(body, x, state, initial, analytic):
    replays, gates = amplitude.stationarity(body, x, state, initial, analytic)
    return dict(replays=replays, gates=gates,
                passedOriginalStationarityGates=all(g['passed'] for g in gates))


def frozen_metrics(m, x, pressure):
    return [metrics(amplitude.ExplicitBody(m, amplitude.ANCHOR, 1., depth=d), x, pressure)
            for d in [1, 2, 3]]


def sensitivity(body, x, analytic_x):
    r = body.evaluate(x, True); free = body.m['free']
    g = r['g'][free]
    delta = solve(r['H'], -g, assume_a='sym')
    direction = np.zeros(x.size); direction[free] = delta
    proposal = x+direction.reshape(x.shape)
    eig = eigh(r['H'], eigvals_only=True)
    return dict(label='ONE_POSTSTOP_NEWTON_PROPOSAL_DIAGNOSTIC_ONLY_NO_ACCEPTANCE',
                smallestAlgebraicEigenvalueNPerM=float(eig[0]),
                smallestAbsoluteEigenvalueNPerM=float(abs(eig).min()),
                largestAbsoluteEigenvalueNPerM=float(abs(eig).max()),
                eigenvalueConditionRatio=float(abs(eig).max()/abs(eig).min()),
                negativeEigenvalueCount=int((eig<0).sum()),
                linearRelativeResidual=float(np.linalg.norm(r['H']@delta+g)/np.linalg.norm(g)),
                proposedMaximumNodeCorrectionM=float(np.linalg.norm(direction.reshape(x.shape), axis=1).max()),
                proposalMetrics=metrics(body, proposal),
                distanceFromHomogeneousMaximumNodeM=float(np.linalg.norm(x-analytic_x, axis=1).max()),
                proposedDistanceFromHomogeneousMaximumNodeM=float(np.linalg.norm(proposal-analytic_x, axis=1).max()))


def save(name, data):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT/name).open('x') as f:
        json.dump(serial(data), f, indent=2, allow_nan=False); f.write('\n')


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('stage', choices=['coarse', 'fine', 'fine-recovery'])
    args = parser.parse_args(); start = time.time()
    original = read(OLD/'coarse-1.01.json'); req = read(OLD/'coarse-1.01-request.json')
    for name, digest in req['sourceHashes'].items():
        assert amplitude.digest(ROOT/name) == digest, name
    old_hashes = {str(p.relative_to(ROOT)): amplitude.digest(p) for directory in [OLD, FINE] for p in directory.rglob('*') if p.is_file()}
    m = mesh(OLD/'coarse-mesh.json') if args.stage == 'coarse' else mesh(FINE/'fine-mesh.json')
    body = amplitude.ExplicitBody(m, req['material'], req['activation'])
    initial, analytic_x, analytic = body.initial(1.01)
    if args.stage == 'coarse':
        assert np.array_equal(initial, req['initialPositionsM'])
    save(args.stage+'-request.json', dict(stage=args.stage, sourceCommit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
         frozenCommit='dc9f22cbc8e0b04fceb062a6e0e7ab0bb8db6d16', frozenTree='90527b2013c4a2a08798a48ca87c82b8ce9f8e91',
         runnerSHA256=amplitude.digest(Path(__file__)), sourceHashes=req['sourceHashes'], previousPacketHashes=old_hashes,
         originalMaxIterations=80, originalBacktracking=24, originalForceGateN=1e-4, originalPressureGate=1e-6,
         initialPositionsM=initial, mesh=m, material=req['material'], activation=req['activation'],
         disposition='DIAGNOSTIC_ONLY; ORIGINAL_COARSE_REJECTION_PRESERVED; NO_HISTORY_ADVANCEMENT'))
    print('START', args.stage, flush=True)
    x, state, history, reason = body.newton(initial)
    save(args.stage+'-solver-terminal.json', dict(reason=reason, history=history,
         terminalPositionsM=x, terminalPressurePa=state['p'], forceResidualN=state['residual'],
         pointwisePressureRMS=state['pointwiseRMS'], label='DIAGNOSTIC_ONLY_NO_ACCEPTANCE',
         recoveryOfExporterException=(args.stage == 'fine-recovery')))
    print('SOLVER_TERMINAL', args.stage, reason, len(history)-1, state['residual'], state['pointwiseRMS'], flush=True)
    output = dict(stage=args.stage, reason=reason, history=history, terminalPositionsM=x, terminalPressurePa=state['p'],
                  metrics=metrics(body, x), quadratureFrozenPressure=frozen_metrics(m, x, state['p']),
                  originalGateChecks=checks(body, x, state, initial, analytic),
                  homogeneousMetrics=metrics(body, analytic_x), analytic=analytic,
                  homogeneousGateChecks=checks(body, analytic_x, body.evaluate(analytic_x), initial, analytic),
                  sensitivity=sensitivity(body, x, analytic_x) if args.stage == 'coarse' else
                     dict(label='NOT_ATTEMPTED_RECOVERY; FIRST_UNACCEPTED_PROPOSAL_HIT_GEOMETRY_GUARD'),
                  disposition='DIAGNOSTIC_ONLY; NO_ACCEPTANCE_OR_STABILITY_CLASSIFICATION')
    if args.stage == 'coarse':
        output['maximumPositionDifferenceFromOriginalM'] = float(abs(x-original['terminalPositionsM']).max())
        output['forceDifferenceFromOriginalN'] = state['residual']-original['terminal']['forceResidualN']
    else:
        coarse = read(OUT/'coarse.json'); cm = mesh(OLD/'coarse-mesh.json')
        interp = interpolate(cm, np.array(coarse['terminalPositionsM']), m['X'])
        output['coarseFineMaximumNodeDifferenceM'] = float(np.linalg.norm(interp-x, axis=1).max())
    assert all(amplitude.digest(ROOT/name) == digest for name, digest in old_hashes.items())
    output['previousPacketHashesUnchanged'] = True
    output['elapsedSeconds'] = time.time()-start
    save(args.stage+'.json', output)
    print('COMPLETE', args.stage, json.dumps(output['metrics']), flush=True)
    print('SENSITIVITY', json.dumps(output['sensitivity']), flush=True)


if __name__ == '__main__':
    main()
