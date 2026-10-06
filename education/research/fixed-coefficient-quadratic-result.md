# Excluded forces and a preserved enlarged-space failure

The [four fixed-coefficient controls](fixed-coefficient-calibration-results.md) justify checking the displacement restriction before changing a material coefficient. This separate experiment appends transverse quadratic nodal ring shapes to the same P2 field. It keeps the same axial fibers, head geometry, 256-point quadrature, ideal fixed caps, material constants and force/geometry gates. The [predeclared single increment](fixed-coefficient-quadratic-protocol.md) is activation **0→0.01**, from undeformed accepted reference, with the same **80 nonlinear/80 linear iterations**.

The old field is an exact subset of the new 126-coordinate / 90-free-coordinate restriction. Three focused tests check that embedding by physical positions, energy and force projection; the analytic prism; and derivatives of the new modes. No original control is overwritten or relabeled.

## The same physical state loses stationarity in added directions

Without moving any node, the previously accepted affine state at activation 0.01 changes from **5.26628069e-5 N** projected residual in its original free space to **30.91672708 N** in the enlarged space. Its full free-nodal force remains **10.58777875 N**. That is direct evidence that the original reduced force balance suppresses relevant excluded displacement directions. It is not a new physical solution or an activation advance.

The separate enlarged solve **rejects after 80 iterations**, with independently replayed residual **0.0256157202251 N**. Accepted activation remains **zero**. The failed candidate has minimum corner **J=0.19968417**, full free-nodal force **48.20301 N**, and total volume ratio **1.00858025**. Its nodes differ by up to **13.87657 mm** from the accepted affine state at 0.01. This is an accepted-versus-rejected diagnostic comparison, not matched accepted refinement evidence; neither a smaller virtual-work discrepancy nor similar total volume qualifies it.

Fresh replay returns `PASS_PRESERVED_ENLARGED_REJECTION` and checks exact source identity, all 126 projected components, iteration/activation lineage, force/geometry gates and rollback. The candidate's independent body assembly agrees within **7.56891e-12 N**. Complete existing transverse edge/face self-crossing checks give zero crossings for all 16 original control candidates and this enlarged candidate. That finite 880-triangle check does not cover coplanar overlap, containment or exact curved P2 surfaces, and passing it does not make the compressed or force-failing states credible tissue.

## Numerical conditioning is a separate obstacle

The failed candidate's frozen 90-coordinate Hessian is positive definite: eigenvalues range from **46.01551 to 459754.43882 N/m**. The original reference-preconditioned operator has an estimated spectral condition number **6.21238e7**. The recorded solve has **74 truncated linear solves**, only six converged linear solves and 6118 recorded PCG iterations across its original 80 nonlinear steps. This is distinct from changing the constitutive law or hiding a geometric failure with a larger budget.

A read-only paired linear control uses the exact same frozen Hessian and right-hand side, unchanged **80-iteration cap / 1e-3 relative linear tolerance**, and never advances a nonlinear or physical state:

| Preconditioner | PCG iterations | Relative actual residual | Outcome |
| --- | ---: | ---: | --- |
| Original undeformed reference operator | 80 | 1.33231975 | Preserved linear-iteration limit |
| Current frozen Hessian Cholesky | 1 | 1.17207328e-13 | Linear solve passes |

The current-Hessian direction also passes fresh gradient/Hessian-vector finite differences at **1e-8 / 5e-9 m**, with relative vector errors **2.93238e-7 / 4.51501e-7** under the unchanged **1e-4** derivative gate. This confirms a numerical preconditioning improvement at this frozen state, not a successful nonlinear solve or a stable full-nodal muscle.

A next separately labeled research control can test current-Hessian Cholesky preconditioning with reference fallback when the shifted Hessian is not positive definite, retaining the existing Newton regularization/Armijo logic and the same 80/80 budgets. It must start again from accepted undeformed reference, preserve the original rejected execution and retain the full nodal/compression diagnostics. It must not reuse the rejected candidate as accepted history, retune coefficients or declare the shape credible merely because projected convergence improves.

The source-backed distinction between the inherited **Holzbaur 1.4 MPa** model specific tension, the fitted **8.708387 MPa** first-Piola parameter, and operating Cauchy stress remains as explained in the [research-book-ready result](fixed-coefficient-calibration-results.md). No published equation, book edition, Lean statement, model default or skin changes. Original source citations and proposed physical/model revisions remain in that explanation; this supplement adds numerical evidence before any such revision.

Raw failed execution, fresh replay, both binary operators, spectral analysis, linear/derivative probes and finite surface audits are under `audit/fixed-coefficient-*` and `review/fixed-coefficient-controls/`. The original 80-iteration failure remains a terminal negative result.
