# First short sliding segment: held proposal

**No sliding execution is authorized by this packet.** The combined incoming
result at `c1c7ba308fee51e8ad74a7aadaeffa31b970151c` has a scoped exploratory ACK
for source semantics, freeze identities, twelve replay bindings, 570 compact
tables, 3,990 margin calculations and 264 event-time comparisons. Its full
external raw replay remains unavailable after transfer cancellation; historical
activation raw replay is also incomplete. No transfer retry/reroute is made.
The ACK is not incoming full qualification or fourth-order convergence.

Parent review of this proposal and explicit execution authorization must precede
any accepted entry or sliding integration. No book release, main change, new
controller/physical law or anatomical qualification is proposed. The separate
Lean branch and every prior failure remain preserved.

## Approved law and representation equivalence

Reuse the [owner-approved Filippov convention](filippov-bounded-experiment-results.md)
and [reviewed derivation](antiwindup-continuation-analysis.md), including their
strict, single-surface domain and absence of an exit law. Let
\(p=(y,w,a,q)\), \(e=(r-F_T)/100\), \(b=u_b+.4e+I\),
\(B=.01\), \(\eta=-1\), \(H=\eta(b-B)\),
\(d=.4\dot e\), \(k=8e\). On the surface the two off-surface mechanical
fields agree at \(u=B\); only their I rates differ. Thus

\[
f_S=\theta f_{on}+(1-\theta)f_{off},\quad
\theta=-d/k\in(0,1),\quad \dot p=G(p,B),\quad \dot I=-d.
\]

The full native-source representation advances eleven coordinates (four physical,
I and six accumulated work/impulse coordinates). The independent representation
advances ten on sliding, reconstructing \(I=B-u_b-.4e(p)\) from its own
BPoly/Brent kernels. In exact arithmetic at H=0 these formulations agree:
differentiating the reconstruction gives \(\dot I=-.4\dot e=-d\), and
both use the same physical field and ledger rates. This conditional equivalence
does not prove binary64 equality, a discrete invariant, biological response,
global residence or uniqueness through an exit. Source assumptions and primary
references remain those of the reviewed derivation; no replacement antiwindup,
finite-gain back-calculation, damping, hysteresis or smoothing is introduced.

## Entry custody and numerical handoff

Every cell retains its own original mass-1 initialization/configuration, actual
incoming polynomial, last accepted eleven-coordinate state, last accepted
quadrature ledger and held candidate from c1c7ba3. Never borrow another cell's
time/state or splice a shared tail. The proposed entry must come from that cell's
original integrating/deactivation incoming auxiliary; no mixed/sliding field is
used in localization. Preserve original clipping and every physical probe gate.

The coarse held H residuals span about 1.2865e−9, exceeding the existing 1e−9 I
comparison gate. Those finite residuals are not new trajectory failures, but they
can contaminate a full/reduced entry comparison: full coordinates retain I while
the reduced reconstruction differs from incoming I by a finite amount.

For parent review, propose fresh localization on the **same actual incoming
polynomial**, starting at its original trial bracket, with **bracket ≤1e−12 s
and |H|≤1e−13 within the unchanged 32-bisection budget**. This tightens solver
targets, not the original 1e−9 constraint/I-coordinate or 2e−6 s event acceptance
gates. Do not continue the old coarse solve with an extra budget, substitute a
polynomial, shrink a physically failed step or manufacture a root by projection.
An unresolved root retains the old accepted state and blocks the complete matrix.

The [read-only preflight](../../tools/first_sliding_segment_preflight.py) diagnoses
this proposal on stored polynomials only. Its root candidates remain unaccepted;
it instantiates no ODE solver, computes no new integration stage and advances no
accepted physical state/time. Static incoming kernel/GL8 evaluations are distinct
from a sliding trajectory and do not repeat the incoming matrix.

After review, certify the incoming prefix from the old accepted time to the
approved entry, excluding its entire trial suffix. Preserve all eleven entry
coordinates exactly in the full representation. Accumulate the original GL8
work/impulse increment into the old independent quadrature; retain all six
historical ledger coordinates instead of zeroing them at entry. Save exact old,
entry and next-solver states, polynomial hash and all stages/probes.

The reduced representation preserves the four physical and six ledger coordinates
exactly but decodes I from the constraint. **Record signed delta-I, signed delta-raw
and whether I is bitwise preserved. A nonzero discrepancy must not be called
exact I continuity or a zero jump.** The approved numerical coordinate gate
remains |delta-I|≤1e−9; the proposed tighter root should reduce this contamination.
There is no I correction in the primary full calculation. Parent must review
this disclosed finite reduced-coordinate handoff before execution. If exact
binary64 I preservation is required, this ten-coordinate handoff cannot provide
it from a finite nonzero-H entry without a separately declared numerical policy;
stop rather than add an offset coordinate or hide a reset.

