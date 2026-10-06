# Bounded P2/P1 pressure-residual diagnosis

Frozen entry: `education/source-amplitude-p2-p1`, commit
`dc9f22cbc8e0b04fceb062a6e0e7ab0bb8db6d16`, tree
`90527b2013c4a2a08798a48ca87c82b8ce9f8e91`. Separate worktree and
branch `research/pressure-residual-diagnosis`. No AGENTS.md or .agents/skills
files were present in the selected workspace or frozen repository tree.
Repository-local author/committer identity is MrScripty
<TheEnvironmentGuy@protonmail.com>. No main, book, Lean, production anatomy,
production mechanics, existing receipts, thresholds or contractile-state work
changed. This is a diagnosis, with no proposed source fix or accepted successor.

## Meaning of the diagnostic

[Source operator](../../tools/full_p2_p1.py) eliminates pressure via
`M p = K b`, where `b_i = integral Q_i log(J) dV0` and
`M_ij = integral Q_i Q_j dV0`. Thus `p/K` is the quadrature-weighted L2
projection of `log(J)` into **continuous P1**. The condensed volume energy is
`K/2 b^T M^-1 b`, not `K/2 integral log(J)^2 dV0`.

The reported **pointwise pressure RMS** is
`sqrt(integral [log(J)-p_h/K]^2 dV0 / V0)`: a dimensionless projection
compatibility error, not pressure in Pa, not the nonlinear force residual,
and not RMS(J-1). Multiplication by K gives an equivalent constitutive
pressure mismatch (335.127 Pa in the reproduced coarse case). The weak
RMS uses `b-Mp/K` and the pressure mass inverse. Exact weak elimination
annuls its moments while permitting a nonzero orthogonal complement.

Because P1 contains constants, the compatibility error also has zero mean
under the solve quadrature. This does not imply local or total volume is
exactly preserved: finite K allows represented log-volume change, and
`mean(exp(log J))` differs from `exp(mean(log J))`. A homogeneous finite-K
patch can pass the 1e-6 compatibility gate while J differs from 1 by much
more than 1e-6. The old gate remains an additional numerical qualification
target, not an identity of the discrete weak method or an experimental
uncertainty interval.

## Bounded execution and reproduction

[Runner](../../tools/diagnose_pressure_residual.py) starts with the archived
coarse initial coordinates, material155000Pa, activation1, stretch1.01,
256 points, and the unchanged80 Newton /24 backtracking budget. It then
uses the existing8x2x2 fine mesh and identical prescribed-case initial
construction for the explicitly authorized diagnostic refinement. Neither
case advances history or changes the old failed classification. All old
packet file hashes are recorded and checked unchanged. Requests are written
before execution; outputs refuse overwrite.

The coarse solve again stops after4 steps. Force residual is
**3.08343838535e-5 N**, pressure compatibility RMS **3.35127148750e-4**.
Maximum coordinate difference from the archived failed result is
**5.48006085e-13 m**; force-residual difference **5.54985623e-12 N**.
The original failure is reproduced, not reclassified.

| Reproduced coarse quantity | Value |
| --- | ---: |
| Reference volume | 5.6e-5 m3 |
| Deformed volume | 5.600056078751e-5 m3 |
| Mean J-1 | 1.00140626729e-5 (0.0010014%) |
| RMS J-1 | 3.35252403007e-4 (0.0335252%) |
| Sampled J, including corners | 0.997580712506–1.001889375399 |
| Mean log J | 9.95786045060e-6 |
| RMS represented p/K | 9.96935974792e-6 |
| Weak pressure RMS, direct residual integration | 6.41998516490e-20 |
| Mean compatibility error | 2.40030088464e-20 |
| Inner product of compatibility error and p/K | 2.67649235700e-25 |
| Maximum node distance from exact homogeneous patch | 1.65016392415e-5 m |

The orthogonal complement dominates the local volume RMS. Global volume
is close to the finite-K analytic patch despite spatially nonuniform
expansion/compression. This is considerably below the unchanged2% geometry
band, but it fails the unchanged1e-6 compatibility target by335x.

### Quadrature and independent implementation

At **frozen coordinates and frozen256-point pressure**, compatibility RMS is
**3.35127307214e-4 / 3.35127148750e-4 / 3.35127138880e-4** for
32/256/2048 points. The256-to2048 change is9.87e-12 absolute,
2.95e-8 relative. These are evaluations, not new solves.32/256-point
original Node replay gives maximum force-assembly differences
**7.58722309e-7 / 3.58706120e-14 N**, below the original2e-6 gate.
No quadrature change can account for the335x rejection.

