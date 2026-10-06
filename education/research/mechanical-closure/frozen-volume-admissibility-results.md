# Frozen coarse pointwise-volume admissibility

The stretch1.25 negative direction survives pointwise linearized volume
preservation. Restricting the complete physical Hessian gives a lowest
Rayleigh value **-4443.161108281245N/m**, with directional logJ RMS
**2.69046096022e-14/m**. The stretch1.01 control has a positive complete
restricted spectrum, lowest **+2.193602593185752N/m**. This is a frozen
coarse diagnostic, with no model selection or state advancement.

Entry09fa01117a53a4800c91404a2ebd5f4aa610327e, tree
b4846f150f06c39fae17867131158e6508ab1d8c; separate branch
research/frozen-volume-admissibility. Preexecution source/test/protocol
commit dffc998be0dd96d583cfa58bfd9e42d9baa44a45, tree
d35b19c090844ae24ed359fc7bb0f4c3890447e0. The [protocol](frozen-volume-admissibility-protocol.md),
[map/kernel code](../../tools/frozen_volume_kernel.py),
[independent original-material observer](../../tools/volume-admissibility-replay.mjs),
[runner](../../tools/run_frozen_volume_admissibility.py) and
[three verification tests](../../tests/test_frozen_volume_kernel.py) were
committed before the one bounded execution. No AGENTS.md or .agents/skills
were present in the selected workspace/checkouts. Repository-local author
and committer identity was verified as MrScripty <TheEnvironmentGuy@protonmail.com>.

Reuse the exact archived coarse4x1x1 mesh, affine coordinates, material and
held complete caps from the qualified pointwise1.25 and1.01 receipts. The
reference volume is5.6e-5m3; mu1000Pa, K1e6Pa, kf20000Pa, b6,
sigma0=155000Pa, activation1, optimumStretch1, activeWidth0.5. The frozen
base quadrature remains256 positive points per tetrahedron. There are zero
nonlinear solves, zero stabilizers, zero coefficient changes and no changed
cap/traction construction. Fine1.25 is excluded and remains UNQUALIFIED.

For held-cap displacement variations, the full linearized map is

    A v = delta(logJ)[v] = F^-T : grad(v).
    D v = integral Q_broken delta(logJ)[v] dV0.
    M = integral Q_broken Q_broken^T dV0 = L L^T.
    T = L^-1 D_free / sqrt(V0).
    Qdirect = sqrt(wq/V0) A_free at every quadrature point.
    Z = orthonormal basis of ker(T); Hrestricted = Z^T Hphysical Z.

At the affine base, delta(logJ) is elementwise linear, so all96 broken-P1
moment rows represent the pointwise map exactly. T has96 rows and189 free
displacement columns; Qdirect has6144 rows and189 columns. The all-row SVD
uses the prospective relative cutoff1e-10, without deleting or fixing a
pressure mode. Both maps have rank86; ten moment equations are redundant,
and the displacement kernel has dimension103. This describes the right
displacement kernel. The broken pressure left-null modes remain unchanged;
it is no inf-sup qualification or pressure-space repair. The pointwise
finite-K energy itself has no independent pressure unknowns.

| Map/kernel verification | Coarse1.25 | Coarse1.01 |
| --- | ---: | ---: |
| Relative Frobenius difference T^T T vs Qdirect^T Qdirect | 4.17360e-15 | 2.48896e-15 |
| Direct/moment right-kernel projector Frobenius difference | 2.88615e-14 | 2.81786e-14 |
| Z orthogonality Frobenius error | 8.04482e-15 | 8.66853e-15 |
| All moment basis residual, Frobenius /m | 8.34838e-14 | 8.36470e-14 |
| All direct basis residual, Frobenius /m | 1.86107e-13 | 1.98218e-13 |
| Restricted eigen-equation residual N/m | 8.95629e-12 | 2.23692e-12 |
| Largest singular value /m | 51.6471064 | 46.4417963 |
| Smallest retained singular value /m | 3.98410120 | 4.51869190 |
| Largest redundant singular value /m | 2.29359e-14 | 2.06931e-14 |

