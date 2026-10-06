# Opposing antiwindup surfaces: mathematical continuation before implementation

The literal conditional-integration ODE has **no local Carathéodory continuation** at either observed strictly attracting surface. If the owner explicitly adopts the Filippov solution convention, the same two off-surface fields have a **locally unique, force/work-consistent sliding completion**. That convention is a meaningful extension of the declared model semantics. It is not a completed numerical qualification, nor a finite-gain back-calculation controller. An explicit reviewed boundary policy is required before replacing the frozen stop. No continuation solver or new trajectory is implemented here.

Frozen review baseline: 504585b962fc4d1a5ad359d24e902d86cc3d7c4b. Its ten full and two prefix-only classifications remain unchanged. This analysis concerns only the upper surface of high and lower surface of mass-1, on constant-command intervals before their next scheduled transitions. It makes no whole-arm, anatomical or descending-stability claim.

## 1. Existing fields and their surface normals

Write the mechanical state as \(p=(y,w,a,q)\), with integral state \(I\). On the declared source-valid domain, retain

\[
 F_T=F_0 f_T(s),\quad s=(L_0-y-l_{f0}q)/l_{t0},\qquad
 R(v)=F_0[a f_L(q)f_V(v)+f_P(q)+\beta v]-F_T=0,
\]
\[
 \dot p=G(p,u)=\left(w,(F_T-mg)/m,A(a,u),v_{max}v\right).
\]

