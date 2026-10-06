# Frozen continuous-P1, broken-P1 and pointwise volume operators

**Broken P1 recovers the original pointwise full tangent at these affine
patches, but has pressure null modes on both meshes. Descending-limb negative
curvature remains.** No candidate model, stabilization or accepted trajectory
is selected from this comparison.

Entry12485b3d1b0b630b505bf35e4acc4934270ab3e0; preexecution source commit
8e7c8f7d4cd1bc4cc1d746c442516d7cbb4ae3c0; branch
research/frozen-pressure-space-comparison. [Protocol](frozen-pressure-space-protocol.md),
[Python operators](../../tools/frozen_pressure_spaces.py),
[independent Node replay](../../tools/frozen-pressure-replay.mjs),
[runner](../../tools/run_frozen_pressure_spaces.py) and
[tests](../../tests/test_frozen_pressure_spaces.py) were committed before the
four-case execution. There were no AGENTS.md/.agents/skills files in the
selected workspace/frozen checkout. Author/committer identity remains
MrScripty <TheEnvironmentGuy@protonmail.com>.

## Fixed fields and complete derivatives

Reuse the archived coarse4x1x1 and fine8x2x2 P2 meshes. Reference block is
0.14x0.02x0.02m; mu1000Pa, K1e6Pa, kf20000Pa, b6, peak155000Pa,
activation1, optimumStretch1, activeWidth0.5. The existing scalar transverse
traction construction supplies the affine reference at stretch1.01/1.25;
both complete caps follow it exactly. No full-block nonlinear solve was
needed or run. Base operators use256 positive quadrature points; original
Node32/256-point integration provides independent replay.

For either P1 space, let

    M = integral Q Q^T dV0
    b = integral Q logJ dV0
    D = db/du
    p = K M^-1 b
    E = integral W0 dV0 + K/2 b^T M^-1 b
    g = integral (P0 + p_h G):gradN dV0, G=F^-T
    H = Hfixed(p_h) + K D^T M^-1 D

Continuous P1 uses shared vertex pressure coefficients; broken P1 uses
four independent coefficients per tetrahedron and a block-diagonal mass.
Both eliminate the same mixed functional p logJ-p^2/(2K). The fixed-pressure
tensor includes **-p_h G_rb G_sa**, all matrix/passive/active terms and
their prestress. No term is removed or shifted positive.

The pointwise operator is separately assembled from
E=integral[W0+K/2(logJ)^2]dV0 and
C=Cfixed(K logJ)+K G outer G. Its Hessian is assembled directly, never
constructed by correcting a continuous-P1 matrix. Original Node
muscleMaterial.solvePotential, P and materialTensor independently assemble
the pointwise energy, force and tangent actions. Mixed Node replay takes
the eliminated p and dp, independently checks their weak/directional moments,
and assembles the fixed-pressure tensor plus G dp. It does not borrow a
Python stress, gradient or material tensor.

At an affine field, G is constant and P2 variations have elementwise-linear
delta(logJ). The broken pressure basis therefore spans every such variation.
The full independently assembled matrices and derivative checks below verify
the expected identity; it was not inserted into either implementation.
Nonaffine frozen unit probes also verify derivatives of each operator's
own complete energy. Equivalence outside affine bases is not asserted.

## Full matrix and field agreement

All three operators have the same affine energy to reported Python precision:
0.0868423348697805J at1.01 and1.901659074157323J at1.25. Cap reactions
are62.0447362297909N and39.7611457353133N. The finite-K J values are
1.000009997014032 and1.000254088151527: passing compatibility does not
mean exact incompressibility.

| Case | Broken-minus-pointwise energy J | Maximum force difference N | Maximum pressure-sample difference Pa | Full tangent relative Frobenius difference |
| --- | ---: | ---: | ---: | ---: |
| coarse1.01 | 0 | 1.7764e-14 | 5.4276e-9 | 2.6371e-15 |
| coarse1.25 | 0 | 1.3323e-14 | 4.9665e-9 | 4.1313e-15 |
| fine1.01 | 0 | 9.7700e-15 | 1.2027e-8 | 2.9596e-15 |
| fine1.25 | 0 | 4.6629e-15 | 1.4260e-8 | 4.3229e-15 |

Maximum broken/pointwise tangent-entry difference is2.3283e-10N/m.
Continuous-P1/pointwise tangent relative differences are0.792996/0.795067
(coarse1.01/1.25) and0.892111/0.901618 (fine1.01/1.25);
their same affine energies and forces do not imply equal tangent operators.
No pressure basis, K, activation or physical fiber term was fitted to match.

