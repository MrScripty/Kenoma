"""Original derivative scope; read-only coarse reclassification, eligible fine only."""
import json
import subprocess
import traceback
import numpy as np

import source_amplitude_p2_p1 as previous

ROOT = previous.ROOT
OLD = ROOT/'data/anatomical-arm-v1/review/source-amplitude-p2-p1'
OUT = ROOT/'data/anatomical-arm-v1/review/source-amplitude-p2-p1-v2'
FIRST_SPECTRUM = previous.spectrum


def original_scope(curve):
    curve = json.loads(json.dumps(previous.serial(curve)))
    for check in curve['gradientChecks']:
        check['firstWrapperPassed'] = check['passed']
        for side in check['sides']:
            side['firstWrapperPassed'] = side['passed']
            side['passed'] = bool(side['maximumAssemblyDifferenceN'] <= 2e-6 and side['weakPressureRMS'] <= 1e-6
                                  and .98 <= side['Jmin'] <= side['Jmax'] <= 1.02 and side['strictCrossings'] == 0)
            side['pointwisePressureScope'] = 'DIAGNOSTIC_NONSTATIONARY_PROBE; EQUILIBRIUM_GATE_UNCHANGED'
        check['passed'] = bool(check['independentGradientRelativeError'] <= 1e-4 and all(s['passed'] for s in check['sides']))
    curve['derivativeGatesPass'] = all(c['passed'] for c in curve['gradientChecks'])
    curve['classification'] = ('NEGATIVE_STATIONARY_DIRECTION' if curve['lowestEigenvaluesNPerM'][0] < 0 else 'POSITIVE_SAMPLED_FULL_SPECTRUM') if curve['derivativeGatesPass'] else 'UNQUALIFIED_DERIVATIVE_FAILURE'
    curve['gateScopeSource'] = 'tools/verify_full_p2_p1.py; stationary pointwise pressure gate does not apply to arbitrary derivative probes'
    return curve


