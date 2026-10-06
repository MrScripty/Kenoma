# Internal audit of the active controls packet

The saved controls support the packet's bounded negative-stability conclusions for the declared instantaneous, fixed-activation law. No mathematical defect was found in the activation isolation, pressure restriction, local counterexample, homogeneous axial slope, or parameter-free Maxwell argument. One symbolic implementation defect was found and corrected by the packet owner, with the failure preserved. This is internal verification, not external review or physiological validation.

The reproducible [independent audit script](../../tools/independent_active_controls_audit.py) produced [its source-pinned JSON receipt](../../data/anatomical-arm-v1/review/active-stability-controls/independent-audit.json) and [raw log](../../data/anatomical-arm-v1/review/active-stability-controls/independent-audit.log). It imports no mechanics solver code. It checks existing receipts and performs separate constant-J energy, 50-digit lateral-branch, and symbolic calculations. It does not rerun the eight controls or recompute their full FE spectra. All prior stationary/failed labels and witnesses remain preserved.

## Activation isolation and stationarity

The eliminated pressure is `p=K M^-1 b(x)`, independent of activation. Accordingly, changing activation from .01 to zero at the same x leaves p, D, M, and the pressure Schur term `K Dᵀ M^-1 D` unchanged. The code adds the assembled difference `P(a)-P(.01)` to the full residual, adds `C(a)-C(.01)` to the displacement Hessian, and applies the corresponding non-volume energy difference. This is the exact activation correction, rather than a surrogate or a solver-only tangent change. The lateral homogeneous state also stays unchanged: an axial reference fiber supplies no direct lateral stress.

The script verifies that all eight position arrays exactly equal their prior terminal arrays, their prior-receipt hashes match, and the packet's recorded source hashes match the files. Both independent replay densities satisfy every stored force, pressure, reaction/work, sampled-J, and crossing gate. Caps have not moved, and every saved full and projected unit witness has exactly zero cap entries.

| Check across eight cases and both replay densities | Largest observed value | Gate |
|---|---:|---:|
| Free nodal force residual | 2.719166195e-5 N | 1e-4 N |
| Python/Node force difference | 2.789608822e-14 N | 2e-6 N |
| Weak pressure RMS | 3.076080475e-16 | 1e-6 |
| Pointwise pressure RMS | 3.514066868e-8 | 1e-6 |
| Reaction/work mismatch | 1.932233562e-6 N | 1e-3 N |
| Full-gradient difference relative error | 8.738791076e-5 | 1e-4 |
| Local stress difference relative error | 2.302571194e-10 | 1e-4 |
| Axial difference relative error | 1.648157288e-8 | 1e-4 |
| Weak-nullspace relative constraint | 4.718288048e-16 | 1e-12 |

Sampled J ranges from 1.000009768289073 to 1.0002540891102103, within [.98,1.02]; every replay records zero crossing pairs. The largest full-gradient error occurs at fine/1.01/activation zero with h=5e-8 m. It passes, but is close to the predeclared tolerance and must not be described as machine precision. Force stationarity and derivative validation are separate gates; all presently pass.

## Weak pressure restriction and strict local volume admissibility

The projected space is the displacement nullspace of the P1 log-J coupling D. The free displacement/rank/null dimensions are 189/20/169 and 1125/81/1044. This enforces only the weak first-order constraint. It does not enforce pointwise incompressibility. The reported negative projected minima at stretch 1.25 remain valid finite-dimensional counterexamples to stabilization by that weak restriction; the pressure-dependent fixed-p tangent remains in H.

The local acoustic tensor uses material indices consistently: `Qij=Ciajb ma mb`, and the admissible polarization satisfies `u·F^-T m=0`. Minimizing its restriction to the two-dimensional polarization plane is correct. The finite 181-angle scan is sufficient to exhibit its negative tested direction, and insufficient to prove ellipticity when the scanned minimum is positive.

For `H=u⊗m`, the determinant lemma makes J constant along `F+εH` when the constraint holds. Both the volumetric directional curvature and the pressure-prestress rank-one contribution vanish. The strict local witness therefore does not depend on confusing `ker D` with local incompressibility.

An independent energy calculation at the reported stretch-1.25, 45-degree witness gives:

| Constant-J directional contribution | Curvature (Pa) |
|---|---:|
| Isochoric matrix | +999.830643758 |
| Passive fiber | +31210.494331688 |
| Active fiber | −79749.222517725 |
| Total | **−47538.8975422791** |

