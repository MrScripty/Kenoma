# Reviewed sliding-stage policy: implementation and structural freeze

Parent conveyed independent ACK of the narrow proposal and authorized this
implementation plus **structural preflight only**. A new matrix is not authorized.
The proposal at `a522899d089d4249bf20e27b2545723b41d3f2f2`, the old nine-of-twelve
result and its original failures remain unchanged. This is exploratory numerical
policy work, not production adoption or anatomical-envelope qualification.

The [new engine](../../tools/sliding_stage_policy_engine.py) inherits the original
decoder, RHS coordinate layout, Jacobian, entry localization/handoff, accepted
interval preparation, witness rows, commit and custody fingerprint. Its only
constraint-admissibility exception is the conjunction:

```
representation == full-source
mode == sliding
role == ODE-stage
```

That role includes unaccepted initialization, RK stages, adaptive error-control
and dense-construction RHS probes. Classification never uses timestamp; a probe
at the final requested time remains unaccepted. The same coordinates evaluated
as candidate endpoint, polynomial guard, GL8, grid/history/witness or diagnostic
must pass the original native and independent |H|≤1e−9 checks. Unknown roles are
strict by default. Incoming/localization checks remain unchanged. A caller cannot
disable constraint checks except for the existing labeled Jacobian auxiliary.

Full native I remains an integrated coordinate without projection, reset,
reconstruction or correction. The auxiliary field remains p_dot=G(p,B),
I_dot=−d, with original ledger derivatives. Off-surface stages are numerical
auxiliaries, not physical sliding states. Every actual RHS probe retains original
finite/domain, force, strict signs/weight, activation, independent normal/tangent,
cumulative and segment work/impulse checks. Signed native and independent H,
the original gate and would-fail flags are recorded even for admitted auxiliaries.
If field evaluation fails before H is available, the failed coordinates/code are
retained and H/flag are explicitly unavailable. Fixed Jacobian auxiliaries keep
their original separate constraint/ledger exemptions and physical checks.

**Norm wording correction:** retain the exact original full-eleven and
reduced-ten SciPy error norms and scaling, rather than describing a physical-only
norm. Full I and all six ledger coordinates contribute in the full method;
all six ledgers contribute in the reduced method, whose I retains the original
decoding and external comparison gate. No component weighting, exclusion, norm
replacement or coordinate transformation is added. Constructor keywords remain
rtol1e−9, atol1e−11, max_step=.0005, with first_step omitted so its existing
default None applies, and the original Radau Jacobian. RK4 arithmetic, four
200/100/50/25 µs levels, next-1 ms caps, endpoint .263 s, twelve cells, four
.26225/.2625/.26275/.263 witnesses and the inherited 12,000-step watchdog remain.

The candidate builder does not mutate accepted custody. The shared transaction
method validates the entire candidate interval before the inherited commit.
On any physical or accepted-curve failure it preserves exact accepted state,
time, history, events, quadrature, interval count and entry custody, saves failed
traces, and explicitly drops the solver cache. A terminal failed cell cannot
invoke a producer again. There is no smaller-step rescue or retrospective pass.
Ordinary adaptive error control remains SciPy's existing policy, with all RHS
evaluations retained. The public advance method refuses while the frozen packet's
matrix-execution authorization is false.

The [structural preflight](../../tools/preflight_sliding_stage_policy.py) makes
no actual ODE solver constructor or step calls. It freshly runs the original
twelve own-root/pre-entry checks without accepting entries, compares the new
unchanged handoffs, and tests the three archived rejected vectors in the new
auxiliary role against accepted roles at identical coordinates and timestamps.
It additionally checks their auxiliary classification at entry timestamps.
Eight static failure producers issue valid auxiliary probes and then trigger
domain, activation, strict-sign, ledger, endpoint, GL8, actual interval-guard or
history-witness rejection through the shared transaction path. The latter dense
functions are deliberately injected negative controls, not claimed ODE-generated
polynomials. Exact rollback, cache-object release and no retry are checked.

Structural norm checks compare original/new constructor keywords, inherited
methods, and actual SciPy error-norm arithmetic for every one of the eleven/ten
integrated components across all twelve cells. These are zero-step tests, not
evidence that any new cell completes. Subsequent execution needs a separately
authorized frozen runner and an independent auditor honoring this role table;
the old auditor's requirement that all internal native stages satisfy H cannot
be silently reused or retrospectively edited.

The mathematical rationale remains the [unchanged held proposal](sliding-constraint-policy-proposal.md)
and its original-source citations. The separate local Lean proof at
`67491e95a43f8a4411c21ca6fa3a156345943015` establishes exact scalar algebra only;
it does not approve stage admissibility or validate a numerical trajectory.
All accepted state/force/event/constraint/normal/tangent/work/impulse comparison
gates remain original. The internal H rejection is explicitly changed, so no
claim that every check is unchanged is made. Both older external raw-review gaps
remain disclosed. No equation, book, main, skin, failed case or old result changes.