Here \(F_0=100\) N, \(l_{f0}=.1\) m, \(l_{t0}=.2\) m, \(v_{max}=10\)/s and \(\beta=.1\), so \(\dot l_f=l_{f0}v_{max}v=v\) m/s numerically. Source activation \(A\), all curves, excitation limits .01/1, force-root bracket/iteration limits and physical failure gates remain unchanged. At the retained points, \(R_v=F_0[a f_L f'_V+\beta]\ge10\) N per normalized velocity. A bracketed root is locally unique and smooth; this justifies reducing the source algebraic equilibrium to an ODE locally. It does not qualify slack or lower-length transitions.

For constant command \(r\), define

\[
 e=(r-F_T)/F_0,\quad b=u_b+k_p e+I,\quad u=\operatorname{clip}(b,.01,1),
 \qquad k_p=.4,\ k_i=8\ {\rm s}^{-1}.
\]

The literal existing law is \(\dot I=0\) when \(b\ge1,e>0\), or \(b\le.01,e<0\); otherwise \(\dot I=k_i e\). Release and fixed activation bypass this analysis. The numerical containment guard is an evidence/qualification stop, not a third mechanical field.

Let \(B\) be the relevant bound, and choose orientation \(\eta=+1\) at the upper bound or \(-1\) at the lower bound. Then

\[
 H=\eta(b-B),\quad H<0\ \text{on the interior side},\qquad
 \partial H/\partial I=\eta\ne0.
\]

For outward error \(\eta e>0\), the interior mode integrates and the exterior/boundary mode freezes. At \(H=0\), both mechanical limits use **the same \(u=B\)**. Only the \(I\) component jumps:

\[
 f_{on}=(G(p,B),k),\quad f_{off}=(G(p,B),0),\qquad k=k_i e.
\]

Since \(\dot l_T=-w-\dot l_f\), \(k_t=dF_T/dl_T>0\),

\[
 \dot e=k_t(w+\dot l_f)/F_0,\quad d=k_p\dot e,
 \qquad \nu_{on}=\nabla H\cdot f_{on}=\eta(d+k),\quad
 \nu_{off}=\nabla H\cdot f_{off}=\eta d.
\]

The signs are those of an unnormalized normal; positive normalization cannot change classification. The following is our application of the single-surface construction in Dieci–Lopez, §2.1, equations (2.6)–(2.10), and its equality caution in §3. [Primary paper](https://epubs.siam.org/doi/10.1137/080724599); [author-provided full text read](https://www.researchgate.net/publication/220179347_Sliding_Motion_in_Filippov_Differential_Systems_Theoretical_Results_and_a_Computational_Approach).

| Normal signs | Local interpretation |
| --- | --- |
| \(\nu_{on}>0,\nu_{off}>0\) | Crossing toward the saturated exterior |
| \(\nu_{on}<0,\nu_{off}<0\) | Crossing toward the interior |
| \(\nu_{on}>0>\nu_{off}\) | Strict attraction; Filippov sliding is locally unique under regularity |
| \(\nu_{on}<0<\nu_{off}\) | Repelling/nonunique in general; impossible here with \(k_i>0,\eta e>0\), since \(\nu_{on}-\nu_{off}=\eta k>0\) |
| Either normal zero | First-order classification is insufficient; analyze higher order or stop unqualified |

When error points inward, both sides integrate, so this antiwindup jump is absent. At \(e=0\) the jump vanishes and the sliding weight formula below is not a selection rule. Neither equality is silently resolved by clipping a weight or adding hysteresis.

## 2. What the retained failures establish

The algebraic receipt reevaluates eleven existing accepted/failed records using the unchanged source kernels. It does not integrate, localize an event, modify any stored state or move accepted time. The most nearly on-surface retained Radau points are:

| Case | Retained time (s) | Raw minus bound | \(e\) | \(d+k\) (/s) | \(d\) (/s) | Formal integrating weight \(\theta\) | Formal tangent \(\dot I\) (/s) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| high | .1054580660559943 | −1.3946e−11 | 1.15389995584 | 9.08932366056 | −.141875986136 | .0153691818578 | .141875986136 |
| mass-1 | .26203073655170017 | 1.6347e−13 | −.0333563229147 | −.0178564313682 | .248994151949 | .933084533126 | −.248994151949 |

Both have \(\nu_{on}>0>\nu_{off}\). These are floating-point near-boundary diagnostics, not exact event solutions or validated post-event orbits. The receipt separately records each rejected-stage raw signal, failure reason and time. A rejected RK/collocation stage is **not an accepted orbit point**; opposite stage signs do not themselves provide a certified exact-flow root bracket.

The guard retains earlier states: high .1054 s (RK4), .105130660/.105139259 s (DOP853/Radau); mass-1 .2620 s (RK4), .261977614/.261972026 s (DOP853/Radau). Original high DOP853 stalled after numerical progress beyond the earliest Radau surface; original RK4 high later reached slack and mass-1 reached .30 s. Those continuations remain unqualified evidence. They do not establish a chosen generalized solution. Earlier diagnostic-column Jacobian overflow is a separate numerical failure, not a proof of sliding.

Event timing is particularly sensitive at the lower surface. Its incoming normal magnitude is about .0178564/s, versus 9.08932/s at the upper surface. Linear **diagnostic predictions only** \(t-H/\nu_{on}\) from the guarded mass-1 points are .262038431 s (fine RK4), .262036709 s (coarse), .262031115/.262031098 s (Radau/DOP853). They are not root locations, but warn against assuming existing sampled state gates imply the 2 µs event-time gate. Even the allowed 1e−4 N force difference alone contributes \(k_p\Delta F/F_0=4e−7\) in raw signal, roughly 22 µs at that normal speed, before integral-state error. An independently localized event is necessary.

## 3. Literal-law nonexistence; conditional Filippov uniqueness

**Local nonexistence for the literal law.** Suppose a Carathéodory solution starts at an exact strictly attracting point. Continuity and strict signs give a short neighborhood with \(\nu_{on}\ge c>0\) for \(H<0\), and \(\nu_{off}\le-c<0\) for \(H\ge0\). Any open interval on which \(H>0\), beginning at \(H=0\), would integrate a strictly negative derivative and hence cannot be positive. The same argument excludes an interval of \(H<0\), whose derivative is strictly positive. Thus an absolutely continuous solution would have to satisfy \(H\equiv0\). Its derivative is then zero almost everywhere, but the literal equality rule selects the frozen field, whose normal derivative is strictly negative. Contradiction. Changing the branch at one isolated instant does not resolve this positive-duration contradiction.

**Filippov completion.** Explicitly replacing the surface value by the convex differential inclusion gives

\[
 f_S=\theta f_{on}+(1-\theta)f_{off},\qquad
 \theta=-d/k\in(0,1),\qquad
 \dot I=\theta k=-d=-k_p\dot e.
\]

Therefore \(H'=0\) and \(I=B-u_b-k_p e\) on the surface. Strict attraction prevents a forward solution leaving either side locally; tangency fixes \(\theta\) uniquely because \(k\ne0\). The retained points are away from activation limits and from the activation/deactivation equality: upper-bound excitation is above activation, and lower-bound excitation is below activation. Both fiber roots are strictly inside their bracket, with taut tendon and valid fiber length. In that local open neighborhood the source field and regular surface meet the required smoothness assumptions. The mechanical reduced ODE is simply \(\dot p=G(p,B)\), locally Lipschitz on the source-valid activation branch, and \(I\) is uniquely reconstructed by the constraint. This proves local forward uniqueness **within the explicitly chosen Filippov convention**, while strict attraction and validity persist. Cortés distinguishes Carathéodory and Filippov solutions and gives a piecewise-field uniqueness criterion (Proposition 5); it also explains why a boundary value ignored by Filippov regularization can matter for literal solutions. [Author preprint](https://arxiv.org/pdf/0901.3583), solution sections and Proposition 5. The argument here is specialized to our common-mechanical-field structure, not a global uniqueness claim.

At \(d=0\) or \(d+k=0\), one field is tangent. Equality alone does not decide departure versus continued contact with the switching surface; appropriate directional derivatives/higher-order analysis are needed. The proposed first experiment below stops at the first such degeneracy. It does not claim uniqueness through all exits, \(e=0\), domain failures or scheduled jumps.

**Model decision.** Filippov sliding is a generalized completion of these original two off-surface branches, with no new finite gain or added mechanical force. It nevertheless replaces the literal frozen surface value during positive sliding time. The frozen lab does not already declare this interpretation. Review must explicitly adopt the solution convention and bounded event policy, or retain the stops. Calling it merely a solver fix would conceal that decision.

## 4. Force/work consistency and distinction from controller replacement

No mechanical state jumps on entry to the candidate sliding surface. \(F_T\) remains continuous, the velocity root still satisfies \(R=0\), and every convex combination has the same mechanical field. The integral is an information state, not additional mechanical storage. The existing component identities therefore hold independently of the mixture:

\[
 \dot E_f=F_P\dot l_f,\quad
 \dot E_T=F_T(-w-\dot l_f),\quad
 \dot E_{load}=F_Tw,
\]
\[
 \dot E_f+\dot E_T+\dot E_{load}
 =(F_P-F_T)\dot l_f=-F_A\dot l_f-F_D\dot l_f=P_{active}-D,
 \qquad m\dot w=F_T-mg.
\]

This is an algebraic consistency result, not a numerical work certificate or ATP/heat model. Work balance alone cannot choose a controller or establish uniqueness. Unsaturated controller invariants or stability results are not extended to sliding.

For contrast, define a finite tracking/back-calculation controller

\[
 \dot I=k_i e+k_{aw}(u-b),\qquad k_{aw}>0.
\]

At \(b=B\), its tracking correction is zero, so its normal velocity is \(\eta(d+k)>0\), unlike sliding. In the saturated exterior, with \(d,k\) temporarily held constant for comparison, \(H'=\eta(d+k)-k_{aw}H\), leaving a finite positive offset. It changes the off-surface vector field and adds a tuning parameter. Taking an unproved infinite-gain limit is not a justification for substituting it. Finite-width smoothing, hysteresis, sample-and-hold memory or freezing based on a different raw-derivative test also need separate controller policies. None is proposed as an accuracy workaround.

Peng–Vrančić–Hanus distinguish conditional integration from feedback antiwindup methods in their original 1996 control paper, including “Conditional Integration,” equation (19), and “Linear Feedback.” Our existing error-direction switch is stated explicitly above; we do not assume that every clamping variant in the literature has the same surface law. [Primary paper DOI](https://doi.org/10.1109/37.526915); [author-uploaded full text read](https://www.researchgate.net/publication/3206463_Anti-windup_bumpless_and_conditioned_transfer_techniques_for_PID_controllers). Åström–Rundqwist (1989) is retained as foundational bibliographic context, not an inferred endorsement of this continuation: [Lund record](https://lup.lub.lu.se/record/8517647), [original six-page PDF](https://skoge.folk.ntnu.no/puublications_others/1989_Astrom-Rundqwist_anti-windup_ACC-conference.pdf). Its scan was located; machine-readable full text was unavailable in this execution.

For a scheduled command jump, \(\Delta b=k_p\Delta r/F_0\) while \(p\) and \(I\) remain continuous. Recompute the mode immediately; do not reset \(I\) to keep a previous bound or add bumpless-transfer behavior. This analysis introduces no new jump/reset rule.

## 5. Proposed bounded protocol — pending review, not executed

1. **Declare semantics first.** Adopt Filippov inclusion only at a single, strictly attracting, source-valid surface with outward error. Keep both original off-surface fields, gains, curves, activation, excitation limits and command schedule. No early successful terminal event is inferred from saturation. Failure/grazing remains unqualified. This is a new mathematical convention, not a retroactive label on old continuations.
2. **Use original initializations, local common endpoints.** Investigate only high through .107 s and mass-1 through .264 s, or stop earlier at the first lost strict sign, zero error, geometry/root failure or scheduled command jump. These fixed absolute endpoints permit independent common-time coverage. A stopped slice is prefix-only. Do not extend to .30 s or change the controller if the bounded experiment fails.
3. **Localize incoming flow, not a mixed trial.** From the last accepted state, use the incoming-mode field and a mode-consistent continuous extension to seek \(H(x_{in}(t))=0\). An opposite-side probe can be a localization auxiliary only; it is never accepted as a switched-law trajectory. All physical stage/root gates still apply. A stage that violates geometry, activation or force validity stops and retains the prior accepted state; do not shrink steps to hide it. A sign change in unrelated failed stage predictors is not a certified flow bracket. Require a bracket width ≤1e−7 s within 32 iterations and \(|H|\le1e−9\); no projection/reset of mechanical state or hidden integral adjustment to manufacture the root. Store incoming/event states, brackets, residuals and rejected probes separately.
4. **Check both fields at the event.** Verify regularity/root validity and \(\nu_{on}>0>\nu_{off}\) with numerical uncertainty below the sign margin; require \(0<\theta<1\) without clipping. Degenerate, uncertified or repelling cases stop. On the strict segment, the formal law is \(\dot p=G(p,B),\dot I=-k_p\dot e\). Stop at the first \(d=0\), \(d+k=0\), \(e=0\) or loss of the source-valid domain. Do not infer an exit just because a computed weight reaches 0 or 1.
5. **Two structurally independent representations.** Compare a full five-state constrained-field calculation with a separate four-mechanical-state calculation reconstructing \(I=B-u_b-k_p e\). This algebraic coordinate is part of the proposed convention, not a post-hoc projection of a failed primary state. Event coordinate consistency must be recorded; the primary calculation must fail rather than reset \(I\) to conceal drift. Use independent curve reconstruction/root evaluation and DOP853/Radau replay. No continuation code exists in this lane.
6. **Refinement and completion.** Predeclare RK4 .0002/.0001/.00005 s, original independent ODE settings, the existing .001 s grid plus event samples, and fixed slice endpoints. Require every required method to complete the same declared endpoint without failure, with adequate common-time coverage using the reviewed completion checker principle. Compare both absolute times and separately labeled event-relative diagnostics; aligning at events cannot hide incoming time error.

Keep original physical gates: force algebra 1e−7 N; curve values/slopes 2e−12/2e−8; matched y/w/a/q/FT 1e−6 m, 1e−5 m/s, 2e−6 a/q, 1e−4 N; event disagreement 2e−6 s; impulse 1e−7 N*s; component/combined work 1e−5 J. Add, before execution, **stricter controller diagnostics**: matched \(|\Delta I|\le1e−9\) and raw signal difference ≤1e−8; sliding constraint \(|H|\le1e−9\); independently evaluated tangent normal residual and mode-normal disagreements ≤1e−8/s. A normal magnitude ≤1e−8/s is a conservative uncertainty stop, not a hysteresis band or changed evolution law. These additional checks address weak event transversality; none weakens a physical gate. Internal source roots may need accuracy stricter than the maximum allowed residual, within the existing 64-iteration limit, to meet these diagnostics.

Recheck mechanical endpoint storage independently of stage-power accumulators, and Gaussian quadrature on actual accepted independent dense polynomials. Require force balance, impulse, every component ledger and combined energy; explicitly check no mechanical impulse/reset at entry. Algebraic identities do not substitute for these numerical checks.

Include negative controls for literal on/off boundary incompatibility, nonconvex weights, zero-error/zero-normal degeneracy, missed incoming roots, constraint drift, truncated/sparse/missing-method completion and invalid physical localization probes. Preserve every failed receipt. No trajectory is labeled qualified until the convention, protocol and subsequent evidence pass review.

## 6. Evidence and remaining decision

[Algebra/frozen-state checker](../../tools/check_antiwindup_continuation_analysis.py) contains no integrator. Five symbolic identities and eleven retained-state directional/root diagnostics pass. Its raw receipt binds original inputs and the unchanged source; finite-difference diagnostic precision is not a trajectory acceptance gate. [Raw algebra log](../../data/antiwindup-continuation-analysis-v1/review/algebra-run.log), [receipt](../../data/antiwindup-continuation-analysis-v1/review/algebra-and-frozen-state-check.json) and the source manifest support review.

The mathematical result is local and conditional: a unique Filippov completion is available under the strict assumptions, but the literal law cannot continue there. The remaining decision is whether to adopt that explicit convention and the bounded experiment. No new implementation, post-surface motion, global continuation, whole-arm credibility or publication is claimed.
