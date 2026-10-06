# Local active-tangent instability in calibration and saved loading

This diagnosis keeps every constitutive coefficient and saved physical coordinate fixed. It follows the [same-budget enlarged convergence result](fixed-coefficient-current-preconditioner-result.md): projected convergence improves, but corner compression and excluded nodal forces worsen. Before changing assumptions, [one frozen protocol](fixed-coefficient-acoustic-protocol.md) probes the existing material tangent at five calibration/control states. A [separate saved-load protocol](fixed-coefficient-loaded-acoustic-protocol.md) checks selected already accepted 0.5 kg trajectory snapshots. Neither performs an optimizer, refit or trajectory rerun.

## What is tested

Let **C=dP/dF** be the exact implemented fixed-activation tangent, and let **m** and **u** be unit reference normal and spatial polarization. For the rank-one increment **delta F=u tensor m**, the potential curvature is **u dot Q(m) u**, where **Q_ik=C_iJkL m_J m_L**, in Pa. Thirteen predeclared anatomical basis and normalized combination directions are tested at all 256 positive integration points of each P2 element. A negative minimum eigenvalue witnesses local negative rank-one curvature. Passing these finite directions proves no universal strong-ellipticity result.

Every worst-point eigenpair is checked by an independent NumPy eigensolve and a separately implemented stress law, using full acoustic-matrix stress differences at steps **1e-6 and 5e-7**. All unchanged **1e-4** relative derivative gates pass. The receipt records source hashes, F, reference fiber, m, polarization, Q, determinant, stretch and stress-term split. This is curvature of a fixed-activation *solve potential*, not a theorem about active living tissue or the complete constrained dynamic system.

| Frozen state | Activation | Minimum tested acoustic eigenvalue, MPa | Reference-volume fraction with a negative witness |
| --- | ---: | ---: | ---: |
| Uniform matched-volume prism | 1 | +0.001000 | 0 |
| Accepted affine tapered control | 1 | −26.501752 | 2.9326% |
| Original stored calibration, authored fibers/sheets retained | 1 | +0.000641 | 0 |
| Preserved rejected quadratic candidate | 0.01 | −0.162780 | 12.8077% |
| Separately accepted quadratic control | 0.01 | −0.163549 | 12.7452% |

The positive original-calibration probes do not repair that pose's failed dense/full-nodal equilibrium, suppressed operating force-length factor or J=0.6158 corner minimum. Conversely, a positive restricted Hessian can coexist with negative local material curvature outside its permitted fields. Local acoustic witnesses alone do not establish a negative eigenvalue of a specific finite constrained mesh; the separate full-P2 tangent audit addresses that distinction.

## The bulk term is positive at the reported witnesses

For the implemented **Wvol=K/2 (log J)^2**, exact rank-one contraction gives

**Qvol=K(1−log J)(F^-T m) tensor (F^-T m).**

The coefficient can become negative at **J>e**. However, all integration points in these five scanned states have **J<e** (maximum 2.40129), and all selected loaded states are below 1.29293. That possible large-expansion defect is not the cause of their reported negative witnesses. Corner/unsampled values and untested trajectories are not covered by this statement.

For either existing fiber term, let **n=F f0/lambda**, **k=Wfiber'(lambda)** and **k'=Wfiber''(lambda)**. Its acoustic contribution is

**Qfiber=(f0 dot m)^2 [k' n tensor n + (k/lambda)(I−n tensor n)].**

Here **kactive=a sigma0 fL(lambda)** and **kactive'=a sigma0 fL'(lambda)**. The derivative is negative on the descending limb. At the accepted quadratic state's worst point (**lambda=1.256143, J=1.387495**), the Rayleigh split in MPa is matrix **+0.00078968**, volume **+0.00009158**, passive fiber **+0.09077784**, active **−0.25520852**, totaling **−0.16354942**. This directly identifies the active term dominating that witness without switching coefficients off or solving another state. It does not prove the cause of every compressed corner.

## The same issue occurs in saved loaded states

The completed 30-step, 256-point trajectory and its existing fresh replay select the earliest worst corner compression (**0.085 s**), earliest maximum activation (**0.13 s**) and final release (**0.43 s**). Exact geometry, authored fibers, head coefficients, activation and 63-coordinate body slices are retained. Scanned integration minima agree with the original independent replay within **1e-10**. No contact, attachment, sheet or joint law is altered; their Hessians are outside this *local body-material* diagnostic.

| Saved time, s | Brachialis minimum / negative volume | Short biceps minimum / negative volume | Long biceps minimum / negative volume |
| --- | ---: | ---: | ---: |
| 0.085 | −0.008356 MPa / 1.1216% | −0.729733 MPa / 8.6932% | +0.000979 MPa / 0 |
| 0.13 | −0.000399 MPa / 0.0513% | −0.728836 MPa / 4.9860% | +0.000979 MPa / 0 |
| 0.43 | +0.000996 MPa / 0 | +0.000994 MPa / 0 | +0.000987 MPa / 0 |

At 0.085 s the short-head witness splits into matrix **+0.00087085**, volume **+0.01429351**, passive fiber **+0.09275464**, active **−0.83765225 MPa**. Thus the active descending-limb tangent limitation is present in the loaded trajectory itself, not merely in the uniform-fiber ablation. The weak brachialis witness and finite-direction long-head passes must be kept separate; no statement about the whole tissue envelope follows from these selected local values.

## Implications for a subsequent constitutive revision

The fitted peak first-Piola coefficient stays **8.708387 MPa** for FJ1512; operating active Cauchy stress remains **a sigma0 fL lambda/J**. Preserve the distinct **140 N/cm²=1.4 MPa** elbow/shoulder model specific tension and the joint-moment-derived provenance in [Holzbaur, Murray and Delp (2005), methods/Table 1](https://nmbl.stanford.edu/publications/pdf/Holzbaur2005.pdf). These tests neither change that conversion nor justify equating it with a fitted fixture coefficient.

[Blemker, Pinsky and Delp (2005), equations 1–9](https://nmbl.stanford.edu/publications/pdf/Blemker2005.pdf) use an uncoupled nearly incompressible energy, independent along/cross-fiber shear measures, fiber stress/area conventions and a logarithmic volume penalty. Those distinctions motivate explicit tests of shear resistance, fiber-stretch/stress conventions and near-incompressible discretization. The present authored isotropic matrix/full-stretch fiber law is not their complete model. Neither increasing bulk stiffness nor replacing the active curve ad hoc is supported by the local witnesses. Anatomy remains an atlas construction rather than patient-specific mechanics, as described in [the original BodyParts3D source](https://academic.oup.com/nar/article/37/suppl_1/D782/1000752).

A revised model must declare its active stress/potential convention, address descending-limb stability or regularization with a defensible physical mechanism, retain calibrated force provenance, and demonstrate full nodal equilibrium and matched refinement before claiming tissue credibility. Compatible pressure/displacement spaces are still needed to assess a mixed nearly incompressible formulation; the earlier pressure-count audit did not establish an inf-sup condition. Changing equations would require corresponding derivations, book statements and applicable Lean propositions. This diagnostic changes none of them and authorizes no skin.

The source-bound audit/replay JSON and raw executions/tests are under `audit/fixed-coefficient-*acoustic*` and `review/fixed-coefficient-controls/`. The PNG/PDF shows calibration controls and saved loaded states separately, with signed curvature and negative-volume fractions. Failed physical cases remain failures; no time or activation is advanced.
