# Exact activation equality properties

This independent proof packet checks 15 Lean declarations, including domain and
algebra helpers, for the unchanged activation equation. It extends no numerical
qualification and does not authorize the held combined incoming-event matrix.
No book claim counts, existing packets, solver equations or tolerances change.

The primary equation is the pinned [OpenSim 4.5.2 source](https://github.com/opensim-org/opensim-core/blob/5bc7d3308eda742690f485ec060bfe725a349fa6/OpenSim/Actuators/MuscleFirstOrderActivationDynamicModel.cpp#L72-L86),
retained [locally](../../data/millard-reference-v1/upstream/MuscleFirstOrderActivationDynamicModel.cpp).
Its [manifest](../../data/millard-reference-v1/upstream/manifest.json) binds the
source commit and SHA-256. Define the clamped activation
\(a_c=\min(1,\max(a_{\min},a))\) and \(S(a_c)=\tfrac12+\tfrac32a_c\). Then

\[
\tau_A=T_A S(a_c),\qquad \tau_D=T_D/S(a_c),\qquad
r(a_c,u)=\begin{cases}(u-a_c)/\tau_A&u>a_c,\\(u-a_c)/\tau_D&u\le a_c.\end{cases}
\]

Defaults are \(T_A=1/100\) s, \(T_D=1/25\) s and \(a_{\min}=1/100\).
[Lean source](../../proofs/ActivationEquality.lean) uses exact real fractions;
`clamp_identity` proves that clamping leaves the rate unchanged for
\(a_{\min}\le a\le1\). For physical use, assume
\(T_A>0,T_D>0,0\le a_{\min}\le a\le1\), and admissible excitation
\(a_{\min}\le u\le1\). Individual proofs often require fewer assumptions,
listed exactly in the [claims inventory](../../proofs/activation-equality-claims.json)
and kernel receipt. Real division is total in Lean; unconditional algebraic
zero/continuity statements at degenerate parameters are not physical claims.

| Declarations | Checked conclusion | Required assumptions |
| --- | --- | --- |
| `clamp_identity` | Clamped and in-domain rates agree | \(a_{\min}\le a\le1\) |
| `scale_positive`, `time_constants_positive` | Positive scale and both positive branch time constants | \(a\ge0\); for time constants, \(T_A,T_D>0\) |
| `one_sided_equality`, `rate_equality` | Both branch extensions and the selected rate equal zero at \(u=a\) | Exact real algebra |
| `positive_above`, `negative_below` | Activation moves toward excitation on either side | \(a\ge0\), the selected time parameter positive, strict side inequality |
| `restoring_sign`, `restoring_strict` | \((a-u)r\le0\), strictly negative if \(a\ne u\) | \(a\ge0,T_A,T_D>0\); strict case also \(a\ne u\) |
| `lower_boundary_inward`, `upper_boundary_inward` | Nonnegative rate at the lower boundary and nonpositive rate at 1 | Lower: \(T_A>0,a_{\min}\ge0,u\ge a_{\min}\); upper: \(T_D>0,u\le1\) |
| `continuous_excitation` | Continuous in \(u\) for each fixed \(a,T_A,T_D\) | Exact real algebra and topology; physical denominators separately positive |
| `deactivation_rewrite` | \(r_D=(u-a)S(a)/T_D\) | Exact real algebra |
| `coefficient_agreement_iff`, `default_coefficients_at_upper` | Branch coefficients agree iff \(T_D=T_A S(a)^2\); defaults agree at \(a=1\) | Iff: \(a\ge0,T_A,T_D>0\); default case exact stated constants |

Continuity follows from continuous affine branch extensions in excitation and
their equal value on the switching boundary. The coefficient result prevents a
blanket assertion that branch derivatives always differ: the default coefficients
agree at the upper endpoint. It proves the coefficient identity, not a derivative
theorem, joint continuity, differentiability along a controller trajectory,
existence/uniqueness, or forward invariance of ODE solutions. Boundary signs alone
do not establish an interval invariant for an implemented discrete solver.

The [Python reference](../../tools/millard_reference_benchmark.py#L58-L60)
clamps before selecting both the branch and time constant. The existing
[native vertical model](../../web/vertical-force-model.js#L50-L51) uses the raw
activation in its time constant and the clamped activation in its numerator;
it agrees with these equations on the stated admissible activation domain.
Equivalence outside that domain is not claimed. This existing scope distinction
is recorded without changing either implementation. The
[equality diagnostic](../../tools/run_activation_equality_diagnostic.py#L21)
uses the same original branch extensions. Formal proofs do not certify these
programs, their decimal arithmetic, event roots, RK refinement order or anatomy.

Reproduce with the already pinned toolchain and dependencies:

```bash
OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python3 education/tests/activation_equality_proof_audit.py
OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python3 education/tools/check_activation_equality_proofs.py --tools /absolute/path/to/education/.tools
```

The isolated [checker](../../tools/check_activation_equality_proofs.py) verifies
Lean 4.19.0, the unchanged [mathlib lock](../../proofs/mathlib-lock.json), every
transitive Git revision and clean dependency source. It invokes the real compiler
with warnings treated as errors. Every theorem must appear once in the claim and
`#print axioms` inventories. No admissions or unchecked native decision are used.
All 15 checked declarations depend only on mathlib's usual `propext`,
`Classical.choice`, `Quot.sound`; no additional axiom is introduced.

The [kernel receipt](../../data/activation-equality-proofs-v1/kernel-check.json)
records exact statements, assumptions, source hashes, dependency identities,
command and compiler exit status. [Raw compiler output](../../data/activation-equality-proofs-v1/lean-check.log)
and [six audit rejection tests](../../data/activation-equality-proofs-v1/audit-tests.log)
are retained separately. The first import attempt lacked an already-built
optional module; its [source](../../data/activation-equality-proofs-v1/attempts/01-missing-import.lean)
and [failure](../../data/activation-equality-proofs-v1/attempts/01-missing-import.log)
are preserved. Existing built modules sufficed for the successful check.

No rendered anatomical trajectory is produced by this mathematical packet.
The whole-envelope/convergence goal and held combined numerical protocol retain
their prior qualification limits; parent review, merge and delivery remain separate.
