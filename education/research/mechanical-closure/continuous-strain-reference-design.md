# Continuous-strain reference before series/parallel initialization

**The shifted ghost-density construction is valid for the declared finite-domain kinetic model.** It evaluates translation of the same evolving strain function at new coordinates, removing adjacent-bin upwind interpolation. Its common population feedback is still approximated by quadrature; time integration and spatial quadrature need independent fixed resolution checks. This is a design and an unexecuted tool, not a continuum accuracy result or a physical release experiment.

Prepared 2026-10-06. Use the [committed original table audit](original-plos-table-visual-audit.md), source-evidence commit `64ef2727ec694f5a85ccce0eabcb708f7fcf97b7`, and the [article/code convention decision](article-code-convention-decision.md). The same independently declared hybrid uses publication medians and fixed width, pinned-code conserved heads M=1−B, held N, raw Q/.5 and direct CE input. It is not exact publication or code reproduction. The [previous finite-bin trajectory audit](../../data/anatomical-arm-v1/review/conserved-ce-trajectory/independent-audit-note.md) measures first-order transient refinement; a finite-bin DOP853 reference did not qualify the continuum strain function.

## Model and quadrature

On D=[−R,R], define

\[
\dot n(x)=f(x)A(t)-g(x)n(x),\quad
A(t)=(1-B)(N-B),\quad B=\int_D n(x)\,dx,
\]

with f(x)=52 exp[−x²/(2·.3²)]/(sqrt(2π)·.3), g(x)=4 exp(−2x)+21.1 exp(.6x), beta=.5 and N=1/[1+(.83/10^(6−pCa))^3.1]. Calcium is in µM in this expression. B, normalized force F=∫D(1+x)n dx/beta and normalized link energy E=∫D .5(1+x)²n dx/beta are dimensionless. No physical gamma, force, area, serial count, PE or SE is selected. The printed thermal-width radical is preserved as a source discrepancy; .3 follows from the explicit printed width/stroke values.

Use positive Gauss–Legendre nodes xi and weights wi on D, R=2.4/3 and counts 200/400/800. Only the **main** density nodes contribute B=Σwi ni. Auxiliary densities are evaluations of the same function and must never be added to population capacity. At fixed B the ODE for any coordinate z∈D has its own f(z),g(z) but shares A(t). Outside D set both injection and density to zero; positive detachment rates acting on a zero density retain zero. This declares an absorbing finite-strain boundary, not a physiological rupture law.

Set I=Σwi f(xi)/g(xi), c=1−N and q=N−B. The positive equilibrium root is

\[
q=\frac{2N}{1+Ic+\sqrt{(1+Ic)^2+4IN}},\qquad
n_*(x)=q(c+q)f(x)/g(x).
\]

The same coefficient defines an analytically evaluable initial strain function, not interpolated nodal samples. Verify the weighted full original-RHS L1 residual≤1e−10/s. Independently integrate f/g and equilibrium moment integrands with adaptive quadrature, epsabs=epsrel=1e−12, and compare initial B/F/E to the fixed **1e−10 initial-moment gate** in the [pre-execution protocol](continuous-strain-ce-protocol.md). Retain quadrature estimates and errors; warnings or failed gates reject the candidate without changing tolerances.

## Exact evaluated translations and common feedback

At t=0 prescribe delta=±.001/±.0005. The new main function is n0+(x)=n*(x−delta) when x−delta∈D and zero otherwise. For the first segment additionally integrate ghost density at zi=xi+delta:

\[
\dot v_i=f(z_i)A(t)-g(z_i)v_i,\qquad
v_i(0)=n_*(x_i)\mathbf1_{z_i\in D}.
\]

The ghost represents n(zi,t) on the same finite domain and under the same main B. At t=.2 apply −delta, hence n.2+(xi)=n.2−(xi+delta)=vi(.2). Use the ghost state directly as the new main density, then evolve main nodes alone to the unchanged terminal t=1. Do not interpolate, shift a BE state, reset to equilibrium, or include ghost weights in B.

This construction removes **strain interpolation** from the two prescribed translations. DOP853 dense output supplies time interpolation at matched times, while quadrature still approximates B and thereby the shared kinetic feedback. An arbitrary additional future displacement would require new function evaluations; two sets of ghost nodes are not a universal strain-function representation.

## Direct boundary integrals and jump ledger

For a shift h, the escaping **source** strip is (R−h,R] if h>0, or [−R,−R−h) if h<0. At loading, independently integrate n*(z), (1+z+h)n*(z)/beta and .5(1+z+h)²n*(z)/beta on that strip with adaptive quadrature at the fixed 1e−12 requested accuracy.

