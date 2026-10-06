# Convergence exposes an unresolved anatomical shape

The [predeclared current-Hessian control](fixed-coefficient-preconditioner-protocol.md) passes the same single activation **0→0.01** increment in **30 nonlinear iterations**, starting again from undeformed accepted reference. The original **80-iteration rejected enlarged solve** remains unchanged. Both runs use the same 126 total / 90 free coordinates, original P2 mesh, tapered head, axial fibers, ideal caps, 256-point quadrature, material parameters, Newton regularization and Armijo rules, **80/80 nonlinear/linear budgets**, and **1e-4 N** reduced force gate. Only the preconditioner changes. This is an isolated calibration-fixture control; the coupled arm already uses current-configuration preconditioning.

Fresh optimizer-free replay reports `PASS_ENLARGED_CONTROL_REPLAY`: independent residual **5.79703632961337e-5 N**, assembly discrepancy **7.864219299098633e-12 N**, unchanged geometry/cap gates passed, and accepted activation **0.01**. Across objective evaluations the preconditioner records 30 current-Hessian applications, 221 reference-fallback applications and 13 rejected SPD factorizations. Existing PCG curvature detection and Newton shifts remain active; there is no selected new shift or relaxed acceptance tolerance.

## Matched accepted displacement restrictions

| Quantity at activation 0.01 | Original affine restriction | Transverse quadratic restriction |
| --- | ---: | ---: |
| Independent reduced residual, N | 5.26628068968e-5 | 5.79703632961e-5 |
| Maximum free nodal force component, N | 10.58777875 | 49.09170071 |
| Minimum corner J | 0.83863647 | 0.18858269 |
| Total volume / reference volume | 1.00862937 | 1.00851328 |
| Mean force-length multiplier | 0.61607956 | 0.60333121 |
| Direct distal body cap force, N | 18.82048778 | 22.49019292 |
| Whole-body axial virtual force, N | 26.11760125 | 25.92378661 |

The maximum physical nodal difference is **13.70325024 mm**, despite almost identical total volume. These are now matched accepted *restricted* states, but they fail to establish spatial convergence: the enlarged restriction admits much stronger local compression and larger excluded full-nodal forces. The minimum integration-point J is **0.33400136**, maximum **2.40128769**; the corner minimum is lower still. A positive determinant merely passes the inversion guard. It does not establish a credible tissue envelope.

Current-Hessian preconditioning resolves a numerical obstacle without resolving the physical one. Enlarging the admissible field changes the state substantially; stopping at either small projected residual would hide the unresolved force and shape behavior. The old rejected result is independently preserved, and its failed candidate is never used as accepted history. No higher activation sweep or loaded trajectory rerun is justified by this isolated success.

## Stress convention and next diagnosis

The fixed coefficient remains **sigma0=8.708387370104775 MPa**, the peak active **first-Piola** scalar in this authored potential. Its operating fiber Cauchy scalar is **a sigma0 fL(lambda) lambda/J**; this state's reference-volume-weighted mean is **0.04496110 MPa** at activation 0.01. Neither quantity replaces the inherited **140 N/cm² = 1.4 MPa** model specific tension for elbow/shoulder muscles in [Holzbaur, Murray and Delp (2005), methods and Table 1](https://nmbl.stanford.edu/publications/pdf/Holzbaur2005.pdf). Those model strengths were selected to match measured joint moments; individual head forces were not direct measurements.

[Blemker, Pinsky and Delp (2005)](https://nmbl.stanford.edu/publications/pdf/Blemker2005.pdf) motivate examining geometry, fascicle architecture and nearly incompressible mechanics. They do not validate this fixture's fitted coefficient or displacement restriction. [BodyParts3D's original account](https://academic.oup.com/nar/article/37/suppl_1/D782/1000752) describes an anatomical concept dictionary, not measured patient fibers or muscle calibration data.

Before changing assumptions, a separate frozen-state material-tangent audit can check rank-one perturbations using the existing stress and tangent. A witnessed negative acoustic eigenvalue would identify a local constitutive limitation independent of optimizer budgets; a finite directional check cannot prove strong ellipticity. Full nodal equilibrium, compatible near-incompressible treatment, quadrature/time refinement and loaded-envelope credibility remain unqualified. No material default, published book edition, Lean statement or skin changes.

Raw terminal execution and fresh replay are in `data/anatomical-arm-v1/review/fixed-coefficient-controls/current-preconditioner-*`; their audit JSON receipts retain coordinates, force traces, failed factorization records and source hashes. The accompanying PNG/PDF shows numerical convergence separately from the unresolved shape/force comparison.