All recorded cutoffs1e-4,1e-6,1e-8,1e-10,1e-12,1e-14 and1e-15 give
the same rank86, kernel103 and lowest restricted values. At1e-16,
roundoff-scale redundant singular values are counted: ranks94/93,
kernels95/96 and minima-4216.29594576/+5.58760570841N/m. Those artificial
extra constraints are retained as numerical sensitivity evidence; they are
not alternative physical models or accepted cutoff selections. Full singular
spectra, every cutoff result, bases and restricted spectra are in the packet.

Each reported direction has Euclidean nodal norm1 and exactly zero variation
on the held caps. This normalization makes values mesh dependent; they are
directional derivatives per metre, not a pressure residual or a finite
volume change caused by applying a unit displacement.

| Frozen witness | Full physical Rayleigh N/m | Negative restricted eigenvalues | Directional logJ RMS /m | Maximum quadrature /m | Maximum corner /m |
| --- | ---: | ---: | ---: | ---: | ---: |
| Coarse1.25 restricted lowest | -4443.16110828 | 43 of103 | 2.69046e-14 | 2.22045e-13 | 1.88294e-13 |
| Coarse1.25 archived finite-K unconstrained | -4991.55280541 | not a restricted spectrum | 3.32916206934 | 12.5549945 | 13.7905628 |
| Coarse1.01 restricted lowest | +2.19360259319 | 0 of103 | 1.06647e-14 | 7.34968e-14 | 8.94840e-14 |
| Coarse1.01 archived finite-K unconstrained | +2.17192898534 | not a restricted spectrum | 0.0195545410243 | 0.0443947817 | 0.0475843818 |

The archived finite-K witnesses are preserved verbatim and explicitly
**not pointwise volume-admissible**: their nonzero directional volume RMS
is independently reproduced. The earlier decomposition field
`unresolvedDirectionalLogJRMSPerM=0` measures a projection complement;
for a pointwise operator it vanishes identically. It is not delta(logJ)
itself and is not used to claim volume admissibility here.

The new restricted witnesses have moment residuals7.71957e-15/6.23267e-15
/m and direct residuals2.69228e-14/1.06737e-14/m. Relative moment witness
residuals, normalized by ||T||2 ||v||2, are1.49468e-16/1.34204e-16.
Original-material Node observations independently give RMS2.56335e-14/
2.66860e-14 at32/256 points for1.25, and1.05695e-14/1.06999e-14 for1.01.
These near-roundoff values are reported with units; no new pressure gate
replaces the original1e-6 target.

The complete physical Hessian includes the positive volume term
K integral(delta logJ)^2 and the pressure prestress
-K logJ integral trace[(F^-1 deltaF)^2], plus matrix, passive and active
terms. Only the positive volume term vanishes in the kernel; prestress is
retained. Independent original materialTensor tangent actions agree with
Python at7.78865e-15/4.49658e-13 relative for the restricted witnesses,
and projected actions at4.18162e-15/4.38632e-12.

| Complete Rayleigh terms N/m | Matrix | Passive fiber | Active | Pressure prestress | Positive volume | Total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Coarse1.25 restricted | 52.425677643 | 1135.96708398 | -5631.45876116 | -0.095108746 | 4.05360e-26 | -4443.16110828 |
| Coarse1.25 archived finite-K | 60.566896546 | 1413.65042749 | -7086.15372121 | -0.282332932 | 620.665924699 | -4991.55280541 |
| Coarse1.01 restricted | 1.504545008 | 9.472284835 | -8.776316629 | -0.006910621 | 6.36925e-27 | +2.19360259318 |
| Coarse1.01 archived finite-K | 1.493189584 | 9.457840953 | -8.793647220 | -0.006867616 | 0.021413284 | +2.17192898534 |

The Node32/256 observer recomputes every term from original materialTensor
and independently evaluates passive/active/prestress/volume terms. Matrix
is the residual physical matrix constituent after these direct terms; no
shift or pressure contribution is discarded. It agrees with the above
decomposition at the displayed precision. The model's instantaneous active
term dominates the1.25 negative witness even within the volume kernel.
This observation supplies evidence for independent review, without editing
the other research worker's contractile-state response work.

