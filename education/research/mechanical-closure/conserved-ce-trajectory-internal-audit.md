# Internal review of the conserved-head CE trajectory runner

**The two jump moment/elastic-energy ledgers and declared event clock are mathematically correct.** This read-only review identifies a latent partial-failure reporting gap, not an observed numerical failure. The completed packet reports 144 admitted histories and a separate independent audit reports 144 cases/48 reference groups passing. No history was executed or rerun in this review.

Reviewed [conserved_ce_trajectory.py](../../tools/conserved_ce_trajectory.py) and the [predeclared protocol](conserved-ce-trajectory-protocol.md). The executed source commit is `b21ee8c252d4160a367fa7b21a9adf8c57a1dcaf`, as recorded in the [execution summary](../../data/anatomical-arm-v1/review/conserved-ce-trajectory/summary.json). The inspected runner SHA-256 is `58e29815607245d40168209cf7a009ed2630946614abaf900c64669450643920`, matching the execution receipt. The executed protocol hash is `7b343008fa34cf7bb88c1c6899ec547d3c90cddb0f877cb448ef6fdbea58466a`. The frozen source was not edited.

## Both jump ledgers

For a signed single-bin displacement δ, r=|δ|/dx redistributes each attached bin mass between its original center and the adjacent center. Before boundary removal, the remap has mean displacement δ and displacement variance |δ|(dx−|δ|). Therefore, with Fhat=Σ(1+x)pi/β and Ehat=Σ(1+x)²pi/(2β), it gives

\[
\Delta\widehat F=B\delta/\beta-m_{\rm escape}/\beta,
\]

\[
\Delta\widehat E=\widehat F_{\rm before}\delta
+\frac{B\delta^2}{2\beta}
+\frac{B|\delta|(dx-|\delta|)}{2\beta}
-e_{\rm escape}/\beta.
\]

Here m_escape=(1+x_destination) times escaped mass is signed, and e_escape=(1+x_destination)² times escaped mass/2 is nonnegative. The destination is the adjacent discrete center beyond the domain, not the endpoint or the continuously shifted original center. The source records already-normalized escaped quantities and subtracts them once, consistently with these identities. Taking an absolute value of the escaped force moment would be incorrect on the left boundary; the runner preserves its sign.

The positive variance contribution is interpolation work, separately labeled in the protocol and runner. It cannot be counted as physical elastic input work. The kinetic reaction changes elastic energy without a modeled chemical-energy balance. These are correctly bounded discrete arithmetic ledgers rather than a thermodynamic closure.

The reversal repeats the same calculation using its own evolved pre-reversal population, attached fraction and force, with displacement −δ. It does not restore the equilibrium population. Returned prescribed CE length therefore does not imply reversed population mixing or zero transient force.

At either jump, B_after=B_before−escapedMass. With the declared implicit free-head pool M=1−B and held N, both M and available-site capacity N−B increase by escapedMass. No detached mass is discarded from total head accounting or immediately reattached by a correction. This is the declared artificial-boundary detachment convention, not a source-derived physical boundary law.

## Event clock and state admission

The 11 saved states are equilibrium at 0-before, loading at 0-after, .008, .02, .04, .1, .2-before, .2-after, .3, .5 and 1 seconds. The runner saves the .2 pre-jump state before executing the reversal, then appends the post-jump state at the same time.

| h (s) | Saved integer step indices, with distinct states at duplicate jump times |
|---:|---|
| .004 | 0, 0, 2, 5, 10, 25, 50, 50, 75, 125, 250 |
| .002 | 0, 0, 4, 10, 20, 50, 100, 100, 150, 250, 500 |
| .001 | 0, 0, 8, 20, 40, 100, 200, 200, 300, 500, 1000 |

Thus every declared sample aligns with each fixed timestep; floating-point alignment is explicitly checked with tolerance 1e-13. The step loop advances its admitted state and clock only after the qualified operator returns and the runner's independently accumulated full BE residual passes. The executed source also gates the terminal candidate's kinetic residual before admitting the final step. A jump changes state only after the transport's population, force, energy and mass gates pass.

On an exception, `finally` retains all completed case records/distributions and the failed case's last admitted state, admitted clock, matched prefix and phase. A candidate returned by the operator and rejected by a subsequent runner gate is archived when present; an exception inside the operator does not expose its internal candidate. This preservation is distinct from the reporting gap below.

## Latent partial-failure ledger reporting gap

Loading/reversal ledger dictionaries and running extrema/residual diagnostics remain local variables in `run_case` until the successful case record is returned. If a later reversal or terminal gate fails, the outer exception preserves state/clock/prefix evidence, but does not serialize already-computed successful jump ledgers or these accumulated diagnostics for that failed case. The gap is in partial diagnostic reporting; it does not show that a rejected candidate advances the clock or that admitted states are lost.

A future additive correction could copy each admitted jump ledger and running diagnostic into `progress` and serialize those values with the failure record, without changing the equations, gates or accepted trajectory. **That correction has not been made here.** The executed runner remains frozen, and the current [summary](../../data/anatomical-arm-v1/review/conserved-ce-trajectory/summary.json) contains 144 successful histories and an empty failures list. The [separate independent audit](../../data/anatomical-arm-v1/review/conserved-ce-trajectory/independent-audit-note.md) reports all 144 cases and 48 reference groups passing; this review did not reproduce that computation.

The result remains a dimensionless source-informed direct-CE prerequisite with a declared hybrid population/force convention. It supplies no finite-series loaded comparison, SI force/area calibration, human anatomical trajectory, continuum stability or erasure of earlier negative witnesses. No simulation, Git operation, production change or old-packet edit occurred in this review.
