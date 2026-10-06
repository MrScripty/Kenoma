# Incoming convergence diagnostic: four added 25 µs prefixes

The added level supports **ordinary smooth truncation error in high**, **loss of smooth refinement around mass-1's existing activation equality**, and a **separate later contribution from ordinary inward-crossing timing**. It does not support a controller-law/gain change or qualify sliding. Every original coarse result remains included, and the failed twenty-cell experiment plus the original ten-full/two-prefix scalar classifications remain unchanged.

The [protocol](filippov-incoming-convergence-protocol.md), inputs and source were committed and pushed before the four runs at **62721a3bd0204a48f8fa03bcedbbac18ea1e07ed**, tree **9870fd29f2b089c874498dbeb515e789782f51d2**. Protocol SHA256 is **7101ad7731dcd699c6af7b47cc81bd3a85f3735926429c666a986201b7e144a7**. All four incoming-only runs reached a held attracting candidate without physical failure. High retained accepted time .10545 s after 4,218 steps; mass-1 retained .262025 s after 10,483 steps. The separately predeclared 12,000-step watchdog accommodated the added resolution; original force/event iteration limits and all physical gates remained unchanged. **Zero sliding states or attracting-event states were accepted; zero trajectories were newly qualified.** Both named representations still use five incoming coordinates; reduced sliding coordinates were never invoked.

## Fixed-segment refinement

The following are maximum absolute-time, common-grid integral differences between adjacent source-kernel RK4 levels. Ratios compare the adjacent differences, not an assumed exact solution. The independent representation gives essentially the same pattern. Full state/force/raw errors, witness times, sample counts and both existing adaptive references are in the [segmented receipt](../../data/filippov-incoming-convergence-v1/review/segmented-analysis.json).

| Case / predeclared segment | 200 vs 100 µs | 100 vs 50 µs | 50 vs 25 µs | Successive ratios |
| --- | --- | --- | --- | --- |
| high, command transient .050–.060 s | 4.0793e−9 | 2.6039e−10 | 1.6339e−11 | 15.67, 15.94 |
| high, later smooth incoming | 3.9329e−9 | 2.5103e−10 | 1.5752e−11 | 15.67, 15.94 |
| mass-1, before activation equality, 0–.002 s | 9.2813e−13 | 5.8201e−14 | 3.6437e−15 | 15.95, 15.97 |
| mass-1, after activation / before freeze, .003–.107 s | 3.0965e−9 | 1.0049e−9 | 5.0390e−10 | 3.08, 1.99 |
| mass-1, frozen, .108–.249 s | 2.5611e−9 | 1.5319e−9 | 2.4787e−10 | 1.67, 6.18 |
| mass-1, after ordinary inward crossing, ≥.250 s | 3.6545e−9 | 2.6155e−9 | 1.8259e−9 | 1.40, 1.43 |

High's raw, activation and force differences also refine near 16 in its command/smooth segments. Its initial equilibrium is at roundoff scale; ratios there are not convergence evidence. In mass-1's fixed activation-transition window .002–.003 s, adjacent activation differences are 1.6687e−8, 5.4140e−9 and 2.7156e−9, with ratios 3.08 and 1.99. The order loss is already visible before either ordinary controller crossing. These measured ratios do not establish a new asymptotic order or prove a sole cause.

Both new lower runs observe `u−a=0` on their actual accepted-step dense polynomial at **.002427392257005 s**, within a **.745 ps** bracket. Those observations are auxiliary and never split a step or change a state. The [pinned original activation source](../../data/millard-reference-v1/upstream/MuscleFirstOrderActivationDynamicModel.cpp) gives a rate zero from both sides at equality, while its two time constants give different one-sided derivatives. This supports treating the existing nonsmooth activation transition as a numerical issue to investigate, rather than changing its law. Old activation dense coefficients were not retained, so no old activation-root trajectory was inferred from its 1 ms samples.

## Frozen memory and later crossing timing remain separate

For the declared incoming controller, write the integrating indicator as χ. With identical initial integral state,

\[
 \Delta I(t)=8\int_0^t[\chi_a(s)e_a(s)-\chi_b(s)e_b(s)]\,ds.
\]

On a common frozen interval, the integral offset is constant. After inward crossing, differing switch times can contribute locally as `−(8e_in) Δt_in`, in addition to the remembered offset and differing errors along the trajectories. This is an analytical interpretation of the declared law, not an independent exact integration certificate. At equal command the raw difference also retains the exact signed decomposition `Δraw = ΔI − .004 ΔFT`; force and integral contributions can cancel, so small raw error does not certify integral convergence.

