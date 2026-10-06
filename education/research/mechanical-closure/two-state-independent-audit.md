# Independent audit of the direct-CE kinetic benchmark

**PASS for the declared fixed-capacity, nonhuman equation-only benchmark.** All 144 archived matched-time backward Euler states satisfy the protocol's numerical gates and agree with an independently reconstructed spectral solution of the same discrete kinetic system. The implemented implicit step, bin-mass measure, signed boundary moment accounting, and invalid-input rejection tests passed. No actual implementation defect was found. This outcome does not reproduce a measured source fiber trajectory or qualify cooperative/series state, descending mechanics, an energy budget, or an anatomical arm law.

The [predeclared protocol](two-state-benchmark-protocol.md) fixes the input values, boundaries, timesteps, matched times, horizon, and tolerances. This audit changes none of them. The [independent audit tool](../../tools/independent_two_state_audit.py) produced a [source-pinned receipt](../../data/anatomical-arm-v1/review/two-state-kinetics/independent-audit.json) and [raw log](../../data/anatomical-arm-v1/review/two-state-kinetics/independent-audit.log). Its full input manifest includes the root implementation, protocol, source notes, benchmark summary, execution log, matched-state archive and the audit tool itself. No original mechanics controls or earlier receipts were rerun or changed.

## Primary source convention resolution

The earlier convention audit's source-access limitation was narrowed by independently reopening an already successful cached original [publisher PDF](https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1014748&type=printable). Printed pages 21–26 supplied extracted equations 2–6, 11 and 22 and Tables 2–3. The extraction supports normalized Gaussian area f1, detachment exponents `−x Ei`, centered strain `(d−dps)/dps`, the attached fraction `∫n dx`, and force `Q/β`. See the [separate source evidence note](source-rendering-evidence.md).

The Table 3 header lists two Hill models followed by four XB models. The three populated nH/Ca50 entries associate the third values 3.1/.83 μM with the ordinary two-state XB model. The four populated XB rate entries associate their first values 52/4/21.1/−.6 with that model. Table 2 supplies E1=2, 10 nm stroke, 3 nm width and β=.5. These are verified extracted values with column association inferred from header and populated-row ordering. Screenshot calls yielded references or a timeout, without inspectable pixels; visually aligned table cells and source-code parity are not certified. Normalized w=.3 and molar Ca50=.83e−6 are explicit unit conversions. No access restriction was bypassed.

## Independent construction and checks

The audit separately integrates the Gaussian over each cell using complementary-error-function differences, evaluates `g=4exp(−2x)+21.1exp(.6x)` at centers, and constructs the attached/detached star generator A. It verifies positive rates, nonnegative off-diagonal entries, zero column sums, the fixed capacity and the equilibrium detailed-balance fluxes.

Let q be the N=1 equilibrium population vector. Detailed balance gives a symmetric similar matrix `S=diag(q)^(-1/2) A diag(q)^(1/2)`, with attachment/detachment couplings `sqrt(Fi gi)`. The audit constructs S directly and diagonalizes it. The transformed eigensystem gives both the exact exponential factors `exp(t λ)` and backward Euler factors `(1−dt λ)^(-k)`. This supplies an independent algebraic solution at every declared matched time without replaying a time-stepping loop or resetting the state to equilibrium.

Across six grids, the audit compares all archived N=1 exponential states against this spectral exponential and all 144 pCa/shift/dt histories against spectral backward Euler powers. It independently recomputes saved forces, endpoint residuals, mass, population signs, immediate moment identities, refinement ratios and extent differences. A fresh full linear solve of `(I−dt A)ynew=yold` checks the implementation's rank-one implicit formula at each timestep on the coarse grid.

| Independent comparison or invariant | Largest observed value |
|---|---:|
| Cell-rate difference from saved CDF rates | 8.660e−15 s−1 |
| Generator column-sum magnitude | 3.553e−14 s−1 |
| Equilibrium detailed-balance flux residual | 1.111e−16 s−1 |
| Archived exponential versus spectral state difference | 9.304e−14 |
| Archived exponential versus spectral force difference | 3.728e−13 |
| Archived BE versus spectral BE state difference | 9.410e−14 |
| Archived BE versus spectral BE force difference | 3.760e−13 |
| Fresh implicit update versus direct solve difference | 1.666e−16 |
| Archived matched-time mass error | 3.775e−14 |
| Independent endpoint kinetic residual l1 | 9.352e−13 s−1 |
| Endpoint force difference from original discrete equilibrium | 5.463e−14 |
| Immediate boundary-corrected force identity error | 8.648e−16 |