Require all twelve independent entries, original incoming absolute-time state
comparisons, event types/order and 2e−6 s event agreement to pass before any cell
enters sliding. Parent's scoped incoming ACK does not itself authorize entry.
The twelve entry states must satisfy q>.4441, taut tendon s>1, source activation
bounds/root validity, outgoing error eta*e>0, nu_on>1e−8/s and
nu_off<−1e−8/s, 0<theta<1 without clipping, negative g=B−a on the reviewed
deactivation side, |H|≤1e−9 and the disclosed coordinate gate. Unexpected pending
activation remainder, competing/touching roots, changed command/configuration or
activation-side ambiguity blocks entry. Guard samples do not exclude hidden roots
by theorem.

## Smallest proposed residence interval and comparisons

Use all twelve mass-1 cells: both representations × RK4 200/100/50/25 microseconds,
DOP853 and Radau, keeping every coarse level and all four adaptive references.
The first segment ends at the **next original absolute 1 ms boundary, .263 s**,
approximately .969 ms after entry; do not extend to .264 or a full original endpoint.
Require each cell to reach exactly .263 with no failure and retain its full
incoming history. Add matched absolute witnesses .26225/.2625/.26275/.263 s on
actual accepted dense polynomials; retain the original incoming grid including
.262 after entry-prefix certification. Never align trajectories at entry times.

Sliding uses a fresh RK step capped by the next original 1 ms boundary, matching
the approved controller restart convention; no discarded incoming trial suffix
is reused. Adaptive solvers restart at the authorized event state with original
rtol 1e−9, atol 1e−11, maximum step .0005 s and the existing physical-column
Jacobian convention, with exactly zero ledger columns. Velocity-root budget 64,
accepted-step watchdog 12,000 and every physical/geometry gate remain unchanged.

Compare all 66 pairs, entry times separately and all seven physical/controller
quantities at the four absolute residence witnesses and .263 endpoint. Preserve
the original gates [1e−6 m,1e−5 m/s,2e−6 a,2e−6 q,1e−4 N,1e−9 I,1e−8 raw],
2e−6 s event disagreement, |H|≤1e−9, normal disagreement and tangent residual
≤1e−8/s, force closure≤1e−7 N, component/combined work≤1e−5 J and
impulse≤1e−7 N*s. Retain signed maxima and exact remaining margins; no anchor
subtraction, corrected-state comparison, coarse-cell removal or tolerance change
may qualify the segment. Sparse/truncated/missing cells fail completion. Report
endpoints, references, event/localizer resolution and timestep ratios separately;
none establishes fourth-order convergence by itself.

## Residence signs, energy and explicit stops

During every sliding stage, endpoint, dense witness and original GL8 evaluation,
require source validity, eta*e>0, nu_on>1e−8/s, nu_off<−1e−8/s,
0<theta<1, H/normal/tangent gates and the reviewed activation side. The full
field has I_dot=−d; independent reduced differentiation must agree. No theta
clipping or normal-sign hysteresis is allowed.

Stop **before accepting a trial** that loses a residence sign, reaches zero error
or normal, encounters activation equality/bounds, an additional/overlapping
controller guard, changed command, slack/fiber/root/geometry failure or an
unresolved event. Retain its prior accepted state and complete failed trial.
There is no declared exit law: do not continue through a zero normal, infer an
ordinary exit from a weight near 0/1, switch back to PI, or label an early stop
successful .263 completion. Invalid physical trials cannot be salvaged by an
earlier apparently valid root or a smaller-step retry. Any new continuation
through such a boundary requires a separate mathematical protocol and review.

Check entry has no physical displacement/velocity/activation/length or six-ledger
jump; hence no added mechanical impulse/work. I is an information coordinate,
not energy storage, and its numerical representation discrepancy is reported
separately. Verify cumulative mechanical storage from the original time-zero
state and independently check segment increments from entry: fiber, tendon,
load, combined active-work/dissipation and momentum. Independent GL8 integrates
only accepted incoming/sliding intervals and excludes every rejected suffix.
Do not reset historical ledgers to disguise inherited errors.

Before a future run, parent must review this protocol and the finite handoff,
then explicitly authorize execution. Freeze actual sliding implementation,
bindings and executable runtime preflight in a separate execution packet before
its twelve-cell matrix. This preparation supplies no sliding runner, residence
trajectory, book adoption or new qualification.