In `quadratureFrozenPressure`, pressure/volume diagnostics use the supplied
frozen pressure, while `forceResidualN` is the independently re-eliminated
Python force for that quadrature. Use `originalGateChecks.replays` for
**frozen-pressure** original Node force residuals. This distinction prevents
confusing different32-point pressure eliminations.

### Solver sensitivity, without a retry

At the failed coarse terminal candidate, one **unaccepted** exact Newton
proposal has maximum nodal correction2.85133036e-6m and linear relative
residual3.97e-13. Its evaluated force drops to6.77284762e-6N but pressure
RMS **increases to3.67988823e-4**. No iterative continuation follows it.
The local tangent eigenvalue magnitude ratio is1.0921e5; its smallest
absolute eigenvalue is0.594844744N/m. Small force alone therefore does not
bound nodal or pressure error, and more Newton iterations are not justified
as an automatic pressure repair. This failed-candidate tangent audit is not
an accepted stability classification.

## Operator cause and boundary control

The exact affine patch under the **same complete cap constraints and
traction-free sides** has coarse force3.98824911e-13N, compatibility
RMS9.37151963e-16, constantJ=1.000009997014 and pressure9.996964Pa.
It passes the original stationarity gates. Boundary incompatibility or an
unrepresentable affine reference is therefore not required for this failure.

[Independent operator audit](../../tools/diagnose_pressure_operator.py)
evaluates that exact patch on both existing meshes. The mixed tangent has
lowest eigenvalues **-32.23543649 / -27.95365851 N/m** and9/48 negative
directions. Original Node full-gradient differences verify the respective
lowest actions at1e-7/5e-8m with relative errors
**6.28e-8/9.61e-8** and **9.83e-8/2.35e-7**, below the original1e-4
derivative target. This is an exact-patch operator result; it supplies no
accepted spectrum for the archived failed candidate.

At stretch1.01 the instantaneous active fiber stress derivative is
**-24790.08Pa**, passive fiber derivative **+21236.73093Pa**, total
**-3553.34907Pa**. The weak pressure operator gives little resistance to
the lowest volume-sensitive directions. Pressure coupling is nevertheless
full rank **20/20 and81/81**, scaled beta **0.579613738 /0.512673010**,
ratio **0.884508038**. There is no pressure gauge/rank failure indicated
by these tests, and this two-level rank check is not a mesh-family theorem.

At the affine patch, the Hessian difference between a hypothetical
pointwise volume penalty and the mixed volume projection is exactly
`K [integral d(log J)^2 - db^T M^-1 db]`, a positive semidefinite
projection complement. For the respective lowest mixed directions:

| Exact patch quantity, Euclidean nodal normalization | Coarse | Fine |
| --- | ---: | ---: |
| Weak volume Rayleigh term, N/m | 0.038721317 | 0.004407979 |
| Hypothetical pointwise volume Rayleigh term, N/m | 17628.52415 | 13791.30062 |
| Missing projection complement, N/m | 17628.48543 | 13791.29621 |
| Same-direction hypothetical total, N/m | 17596.24999 | 13763.34255 |

[Full hypothetical operator comparison](../../tools/diagnose_pointwise_comparison.py)
gives lowest eigenvalues **+2.171928985 /+0.364033353 N/m**, with no
negative eigenvalues on these two exact patch meshes. The complement's
minimum eigenvalues are-7.38e-11/-3.83e-11N/m, roundoff-scale compared
with its positive terms. This isolates the pressure projection's omitted
volume stiffness interacting with the active tangent in this configuration.
It does **not** select the pointwise penalty as a physical fix: that would
change the discrete functional, and positivity at one affine configuration
does not prove nonlinear, nonuniform or continuum validity. No coefficient,
pressure basis, production operator or acceptance target was changed.

## Diagnostic refinement

The recovery fine solve stops at **iteration34** with reason **True tangent
linear residual rejected**: actual linear relative residual
**1.45786308421e-10**, above the unchanged1e-10 guard. It does not exhaust
or extend the80-iteration limit. Force residual is **2.07745783062e-4N**,
compatibility RMS **1.44805701916e-3**; both original gates fail. The
pointwise mismatch is **4.321x the coarse value**, so this refinement does
not demonstrate convergence. No accepted coarse/fine pair exists.

| Fine recovery volume quantity | Value |
| --- | ---: |
| Deformed volume | 5.600059164098e-5m3 |
| Mean J-1 | 1.05650175757e-5 (0.0010565%) |
| RMS J-1 | 1.44828121848e-3 (0.1448281%) |
| Sampled J, including corners | 0.991204435507–1.010503602701 |
| Weak pressure RMS, direct residual integration | 3.48100671334e-19 |
| Equivalent pressure mismatch RMS | 1448.057019Pa |
| Maximum interpolated coarse/fine node difference | 3.51864644774e-5m |

