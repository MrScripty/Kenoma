# Reference normalization matters; incompressibility does not remove the current witness

The [recommended closure/solver experiment](recommendation.md) separates displacement restriction, reference architecture, constitutive law and pressure treatment. The [minimal prototype protocol](protocol.md) is now executed at **14 previously selected saved material points**, with six explicit variants per point. These **84 frozen diagnostics** are not new equilibria, accepted parameter choices or a full-quadrature search. All stress coefficients, passive laws, fields and activations stay fixed; only the labeled active stretch convention/reference ratio changes in an isolated research module that production code never imports.

## Exact constraint and derivative checks

For each of thirteen reference directions m, constrain spatial polarization by **u dot F^-T m=0**. This rank-one path preserves the determinant exactly. Diagonalizing the existing acoustic tensor on that polarization plane gives a sharper question than its unconstrained minimum: whether a negative local direction survives the incompressibility constraint.

All **84 cases** pass independent NumPy constrained/full eigenvalue checks and separately implemented stress differences. Maximum independent relative vector error is **6.33371e-6**, under the unchanged **1e-4** gate. Four focused tests pass: original-law reproduction; derivatives/objectivity; exact determinant-preserving pressure equivalence; and the passive cutoff's distinct one-sided behavior. The baseline full-stretch/optimal-ratio-one stress and tangent agree with the original law within **1e-10 relative**.

Two prism/proxy cases cross the unchanged passive tension cutoff at lambda≈1. Their analytic tangent is branch-dependent. The initial centered-check failure is retained with its exact source commit/hash; the final report explicitly uses same-branch one-sided differences at those points and claims **no two-sided tangent**. The other 82 cases use centered smooth probes. No tolerance, physical tangent or material branch is changed to make the test pass.

## Current-law negative curvature survives incompressible admissibility

| Saved point, current full-stretch law / lambda*=1 | Unconstrained minimum, MPa | Exactly admissible minimum, MPa |
| --- | ---: | ---: |
| Uniform full-activation prism | +0.001000 | +0.001000 |
| Full-activation affine tapered control | −26.501752 | −14.712467 |
| Original stored calibration | +0.000641 | +0.000641 |
| Rejected quadratic candidate, a=0.01 | −0.162780 | −0.162685 |
| Accepted restricted quadratic state, a=0.01 | −0.163549 | −0.163455 |
| Brachialis at 0.085 s | −0.008356 | −0.007892 |
| Short biceps at 0.085 s | −0.729733 | −0.713237 |
| Short biceps at 0.13 s | −0.728836 | −0.664432 |
| Long biceps at 0.085 s | +0.000979 | +0.000979 |

Final release points also pass these selected finite directions. The original frozen calibration's finite positive probes do not repair its failed dense equilibrium. Negative constrained directions establish a local limitation of the current fixed-activation law at these *fields*. They do not establish that every true equilibrium is unstable or that none exists. The earlier full-P2 direction is likewise at a nonstationary full nodal pose with 49.09 N residual; it remains an excluded curvature/force diagnostic, not a stationary saddle proof.

## Reference-length sensitivity changes the local result without validating a replacement

At the accepted quadratic point, current normalized stretch is **1.256143**, force-length multiplier **0.543999** and slope **−3.022746**. The source benchmark lambda*=1.4 changes that normalized stretch to **0.897245**, multiplier **0.917315** and slope **+1.574643**. Its minimum tested constrained curvature becomes **+0.000804 MPa** at the same frozen point. Short-head points at 0.085/0.13 s similarly move onto the ascending limb, producing positive tested minima **+0.001098 / +0.001077 MPa**.

