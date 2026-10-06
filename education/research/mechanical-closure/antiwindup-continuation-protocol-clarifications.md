# Antiwindup continuation protocol: localization extension and complete method matrix

This research-only addendum clarifies items 3, 5 and 6 of the [proposed bounded protocol](antiwindup-continuation-analysis.md). The accepted local analysis and its evidence remain frozen at commit 277ce67fdf1bf88182aebd1cda7b20c10fe8f5a5. The owner has not authorized the separate Filippov sliding experiment. No continuation implementation, trajectory advancement, controller/gain/force change or new qualification is made here. The existing ten-full/two-prefix classifications remain unchanged.

## Incoming-flow auxiliary extension

For these two constant-command, outward-error entries, the incoming mode integrates the error. From the last accepted state, define the localization-only extension

\[
 b=u_b+k_p e(p)+I,\qquad
 f_{in}^{aux}(p,I)=\left(G\bigl(p,\operatorname{clip}(b,.01,1)\bigr),\ k_i e(p)\right).
\]

It agrees with the declared incoming field while \(H<0\). Continue **that integrating mode** in auxiliary stages and dense-output probes on either side of the candidate surface solely to bracket and solve \(H(x_{in}^{aux}(t))=0\). Retain the original excitation clipping everywhere, including probes beyond the bound; do not extrapolate unbounded excitation or set excitation to \(B\) on the whole incoming interval. At the surface the clipped excitation is \(B\). The extension crosses the switch by continuing \(\dot I=k_i e\); it is not the literal exterior frozen law or an accepted post-event solution.

All probes use the original mechanical equations, curve/root checks, geometry and activation validity gates. A physical failure in any localization stage stops the attempt and retains the previous accepted state; shrinking the step to conceal that failure is prohibited. Conversely, crossing the controller surface in an otherwise valid auxiliary probe is an explicitly labeled localization operation, not accepted time advancement. Stop if outward error or the constant-command assumption ceases to apply. Do not mix the exterior frozen field into the incoming polynomial: that would localize a different flow.

Store the starting accepted state, incoming-mode stages/continuous extension, bracket endpoints, candidate root state, force/geometry residuals and every rejected probe separately. Beyond-surface auxiliary probes are never appended to accepted history or work/impulse ledgers. A candidate event state may be accepted only in a subsequently authorized experiment after the original validity gates, root bracket width ≤1e−7 s within 32 iterations, \(|H|\le1e−9\), independent event-time agreement and strict-attraction checks pass. No physical-state projection or integral reset is permitted. Any accepted incoming interval ends at the certified event; its work/impulse integration excludes the rest of the auxiliary extension. A failed predictor from another flow is not a bracket endpoint for this flow.

This is the explicit one-sided incoming-flow construction needed by the event-localization proposal, not a change to the accepted dynamics. The original analysis cites Dieci–Lopez's primary discussion of one-sided stage handling and roots of continuous extensions; its local uniqueness and degeneracy restrictions still apply.

## Required representation/method matrix

Every cell below is required for **each** case: high through the fixed absolute endpoint .107 s and mass-1 through .264 s, with the original initializations and earlier failure/degeneracy stops. Thus there are ten proposed cells per case, twenty in total. These cells are a future experimental requirement, not additional completed cases.

| Method / integration settings | Full five-state representation | Independent reduced representation |
| --- | --- | --- |
| RK4, step .0002 s | Required | Required |
| RK4, step .0001 s | Required | Required |
| RK4, step .00005 s | Required | Required |
| DOP853, original adaptive settings | Required | Required |
| Radau, original adaptive settings | Required | Required |

The full representation advances \((p,I)\), using \(\dot I=-k_p\dot e\) only on an authorized strictly attracting sliding segment, without resetting \(I\) to repair drift. The separate reduced representation advances the four mechanical coordinates on that segment and reconstructs \(I=B-u_b-k_p e\) as its declared coordinate. **Both representations still need all five incoming coordinates before entry** and their own incoming-flow localization; the reduced sliding formula cannot replace the incoming integral history. The two representations use separate source versus independently reconstructed curve/root evaluations, as specified in the original protocol. The reduced calculation must not consume the full calculation's event time/state, accepted trajectory or ledger.

Both DOP853 and Radau are required in both representations. Retain the original adaptive settings from [protocol.json](../../data/vertical-force-command-v1/protocol.json) and [reference solver](../../tools/vertical_force_reference.py): rtol 1e−9, atol 1e−11 and maximum step .0005 s. Three RK4 levels are required in both representations; adaptive replay does not replace any RK4 level, and one adaptive solver does not replace the other. All existing force-root iteration limits, physical gates and the pending protocol's controller/constraint checks remain as stated.

For each case, require every cell to reach the same fixed endpoint without failure and cover the original .001 s common-time grid plus independently localized event samples and the exact endpoint. Retain each method's independent event state/time and stopping reason. Missing, truncated, sparse or stopped cells leave the bounded experiment unqualified; a passing prefix is not full completion. Compare adjacent RK4 levels within each representation, both adaptive solvers, matching methods across representations and the finest RK4 against both adaptive references. Compare physical states/forces and ledgers at matched absolute times. Separately labeled event-relative comparisons supplement those checks and cannot erase entry-time disagreement. No automatic exit through a zero normal, zero error or lost validity is added.

## Lower-surface event refinement remains independent

At the retained mass-1 near-surface state, the incoming oriented normal is about .0178564313682/s. The existing matched force allowance 1e−4 N alone permits a raw-signal contribution

\[
 |\Delta b_F|=k_p|\Delta F_T|/F_0=4\times10^{-7},\qquad
 |\Delta t|\approx |\Delta b_F|/|\nu_{on}|=22.4\ \mu\mathrm{s}.
\]

That linear sensitivity diagnostic exceeds the unchanged **2 µs event disagreement gate** by about a factor of eleven. It is not a rigorous error bound or an event location. Integral/raw-signal tolerances constrain additional error contributions but cannot replace event localization and event-time refinement. A narrow numerical root bracket also cannot certify the accuracy of its incoming trajectory. Independently localize entry in all twenty proposed cells, demonstrate event-time convergence across all three RK4 levels and agreement with both adaptive solvers and the independent representation, and retain bracket/constraint/normal diagnostics alongside those comparisons. If event agreement fails while force/state gates pass, retain the failure; do not align trajectories to hide it, relax the gate or substitute tighter integral/raw checks for the missing event evidence.

The original force, impulse, component/combined work and matched-state gates remain unchanged. No work/force certificate or new trajectory qualification follows from this addendum. Execution remains blocked on the owner's explicit decision about the Filippov convention and separate bounded experiment.