For source RK4 pairs, the measured change from the frozen .200 s signed offset and the **original recorded** inward timing proxy are:

| Pair | Frozen signed ΔI | Max after-inward change from that offset | `max(|8e|) |Δt_in|` | Original Δt_in |
| --- | --- | --- | --- | --- |
| 200 vs 100 µs | −2.5611e−9 | 6.2155e−9 | 6.2269e−9 | +18.311 ns |
| 100 vs 50 µs | −1.5319e−9 | 4.1474e−9 | 4.1513e−9 | +12.207 ns |
| 50 vs 25 µs | +2.4787e−10 | 2.0737e−9 | 2.0756e−9 | −6.104 ns |

The close agreement supports a substantial later timing contribution while preserving the early activation/incoming error and frozen memory as separate quantities. It is not causal proof or a rigorous orbit-error bound. Anchor subtraction is interpreted only as an after-inward diagnostic; it never corrects an original error or state. Generic raw tables retain anchor-derived values for other segments, which are not used for this interpretation.

## Original brackets versus tighter auxiliary observations

All **32 RK4 controller-event auxiliary polynomials** were reconstructed from their four stored stages, reproduced their original candidate states within 1e−12, and re-localized diagnostically within the original brackets. All 32 met the separately predeclared 1e−12 s bracket/1e−13 surface targets within 32 diagnostic iterations. No polished root fed an existing or new accepted state, event, history or ledger. The 16 adaptive event records retain their original brackets/residuals because their actual dense coefficients were not serialized; no substitute polynomial was invented.

The [event records](../../data/filippov-incoming-convergence-v1/review/segmented-analysis.json) retain H, the incoming normal, original bracket radius, force-root residual, and `|H|/|normal|` local surface-residual timing proxy. Mechanical equilibrium residual is recorded separately and does not bound position/raw orbit error. The weak lower attracting surface has original RK4 residual-time proxies up to about 46.14 ns. **Attracting candidates were never accepted**, so their potentially large `|8e|Δt` terms cannot explain earlier accepted-history errors.

At the earlier ordinary inward crossing, tighter polynomial observation changes the pairwise timing proxy substantially:

| Source pair | Original `|8e| |Δt_in|` | Polished-polynomial-only proxy |
| --- | --- | --- |
| 200 vs 100 µs | 6.2269e−9 | 7.1947e−9 |
| 100 vs 50 µs | 4.1513e−9 | 3.0810e−9 |
| 50 vs 25 µs | 2.0756e−9 | 1.0329e−9 |

For 50/25 µs the change is **1.0428e−9**, comparable to the unchanged 1e−9 integral diagnostic gate. Even the outward crossing can mask underlying polynomial timing differences: its original 50/25 times nearly coincide, whereas their diagnostic-only polished roots differ by about .502 ns. These polished roots describe auxiliaries built from the **original accepted starting states**; replacing an event time alone would not replay or correct those trajectories.

## Limits and next protocol decision

All four new accepted prefixes pass the unchanged independent force/work/impulse/dense-quadrature checks. Peak independent accepted force closure is 8.3134e−13 N and peak work-ledger error is 5.6348e−13 J. The two new representations agree to about 5.1e−14 in integral and 2.6e−13 in raw signal for lower. These incoming certificates do not qualify post-surface motion.

The new 25 µs lower run differs from the existing independent Radau reference by **1.4684e−9 in integral**, above the original 1e−9 criterion, despite smaller differences against DOP853. Both references and every coarse level remain in the receipt. Choosing the favorable reference or dropping the coarse results would not justify a pass, and this diagnostic issues no qualification label.

The evidence supports a separately reviewed numerical protocol that first strengthens **ordinary-event localization** and investigates event-consistent handling of the **existing continuous activation equality**. Keep its gains/laws fixed and require both independent adaptive references. The smooth high error and nonsmooth/timing-limited lower error should have separate evidence requirements. This is a proposed next decision, not authority to implement that protocol, start sliding, relax gates or adopt changes into the book/Lean/anatomical capstone.

[Decision summary](../../data/filippov-incoming-convergence-v1/review/decision-summary.json), [raw segment/event analysis](../../data/filippov-incoming-convergence-v1/review/segmented-analysis.json), [tests](../../data/filippov-incoming-convergence-v1/review/test-run.log) and [inspected figure](../../data/filippov-incoming-convergence-v1/review/segmented-refinement.png) support review. The figure retains all four RK4 levels against each representation's existing DOP853; both adaptive references remain in the raw tables. Its display floor is 1e−17 for logarithmic visibility only, and the receipt retains the actual smaller errors.
