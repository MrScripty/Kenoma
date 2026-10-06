"""Frozen local tangent / P1 projection audit; no optimizer or changed model."""
import json
import numpy as np
from scipy.linalg import cho_solve, eigh
from diagnose_pressure_residual import OUT, OLD, FINE, ROOT, read, mesh, save, metrics
from source_amplitude_p2_p1 import ExplicitBody, ANCHOR, parameters, ORIGINAL_CONSTITUTIVE, node, digest
from run_full_p2_p1 import coupling


def audit(level):
    m = mesh((OLD if level == 'coarse' else FINE)/(level+'-mesh.json'))
    B = ExplicitBody(m, ANCHOR, 1.)
    _, x, analytic = B.initial(1.01)
    r = B.evaluate(x, True)
    eig, vectors = eigh(r['H'])
    v = np.zeros(x.size); v[m['free']] = vectors[:, 0]; v = v.reshape(x.shape)
    F = np.einsum('eni,eqna->eqia', x[m['tets']], B.grad)
    dF = np.einsum('eni,eqna->eqia', v[m['tets']], B.grad)
    dlog = np.einsum('eqai,eqia->eq', np.linalg.inv(F), dF)
    db = r['D']@v.ravel()
    represented = cho_solve(B.Mfactor, db)
    dpq = represented[B.pi]@B.L.T
    pointwise = float(ANCHOR['bulk']*np.sum(B.w*dlog*dlog))
    mixed = float(ANCHOR['bulk']*db@represented)
    sides = []
    for h in [1e-7, 5e-8]:
        gradients = []
        for sign in [1, -1]:
            probe = x+sign*h*v; z = B.evaluate(probe)
            q = node(B, probe, z['p'])
            gradients.append(np.array(q['gradientN'])[m['free']])
        fd = (gradients[0]-gradients[1])/(2*h)
        Hv = r['H']@vectors[:, 0]
        sides.append(dict(stepM=h, independentNodeGradientRelativeError=float(np.linalg.norm(fd-Hv)/np.linalg.norm(Hv))))
    with parameters(ANCHOR):
        P, C, *_ = ORIGINAL_CONSTITUTIVE(F[:1, :1], np.full((1, 1), analytic['pressurePa']), activation=1., tangent=True)
    lam = 1.01; u = (lam-1)/ANCHOR['activeWidth']
    active_prime = ANCHOR['sigma0']*(-4*u*(1-u*u)/ANCHOR['activeWidth'])
    passive_prime = ANCHOR['kf']*np.exp(ANCHOR['b']*(lam-1))
    # At the affine patch logJ is exactly represented, so the difference of
    # pointwise-penalty and finite-P1 Hessians is exactly this PSD complement.
    complement = pointwise-mixed
    return dict(level=level, label='EXACT_HOMOGENEOUS_PATCH_OPERATOR_ONLY; NO_RECLASSIFICATION_OF_FAILED_SOLVE',
                homogeneousMetrics=metrics(B, x), lowestMixedEigenvalueNPerM=float(eig[0]),
                negativeEigenvalueCount=int((eig<0).sum()), pressureCoupling=coupling(B, r),
                lowestDirection=v, independentNodeGradientChecks=sides,
                weakVolumeRayleighNPerM=mixed, hypotheticalPointwiseVolumeRayleighNPerM=pointwise,
                missingProjectionComplementRayleighNPerM=complement,
                sameDirectionHypotheticalPointwiseTotalRayleighNPerM=float(eig[0]+complement),
                unresolvedDirectionalLogJRMSPerM=float(np.sqrt(np.sum(B.w*(dlog-dpq)**2)/B.volume)),
                activeFiberStressDerivativePa=float(active_prime), passiveFiberStressDerivativePa=float(passive_prime),
                totalFiberStressDerivativePa=float(active_prime+passive_prime),
                warning='The hypothetical pointwise operator is a mathematical comparison, not a proposed constitutive/source change or proof its full spectrum is positive.')


if __name__ == '__main__':
    results = [audit(level) for level in ['coarse', 'fine']]
    save('operator.json', dict(runnerSHA256=digest(__import__('pathlib').Path(__file__)), results=results))
    for r in results:
        print(json.dumps({k:v for k,v in r.items() if k not in ['lowestDirection', 'pressureCoupling', 'homogeneousMetrics']}), flush=True)
