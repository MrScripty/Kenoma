"""Frozen tangent-space diagnostic only: full H restricted to delta(logJ)=0.

All broken-P1 moment rows remain in the map. SVD handles redundant equations
only for a displacement-kernel basis; it never repairs pressure null modes.
"""
import numpy as np
from scipy.linalg import cholesky, eigh, solve_triangular, svd

RANK_TOLERANCES = [1e-4, 1e-6, 1e-8, 1e-10, 1e-12, 1e-14, 1e-15, 1e-16]
REFERENCE_SINGULAR_TOLERANCE = 1e-10


def maps(pointwise, point_state, broken, broken_state):
    free = pointwise.m['free']; V = pointwise.volume
    # M=L L.T, so ||L^-1 D v||^2/V = RMS(delta logJ[v])^2.
    L = cholesky(broken.M, lower=True)
    moments = broken_state['D'][:, free].toarray()
    whitened = solve_triangular(L, moments, lower=True)/np.sqrt(V)
    local = np.einsum('eqia,eqna->eqni', point_state['G'], pointwise.grad).reshape(-1, 30)
    rows = np.arange(len(local))[:, None]
    cols = np.broadcast_to(pointwise.di[:, None, :], (len(pointwise.m['tets']), len(pointwise.L), 30)).reshape(-1, 30)
    direct = np.zeros((len(local), len(point_state['g'])))
    direct[rows, cols] = local
    direct = np.sqrt(pointwise.w.ravel()/V)[:, None]*direct[:, free]
    return whitened, direct, moments


def kernel_basis(matrix, relative_tolerance=REFERENCE_SINGULAR_TOLERANCE):
    _, singular, vh = svd(matrix, full_matrices=matrix.shape[0] < matrix.shape[1])
    rank = int(np.sum(singular > relative_tolerance*singular[0]))
    return vh[rank:].T, singular, rank


def restrict(H, map_matrix, direct_map):
    Z, singular, rank = kernel_basis(map_matrix)
    restricted = Z.T@H@Z
    eigen, vectors = eigh(restricted)
    v = Z@vectors[:, 0]
    direct_Z, direct_singular, direct_rank = kernel_basis(direct_map)
    sensitivity = []
    # Reuse the same SVD basis for sensitivity; no result-based cutoff selection.
    _, _, vh = svd(map_matrix, full_matrices=True)
    for tolerance in RANK_TOLERANCES:
        r = int(np.sum(singular > tolerance*singular[0])); basis = vh[r:].T
        vals = eigh(basis.T@H@basis, eigvals_only=True)
        sensitivity.append(dict(relativeSingularCutoff=tolerance, rank=r,
                                redundantRowCount=map_matrix.shape[0]-r,
                                displacementKernelDimension=basis.shape[1], lowestRestrictedEigenvalueNPerM=float(vals[0]),
                                momentKernelBasisResidualFrobeniusPerM=float(np.linalg.norm(map_matrix@basis)),
                                directPointKernelBasisResidualFrobeniusPerM=float(np.linalg.norm(direct_map@basis))))
    gram = direct_map.T@direct_map
    return dict(basis=Z, restrictedHessian=restricted, fullRestrictedEigenvaluesNPerM=eigen,
                lowestFreeDirection=v, singularValuesPerM=singular, rank=rank,
                rowCount=map_matrix.shape[0], redundantRowCount=map_matrix.shape[0]-rank,
                freeDisplacementCount=map_matrix.shape[1], displacementKernelDimension=Z.shape[1],
                referenceRelativeSingularCutoff=REFERENCE_SINGULAR_TOLERANCE, rankToleranceSensitivity=sensitivity,
                directPointMapRank=direct_rank, directPointSingularValuesPerM=direct_singular,
                momentDirectGramRelativeDifference=float(np.linalg.norm(map_matrix.T@map_matrix-gram)/np.linalg.norm(gram)),
                directMomentKernelProjectorDifferenceFrobenius=float(np.linalg.norm(Z@Z.T-direct_Z@direct_Z.T)),
                basisOrthogonalityErrorFrobenius=float(np.linalg.norm(Z.T@Z-np.eye(Z.shape[1]))),
                momentNullspaceResidualFrobeniusPerM=float(np.linalg.norm(map_matrix@Z)),
                directNullspaceResidualFrobeniusPerM=float(np.linalg.norm(direct_map@Z)),
                displacementProjectedEigenResidualNPerM=float(np.linalg.norm(Z.T@H@v-eigen[0]*(Z.T@v))),
                convention='Euclidean free-nodal normalization; RMS-normalized volume map; all moment rows retained; no pressure null or physical term repaired')


def volume_metrics(body, state, x, v, moment_map, direct_map):
    free_v = v.ravel()[body.m['free']]
    dF = np.einsum('eni,eqna->eqia', v[body.m['tets']], body.grad)
    dlog = np.einsum('eqia,eqia->eq', state['G'], dF)
    Fcorner = np.einsum('eni,eqna->eqia', x[body.m['tets']], body.cornergrad)
    dFcorner = np.einsum('eni,eqna->eqia', v[body.m['tets']], body.cornergrad)
    corner_dlog = np.einsum('eqai,eqia->eq', np.linalg.inv(Fcorner), dFcorner)
    return dict(euclideanNodalNorm=float(np.linalg.norm(v)), maximumHeldCapVariationM=float(abs(v[body.m['cap']]).max()),
                directionalLogJRMSPerM=float(np.sqrt(np.sum(body.w*dlog*dlog)/body.volume)),
                maximumAbsDirectionalLogJAtQuadraturePerM=float(abs(dlog).max()),
                maximumAbsDirectionalLogJAtCornersPerM=float(abs(corner_dlog).max()),
                momentMapWitnessResidualPerM=float(np.linalg.norm(moment_map@free_v)),
                directPointMapWitnessResidualPerM=float(np.linalg.norm(direct_map@free_v)),
                relativeMomentMapWitnessResidual=float(np.linalg.norm(moment_map@free_v)/(np.linalg.norm(moment_map,2)*np.linalg.norm(free_v))),
                scope='First-order volume preservation at current finite-K J; not an exact nonlinear incompressible path')