The exact fine affine patch remains an excellent boundary/operator control:
force4.80049860e-13N, compatibility1.90288395e-15. At the failed fine
terminal geometry, frozen-field32/256/2048-point compatibility RMS is
1.44805505526e-3 /1.44805701916e-3 /1.44805714277e-3. The256-to2048
change is1.2361e-10 absolute,8.54e-8 relative. Original256-point Node
force assembly agrees within1.87410851e-14N. The32-point replay's
assembly difference **2.63548664e-6N** exceeds the original2e-6N
gate and is retained as another failure; it does not explain the large
pressure mismatch. Both Node replays fail force and pointwise pressure,
while weak pressure, reaction/work, held caps, sampled geometry and strict
crossing gates pass. The full coarse/fineJ-extrema difference is about
0.00861423, exceeding0.005; no passing interpolation or reaction measure
is used to qualify the pair. Recovery elapsed time405.694s.

The first fine solve returned, but its exporter evaluated an optional,
unaccepted Newton sensitivity proposal before writing terminal fields. That
proposal hit the unchanged positive-geometry guard, causing an export
exception and exit1. The terminal solve fields from this attempt were not
persisted, so no convergence result is inferred from it; the fine numbers
above refer exclusively to the new recovery receipt. The exact first
runner is archived as `diagnose_pressure_residual-v1.py`; its hash matches
the original coarse/fine requests. The exception log and
`fine-export-failure.json` remain intact.

One deterministic **receipt recovery** repeats the same fine inputs and
80/24 limits, writes terminal coordinates/pressure/history immediately
after the solver returns, and omits that optional fine sensitivity proposal.
The separate `fine-recovery-request.json` records the amended exporter hash;
its material, activation, mesh, initial coordinates, budgets, source hashes
and numerical gates exactly equal the first fine request. This is an
explicitly reported diagnostic-exporter repair, with no production source
fix, changed convergence strategy or attempt to obtain acceptance. The
isolated [exporter fault-injection regression](../../tests/test_pressure_diagnostic_export.py)
confirms that an exception in post-solve diagnostics leaves the terminal
coordinates, pressure, history and diagnostic-only label on disk. It passed;
`export-regression.log` records the result.

## Diagnosis and next step

The failure directly measures a **continuous-P1 log-volume projection
error**. The implementation consistently solves the declared weak mixed
equations. The combination of weakly penalized unresolved volume directions
and the negative active fiber tangent is demonstrated at an exact patch;
the force-only stopping rule does not control this additional pressure
target. It is not evidence of boundary inconsistency, inadequate integration,
or an identified source bug. Two independently initialized perturbed solves
cannot establish a convergent nonlinear branch or a pressure convergence
order, especially with an indefinite operator. No old receipt is accepted
and no longer solve is recommended from this evidence.

The smallest justified next step is **parent review of the volume operator
contract**, using the frozen-fields projection-complement and true tangent
receipts, before authorizing one pressure-space/stabilization study. Such
a study must state which discrete energy it approximates, verify its actual
tangent, weak residual and local/global volume errors, and reuse the original
coarse/fine budgets and gates. It must remain separate from the other worker's
contractile-state response development. No source fix/regression is proposed
because no source bug was demonstrated here.

The155000Pa source is a reported TypeI mean, with reported SD50000Pa,
for the retained skinned-fiber experiment. That descriptive spread and the
unmeasured mapping to this educational block are physical-data uncertainties;
they do not license changing the1e-6 numerical compatibility target, the
1e-4N force target, or the2% sampledJ engineering band. No matched-specimen,
whole-arm, transient, clinical or calibrated-volume claim follows.

## Evidence and limitations

All additive requests, coordinates, pressure, histories, original Node
replays and mathematical comparisons are in
[pressure-residual-diagnosis](../../data/anatomical-arm-v1/review/pressure-residual-diagnosis/).
The existing full-P2/P1 tests (4) and source-amplitude/scope tests (4)
passed; raw output is `tests.log`. The exporter recovery regression also
passed. No changed optimizer, new starts,
material changes, threshold changes, downloads or history rewrite occurred.
The post-stop proposals are explicitly labelled one-step sensitivity
evaluations, not accepted solves; the first fine proposal caused the preserved
export exception and is omitted in recovery. Exact patch spectra use Euclidean nodal
normalization, so their magnitudes are mesh dependent. Sampled integration
points/corners do not certify globalJ extrema; existing triangulated surface
checks do not certify curved surfaces, coplanar overlaps or containment.
