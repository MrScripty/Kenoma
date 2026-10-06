# Rejected Euler predictors: diagnosis and held numerical policy

**Proposal only.** The completed first-sliding packet remains at
`455641c0aa9b4a9ad4b68e50fc1b6f5746180226`, tree
`8dfc931e72a58730ac61b8ea34a80a0abe2bb4bf`: nine of twelve cells completed,
and the required matrix remains unqualified. This separate branch changes no
existing source, gate, input, result, book chapter or Lean declaration. It adds
read-only diagnosis of three already rejected states. No revised integration,
decoder, acceptance policy or trajectory has been implemented or executed.
Independent review and subsequent explicit execution authorization are required.

## What failed

All three native/full cells stopped at their accepted attracting entry, with
zero accepted sliding steps and exact accepted-state/time/quadrature rollback.
The evaluated predictor is not an accepted endpoint, even when its timestamp is
the requested endpoint. Domain, force, strict attraction, convex weight and
activation-side checks passed at these probes; the original |H|≤1e−9 check failed.

| Full cell | Unaccepted evaluation | Predictor offset | Native H | Gate multiple |
| --- | --- | ---: | ---: | ---: |
| RK4 200 µs | First midpoint, before c/d or candidate endpoint exists | 100 µs | 2.7785112041017745e−9 | 2.778511 |
| DOP853 | Constructor initial-step Euler RHS probe | 969.265867120 µs | 2.603989826769487e−7 | 260.398983 |
| Radau | Constructor initial-step Euler RHS probe | 969.265367020 µs | 2.6039869648226965e−7 | 260.398696 |

The [raw curvature receipt](../../data/sliding-constraint-policy-proposal-v1/predictor-curvature-diagnosis.json)
binds each original raw file and independently reevaluates it. RK correspondence
is bitwise exact using the declared h/2=.0001; subtracting binary64 timestamps
gives .00009999999999998899 instead. The original diagnosis using that subtraction
and its tiny nonzero vector difference remain preserved. Both adaptive vectors
match the archived Euler construction bitwise.

SciPy 1.17.0's [select_initial_step source](https://github.com/scipy/scipy/blob/v1.17.0/scipy/integrate/_ivp/common.py)
forms y1=y0+h0*f0 and evaluates f1 after capping h0 to the interval length;
max_step enters the final returned recommendation after that evaluation.
Consequently a .969 ms initialization probe can precede a .5 ms accepted-step
cap. Neither adaptive cell reached solver.step(). Setting first_step alone would
avoid this particular heuristic probe but would not address RK4's midpoint.

## Mathematical diagnosis under the approved law