The smallest archived matched population is 1.385419089e−26. The independently reconstructed spectral exponential also has nonnegative observed populations, with minimum 2.972953887e−26. No population was clipped. Exact-reference state/force comparisons are below 2e−12; protocol mass, positivity, endpoint and moment gates retain their original tolerances. All-step metrics are read from the source-pinned root receipts; the audit independently checks every archived matched state, the implemented one-step formula, and its algebraic positivity, rather than claiming to have separately scanned every intermediate step.

The BE update is positive because each numerator and denominator is nonnegative for admitted rates and dt, and the detached numerator includes the opposite binding/unbinding balance. In particular it computes d directly, avoiding a nearly cancelling `N−Σpi` reconstruction. Summing the implicit equations preserves total accessible population. The source implementation validates each candidate before recording advancement.

## Boundary and rejection tests

The independently constructed center-mass shift matrix has nonnegative entries and unit column sums. The escaping fraction moves into the detached state, whose force is zero. Its lost moment retains the sign of `(1+xescaped)`.

A synthetic population puts .27 at the left edge, .31 at the right edge, .12 in an interior bin and .30 in the detached state. With dx=.04, a +.01 shift detaches .0775 and loses discrete moment +.26505; a −.01 shift detaches .0675 and loses discrete moment −.09585. Both preserve total mass exactly in observed arithmetic and match the implemented remap and corrected force identity. The large boundary force changes are deliberate implementation challenges, not source-fixture predictions. They expose signed left/right accounting even though the actual fixture's boundary populations are tiny.

Sixteen invalid inputs are explicitly recorded as rejected: negative/nonfinite populations, incorrect mass, capacities outside the permitted interval or nonfinite, zero/negative/nonfinite dt, and zero/nonfinite shifts or shifts with magnitude at least dx. The tests preserve the exception messages. There is no hidden support for multi-cell shifts, coefficient alteration or clip-and-continue behavior.

This boundary convention is exactly the one declared in the protocol: off-grid destination centers define the lost **discrete** force moment. It is not an exact continuous partial-cell Gaussian-tail moment. Artificial boundary detachment is retained and measured; no escaped population is silently discarded or renormalized.

## Accuracy, spatial distinction and scope

Independently reconstructed temporal force-error halving ratios range from .504600125 to .509538407, consistent with the first-order BE discretization and within the predeclared .3–.8 gate. Equilibrium force-error halving ratios range from .250009248 to .250036992; the finest relative equilibrium error is about 1.687e−6, within the declared 1e−4 gate. The matched extent-force difference recomputed from archive states is 7.394e−14, below 1e−8. The slight difference from the root's reported 7.372e−14 comes from summation order when reconstructing forces.

An additional **diagnostic**, without a new acceptance gate, compares exact-generator transient force increments after subtracting each grid's own equilibrium baseline. The maximum matched increment differences between dx=.04/.02 and .02/.01 halve with ratios .482695242–.521991077. The largest pairwise difference is 3.198231440e−6 normalized force. The finest pair difference divided by `abs(delta) N/β` is at most .000771895248.

These transient differences behave approximately as first order in dx, while the equilibrium error behaves approximately as second order. Center-mass linear remapping adds displacement variance `abs(delta)(dx−abs(delta))` on an unbounded uniform grid, making a first-order transient artifact plausible. This is a diagnostic interpretation, not a proof of asymptotic order. The protocol's equilibrium spatial gate alone does not certify transient strain-space convergence, and this audit does not extend it into such a claim.

Independent continuous quadrature reproduces `I=1.992220371317`, the attached fraction .665800016073 at N=1, and baseline force 1.317797077720 with β=.5. The fixture retains this predicted baseline; no force-to-unity reset is performed. The unique fixed-capacity equilibrium explains the zero relaxed increment in this directly clamped, fixed-overlap experiment. That feature is a declared model limitation and cannot be cited as removal of the original descending-branch arm witnesses.

The justified outcome is closure of the declared kinetic mass, transport bookkeeping, implicit-time, equilibrium and fixed-budget relaxation gates for this equation fixture. A substantive source replay still requires an immutable individual-fiber code/data set, source series initialization and held-out histories. Cooperative pool conservation, physiological reference architecture, objective three-dimensional stress/state mapping, transverse/shear tests and coupled dynamic qualification remain separate obligations. No human coefficient or stabilizing law was selected by this audit.