This is a sensitivity result, not an optimal-length estimate or a successful equilibrium. The 1.4 value belongs to [Blemker et al.'s own reference configuration/Table 2](https://nmbl.stanford.edu/publications/pdf/Blemker2005.pdf). It is not a measured optimal/reference ratio for the BodyParts3D subject. Changing only active normalization also leaves passive normalization unchanged by design; a coherent replacement reference state must reconcile both. The original calibration's median stretch 0.5902 would fall below this benchmark's active window, while other parts can move into the window. This selected-point study does not recompute the whole calibration's operating force or establish a strength fit. No peak stress is refitted to compensate.

The per-head model/centerline proxies are:

| Head | Arm26 optimal fiber length, m | Authored centerline arc, m | Proxy lambda* |
| --- | ---: | ---: | ---: |
| Brachialis | 0.0858 | 0.13707029 | 0.62595621 |
| Short biceps | 0.1321 | 0.14385179 | 0.91830629 |
| Long biceps | 0.1157 | 0.14645512 | 0.79000308 |

These are dimensionally correct ratios of incompatible unverified structural quantities. The original reference map contains unit centerline-based element fiber directions, not measured fascicle lengths or sarcomere lengths. The proxy therefore remains labeled **unqualified**. Its short-head constrained minima stay negative: **−0.157060 MPa** at the quadratic point and **−0.636757 / −0.533395 MPa** at 0.085/0.13 s. A source number divided by a convenient atlas length is not a reference-fiber calibration.

## Isochoric active projection is not a cure

The research potential is **a sigma0 lambda* Phi(s/lambda*)**, with either **s=lambda** or **s=J^-1/3 lambda**. Its stress and physical tangent are rederived analytically and independently tested; no positive algorithmic approximation replaces them. The full-stretch variant preserves the peak first-Piola amplitude sigma0; at its peak and J=1 the active fiber Cauchy scalar is **a sigma0 lambda***. Thus changing lambda* with sigma0 fixed does not preserve a peak-Cauchy convention such as Blemker's, and this is not an implementation of their complete curve/model. At J=1 the two prototype potentials agree along exactly incompressible paths. Their active stress difference is purely spherical and can be absorbed by the pressure multiplier; constrained rank-one curvatures agree within **1e-8 relative**.

At the actual J≠1 saved points the two laws differ. The isochoric variant reduces the accepted quadratic point's negative constrained minimum to **−0.035730 MPa**, but does not remove it. At short-head 0.085/0.13 s it remains **−0.697150 / −0.613597 MPa**. In the near-reference prism its unconstrained tangent may even change sign while the constrained minimum stays +0.001 MPa; pressure/constrained-space treatment matters. These are neither optimized replacement states nor evidence that the finite-K volume envelope improves.

[Ambrosi and Pezzuto's original constitutive analysis](https://www.mate.polimi.it/biblioteca/add/qmox/21-2011.pdf) motivates checking admissible rank-one curvature and total-law ellipticity, while cautioning that a numerical strategy cannot cure a constitutive loss. Its cardiac examples do not select a skeletal reference map. [Klotz, Bleiler and Röhrle](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2021.685531/full) distinguish active-stress and active-strain force-transmission assumptions; switching families would introduce new physical assumptions requiring shear/force/rate validation. The prototype supports the staged recommendation rather than promoting any of its sensitivity variants.

## What is now justified next

Reference-fascicle/optimal-length mapping is an explicit unresolved input, and current negative material directions survive incompressibility at the tested fields. A merely deviatoric active projection, larger bulk penalty, arbitrary damping or positive solver tangent does not close those issues. The recommendation provides an explicit finite-K full P2/P1 comparator and prospective force, mixed-volume, geometry, reaction-work, spatial-refinement and stationary-curvature gates. Its saddle system requires an appropriate indefinite linear solve; a preconditioner must not replace the physical Jacobian or be used as stability evidence. No new full-space equilibrium or qualified loaded motion is claimed here.

The earlier Holzbaur **140 N/cm²=1.4 MPa** model reference and the fixed fitted peak coefficients are preserved. Production equations, published book/Lean and all previous evidence stay frozen. Prototype equations are stated here; no original Lean proposition is claimed for this separate ablation. Promoting a revised mechanical closure would require corresponding book/formal-scope revisions and new physical evidence. Raw tests, original failure, 84-case execution, independent replay and source-bound PNG/PDF are under `review/mechanical-closure/` and `audit/mechanical-closure-reference-active*`.