## Mass positivity and all pressure modes

Minimum mass eigenvalues, in m3:

| Pressure mass | Coarse | Fine |
| --- | ---: | ---: |
| Continuous P1 | 2.8355111e-7 | 4.6927197e-8 |
| Broken P1 | 1.1666667e-7 | 1.4583333e-8 |
| Formal quadrature pressure mass | 9.1145833e-9 | 1.1393229e-9 |

All are positive. No pressure null mode or automatic gauge is removed.
The scaled pressure coupling spectrum uses the reference displacement H1
seminorm and full pressure mass, with the original1e-10 relative rank cutoff.
Raw signed numerical eigenvalues and witnesses are preserved.

| Space | Coarse rank/count; nullity | Fine rank/count; nullity |
| --- | --- | --- |
| Continuous P1 | 20/20;0 | 81/81;0 |
| Broken P1 | 86/96;10 | 632/768;136 |
| Formal pointwise quadrature space | 86/6144;6058 | 632/49152;48520 |

Continuous-P1 beta is0.579613738/0.512673010 at1.01 and
0.585273107/0.513105352 at1.25 (coarse/fine). Broken P1 **beta including
nulls is zero**, distinct from its smallest positive singular value:
0.139532599/0.090178557 at1.01 and0.118895527/0.077581117 at1.25.
Its retained null-pressure witnesses have mass norm1 and scaled coupling
squared between4.01e-30 and6.93e-30. Constant-pressure coupling squared
is1.7877–2.2801, so these nulls are not a constant-pressure gauge.

The pointwise energy has **zero actual finite pressure unknowns**. Its
formal quadrature-space diagnostic uses diagonal quadrature mass and the
weighted delta(logJ) Gram operator. Nonzero eigenvalues are computed through
the smaller displacement Gram matrix; the complete pressure-space spectrum
retains zero-mode multiplicity, plus the raw nodal Gram eigenvalues including
roundoff-sign nulls. Its positive singular values match broken P1 at these
affine fields. The many quadrature-space nulls are not an assertion that the
penalty operator has pressure unknowns or satisfies an incompressible mixed
inf-sup condition. Positive finite-K mass never establishes either conclusion.

## Physical spectra and lowest-mode decompositions

| Case | Continuous P1 lowest N/m; negative count | Broken P1 lowest N/m; negative count | Pointwise lowest N/m; negative count |
| --- | ---: | ---: | ---: |
| coarse1.01 | -32.23543649;9 | +2.171928985;0 | +2.171928985;0 |
| coarse1.25 | -9477.446662;63 | -4991.552805;46 | -4991.552805;46 |
| fine1.01 | -27.95365851;48 | +0.364033353;0 | +0.364033353;0 |
| fine1.25 | -6705.236024;359 | -4127.585678;244 | -4127.585678;244 |

Fine1.25 raw combined comparison classifications remain **UNQUALIFIED**
because of the energy accumulation check described below; the computed
curvatures and passing independent derivative evidence remain visible.
These are distinct affine diagnostic fields, not replacements for any
previous rejected perturbed result. Euclidean nodal normalization makes
eigenvalue magnitudes and counts mesh dependent; no continuum spectral
convergence or nonlinear branch qualification is claimed.

Complete Rayleigh terms for each lowest witness (N/m):

| Case/space | Matrix | Passive fiber | Active | Pressure prestress | Volume | Total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| coarse1.01 continuous | 30.48796 | 380.92026 | -443.50622 | -0.17615 | 0.03872 | -32.23544 |
| coarse1.01 broken | 1.49319 | 9.45784 | -8.79365 | -0.00687 | 0.02141 | 2.17193 |
| coarse1.25 continuous | 62.72789 | 2283.43117 | -11842.26682 | -4.04360 | 22.70470 | -9477.44666 |
| coarse1.25 broken | 60.56690 | 1413.65043 | -7086.15372 | -0.28233 | 620.66592 | -4991.55281 |
| fine1.01 continuous | 21.95424 | 298.48800 | -348.26245 | -0.13786 | 0.00441 | -27.95366 |
| fine1.01 broken | 0.27553 | 1.78852 | -1.70446 | -0.00131 | 0.00576 | 0.36403 |
| fine1.25 continuous | 58.41905 | 1615.80213 | -8381.95973 | -2.92728 | 5.42980 | -6705.23602 |
| fine1.25 broken | 59.85093 | 1214.96382 | -6035.77829 | -0.16078 | 633.53865 | -4127.58568 |

