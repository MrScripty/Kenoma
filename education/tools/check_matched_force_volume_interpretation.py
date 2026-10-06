#!/usr/bin/env python3
"""Read-only volume-Gram interpretation audit; no Hessian or new solve."""
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
from scipy.linalg import cho_solve

import full_p2_p1 as model

ROOT = Path(__file__).resolve().parents[1]
FROZEN = 'f2504e871b9ee4b536e94405612efa2436d39b45'
OLD = ROOT/'data/anatomical-arm-v1/review/matched-force-contractile-state'
OUT = ROOT/'data/anatomical-arm-v1/review/matched-force-volume-interpretation'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    paths = [OLD/'summary.json', OLD/'frozen-mode-inspection.json',
             ROOT/'data/anatomical-arm-v1/review/source-amplitude-p2-p1-v2/coarse-1.25-reclassification.json',
             ROOT/'data/anatomical-arm-v1/review/source-amplitude-p2-p1/coarse-mesh.json',
             ROOT/'tools/full_p2_p1.py', ROOT/'web/anatomical-material.mjs',
             ROOT/'research/mechanical-closure/full-p2-p1-protocol.md']
    bindings = {}
    for path in paths:
        relative = str(path.relative_to(ROOT))
        frozen_bytes = subprocess.check_output(['git', 'show', FROZEN+':education/'+relative], cwd=ROOT)
        assert hashlib.sha256(frozen_bytes).hexdigest() == digest(path), relative
        bindings[relative] = digest(path)
    summary = json.loads(paths[0].read_text())
    archived = summary['block']['diagnosisNPerM']
    base = json.loads(paths[2].read_text())
    mesh = {k: np.asarray(v) for k, v in json.loads(paths[3].read_text())['mesh'].items()}
    body = model.Body(mesh, depth=2)
    x = np.asarray(base['terminalPositionsM'])
    v = np.asarray(base['spectrum']['witnessDirection'])
    assert np.max(abs(v[mesh['cap']])) == 0
    assert abs(np.linalg.norm(v)-1) <= 1e-12
    F = np.einsum('eni,eqna->eqia', x[mesh['tets']], body.grad)
    dF = np.einsum('eni,eqna->eqia', v[mesh['tets']], body.grad)
    dlogJ = np.einsum('eqai,eqia->eq', np.linalg.inv(F), dF)
    # Independently reconstruct the P1 L2 projection of this scalar direction.
    local = np.einsum('qi,eq,eq->ei', body.L, dlogJ, body.w)
    b = np.zeros(mesh['nv'])
    np.add.at(b, body.pi, local)
    coefficients = cho_solve(body.Mfactor, b)
    projected = coefficients[body.pi]@body.L.T
    remainder = dlogJ-projected
    K = float(base['material']['bulk'])
    full = float(K*np.sum(body.w*dlogJ**2))
    represented = float(K*np.sum(body.w*projected**2))
    complement = float(K*np.sum(body.w*remainder**2))
    alternative_represented = float(K*b@coefficients)
    reconstructed_rms = float(np.sqrt(np.sum(body.w*dlogJ**2)/body.volume))
    from_archived_rms = K*body.volume*archived['logJDirectionalRMSPerM']**2
    checks = dict(
        sourceHashesMatchFrozen=True,
        RMSAbsoluteDifferencePerM=abs(reconstructed_rms-archived['logJDirectionalRMSPerM']),
        fullGramVersusArchivedRMSDifferenceNPerM=abs(full-from_archived_rms),
        representedGramVersusArchivedDifferenceNPerM=abs(represented-archived['weakVolumeResponse']),
        representedGramVersusMassInverseDifferenceNPerM=abs(represented-alternative_represented),
        projectionPythagorasDifferenceNPerM=abs(full-represented-complement),
        maximumProjectionOrthogonalityResidual=float(np.max(abs(b-body.M@coefficients))))
    assert checks['RMSAbsoluteDifferencePerM'] <= 1e-10
    for key in ['fullGramVersusArchivedRMSDifferenceNPerM', 'representedGramVersusArchivedDifferenceNPerM',
                'representedGramVersusMassInverseDifferenceNPerM', 'projectionPythagorasDifferenceNPerM']:
        assert checks[key] <= 1e-8, (key, checks[key])
    assert complement >= 0 and checks['maximumProjectionOrthogonalityResidual'] <= 1e-12
    report = dict(result='PASS_READ_ONLY_VOLUME_COMPLEMENT_DIAGNOSTIC', frozenCommit=FROZEN,
        sourceHashes=bindings, checkerSHA256=digest(Path(__file__)),
        quadraturePointsPerTet=len(body.L), bulkPa=K, referenceVolumeM3=float(body.volume),
        archivedWitnessRayleighNPerM=archived['total'],
        reconstructedDirectionalLogJRMSPerM=reconstructed_rms,
        pointwiseVolumeGramNPerM=full, P1RepresentedVolumeGramNPerM=represented,
        positiveVolumeComplementNPerM=complement,
        algebraicWitnessPlusComplementNPerM=archived['total']+complement,
        initialPointwiseLogJProjectionMismatchRMS=base['replays']['256']['pointwisePressureRMS'],
        checks=checks,
        interpretation='Negative witness belongs to the finite-P1 weak discrete model; it alone does not establish a continuum or physical-law defect.',
        limits='The positive algebraic diagnostic is not a full recomputed Hessian, stationary point, spectrum, stability proof or human muscle validation.',
        newHessianAssembled=False, newSpectrumComputed=False, physicalHistoryAdvanced=False,
        newNonlinearSolve=False, constitutiveChanges=False, pressureSpaceComparison=False)
    OUT.mkdir(exist_ok=True)
    with (OUT/'volume-complement-diagnostic.json').open('x') as f:
        json.dump(report, f, indent=2, allow_nan=False)
        f.write('\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