| Unchanged base constituent energies J (independent Node256) | Coarse1.25 | Coarse1.01 |
| --- | ---: | ---: |
| Matrix | 0.00454638472615 | 8.33895691299e-6 |
| Volume | 1.80724287617e-6 | 2.79830013275e-9 |
| Passive fiber | 0.06165254885496 | 5.71370036334e-5 |
| Active potential | 1.83545833333310 | 0.08677685611094 |

Base free force residuals are1.49406e-11/5.18015e-13N. Python total
energies are1.9016590741573225/0.08684233486978053J. Current finite-K
J is1.000254088151527/1.000009997014032: volume preservation is about
this current base, not resetting it toJ=1. Pointwise p=K logJ compatibility
is an identity of this energy and does not imply exact incompressibility.

All four new witness records pass unchanged base force1e-4N, assembly2e-6N,
reaction/work1e-3N, local compatibility1e-6,0.98<=J<=1.02, zero strict
crossings and unit energy replay1e-12J checks. Both prescribed1e-7/5e-8m
central gradient differences pass full-action relative1e-4 and energy-gradient
1e-6N targets. The two restricted witnesses also pass the1e-4 projected
gradient-action target:

| Restricted derivative replay | Full relative error h=1e-7 /5e-8m | Projected relative error h=1e-7 /5e-8m | Independently differenced Rayleigh N/m h=1e-7 /5e-8m |
| --- | ---: | ---: | ---: |
| Coarse1.25 | 6.98236e-10 /1.86295e-9 | 1.35770e-10 /3.74291e-10 | -4443.16110795 /-4443.16110823 |
| Coarse1.01 | 1.82404e-7 /2.48769e-7 | 1.66654e-7 /3.25730e-7 | +2.19360273249 /+2.19360252241 |

Worst full-action relative error over all eight differences is3.35815e-6;
worst independent energy-gradient error is1.70974e-7N. Every side probe
retains exact held caps, original geometry and energy/force replay gates.
They are straight-line derivative probes with a base first-order constraint;
no exact nonlinear incompressible trajectory or nonlinear branch is accepted.

[Evidence packet](../../data/anatomical-arm-v1/review/frozen-volume-admissibility/)
retains source-bound requests, exact mesh/coordinates, all-row moment maps,
direct Gram operators, full kernel bases and restricted spectra, both witness
types, complete independent derivatives,32/256 observations, original gates,
execution log and manifest. Kernel/assembled fields were persisted before
optional checks. The single execution exited0 in17.75s. All79 older packet
files are hash-identical, including every failure, original threshold and
fine1.25 UNQUALIFIED record. Frozen material/operator sources are unchanged.
No production anatomy, main, book, Lean, history rewrite, credentials/network
configuration or ONNX download was involved.

The original pressure-residual diagnosis remains: RMS(logJ-p_h/K) is the
continuous-P1 L2 projection complement. The weak equation can be satisfied
while local volume varies; it does not bound RMS(J-1) or total volume change.
The old reproduced coarse failure3.35127e-4 remains failed against1e-6;
the failed nonlinear fine diagnostic supplies no convergence order. The new
affine kernel result neither relabels those states nor changes their cause.

Numerical tolerances/rank cutoffs address discrete calculations. The retained
155000Pa educational TypeI source and its reported50000Pa descriptive SD
refer to the original fiber experiment, with separate transfer/constitutive
uncertainty. That spread is not a numerical acceptance tolerance, an in-vivo
calibration or a reason to alter the gates. No amplitude fitting is performed.

Stop here for independent parent review of the full physical operator and
restricted witness. The smallest justified next step is to review this
volume-admissible negative direction together with the separate matched-force
response evidence before authorizing any further model. This coarse result
does not establish continuum convergence, nonlinear volume control, freedom
from locking, anatomical validity or incompressible pressure stability; no
source bug or proposed production fix is established by this diagnostic.