For the reversal, h=−delta. During the first segment integrate an additional **32** Gauss–Legendre density probes on its escaping source strip, each with its own f(z),g(z), the same main B and initialization n*(z−delta) masked to the old and current D. Their weights contribute only the escaping strip integrals at t=.2. They do not add to B. This obtains the evolved pre-reversal escaping function without a strain interpolant or an additional integration/retry budget.

Call the directly integrated terms Lesc, Fesc and Eesc. Lesc and Eesc are nonnegative; Fesc is **signed** because the left boundary has 1+z+h<0. Do not infer escape by subtracting nearly equal before/after population sums or clip its signed moment. Independently check, at both jumps,

\[
B_+=B_--L_{\rm esc},\quad
F_+-F_-=B_-h/\beta-F_{\rm esc},\quad
E_+-E_-=F_-h+B_-h^2/(2\beta)-E_{\rm esc}.
\]

Gate each absolute identity error≤2e−12. There is **no upwind interpolation-work term** in these continuum translation identities. Their finite-quadrature implementation can fail a gate and must preserve that failure. The 32-node narrow-strip probe is fixed, not an adaptive retry; tiny boundary integrals alone are not permission to discard the ledger. Kinetic attachment/detachment energy exchange and chemical accounting remain outside this model.

## Fixed execution and acceptance plan

For each R/count/pCa/delta, run DOP853 with rtol=1e−11, atol=1e−14 and both fixed max_step=.001/.0005 s. Each reference follows its own density through both jumps. Check finite/nonnegative density at **every accepted node and matched state**, and compute main B independently from the main weights with strict B≤N. Reject without clipping or resetting; preserve the raw invalid density, weights, N, label and active coordinate metadata. Terminal time remains 1 s; neither a solver failure nor a terminal residual changes the hold.

Use the public DOP853 step interface. After one solver step, validate its accepted-node candidate and every requested matched sample in that step's dense-output interval **before** advancing the externally admitted clock/state or starting the next step. On rejection retain the previous admitted step prefix and the attempted node separately. Passed initialization metrics and loading/reversal ledgers remain attached to the active reference context and survive any later failure. Build the final time interpolant from admitted intervals; matched outputs reuse samples already validated in their intervals, so a retrospective failure cannot report a later admitted clock.

The official [DOP853 API](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.DOP853.html) supplies step and dense-output methods; [OdeSolution](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.OdeSolution.html) combines admitted interval interpolants. Retain the integrator's normal embedded adaptive trial-step error control at the declared rtol/atol/max_step. The prohibited retry is an **external restart or new solver attempt after a population, jump-ledger or accuracy-gate failure**; this rule does not disable ordinary internal error control. Failed exports include admitted accepted-node and matched-sample prefixes, not only the last state.

The matched samples are 0-before,0-after,.008,.02,.04,.1,.2-before,.2-after,.3,.5,1. At a common quadrature, time-resolution differences must be ≤1e−10 for B and ≤2e−10 for F/E. At a common R/input and finer time resolution, both adjacent count comparisons 200→400 and 400→800 must have matched-moment absolute differences≤1e−9 for B/F/E. These are declared numerical gates, not physiological targets or proof of an unbounded-domain limit. Record R=2.4 versus R=3 differences separately without inventing another extent threshold.

The [new tool](../../tools/continuous_strain_ce_reference.py) must wait for the parent's precommitted [protocol](continuous-strain-ce-protocol.md), full identity and the declared failed-case export correction/negative-test prerequisite before execution. Preserve matched main/ghost/edge densities and accepted **time** arrays, plus canonical full accepted-state hashes, shapes, byte counts and min/max statistics. On a rejection preserve the actual candidate density and its coordinates/weights/N, the last admitted density and clock, and failed jump terms. Do not archive every internal population array. An optional read-only comparison with the preserved 144-case bin packet compares moments at identical event/time indices against the 800-node finer-time reference at matching R/input. It cannot compare nodal density L1 directly to bin masses without another representation map. Report raw and baseline-subtracted force errors, normalized perturbation errors and timestep/bin halving diagnostics; do not invent new response-error pass gates.

Passing would strengthen continuum-strain numerical qualification for this bounded model and history. It would not supply a force/area scale, identify human architecture, initialize PE/SE, reproduce the promised series-loaded comparison, erase the original fixed-activation saddle or qualify anatomical stability.