For unit u,m, this calculation uses matrix curvature `μJ^-2/3` and fiber curvature `mx²[k′ux²+(k/λ)(1−ux²)]`. It matches the saved acoustic result to about 1.1e-10 Pa without importing its tangent implementation. The saved constrained rank-one paths also keep their determinants unchanged at the four tested ±.001/±.01 steps to floating-point precision. Increasing the volumetric coefficient cannot cure this particular controlled local direction. This does not validate the atlas reference mapping or establish convergence of a nonuniform anatomical continuum solve.

## Axial loading conclusions

An independent reduction of lateral equilibrium gives

`K log(λs²)=μ(λs²)^(-2/3)(λ²−s²)/3`,

and substitution into axial traction gives

`R=A0[μ(λs²)^(-2/3)(λ−s²/λ)+k(λ)]`.

Solving and differentiating this branch at 50 decimal digits reproduces the reported slopes: active +29.2830421503143 N/m at 1.01 and −484.557191735254 N/m at 1.25; passive +69.0768890767451 and +261.876011416584 N/m. The largest difference from the saved slopes is 2.564e-11 N/m. This independently checks the pressure-eliminated tangent and implicit transverse derivative rather than reusing the assembled C entries.

The loading conclusions follow within the declared homogeneous branch. Length control excludes the global axial coordinate but retains the zero-cap interior witnesses. Dead force adds linear work, hence no curvature. An end-separation spring requires stiffness strictly above 484.557191735 N/m for the descending global scalar mode, and has zero action on the retained zero-cap witnesses. No physiological spring coefficient, distributed tendon geometry, or controller is thereby selected. Positive discrete minima at stretch 1.01 support these controlled specimens; their Euclidean nodal normalization and two mesh levels do not establish continuum spectral convergence.

## Maxwell calculation and corrected implementation defect

With `K=kr+ks`, independently constructing the two-equation operator gives

`P(s)=Mτs³+(M+cτ)s²+[c+τ(K+km)]s+K`.

For K<0, P(0)<0 and its positive leading coefficient guarantees a positive real root. For K>0 and either c>0 or km>0, the coefficients are positive and the cubic Routh–Hurwitz margin is

`Mc+Mτkm+c²τ+cτ²(K+km)>0`.

For c=km=0, `P=(1+τs)(Ms²+K)` has a neutral oscillatory pair when K>0; K=0 leaves a zero root. These are correct statements for the scalar linear thought experiment. They are not muscle rate calibration, nonlinear stability, or a multiaxial internal-state theorem.

The original symbolic execution failed because an expanded expression was compared by structural `==` with an unexpanded equivalent expression. Its determinant and general margin checks had already passed. The owner replaced that single assertion with `simplify(lhs−rhs)==0`, without changing the equations or parameters. The [first-failure receipt](../../data/anatomical-arm-v1/review/active-stability-controls/memory-stability-first-failure-receipt.json), [original failed log](../../data/anatomical-arm-v1/review/active-stability-controls/memory-stability-symbolic-first-failure.log), and [successful symbolic receipt](../../data/anatomical-arm-v1/review/active-stability-controls/memory-stability-symbolic.json) preserve that distinction. The independent audit verifies the successful receipt's source hash. The earlier absence of the claimed successful receipt was an evidence defect; it is now resolved.

## Strongest supported claim and next independent verification

The strongest claim is that the specified instantaneous fixed-activation material admits a descending-branch strict local constant-volume negative-curvature direction, and the saved stationary prescribed-cap specimens retain negative full and weak-constrained interior directions. Activation removal isolates the active contribution. The calculation does not imply that every real descending-branch muscle is unstable or that a positive fast tangent supplies long-time stability.

A useful next independent numerical check is an original-Node symmetric energy-curvature test on one saved descending full witness and one saved weak-projected witness, with independently re-eliminated pressure at each perturbation. Predeclare steps and verify the quadratic coefficient against their Rayleigh values while retaining the force gates and zero-cap directions. This would directly test the energy sign in the projected direction, which the present full-gradient checks do not separately exercise. It needs no new equilibrium simulation or fitted coefficient.

Before any anatomical replacement is qualified, define a source-supported contractile/internal and distributed series force path, its held/evolving states, and its reference architecture. Validate fast, relaxed, and coupled dynamic responses separately. This internal audit did not independently review the external physiology papers or qualify production, book, Lean, loaded trajectories, tissue envelopes, or skin.