def qualified_spectrum(body, x, state):
    return original_scope(FIRST_SPECTRUM(body, x, state))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if (OUT/'summary.json').exists() or list(OUT.glob('*-request.json')):
        raise RuntimeError('Preserve earlier successor execution')
    previous.OUT = OUT
    previous.spectrum = qualified_spectrum
    coarse_path = OLD/'coarse-1.25.json'
    coarse = json.loads(coarse_path.read_text())
    for name, digest in coarse['sourceHashes'].items():
        assert previous.digest(ROOT/name) == digest, name
    assert coarse['stationaryAccepted'] and all(g['passed'] for g in coarse['stationarityGates'])
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    hashes = {**coarse['sourceHashes'], **{p: previous.digest(ROOT/p) for p in [
        'tools/source_amplitude_p2_p1_v2.py', 'tools/verify_full_p2_p1.py',
        'research/mechanical-closure/source-amplitude-gate-scope-correction.md']}}
    coarse['spectrum'] = original_scope(coarse['spectrum'])
    coarse.update(derivativeGatesPass=coarse['spectrum']['derivativeGatesPass'],
                  fineEligible=coarse['spectrum']['derivativeGatesPass'],
                  result='PASS_STATIONARY_ORIGINAL_DERIVATIVE_GATES' if coarse['spectrum']['derivativeGatesPass'] else 'REJECTED_ORIGINAL_DERIVATIVE_GATES',
                  reclassificationSourceCommit=commit, reclassificationSourceHashes=hashes,
                  originalReceiptSHA256=previous.digest(coarse_path), repeatedCoarseSolve=False)
    previous.save('coarse-1.25-reclassification.json', coarse)
    print('RECLASSIFICATION', coarse['result'], 'existing force residual', coarse['terminal']['forceResidualN'], flush=True)
    rejected_path = OLD/'coarse-1.01.json'
    rejected = json.loads(rejected_path.read_text())
    assert not rejected['stationaryAccepted']
    skips = [dict(name='fine-1.01', reason='Retained coarse pointwise pressure rejection', originalReceiptSHA256=previous.digest(rejected_path))]
    records = [coarse]
    refinement = []
    if coarse['fineEligible']:
        mesh = previous.model.mesh((8, 2, 2))
        previous.save('fine-mesh.json', dict(sourceCommit=commit, sourceHashes=hashes, mesh=mesh))
        fine = previous.case('fine', mesh, 1.25, hashes, commit)
        records.append(fine)
        if fine['fineEligible']:
            cm = json.loads((OLD/'coarse-mesh.json').read_text())['mesh']
            cm = {k: np.array(v) if isinstance(v, list) else v for k, v in cm.items()}
            positions = previous.interpolate(cm, np.array(coarse['terminalPositionsM']), mesh['X'])
            difference = float(np.linalg.norm(positions-np.array(fine['terminalPositionsM']), axis=1).max())
            force = abs(coarse['replays']['256']['capForceN']-fine['replays']['256']['capForceN'])/abs(fine['replays']['256']['capForceN'])
            j = max(abs(coarse['terminal'][k]-fine['terminal'][k]) for k in ['Jmin', 'Jmax'])
            ratio = fine['coupling']['beta']/coarse['coupling']['beta']
            refinement.append(dict(stretch=1.25, maximumInterpolatedPositionDifferenceM=difference, relativeCapForceDifference=force,
                                   JExtremaDifference=j, infSupBetaRatio=ratio, infSupTrendConcern=ratio < .5,
                                   matchedStaticRefinementPass=bool(difference <= .0005 and force <= .01 and j <= .005)))
        else:
            refinement.append(dict(stretch=1.25, result='UNQUALIFIED_FINE_GATE_REJECTION'))
    else:
        skips.append(dict(name='fine-1.25', reason='Original coarse derivative scope still failed'))
    cases = [dict(name=r['name'], result=r['result'], stationaryAccepted=r['stationaryAccepted'],
                  derivativeGatesPass=r['derivativeGatesPass'], forceResidualN=r.get('terminal', {}).get('forceResidualN'),
                  capForceN=r.get('replays', {}).get('256', {}).get('capForceN'), Jmin=r.get('terminal', {}).get('Jmin'), Jmax=r.get('terminal', {}).get('Jmax'),
                  curvatureClassification=None if r.get('spectrum') is None else r['spectrum']['classification'],
                  minimumEigenvalueNPerM=None if r.get('spectrum') is None else r['spectrum']['lowestEigenvaluesNPerM'][0],
                  passiveStationary=None if r.get('passiveControl') is None else r['passiveControl']['stationaryAccepted'],
                  passiveDerivativePass=None if r.get('passiveControl') is None or r['passiveControl']['spectrum'] is None else r['passiveControl']['spectrum']['derivativeGatesPass'],
                  passiveMinimumNPerM=None if r.get('passiveControl') is None or r['passiveControl']['spectrum'] is None else r['passiveControl']['spectrum']['lowestEigenvaluesNPerM'][0]) for r in records]
    previous.save('summary.json', dict(sourceCommit=commit, sourceHashes=hashes, cases=cases, refinement=refinement, skipped=skips,
                                      retainedNearReferenceRejection=dict(receiptSHA256=previous.digest(rejected_path), forceResidualN=rejected['terminal']['forceResidualN'],
                                                                        pointwisePressureRMS=rejected['replays']['256']['pointwisePressureRMS']),
                                      priorEquivalenceSHA256=previous.digest(OLD/'equivalence-control.json'),
                                      physicalHistoryAdvanced=False, repeatedCoarseSolve=False,
                                      scope='COMPOSITE_EDUCATIONAL_STATIC_AMPLITUDE_ONLY; NO_SPECIMEN_ARM_OR_CLINICAL_VALIDATION'))
    print('COMPLETE_SUCCESSOR', json.dumps(previous.serial(cases)), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        if OUT.is_dir() and not (OUT/'unexpected-run-failure.json').exists():
            previous.save('unexpected-run-failure.json', dict(result='EXCEPTION_NO_ADVANCEMENT', traceback=traceback.format_exc(), physicalHistoryAdvanced=False))
        raise
