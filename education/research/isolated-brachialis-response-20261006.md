# One paired brachialis response at fixed quadrature

The source branch starts from frozen protocol/preflight `f50e1cecfa420fa06d1a953b15764030ec97269f`; protocol source `b14ac8ee41ff5ceafb848ffdd02e1466918453c5`. Independent review accepted the narrow diagnosis and root explicitly authorized the smallest paired45/46 experiment after source and preflight freeze. This runner does not authorize the larger nested sequence or force fitting.

Run only FJ1486 brachialis at **2,048 points per P2 element**, activation1, original geometry/fibres/caps and fitted sigma0. Its original embedded sheet model has zero branches and zero matrix strips. Both caps coincide exactly with the original frozen reference positions, and original free-mode cap traces are exactly zero. Other heads are not solved. Main, diagnosis, protocol, published books and historical evidence remain unchanged.

The45-mode control and46-mode response use the same analytic projected Newton algorithm and unchanged material tensor from `web/anatomical-modal.mjs`, with the existing `muscleMaterial` potential/stress and reference quadrature. Both have a60-iteration ceiling,0.0001N projected criterion, Armijo fraction0.0001,0.2mm maximum nodal Newton step, minimum line fraction2^-20, and refusal on any invalid/uncertified geometry or nonpositive projected Cholesky pivot. There is no material/search regularization. These are experimental solver controls, not a constitutive modification or convergence theorem. Every full free-node gate is also reported against0.0001N; projected success never upgrades it to physical equilibrium.

First re-equilibrate45 modes under the fixed fine rule. From that same-rule control's full free nodal gradient, freeze one negative normalized omitted-gradient direction, with exact zero cap values and independently checked rank46. Start46 modes at the identical control field with its new coefficient zero. Verify the added derivative by two energy perturbation sizes and tangent differences. Report direct and relaxed added-direction curvature. When the45-mode tangent is positive, the relaxed scalar curvature is the Schur expression `H_dd - H_d0 H_00^-1 H_0d`, obtained by eliminating the original-coordinate increments from the quadratic model; it is an algebraic local diagnostic, not a global stability claim. Stop on nonpositive curvature and retain that refusal.

Source, operator tests and deterministic structural protocol preflight are frozen before the following numerical preflight. Numerical preflight only evaluates the original state and derivative probes; it does not solve. Commit its receipt before executing either nonlinear solve. Each run refuses to overwrite existing evidence. The original coordinates, all solver traces, line-search refusals, full nodal states/gradients, energies, cap reactions, queried J and exact stored P2 orientation are retained under `review/isolated-brachialis-response-20261006/`.

```sh
cd education
node --test tests/isolated_projected_response.test.mjs
node --max-old-space-size=6144 tools/run-isolated-brachialis-response.mjs --preflight
# Freeze the preflight receipt in a separate commit before proceeding.
node --max-old-space-size=6144 tools/run-isolated-brachialis-response.mjs --execute
```

The unchanged0.0001N force gate remains mandatory. Failed projected/domain/tangent controls stop execution and leave the original physical state unadvanced. A passing projected response with a failing full free-node gate is preserved as a **failed physical qualification**. All potential components use J, force gradients/reactions N, nodal coordinates m and tangent curvature N/m. Active solve potential is not passive stored energy. No force rematching, anatomical qualification, monotone/continuum convergence, mesh or parameter changes, publication or deployment is claimed. Controlled frozen-state quadrature comparisons remain a subsequent independently reviewed task; the known71×/888×/467× changes already block an integration-convergence claim.
