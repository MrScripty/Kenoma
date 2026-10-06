# Bulk prestress and excluded full-P2 curvature

The accepted enlarged fixed-coefficient control at activation **0.01** passes its unchanged reduced residual gate but has **49.09170 N** maximum free nodal force and minimum corner **J=0.18858**. The [frozen material audit](fixed-coefficient-material-tangent-results.md) additionally witnesses negative local rank-one curvature dominated by the active descending limb. This separate [predeclared full-P2 diagnostic](fixed-coefficient-full-nodal-curvature-protocol.md) asks whether negative curvature exists in the finite held-cap mesh, and which terms dominate that direction. No optimizer, parameter fit, accepted coordinate, activation or time is changed.

## The restriction hides both force and curvature

The same 585-node P2 mesh has **1755 nodal components**. Holding its original 90 complete cap nodes fixes 270 components, leaving **1485 free**. Each element's complete 30×30 body tangent is assembled with the unchanged **256-point** rule and original material tensor. Source-bound binary64 element matrices permit independent Python sparse assembly and a NumPy/SciPy eigensolve.

The embedded 90-free-coordinate modal Hessian agrees with the original implementation to maximum **2.61934e-8 N/m**, relative **1.37836e-13**. Its minimum eigenvalue is **+48.04522 N/m**. The full held-cap operator's six smallest eigenvalues are:

**−1027.02119, −861.45585, −692.26293, −616.02718, −523.58702, −441.13314 N/m.**

The minimum eigenpair relative residual is **4.57051e-13**. Its Euclidean-norm-one nodal direction has exactly zero cap motion. Fresh full nodal stress differences at **1e-7 / 5e-8 m** give relative Hessian-vector errors **6.17573e-7 / 1.64428e-6**, under the unchanged **1e-4** derivative gate. Their directional curvatures are **−1027.021182 / −1027.021186 N/m**. The independently reassembled full nodal force differs from the saved diagnostic by at most **1.27898e-13 N**. Finite transverse self-surface checking gives zero crossings among 880 triangles; coplanar overlap, containment and curved P2 surface geometry remain unqualified.

This is a nonstationary full nodal pose with negative finite-mesh curvature, not an accepted full nodal equilibrium or a completed relaxation. Its first derivative along the saved direction is **0.82897688 N**, so calling it a stationary saddle would also be incorrect. The positive restricted Hessian certifies none of these excluded properties.

## A different negative mechanism from the local rank-one witness

The full eigen-direction Rayleigh split is:

| Existing term | Curvature, N/m |
| --- | ---: |
| Isotropic matrix | +261.284279 |
| Volume penalty | −1390.369613 |
| Passive fiber | +106.802973 |
| Active fiber | −4.738826 |
| Total | **−1027.021187** |

The *global finite nodal direction* is dominated by the volume term. The earlier *local rank-one direction* was dominated by the active term. These are different perturbations and must not be given the same causal explanation.

For **Wvol=K/2(log J)^2**, write **D=gradient(delta x)** and **G=F^-T**. Direct differentiation gives

**D²Wvol[D,D] = K(G:D)² − K log(J) tr[(F^-1 D)²].**

The first term is nonnegative; the second is a prestress geometric term. For a rank-one D=u tensor m, the trace becomes (G:D)², recovering **K(1−log J)(G:D)²**, positive when J<e. A general full-P2 nodal perturbation need not be rank one at every point. Its integrated volume curvature can therefore be negative even though all sampled J remain below e and the local rank-one volume contribution is positive.

At this fixed field/direction, exact independent integration splits the volume curvature into **+725.038323 N/m** first-variation-squared and **−2115.407936 N/m** prestress-geometric contributions. Partitioning the same points by J gives:

| Sampled region | First-variation-squared | Prestress geometric | Net volume curvature, N/m |
| --- | ---: | ---: | ---: |
| J<1 | +229.849291 | −1871.007016 | −1641.157725 |
| J≥1 | +495.189032 | −244.400920 | +250.788112 |

Their sum agrees with the independently verified volume Rayleigh term within **1e-6 N/m**. Compressed integration points dominate the negative volume contribution in this direction. This diagnoses bulk prestress at the existing nonstationary field; it does not prove the cause of every loaded compression or predict what a different bulk coefficient would do after re-solving. No bulk stiffness is retuned.

## What blocks physical qualification

The fixed-coefficient controls are now sufficient to reject a credible-envelope claim for this enlarged state: reduced equilibrium suppresses substantial full forces; a larger displacement restriction changes nodes by 13.703 mm and admits severe local compression; local active-tangent witnesses occur in both calibration controls and saved loading; and the full held-cap body tangent has negative curvature dominated by compressed bulk prestress.

The next model change needs an explicit physical closure for shear resistance, active force-length/stress convention, instability regularization and near-incompressible discretization. The current diagnostic supplies no measured viscosity or length scale with which to choose a stabilizing mechanism. More iterations, relaxed tolerances or a fitted coefficient adjustment would not qualify that choice. A full nodal or compatible mixed solver would need new accepted equilibria, geometry checks and matched spatial/quadrature/time refinement; none is claimed here.

[Blemker, Pinsky and Delp (2005), equations 1–9](https://nmbl.stanford.edu/publications/pdf/Blemker2005.pdf) motivate explicit along/cross-fiber shear and nearly incompressible volume treatment; their logarithmic penalty is shared, but their complete constitutive model is not the present authored fixture. Preserve [Holzbaur, Murray and Delp (2005)](https://nmbl.stanford.edu/publications/pdf/Holzbaur2005.pdf)'s **140 N/cm²=1.4 MPa** elbow/shoulder model reference and joint-moment calibration provenance, distinct from this fitted first-Piola coefficient and its operating Cauchy stress. [BodyParts3D](https://academic.oup.com/nar/article/37/suppl_1/D782/1000752) remains an atlas anatomy source, not measured mechanical calibration.

All coordinates, negative cases, binaries, raw focused tests, spectra, fresh derivative replay and bulk split are preserved under `audit/fixed-coefficient-full-p2-*` and `review/fixed-coefficient-controls/full-p2-*`. The accompanying figure compares restricted/full curvature, the frozen nodal direction and the exact bulk split. Constitutive assumptions, production code, published teaching/book edition, Lean statements and skin are unchanged. The capstone remains physically unqualified; this milestone makes the remaining mechanism and discretization work concrete and reviewable.
