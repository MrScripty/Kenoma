# Strict-attraction scalar convex-weight proofs

This isolated author branch starts from combined incoming commit
`c1c7ba308fee51e8ad74a7aadaeffa31b970151c`; it does not descend from or edit the
held first-sliding proposal `b692d372bfcec354dfef377dc2245c3176c3e5cb` or the
separate activation-proof branch. It adds exact scalar real statements to
[FilippovConvexWeight.lean](../../proofs/FilippovConvexWeight.lean), with an
[independent claim inventory](../../proofs/filippov-convex-weight-claims.json).
No book proof registry or manuscript is modified. Sliding execution remains held.

## Mathematical statements

Let `νon` and `νoff` be real normal components of the integrating and frozen
limiting fields, and let θ weight the integrating field. Define

\[
 \theta_* = \frac{-\nu_{off}}{\nu_{on}-\nu_{off}},\qquad
 N(\theta)=\theta\nu_{on}+(1-\theta)\nu_{off}.
\]

With **explicit** assumptions `0 < νon` and `νoff < 0`, the proof establishes
`νon−νoff > 0`, a nonzero denominator and `0 < θ* < 1`. For any nonzero
`νon−νoff`, the proof establishes `N(θ*)=0` and that every real θ with
`N(θ)=0` equals θ*. The uniqueness statement does not require θ to be assumed
convex in advance; strict attraction supplies its strict convexity. It is
uniqueness of this scalar weight, not uniqueness of an ODE solution.

The Lean theorem `strict_attraction_selection` bundles the bounds, zero mixed
normal and scalar uniqueness. Its supporting declarations and model rewrites
make **14 checked theorem declarations** only after a fresh successful kernel
receipt is available. The separate source file provides all assumptions; no
unproved equation is introduced as an axiom.

## Exact mapping to the approved source convention

The [existing derivation](antiwindup-continuation-analysis.md) and unchanged
[bounded runner](../../tools/run_filippov_bounded_experiment.py) use

\[
 H=\eta(b-B),\quad b=u_b+.4e+I,\quad d=.4\dot e,\quad k=8e,
 \quad \nu_{on}=\eta(d+k),\quad \nu_{off}=\eta d.
\]

| Proof symbol or assumption | Declared model interpretation |
| --- | --- |
| `νon` | Normal component of the **integrating** limiting field, whose I rate is k |
| `νoff` | Normal component of the frozen limiting field, whose I rate is 0 |
| θ | Coefficient of the integrating field in `θ f_on+(1−θ) f_off` |
| `η` | +1 at upper B=1; −1 at lower B=.01; both nonzero |
| `0 < νon`, `νoff < 0` | Exact strict attraction; numerical gates require margins greater than 1e−8/s |
| `νon−νoff ≠ 0` | Required denominator for generic zero-normal selection and uniqueness |
| `k ≠ 0` | Implied by opposite model-normal signs; also explicit in algebraic I-rate statements |

`source_normal_gap` proves `νon−νoff=ηk`. For nonzero η and k,
`source_weight_identity` proves `θ*=−d/k`, so `source_weight_strict_bounds`
places the existing source weight strictly inside the unit interval.
`source_integral_rate` proves

\[
 (-d/k)k + (1-(-d/k))0 = -d.
\]

`source_normal_tangency` substitutes this scalar I rate into `η(d+I_rate)`
and proves zero. `source_unique_weight` identifies any zero mixed-normal
weight with `−d/k` when η and k are nonzero. These are algebraic substitutions;
Lean does not prove the spatial gradient formula or differentiate H along an ODE.
The meanings of d, k and the normal components are the explicitly declared
model equations mapped above.

The two mechanical limiting fields already agree at excitation B under the
[approved adapter](../../tools/filippov_source_worker.mjs). This branch changes
no excitation, field, gain, bound, normal orientation or physical law. Both upper
and lower orientations map to the same integrating-field weight. No sign
convention mismatch was found. The existing primary single-surface construction
is cited in [Dieci–Lopez](https://epubs.siam.org/doi/10.1137/080724599); distinctions
between solution conventions are documented in [Cortés](https://arxiv.org/pdf/0901.3583)
and the reviewed local derivation. The present formal result is narrower than
the existence/uniqueness results discussed in those sources.

## Compiler custody and limits

The [checker](../../tools/check_filippov_convex_weight_proofs.py) invokes the real
Lean 4.19.0 compiler with `-DwarningAsError=true` in the pinned clean mathlib
checkout. It checks all transitive Git revisions and the dependency manifest,
checks proof/claim/checker bytes against a frozen Git commit, and records exact
statements, source, binary, log and equation-source SHA-256 bindings. It refuses
to overwrite an existing compiler log or receipt. There is no manually assigned
checked status. Seven [audit negative controls](../../tests/filippov_convex_weight_proof_audit.py)
reject admissions, custom axioms, hidden/missing declarations, mismatched
inventories and unsupported/missing/duplicate kernel reports.

Only the standard foundational dependencies `propext`, `Classical.choice` and
`Quot.sound` are allowed. No custom axiom, admission or unchecked native tactic
is allowed in the accepted source. Failed compiler runs may print `sorryAx` as
Lean's error-recovery placeholder; those runs remain **failed**, with no checked
receipt. Their exact source/log hashes and exit statuses are preserved in the
[attempt manifest](../../data/filippov-convex-weight-proofs-v1/attempts/manifest.json).

A failed environment invocation, a missing ring tactic import and then three
warning-as-error findings were preserved. The corrected source imports the full
ring tactic and removes unnecessary tactic sequencing; no warning is disabled
and no theorem assumption changes. The successful preliminary compile is also
retained. A separate frozen-source fresh compilation provides the final receipt.

These statements do not prove that a floating-point event lies on H=0, that
computed normals satisfy their exact assumptions, that state handoff is bitwise
continuous, or that an ODE exists, remains on the surface, is unique or stable.
They do not resolve zero-normal/error degeneracy, an exit law, hidden roots,
command changes, force/work convergence or anatomical credibility. No sliding
matrix, trajectory advancement, first-sliding protocol change, activation-proof
change, book adoption, main merge or deployment is performed.
