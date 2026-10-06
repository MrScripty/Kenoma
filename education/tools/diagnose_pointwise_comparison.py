"""Hypothetical operator comparison at exact patch; never an accepted solve."""
import numpy as np
from scipy.linalg import cho_solve, eigh
from pathlib import Path
from diagnose_pressure_residual import OUT, OLD, FINE, mesh, save
from source_amplitude_p2_p1 import ExplicitBody, ANCHOR, digest

results = []
for level, directory in [('coarse', OLD), ('fine', FINE)]:
    m = mesh(directory/(level+'-mesh.json')); B = ExplicitBody(m, ANCHOR, 1.)
    _, x, _ = B.initial(1.01); r = B.evaluate(x, True)
    F = np.einsum('eni,eqna->eqia', x[m['tets']], B.grad)
    G = np.swapaxes(np.linalg.inv(F), -1, -2)
    directional = np.einsum('eqia,eqna->eqni', G, B.grad).reshape(len(m['tets']), len(B.L), 30)
    local = np.einsum('eqa,eqb,eq->eab', directional, directional, B.w)
    free = m['free']; R = B.assemble(local, B.di, B.di, x.size, x.size)[free][:, free].toarray()
    D = r['D'][:, free].toarray()
    complement = ANCHOR['bulk']*(R-D.T@cho_solve(B.Mfactor, D))
    full = r['H']+complement
    eig = eigh(full, eigvals_only=True)
    missing = eigh(complement, eigvals_only=True)
    output = dict(level=level, lowestHypotheticalPointwiseEigenvalueNPerM=float(eig[0]),
                  negativeEigenvalueCount=int((eig < -1e-8).sum()),
                  minimumProjectionComplementEigenvalueNPerM=float(missing[0]),
                  label='HYPOTHETICAL_ORIGINAL_POINTWISE_PENALTY_TANGENT_AT_EXACT_PATCH_ONLY',
                  scope='No source change, solve, acceptance, physiological preference or mesh convergence claim.')
    results.append(output); print(output, flush=True)
save('pointwise-comparison.json', dict(runnerSHA256=digest(Path(__file__)), results=results))
