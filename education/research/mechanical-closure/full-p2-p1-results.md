# Controlled finite-K full-P2/P1 result

**The mixed full-nodal operator passes controlled equilibrium and refinement checks. The unchanged active potential still has negative physical curvature at an adequately stationary descending-limb equilibrium.** This closes the declared homogeneous comparator, not the anatomical capstone or dense lift/release qualification. Entry is the frozen mechanical diagnosis **e28cb6631a8f4cba0f250786c0c7d3210200d00d**. The experiment source checkpoint is **b97491152ba9e4ac20c75af768e88838a6f7c282**, with ten exact source hashes in each raw receipt. See the [predeclared protocol](full-p2-p1-protocol.md).

## Formulation and retained assumptions

The authored 0.14×0.02×0.02 m block uses continuous ten-node P2 displacement and continuous vertex P1 pressure, with exact finite-P1 pressure elimination. Its functional is `∫(Wnonvolume+p log J−p²/(2K)) dV0`; the physical condensed Hessian includes both the fixed-pressure geometric term and `K Dᵀ M^-1 D`. No positive surrogate tangent or prestress omission is used. This is a mixed-discretization research experiment, not a replacement physiological constitutive law. The production equations, edition and Lean are frozen.

Coefficients remain `mu=1000 Pa, K=1e6 Pa, kf=20000 Pa, b=6, sigma0=8708387.370104775 Pa`, activation 0.01, optimal stretch 1, width 0.5 and force-velocity factor one. The fitted sigma0 is an experimental input, not a validated muscle stress. The earlier **1.4 dimensionless optimal/reference stretch benchmark** from [Blemker, Pinsky and Delp](https://nmbl.stanford.edu/publications/pdf/Blemker2005.pdf) is not used. [Holzbaur, Murray and Delp's](https://nmbl.stanford.edu/publications/pdf/Holzbaur2005.pdf) separate **140 N/cm²=1.4 MPa** is model specific tension; it is neither that stretch ratio nor this fitted coefficient. Missing anatomical fascicle/reference mapping remains missing.

Both complete end caps are held at the homogeneous benchmark, including transverse scaling; lateral faces are traction-free. Stretches 1, 1.01 and 1.25 are independent prescribed-cap specimens, not a time history. The smooth specimens start from the same declared 10 micrometre perturbation. The two meshes have 81/425 P2 nodes, 20/81 pressure nodes and 189/1125 free displacement coordinates. Each solve uses 256 positive points per tetrahedron and the unchanged 80-iteration/24-backtracking budget. The two perturbed solves at each mesh converge in two and three Newton steps. No increased iterations, tolerance change, material retuning or physical-history advancement occurred.

## Stationary results

| Mesh / axial stretch | Full free force (N) | Cap reaction (N) | Sampled J range | Pointwise pressure RMS | Lowest physical eigenvalue (N/m) |
|---|---:|---:|---:|---:|---:|
| coarse / 1.00 | 9.928e-14 | 34.83354948 | 1 to roundoff | 8.558e-16 | unassessed cutoff |
| fine / 1.00 | 1.237e-13 | 34.83354948 | 1 to roundoff | 1.776e-15 | unassessed cutoff |
| coarse / 1.01 | 2.719e-5 | 34.90001417 | 1.00000984–1.00001007 | 2.364e-8 | +5.43301227 |
| fine / 1.01 | 1.269e-5 | 34.90001454 | 1.00000977–1.00001017 | 3.514e-8 | +1.02498041 |
| coarse / 1.25 | 6.545e-11 | 24.48001732 | 1.00025408809–1.00025408822 | 1.308e-11 | −4293.98749643 |
| fine / 1.25 | 5.481e-10 | 24.48001732 | 1.00025408742–1.00025408911 | 7.552e-11 | −3033.96615975 |

Every case passes full force ≤1e-4 N, independent original-Node assembly ≤2e-6 N, direct cap reaction versus axial virtual work ≤1e-3 N, both weak and pointwise pressure gates, exact held nodes, positive finite geometry and sampled 0.98≤J≤1.02. Independent 32- and 256-point replay both pass, with zero strict transverse boundary crossing pairs. These checks do not certify coplanar overlap, containment or the exact curved boundary.

**Raw-label correction:** the original stretch-one records set `stationaryStabilityDiagnosticPass=true` through the equilibrium shortcut even though no spectrum was assessed at the nonsmooth passive cutoff. Preserve those source-bound records; their stability classification is **UNASSESSED_PASSIVE_CUTOFF**, as explicitly corrected by the [fresh replay](../../data/anatomical-arm-v1/review/full-p2-p1/verification.json). Only the two smooth stretches receive curvature classifications. A positive spectrum is local to this prescribed-cap specimen and fixed activation; it is not material or physiological validation.

## Matched spatial refinement and pressure coupling

At stretch 1.01, the maximum interpolated coarse/fine physical-node difference is **8.852e-10 m**, cap-force relative difference **1.066e-8**, and J-extrema difference **1.067e-7**. At 1.25 they are **1.423e-12 m**, **2.322e-14**, and **8.895e-10**. All declared homogeneous refinement gates pass. This is an implementation/patch consistency result; it supplies no nonuniform atlas or timestep convergence evidence.

Pressure coupling has complete rank **20/20** and **81/81** without deleting a supposed gauge mode. The dimensionless H1/mass-scaled inf-sup estimates are 0.5794→0.5130 at stretch 1, 0.5796→0.5127 at 1.01, and 0.5853→0.5131 at 1.25. Fine/coarse ratios 0.8854, 0.8845 and 0.8767 pass the declared 0.5 trend concern threshold. Two levels prove no stable mesh-family theorem. The reported Hessian eigenvalues use unit Euclidean nodal directions, so their mesh-dependent magnitudes are not a continuum spectrum-convergence claim. [FEBio's original formulation paper](https://febio.org/site/uploads/maas_jbme_2012.pdf) motivates mixed formulations; it does not prove this mesh family stable.

## Stationary negative witness and mechanism

The saved full-nodal negative directions have unit norm, vanish on both caps and have negligible first variation at the accepted stationary candidates. Fresh original-Node full-gradient differences at **1e-7 and 5e-8 m**, with pressure re-eliminated for each probe, agree with the physical Hessian action below the unchanged 1e-4 relative gate; the largest error across all four smooth witnesses is **4.685e-6**. Probes are derivative evidence, not newly accepted states.

| Rayleigh component at stretch 1.25 (N/m) | coarse | fine |
|---|---:|---:|
| matrix | +62.50735 | +57.65738 |
| passive fiber | +2278.39929 | +1614.32941 |
| active potential | −6637.93013 | −4704.83732 |
| fixed-pressure geometric term | −4.03911 | −2.92788 |
| weak volumetric constraint | +7.07510 | +1.81225 |
| total | **−4293.98750** | **−3033.96616** |

The active term dominates these negative stationary directions while J stays near one. The mixed bulk operator therefore does not cure the existing descending-limb instability. This distinguishes the result from the earlier highly compressed nonstationary atlas field, whose full-space negative direction was dominated by volumetric prestress. The interpretation is consistent with the active-law/ellipticity distinction reviewed from [Ambrosi and Pezzuto's original work](https://www.mate.polimi.it/biblioteca/add/qmox/21-2011.pdf); the present calculation concerns this repository's fixed-activation potential, not their numerical parameters or a validated human muscle.

## Evidence and remaining gate

[Raw operator tests](../../data/anatomical-arm-v1/review/full-p2-p1/operator-tests.log): four passed. [Solve log](../../data/anatomical-arm-v1/review/full-p2-p1/solve.log), [six-case summary](../../data/anatomical-arm-v1/review/full-p2-p1/summary.json), [fresh original-law replay](../../data/anatomical-arm-v1/review/full-p2-p1/fresh-replay.log), [corrected source-bound figure](../../data/anatomical-arm-v1/review/full-p2-p1/controlled-mixed-comparator-v2.png) and [PDF](../../data/anatomical-arm-v1/review/full-p2-p1/controlled-mixed-comparator-v2.pdf) retain the evidence. The first render and receipt remain preserved: its negative-value annotations overlapped tick labels, so v2 changes layout only. The prior preservation check confirms **281 manifest bindings, 27 terminal audit receipts and 488 source hashes**, requested audit ancestry, and untouched protected/production/book/Lean scope.

The finite-K controlled comparator is complete. **Credible nonuniform arm mechanics and a self-consistent denser loaded lift/release remain blocked by unresolved reference fascicle/architecture inputs and active-law stationary stability.** Selecting a new normalization, active stress/strain family or physical coefficient requires explicit source-backed assumptions and controlled validation; silently selecting one would invalidate this fixed-coefficient comparison. No atlas state or skin is qualified by these patch tests. Keep the failed/negative evidence and close those material/reference gates before exporting a new anatomical trajectory or promoting fitted force targets.