Keep constant command r, ub, gain κ=.4, B=.01 and η=−1. Let p=(y,w,a,q),
s=(L0−y−.1q)/.2, FT=100 fT(s), e=(r−FT)/100,
b=ub+κe+I, and H=η(b−B). The existing construction uses d=κ e_dot,
k=8e, normal_on=η(d+k), normal_off=ηd, and θ=−d/k.
Strict normal_on>1e−8, normal_off<−1e−8, ηe>0 and 0<θ<1 are required.
The common mechanical field at B is p_dot=G(p,B); q_dot=10v and fiber
length derivative is v. The mixed integral derivative is I_dot=θk=−d.
This is the already reviewed single-surface Filippov construction, not a new
switching rule; see [Dieci–Lopez, §2.1](https://epubs.siam.org/doi/10.1137/080724599)
and the [local derivation](antiwindup-continuation-analysis.md).

For a forward Euler predictor from an entry, write τ for its declared offset:

```
pE = p0 + τ G(p0,B),       IE = I0 − τ κ e_dot0
δs = sE−s0 = −τ(w0+v0)/.2
HE−H0 = ηκ [e(pE)−e(p0)−τ e_dot0]
       = .4 [fT(sE)−fT(s0)−fT'(s0)δs]          (η=−1)
       = .4 ∫[s0,sE] (sE−ξ) fT''(ξ) dξ
       = .2 fT''(s0) δs² + O(δs³).
```

The identities are exact in real arithmetic when e is differentiable, and the
integral/Taylor statements require C2/C3 respectively on the interval. Here all
three intervals lie inside the same unchanged smooth tendon patch. The analytic
parametric derivative used in the independent BPoly calculation is
fT''=(y''x'−y'x'')/(x')³. Positive sampled curvature gives the observed positive
remainder; the 65-point curvature range is a diagnostic, not a certified bound.
Static quadrature of that derivative gives 2.7785154133756865e−9,
2.6039898596349887e−7 and 2.6039869733541797e−7 respectively. These should be
compared to **HE−H0**, including the signed finite entry residual, rather than
to HE alone. Maximum discrepancy is 1.70771874213e−15; quadrature's reported
error estimate excludes source/root/rounding error. The leading quadratic term
differs by about .028% for RK and .272% for the adaptive probes.

The failure therefore diagnoses a tangent Euler predictor leaving a curved
constraint surface. It does not diagnose a failed tendon equilibrium or establish
a constitutive defect. Continuous invariance H_dot=0 does not imply discrete
Euler-stage invariance. The invariant criterion is standard; see
[Hairer's original geometric integration notes, p.4](https://www.unige.ch/~hairer/poly_geoint/week2.pdf).
No global convergence or unseen-root conclusion follows from this calculation.
The unchanged elastic/damped-equilibrium assumptions retain their original
[Millard et al. source](https://doi.org/10.1115/1.4023390) and pinned OpenSim
source notices. No anatomical, bulk-energy or compression equation changes.

## Primary held option: distinguish internal probes from accepted motion

The independent reviewer recommended a distinct **stage-admissibility policy**.
For native/full unaccepted numerical probes, evaluate the auxiliary extension

```
p_dot = G(p,B),       I_dot = −κ e_dot(p;G(p,B)),
six ledger derivatives = original powers and load impulse rate at B.
```

Retain full eleven-coordinate integration, incoming I, the actual solver
polynomials and physical-coordinate adaptive error norms. No I projection,
reconstruction, reset or offset correction occurs. On H=0 this field agrees
with the approved Filippov field. Off H=0 it is a declared numerical extension,
**not a claim that the unaccepted point is a physical sliding state**.
For constant command/configuration and a differentiable error function,
H_dot=η(κe_dot+I_dot)=0 throughout this extension in exact arithmetic.
Finite entry H is retained; it is not made zero. Smooth local field/unique
velocity-root assumptions must hold on all used points. No regularization,
force modification or off-surface physical switching law is introduced.

| Evaluation role | Existing policy | Held proposed policy |
| --- | --- | --- |
| Native/full RHS stage, initialization, error-control or dense-construction RHS probe | Constraint failure stops cell | Record signed H, gate multiple and would-fail flag; no H rejection solely for this explicitly unaccepted role |
| Candidate endpoint, actual polynomial guard, GL8, original-grid/history/witness evaluation | Absolute H≤1e−9 | Same absolute H≤1e−9, native and independent |
| All actual RHS probes | Domain, force, strict signs/weight, activation side, independent normal/tangent, cumulative/segment work and impulse | Same checks and same gates |
| Fixed Jacobian auxiliary | Separately labeled; physical/force/sign checks; constraint/ledger exempt | Same convention and perturbations; never an accepted point |
| Reduced independent representation | Ten integrated coordinates, original I=B−ub−.4e decoding | Same, including finite handoff disclosure |

This **removes an internal native/full H rejection**, so a future run cannot
claim every check was unchanged. There is no replacement enlarged H tolerance
for accepted motion or hidden extra threshold for unaccepted predictors.
Record all internal defects, including nonfinite or failed probes. Finite/domain,
force, strict-sign/weight, activation, normal/tangent or retained ledger failure
still terminates the cell. Adaptive error rejection may use its ordinary
controller; a physical failure or accepted-polynomial gate failure is terminal
with no smaller-step rescue. Incoming mode and entry localization retain their
existing checks; stage exceptions must be tied to the explicit sliding trial
role, not to whether a point happens to have a convenient timestamp.

Tangency of this auxiliary field is not a discrete accepted-curve certificate.
Even with high-order endpoints, an actual dense polynomial may fail |H|≤1e−9.
That remains a legitimate terminal failure. The reduced formulation's finite
I adjustment is still not exact eleven-coordinate continuity. This proposal
does not authorize discarding any of the twelve required cells.

An alternative anchored coordinate c=I+κ(e(p)−e_entry) has c_dot=0 and can
decode I without drifting H. It is **not selected** for this bounded proposal:
it changes coordinate error control and nonlinear dense-I semantics, and needs
separate review of finite-entry preservation, anchors and serialization. There
is no implemented decoder or experiment for that alternative.

## Bounded prospective review and rollback requirements

1. Review this role table, off-surface numerical interpretation and finite-entry
   residual. Independent ACK alone is not execution authorization. After explicit
   authorization, implement in a new execution branch and freeze source/config
   hashes before any revised matrix run. Preserve this proposal and the old 9/12
   result; no retrospective pass labels.
2. Preflight all twelve own incoming polynomials with the same 32-bisection,
   width≤1e−12 s and |H|≤1e−13 localization targets, 64 velocity iterations,
   finite I/raw handoff checks and bitwise other-ten preservation. Recheck all
   66 pair comparisons on the original 0..262 ms grid before accepting any entry.
   Native/full retains all eleven entry coordinates exactly.
3. Test classification with the three archived probes only: full auxiliary RHS
   must reproduce original rates, retain input bits and report H as unaccepted;
   the same coordinates labeled endpoint/guard/GL8/witness must reject. Test
   independently a later invalid force/domain/sign/activation probe after a valid
   probe, and a failed endpoint/guard/GL8/witness after valid internal stages.
   Verify exact accepted state/time/history/events/quadrature/count rollback.
   Solver caches must never be reused after terminal failure. Preserve trial
   traces separately from accepted custody, including roles and source hashes.
4. If preflight passes and frozen execution is authorized, run exactly the same
   twelve mass-1 cells: both representations × RK4 200/100/50/25 µs, DOP853 and
   Radau, through absolute .263 s. Keep next-1 ms RK caps, adaptive first_step=None,
   rtol1e−9, atol1e−11, max_step=.0005 and fixed Jacobian. Keep the 12,000 total
   accepted-step watchdog including incoming steps and original tiny-step check.
   Freeze no parameter sweep, new exit rule, iteration increase or retry policy.
5. Prepare the whole trial transaction before committing it: unchanged domain,
   force, signs, tangent/normal and work/impulse gates on the actual candidate
   endpoint, existing start/mid/end and GL8 polynomial probes, plus original-grid
   points and .26225/.2625/.26275/.263 witnesses falling in that interval.
   Any failed accepted-polynomial probe preserves previous accepted custody and
   the entire failed trial. Retain all RHS calls from rejected adaptive trials;
   never put them in the accepted trajectory or quadrature.
6. Audit each stored actual polynomial independently and reevaluate all accepted
   witnesses and GL8 nodes with independent kernels. Check all 66 pairs at the
   original absolute times without alignment, candidate event gate 2e−6 s,
   seven state gates [1e−6,1e−5,2e−6,2e−6,1e−4,1e−9,1e−8], constraint1e−9,
   force1e−7 N, normal/tangent1e−8/s, all component/combined work1e−5 J and
   impulse1e−7 N*s. Require all twelve complete for the bounded matrix result.
   Report the largest internal defects separately from accepted-curve defects.

No future outcome is predicted by this proposal. Sampled accepted checks are not
a continuous constraint or hidden-root theorem. Scalar Lean declarations remain
limited to their algebraic claims; no numerical-policy proof is asserted.
Both older external raw-review gaps remain explicitly incomplete; the fresh
first-sliding raw replay ACK does not close them, and no canceled transfer is
retried or rerouted. Anatomical bulk/compression and self-consistent dense arm
lift/release remain unqualified; no skin, book adoption, deployment or merge.