Pointwise decompositions match the broken values at the displayed precision;
their independently computed full terms and distinct witnesses are retained
for every case. Largest decomposition/eigenvalue difference is9.10e-12N/m.
Pressure prestress is present in every row. Broken lowest-witness unresolved
delta(logJ) RMS is at most3.67e-14/m.

Cross-operator evaluations retain the same witness rather than compare only
different lowest vectors. At1.01, the continuous lowest-direction weak volume
terms0.0387213/0.00440798N/m become17628.5242/13791.3006N/m under broken
or pointwise volume control; same-direction totals become+17596.2500/
+13763.3426N/m. At1.25, continuous lowest witnesses also become positive
under pointwise volume, but **different negative directions survive**, with
lowest broken/pointwise values-4991.55/-4127.59. Thus recovering the volume
tangent does not repair the current descending active response.

## Original gates, derivatives and retained energy precision failure

Every affine case/space passes the original force1e-4N, assembly2e-6N,
reaction/work1e-3N, weak/local compatibilityRMS1e-6,0.98<=J<=1.02,
exact-cap, strict-crossing and analytic-reaction1% gates at32/256 points.
Worst independent force assembly difference is1.731e-13N; maximum base
local compatibility is1.903e-15. Reaction/work discrepancies are at most
1.36e-13N. Independent local mass assembly differs by at most8.21e-22m3.

All24 original two-step gradient checks pass at1e-7/5e-8m under the unchanged
1e-4 relative target. Worst relative error is3.8404e-5 (fine1.01 pointwise).
Worst independent directional energy-gradient error is1.1768e-7N, below
the retained unit-test1e-6N target. Complete original-material tangent-action
replay at32/256 points differs by at most2.219e-11 relative. Independently
assembled directional weak-pressure RMS is at most3.431e-14/m. Nonstationary
probe local compatibility remains diagnostic; no equilibrium gate is added
to those probes. The original stationary local gate remains unchanged.

The runner additionally retains the existing unit-test energy replay
precision target **1e-12J**. Fine1.25 at256 points fails it in all three
spaces: original naive Node summation1.9016590741587245J versus Python
1.9016590741573234J, error **1.40110145708e-12J**. Those failed gates and
raw UNQUALIFIED classifications are unchanged. In the raw records,
`baseChecks.originalStationarityGatesPass` is a combined flag which also
includes this unit energy check; it must not be mistaken for a failure of
the original force/pressure/geometry gates alone.

[Accumulation audit](../../tools/frozen_energy_accumulation_audit.mjs)
re-evaluates only the same retained fine1.25 field, with no solve, altered
physics or operator repair. Its naive sum reproduces the original energy
bit-for-bit. Pairwise/compensated accumulation of the **same49152 weighted
terms** differs from Python by4.44e-16/at most6.66e-16J. This identifies
floating-point accumulation as the discrepancy. The additive
`energy-accumulation-audit.json` binds input/source hashes and retains the
original1e-12J target; it does not reclassify any prior result or silently
replace the replay source. No proposed production source fix is applied.

## Receipts, scope and stopping point

[Packet](../../data/anatomical-arm-v1/review/frozen-pressure-space-comparison/)
contains committed preexecution tests, exact meshes/affine positions,
source-bound requests, assembled energy/forces/pressure/full spectra and
matrix hashes written before optional checks, witnesses, full signed coupling
spectra/null multiplicities, independent Node32/256 replays, derivative
probes, all failures, decomposition/cross-Rayleigh comparisons, accumulation
audit, summary and manifest. The three preexecution tests passed. Main
comparison exit0,106.8143s; zero nonlinear solves and zero stabilization
parameters. Prior packet hashes are unchanged, including the original
source-amplitude and pressure-diagnosis failures (all47 prior packet files).

No production anatomy, material operator, main, book, Lean, contractile-state
response, physical history, credential configuration or downloaded imagery
changed.155000Pa remains the same composite educational amplitude; measured
fiber-source uncertainty does not alter numerical targets. This is an affine
operator comparison, not incompressible inf-sup stability, locking freedom,
nonuniform/nonlinear convergence, anatomical calibration, measured tissue
volume or a transient law. Sampled J and triangulated strict crossings retain
their previous global/curved-surface/coplanar/containment limitations.

Stop here. Parent review can compare these complete energy operators with
the separate matched-force result. The broken-P1 affine identity is verified,
but its pressure nulls and surviving descending negative directions preclude
declaring it a qualified replacement model from this packet.
